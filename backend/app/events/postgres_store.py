"""Postgres-backed event store implementation for Phase 1 deployment wiring."""

from __future__ import annotations

import json
from typing import Any, Mapping

from app.events.registry import validate_event
from app.tenancy.postgres_context import set_local_tenant

INSERT_EVENT_SQL = """
INSERT INTO events (
    event_id, event_type, event_version, tenant_id, actor_user_id, student_id,
    session_id, exam_id, subject_id, chapter_id, chapter_analysis_id,
    concept_entry_id, node_id, offer_set_id, occurred_at, producer, payload,
    policy_version, prompt_version, model_id, projection_version, replay_id
) VALUES (
    %(event_id)s, %(event_type)s, %(event_version)s, %(tenant_id)s,
    %(actor_user_id)s, %(student_id)s, %(session_id)s, %(exam_id)s,
    %(subject_id)s, %(chapter_id)s, %(chapter_analysis_id)s,
    %(concept_entry_id)s, %(node_id)s, %(offer_set_id)s, %(occurred_at)s,
    %(producer)s, %(payload)s::jsonb, %(policy_version)s, %(prompt_version)s,
    %(model_id)s, %(projection_version)s, %(replay_id)s
) RETURNING *
"""

SELECT_EVENT_SQL = """
SELECT * FROM events WHERE event_id = %(event_id)s
"""

SELECT_EVENTS_SQL = """
SELECT * FROM events ORDER BY recorded_at, event_id
"""


class PostgresEventStore:
    """Append-only event store using the migration 0001 `events` table."""

    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def append(self, event: Mapping[str, Any], *, producer: str) -> dict[str, Any]:
        validate_event(event, producer=producer)
        params = {key: event.get(key) for key in _EVENT_COLUMNS}
        params["payload"] = json.dumps(event.get("payload", {}), default=str)
        params["producer"] = producer
        with self.connection.transaction():
            set_local_tenant(self.connection, event["tenant_id"])
            cursor = self.connection.execute(INSERT_EVENT_SQL, params)
            row = cursor.fetchone()
        return _row_to_dict(row) | {"producer": producer}

    def get_event_by_id(self, event_id: str, *, tenant_id: Any | None = None) -> dict[str, Any]:
        with self.connection.transaction():
            if tenant_id is not None:
                set_local_tenant(self.connection, tenant_id)
            cursor = self.connection.execute(SELECT_EVENT_SQL, {"event_id": event_id})
            row = cursor.fetchone()
        if row is None:
            raise LookupError(f"event not found: {event_id}")
        return _row_to_dict(row)

    @property
    def events(self) -> list[dict[str, Any]]:
        """Return events visible under the current transaction-local tenant context."""
        with self.connection.transaction():
            cursor = self.connection.execute(SELECT_EVENTS_SQL)
            return [_row_to_dict(row) for row in cursor.fetchall()]

    def rollback_to(self, event_count: int) -> None:
        """Compatibility hook; the surrounding Postgres transaction performs rollback."""
        del event_count


_EVENT_COLUMNS = (
    "event_id",
    "event_type",
    "event_version",
    "tenant_id",
    "actor_user_id",
    "student_id",
    "session_id",
    "exam_id",
    "subject_id",
    "chapter_id",
    "chapter_analysis_id",
    "concept_entry_id",
    "node_id",
    "offer_set_id",
    "occurred_at",
    "payload",
    "policy_version",
    "prompt_version",
    "model_id",
    "projection_version",
    "replay_id",
)


def _row_to_dict(row: Any) -> dict[str, Any]:
    if isinstance(row, Mapping):
        return dict(row)
    if hasattr(row, "_asdict"):
        return dict(row._asdict())
    return dict(row)
