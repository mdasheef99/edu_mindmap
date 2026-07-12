from datetime import datetime, timezone
from uuid import uuid4

import pytest


def test_event_registry_rejects_unknown_event_type() -> None:
    """T1: unknown event types must be rejected before append."""
    from app.events.registry import UnknownEventTypeError, validate_event

    unknown_event = {
        "event_id": uuid4(),
        "event_type": "unknown_event_type",
        "event_version": 1,
        "tenant_id": uuid4(),
        "occurred_at": datetime.now(timezone.utc),
        "payload": {},
    }

    with pytest.raises(UnknownEventTypeError):
        validate_event(unknown_event, producer="client")


def _valid_node_created_event():
    return {
        "event_id": uuid4(),
        "event_type": "node_created",
        "event_version": 1,
        "tenant_id": uuid4(),
        "actor_user_id": uuid4(),
        "student_id": uuid4(),
        "session_id": uuid4(),
        "node_id": uuid4(),
        "occurred_at": datetime.now(timezone.utc),
        "payload": {
            "node_id": str(uuid4()),
            "session_id": str(uuid4()),
            "node_type": "ai",
            "content": "Explore: test",
            "source_node_id": str(uuid4()),
            "source_offer_set_id": str(uuid4()),
            "source_option_id": str(uuid4()),
            "source_option_text": "test",
            "thread_context_id": str(uuid4()),
        },
    }


def test_event_registry_requires_node_created_source_fields() -> None:
    """node_created projection depends on source_node_id and source_option_text."""
    from app.events.registry import InvalidEventPayloadError, validate_event

    event = _valid_node_created_event()
    assert validate_event(event, producer="server") is event

    for omitted in ("source_node_id", "source_option_text"):
        missing = _valid_node_created_event()
        missing["payload"] = {k: v for k, v in missing["payload"].items() if k != omitted}
        with pytest.raises(InvalidEventPayloadError, match=omitted):
            validate_event(missing, producer="server")


# --- M3 §12 T5 — canvas event registry (node_visited v1, viewport_changed v1) -------------
#
# Traceability: phase-3-m3-canvas-sdd.md §10, §12 T5; backend-architecture.md §5.3.
# node_visited powers the ordered-path-of-node-visits contract (framework-design-philosophy.md §1);
# events_node_id_idx (migration 0006) is backed by the node_id envelope column.
#
# SDD-wording note: §12 names InvalidEventPayloadError for the wrong-producer cases, but the
# registry's typed producer-restriction contract raises InvalidEventProducerError (a sibling of
# InvalidEventPayloadError under EventRegistryError). The correct existing API is asserted here.


def _valid_node_visited_event():
    return {
        "event_id": uuid4(),
        "event_type": "node_visited",
        "event_version": 1,
        "tenant_id": uuid4(),
        "actor_user_id": uuid4(),
        "student_id": uuid4(),
        "session_id": uuid4(),
        "node_id": uuid4(),
        "occurred_at": datetime.now(timezone.utc),
        "payload": {
            "node_id": str(uuid4()),
            "session_id": str(uuid4()),
            "visit_source": "tap",
        },
    }


def _valid_viewport_changed_event():
    return {
        "event_id": uuid4(),
        "event_type": "viewport_changed",
        "event_version": 1,
        "tenant_id": uuid4(),
        "actor_user_id": uuid4(),
        "student_id": uuid4(),
        "session_id": uuid4(),
        "occurred_at": datetime.now(timezone.utc),
        "payload": {
            "session_id": str(uuid4()),
            "scale": 1.25,
            "translate_x": -42.5,
            "translate_y": 318.0,
            "visible_node_ids": [str(uuid4()), str(uuid4())],
        },
    }


def test_node_visited_v1_valid() -> None:
    from app.events.registry import validate_event

    event = _valid_node_visited_event()
    assert validate_event(event, producer="client") is event


def test_node_visited_missing_visit_source() -> None:
    from app.events.registry import InvalidEventPayloadError, validate_event

    event = _valid_node_visited_event()
    event["payload"] = {k: v for k, v in event["payload"].items() if k != "visit_source"}
    with pytest.raises(InvalidEventPayloadError, match="visit_source"):
        validate_event(event, producer="client")


def test_node_visited_client_only() -> None:
    from app.events.registry import InvalidEventProducerError, validate_event

    event = _valid_node_visited_event()
    with pytest.raises(InvalidEventProducerError):
        validate_event(event, producer="worker")


def test_viewport_changed_v1_valid() -> None:
    from app.events.registry import validate_event

    event = _valid_viewport_changed_event()
    assert validate_event(event, producer="client") is event


def test_viewport_changed_missing_visible_node_ids() -> None:
    from app.events.registry import InvalidEventPayloadError, validate_event

    event = _valid_viewport_changed_event()
    event["payload"] = {k: v for k, v in event["payload"].items() if k != "visible_node_ids"}
    with pytest.raises(InvalidEventPayloadError, match="visible_node_ids"):
        validate_event(event, producer="client")


def test_viewport_changed_worker_rejected() -> None:
    from app.events.registry import InvalidEventProducerError, validate_event

    event = _valid_viewport_changed_event()
    with pytest.raises(InvalidEventProducerError):
        validate_event(event, producer="worker")
