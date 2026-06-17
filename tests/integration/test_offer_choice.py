from uuid import uuid4

from fastapi.testclient import TestClient


def _build_client_and_runtime():
    from app.main import SessionRuntime, create_app

    runtime = SessionRuntime.for_testing(
        tenant_id=uuid4(),
        student_user_id=uuid4(),
    )
    return TestClient(create_app(runtime=runtime)), runtime


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


def _start_session(client: TestClient) -> str:
    response = client.post(
        "/v1/student/sessions",
        json={
            "exam_id": str(uuid4()),
            "subject_id": str(uuid4()),
            "chapter_id": str(uuid4()),
            "concept_entry_id": str(uuid4()),
            "chapter_analysis_id": str(uuid4()),
        },
    )
    assert response.status_code == 201
    return response.json()["session_id"]


def test_offer_choice_selected_appends_offer_set_choice() -> None:
    """T6: selected offer choice must append offer_set_choice."""
    client, runtime = _build_client_and_runtime()
    offer_set_id = uuid4()
    request_body = _selected_choice_body()

    response = client.post(
        f"/v1/student/offer-sets/{offer_set_id}/choices",
        json=request_body,
    )

    assert response.status_code == 202
    assert len(runtime.event_store.events) == 1
    event = runtime.event_store.events[0]

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
    offer_set_id = uuid4()
    request_body = _selected_choice_body()

    response = client.post(
        f"/v1/student/offer-sets/{offer_set_id}/choices",
        json=request_body,
    )

    assert response.status_code == 202
    assert len(runtime.job_queue.jobs) == 1
    job = runtime.job_queue.jobs[0]
    event = runtime.event_store.events[0]

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
    offer_set_id = uuid4()

    response = client.post(
        f"/v1/student/offer-sets/{offer_set_id}/choices",
        json=_dismissed_choice_body(),
    )

    assert response.status_code == 202
    assert len(runtime.event_store.events) == 1
    assert runtime.event_store.events[0]["event_type"] == "offer_set_choice"
    assert runtime.event_store.events[0]["payload"]["outcome"] == "dismissed"
    assert runtime.job_queue.jobs == []


def test_offer_choice_response_returns_with_classify_still_queued() -> None:
    """T17: student response must not wait for classify to run."""
    client, runtime = _build_client_and_runtime()
    session_id = _start_session(client)
    offer_set_id = uuid4()
    request_body = _selected_choice_body() | {"session_id": session_id}

    response = client.post(
        f"/v1/student/offer-sets/{offer_set_id}/choices",
        json=request_body,
    )

    assert response.status_code == 202
    assert response.json() == {
        "offer_set_id": str(offer_set_id),
        "outcome": "selected",
        "recorded": True,
    }
    assert runtime.job_queue.jobs[0]["status"] == "queued"
    assert not any(
        event["event_type"] == "question_classified"
        for event in runtime.event_store.events
    )
    assert runtime.analytic_question_classifications.rows == []


def test_offer_choice_append_and_classify_enqueue_are_atomic() -> None:
    """T22: selected choice append and classify enqueue must commit or rollback together."""
    from app.domain.student.offer_choices import OfferChoiceRequest
    from app.main import SessionRuntime

    runtime = SessionRuntime.for_testing(
        tenant_id=uuid4(),
        student_user_id=uuid4(),
        job_queue=FailingJobQueue(),
    )
    payload = OfferChoiceRequest.model_validate(_selected_choice_body())

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
    session_id = _start_session(client)
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
        json={
            "tenant_id": str(attacker_tenant_id),
            "exam_id": str(uuid4()),
            "subject_id": str(uuid4()),
            "chapter_id": str(uuid4()),
            "concept_entry_id": str(uuid4()),
            "chapter_analysis_id": str(uuid4()),
        },
    )

    assert response.status_code == 201
    event = runtime.event_store.events[-1]
    assert event["tenant_id"] == runtime.tenant_id
    assert event["tenant_id"] != attacker_tenant_id