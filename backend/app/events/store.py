"""In-memory event append boundary for the Phase 1 walking skeleton."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from app.events.registry import validate_event


class InMemoryEventStore:
    """Small testable append-only store used by the first vertical slice."""

    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    def append(self, event: Mapping[str, Any], *, producer: str) -> dict[str, Any]:
        validate_event(event, producer=producer)
        stored_event = deepcopy(dict(event))
        stored_event["producer"] = producer
        self.events.append(stored_event)
        return stored_event

    def rollback_to(self, event_count: int) -> None:
        del self.events[event_count:]