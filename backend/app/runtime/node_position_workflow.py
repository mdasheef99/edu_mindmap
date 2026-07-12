"""Node-position update orchestration kept out of the FastAPI composition root."""

from __future__ import annotations

from math import isfinite
from uuid import UUID

from app.domain.auth import AuthContext
from app.domain.student.nodes import (
    NodePositionResponse,
    NodePositionUpdate,
    build_node_position_updated,
)
from app.runtime.canvas_state import active_canvas_from_events
from app.runtime.ports import EventStorePort, TenantPoolPort


def update_node_position_workflow(
    *,
    session_id: UUID,
    node_id: UUID,
    payload: NodePositionUpdate,
    auth: AuthContext,
    event_store: EventStorePort,
    tenant_pool: TenantPoolPort,
) -> NodePositionResponse | None:
    """Validate, guard, and record a node-position update event.

    Returns None when the session or node is not accessible to the student.
    Raises ValueError for non-finite coordinate values.
    """
    if not (isfinite(payload.position_x) and isfinite(payload.position_y)):
        raise ValueError("position_x and position_y must be finite numbers")

    with tenant_pool.transaction(auth.tenant_id) as connection:
        session_row = connection.fetch_session_for_student(str(session_id), auth.user_id)
    if session_row is None:
        return None

    active_nodes, _ = active_canvas_from_events(
        event_store.events,
        session_id=session_id,
        tenant_id=auth.tenant_id,
        student_user_id=auth.user_id,
    )
    if str(node_id) not in active_nodes:
        return None

    event = build_node_position_updated(
        tenant_id=auth.tenant_id,
        student_user_id=auth.user_id,
        session_id=session_id,
        node_id=node_id,
        position_x=payload.position_x,
        position_y=payload.position_y,
    )
    event_store.append(event, producer="client")
    return NodePositionResponse(
        node_id=node_id,
        position_x=payload.position_x,
        position_y=payload.position_y,
    )
