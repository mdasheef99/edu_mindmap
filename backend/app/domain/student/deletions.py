"""Student-safe deletion cascade models and event construction."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import UUID, uuid4

from pydantic import BaseModel


class DeletionConfirmationRequired(Exception):
    """Raised when a destructive node deletion request lacks confirmation."""


class NodeDeletionResponse(BaseModel):
    session_id: UUID
    root_node_id: UUID
    deleted_node_ids: list[UUID]
    deleted_edge_ids: list[UUID]
    confirmed: bool


def build_edge_deleted(
    *,
    tenant_id: UUID,
    student_user_id: UUID,
    session_id: UUID,
    root_node_id: UUID,
    edge: Mapping[str, Any],
    now: datetime | None = None,
    event_id: UUID | None = None,
) -> dict[str, Any]:
    occurred_at = now or datetime.now(timezone.utc)
    edge_id = UUID(str(edge["edge_id"]))
    payload = {
        "edge_id": str(edge_id),
        "session_id": str(session_id),
        "source_node_id": str(edge["source_node_id"]),
        "target_node_id": str(edge["target_node_id"]),
        "edge_kind": edge["edge_kind"],
        "deletion_cause": "node_cascade",
        "root_node_id": str(root_node_id),
    }
    return {
        "event_id": event_id or uuid4(),
        "event_type": "edge_deleted",
        "event_version": 1,
        "tenant_id": tenant_id,
        "actor_user_id": student_user_id,
        "student_id": student_user_id,
        "session_id": session_id,
        "node_id": root_node_id,
        "edge_id": edge_id,
        "occurred_at": occurred_at,
        "payload": payload,
    }


def build_node_deleted(
    *,
    tenant_id: UUID,
    student_user_id: UUID,
    session_id: UUID,
    root_node_id: UUID,
    deleted_node_ids: list[UUID],
    deleted_edge_ids: list[UUID],
    now: datetime | None = None,
    event_id: UUID | None = None,
) -> tuple[dict[str, Any], NodeDeletionResponse]:
    occurred_at = now or datetime.now(timezone.utc)
    payload = {
        "root_node_id": str(root_node_id),
        "session_id": str(session_id),
        "deleted_node_ids": [str(node_id) for node_id in deleted_node_ids],
        "deleted_edge_ids": [str(edge_id) for edge_id in deleted_edge_ids],
        "confirmed": True,
        "deletion_cause": "user_confirmed_node_delete",
    }
    event = {
        "event_id": event_id or uuid4(),
        "event_type": "node_deleted",
        "event_version": 1,
        "tenant_id": tenant_id,
        "actor_user_id": student_user_id,
        "student_id": student_user_id,
        "session_id": session_id,
        "node_id": root_node_id,
        "occurred_at": occurred_at,
        "payload": payload,
    }
    response = NodeDeletionResponse(
        session_id=session_id,
        root_node_id=root_node_id,
        deleted_node_ids=deleted_node_ids,
        deleted_edge_ids=deleted_edge_ids,
        confirmed=True,
    )
    return event, response
