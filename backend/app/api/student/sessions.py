"""Student session router for the first POST /v1/student/sessions slice."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.domain.auth import AuthContext
from app.domain.student.sessions import (
    ChapterLaunchNotFoundError,
    SessionStartRequest,
    StudentSession,
)
from app.tenancy.auth import get_auth_context

router = APIRouter(prefix="/v1/student", tags=["student"])


@router.get("/sessions/recent", response_model=list[StudentSession])
def list_recent_sessions(
    request: Request,
    auth: AuthContext = Depends(get_auth_context),
) -> list[StudentSession]:
    runtime = request.app.state.session_runtime
    return runtime.list_recent_student_sessions(auth=auth)


@router.post("/sessions", response_model=StudentSession, status_code=status.HTTP_201_CREATED)
def start_session(
    payload: SessionStartRequest,
    request: Request,
    auth: AuthContext = Depends(get_auth_context),
) -> StudentSession:
    runtime = request.app.state.session_runtime
    try:
        return runtime.start_session(payload, auth=auth)
    except ChapterLaunchNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Chapter not found in curriculum") from exc


@router.post("/sessions/{session_id}/resume", response_model=StudentSession)
def resume_session(
    session_id: UUID,
    request: Request,
    auth: AuthContext = Depends(get_auth_context),
) -> StudentSession:
    runtime = request.app.state.session_runtime
    session = runtime.resume_student_session(session_id=session_id, auth=auth)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
