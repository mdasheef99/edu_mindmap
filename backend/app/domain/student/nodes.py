"""Student-safe node position persistence model and event construction.

PATCH /v1/student/sessions/{id}/nodes/{id} persists a canvas node's layout
coordinates by appending a node_position_updated v1 event (registry §4.2).

Traceability:
- docs/planning/sdd/phase-3-m3c-infrastructure-remediation-sdd.md §4.2, §6.3
- docs/api/student-api-spec.md §6 (PATCH /nodes/{id})
- docs/planning/session-path-data-contract.md §6 (node layout/position contract)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel


class NodePositionUpdate(BaseModel):
    position_x: float
    position_y: float


class NodePositionResponse(BaseModel):
    node_id: UUID
    position_x: float
    position_y: float


def build_node_position_updated(
    *,
    tenant_id: UUID,
    student_user_id: UUID,
    session_id: UUID,
    node_id: UUID,
    position_x: float,
    position_y: float,
    now: datetime | None = None,
    event_id: UUID | None = None,
) -> dict[str, Any]:
    occurred_at = now or datetime.now(timezone.utc)
    payload = {
        "node_id": str(node_id),
        "session_id": str(session_id),
        "position_x": position_x,
        "position_y": position_y,
    }
    return {
        "event_id": event_id or uuid4(),
        "event_type": "node_position_updated",
        "event_version": 1,
        "tenant_id": tenant_id,
        "actor_user_id": student_user_id,
        "student_id": student_user_id,
        "session_id": session_id,
        "node_id": node_id,
        "occurred_at": occurred_at,
        "payload": payload,
    }
