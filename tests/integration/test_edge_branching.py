from datetime import datetime, timezone
from uuid import UUID, uuid4

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
    "randomization",
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


def _create_edge_offer_set(client: TestClient, session_id: str) -> tuple[dict, dict]:
    request_body = {
        "session_id": session_id,
        "source_node_id": str(uuid4()),
        "thread_context_id": str(uuid4()),
    }
    response = client.post("/v1/student/offer-sets/edge", json=request_body)
    assert response.status_code == 201
    return request_body, response.json()


def test_selected_edge_offer_choice_creates_child_ai_path_events() -> None:
    client, runtime = _build_client_and_runtime()
    session_id = _start_session(client, runtime)
    offer_request, offer_response = _create_edge_offer_set(client, session_id)
    selected_option = offer_response["options"][0]
    event_count = len(runtime.event_store.events)

    response = client.post(
        f"/v1/student/offer-sets/{offer_response['offer_set_id']}/choices",
        json={
            "session_id": session_id,
            "source_node_id": offer_request["source_node_id"],
            "outcome": "selected",
            "selected_option_id": selected_option["option_id"],
            "selected_option_text": selected_option["text"],
            "thread_context_id": offer_request["thread_context_id"],
        },
    )

    assert response.status_code == 202
    body = response.json()
    appended_events = runtime.event_store.events[event_count:]
    assert [event["event_type"] for event in appended_events] == [
        "offer_set_choice",
        "node_created",
        "edge_created",
    ]

    choice_event, node_event, edge_event = appended_events
    assert str(node_event["payload"]["node_id"]) == body["child_node_id"]
    assert node_event["payload"]["node_type"] == "ai"
    assert node_event["payload"]["content"] == body["child_content"]
    assert node_event["payload"]["source_offer_set_id"] == offer_response["offer_set_id"]
    assert node_event["payload"]["source_option_id"] == selected_option["option_id"]
    assert node_event["payload"]["thread_context_id"] == offer_request["thread_context_id"]

    assert str(edge_event["payload"]["edge_id"]) == body["edge_id"]
    assert edge_event["payload"]["edge_kind"] == "ai_path"
    assert edge_event["payload"]["source_node_id"] == offer_request["source_node_id"]
    assert edge_event["payload"]["target_node_id"] == body["child_node_id"]
    assert edge_event["payload"]["created_by"] == "offer_set_choice"
    assert edge_event["payload"]["source_offer_set_id"] == offer_response["offer_set_id"]
    assert edge_event["payload"]["source_choice_event_id"] == str(choice_event["event_id"])


def test_dismissed_edge_offer_choice_does_not_create_child_path() -> None:
    client, runtime = _build_client_and_runtime()
    session_id = _start_session(client, runtime)
    offer_request, offer_response = _create_edge_offer_set(client, session_id)
    event_count = len(runtime.event_store.events)

    response = client.post(
        f"/v1/student/offer-sets/{offer_response['offer_set_id']}/choices",
        json={
            "session_id": session_id,
            "source_node_id": offer_request["source_node_id"],
            "outcome": "dismissed",
            "thread_context_id": offer_request["thread_context_id"],
        },
    )

    assert response.status_code == 202
    appended_events = runtime.event_store.events[event_count:]
    assert [event["event_type"] for event in appended_events] == ["offer_set_choice"]
    assert runtime.job_queue.jobs == []


def _seed_node_created_events(runtime, session_id: str, count: int) -> None:
    """Append `count` in-scope node_created events directly to the event store.

    Used to drive the session to the CANVAS_NODE_HARD_LIMIT without exercising the full
    offer-choice path for each node. Scope (tenant_id/student_id/session_id) matches the
    auth-resolved identity so the workflow's active-node count includes them.
    """
    session_uuid = UUID(session_id)
    for _ in range(count):
        node_id = uuid4()
        runtime.event_store.append(
            {
                "event_id": uuid4(),
                "event_type": "node_created",
                "event_version": 1,
                "tenant_id": runtime.tenant_id,
                "actor_user_id": runtime.student_user_id,
                "student_id": runtime.student_user_id,
                "session_id": session_uuid,
                "node_id": node_id,
                "occurred_at": datetime.now(timezone.utc),
                "payload": {
                    "node_id": str(node_id),
                    "session_id": session_id,
                    "node_type": "ai",
                    "content": "Explore: seeded",
                    "source_node_id": str(uuid4()),
                    "source_offer_set_id": str(uuid4()),
                    "source_option_id": str(uuid4()),
                    "source_option_text": "seeded",
                    "thread_context_id": str(uuid4()),
                },
            },
            producer="server",
        )


def test_hard_limit_blocks_node_creation_at_65() -> None:
    """T6 (§11): at CANVAS_NODE_HARD_LIMIT active nodes the choice endpoint returns 409
    and appends no node_created event."""
    from app.canvas.limits import canvas_node_hard_limit

    client, runtime = _build_client_and_runtime()
    session_id = _start_session(client, runtime)
    offer_request, offer_response = _create_edge_offer_set(client, session_id)
    selected_option = offer_response["options"][0]

    _seed_node_created_events(runtime, session_id, canvas_node_hard_limit())
    event_count = len(runtime.event_store.events)
    node_created_before = sum(
        1 for event in runtime.event_store.events if event["event_type"] == "node_created"
    )

    response = client.post(
        f"/v1/student/offer-sets/{offer_response['offer_set_id']}/choices",
        json={
            "session_id": session_id,
            "source_node_id": offer_request["source_node_id"],
            "outcome": "selected",
            "selected_option_id": selected_option["option_id"],
            "selected_option_text": selected_option["text"],
            "thread_context_id": offer_request["thread_context_id"],
        },
    )

    assert response.status_code == 409
    # No node_created appended; the rejected choice leaves the event log unchanged.
    assert len(runtime.event_store.events) == event_count
    node_created_after = sum(
        1 for event in runtime.event_store.events if event["event_type"] == "node_created"
    )
    assert node_created_after == node_created_before
    assert runtime.job_queue.jobs == []
    body = response.json()
    assert not any(
        forbidden in str(value)
        for value in body.values()
        for forbidden in FORBIDDEN_STUDENT_RESPONSE_FRAGMENTS
    )


def test_edge_branching_response_stays_student_safe() -> None:
    client, runtime = _build_client_and_runtime()
    session_id = _start_session(client, runtime)
    offer_request, offer_response = _create_edge_offer_set(client, session_id)
    selected_option = offer_response["options"][0]

    response = client.post(
        f"/v1/student/offer-sets/{offer_response['offer_set_id']}/choices",
        json={
            "session_id": session_id,
            "source_node_id": offer_request["source_node_id"],
            "outcome": "selected",
            "selected_option_id": selected_option["option_id"],
            "selected_option_text": selected_option["text"],
            "thread_context_id": offer_request["thread_context_id"],
        },
    )

    assert response.status_code == 202
    body = response.json()
    assert body["child_node_type"] == "ai"
    assert not any(
        forbidden in field for field in body for forbidden in FORBIDDEN_STUDENT_RESPONSE_FRAGMENTS
    )
