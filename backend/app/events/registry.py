"""Phase 1 event registry.

The registry is the in-code gate before any append to the event store. It keeps event
names/version/producers explicit so unknown events and client-submitted worker events
fail before reaching the append-only `events` table.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from numbers import Real
from typing import Any, Mapping


class EventRegistryError(ValueError):
    """Base error for event registry validation failures."""


class UnknownEventTypeError(EventRegistryError):
    """Raised when an event type is not registered for Phase 1."""


class InvalidEventProducerError(EventRegistryError):
    """Raised when a producer is not allowed to append an event type."""


class InvalidEventPayloadError(EventRegistryError):
    """Raised when required event envelope fields are missing or invalid."""


@dataclass(frozen=True)
class EventTypeSpec:
    """Registered event metadata for one `(event_type, event_version)`."""

    event_type: str
    event_version: int
    allowed_producers: frozenset[str]
    required_fields: frozenset[str]
    required_payload_fields: frozenset[str] = frozenset()


COMMON_REQUIRED_FIELDS = frozenset(
    {"event_id", "event_type", "event_version", "tenant_id", "occurred_at", "payload"}
)

REGISTRY: dict[tuple[str, int], EventTypeSpec] = {
    ("session_started", 1): EventTypeSpec(
        event_type="session_started",
        event_version=1,
        allowed_producers=frozenset({"client", "server"}),
        required_fields=COMMON_REQUIRED_FIELDS
        | frozenset(
            {
                "actor_user_id",
                "student_id",
                "session_id",
                "exam_id",
                "subject_id",
                "chapter_id",
                "chapter_analysis_id",
                "concept_entry_id",
            }
        ),
        required_payload_fields=frozenset(
            {
                "session_id",
                "student_user_id",
                "exam_id",
                "subject_id",
                "chapter_id",
                "chapter_analysis_id",
                "concept_entry_id",
            }
        ),
    ),
    ("session_resumed", 1): EventTypeSpec(
        event_type="session_resumed",
        event_version=1,
        allowed_producers=frozenset({"client", "server"}),
        required_fields=COMMON_REQUIRED_FIELDS
        | frozenset({"actor_user_id", "student_id", "session_id"}),
        required_payload_fields=frozenset({"session_id", "student_user_id"}),
    ),
    ("node_created", 1): EventTypeSpec(
        event_type="node_created",
        event_version=1,
        allowed_producers=frozenset({"client", "server"}),
        required_fields=COMMON_REQUIRED_FIELDS
        | frozenset({"actor_user_id", "student_id", "session_id", "node_id"}),
        required_payload_fields=frozenset(
            {
                "node_id",
                "session_id",
                "node_type",
                "content",
                "source_node_id",
                "source_offer_set_id",
                "source_option_id",
                "source_option_text",
                "thread_context_id",
            }
        ),
    ),
    ("edge_created", 1): EventTypeSpec(
        event_type="edge_created",
        event_version=1,
        allowed_producers=frozenset({"client", "server"}),
        required_fields=COMMON_REQUIRED_FIELDS
        | frozenset({"actor_user_id", "student_id", "session_id", "node_id", "edge_id"}),
        required_payload_fields=frozenset(
            {
                "edge_id",
                "session_id",
                "source_node_id",
                "target_node_id",
                "edge_kind",
                "created_by",
            }
        ),
    ),
    ("edge_deleted", 1): EventTypeSpec(
        event_type="edge_deleted",
        event_version=1,
        allowed_producers=frozenset({"client", "server"}),
        required_fields=COMMON_REQUIRED_FIELDS
        | frozenset({"actor_user_id", "student_id", "session_id", "node_id", "edge_id"}),
        required_payload_fields=frozenset(
            {
                "edge_id",
                "session_id",
                "edge_kind",
                "deletion_cause",
            }
        ),
    ),
    ("node_deleted", 1): EventTypeSpec(
        event_type="node_deleted",
        event_version=1,
        allowed_producers=frozenset({"client", "server"}),
        required_fields=COMMON_REQUIRED_FIELDS
        | frozenset({"actor_user_id", "student_id", "session_id", "node_id"}),
        required_payload_fields=frozenset(
            {
                "root_node_id",
                "session_id",
                "deleted_node_ids",
                "deleted_edge_ids",
                "confirmed",
                "deletion_cause",
            }
        ),
    ),
    ("offer_set_created", 1): EventTypeSpec(
        event_type="offer_set_created",
        event_version=1,
        allowed_producers=frozenset({"client", "server"}),
        required_fields=COMMON_REQUIRED_FIELDS
        | frozenset({"actor_user_id", "student_id", "session_id", "node_id", "offer_set_id"}),
        required_payload_fields=frozenset(
            {
                "offer_set_id",
                "session_id",
                "source_node_id",
                "launch_method",
                "options",
                "policy_name",
                "policy_version",
                "mode",
                "gen_ms",
                "rank_ms",
                "total_ms",
            }
        ),
    ),
    ("phrase_selected", 1): EventTypeSpec(
        event_type="phrase_selected",
        event_version=1,
        allowed_producers=frozenset({"server"}),
        required_fields=COMMON_REQUIRED_FIELDS
        | frozenset({"actor_user_id", "student_id", "session_id", "node_id"}),
        required_payload_fields=frozenset(
            {
                "session_id",
                "source_node_id",
                "thread_context_id",
                "selected_phrase",
                "source_excerpt",
                "selection_surface",
            }
        ),
    ),
    ("phrase_offer_set_created", 1): EventTypeSpec(
        event_type="phrase_offer_set_created",
        event_version=1,
        allowed_producers=frozenset({"server"}),
        required_fields=COMMON_REQUIRED_FIELDS
        | frozenset({"actor_user_id", "student_id", "session_id", "node_id", "offer_set_id"}),
        required_payload_fields=frozenset(
            {
                "offer_set_id",
                "session_id",
                "source_node_id",
                "thread_context_id",
                "launch_method",
                "selected_phrase",
                "source_phrase_event_id",
                "options",
                "policy_name",
                "policy_version",
                "mode",
                "gen_ms",
                "rank_ms",
                "total_ms",
            }
        ),
    ),
    ("offer_set_impression", 1): EventTypeSpec(
        event_type="offer_set_impression",
        event_version=1,
        allowed_producers=frozenset({"client", "server"}),
        required_fields=COMMON_REQUIRED_FIELDS
        | frozenset({"actor_user_id", "student_id", "session_id", "node_id", "offer_set_id"}),
        required_payload_fields=frozenset(
            {
                "offer_set_id",
                "session_id",
                "source_node_id",
                "visible_option_ids",
                "ui_positioning",
            }
        ),
    ),
    ("offer_set_choice", 1): EventTypeSpec(
        event_type="offer_set_choice",
        event_version=1,
        allowed_producers=frozenset({"client", "server"}),
        required_fields=COMMON_REQUIRED_FIELDS
        | frozenset({"actor_user_id", "student_id", "session_id", "node_id", "offer_set_id"}),
        required_payload_fields=frozenset(
            {
                "offer_set_id",
                "session_id",
                "source_node_id",
                "outcome",
                "thread_context_id",
            }
        ),
    ),
    ("question_classified", 1): EventTypeSpec(
        event_type="question_classified",
        event_version=1,
        allowed_producers=frozenset({"worker"}),
        required_fields=COMMON_REQUIRED_FIELDS
        | frozenset(
            {
                "student_id",
                "session_id",
                "chapter_id",
                "chapter_analysis_id",
                "offer_set_id",
                "prompt_version",
                "model_id",
                "projection_version",
            }
        ),
        required_payload_fields=frozenset(
            {
                "source_event_id",
                "source_event_type",
                "source_event_recorded_at_max",
                "offer_set_id",
                "session_id",
                "selected_option_text",
                "scores_payload",
                "entropy_payload",
                "dispersion_payload",
            }
        ),
    ),
    ("node_visited", 1): EventTypeSpec(
        event_type="node_visited",
        event_version=1,
        allowed_producers=frozenset({"client"}),
        required_fields=COMMON_REQUIRED_FIELDS
        | frozenset({"actor_user_id", "student_id", "session_id", "node_id"}),
        required_payload_fields=frozenset(
            {
                "node_id",
                "session_id",
                "visit_source",
            }
        ),
    ),
    ("viewport_changed", 1): EventTypeSpec(
        event_type="viewport_changed",
        event_version=1,
        allowed_producers=frozenset({"client"}),
        required_fields=COMMON_REQUIRED_FIELDS
        | frozenset({"actor_user_id", "student_id", "session_id"}),
        required_payload_fields=frozenset(
            {
                "session_id",
                "scale",
                "translate_x",
                "translate_y",
                "visible_node_ids",
            }
        ),
    ),
    ("node_position_updated", 1): EventTypeSpec(
        event_type="node_position_updated",
        event_version=1,
        allowed_producers=frozenset({"client"}),
        required_fields=COMMON_REQUIRED_FIELDS
        | frozenset({"actor_user_id", "student_id", "session_id", "node_id"}),
        required_payload_fields=frozenset(
            {
                "node_id",
                "session_id",
                "position_x",
                "position_y",
            }
        ),
    ),
    ("consent_recorded", 1): EventTypeSpec(
        event_type="consent_recorded",
        event_version=1,
        allowed_producers=frozenset({"server", "admin", "internal"}),
        required_fields=COMMON_REQUIRED_FIELDS,
    ),
}


def get_event_spec(event_type: str, event_version: int) -> EventTypeSpec:
    """Return the registered event spec or raise for unknown event types."""
    try:
        return REGISTRY[(event_type, event_version)]
    except KeyError as exc:
        raise UnknownEventTypeError(
            f"Unknown event type/version: {event_type!r} v{event_version!r}"
        ) from exc


def validate_event(event: Mapping[str, Any], *, producer: str) -> Mapping[str, Any]:
    """Validate an event envelope against the Phase 1 registry.

    Full payload schemas will be tightened as each Phase 1 endpoint/worker test is
    opened; this first registry slice enforces the non-negotiable event envelope,
    known type/version registration, and producer restrictions.
    """
    event_type = event.get("event_type")
    event_version = event.get("event_version")
    if not isinstance(event_type, str) or not isinstance(event_version, int):
        raise InvalidEventPayloadError("event_type and integer event_version are required")

    spec = get_event_spec(event_type, event_version)

    if producer not in spec.allowed_producers:
        raise InvalidEventProducerError(
            f"Producer {producer!r} cannot append {event_type!r} v{event_version}"
        )

    missing_fields = sorted(field for field in spec.required_fields if event.get(field) is None)
    if missing_fields:
        raise InvalidEventPayloadError(f"Missing required event fields: {missing_fields}")

    payload = event.get("payload")
    if not isinstance(payload, Mapping):
        raise InvalidEventPayloadError("payload must be a mapping")

    missing_payload_fields = sorted(
        field for field in spec.required_payload_fields if payload.get(field) is None
    )
    if missing_payload_fields:
        raise InvalidEventPayloadError(f"Missing required payload fields: {missing_payload_fields}")

    if event_type == "node_position_updated":
        for field in ("position_x", "position_y"):
            value = payload[field]
            if isinstance(value, bool) or not isinstance(value, Real) or not isfinite(float(value)):
                raise InvalidEventPayloadError(f"{field} must be a finite number")

    return event
