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


def _token(user_id, secret: str = "test-secret") -> str:
    return jwt.encode({"sub": str(user_id)}, secret, algorithm="HS256")


def _build_client_and_runtime(*, tenant_id=None, student_user_id=None, shared=None):
    from app.main import SessionRuntime, create_app

    resolved_tenant_id = tenant_id or uuid4()
    resolved_student_id = student_user_id or uuid4()
    runtime = SessionRuntime.for_testing(
        tenant_id=resolved_tenant_id,
        student_user_id=resolved_student_id,
        **(shared or {}),
    )
    runtime.memberships.add_membership(
        user_id=resolved_student_id,
        tenant_id=resolved_tenant_id,
        role="student",
    )
    client = TestClient(create_app(runtime=runtime))
    client.headers["Authorization"] = f"Bearer {_token(resolved_student_id, runtime.jwt_secret)}"
    return client, runtime


def _shared_components() -> dict[str, object]:
    from app.events.store import InMemoryEventStore
    from app.projections.question_classifications import (
        InMemoryQuestionClassificationProjectionStore,
    )
    from app.projections.student_sessions import InMemoryStudentSessionProjectionStore
    from app.tenancy.pool import InMemoryTenantConnectionPool
    from app.workers.queue import InMemoryJobQueue

    session_store = InMemoryStudentSessionProjectionStore()
    return {
        "event_store": InMemoryEventStore(),
        "job_queue": InMemoryJobQueue(),
        "student_sessions": session_store,
        "analytic_question_classifications": InMemoryQuestionClassificationProjectionStore(),
        "tenant_pool": InMemoryTenantConnectionPool(session_store),
    }


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
    chapter_row = runtime.curriculum.chapters[str(chapter_id)]
    return {
        "exam_id": str(chapter_row["exam_id"]),
        "subject_id": str(chapter_row["subject_id"]),
        "chapter_id": str(chapter_id),
        "concept_entry_id": str(concept_id),
    }


def _start_session(client: TestClient, runtime) -> dict:
    response = client.post("/v1/student/sessions", json=_seed_curriculum(runtime))
    assert response.status_code == 201
    return response.json()


def _assert_no_analytic_fields(payload: dict) -> None:
    assert not any(
        forbidden in field for field in payload for forbidden in FORBIDDEN_ANALYTIC_FIELD_FRAGMENTS
    )


def test_recent_sessions_returns_latest_five_owned_sessions_without_analytic_fields() -> None:
    """Phase 3 SDD §8 T1: recent list powers dashboard re-entry without leaks."""
    client, runtime = _build_client_and_runtime()
    owned_sessions = [_start_session(client, runtime)["session_id"] for _ in range(6)]
    other_student = uuid4()
    runtime.memberships.add_membership(
        user_id=other_student,
        tenant_id=runtime.tenant_id,
        role="student",
    )
    client.headers["Authorization"] = f"Bearer {_token(other_student, runtime.jwt_secret)}"
    other_session_id = _start_session(client, runtime)["session_id"]
    client.headers["Authorization"] = (
        f"Bearer {_token(runtime.student_user_id, runtime.jwt_secret)}"
    )

    response = client.get("/v1/student/sessions/recent")

    assert response.status_code == 200
    body = response.json()
    returned_ids = [session["session_id"] for session in body]
    assert len(body) == 5
    assert returned_ids[0] == owned_sessions[-1]
    assert owned_sessions[0] not in returned_ids
    assert other_session_id not in returned_ids
    for session in body:
        _assert_no_analytic_fields(session)


def test_resume_session_appends_event_and_updates_last_active_at() -> None:
    """Phase 3 SDD §8 T2: resume records session_resumed for path reconstruction."""
    client, runtime = _build_client_and_runtime()
    session_id = _start_session(client, runtime)["session_id"]
    original_last_active_at = runtime.student_sessions.sessions[session_id]["last_active_at"]

    response = client.post(f"/v1/student/sessions/{session_id}/resume")

    assert response.status_code == 200
    body = response.json()
    _assert_no_analytic_fields(body)
    assert body["session_id"] == session_id
    resume_events = [
        event for event in runtime.event_store.events if event["event_type"] == "session_resumed"
    ]
    assert len(resume_events) == 1
    event = resume_events[0]
    assert event["tenant_id"] == runtime.tenant_id
    assert event["student_id"] == runtime.student_user_id
    assert str(event["session_id"]) == session_id
    assert runtime.student_sessions.sessions[session_id]["last_active_at"] > original_last_active_at


def test_other_tenant_cannot_resume_session_through_pool() -> None:
    """Phase 3 SDD §8 T3: resume reads remain tenant-isolated through the pool."""
    shared = _shared_components()
    client_a, runtime_a = _build_client_and_runtime(shared=shared)
    client_b, runtime_b = _build_client_and_runtime(shared=shared)
    session_id = _start_session(client_a, runtime_a)["session_id"]

    response = client_b.post(f"/v1/student/sessions/{session_id}/resume")

    assert response.status_code == 404
    assert runtime_a.tenant_pool is runtime_b.tenant_pool
    assert not any(
        event["event_type"] == "session_resumed" for event in runtime_b.event_store.events
    )
