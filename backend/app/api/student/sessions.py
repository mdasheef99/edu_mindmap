"""Student session router for the first POST /v1/student/sessions slice."""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from app.domain.student.sessions import SessionStartRequest, StudentSession


router = APIRouter(prefix="/v1/student", tags=["student"])


@router.post("/sessions", response_model=StudentSession, status_code=status.HTTP_201_CREATED)
def start_session(payload: SessionStartRequest, request: Request) -> StudentSession:
    runtime = request.app.state.session_runtime
    return runtime.start_session(payload)