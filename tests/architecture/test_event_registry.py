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
