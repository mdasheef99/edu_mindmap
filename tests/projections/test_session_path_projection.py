from uuid import uuid4

import jwt
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


def _seed_curriculum(runtime) -> dict[str, str]:
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
        "chapter_analysis_id": str(chapter_analysis_id),
    }


def _start_session(client: TestClient, seed: dict[str, str]) -> dict[str, str]:
    response = client.post(
        "/v1/student/sessions",
        json={
            "exam_id": seed["exam_id"],
            "subject_id": seed["subject_id"],
            "chapter_id": seed["chapter_id"],
            "concept_entry_id": seed["concept_entry_id"],
        },
    )
    assert response.status_code == 201
    return response.json()


def _record_offer_choice(
    client: TestClient, session_id: str, source_node_id: str, *, outcome: str
) -> dict[str, str | None]:
    offer_request = {
        "session_id": session_id,
        "source_node_id": source_node_id,
        "thread_context_id": str(uuid4()),
    }
    offer_response = client.post("/v1/student/offer-sets/edge", json=offer_request)
    assert offer_response.status_code == 201
    offer_body = offer_response.json()
    selected_option = offer_body["options"][0]
    choice_payload = {
        "session_id": session_id,
        "source_node_id": source_node_id,
        "outcome": outcome,
        "thread_context_id": offer_request["thread_context_id"],
    }
    if outcome == "selected":
        choice_payload |= {
            "selected_option_id": selected_option["option_id"],
            "selected_option_text": selected_option["text"],
        }
    response = client.post(
        f"/v1/student/offer-sets/{offer_body['offer_set_id']}/choices",
        json=choice_payload,
    )
    assert response.status_code == 202
    body = response.json()
    return {
        "offer_set_id": offer_body["offer_set_id"],
        "source_node_id": source_node_id,
        "thread_context_id": offer_request["thread_context_id"],
        "outcome": outcome,
        "selected_option_id": selected_option["option_id"] if outcome == "selected" else None,
        "selected_option_text": selected_option["text"] if outcome == "selected" else None,
        "child_node_id": body.get("child_node_id"),
        "edge_id": body.get("edge_id"),
    }


def _build_session_event_stream(
    client: TestClient, runtime
) -> tuple[dict[str, str], dict[str, str | None]]:
    seed = _seed_curriculum(runtime)
    session = _start_session(client, seed)
    root_node_id = str(
        next(
            event["node_id"]
            for event in runtime.event_store.events
            if event["event_type"] == "node_created"
            and str(event["session_id"]) == session["session_id"]
        )
    )
    first = _record_offer_choice(client, session["session_id"], root_node_id, outcome="selected")
    second = _record_offer_choice(
        client, session["session_id"], str(first["child_node_id"]), outcome="selected"
    )
    third = _record_offer_choice(client, session["session_id"], root_node_id, outcome="selected")
    dismissed = _record_offer_choice(
        client, session["session_id"], str(third["child_node_id"]), outcome="dismissed"
    )
    delete_response = client.delete(
        f"/v1/student/sessions/{session['session_id']}/nodes/{first['child_node_id']}",
        params={"confirmed": "true"},
    )
    assert delete_response.status_code == 200
    return session | seed, {
        "root_node_id": root_node_id,
        "first_child_node_id": str(first["child_node_id"]),
        "second_child_node_id": str(second["child_node_id"]),
        "third_child_node_id": str(third["child_node_id"]),
        "third_edge_id": str(third["edge_id"]),
        "dismissed_offer_set_id": str(dismissed["offer_set_id"]),
    }


def test_session_path_rebuild_tracks_context_history_and_active_structure() -> None:
    from app.projections.session_path import rebuild_session_path_projection

    client, runtime = _build_client_and_runtime()
    session, expected = _build_session_event_stream(client, runtime)

    store = rebuild_session_path_projection(runtime.event_store.events)
    path = store.get_for_tenant_and_student(
        session["session_id"], runtime.tenant_id, runtime.student_user_id
    )

    assert path is not None
    assert str(path["session_id"]) == session["session_id"]
    assert str(path["concept_entry_id"]) == session["concept_entry_id"]
    assert [entry["outcome"] for entry in path["offer_history"]] == [
        "selected",
        "selected",
        "selected",
        "dismissed",
    ]
    assert str(path["offer_history"][-1]["offer_set_id"]) == expected["dismissed_offer_set_id"]
    assert [str(node["node_id"]) for node in path["created_path_nodes"]] == [
        expected["root_node_id"],
        expected["first_child_node_id"],
        expected["second_child_node_id"],
        expected["third_child_node_id"],
    ]
    assert [str(node["node_id"]) for node in path["active_path_nodes"]] == [
        expected["root_node_id"],
        expected["third_child_node_id"],
    ]
    assert [str(edge["edge_id"]) for edge in path["active_path_edges"]] == [
        expected["third_edge_id"]
    ]


def test_session_path_projection_is_byte_identical_and_idempotent() -> None:
    from app.projections.session_path import (
        InMemorySessionPathProjectionStore,
        apply_session_path_projection_events,
        rebuild_session_path_projection,
    )

    client, runtime = _build_client_and_runtime()
    _build_session_event_stream(client, runtime)

    store = InMemorySessionPathProjectionStore()
    apply_session_path_projection_events(store, runtime.event_store.events)
    first_snapshot = store.snapshot_bytes()
    apply_session_path_projection_events(store, runtime.event_store.events)

    assert store.snapshot_bytes() == first_snapshot
    assert (
        rebuild_session_path_projection(runtime.event_store.events).snapshot_bytes()
        == first_snapshot
    )
