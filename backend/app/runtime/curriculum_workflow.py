"""Curriculum-related orchestration kept out of the FastAPI composition root."""

from __future__ import annotations

from uuid import UUID

from app.domain.auth import AuthContext
from app.domain.curriculum import ChapterGraphNotFoundError, TeacherChapterGraph
from app.domain.student.sessions import (
    ChapterLaunchNotFoundError,
    SessionStartRequest,
)
from app.runtime.ports import CurriculumStorePort


def resolve_session_request(
    payload: SessionStartRequest,
    *,
    tenant_id: UUID,
    curriculum: CurriculumStorePort,
) -> SessionStartRequest:
    """Look up the chapter in the curriculum and inject chapter_analysis_id.

    Raises:
        ChapterLaunchNotFoundError: if the chapter is not found for the tenant.
    """
    chapter = curriculum.find_chapter(
        tenant_id=tenant_id,
        exam_id=payload.exam_id,
        subject_id=payload.subject_id,
        chapter_id=payload.chapter_id,
    )
    if chapter is None:
        raise ChapterLaunchNotFoundError("Chapter not found in curriculum")
    return payload.model_copy(update={"chapter_analysis_id": chapter["chapter_analysis_id"]})


def render_teacher_chapter_graph(
    *,
    chapter_id: UUID,
    auth: AuthContext,
    curriculum: CurriculumStorePort,
) -> TeacherChapterGraph:
    """Render the teacher chapter graph for the given chapter_id.

    Raises:
        ChapterGraphNotFoundError: if the chapter graph is not found.
    """
    graph = curriculum.render_chapter_graph(
        tenant_id=auth.tenant_id,
        chapter_id=chapter_id,
    )
    if graph is None:
        raise ChapterGraphNotFoundError("Chapter graph not found")
    return graph
