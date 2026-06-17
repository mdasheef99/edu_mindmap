"""Deterministic Stage 2 classification fixture used by the first worker slice."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from app.llm_gateway.config import stage2_classification_model_id
from app.llm_gateway.usage import InMemoryLLMUsageStore, record_llm_usage


CLASSIFICATION_PROMPT_VERSION = "question-classifier-fixture-v1"


def classify_selected_option(
    selected_option_text: str,
    *,
    tenant_id: UUID | None = None,
    usage_store: InMemoryLLMUsageStore | None = None,
) -> dict[str, Any]:
    """Return a stable fixture payload for CI-safe classification tests."""
    model_id = stage2_classification_model_id()
    if usage_store is not None:
        record_llm_usage(
            usage_store,
            tenant_id=tenant_id,
            purpose="classification",
            model_id=model_id,
            prompt_version=CLASSIFICATION_PROMPT_VERSION,
            prompt_tokens=12,
            completion_tokens=18,
            cost_usd=0.0,
            fixture=True,
        )
    return {
        "selected_option_text": selected_option_text,
        "prompt_version": CLASSIFICATION_PROMPT_VERSION,
        "model_id": model_id,
        "scores_payload": {
            "understand": 0.72,
            "apply": 0.58,
            "analyze": 0.41,
        },
        "entropy_payload": {"total": 0.19},
        "dispersion_payload": {"median_abs_dev": 0.08},
    }