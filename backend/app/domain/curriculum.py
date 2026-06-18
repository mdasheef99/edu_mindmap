"""Teacher-safe curriculum render models for Phase 2.

Traceability:
- docs/planning/sdd/phase-2-curriculum-ingestion-sdd.md §§7.1, 8-10
- docs/architecture/backend-architecture.md §7.5
"""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel


class ChapterGraphNotFoundError(Exception):
    """Raised when a tenant-scoped teacher chapter graph is absent."""


class TeacherChapterSegment(BaseModel):
    """Segment metadata for teacher graph rendering; omits raw text and student data."""

    segment_id: str
    segment_type: str
    page: int
    char_span: tuple[int, int]
    location: str | None = None


class TeacherChapterConcept(BaseModel):
    concept_id: str
    label: str
    definition: str
    category_tag: str
    passage_refs: dict[str, list[str]]


class TeacherChapterEdge(BaseModel):
    edge_id: str
    edge_kind: str
    from_concept_id: str
    to_concept_id: str
    passage_support: list[str]
    rationale: str | None = None


class TeacherChapterGraph(BaseModel):
    """Render-only chapter-analysis graph for Teacher Dashboard V1."""

    chapter_id: UUID
    chapter_analysis_id: UUID
    title: str
    segment_index_version: str
    pipeline_version: str
    segments: list[TeacherChapterSegment]
    concepts: list[TeacherChapterConcept]
    edges: list[TeacherChapterEdge]
