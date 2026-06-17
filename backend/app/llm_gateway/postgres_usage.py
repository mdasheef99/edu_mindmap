"""Postgres-backed LLM usage store adapter."""

from __future__ import annotations

from typing import Any

from app.llm_gateway.usage import LLMUsageRecord
from app.tenancy.postgres_context import set_local_tenant

INSERT_LLM_USAGE_SQL = """
INSERT INTO llm_usage_records (
    usage_id, tenant_id, purpose, model_id, prompt_version, prompt_tokens,
    completion_tokens, cost_usd, fixture, recorded_at
) VALUES (
    %(usage_id)s, %(tenant_id)s, %(purpose)s, %(model_id)s, %(prompt_version)s,
    %(prompt_tokens)s, %(completion_tokens)s, %(cost_usd)s, %(fixture)s, %(recorded_at)s
)
RETURNING *
"""


class PostgresLLMUsageStore:
    """Append-only LLM usage/cost store backed by migration 0001."""

    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def append(self, record: LLMUsageRecord) -> LLMUsageRecord:
        with self.connection.transaction():
            if record.tenant_id is not None:
                set_local_tenant(self.connection, record.tenant_id)
            self.connection.execute(INSERT_LLM_USAGE_SQL, record.__dict__)
        return record
