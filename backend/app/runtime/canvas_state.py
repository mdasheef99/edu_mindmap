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
        payload = event.get("payload")
        if not isinstance(payload, dict):
            raise ValueError(f"Event payload must be a dict for event: {event}")
        if event["event_type"] == "node_created":
            node_id = payload.get("node_id")
            if node_id is None:
                raise KeyError(f"node_created payload missing required key 'node_id': {payload}")
            active_nodes.add(str(node_id))
        elif event["event_type"] == "edge_created":
            edge_id = payload.get("edge_id")
            if edge_id is None:
                raise KeyError(f"edge_created payload missing required key 'edge_id': {payload}")
            active_edges[str(edge_id)] = _edge_payload(payload)
        elif event["event_type"] == "edge_deleted":
            edge_id = payload.get("edge_id")
            if edge_id is None:
                raise KeyError(f"edge_deleted payload missing required key 'edge_id': {payload}")
            active_edges.pop(str(edge_id), None)
        elif event["event_type"] == "node_deleted":
            for deleted_node_id in payload.get("deleted_node_ids", []):
                active_nodes.discard(str(deleted_node_id))
            for deleted_edge_id in payload.get("deleted_edge_ids", []):
                active_edges.pop(str(deleted_edge_id), None)
    return active_nodes, active_edges


def canvas_snapshot_from_events(
    events: list[dict[str, Any]],
    *,
    session_id: UUID,
    tenant_id: UUID,
    student_user_id: UUID,
) -> dict[str, Any]:
    """Return {"nodes": [...], "edges": [...]} for GET /sessions/{id}.

    Replays node_created, edge_created, edge_deleted, node_deleted, and
    node_position_updated in temporal order. node_position_updated supersedes the
    initial position for any node_id it names. Returns only student-safe
    (student_rm) fields — no analytic data (Category Invisibility invariant).
    """
    nodes: dict[str, dict[str, Any]] = {}
    edges: dict[str, dict[str, Any]] = {}
    for event in events:
        if not _same_scope(event, session_id, tenant_id, student_user_id):
            continue
        payload = event.get("payload")
        if not isinstance(payload, dict):
            raise ValueError(f"Event payload must be a dict for event: {event}")
        event_type = event["event_type"]
        if event_type == "node_created":
            node_id = payload.get("node_id")
            if node_id is None:
                continue
            nodes[str(node_id)] = {
                "node_id": str(node_id),
                "node_type": str(payload.get("node_type")),
                "content": str(payload.get("content")),
                "position_x": None,
                "position_y": None,
                "thread_context_id": payload.get("thread_context_id"),
            }
        elif event_type == "edge_created":
            edge_id = payload.get("edge_id")
            if edge_id is None:
                continue
            edges[str(edge_id)] = {
                "edge_id": str(edge_id),
                "source_node_id": str(payload.get("source_node_id")),
                "target_node_id": str(payload.get("target_node_id")),
                "edge_kind": str(payload.get("edge_kind")),
                "label": payload.get("label"),
            }
        elif event_type == "edge_deleted":
            edges.pop(str(payload.get("edge_id")), None)
        elif event_type == "node_deleted":
            for deleted_node_id in payload.get("deleted_node_ids", []):
                nodes.pop(str(deleted_node_id), None)
            for deleted_edge_id in payload.get("deleted_edge_ids", []):
                edges.pop(str(deleted_edge_id), None)
        elif event_type == "node_position_updated":
            node = nodes.get(str(payload.get("node_id")))
            if node is not None:
                node["position_x"] = payload.get("position_x")
                node["position_y"] = payload.get("position_y")
    return {"nodes": list(nodes.values()), "edges": list(edges.values())}


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
    missing_keys = [
        key for key in ("edge_id", "session_id", "source_node_id", "target_node_id", "edge_kind")
        if payload.get(key) is None
    ]
    if missing_keys:
        raise KeyError(f"edge_created payload missing required keys {missing_keys}: {payload}")
    return {
        "edge_id": str(payload["edge_id"]),
        "session_id": str(payload["session_id"]),
        "source_node_id": str(payload["source_node_id"]),
        "target_node_id": str(payload["target_node_id"]),
        "edge_kind": str(payload["edge_kind"]),
    }
