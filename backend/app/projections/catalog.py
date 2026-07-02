"""In-memory app-facing curriculum catalog for M4.

This store is separate from the Phase 2 chapter-analysis `curriculum.*`
projection. It models only student-safe launch catalog metadata.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from app.domain.student.curriculum import (
    ConceptEntry,
    CurriculumChapter,
    CurriculumClass,
    CurriculumExam,
    CurriculumSubject,
)


@dataclass(frozen=True)
class M4ElectricityCatalogSeed:
    class_level_id: UUID
    exam_id: UUID
    subject_id: UUID
    chapter_id: UUID
    chapter_analysis_id: UUID
    root_concept_entry_id: UUID


class InMemoryCatalogStore:
    """Student-safe app catalog rows keyed by stable UUIDs."""

    def __init__(self) -> None:
        self.classes: dict[str, dict[str, Any]] = {}
        self.exams: dict[str, dict[str, Any]] = {}
        self.subjects: dict[str, dict[str, Any]] = {}
        self.chapters: dict[str, dict[str, Any]] = {}
        self.concept_entries: dict[str, dict[str, Any]] = {}

    def add_class(self, **row: Any) -> None:
        self.classes[str(row["class_level_id"])] = deepcopy(row)

    def add_exam(self, **row: Any) -> None:
        self.exams[str(row["exam_id"])] = deepcopy(row)

    def add_subject(self, **row: Any) -> None:
        self.subjects[str(row["subject_id"])] = deepcopy(row)

    def add_chapter(self, **row: Any) -> None:
        subject = self.subjects.get(str(row["subject_id"]), {})
        stored = {
            "sort_order": 0,
            "class_level_id": subject.get("class_level_id"),
            "exam_id": subject.get("exam_id"),
            **row,
        }
        self.chapters[str(stored["chapter_id"])] = deepcopy(stored)

    def add_concept_entry(self, **row: Any) -> None:
        stored = {"sort_order": 0, **row}
        self.concept_entries[str(stored["concept_entry_id"])] = deepcopy(stored)

    def list_classes(self) -> list[CurriculumClass]:
        return [
            CurriculumClass.model_validate(row)
            for row in sorted(self.classes.values(), key=_sort_key)
        ]

    def list_exams(self, *, class_level_id: UUID) -> list[CurriculumExam]:
        return [
            CurriculumExam.model_validate(row)
            for row in sorted(self.exams.values(), key=_sort_key)
            if row["class_level_id"] == class_level_id and row["status"] == "active"
        ]

    def list_subjects(self, *, class_level_id: UUID, exam_id: UUID) -> list[CurriculumSubject]:
        return [
            CurriculumSubject.model_validate(row)
            for row in sorted(self.subjects.values(), key=_sort_key)
            if row["class_level_id"] == class_level_id
            and row["exam_id"] == exam_id
            and row["status"] == "active"
        ]

    def list_chapters(
        self,
        *,
        tenant_id: UUID,
        class_level_id: UUID,
        exam_id: UUID,
        subject_id: UUID,
    ) -> list[CurriculumChapter]:
        return [
            CurriculumChapter.model_validate(row)
            for row in sorted(self.chapters.values(), key=_sort_key)
            if row["tenant_id"] == tenant_id
            and row["class_level_id"] == class_level_id
            and row["exam_id"] == exam_id
            and row["subject_id"] == subject_id
            and row["status"] == "launchable"
        ]

    def get_chapter(self, *, tenant_id: UUID, chapter_id: UUID) -> CurriculumChapter | None:
        row = self.chapters.get(str(chapter_id))
        if row is None or row["tenant_id"] != tenant_id or row["status"] != "launchable":
            return None
        return CurriculumChapter.model_validate(row)

    def list_launch_suggestions(self, *, tenant_id: UUID, limit: int = 5) -> list[CurriculumChapter]:
        chapters = [
            CurriculumChapter.model_validate(row)
            for row in sorted(self.chapters.values(), key=_sort_key)
            if row["tenant_id"] == tenant_id and row["status"] == "launchable"
        ]
        return chapters[:limit]

    def list_concept_entries(self, *, chapter_id: UUID) -> list[ConceptEntry]:
        return [
            ConceptEntry.model_validate(row)
            for row in sorted(self.concept_entries.values(), key=_sort_key)
            if row["chapter_id"] == chapter_id and row["status"] == "active"
        ]


def seed_m4_electricity_catalog(
    catalog: InMemoryCatalogStore, *, tenant_id: UUID
) -> M4ElectricityCatalogSeed:
    """Seed the M4 launch path with deterministic local UUIDs."""
    seed = M4ElectricityCatalogSeed(
        class_level_id=UUID("10000000-0000-4000-8000-000000000010"),
        exam_id=UUID("10000000-0000-4000-8000-000000000020"),
        subject_id=UUID("10000000-0000-4000-8000-000000000030"),
        chapter_id=UUID("10000000-0000-4000-8000-000000000040"),
        chapter_analysis_id=UUID("10000000-0000-4000-8000-000000000050"),
        root_concept_entry_id=UUID("10000000-0000-4000-8000-000000000060"),
    )
    catalog.add_class(
        class_level_id=seed.class_level_id,
        slug="class-10",
        label="Class 10",
        sort_order=10,
    )
    catalog.add_exam(
        exam_id=seed.exam_id,
        class_level_id=seed.class_level_id,
        slug="cbse",
        name="CBSE",
        status="active",
        sort_order=10,
    )
    catalog.add_subject(
        subject_id=seed.subject_id,
        class_level_id=seed.class_level_id,
        exam_id=seed.exam_id,
        slug="science",
        name="Science",
        status="active",
        sort_order=10,
    )
    catalog.add_chapter(
        tenant_id=tenant_id,
        class_level_id=seed.class_level_id,
        exam_id=seed.exam_id,
        subject_id=seed.subject_id,
        chapter_id=seed.chapter_id,
        chapter_analysis_id=seed.chapter_analysis_id,
        slug="electricity",
        title="Electricity",
        status="launchable",
        sort_order=10,
    )
    catalog.add_concept_entry(
        concept_entry_id=seed.root_concept_entry_id,
        chapter_id=seed.chapter_id,
        slug="electricity-overview",
        title="Electricity overview",
        status="active",
        sort_order=10,
    )
    return seed


def _sort_key(row: dict[str, Any]) -> tuple[int, str]:
    return int(row.get("sort_order", 0)), str(row.get("slug", ""))
