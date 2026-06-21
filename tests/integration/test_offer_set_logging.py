from uuid import uuid4

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
    response = client.post(
        "/v1/student/sessions",
        json=_seed_curriculum(runtime),
    )
    assert response.status_code == 201
    return response.json()["session_id"]


def _edge_offer_set_request(session_id: str) -> dict[str, str]:
    return {
        "session_id": session_id,
        "source_node_id": str(uuid4()),
        "thread_context_id": str(uuid4()),
    }


def test_edge_offer_set_logs_created_and_impression_events() -> None:
    client, runtime = _build_client_and_runtime()
    request_body = _edge_offer_set_request(_start_session(client, runtime))
    event_count = len(runtime.event_store.events)

    response = client.post("/v1/student/offer-sets/edge", json=request_body)

    assert response.status_code == 201
    appended_events = runtime.event_store.events[event_count:]
    assert [event["event_type"] for event in appended_events] == [
        "offer_set_created",
        "offer_set_impression",
    ]

    created_event, impression_event = appended_events
    assert created_event["producer"] == "server"
    assert impression_event["producer"] == "server"
    assert str(created_event["tenant_id"]) == str(runtime.tenant_id)
    assert str(created_event["student_id"]) == str(runtime.student_user_id)
    assert created_event["payload"]["session_id"] == request_body["session_id"]
    assert created_event["payload"]["source_node_id"] == request_body["source_node_id"]
    assert created_event["payload"]["launch_method"] == "edge_plus"
    assert created_event["payload"]["mode"] == "discovery"
    assert created_event["payload"]["policy_name"] == "fixture_edge_offer_set"
    assert created_event["payload"]["policy_version"] == "v1"
    assert created_event["payload"]["total_ms"] >= 0
    assert len(created_event["payload"]["options"]) == 3
    assert all(option["rank_position"] >= 1 for option in created_event["payload"]["options"])
    assert all("propensity" in option for option in created_event["payload"]["options"])
    assert all("is_probe" in option for option in created_event["payload"]["options"])
    assert all("randomization_id" in option for option in created_event["payload"]["options"])

    option_ids = [option["option_id"] for option in created_event["payload"]["options"]]
    assert impression_event["payload"] == {
        "offer_set_id": created_event["payload"]["offer_set_id"],
        "session_id": request_body["session_id"],
        "source_node_id": request_body["source_node_id"],
        "visible_option_ids": option_ids,
        "ui_positioning": option_ids,
    }


def test_edge_offer_set_response_hides_measurement_fields() -> None:
    client, runtime = _build_client_and_runtime()
    request_body = _edge_offer_set_request(_start_session(client, runtime))

    response = client.post("/v1/student/offer-sets/edge", json=request_body)

    assert response.status_code == 201
    body = response.json()
    assert not any(
        forbidden in field for field in body for forbidden in FORBIDDEN_ANALYTIC_FIELD_FRAGMENTS
    )
    assert len(body["options"]) == 3
    for option in body["options"]:
        assert set(option) == {"option_id", "text", "rank_position"}
        assert not any(
            forbidden in field
            for field in option
            for forbidden in FORBIDDEN_ANALYTIC_FIELD_FRAGMENTS
        )


def test_edge_offer_set_impression_does_not_enqueue_classify() -> None:
    client, runtime = _build_client_and_runtime()
    request_body = _edge_offer_set_request(_start_session(client, runtime))

    response = client.post("/v1/student/offer-sets/edge", json=request_body)

    assert response.status_code == 201
    assert runtime.job_queue.jobs == []

    offer_set_id = response.json()["offer_set_id"]
    selected_option = response.json()["options"][0]
    choice_response = client.post(
        f"/v1/student/offer-sets/{offer_set_id}/choices",
        json={
            "session_id": request_body["session_id"],
            "source_node_id": request_body["source_node_id"],
            "outcome": "selected",
            "selected_option_id": selected_option["option_id"],
            "selected_option_text": selected_option["text"],
            "thread_context_id": request_body["thread_context_id"],
        },
    )

    assert choice_response.status_code == 202
    classify_jobs = [job for job in runtime.job_queue.jobs if job["job_type"] == "classify"]
    assert len(classify_jobs) == 1
