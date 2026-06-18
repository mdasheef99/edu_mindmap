from uuid import uuid4

import pytest


def _segment_index() -> list[dict[str, object]]:
    from app.chapter_analysis.segments import segment_chapter_text

    return segment_chapter_text(
        "ch_phys10_electricity",
        ["Electric current is charge flow.\n\nWhy does current need a circuit?"],
    )


def _known_segment_ids(segments: list[dict[str, object]]) -> set[str]:
    return {str(segment["segment_id"]) for segment in segments}


def test_p1_p2_p4_fixture_passes_use_llm_gateway_and_record_usage() -> None:
    """SDD §8 L5: P1/P2/P4 CI calls use recorded fixtures through llm_gateway."""
    from app.chapter_analysis.merge import merge_concept_records
    from app.chapter_analysis.passes import (
        run_p1_named_concept_extraction,
        run_p2_embedded_concept_extraction,
        run_p4_relationship_extraction,
    )
    from app.llm_gateway.usage import InMemoryLLMUsageStore

    segments = _segment_index()
    known_segment_ids = _known_segment_ids(segments)
    usage_store = InMemoryLLMUsageStore()
    tenant_id = uuid4()

    p1 = run_p1_named_concept_extraction(segments, tenant_id=tenant_id, usage_store=usage_store)
    p2 = run_p2_embedded_concept_extraction(
        segments,
        p1["concepts"],
        tenant_id=tenant_id,
        usage_store=usage_store,
    )
    merged_concepts = merge_concept_records(p1["concepts"], p2["concepts"])
    p4 = run_p4_relationship_extraction(
        segments,
        merged_concepts,
        tenant_id=tenant_id,
        usage_store=usage_store,
    )

    assert p1["prompt_version"] == "chapter-analysis-p1-fixture-v1"
    assert p2["prompt_version"] == "chapter-analysis-p2-fixture-v1"
    assert p4["prompt_version"] == "chapter-analysis-p4-fixture-v1"
    assert p1["model_id"] == p2["model_id"] == p4["model_id"]

    for concept in [*p1["concepts"], *p2["concepts"]]:
        assert set(concept) >= {"concept_id", "label", "definition", "category_tag", "passage_refs"}
        assert concept["extraction_pass"] in {"P1", "P2"}
        refs = concept["passage_refs"]
        assert isinstance(refs, dict)
        for values in refs.values():
            if isinstance(values, list):
                assert set(values) <= known_segment_ids

    assert p4["edges"]
    for edge in p4["edges"]:
        assert set(edge) >= {"from_concept", "to_concept", "type", "passage_support", "rationale"}
        assert edge["type"] in {"PREREQUISITE_OF", "CONNECTS", "CONTRASTS_WITH"}
        assert set(edge["passage_support"]) <= known_segment_ids

    assert len(usage_store.records) == 3
    assert [record.prompt_version for record in usage_store.records] == [
        p1["prompt_version"],
        p2["prompt_version"],
        p4["prompt_version"],
    ]
    assert all(record.tenant_id == tenant_id for record in usage_store.records)
    assert all(record.purpose == "analysis" for record in usage_store.records)
    assert all(record.fixture for record in usage_store.records)


def test_p1_fixture_rejects_segment_without_segment_id() -> None:
    """Fixture gateway should raise a contract error, not KeyError, for malformed segments."""
    from app.llm_gateway.chapter_analysis_fixture import extract_named_concepts_fixture

    malformed_segments = [
        {
            "segment_type": "para",
            "text": "Electric current is charge flow.",
            "page": 1,
            "char_span": (0, 32),
        }
    ]

    with pytest.raises(ValueError, match="missing segment_id"):
        extract_named_concepts_fixture(malformed_segments)
