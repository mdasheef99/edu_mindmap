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


def _selected_choice_body(session_id: str) -> dict[str, str]:
    return {
        "session_id": session_id,
        "source_node_id": str(uuid4()),
        "outcome": "selected",
        "selected_option_id": str(uuid4()),
        "selected_option_text": "Why does roughness increase friction?",
        "thread_context_id": str(uuid4()),
    }


def test_classify_worker_claims_job_with_skip_locked() -> None:
    """T9: classify worker must claim queued work with SKIP LOCKED semantics."""
    from app.workers.classify import ClassifyWorker

    client, runtime = _build_client_and_runtime()
    session_id = _start_session(client, runtime)
    offer_set_id = uuid4()

    response = client.post(
        f"/v1/student/offer-sets/{offer_set_id}/choices",
        json=_selected_choice_body(session_id),
    )

    assert response.status_code == 202
    worker = ClassifyWorker(runtime)

    claimed_job = worker.claim_next(worker_id="worker-a")

    assert claimed_job is not None
    assert claimed_job["job_type"] == "classify"
    assert claimed_job["status"] == "running"
    assert claimed_job["locked_by"] == "worker-a"
    assert worker.claim_next(worker_id="worker-b") is None


def test_classify_worker_appends_question_classified() -> None:
    """T10: classify worker must append question_classified and project analytic output."""
    from app.workers.classify import ClassifyWorker

    client, runtime = _build_client_and_runtime()
    session_id = _start_session(client, runtime)
    offer_set_id = uuid4()
    runtime.grant_behavioral_analytics_consent()

    response = client.post(
        f"/v1/student/offer-sets/{offer_set_id}/choices",
        json=_selected_choice_body(session_id),
    )

    assert response.status_code == 202
    worker = ClassifyWorker(runtime)

    classified_event = worker.run_next(worker_id="worker-a")

    assert classified_event is not None
    assert runtime.event_store.events[-1]["event_type"] == "question_classified"
    assert runtime.event_store.events[-1]["producer"] == "worker"
    assert runtime.event_store.events[-1]["prompt_version"]
    assert runtime.event_store.events[-1]["model_id"]
    assert runtime.event_store.events[-1]["projection_version"]
    assert len(runtime.analytic_question_classifications.rows) == 1
    row = runtime.analytic_question_classifications.rows[0]
    assert str(row["tenant_id"]) == str(runtime.tenant_id)
    assert str(row["student_user_id"]) == str(runtime.student_user_id)
    assert str(row["session_id"]) == session_id
    assert str(row["offer_set_id"]) == str(offer_set_id)


def test_question_classified_not_visible_to_student_api() -> None:
    """T11: question_classified must stay out of student-visible state."""
    from app.workers.classify import ClassifyWorker

    client, runtime = _build_client_and_runtime()
    session_id = _start_session(client, runtime)
    offer_set_id = uuid4()
    runtime.grant_behavioral_analytics_consent()

    response = client.post(
        f"/v1/student/offer-sets/{offer_set_id}/choices",
        json=_selected_choice_body(session_id),
    )

    assert response.status_code == 202
    ClassifyWorker(runtime).run_next(worker_id="worker-a")

    session_row = runtime.student_sessions.sessions[session_id]

    assert len(runtime.analytic_question_classifications.rows) == 1
    assert not any(
        forbidden in field
        for field in session_row
        for forbidden in FORBIDDEN_ANALYTIC_FIELD_FRAGMENTS
    )


def test_question_classified_row_carries_version_stamps() -> None:
    """T19: analytic row must carry version stamps and source lineage."""
    from app.workers.classify import ClassifyWorker

    client, runtime = _build_client_and_runtime()
    session_id = _start_session(client, runtime)
    offer_set_id = uuid4()
    runtime.grant_behavioral_analytics_consent()

    response = client.post(
        f"/v1/student/offer-sets/{offer_set_id}/choices",
        json=_selected_choice_body(session_id),
    )

    assert response.status_code == 202
    matching_events = [
        e for e in runtime.event_store.events if e["event_type"] == "offer_set_choice"
    ]
    assert matching_events, "No offer_set_choice event found"
    source_event = matching_events[0]
    classified_event = ClassifyWorker(runtime).run_next(worker_id="worker-a")
    row = runtime.analytic_question_classifications.rows[0]

    assert classified_event is not None
    assert row["projection_version"] == classified_event["projection_version"]
    assert row["prompt_version"] == classified_event["prompt_version"]
    assert row["model_id"] == classified_event["model_id"]
    assert row["source_event_id"] == source_event["event_id"]
    assert row["source_event_type"] == "offer_set_choice"
    assert (
        row["chapter_analysis_id"]
        == runtime.student_sessions.sessions[session_id]["chapter_analysis_id"]
    )


def test_classify_worker_skips_analytic_projection_without_consent() -> None:
    """T26: no behavioral_analytics consent means no analytic_rm projection write."""
    from app.workers.classify import ClassifyWorker

    client, runtime = _build_client_and_runtime()
    session_id = _start_session(client, runtime)
    offer_set_id = uuid4()

    response = client.post(
        f"/v1/student/offer-sets/{offer_set_id}/choices",
        json=_selected_choice_body(session_id),
    )

    assert response.status_code == 202
    classified_event = ClassifyWorker(runtime).run_next(worker_id="worker-a")

    assert classified_event is not None
    assert runtime.event_store.events[-1]["event_type"] == "question_classified"
    assert runtime.job_queue.jobs[0]["status"] == "done"
    assert runtime.analytic_question_classifications.rows == []
