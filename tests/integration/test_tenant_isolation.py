from uuid import uuid4

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


def _build_client_and_runtime(tenant_id, student_user_id, shared_components):
    from app.main import SessionRuntime, create_app

    runtime = SessionRuntime.for_testing(
        tenant_id=tenant_id,
        student_user_id=student_user_id,
        **shared_components,
    )
    return TestClient(create_app(runtime=runtime)), runtime


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


def test_tenant_a_cannot_read_tenant_b_session() -> None:
    """T12: tenant-scoped reads must hide other tenants' sessions."""
    shared = _shared_components()
    tenant_a = uuid4()
    tenant_b = uuid4()
    student_a = uuid4()
    student_b = uuid4()

    client_a, runtime_a = _build_client_and_runtime(tenant_a, student_a, shared)
    _, runtime_b = _build_client_and_runtime(tenant_b, student_b, shared)
    session_id = _start_session(client_a)

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
    session_a = _start_session(client_a)
    session_b = _start_session(client_b)

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
    session_a = _start_session(client_a)

    assert runtime_a.tenant_pool is runtime_b.tenant_pool
    assert runtime_b.tenant_pool is not None
    connection = runtime_b.tenant_pool.connection

    connection.set_local_tenant(tenant_b)
    try:
        assert connection.fetch_session_bypassing_app_guard(session_a) is None
    finally:
        connection.clear_local_tenant()
