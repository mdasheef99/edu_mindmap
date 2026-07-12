"""Student dashboard endpoint for M4."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request

from app.domain.auth import AuthContext
from app.domain.student.curriculum import DashboardResponse, DashboardSessionSummary
from app.domain.student.sessions import StudentSession
from app.tenancy.auth import get_auth_context

router = APIRouter(prefix="/v1/student", tags=["student"])


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    request: Request,
    auth: AuthContext = Depends(get_auth_context),
) -> DashboardResponse:
    if auth.role != "student":
        raise HTTPException(status_code=403, detail="Student membership required")
    runtime = request.app.state.session_runtime
    recent = runtime.list_recent_student_sessions(auth=auth)
    summaries = [_summary_for_session(runtime, auth, session) for session in recent]
    return DashboardResponse(
        continue_learning=summaries[0] if summaries else None,
        recent_sessions=summaries,
        launch_suggestions=runtime.catalog.list_launch_suggestions(tenant_id=auth.tenant_id),
    )


def _summary_for_session(
    runtime: Any, auth: AuthContext, session: StudentSession
) -> DashboardSessionSummary:
    chapter = runtime.catalog.get_chapter(
        tenant_id=auth.tenant_id,
        chapter_id=session.chapter_id,
    )
    return DashboardSessionSummary(
        session_id=session.session_id,
        chapter_id=session.chapter_id,
        chapter_title=chapter.title if chapter is not None else "Chapter",
        last_active_at=session.last_active_at,
        status=session.status,
    )
