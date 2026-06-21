"""Deterministic P0 segmentation helpers."""

# Traceability:
# - docs/planning/sdd/phase-2-curriculum-ingestion-sdd.md §9 (T1, T2)
# - docs/planning/sdd/phase-2-curriculum-ingestion-sdd.md §8 (L1, L2)
# - docs/chapter-analysis-pipeline-specification.md P0

from __future__ import annotations

from collections.abc import Sequence
from io import BytesIO

from pypdf import PdfReader


def extract_pdf_pages(pdf_bytes: bytes) -> list[str]:
    """Extract deterministic page-text inputs from source chapter PDF bytes."""

    reader = PdfReader(BytesIO(pdf_bytes))
    return [page.extract_text() or "" for page in reader.pages]


def segment_chapter_pdf_bytes(chapter_id: str, pdf_bytes: bytes) -> list[dict[str, object]]:
    """Extract PDF page text and split it into the deterministic P0 segment index."""

    return segment_chapter_text(chapter_id, extract_pdf_pages(pdf_bytes))


def segment_chapter_text(chapter_id: str, pages: Sequence[str]) -> list[dict[str, object]]:
    """Split chapter pages into a deterministic segment index.

    The initial Phase 2 slice accepts already-extracted page text. PDF extraction stays a separate
    concern so the deterministic index can be tested without file IO.
    """

    segments: list[dict[str, object]] = []
    counters: dict[str, int] = {}

    for page_number, page_text in enumerate(pages, start=1):
        cursor = 0
        for raw_block in page_text.split("\n\n"):
            stripped = raw_block.strip()
            if not stripped:
                cursor += len(raw_block) + 2
                continue

            block_start = page_text.index(stripped, cursor)
            block_end = block_start + len(stripped)
            cursor = block_end

            segment_type = "question" if stripped.endswith("?") else "para"
            counters[segment_type] = counters.get(segment_type, 0) + 1
            segment: dict[str, object] = {
                "segment_id": f"{chapter_id}_{segment_type}_{counters[segment_type]:03d}",
                "segment_type": segment_type,
                "text": stripped,
                "page": page_number,
                "char_span": (block_start, block_end),
            }
            if segment_type == "question":
                segment["location"] = "in_text"
            segments.append(segment)

    return segments
