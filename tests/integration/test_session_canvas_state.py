"""Seam B integration tests — GET /v1/student/sessions/{id} canvas hydration (M3-C R1-bis).

Red-before-green per canon §9. Verifies the canvas snapshot reconstructed from the
event log is returned by GET /sessions/{id}, stays student-safe (Category Invisibility),
and that router ordering does not break GET /sessions/recent.

Traceability:
- docs/planning/sdd/phase-3-m3c-infrastructure-remediation-sdd.md §5, §9.2 (TB-1..TB-8)
- docs/api/student-api-spec.md §5 (canvas payload shape)
- docs/planning/session-path-data-contract.md §6 (node contract)
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

import jwt
from fastapi.testclient import TestClient

FORBIDDEN_ANALYTIC_FIELD_FRAGMENTS = (
    "dimension",
    "classification",
    "coverage",
    "gap",
    "score",
    "confidence",
    "entropy",
    "vector",
    "profile",
    "weight",
    "propensity",
    "probe",
    "teacher_",
)


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


def _start_session(client, runtime) -> str:
    body = _seed_curriculum(runtime)
    response = client.post("/v1/student/sessions", json=body)
    assert response.status_code == 201
    return response.json()["session_id"]


def _scope(runtime, session_id, **extra):
    base = {
        "event_id": uuid4(),
        "event_version": 1,
        "tenant_id": runtime.tenant_id,
        "actor_user_id": runtime.student_user_id,
        "student_id": runtime.student_user_id,
        "session_id": UUID(session_id),
        "occurred_at": datetime.now(timezone.utc),
    }
    base.update(extra)
    return base


def _append_node_created(runtime, session_id, *, node_id=None, content="Explore: alpha"):
    node_id = node_id or uuid4()
    event = _scope(
        runtime,
        session_id,
        event_type="node_created",
        node_id=node_id,
        payload={
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
    )
    runtime.event_store.append(event, producer="server")
    return node_id


def _append_edge_created(runtime, session_id, *, source_node_id, target_node_id, edge_id=None):
    edge_id = edge_id or uuid4()
    event = _scope(
        runtime,
        session_id,
        event_type="edge_created",
        node_id=source_node_id,
        edge_id=edge_id,
        payload={
            "edge_id": str(edge_id),
            "session_id": session_id,
            "source_node_id": str(source_node_id),
            "target_node_id": str(target_node_id),
            "edge_kind": "ai_path",
            "created_by": "server",
        },
    )
    runtime.event_store.append(event, producer="server")
    return edge_id


def _append_node_deleted(runtime, session_id, *, root_node_id, deleted_node_ids, deleted_edge_ids):
    event = _scope(
        runtime,
        session_id,
        event_type="node_deleted",
        node_id=root_node_id,
        payload={
            "root_node_id": str(root_node_id),
            "session_id": session_id,
            "deleted_node_ids": [str(n) for n in deleted_node_ids],
            "deleted_edge_ids": [str(e) for e in deleted_edge_ids],
            "confirmed": True,
            "deletion_cause": "user_confirmed_node_delete",
        },
    )
    runtime.event_store.append(event, producer="server")


def _append_edge_deleted(runtime, session_id, *, root_node_id, edge_id):
    event = _scope(
        runtime,
        session_id,
        event_type="edge_deleted",
        node_id=root_node_id,
        edge_id=edge_id,
        payload={
            "edge_id": str(edge_id),
            "session_id": session_id,
            "edge_kind": "ai_path",
            "deletion_cause": "node_cascade",
        },
    )
    runtime.event_store.append(event, producer="server")


def _append_node_position(runtime, session_id, *, node_id, position_x, position_y):
    event = _scope(
        runtime,
        session_id,
        event_type="node_position_updated",
        node_id=node_id,
        payload={
            "node_id": str(node_id),
            "session_id": session_id,
            "position_x": position_x,
            "position_y": position_y,
        },
    )
    runtime.event_store.append(event, producer="client")


def _has_forbidden_key(obj) -> bool:
    if isinstance(obj, dict):
        for key, value in obj.items():
            if any(frag in key for frag in FORBIDDEN_ANALYTIC_FIELD_FRAGMENTS):
                return True
            if _has_forbidden_key(value):
                return True
    elif isinstance(obj, list):
        return any(_has_forbidden_key(item) for item in obj)
    return False


def test_tb1_started_canvas_contains_fixture_root() -> None:
    client, runtime = _build_client_and_runtime()
    session_id = _start_session(client, runtime)
    response = client.get(f"/v1/student/sessions/{session_id}")
    assert response.status_code == 200
    canvas = response.json()["canvas"]
    assert len(canvas["nodes"]) == 1
    assert canvas["nodes"][0]["content"].startswith("Electricity studies")
    assert canvas["edges"] == []


def test_tb2_node_created_appears() -> None:
    client, runtime = _build_client_and_runtime()
    session_id = _start_session(client, runtime)
    node_id = _append_node_created(runtime, session_id, content="Explore: Ohm")
    response = client.get(f"/v1/student/sessions/{session_id}")
    assert response.status_code == 200
    nodes = response.json()["canvas"]["nodes"]
    assert len(nodes) == 2
    created = next(node for node in nodes if node["node_id"] == str(node_id))
    assert created["content"] == "Explore: Ohm"


def test_tb3_node_deleted_removed() -> None:
    client, runtime = _build_client_and_runtime()
    session_id = _start_session(client, runtime)
    node_id = _append_node_created(runtime, session_id)
    _append_node_deleted(
        runtime, session_id, root_node_id=node_id, deleted_node_ids=[node_id], deleted_edge_ids=[]
    )
    response = client.get(f"/v1/student/sessions/{session_id}")
    assert response.status_code == 200
    remaining = response.json()["canvas"]["nodes"]
    assert len(remaining) == 1
    assert remaining[0]["content"].startswith("Electricity studies")


def test_tb4_edge_deleted_removed() -> None:
    client, runtime = _build_client_and_runtime()
    session_id = _start_session(client, runtime)
    src = _append_node_created(runtime, session_id)
    tgt = _append_node_created(runtime, session_id)
    edge_id = _append_edge_created(runtime, session_id, source_node_id=src, target_node_id=tgt)
    _append_edge_deleted(runtime, session_id, root_node_id=src, edge_id=edge_id)
    response = client.get(f"/v1/student/sessions/{session_id}")
    assert response.status_code == 200
    assert response.json()["canvas"]["edges"] == []


def test_tb5_node_position_updated_supersedes() -> None:
    client, runtime = _build_client_and_runtime()
    session_id = _start_session(client, runtime)
    node_id = _append_node_created(runtime, session_id)
    _append_node_position(runtime, session_id, node_id=node_id, position_x=123.5, position_y=-7.0)
    response = client.get(f"/v1/student/sessions/{session_id}")
    assert response.status_code == 200
    nodes = response.json()["canvas"]["nodes"]
    positioned = next(node for node in nodes if node["node_id"] == str(node_id))
    assert positioned["position_x"] == 123.5
    assert positioned["position_y"] == -7.0


def test_tb6_wrong_tenant_returns_404() -> None:
    client, runtime = _build_client_and_runtime()
    session_id = _start_session(client, runtime)
    other_user = uuid4()
    runtime.memberships.add_membership(user_id=other_user, tenant_id=uuid4(), role="student")
    other_token = jwt.encode({"sub": str(other_user)}, "test-secret", algorithm="HS256")
    response = client.get(
        f"/v1/student/sessions/{session_id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert response.status_code == 404


def test_tb7_category_invisibility() -> None:
    client, runtime = _build_client_and_runtime()
    session_id = _start_session(client, runtime)
    src = _append_node_created(runtime, session_id)
    tgt = _append_node_created(runtime, session_id)
    _append_edge_created(runtime, session_id, source_node_id=src, target_node_id=tgt)
    response = client.get(f"/v1/student/sessions/{session_id}")
    assert response.status_code == 200
    assert not _has_forbidden_key(response.json())


def test_tb8_recent_still_resolves() -> None:
    client, runtime = _build_client_and_runtime()
    _start_session(client, runtime)
    response = client.get("/v1/student/sessions/recent")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
