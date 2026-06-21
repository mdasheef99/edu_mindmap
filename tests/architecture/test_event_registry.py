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
