import os
from uuid import uuid4

import pytest


def _test_database_url_missing() -> bool:
    import os
    return os.getenv("TEST_DATABASE_URL") is None


@pytest.mark.skipif(
    _test_database_url_missing(),
    reason="Requires explicit TEST_DATABASE_URL for real Postgres/Supabase RLS validation.",
)
def test_real_postgres_rls_isolation_through_tenant_context() -> None:
    """Live Supabase/Postgres RLS denies cross-tenant reads through app.tenant_id."""
    psycopg = pytest.importorskip("psycopg")
    from psycopg.rows import dict_row

    tenant_a = uuid4()
    tenant_b = uuid4()
    user_a = uuid4()

    with psycopg.connect(os.environ["TEST_DATABASE_URL"], row_factory=dict_row) as conn:
        if _current_role_bypasses_rls(conn):
            pytest.skip("TEST_DATABASE_URL role bypasses RLS; use a non-bypass app role.")

        conn.execute("BEGIN")
        try:
            _insert_tenant_and_session(conn, tenant_id=tenant_a, student_user_id=user_a)
            _insert_tenant_and_session(conn, tenant_id=tenant_b, student_user_id=uuid4())

            conn.execute("SET LOCAL app.tenant_id = %s", (str(tenant_a),))
            rows = conn.execute(
                "SELECT tenant_id FROM student_rm.sessions ORDER BY tenant_id",
            ).fetchall()

            assert [row["tenant_id"] for row in rows] == [tenant_a]
        finally:
            conn.rollback()


@pytest.mark.skipif(
    _test_database_url_missing(),
    reason="Requires explicit TEST_DATABASE_URL for real Postgres/Supabase SKIP LOCKED validation.",
)
def test_real_postgres_skip_locked_claims_each_job_once() -> None:
    """Live Supabase/Postgres queue claim uses row locks to prevent double-claiming."""
    psycopg = pytest.importorskip("psycopg")
    from psycopg.rows import dict_row

    tenant_id = uuid4()
    job_payload = '{"event_id":"00000000-0000-4000-8000-000000000001"}'
    claim_sql = """
    WITH claimed AS (
        SELECT job_id
        FROM public.jobs
        WHERE job_type = 'classify'
          AND status = 'queued'
          AND run_after <= now()
        ORDER BY created_at
        FOR UPDATE SKIP LOCKED
        LIMIT 1
    )
    UPDATE public.jobs
    SET status = 'running', locked_by = %s, locked_at = now(), attempts = attempts + 1
    WHERE job_id IN (SELECT job_id FROM claimed)
    RETURNING job_id
    """

    conn1 = psycopg.connect(os.environ["TEST_DATABASE_URL"], row_factory=dict_row)
    conn2 = psycopg.connect(os.environ["TEST_DATABASE_URL"], row_factory=dict_row)
    try:
        if _current_role_bypasses_rls(conn1):
            pytest.skip("TEST_DATABASE_URL role bypasses RLS; use a non-bypass app role.")

        conn1.execute("BEGIN")
        conn1.execute("SET LOCAL app.tenant_id = %s", (str(tenant_id),))
        conn1.execute(
            "INSERT INTO public.tenants (tenant_id, kind, name) VALUES (%s, 'individual', 'skip locked test')",
            (tenant_id,),
        )
        conn1.execute(
            "INSERT INTO public.jobs (job_type, tenant_id, payload, idempotency_key) "
            "VALUES ('classify', %s, %s::jsonb, 'skip-locked-live-test')",
            (tenant_id, job_payload),
        )

        first_claim = conn1.execute(claim_sql, ("worker-1",)).fetchone()
        assert first_claim is not None

        conn2.execute("BEGIN")
        conn2.execute("SET LOCAL app.tenant_id = %s", (str(tenant_id),))
        second_claim = conn2.execute(claim_sql, ("worker-2",)).fetchone()
        assert second_claim is None
    finally:
        conn2.rollback()
        conn2.close()
        conn1.rollback()
        conn1.close()


def _current_role_bypasses_rls(conn) -> bool:
    row = conn.execute(
        "SELECT rolsuper OR rolbypassrls AS bypasses_rls "
        "FROM pg_roles WHERE rolname = current_user"
    ).fetchone()
    return bool(row["bypasses_rls"])


def _insert_tenant_and_session(conn, *, tenant_id, student_user_id) -> None:
    session_id = uuid4()
    conn.execute("SET LOCAL app.tenant_id = %s", (str(tenant_id),))
    conn.execute(
        "INSERT INTO public.tenants (tenant_id, kind, name) VALUES (%s, 'individual', 'rls test')",
        (tenant_id,),
    )
    conn.execute(
        """
        INSERT INTO student_rm.sessions (
            session_id, tenant_id, student_user_id, exam_id, subject_id, chapter_id,
            concept_entry_id, chapter_analysis_id, status, started_at, last_active_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'active', now(), now())
        """,
        (session_id, tenant_id, student_user_id, uuid4(), uuid4(), uuid4(), uuid4(), uuid4()),
    )