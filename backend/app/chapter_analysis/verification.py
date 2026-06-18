"""Verification-gate helpers for chapter analysis passes."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence


def verify_cited_segment_ids(
    cited_segment_ids: Iterable[str],
    segment_index: Sequence[Mapping[str, object]],
) -> None:
    """Raise when a pass cites segment ids not present in the deterministic P0 index."""

    known_segment_ids = {str(segment["segment_id"]) for segment in segment_index}
    missing = sorted(
        segment_id for segment_id in cited_segment_ids if segment_id not in known_segment_ids
    )
    if missing:
        raise ValueError(f"Unknown segment ids: {', '.join(missing)}")
