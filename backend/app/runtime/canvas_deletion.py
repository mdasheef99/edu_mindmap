"""Event-sourced canvas deletion cascade workflow."""

from __future__ import annotations

from collections import deque
from uuid import UUID

from app.domain.auth import AuthContext
from app.domain.student.deletions import (
    DeletionConfirmationRequired,
    NodeDeletionResponse,
    build_edge_deleted,
    build_node_deleted,
)
from app.events.store import InMemoryEventStore
from app.runtime.canvas_state import active_canvas_from_events
from app.tenancy.pool import InMemoryTenantConnectionPool


def delete_node_cascade_workflow(
    *,
    session_id: UUID,
    node_id: UUID,
    confirmed: bool,
    auth: AuthContext,
    tenant_pool: InMemoryTenantConnectionPool,
    event_store: InMemoryEventStore,
) -> NodeDeletionResponse | None:
    if not confirmed:
        raise DeletionConfirmationRequired("node deletion requires confirmed=true")

    with tenant_pool.transaction(auth.tenant_id) as connection:
        session_row = connection.fetch_session_for_student(str(session_id), auth.user_id)
    if session_row is None:
        return None

    active_nodes, active_edges = active_canvas_from_events(
        event_store.events,
        session_id=session_id,
        tenant_id=auth.tenant_id,
        student_user_id=auth.user_id,
    )
    if str(node_id) not in active_nodes:
        return None

    deleted_node_ids, deleted_edges = _cascade_from_root(
        root_node_id=str(node_id),
        active_nodes=active_nodes,
        active_edges=active_edges,
    )
    deleted_edge_ids = [UUID(edge["edge_id"]) for edge in deleted_edges]
    deleted_node_uuids = [UUID(deleted_node_id) for deleted_node_id in deleted_node_ids]

    event_count = len(event_store.events)
    try:
        for edge in deleted_edges:
            event_store.append(
                build_edge_deleted(
                    tenant_id=auth.tenant_id,
                    student_user_id=auth.user_id,
                    session_id=session_id,
                    root_node_id=node_id,
                    edge=edge,
                ),
                producer="server",
            )
        node_deleted_event, response = build_node_deleted(
            tenant_id=auth.tenant_id,
            student_user_id=auth.user_id,
            session_id=session_id,
            root_node_id=node_id,
            deleted_node_ids=deleted_node_uuids,
            deleted_edge_ids=deleted_edge_ids,
        )
        event_store.append(node_deleted_event, producer="server")
    except Exception:
        event_store.rollback_to(event_count)
        raise
    return response


def _cascade_from_root(
    *, root_node_id: str, active_nodes: set[str], active_edges: dict[str, dict[str, str]]
) -> tuple[list[str], list[dict[str, str]]]:
    deleted_nodes: list[str] = [root_node_id]
    seen_nodes = {root_node_id}
    queue: deque[str] = deque([root_node_id])

    while queue:
        current_node_id = queue.popleft()
        for edge in active_edges.values():
            if edge["edge_kind"] != "ai_path" or edge["source_node_id"] != current_node_id:
                continue
            target_node_id = edge["target_node_id"]
            if target_node_id in active_nodes and target_node_id not in seen_nodes:
                seen_nodes.add(target_node_id)
                deleted_nodes.append(target_node_id)
                queue.append(target_node_id)

    deleted_node_set = set(deleted_nodes)
    deleted_edges = [
        edge
        for edge in active_edges.values()
        if edge["source_node_id"] in deleted_node_set or edge["target_node_id"] in deleted_node_set
    ]
    return deleted_nodes, deleted_edges
