from uuid import uuid4

import jwt
from fastapi.testclient import TestClient


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


def _build_client_and_runtime(
    tenant_id, student_user_id, shared_components, jwt_secret: str = "test-secret"
):
    from app.main import SessionRuntime, create_app

    runtime = SessionRuntime.for_testing(
        tenant_id=tenant_id,
        student_user_id=student_user_id,
        jwt_secret=jwt_secret,
        **shared_components,
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


def test_tenant_a_cannot_read_tenant_b_session() -> None:
    """T12: tenant-scoped reads must hide other tenants' sessions."""
    shared = _shared_components()
    tenant_a = uuid4()
    tenant_b = uuid4()
    student_a = uuid4()
    student_b = uuid4()

    client_a, runtime_a = _build_client_and_runtime(tenant_a, student_a, shared)
    _, runtime_b = _build_client_and_runtime(tenant_b, student_b, shared)
    session_id = _start_session(client_a, runtime_a)

    assert runtime_a.get_student_session(session_id) is not None
    assert runtime_b.get_student_session(session_id) is None


def test_tenant_isolation_holds_through_connection_pool() -> None:
    """T14: pooled-path tenant isolation must reset tenant context per request."""
    shared = _shared_components()
    tenant_a = uuid4()
    tenant_b = uuid4()
    student_a = uuid4()
    student_b = uuid4()

    client_a, runtime_a = _build_client_and_runtime(tenant_a, student_a, shared)
    client_b, runtime_b = _build_client_and_runtime(tenant_b, student_b, shared)
    session_a = _start_session(client_a, runtime_a)
    session_b = _start_session(client_b, runtime_b)

    assert runtime_a.tenant_pool is runtime_b.tenant_pool
    assert runtime_a.get_student_session_via_pool(session_a) is not None
    assert runtime_b.get_student_session_via_pool(session_a) is None
    assert runtime_b.get_student_session_via_pool(session_b) is not None
    assert runtime_a.get_student_session_via_pool(session_b) is None


def test_rls_denies_cross_tenant_when_app_guard_bypassed() -> None:
    """T20: DB-level tenant backstop must deny cross-tenant rows without app guard."""
    shared = _shared_components()
    tenant_a = uuid4()
    tenant_b = uuid4()
    student_a = uuid4()
    student_b = uuid4()

    client_a, runtime_a = _build_client_and_runtime(tenant_a, student_a, shared)
    _, runtime_b = _build_client_and_runtime(tenant_b, student_b, shared)
    session_a = _start_session(client_a, runtime_a)

    assert runtime_a.tenant_pool is runtime_b.tenant_pool
    assert runtime_b.tenant_pool is not None
    connection = runtime_b.tenant_pool.connection

    connection.set_local_tenant(tenant_b)
    try:
        assert connection.fetch_session_bypassing_app_guard(session_a) is None
    finally:
        connection.clear_local_tenant()
