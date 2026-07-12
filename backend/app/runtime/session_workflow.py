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
    build_root_node_created,
    build_session_resumed,
    build_session_started,
)
from app.generation.provider import GenerationProvider
from app.projections.student_sessions import (
    project_session_resumed,
    project_session_started,
)
from app.runtime.canvas_state import canvas_snapshot_from_events
from app.runtime.curriculum_workflow import resolve_session_request
from app.runtime.ports import (
    ConsentRecordStorePort,
    CurriculumStorePort,
    EventStorePort,
    StudentSessionStorePort,
    TenantPoolPort,
)


def start_session_workflow(
    payload: SessionStartRequest,
    *,
    auth: AuthContext,
    event_store: EventStorePort,
    student_sessions: StudentSessionStorePort,
    curriculum: CurriculumStorePort,
    generation_provider: GenerationProvider,
    consent_records: ConsentRecordStorePort,
) -> StudentSession:
    """Start a student session and persist an explicitly acknowledged consent grant."""
    request = resolve_session_request(
        payload,
        tenant_id=auth.tenant_id,
        curriculum=curriculum,
    )

    if payload.behavioral_analytics_consent:
        record_behavioral_analytics_consent_workflow(
            auth=auth,
            event_store=event_store,
            consent_records=consent_records,
        )

    event, _, response_model = build_session_started(
        context=SessionContext(
            tenant_id=auth.tenant_id,
            student_user_id=auth.user_id,
        ),
        request=request,
    )
    stored_event = event_store.append(event, producer="server")
    student_sessions.upsert(project_session_started(stored_event))
    root_event = build_root_node_created(
        context=SessionContext(
            tenant_id=auth.tenant_id,
            student_user_id=auth.user_id,
        ),
        session=response_model,
        generated_node=generation_provider.root(),
    )
    event_store.append(root_event, producer="server")
    return response_model


def record_behavioral_analytics_consent_workflow(
    *,
    auth: AuthContext,
    event_store: EventStorePort,
    consent_records: ConsentRecordStorePort,
) -> None:
    """Idempotently persist the consent entity and its append-only audit event."""
    if consent_records.has_valid_behavioral_analytics(
        tenant_id=auth.tenant_id,
        student_user_id=auth.user_id,
    ):
        return
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
    stored_event = event_store.append(consent_event, producer="server")
    consent_records.grant_behavioral_analytics(
        tenant_id=auth.tenant_id,
        student_user_id=auth.user_id,
        event_id=stored_event["event_id"],
    )


def get_student_session_with_canvas_workflow(
    *,
    session_id: UUID,
    auth: AuthContext,
    event_store: EventStorePort,
    tenant_pool: TenantPoolPort,
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
    event_store: EventStorePort,
    student_sessions: StudentSessionStorePort,
    tenant_pool: TenantPoolPort,
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
