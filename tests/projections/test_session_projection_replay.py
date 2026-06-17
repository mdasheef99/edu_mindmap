from datetime import datetime, timezone
from uuid import uuid4


def test_first_projection_rebuild_is_byte_identical() -> None:
    """T15: the first projection rebuild must be byte-identical."""
    from app.domain.student.sessions import SessionContext, SessionStartRequest, build_session_started
    from app.projections.student_sessions import (
        InMemoryStudentSessionProjectionStore,
        project_session_started,
        rebuild_session_projection,
    )

    event, _, _ = build_session_started(
        context=SessionContext(
            tenant_id=uuid4(),
            student_user_id=uuid4(),
        ),
        request=SessionStartRequest(
            exam_id=uuid4(),
            subject_id=uuid4(),
            chapter_id=uuid4(),
            concept_entry_id=uuid4(),
            chapter_analysis_id=uuid4(),
        ),
        now=datetime(2026, 6, 17, tzinfo=timezone.utc),
        session_id=uuid4(),
        event_id=uuid4(),
    )

    store = InMemoryStudentSessionProjectionStore()
    store.upsert(project_session_started(event))

    assert rebuild_session_projection([event]).snapshot_bytes() == store.snapshot_bytes()


def test_projection_is_idempotent_on_replay() -> None:
    """T16: applying the same projection events twice must be a no-op."""
    from app.domain.student.sessions import SessionContext, SessionStartRequest, build_session_started
    from app.projections.student_sessions import (
        InMemoryStudentSessionProjectionStore,
        apply_session_projection_events,
    )

    event, _, _ = build_session_started(
        context=SessionContext(
            tenant_id=uuid4(),
            student_user_id=uuid4(),
        ),
        request=SessionStartRequest(
            exam_id=uuid4(),
            subject_id=uuid4(),
            chapter_id=uuid4(),
            concept_entry_id=uuid4(),
            chapter_analysis_id=uuid4(),
        ),
        now=datetime(2026, 6, 17, tzinfo=timezone.utc),
        session_id=uuid4(),
        event_id=uuid4(),
    )
    store = InMemoryStudentSessionProjectionStore()

    apply_session_projection_events(store, [event])
    first_snapshot = store.snapshot_bytes()
    apply_session_projection_events(store, [event])

    assert store.snapshot_bytes() == first_snapshot