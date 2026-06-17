"""Environment-backed LLM Gateway configuration.

Traceability:
- docs/architecture/backend-architecture.md §9
- docs/configuration-reference.md §9
- docs/planning/sdd/phase-1-walking-skeleton-sdd.md §10
"""

from __future__ import annotations

import os


DEFAULT_STAGE1_MODEL_ID = "stage-1-generation-fixture-model"
DEFAULT_STAGE2_MODEL_ID = "stage-2-classification-fixture-model"


def llm_provider() -> str:
    """Return the configured provider label; callers must not construct clients directly."""
    return os.getenv("LLM_PROVIDER", "fixture")


def stage1_generation_model_id() -> str:
    """Return the configured Stage 1 generation model id."""
    return os.getenv("LLM_STAGE1_MODEL_ID", DEFAULT_STAGE1_MODEL_ID)


def stage2_classification_model_id() -> str:
    """Return the configured Stage 2 classification model id."""
    return os.getenv("LLM_STAGE2_MODEL_ID", DEFAULT_STAGE2_MODEL_ID)


def llm_ci_mode() -> str:
    """Return the configured CI mode; Phase 1 CI uses recorded fixtures."""
    return os.getenv("LLM_CI_MODE", "recorded_fixtures")