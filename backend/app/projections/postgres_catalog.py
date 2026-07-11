"""Postgres-backed student-safe M4 launch catalog."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from app.domain.student.curriculum import (
    ConceptEntry,
    CurriculumChapter,
    CurriculumClass,
    CurriculumExam,
    CurriculumSubject,
)
from app.tenancy.postgres_context import set_local_tenant


class PostgresCatalogStore:
    """Read the app-facing catalog under the configured M4 B2C tenant."""

    def __init__(self, connection: Any, *, tenant_id: UUID) -> None:
        self.connection = connection
        self.tenant_id = tenant_id

    def _fetch(self, sql: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        with self.connection.transaction():
            set_local_tenant(self.connection, self.tenant_id)
            cursor = self.connection.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]

    def list_classes(self) -> list[CurriculumClass]:
        rows = self._fetch(
            "SELECT * FROM public.curriculum_classes "
            "WHERE tenant_id = %(tenant_id)s ORDER BY sort_order, slug",
            {"tenant_id": self.tenant_id},
        )
        return [CurriculumClass.model_validate(row) for row in rows]

    def list_exams(self, *, class_level_id: UUID) -> list[CurriculumExam]:
        rows = self._fetch(
            "SELECT * FROM public.exams WHERE tenant_id = %(tenant_id)s "
            "AND class_level_id = %(class_level_id)s AND status = 'active' "
            "ORDER BY sort_order, slug",
            {"tenant_id": self.tenant_id, "class_level_id": class_level_id},
        )
        return [CurriculumExam.model_validate(row) for row in rows]

    def list_subjects(
        self, *, class_level_id: UUID, exam_id: UUID
    ) -> list[CurriculumSubject]:
        rows = self._fetch(
            "SELECT * FROM public.subjects WHERE tenant_id = %(tenant_id)s "
            "AND class_level_id = %(class_level_id)s AND exam_id = %(exam_id)s "
            "AND status = 'active' ORDER BY sort_order, slug",
            {
                "tenant_id": self.tenant_id,
                "class_level_id": class_level_id,
                "exam_id": exam_id,
            },
        )
        return [CurriculumSubject.model_validate(row) for row in rows]

    def list_chapters(
        self,
        *,
        tenant_id: UUID,
        class_level_id: UUID,
        exam_id: UUID,
        subject_id: UUID,
    ) -> list[CurriculumChapter]:
        if tenant_id != self.tenant_id:
            return []
        rows = self._fetch(
            "SELECT * FROM public.chapters WHERE tenant_id = %(tenant_id)s "
            "AND class_level_id = %(class_level_id)s AND exam_id = %(exam_id)s "
            "AND subject_id = %(subject_id)s AND status = 'launchable' "
            "ORDER BY sort_order, slug",
            {
                "tenant_id": tenant_id,
                "class_level_id": class_level_id,
                "exam_id": exam_id,
                "subject_id": subject_id,
            },
        )
        return [CurriculumChapter.model_validate(row) for row in rows]

    def get_chapter(
        self, *, tenant_id: UUID, chapter_id: UUID
    ) -> CurriculumChapter | None:
        if tenant_id != self.tenant_id:
            return None
        rows = self._fetch(
            "SELECT * FROM public.chapters WHERE tenant_id = %(tenant_id)s "
            "AND chapter_id = %(chapter_id)s AND status = 'launchable'",
            {"tenant_id": tenant_id, "chapter_id": chapter_id},
        )
        return None if not rows else CurriculumChapter.model_validate(rows[0])

    def list_launch_suggestions(
        self, *, tenant_id: UUID, limit: int = 5
    ) -> list[CurriculumChapter]:
        if tenant_id != self.tenant_id:
            return []
        rows = self._fetch(
            "SELECT * FROM public.chapters WHERE tenant_id = %(tenant_id)s "
            "AND status = 'launchable' ORDER BY sort_order, slug LIMIT %(limit)s",
            {"tenant_id": tenant_id, "limit": limit},
        )
        return [CurriculumChapter.model_validate(row) for row in rows]

    def list_concept_entries(self, *, chapter_id: UUID) -> list[ConceptEntry]:
        rows = self._fetch(
            "SELECT * FROM public.concept_entries WHERE tenant_id = %(tenant_id)s "
            "AND chapter_id = %(chapter_id)s AND status = 'active' "
            "ORDER BY sort_order, slug",
            {"tenant_id": self.tenant_id, "chapter_id": chapter_id},
        )
        return [ConceptEntry.model_validate(row) for row in rows]

