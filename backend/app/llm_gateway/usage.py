"""LLM usage and cost accounting primitives.

The first Phase 1 implementation records fixture calls in memory; Postgres persistence can
reuse the same record shape when the deployed `llm_gateway` is wired to the database.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal
from uuid import UUID, uuid4


LLMPurpose = Literal["generation", "classification", "analysis", "podcast"]


@dataclass(frozen=True)
class LLMUsageRecord:
    usage_id: UUID
    tenant_id: UUID | None
    purpose: LLMPurpose
    model_id: str
    prompt_version: str
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    fixture: bool
    recorded_at: datetime


class InMemoryLLMUsageStore:
    """Append-only usage counter used by tests and fixture-mode runtime."""

    def __init__(self) -> None:
        self.records: list[LLMUsageRecord] = []

    def append(self, record: LLMUsageRecord) -> LLMUsageRecord:
        self.records.append(record)
        return record


def record_llm_usage(
    store: InMemoryLLMUsageStore,
    *,
    tenant_id: UUID | None,
    purpose: LLMPurpose,
    model_id: str,
    prompt_version: str,
    prompt_tokens: int,
    completion_tokens: int,
    cost_usd: float,
    fixture: bool,
) -> LLMUsageRecord:
    """Record one model call before returning control to the caller."""
    record = LLMUsageRecord(
        usage_id=uuid4(),
        tenant_id=tenant_id,
        purpose=purpose,
        model_id=model_id,
        prompt_version=prompt_version,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        cost_usd=cost_usd,
        fixture=fixture,
        recorded_at=datetime.now(timezone.utc),
    )
    return store.append(record)