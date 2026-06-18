from uuid import uuid4

import jwt
from fastapi.testclient import TestClient

FORBIDDEN_STUDENT_RESPONSE_FRAGMENTS = (
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


def _start_session(client: TestClient, runtime) -> str:
    response = client.post("/v1/student/sessions", json=_seed_curriculum(runtime))
    assert response.status_code == 201
    return response.json()["session_id"]


def _select_child_from_source(client: TestClient, session_id: str, source_node_id: str) -> dict:
    offer_request = {
        "session_id": session_id,
        "source_node_id": source_node_id,
        "thread_context_id": str(uuid4()),
    }
    offer_response = client.post("/v1/student/offer-sets/edge", json=offer_request)
    assert offer_response.status_code == 201
    offer_body = offer_response.json()
    selected_option = offer_body["options"][0]

    choice_response = client.post(
        f"/v1/student/offer-sets/{offer_body['offer_set_id']}/choices",
        json={
            "session_id": session_id,
            "source_node_id": source_node_id,
            "outcome": "selected",
            "selected_option_id": selected_option["option_id"],
            "selected_option_text": selected_option["text"],
            "thread_context_id": offer_request["thread_context_id"],
        },
    )
    assert choice_response.status_code == 202
    return choice_response.json()


def _build_two_level_path(client: TestClient, runtime) -> dict[str, str]:
    session_id = _start_session(client, runtime)
    root_node_id = str(uuid4())
    first_child = _select_child_from_source(client, session_id, root_node_id)
    second_child = _select_child_from_source(client, session_id, first_child["child_node_id"])
    return {
        "session_id": session_id,
        "root_node_id": root_node_id,
        "first_child_node_id": first_child["child_node_id"],
        "second_child_node_id": second_child["child_node_id"],
        "first_edge_id": first_child["edge_id"],
        "second_edge_id": second_child["edge_id"],
    }


def _build_branching_path(client: TestClient, runtime) -> dict[str, str]:
    session_id = _start_session(client, runtime)
    root_node_id = str(uuid4())
    first_child = _select_child_from_source(client, session_id, root_node_id)
    sibling_child = _select_child_from_source(client, session_id, root_node_id)
    grandchild = _select_child_from_source(client, session_id, first_child["child_node_id"])
    return {
        "session_id": session_id,
        "root_node_id": root_node_id,
        "first_child_node_id": first_child["child_node_id"],
        "sibling_child_node_id": sibling_child["child_node_id"],
        "grandchild_node_id": grandchild["child_node_id"],
        "first_edge_id": first_child["edge_id"],
        "sibling_edge_id": sibling_child["edge_id"],
        "grandchild_edge_id": grandchild["edge_id"],
    }


def test_delete_node_requires_explicit_confirmation() -> None:
    client, runtime = _build_client_and_runtime()
    path = _build_two_level_path(client, runtime)
    event_count = len(runtime.event_store.events)

    response = client.delete(
        f"/v1/student/sessions/{path['session_id']}/nodes/{path['first_child_node_id']}"
    )

    assert response.status_code == 409
    assert runtime.event_store.events[event_count:] == []


def test_confirmed_node_delete_cascades_descendant_ai_path_events() -> None:
    client, runtime = _build_client_and_runtime()
    path = _build_two_level_path(client, runtime)
    event_count = len(runtime.event_store.events)

    response = client.delete(
        f"/v1/student/sessions/{path['session_id']}/nodes/{path['first_child_node_id']}",
        params={"confirmed": "true"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["session_id"] == path["session_id"]
    assert body["root_node_id"] == path["first_child_node_id"]
    assert body["confirmed"] is True
    assert set(body["deleted_node_ids"]) == {
        path["first_child_node_id"],
        path["second_child_node_id"],
    }
    assert set(body["deleted_edge_ids"]) == {path["first_edge_id"], path["second_edge_id"]}

    appended_events = runtime.event_store.events[event_count:]
    assert [event["event_type"] for event in appended_events] == [
        "edge_deleted",
        "edge_deleted",
        "node_deleted",
    ]
    edge_deleted_events = appended_events[:2]
    assert {event["payload"]["edge_id"] for event in edge_deleted_events} == {
        path["first_edge_id"],
        path["second_edge_id"],
    }
    assert all(
        event["payload"]["deletion_cause"] == "node_cascade" for event in edge_deleted_events
    )
    node_deleted_event = appended_events[-1]
    assert node_deleted_event["payload"]["root_node_id"] == path["first_child_node_id"]
    assert set(node_deleted_event["payload"]["deleted_node_ids"]) == set(body["deleted_node_ids"])
    assert set(node_deleted_event["payload"]["deleted_edge_ids"]) == set(body["deleted_edge_ids"])


def test_confirmed_node_delete_preserves_sibling_ai_path_branch() -> None:
    client, runtime = _build_client_and_runtime()
    path = _build_branching_path(client, runtime)
    event_count = len(runtime.event_store.events)

    response = client.delete(
        f"/v1/student/sessions/{path['session_id']}/nodes/{path['first_child_node_id']}",
        params={"confirmed": "true"},
    )

    assert response.status_code == 200
    body = response.json()
    assert set(body["deleted_node_ids"]) == {
        path["first_child_node_id"],
        path["grandchild_node_id"],
    }
    assert path["sibling_child_node_id"] not in body["deleted_node_ids"]
    assert set(body["deleted_edge_ids"]) == {path["first_edge_id"], path["grandchild_edge_id"]}
    assert path["sibling_edge_id"] not in body["deleted_edge_ids"]

    appended_events = runtime.event_store.events[event_count:]
    deleted_edge_ids = {
        event["payload"]["edge_id"]
        for event in appended_events
        if event["event_type"] == "edge_deleted"
    }
    assert deleted_edge_ids == {path["first_edge_id"], path["grandchild_edge_id"]}


def test_deletion_cascade_response_stays_student_safe() -> None:
    client, runtime = _build_client_and_runtime()
    path = _build_two_level_path(client, runtime)

    response = client.delete(
        f"/v1/student/sessions/{path['session_id']}/nodes/{path['first_child_node_id']}",
        params={"confirmed": "true"},
    )

    assert response.status_code == 200
    body = response.json()
    assert not any(
        forbidden in field for field in body for forbidden in FORBIDDEN_STUDENT_RESPONSE_FRAGMENTS
    )
