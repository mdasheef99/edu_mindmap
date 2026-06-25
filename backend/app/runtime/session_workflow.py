"""Session lifecycle orchestration kept out of the FastAPI composition root."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.domain.auth import AuthContext
from app.domain.student.sessions import (
    SessionContext,
    SessionStartRequest,
    StudentSession,
    StudentSessionWithCanvas,
    build_session_resumed,
    build_session_started,
)
from app.events.store import InMemoryEventStore
from app.projections.curriculum import InMemoryCurriculumStore
from app.projections.student_sessions import (
    InMemoryStudentSessionProjectionStore,
    project_session_resumed,
    project_session_started,
)
from app.runtime.canvas_state import canvas_snapshot_from_events
from app.runtime.curriculum_workflow import resolve_session_request
from app.tenancy.pool import InMemoryTenantConnectionPool


def start_session_workflow(
    payload: SessionStartRequest,
    *,
    auth: AuthContext,
    event_store: InMemoryEventStore,
    student_sessions: InMemoryStudentSessionProjectionStore,
    curriculum: InMemoryCurriculumStore,
    seen_users: set[UUID],
) -> StudentSession:
    """Start a new student session, emitting consent_recorded on first sign-in."""
    request = resolve_session_request(
        payload,
        tenant_id=auth.tenant_id,
        curriculum=curriculum,
    )

    if auth.user_id not in seen_users:
        seen_users.add(auth.user_id)
        consent_event = {
            "event_id": uuid4(),
            "event_type": "consent_recorded",
            "event_version": 1,
            "tenant_id": auth.tenant_id,
            "actor_user_id": auth.user_id,
            "student_id": auth.user_id,
            "occurred_at": datetime.now(timezone.utc),
            "payload": {
                "user_id": str(auth.user_id),
                "consent_kind": "behavioral_analytics",
                "grantor": "self",
            },
        }
        event_store.append(consent_event, producer="server")

    event, _, response_model = build_session_started(
        context=SessionContext(
            tenant_id=auth.tenant_id,
            student_user_id=auth.user_id,
        ),
        request=request,
    )
    stored_event = event_store.append(event, producer="server")
    student_sessions.upsert(project_session_started(stored_event))
    return response_model


def get_student_session_with_canvas_workflow(
    *,
    session_id: UUID,
    auth: AuthContext,
    event_store: InMemoryEventStore,
    tenant_pool: InMemoryTenantConnectionPool,
) -> StudentSessionWithCanvas | None:
    """Fetch session row + live canvas snapshot for the authenticated student."""
    with tenant_pool.transaction(auth.tenant_id) as connection:
        session_row = connection.fetch_session_for_student(str(session_id), auth.user_id)
    if session_row is None:
        return None
    snapshot = canvas_snapshot_from_events(
        event_store.events,
        session_id=session_id,
        tenant_id=auth.tenant_id,
        student_user_id=auth.user_id,
    )
    return StudentSessionWithCanvas.model_validate({**session_row, "canvas": snapshot})


def resume_student_session_workflow(
    *,
    session_id: UUID,
    auth: AuthContext,
    event_store: InMemoryEventStore,
    student_sessions: InMemoryStudentSessionProjectionStore,
    tenant_pool: InMemoryTenantConnectionPool,
) -> StudentSession | None:
    """Append session_resumed event and update the projection row."""
    with tenant_pool.transaction(auth.tenant_id) as connection:
        session_row = connection.fetch_session_for_student(str(session_id), auth.user_id)
    if session_row is None:
        return None

    event = build_session_resumed(
        context=SessionContext(tenant_id=auth.tenant_id, student_user_id=auth.user_id),
        session_id=session_id,
    )
    stored_event = event_store.append(event, producer="server")
    updated_row = student_sessions.mark_resumed(project_session_resumed(stored_event))
    return StudentSession.model_validate(updated_row or session_row)
