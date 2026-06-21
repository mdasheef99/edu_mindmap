"""Shared event-sourced reconstruction of a session's active canvas.

Replaying node_created / edge_created / edge_deleted / node_deleted in order yields the set
of active nodes and edges for one (tenant, student, session) scope. Both the deletion-cascade
workflow and the node-limit guard derive their state from this single helper rather than
duplicating the replay logic (canon: shared helpers, not copy-paste).

Traceability:
- docs/architecture/backend-architecture.md §5.3 (canvas event family)
- docs/planning/sdd/phase-3-m3-canvas-sdd.md §11 (node limits)
"""

from __future__ import annotations

from typing import Any, Mapping
from uuid import UUID


def active_canvas_from_events(
    events: list[dict[str, Any]],
    *,
    session_id: UUID,
    tenant_id: UUID,
    student_user_id: UUID,
) -> tuple[set[str], dict[str, dict[str, str]]]:
    """Replay events in scope, returning (active_node_ids, active_edges_by_id)."""
    active_nodes: set[str] = set()
    active_edges: dict[str, dict[str, str]] = {}
    for event in events:
        if not _same_scope(event, session_id, tenant_id, student_user_id):
            continue
        payload = event["payload"]
        if event["event_type"] == "node_created":
            active_nodes.add(str(payload["node_id"]))
        elif event["event_type"] == "edge_created":
            active_edges[str(payload["edge_id"])] = _edge_payload(payload)
        elif event["event_type"] == "edge_deleted":
            active_edges.pop(str(payload["edge_id"]), None)
        elif event["event_type"] == "node_deleted":
            for deleted_node_id in payload["deleted_node_ids"]:
                active_nodes.discard(str(deleted_node_id))
            for deleted_edge_id in payload["deleted_edge_ids"]:
                active_edges.pop(str(deleted_edge_id), None)
    return active_nodes, active_edges


def count_active_nodes(
    events: list[dict[str, Any]],
    *,
    session_id: UUID,
    tenant_id: UUID,
    student_user_id: UUID,
) -> int:
    """Return the number of active (created and not deleted) nodes for the scope."""
    active_nodes, _ = active_canvas_from_events(
        events,
        session_id=session_id,
        tenant_id=tenant_id,
        student_user_id=student_user_id,
    )
    return len(active_nodes)


def _same_scope(
    event: Mapping[str, Any], session_id: UUID, tenant_id: UUID, student_user_id: UUID
) -> bool:
    return (
        event.get("session_id") == session_id
        and event.get("tenant_id") == tenant_id
        and event.get("student_id") == student_user_id
    )


def _edge_payload(payload: Mapping[str, Any]) -> dict[str, str]:
    return {
        "edge_id": str(payload["edge_id"]),
        "session_id": str(payload["session_id"]),
        "source_node_id": str(payload["source_node_id"]),
        "target_node_id": str(payload["target_node_id"]),
        "edge_kind": str(payload["edge_kind"]),
    }
