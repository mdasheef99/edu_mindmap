"""P3 merge and dedup helpers for the curriculum concept inventory."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from copy import deepcopy

PASSAGE_REF_KEYS = ("definitional", "explanatory", "application")


def merge_concept_records(
    named_concepts: Sequence[dict[str, object]],
    embedded_concepts: Sequence[dict[str, object]],
) -> list[dict[str, object]]:
    """Merge embedded concepts into named concepts when labels normalize to the same key."""

    merged = [deepcopy(concept) for concept in named_concepts]
    for concept in merged:
        concept.setdefault("merged_from", [])

    for embedded in embedded_concepts:
        target = _find_matching_named_concept(merged, str(embedded["label"]))
        if target is None:
            new_concept = deepcopy(embedded)
            new_concept.setdefault("merged_from", [])
            merged.append(new_concept)
            continue

        target["passage_refs"] = _union_passage_refs(
            target.get("passage_refs", {}),
            embedded.get("passage_refs", {}),
        )
        raw_merged_from = target.get("merged_from", [])
        merged_from = (
            [str(value) for value in raw_merged_from] if isinstance(raw_merged_from, list) else []
        )
        merged_from.append(str(embedded["concept_id"]))
        target["merged_from"] = sorted(dict.fromkeys(merged_from))

    return merged


def _find_matching_named_concept(
    named_concepts: Iterable[dict[str, object]], label: str
) -> dict[str, object] | None:
    normalized_label = _normalize_label(label)
    for concept in named_concepts:
        if _normalize_label(str(concept["label"])) == normalized_label:
            return concept
    return None


def _normalize_label(label: str) -> str:
    collapsed = " ".join(label.lower().split())
    if collapsed.endswith("ies") and len(collapsed) > 3:
        return f"{collapsed[:-3]}y"
    if collapsed.endswith("s") and not collapsed.endswith("ss"):
        return collapsed[:-1]
    return collapsed


def _union_passage_refs(
    left: object,
    right: object,
) -> dict[str, list[str]]:
    left_refs = left if isinstance(left, dict) else {}
    right_refs = right if isinstance(right, dict) else {}
    merged: dict[str, list[str]] = {}
    for key in PASSAGE_REF_KEYS:
        values: list[str] = []
        for source in (left_refs, right_refs):
            raw_values = source.get(key, [])
            if isinstance(raw_values, list):
                values.extend(str(value) for value in raw_values)
        merged[key] = list(dict.fromkeys(values))
    return merged
