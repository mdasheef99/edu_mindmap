def test_postgres_event_store_uses_events_table_and_tenant_context() -> None:
    """Postgres event store must append through migration 0001 table under tenant context."""
    from app.events.postgres_store import INSERT_EVENT_SQL

    sql = INSERT_EVENT_SQL.lower()

    assert "insert into events" in sql
    assert "tenant_id" in sql
    assert "event_version" in sql
    assert "returning" in sql


def test_postgres_queue_claim_uses_for_update_skip_locked() -> None:
    """Postgres queue adapter must claim jobs with SKIP LOCKED semantics."""
    from app.workers.postgres_queue import CLAIM_NEXT_SQL, ENQUEUE_CLASSIFY_SQL

    claim_sql = CLAIM_NEXT_SQL.lower()
    enqueue_sql = ENQUEUE_CLASSIFY_SQL.lower()

    assert "for update skip locked" in claim_sql
    assert "status = 'running'" in claim_sql
    assert "attempts = attempts + 1" in claim_sql
    assert "insert into jobs" in enqueue_sql
    assert "on conflict" in enqueue_sql