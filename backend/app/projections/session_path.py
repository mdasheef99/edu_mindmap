"""Deterministic replay of one session path from append-only events."""

from __future__ import annotations

import json
from copy import deepcopy
from typing import Any, Mapping
from uuid import UUID


class InMemorySessionPathProjectionStore:
    """Student-safe session-path views keyed by session_id string."""

    def __init__(self) -> None:
        self.sessions: dict[str, dict[str, Any]] = {}

    def get_for_tenant_and_student(
        self, session_id: str | UUID, tenant_id: UUID, student_user_id: UUID
    ) -> dict[str, Any] | None:
        session = self.sessions.get(str(session_id))
        if session is None:
            return None
        if session["tenant_id"] != tenant_id or session["student_user_id"] != student_user_id:
            return None
        return _public_row(session)

    def snapshot_bytes(self) -> bytes:
        payload = {
            session_id: _public_row(session)
            for session_id, session in sorted(self.sessions.items(), key=lambda item: item[0])
        }
        return json.dumps(
            payload,
            sort_keys=True,
            default=_json_default,
            separators=(",", ":"),
        ).encode("utf-8")


def rebuild_session_path_projection(
    events: list[Mapping[str, Any]],
) -> InMemorySessionPathProjectionStore:
    store = InMemorySessionPathProjectionStore()
    apply_session_path_projection_events(store, events)
    return store


def apply_session_path_projection_events(
    store: InMemorySessionPathProjectionStore,
    events: list[Mapping[str, Any]],
) -> InMemorySessionPathProjectionStore:
    for event_order, event in enumerate(events):
        event_type = event.get("event_type")
        if event_type == "session_started":
            _apply_session_started(store, event, event_order)
        elif event_type == "session_resumed":
            _apply_session_resumed(store, event)
        elif event_type == "offer_set_created":
            _apply_offer_set_created(store, event, event_order)
        elif event_type == "offer_set_impression":
            _apply_offer_set_impression(store, event, event_order)
        elif event_type == "offer_set_choice":
            _apply_offer_set_choice(store, event, event_order)
        elif event_type == "node_created":
            _apply_node_created(store, event, event_order)
        elif event_type == "edge_created":
            _apply_edge_created(store, event, event_order)
        elif event_type == "edge_deleted":
            _apply_edge_deleted(store, event)
        elif event_type == "node_deleted":
            _apply_node_deleted(store, event)
    return store


def _apply_session_started(
    store: InMemorySessionPathProjectionStore, event: Mapping[str, Any], event_order: int
) -> None:
    session = _session_state(store, event)
    session.update(
        {
            "exam_id": event["exam_id"],
            "subject_id": event["subject_id"],
            "chapter_id": event["chapter_id"],
            "concept_entry_id": event["concept_entry_id"],
            "chapter_analysis_id": event["chapter_analysis_id"],
            "started_at": event["occurred_at"],
            "last_active_at": event["occurred_at"],
            "_session_order": session.get("_session_order", event_order),
        }
    )


def _apply_session_resumed(
    store: InMemorySessionPathProjectionStore, event: Mapping[str, Any]
) -> None:
    _session_state(store, event)["last_active_at"] = event["occurred_at"]


def _apply_offer_set_created(
    store: InMemorySessionPathProjectionStore, event: Mapping[str, Any], event_order: int
) -> None:
    payload = event["payload"]
    offer = _offer_state(store, event, event_order)
    offer.update(
        {
            "offer_set_id": event["offer_set_id"],
            "source_node_id": UUID(payload["source_node_id"]),
            "launch_method": payload["launch_method"],
            "created_at": event["occurred_at"],
        }
    )


def _apply_offer_set_impression(
    store: InMemorySessionPathProjectionStore, event: Mapping[str, Any], event_order: int
) -> None:
    offer = _offer_state(store, event, event_order)
    offer["impressed_at"] = event["occurred_at"]


def _apply_offer_set_choice(
    store: InMemorySessionPathProjectionStore, event: Mapping[str, Any], event_order: int
) -> None:
    payload = event["payload"]
    offer = _offer_state(store, event, event_order)
    offer.update(
        {
            "outcome": payload["outcome"],
            "thread_context_id": UUID(payload["thread_context_id"]),
            "selected_option_id": _uuid_or_none(payload["selected_option_id"]),
            "selected_option_text": payload["selected_option_text"],
            "choice_recorded_at": event["occurred_at"],
        }
    )


def _apply_node_created(
    store: InMemorySessionPathProjectionStore, event: Mapping[str, Any], event_order: int
) -> None:
    payload = event["payload"]
    _session_state(store, event)["created_path_nodes"][str(payload["node_id"])] = {
        "_order": event_order,
        "node_id": UUID(payload["node_id"]),
        "parent_node_id": UUID(payload["source_node_id"]),
        "node_type": payload["node_type"],
        "content": payload["content"],
        "creation_source": "edge_plus",
        "source_offer_set_id": UUID(payload["source_offer_set_id"]),
        "source_option_id": UUID(payload["source_option_id"]),
        "source_option_text": payload["source_option_text"],
        "thread_context_id": UUID(payload["thread_context_id"]),
        "created_at": event["occurred_at"],
    }


def _apply_edge_created(
    store: InMemorySessionPathProjectionStore, event: Mapping[str, Any], event_order: int
) -> None:
    payload = event["payload"]
    _session_state(store, event)["created_path_edges"][str(payload["edge_id"])] = {
        "_order": event_order,
        "edge_id": UUID(payload["edge_id"]),
        "source_node_id": UUID(payload["source_node_id"]),
        "target_node_id": UUID(payload["target_node_id"]),
        "edge_kind": payload["edge_kind"],
        "created_by": payload["created_by"],
        "created_at": event["occurred_at"],
    }


def _apply_edge_deleted(
    store: InMemorySessionPathProjectionStore, event: Mapping[str, Any]
) -> None:
    _session_state(store, event)["deleted_edge_ids"].add(UUID(event["payload"]["edge_id"]))


def _apply_node_deleted(
    store: InMemorySessionPathProjectionStore, event: Mapping[str, Any]
) -> None:
    payload = event["payload"]
    session = _session_state(store, event)
    session["deleted_node_ids"].update(UUID(node_id) for node_id in payload["deleted_node_ids"])
    session["deleted_edge_ids"].update(UUID(edge_id) for edge_id in payload["deleted_edge_ids"])


def _session_state(
    store: InMemorySessionPathProjectionStore, event: Mapping[str, Any]
) -> dict[str, Any]:
    session_id = str(event["session_id"])
    return store.sessions.setdefault(
        session_id,
        {
            "session_id": event["session_id"],
            "tenant_id": event["tenant_id"],
            "student_user_id": event["student_id"],
            "exam_id": None,
            "subject_id": None,
            "chapter_id": None,
            "concept_entry_id": None,
            "chapter_analysis_id": None,
            "started_at": None,
            "last_active_at": None,
            "offer_history": {},
            "created_path_nodes": {},
            "created_path_edges": {},
            "deleted_node_ids": set(),
            "deleted_edge_ids": set(),
        },
    )


def _offer_state(
    store: InMemorySessionPathProjectionStore, event: Mapping[str, Any], event_order: int
) -> dict[str, Any]:
    session = _session_state(store, event)
    offer_set_id = str(event["offer_set_id"])
    return session["offer_history"].setdefault(offer_set_id, {"_order": event_order})


def _public_row(session: Mapping[str, Any]) -> dict[str, Any]:
    created_nodes = _sorted_public_items(session["created_path_nodes"], deleted_ids=None)
    active_nodes = _sorted_public_items(
        session["created_path_nodes"], deleted_ids=session["deleted_node_ids"]
    )
    active_edges = [
        item
        for item in _sorted_public_items(
            session["created_path_edges"], deleted_ids=session["deleted_edge_ids"]
        )
        if item["edge_kind"] == "ai_path"
    ]
    offers = _sorted_public_items(session["offer_history"], deleted_ids=None)
    return {
        "session_id": session["session_id"],
        "tenant_id": session["tenant_id"],
        "student_user_id": session["student_user_id"],
        "exam_id": session["exam_id"],
        "subject_id": session["subject_id"],
        "chapter_id": session["chapter_id"],
        "concept_entry_id": session["concept_entry_id"],
        "chapter_analysis_id": session["chapter_analysis_id"],
        "started_at": session["started_at"],
        "last_active_at": session["last_active_at"],
        "offer_history": offers,
        "created_path_nodes": created_nodes,
        "active_path_nodes": active_nodes,
        "active_path_edges": active_edges,
    }


def _sorted_public_items(
    values: Mapping[str, Mapping[str, Any]], deleted_ids: set[UUID] | None
) -> list[dict[str, Any]]:
    items = []
    for value in values.values():
        identifier = value.get("node_id") or value.get("edge_id") or value.get("offer_set_id")
        if identifier is None:
            continue
        if deleted_ids is not None and identifier in deleted_ids:
            continue
        items.append({key: deepcopy(val) for key, val in value.items() if not key.startswith("_")})
    return sorted(
        items,
        key=lambda item: (
            values[str(item.get("node_id") or item.get("edge_id") or item.get("offer_set_id"))][
                "_order"
            ],
            str(item.get("node_id") or item.get("edge_id") or item.get("offer_set_id")),
        ),
    )


def _uuid_or_none(value: str | None) -> UUID | None:
    return None if value is None else UUID(value)


def _json_default(value: Any) -> str:
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)
