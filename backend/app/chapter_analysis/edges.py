"""P4 edge-id assignment helpers."""

from __future__ import annotations

from collections.abc import Sequence

NON_DIRECTIONAL_EDGE_TYPES = {"CONNECTS", "CONTRASTS_WITH"}


def assign_edge_ids(edges: Sequence[dict[str, object]]) -> list[dict[str, object]]:
    """Attach deterministic edge ids after the P4 relationship pass."""

    enriched_edges: list[dict[str, object]] = []
    for edge in edges:
        edge_type = str(edge["type"])
        from_concept = str(edge["from_concept"])
        to_concept = str(edge["to_concept"])
        edge_from, edge_to = _edge_endpoints(edge_type, from_concept, to_concept)
        enriched_edge = dict(edge)
        enriched_edge["edge_id"] = f"edge_{edge_type.lower()}_{edge_from}_{edge_to}"
        enriched_edges.append(enriched_edge)
    return enriched_edges


def _edge_endpoints(edge_type: str, from_concept: str, to_concept: str) -> tuple[str, str]:
    if edge_type in NON_DIRECTIONAL_EDGE_TYPES:
        left, right = sorted((from_concept, to_concept))
        return left, right
    return from_concept, to_concept
