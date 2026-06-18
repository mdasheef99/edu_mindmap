"""P1/P2/P4 chapter-analysis pass wrappers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from uuid import UUID

from app.llm_gateway.chapter_analysis_fixture import (
    extract_embedded_concepts_fixture,
    extract_named_concepts_fixture,
    extract_relationship_edges_fixture,
)
from app.llm_gateway.usage import InMemoryLLMUsageStore


def run_p1_named_concept_extraction(
    segments: Sequence[Mapping[str, object]],
    *,
    tenant_id: UUID | None = None,
    usage_store: InMemoryLLMUsageStore | None = None,
) -> dict[str, object]:
    """Run P1 named concept extraction through the LLM Gateway fixture path."""

    return extract_named_concepts_fixture(
        segments,
        tenant_id=tenant_id,
        usage_store=usage_store,
    )


def run_p2_embedded_concept_extraction(
    segments: Sequence[Mapping[str, object]],
    named_concepts: Sequence[Mapping[str, object]],
    *,
    tenant_id: UUID | None = None,
    usage_store: InMemoryLLMUsageStore | None = None,
) -> dict[str, object]:
    """Run P2 embedded concept extraction through the LLM Gateway fixture path."""

    return extract_embedded_concepts_fixture(
        segments,
        named_concepts,
        tenant_id=tenant_id,
        usage_store=usage_store,
    )


def run_p4_relationship_extraction(
    segments: Sequence[Mapping[str, object]],
    concepts: Sequence[Mapping[str, object]],
    *,
    tenant_id: UUID | None = None,
    usage_store: InMemoryLLMUsageStore | None = None,
) -> dict[str, object]:
    """Run P4 relationship extraction through the LLM Gateway fixture path."""

    return extract_relationship_edges_fixture(
        segments,
        concepts,
        tenant_id=tenant_id,
        usage_store=usage_store,
    )
