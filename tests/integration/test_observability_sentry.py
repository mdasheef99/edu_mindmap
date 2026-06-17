def test_sentry_init_is_noop_without_dsn(monkeypatch) -> None:
    """Sentry is optional locally and must not break tests when no DSN is configured."""
    from app.observability.sentry import init_sentry

    monkeypatch.delenv("SENTRY_DSN_BACKEND", raising=False)

    assert init_sentry() is False


def test_postgres_llm_usage_store_targets_usage_table() -> None:
    """The durable usage adapter writes to the migration 0001 usage table."""
    from app.llm_gateway.postgres_usage import INSERT_LLM_USAGE_SQL

    sql = INSERT_LLM_USAGE_SQL.lower()

    assert "insert into llm_usage_records" in sql
    assert "tenant_id" in sql
    assert "model_id" in sql
    assert "cost_usd" in sql