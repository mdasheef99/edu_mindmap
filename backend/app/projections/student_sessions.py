"""Minimal student_rm.sessions projection for the first Phase 1 slice."""

from __future__ import annotations

import json
from copy import deepcopy
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

    def get_for_tenant_and_student(
        self, session_id: str | UUID, tenant_id: UUID, student_user_id: UUID
    ) -> dict[str, Any] | None:
        session_row = self.get_for_tenant(session_id, tenant_id)
        if session_row is None or session_row["student_user_id"] != student_user_id:
            return None
        return session_row

    def list_recent_for_tenant_and_student(
        self, *, tenant_id: UUID, student_user_id: UUID, limit: int = 5
    ) -> list[dict[str, Any]]:
        rows = [
            deepcopy(row)
            for row in self.sessions.values()
            if row["tenant_id"] == tenant_id and row["student_user_id"] == student_user_id
        ]
        rows.sort(
            key=lambda row: (row["last_active_at"], row["started_at"], str(row["session_id"])),
            reverse=True,
        )
        return rows[:limit]

    def mark_resumed(self, resume_row: Mapping[str, Any]) -> dict[str, Any] | None:
        session_id = str(resume_row["session_id"])
        session_row = self.sessions.get(session_id)
        if session_row is None:
            return None
        if (
            session_row["tenant_id"] != resume_row["tenant_id"]
            or session_row["student_user_id"] != resume_row["student_user_id"]
        ):
            return None
        updated_row = deepcopy(session_row)
        updated_row["status"] = "active"
        updated_row["last_active_at"] = resume_row["last_active_at"]
        self.sessions[session_id] = updated_row
        return deepcopy(updated_row)

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


def project_session_resumed(event: Mapping[str, Any]) -> dict[str, Any]:
    """Project one session_resumed event into the student session read model."""
    return {
        "session_id": event["session_id"],
        "tenant_id": event["tenant_id"],
        "student_user_id": event["student_id"],
        "last_active_at": event["occurred_at"],
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
        elif event.get("event_type") == "session_resumed":
            store.mark_resumed(project_session_resumed(event))
    return store


def _json_default(value: Any) -> str:
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)
