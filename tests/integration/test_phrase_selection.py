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


def _phrase_offer_request(session_id: str) -> dict[str, str | int]:
    return {
        "session_id": session_id,
        "source_node_id": str(uuid4()),
        "thread_context_id": str(uuid4()),
        "selected_phrase": "closed circuit",
        "source_excerpt": "Electric current flows through a closed circuit.",
        "selection_start": 33,
        "selection_end": 47,
    }


def test_reader_phrase_offer_set_logs_phrase_offer_and_impression_events() -> None:
    client, runtime = _build_client_and_runtime()
    request_body = _phrase_offer_request(_start_session(client, runtime))
    event_count = len(runtime.event_store.events)

    response = client.post("/v1/student/offer-sets/phrase", json=request_body)

    assert response.status_code == 201
    appended_events = runtime.event_store.events[event_count:]
    assert [event["event_type"] for event in appended_events] == [
        "phrase_selected",
        "phrase_offer_set_created",
        "offer_set_impression",
    ]

    phrase_event, created_event, impression_event = appended_events
    assert phrase_event["producer"] == "server"
    assert created_event["producer"] == "server"
    assert impression_event["producer"] == "server"
    assert str(created_event["tenant_id"]) == str(runtime.tenant_id)
    assert str(created_event["student_id"]) == str(runtime.student_user_id)
    assert phrase_event["payload"]["selected_phrase"] == "closed circuit"
    assert phrase_event["payload"]["source_excerpt"] == request_body["source_excerpt"]
    assert created_event["payload"]["launch_method"] == "phrase_selection"
    assert created_event["payload"]["selected_phrase"] == "closed circuit"
    assert created_event["payload"]["source_phrase_event_id"] == str(phrase_event["event_id"])
    assert len(created_event["payload"]["options"]) == 5

    option_ids = [option["option_id"] for option in created_event["payload"]["options"]]
    assert impression_event["payload"] == {
        "offer_set_id": created_event["payload"]["offer_set_id"],
        "session_id": request_body["session_id"],
        "source_node_id": request_body["source_node_id"],
        "visible_option_ids": option_ids,
        "ui_positioning": option_ids,
    }


def test_reader_phrase_offer_response_is_student_safe_and_bottom_sheet_ready() -> None:
    client, runtime = _build_client_and_runtime()
    request_body = _phrase_offer_request(_start_session(client, runtime))

    response = client.post("/v1/student/offer-sets/phrase", json=request_body)

    assert response.status_code == 201
    body = response.json()
    assert body["launch_method"] == "phrase_selection"
    assert body["selected_phrase"] == "closed circuit"
    assert set(body) == {
        "offer_set_id",
        "session_id",
        "source_node_id",
        "thread_context_id",
        "launch_method",
        "selected_phrase",
        "actions",
        "recommended_questions",
    }
    assert [action["action_type"] for action in body["actions"]] == ["elaborate", "custom"]
    assert len(body["recommended_questions"]) == 3

    for field in body:
        assert not any(forbidden in field for forbidden in FORBIDDEN_STUDENT_RESPONSE_FRAGMENTS)
    for option in body["actions"] + body["recommended_questions"]:
        assert set(option) == {"option_id", "text", "rank_position", "action_type"}
        assert not any(
            forbidden in field
            for field in option
            for forbidden in FORBIDDEN_STUDENT_RESPONSE_FRAGMENTS
        )


def test_reader_phrase_offer_set_is_tenant_and_student_scoped() -> None:
    client, runtime = _build_client_and_runtime()
    session_id = _start_session(client, runtime)
    other_user_id = uuid4()
    runtime.memberships.add_membership(user_id=other_user_id, tenant_id=uuid4(), role="student")
    token = jwt.encode({"sub": str(other_user_id)}, runtime.jwt_secret, algorithm="HS256")
    client.headers["Authorization"] = f"Bearer {token}"

    response = client.post("/v1/student/offer-sets/phrase", json=_phrase_offer_request(session_id))

    assert response.status_code == 404
    assert [event["event_type"] for event in runtime.event_store.events].count(
        "phrase_selected"
    ) == 0


def test_selected_phrase_offer_choice_branches_and_dismissed_choice_does_not_classify() -> None:
    client, runtime = _build_client_and_runtime()
    request_body = _phrase_offer_request(_start_session(client, runtime))
    offer_response = client.post("/v1/student/offer-sets/phrase", json=request_body)
    assert offer_response.status_code == 201
    recommended_option = offer_response.json()["recommended_questions"][0]
    event_count = len(runtime.event_store.events)

    selected_response = client.post(
        f"/v1/student/offer-sets/{offer_response.json()['offer_set_id']}/choices",
        json={
            "session_id": request_body["session_id"],
            "source_node_id": request_body["source_node_id"],
            "outcome": "selected",
            "selected_option_id": recommended_option["option_id"],
            "selected_option_text": recommended_option["text"],
            "thread_context_id": request_body["thread_context_id"],
        },
    )

    assert selected_response.status_code == 202
    assert [event["event_type"] for event in runtime.event_store.events[event_count:]] == [
        "offer_set_choice",
        "node_created",
        "edge_created",
    ]
    assert selected_response.json()["child_node_type"] == "ai"
    assert len([job for job in runtime.job_queue.jobs if job["job_type"] == "classify"]) == 1

    dismissed_offer = client.post("/v1/student/offer-sets/phrase", json=request_body)
    assert dismissed_offer.status_code == 201
    event_count = len(runtime.event_store.events)
    job_count = len(runtime.job_queue.jobs)
    dismissed_response = client.post(
        f"/v1/student/offer-sets/{dismissed_offer.json()['offer_set_id']}/choices",
        json={
            "session_id": request_body["session_id"],
            "source_node_id": request_body["source_node_id"],
            "outcome": "dismissed",
            "thread_context_id": request_body["thread_context_id"],
        },
    )

    assert dismissed_response.status_code == 202
    assert [event["event_type"] for event in runtime.event_store.events[event_count:]] == [
        "offer_set_choice"
    ]
    assert len(runtime.job_queue.jobs) == job_count
