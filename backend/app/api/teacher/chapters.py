"""Teacher Dashboard V1 chapter graph render endpoint."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request

from app.domain.auth import AuthContext
from app.domain.curriculum import ChapterGraphNotFoundError, TeacherChapterGraph
from app.tenancy.auth import get_auth_context

router = APIRouter(prefix="/v1/teacher", tags=["teacher"])
TEACHER_ROLES = {"teacher", "approved_teacher"}


@router.get("/chapters/{chapter_id}", response_model=TeacherChapterGraph)
def render_chapter_graph(
    chapter_id: UUID,
    request: Request,
    auth: AuthContext = Depends(get_auth_context),
) -> TeacherChapterGraph:
    """Render the ingested curriculum graph without per-student fields."""
    if auth.role not in TEACHER_ROLES:
        raise HTTPException(status_code=403, detail="Teacher role required")

    runtime = request.app.state.session_runtime
    try:
        return runtime.render_teacher_chapter(chapter_id=chapter_id, auth=auth)
    except ChapterGraphNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Chapter graph not found") from exc
