"""Student-safe session models and pure session-start construction."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel

from app.generation.provider import GeneratedNode


class ChapterLaunchNotFoundError(Exception):
    """Raised when a requested chapter is not launchable from curriculum for this tenant."""


class SessionStartRequest(BaseModel):
    exam_id: UUID
    subject_id: UUID
    chapter_id: UUID
    concept_entry_id: UUID
    chapter_analysis_id: UUID | None = None


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


class CanvasNodeSnapshot(BaseModel):
    node_id: UUID
    node_type: str
    content: str
    position_x: float | None = None
    position_y: float | None = None
    thread_context_id: UUID | None = None


class CanvasEdgeSnapshot(BaseModel):
    edge_id: UUID
    source_node_id: UUID
    target_node_id: UUID
    edge_kind: str
    label: str | None = None


class CanvasSnapshot(BaseModel):
    nodes: list[CanvasNodeSnapshot]
    edges: list[CanvasEdgeSnapshot]


class StudentSessionWithCanvas(StudentSession):
    canvas: CanvasSnapshot


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


def build_root_node_created(
    *,
    context: SessionContext,
    session: StudentSession,
    generated_node: GeneratedNode,
    now: datetime | None = None,
    event_id: UUID | None = None,
    node_id: UUID | None = None,
) -> dict[str, Any]:
    occurred_at = now or datetime.now(timezone.utc)
    resolved_event_id = event_id or uuid4()
    resolved_node_id = node_id or uuid4()
    payload = {
        "node_id": str(resolved_node_id),
        "session_id": str(session.session_id),
        "node_type": "ai",
        "content": generated_node.node_body,
        "source_node_id": str(session.concept_entry_id),
        "source_offer_set_id": str(session.session_id),
        "source_option_id": str(session.concept_entry_id),
        "source_option_text": generated_node.node_title,
        "thread_context_id": str(session.concept_entry_id),
        "fixture_node_key": generated_node.node_key,
        "node_title": generated_node.node_title,
        "prompt_version": generated_node.prompt_version,
        "model_id": generated_node.model_id,
        "lineage": generated_node.lineage,
    }
    return {
        "event_id": resolved_event_id,
        "event_type": "node_created",
        "event_version": 1,
        "tenant_id": context.tenant_id,
        "actor_user_id": context.student_user_id,
        "student_id": context.student_user_id,
        "session_id": session.session_id,
        "node_id": resolved_node_id,
        "occurred_at": occurred_at,
        "payload": payload,
    }


def build_session_resumed(
    *,
    context: SessionContext,
    session_id: UUID,
    now: datetime | None = None,
    event_id: UUID | None = None,
) -> dict[str, Any]:
    occurred_at = now or datetime.now(timezone.utc)
    resolved_event_id = event_id or uuid4()
    return {
        "event_id": resolved_event_id,
        "event_type": "session_resumed",
        "event_version": 1,
        "tenant_id": context.tenant_id,
        "actor_user_id": context.student_user_id,
        "student_id": context.student_user_id,
        "session_id": session_id,
        "occurred_at": occurred_at,
        "payload": {
            "session_id": str(session_id),
            "student_user_id": str(context.student_user_id),
        },
    }
