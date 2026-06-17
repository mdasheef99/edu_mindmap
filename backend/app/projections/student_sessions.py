"""Minimal student_rm.sessions projection for the first Phase 1 slice."""

from __future__ import annotations

from copy import deepcopy
import json
from typing import Any, Mapping
from uuid import UUID


class InMemoryStudentSessionProjectionStore:
    """Student-safe session rows keyed by session_id string."""

    def __init__(self) -> None:
        self.sessions: dict[str, dict[str, Any]] = {}

    def upsert(self, session_row: Mapping[str, Any]) -> dict[str, Any]:
        stored_row = deepcopy(dict(session_row))
        self.sessions[str(stored_row["session_id"])] = stored_row
        return stored_row

    def get_for_tenant(self, session_id: str | UUID, tenant_id: UUID) -> dict[str, Any] | None:
        session_row = self.sessions.get(str(session_id))
        if session_row is None or session_row["tenant_id"] != tenant_id:
            return None
        return deepcopy(session_row)

    def snapshot_bytes(self) -> bytes:
        return json.dumps(
            self.sessions,
            sort_keys=True,
            default=_json_default,
            separators=(",", ":"),
        ).encode("utf-8")


def project_session_started(event: Mapping[str, Any]) -> dict[str, Any]:
    """Project one session_started event into the student session read model."""
    return {
        "session_id": event["session_id"],
        "tenant_id": event["tenant_id"],
        "student_user_id": event["student_id"],
        "exam_id": event["exam_id"],
        "subject_id": event["subject_id"],
        "chapter_id": event["chapter_id"],
        "concept_entry_id": event["concept_entry_id"],
        "chapter_analysis_id": event["chapter_analysis_id"],
        "status": "active",
        "last_active_node_id": None,
        "started_at": event["occurred_at"],
        "last_active_at": event["occurred_at"],
        "closed_at": None,
    }


def rebuild_session_projection(
    events: list[Mapping[str, Any]],
) -> InMemoryStudentSessionProjectionStore:
    store = InMemoryStudentSessionProjectionStore()
    apply_session_projection_events(store, events)
    return store


def apply_session_projection_events(
    store: InMemoryStudentSessionProjectionStore,
    events: list[Mapping[str, Any]],
) -> InMemoryStudentSessionProjectionStore:
    for event in events:
        if event.get("event_type") == "session_started":
            store.upsert(project_session_started(event))
    return store


def _json_default(value: Any) -> str:
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)