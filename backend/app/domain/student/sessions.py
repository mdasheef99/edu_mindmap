"""Student-safe session models and pure session-start construction."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel


class SessionStartRequest(BaseModel):
    exam_id: UUID
    subject_id: UUID
    chapter_id: UUID
    concept_entry_id: UUID
    chapter_analysis_id: UUID


class SessionContext(BaseModel):
    tenant_id: UUID
    student_user_id: UUID


class StudentSession(BaseModel):
    session_id: UUID
    student_user_id: UUID
    exam_id: UUID
    subject_id: UUID
    chapter_id: UUID
    concept_entry_id: UUID
    chapter_analysis_id: UUID
    status: str
    last_active_node_id: UUID | None = None
    started_at: datetime
    last_active_at: datetime


def build_session_started(
    *,
    context: SessionContext,
    request: SessionStartRequest,
    now: datetime | None = None,
    session_id: UUID | None = None,
    event_id: UUID | None = None,
) -> tuple[dict[str, Any], dict[str, Any], StudentSession]:
    occurred_at = now or datetime.now(timezone.utc)
    resolved_session_id = session_id or uuid4()
    resolved_event_id = event_id or uuid4()
    payload = {
        "session_id": str(resolved_session_id),
        "student_user_id": str(context.student_user_id),
        "exam_id": str(request.exam_id),
        "subject_id": str(request.subject_id),
        "chapter_id": str(request.chapter_id),
        "concept_entry_id": str(request.concept_entry_id),
        "chapter_analysis_id": str(request.chapter_analysis_id),
    }
    event = {
        "event_id": resolved_event_id,
        "event_type": "session_started",
        "event_version": 1,
        "tenant_id": context.tenant_id,
        "actor_user_id": context.student_user_id,
        "student_id": context.student_user_id,
        "session_id": resolved_session_id,
        "exam_id": request.exam_id,
        "subject_id": request.subject_id,
        "chapter_id": request.chapter_id,
        "chapter_analysis_id": request.chapter_analysis_id,
        "concept_entry_id": request.concept_entry_id,
        "occurred_at": occurred_at,
        "payload": payload,
    }
    session_row = {
        "session_id": resolved_session_id,
        "tenant_id": context.tenant_id,
        "student_user_id": context.student_user_id,
        "exam_id": request.exam_id,
        "subject_id": request.subject_id,
        "chapter_id": request.chapter_id,
        "concept_entry_id": request.concept_entry_id,
        "chapter_analysis_id": request.chapter_analysis_id,
        "status": "active",
        "last_active_node_id": None,
        "started_at": occurred_at,
        "last_active_at": occurred_at,
        "closed_at": None,
    }
    return event, session_row, StudentSession.model_validate(session_row)
