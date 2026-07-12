"""Seam C backend integration tests — PATCH /v1/student/sessions/{id}/nodes/{id} (M3-C R2).

Red-before-green per canon §9. Verifies node position persistence emits a
node_position_updated v1 event, echoes the persisted coordinates, rejects
non-finite floats, and 404s for unknown nodes/sessions.

Traceability:
- docs/planning/sdd/phase-3-m3c-infrastructure-remediation-sdd.md §6.3, §9.3 (TC-1..TC-4)
- docs/api/student-api-spec.md §6 (PATCH /nodes/{id})
- docs/planning/session-path-data-contract.md §6 (node layout/position contract)
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

import jwt
from app.domain.auth import AuthContext
from app.domain.student.nodes import NodePositionUpdate
from fastapi.testclient import TestClient


def _build_client_and_runtime(jwt_secret: str = "test-secret"):
    from app.main import SessionRuntime, create_app

    tenant_id = uuid4()
    student_user_id = uuid4()
    runtime = SessionRuntime.for_testing(
        tenant_id=tenant_id,
        student_user_id=student_user_id,
        jwt_secret=jwt_secret,
    )
    runtime.memberships.add_membership(
        user_id=student_user_id,
        tenant_id=tenant_id,
        role="student",
    )
    client = TestClient(create_app(runtime=runtime))
    token = jwt.encode({"sub": str(student_user_id)}, jwt_secret, algorithm="HS256")
    client.headers["Authorization"] = f"Bearer {token}"
    return client, runtime


def _seed_curriculum(runtime):
    from app.projections.curriculum import CurriculumIngestInput, build_curriculum_rows

    chapter_id = uuid4()
    chapter_analysis_id = uuid4()
    concept_id = uuid4()
    runtime.curriculum.ingest(
        build_curriculum_rows(
            CurriculumIngestInput(
                tenant_id=runtime.tenant_id,
                exam_id=uuid4(),
                subject_id=uuid4(),
                chapter_id=chapter_id,
                title="Electricity",
                chapter_analysis_id=chapter_analysis_id,
                segment_index_version="p0-v1",
                pipeline_version="p0-p4-v1",
                prompt_version="fixtures-v1",
                model_id="fixture-model",
                pages=["Electric current flows through a closed circuit."],
                named_concepts=[
                    {
                        "concept_id": str(concept_id),
                        "label": "Electric current",
                        "definition": "Flow of charge in a circuit.",
                        "category_tag": "definition",
                        "passage_refs": {
                            "definitional": [f"{chapter_id}_para_001"],
                            "explanatory": [],
                            "application": [],
                        },
                    }
                ],
                embedded_concepts=[],
                edges=[],
            )
        )
    )
    chapter_row = next(iter(runtime.curriculum.chapters.values()))
    return {
        "exam_id": str(chapter_row["exam_id"]),
        "subject_id": str(chapter_row["subject_id"]),
        "chapter_id": str(chapter_id),
        "concept_entry_id": str(concept_id),
    }


def _start_session(client: TestClient, runtime) -> str:
    response = client.post("/v1/student/sessions", json=_seed_curriculum(runtime))
    assert response.status_code == 201
    return response.json()["session_id"]


def _append_node_created(runtime, session_id, *, node_id=None, content="Explore: alpha"):
    node_id = node_id or uuid4()
    event = {
        "event_id": uuid4(),
        "event_type": "node_created",
        "event_version": 1,
        "tenant_id": runtime.tenant_id,
        "actor_user_id": runtime.student_user_id,
        "student_id": runtime.student_user_id,
        "session_id": UUID(session_id),
        "node_id": node_id,
        "occurred_at": datetime.now(timezone.utc),
        "payload": {
            "node_id": str(node_id),
            "session_id": session_id,
            "node_type": "ai",
            "content": content,
            "source_node_id": str(uuid4()),
            "source_offer_set_id": str(uuid4()),
            "source_option_id": str(uuid4()),
            "source_option_text": "x",
            "thread_context_id": str(uuid4()),
        },
    }
    runtime.event_store.append(event, producer="server")
    return node_id


def test_tc1_patch_echoes_position() -> None:
    client, runtime = _build_client_and_runtime()
    session_id = _start_session(client, runtime)
    node_id = _append_node_created(runtime, session_id)
    response = client.patch(
        f"/v1/student/sessions/{session_id}/nodes/{node_id}",
        json={"position_x": 42.5, "position_y": -13.0},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["node_id"] == str(node_id)
    assert body["position_x"] == 42.5
    assert body["position_y"] == -13.0


def test_tc2_patch_appends_node_position_updated_event() -> None:
    client, runtime = _build_client_and_runtime()
    session_id = _start_session(client, runtime)
    node_id = _append_node_created(runtime, session_id)
    event_count = len(runtime.event_store.events)
    response = client.patch(
        f"/v1/student/sessions/{session_id}/nodes/{node_id}",
        json={"position_x": 10.0, "position_y": 20.0},
    )
    assert response.status_code == 200
    appended = runtime.event_store.events[event_count:]
    assert len(appended) == 1
    event = appended[0]
    assert event["event_type"] == "node_position_updated"
    assert event["payload"]["node_id"] == str(node_id)
    assert event["payload"]["position_x"] == 10.0
    assert event["payload"]["position_y"] == 20.0


def test_tc3_patch_non_finite_float_is_422() -> None:
    client, runtime = _build_client_and_runtime()
    session_id = _start_session(client, runtime)
    node_id = _append_node_created(runtime, session_id)
    # JSON standard has no inf/nan; httpx's json= encoder rejects it client-side,
    # so send raw content (Python json.loads accepts Infinity) to exercise the
    # server-side allow_inf_nan=False boundary.
    response = client.patch(
        f"/v1/student/sessions/{session_id}/nodes/{node_id}",
        content='{"position_x": Infinity, "position_y": 0.0}',
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422


def test_tc4_patch_unknown_node_is_404() -> None:
    client, runtime = _build_client_and_runtime()
    session_id = _start_session(client, runtime)
    response = client.patch(
        f"/v1/student/sessions/{session_id}/nodes/{uuid4()}",
        json={"position_x": 1.0, "position_y": 2.0},
    )
    assert response.status_code == 404


def test_runtime_patch_rejects_non_finite_coordinates() -> None:
    client, runtime = _build_client_and_runtime()
    session_id = _start_session(client, runtime)
    node_id = _append_node_created(runtime, session_id)
    auth = AuthContext(user_id=runtime.student_user_id, tenant_id=runtime.tenant_id, role="student")
    event_count_before = len(runtime.event_store.events)

    try:
        runtime.update_node_position(
            session_id=UUID(session_id),
            node_id=node_id,
            payload=NodePositionUpdate(position_x=float("inf"), position_y=0.0),
            auth=auth,
        )
    except ValueError as exc:
        assert "finite" in str(exc)
    else:
        raise AssertionError("Expected ValueError for non-finite coordinates")

    # No node_position_updated event must be appended on rejection.
    assert len(runtime.event_store.events) == event_count_before
