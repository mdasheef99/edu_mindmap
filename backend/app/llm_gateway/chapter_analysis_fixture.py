"""Recorded fixture responses for Phase 2 chapter-analysis LLM passes.

These fixtures intentionally stay deterministic, but they should still enforce the
same basic schema/contract guarantees the real gateway path must uphold.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from uuid import UUID

from app.llm_gateway.usage import InMemoryLLMUsageStore, record_llm_usage

CHAPTER_ANALYSIS_FIXTURE_MODEL_ID = "chapter-analysis-fixture-model"
P1_PROMPT_VERSION = "chapter-analysis-p1-fixture-v1"
P2_PROMPT_VERSION = "chapter-analysis-p2-fixture-v1"
P4_PROMPT_VERSION = "chapter-analysis-p4-fixture-v1"
PASSAGE_REF_KEYS = ("definitional", "explanatory", "application")
ALLOWED_EDGE_TYPES = {"PREREQUISITE_OF", "CONNECTS", "CONTRASTS_WITH"}


def extract_named_concepts_fixture(
    segments: Sequence[Mapping[str, object]],
    *,
    tenant_id: UUID | None = None,
    usage_store: InMemoryLLMUsageStore | None = None,
) -> dict[str, object]:
    """Return a recorded P1 fixture envelope and record analysis usage."""
    _record_usage(usage_store, tenant_id=tenant_id, prompt_version=P1_PROMPT_VERSION)
    segment_ids_by_type = _segment_ids_by_type(segments)
    para_id = _first_segment_id(segment_ids_by_type, "para")
    question_id = _first_segment_id(segment_ids_by_type, "question", fallback=para_id)
    concepts = [
        _concept(
            "electric_current",
            "Electric current",
            "Rate of flow of electric charge as treated in the chapter.",
            "quantity",
            "P1",
            definitional=[para_id],
            explanatory=[para_id],
            application=[question_id],
        ),
        _concept(
            "circuit",
            "Circuit",
            "A closed conducting path needed for current flow.",
            "quantity",
            "P1",
            definitional=[para_id],
            explanatory=[],
            application=[question_id],
        ),
    ]
    _validate_fixture_concepts(concepts, extraction_pass="P1")
    return _envelope(
        P1_PROMPT_VERSION,
        concepts=concepts,
    )


def extract_embedded_concepts_fixture(
    segments: Sequence[Mapping[str, object]],
    named_concepts: Sequence[Mapping[str, object]],
    *,
    tenant_id: UUID | None = None,
    usage_store: InMemoryLLMUsageStore | None = None,
) -> dict[str, object]:
    """Return a recorded P2 fixture envelope and record analysis usage."""
    _record_usage(usage_store, tenant_id=tenant_id, prompt_version=P2_PROMPT_VERSION)
    segment_ids_by_type = _segment_ids_by_type(segments)
    para_id = _first_segment_id(segment_ids_by_type, "para")
    concepts = [
        _concept(
            "charge_flow_requires_closed_path",
            "charge flow requires a closed path",
            "The explanation relies on continuity of a closed path for charge flow.",
            "phenomenon",
            "P2",
            definitional=[],
            explanatory=[para_id],
            application=[],
        )
    ]
    _validate_fixture_concepts(
        concepts,
        extraction_pass="P2",
        forbidden_normalized_labels={
            _normalize_label(str(concept["label"]))
            for concept in named_concepts
            if "label" in concept
        },
    )
    return _envelope(
        P2_PROMPT_VERSION,
        concepts=concepts,
    )


def extract_relationship_edges_fixture(
    segments: Sequence[Mapping[str, object]],
    concepts: Sequence[Mapping[str, object]],
    *,
    tenant_id: UUID | None = None,
    usage_store: InMemoryLLMUsageStore | None = None,
) -> dict[str, object]:
    """Return a recorded P4 fixture envelope and record analysis usage."""
    _record_usage(usage_store, tenant_id=tenant_id, prompt_version=P4_PROMPT_VERSION)
    segment_ids_by_type = _segment_ids_by_type(segments)
    question_id = _first_segment_id(
        segment_ids_by_type,
        "question",
        fallback=_first_segment_id(segment_ids_by_type, "para"),
    )
    edges = [
        {
            "from_concept": "electric_current",
            "to_concept": "circuit",
            "type": "CONNECTS",
            "passage_support": [question_id],
            "rationale": "The chapter links current to the need for a circuit.",
        }
    ]
    _validate_fixture_edges(
        edges,
        known_concept_ids={
            str(concept["concept_id"]) for concept in concepts if "concept_id" in concept
        },
    )
    return _envelope(
        P4_PROMPT_VERSION,
        edges=edges,
    )


def _concept(
    concept_id: str,
    label: str,
    definition: str,
    category_tag: str,
    extraction_pass: str,
    *,
    definitional: list[str],
    explanatory: list[str],
    application: list[str],
) -> dict[str, object]:
    return {
        "concept_id": concept_id,
        "label": label,
        "definition": definition,
        "category_tag": category_tag,
        "extraction_pass": extraction_pass,
        "passage_refs": {
            "definitional": definitional,
            "explanatory": explanatory,
            "application": application,
        },
    }


def _envelope(prompt_version: str, **payload: object) -> dict[str, object]:
    return {
        "prompt_version": prompt_version,
        "model_id": CHAPTER_ANALYSIS_FIXTURE_MODEL_ID,
    } | payload


def _validate_fixture_concepts(
    concepts: Sequence[Mapping[str, object]],
    *,
    extraction_pass: str,
    forbidden_normalized_labels: set[str] | None = None,
) -> None:
    seen_ids: set[str] = set()
    seen_labels: set[str] = set()
    for concept in concepts:
        concept_id = str(concept["concept_id"])
        if concept_id in seen_ids:
            raise ValueError(f"Duplicate concept_id in fixture output: {concept_id}")
        seen_ids.add(concept_id)

        if str(concept.get("extraction_pass")) != extraction_pass:
            raise ValueError(f"Fixture concept {concept_id} has wrong extraction pass")
        if not str(concept.get("category_tag", "")).strip():
            raise ValueError(f"Fixture concept {concept_id} is missing category_tag")

        normalized_label = _normalize_label(str(concept["label"]))
        if normalized_label in seen_labels:
            raise ValueError(f"Duplicate concept label in fixture output: {concept['label']}")
        seen_labels.add(normalized_label)
        if forbidden_normalized_labels and normalized_label in forbidden_normalized_labels:
            raise ValueError(
                f"Embedded fixture concept duplicates named concept: {concept['label']}"
            )

        passage_refs = concept.get("passage_refs")
        if not isinstance(passage_refs, Mapping):
            raise ValueError(f"Fixture concept {concept_id} is missing passage_refs")

        definitional = _string_list(passage_refs.get("definitional", []), field="definitional")
        explanatory = _string_list(passage_refs.get("explanatory", []), field="explanatory")
        application = _string_list(passage_refs.get("application", []), field="application")

        if extraction_pass == "P1" and len(definitional) != 1:
            raise ValueError(
                f"P1 fixture concept {concept_id} must have exactly one definitional ref"
            )
        if extraction_pass == "P2" and len(definitional) > 1:
            raise ValueError(
                f"P2 fixture concept {concept_id} may not have multiple definitional refs"
            )
        if len(explanatory) > 2 or len(application) > 2:
            raise ValueError(f"Fixture concept {concept_id} exceeds passage-ref density bounds")

        for key in PASSAGE_REF_KEYS:
            if key not in passage_refs:
                raise ValueError(f"Fixture concept {concept_id} is missing {key} passage refs")


def _validate_fixture_edges(
    edges: Sequence[Mapping[str, object]], *, known_concept_ids: set[str]
) -> None:
    if not known_concept_ids:
        raise ValueError("P4 fixture requires known concepts from the merged inventory")
    for edge in edges:
        edge_type = str(edge.get("type"))
        if edge_type not in ALLOWED_EDGE_TYPES:
            raise ValueError(f"Fixture edge has unsupported type: {edge_type}")

        from_concept = str(edge.get("from_concept"))
        to_concept = str(edge.get("to_concept"))
        if from_concept not in known_concept_ids or to_concept not in known_concept_ids:
            raise ValueError("Fixture edge references unknown concept ids")

        passage_support = _string_list(edge.get("passage_support", []), field="passage_support")
        if not 1 <= len(passage_support) <= 2:
            raise ValueError("Fixture edges must carry 1-2 supporting segment ids")
        if not str(edge.get("rationale", "")).strip():
            raise ValueError("Fixture edge rationale must be non-empty")


def _segment_ids_by_type(
    segments: Sequence[Mapping[str, object]],
) -> dict[str, list[str]]:
    segment_ids_by_type: dict[str, list[str]] = {}
    for segment in segments:
        segment_id = segment.get("segment_id")
        if segment_id is None:
            raise ValueError("Fixture segment is missing segment_id")

        type_value = segment.get("segment_type")
        if not isinstance(type_value, str) or not type_value.strip():
            continue

        segment_ids_by_type.setdefault(type_value, []).append(str(segment_id))
    return segment_ids_by_type


def _first_segment_id(
    segment_ids_by_type: Mapping[str, Sequence[str]],
    segment_type: str,
    *,
    fallback: str | None = None,
) -> str:
    segment_ids = segment_ids_by_type.get(segment_type, ())
    if segment_ids:
        return str(segment_ids[0])
    if fallback is not None:
        return fallback
    raise ValueError(f"Missing {segment_type} segment for chapter-analysis fixture")


def _normalize_label(label: str) -> str:
    return " ".join(label.lower().split())


def _string_list(value: object, *, field: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"Fixture field {field} must be a list")
    return [str(item) for item in value]


def _record_usage(
    usage_store: InMemoryLLMUsageStore | None,
    *,
    tenant_id: UUID | None,
    prompt_version: str,
) -> None:
    if usage_store is None:
        return
    record_llm_usage(
        usage_store,
        tenant_id=tenant_id,
        purpose="analysis",
        model_id=CHAPTER_ANALYSIS_FIXTURE_MODEL_ID,
        prompt_version=prompt_version,
        prompt_tokens=48,
        completion_tokens=64,
        cost_usd=0.0,
        fixture=True,
    )
