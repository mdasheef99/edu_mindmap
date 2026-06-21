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


class FailingJobQueue:
    jobs: list[dict] = []

    def enqueue_classify_from_offer_choice(self, *args, **kwargs):
        raise RuntimeError("simulated enqueue failure")


def _selected_choice_body() -> dict[str, str]:
    return {
        "session_id": str(uuid4()),
        "source_node_id": str(uuid4()),
        "outcome": "selected",
        "selected_option_id": str(uuid4()),
        "selected_option_text": "Why does friction increase with roughness?",
        "thread_context_id": str(uuid4()),
    }


def _dismissed_choice_body() -> dict[str, str]:
    return {
        "session_id": str(uuid4()),
        "source_node_id": str(uuid4()),
        "outcome": "dismissed",
        "thread_context_id": str(uuid4()),
    }


def _start_session(client: TestClient, runtime) -> str:
    response = client.post(
        "/v1/student/sessions",
        json=_seed_curriculum(runtime),
    )
    assert response.status_code == 201
    return response.json()["session_id"]


def _single_event_of_type(runtime, event_type: str):
    events = [event for event in runtime.event_store.events if event["event_type"] == event_type]
    assert len(events) == 1
    return events[0]


def test_offer_choice_selected_appends_offer_set_choice() -> None:
    """T6: selected offer choice must append offer_set_choice."""
    client, runtime = _build_client_and_runtime()
    session_id = _start_session(client, runtime)
    offer_set_id = uuid4()
    request_body = _selected_choice_body() | {"session_id": session_id}

    response = client.post(
        f"/v1/student/offer-sets/{offer_set_id}/choices",
        json=request_body,
    )

    assert response.status_code == 202
    choice_events = [e for e in runtime.event_store.events if e["event_type"] == "offer_set_choice"]
    assert len(choice_events) == 1
    event = choice_events[0]

    assert event["event_type"] == "offer_set_choice"
    assert event["producer"] == "server"
    assert str(event["tenant_id"]) == str(runtime.tenant_id)
    assert str(event["student_id"]) == str(runtime.student_user_id)
    assert str(event["offer_set_id"]) == str(offer_set_id)
    assert event["payload"] == {
        "offer_set_id": str(offer_set_id),
        "session_id": request_body["session_id"],
        "source_node_id": request_body["source_node_id"],
        "outcome": "selected",
        "selected_option_id": request_body["selected_option_id"],
        "selected_option_text": request_body["selected_option_text"],
        "thread_context_id": request_body["thread_context_id"],
    }


def test_offer_choice_selected_enqueues_classify_job() -> None:
    """T7: selected offer choice must enqueue classify after append."""
    client, runtime = _build_client_and_runtime()
    session_id = _start_session(client, runtime)
    offer_set_id = uuid4()
    request_body = _selected_choice_body() | {"session_id": session_id}

    response = client.post(
        f"/v1/student/offer-sets/{offer_set_id}/choices",
        json=request_body,
    )

    assert response.status_code == 202
    assert len(runtime.job_queue.jobs) == 1
    job = runtime.job_queue.jobs[0]
    choice_events = [e for e in runtime.event_store.events if e["event_type"] == "offer_set_choice"]
    assert len(choice_events) == 1
    event = choice_events[0]

    assert job["job_type"] == "classify"
    assert job["status"] == "queued"
    assert str(job["tenant_id"]) == str(runtime.tenant_id)
    assert job["payload"] == {
        "event_id": str(event["event_id"]),
        "student_user_id": str(runtime.student_user_id),
        "session_id": request_body["session_id"],
        "offer_set_id": str(offer_set_id),
        "selected_option_id": request_body["selected_option_id"],
        "selected_option_text": request_body["selected_option_text"],
        "thread_context_id": request_body["thread_context_id"],
    }


def test_offer_choice_dismissed_does_not_enqueue_classify() -> None:
    """T8: dismissed/no-selection outcome must not enqueue classify."""
    client, runtime = _build_client_and_runtime()
    session_id = _start_session(client, runtime)
    offer_set_id = uuid4()

    response = client.post(
        f"/v1/student/offer-sets/{offer_set_id}/choices",
        json=_dismissed_choice_body() | {"session_id": session_id},
    )

    assert response.status_code == 202
    choice_events = [e for e in runtime.event_store.events if e["event_type"] == "offer_set_choice"]
    assert len(choice_events) == 1
    assert choice_events[0]["payload"]["outcome"] == "dismissed"
    assert runtime.job_queue.jobs == []


def test_offer_choice_response_returns_with_classify_still_queued() -> None:
    """T17: student response must not wait for classify to run."""
    client, runtime = _build_client_and_runtime()
    session_id = _start_session(client, runtime)
    offer_set_id = uuid4()
    request_body = _selected_choice_body() | {"session_id": session_id}

    response = client.post(
        f"/v1/student/offer-sets/{offer_set_id}/choices",
        json=request_body,
    )

    assert response.status_code == 202
    body = response.json()
    assert body["offer_set_id"] == str(offer_set_id)
    assert body["outcome"] == "selected"
    assert body["recorded"] is True
    assert body["child_node_type"] == "ai"
    assert body["child_node_id"]
    assert body["edge_id"]
    assert body["child_content"] == f"Explore: {request_body['selected_option_text']}"
    assert runtime.job_queue.jobs[0]["status"] == "queued"
    assert not any(
        event["event_type"] == "question_classified" for event in runtime.event_store.events
    )
    assert runtime.analytic_question_classifications.rows == []


def test_offer_choice_append_and_classify_enqueue_are_atomic() -> None:
    """T22: selected choice append and classify enqueue must commit or rollback together."""
    from datetime import datetime, timezone

    from app.domain.student.offer_choices import OfferChoiceRequest
    from app.main import SessionRuntime

    tenant_id = uuid4()
    student_user_id = uuid4()
    session_id = uuid4()
    runtime = SessionRuntime.for_testing(
        tenant_id=tenant_id,
        student_user_id=student_user_id,
        job_queue=FailingJobQueue(),
    )
    runtime.student_sessions.upsert(
        {
            "session_id": session_id,
            "tenant_id": tenant_id,
            "student_user_id": student_user_id,
            "exam_id": uuid4(),
            "subject_id": uuid4(),
            "chapter_id": uuid4(),
            "concept_entry_id": uuid4(),
            "chapter_analysis_id": uuid4(),
            "status": "active",
            "last_active_node_id": None,
            "started_at": datetime.now(timezone.utc),
            "last_active_at": datetime.now(timezone.utc),
            "closed_at": None,
        }
    )
    payload = OfferChoiceRequest.model_validate(
        _selected_choice_body() | {"session_id": str(session_id)}
    )

    try:
        runtime.record_offer_choice(offer_set_id=uuid4(), payload=payload)
    except RuntimeError as exc:
        assert str(exc) == "simulated enqueue failure"
    else:
        raise AssertionError("enqueue failure should bubble so the request transaction rolls back")

    assert runtime.event_store.events == []


def test_duplicate_offer_choice_does_not_double_enqueue_classify() -> None:
    """T23: duplicate selected-choice retry must not double-enqueue classify."""
    client, runtime = _build_client_and_runtime()
    session_id = _start_session(client, runtime)
    offer_set_id = uuid4()
    request_body = _selected_choice_body() | {"session_id": session_id}

    first = client.post(f"/v1/student/offer-sets/{offer_set_id}/choices", json=request_body)
    second = client.post(f"/v1/student/offer-sets/{offer_set_id}/choices", json=request_body)

    assert first.status_code == 202
    assert second.status_code == 202
    classify_jobs = [job for job in runtime.job_queue.jobs if job["job_type"] == "classify"]
    assert len(classify_jobs) == 1


def test_mobile_supplied_tenant_id_is_ignored() -> None:
    """T25: mobile-supplied tenant_id must never override backend-resolved tenant."""
    client, runtime = _build_client_and_runtime()
    attacker_tenant_id = uuid4()

    response = client.post(
        "/v1/student/sessions",
        json=_seed_curriculum(runtime) | {"tenant_id": str(attacker_tenant_id)},
    )

    assert response.status_code == 201
    event = _single_event_of_type(runtime, "session_started")
    assert event["tenant_id"] == runtime.tenant_id
    assert event["tenant_id"] != attacker_tenant_id
