"""Student-safe M4 curriculum and dashboard DTOs.

Traceability:
- docs/api/student-api-spec.md §§4-5
- docs/planning/sdd/phase-3-m4-curriculum-auth-sdd.md §§7-8
- docs/database/core-operational-schema.md §6
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CurriculumClass(BaseModel):
    class_level_id: UUID
    slug: str
    label: str
    sort_order: int


class CurriculumExam(BaseModel):
    exam_id: UUID
    class_level_id: UUID
    slug: str
    name: str
    status: str
    sort_order: int


class CurriculumSubject(BaseModel):
    subject_id: UUID
    class_level_id: UUID
    exam_id: UUID
    slug: str
    name: str
    status: str
    sort_order: int


class CurriculumChapter(BaseModel):
    chapter_id: UUID
    subject_id: UUID
    chapter_analysis_id: UUID
    slug: str
    title: str
    status: str
    sort_order: int


class ConceptEntry(BaseModel):
    concept_entry_id: UUID
    chapter_id: UUID
    slug: str
    title: str
    status: str
    sort_order: int


class ClassListResponse(BaseModel):
    items: list[CurriculumClass]


class ExamListResponse(BaseModel):
    items: list[CurriculumExam]


class SubjectListResponse(BaseModel):
    items: list[CurriculumSubject]


class ChapterListResponse(BaseModel):
    items: list[CurriculumChapter]


class ChapterDetailResponse(BaseModel):
    chapter: CurriculumChapter
    concept_entries: list[ConceptEntry]


class ConceptEntryListResponse(BaseModel):
    items: list[ConceptEntry]


class DashboardSessionSummary(BaseModel):
    session_id: UUID
    chapter_id: UUID
    chapter_title: str
    last_active_at: datetime
    status: str


class DashboardResponse(BaseModel):
    display_name: str | None = None
    continue_learning: DashboardSessionSummary | None = None
    recent_sessions: list[DashboardSessionSummary]
    launch_suggestions: list[CurriculumChapter]
