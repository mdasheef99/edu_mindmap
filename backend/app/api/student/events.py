"""Student client-event ingest router (M3-C Seam A).

POST /v1/student/sessions/{session_id}/events — batch ingest of whitelisted
client events. Tenant/student/session scope is backend-resolved (mobile-supplied
values are never authoritative; canon Tenant Isolation invariant). Each event is
validated against the in-code registry and boundary rules, then appended with
producer="client" (canon Event Sourcing invariant).

Import-linter: this module imports only app.domain.student, app.events, app.canvas,
and app.tenancy — zero analytic imports (Category Invisibility).

Traceability:
- docs/planning/sdd/phase-3-m3c-infrastructure-remediation-sdd.md §4
- docs/api/student-api-spec.md §5 (POST /events whitelist)
- docs/planning/session-path-data-contract.md §8 (interaction event contract)
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from app.canvas.limits import canvas_max_zoom, canvas_min_zoom
from app.domain.auth import AuthContext
from app.events.registry import EventRegistryError, InvalidEventProducerError, validate_event
from app.tenancy.auth import get_auth_context

router = APIRouter(prefix="/v1/student", tags=["student"])

CLIENT_EVENT_WHITELIST = frozenset({"node_visited", "viewport_changed"})
VISIT_SOURCES = frozenset({"tap", "edge_plus", "session_resume"})
MAX_BATCH_SIZE = 20


class EventBatchRequest(BaseModel):
    events: list[dict[str, Any]]


@router.post("/sessions/{session_id}/events", status_code=status.HTTP_202_ACCEPTED)
def ingest_events(
    session_id: UUID,
    payload: EventBatchRequest,
    request: Request,
    auth: AuthContext = Depends(get_auth_context),
) -> dict[str, Any]:
    events = payload.events
    if not events or len(events) > MAX_BATCH_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"events batch must contain 1..{MAX_BATCH_SIZE} events",
        )

    runtime = request.app.state.session_runtime
    accepted = 0
    rejected: list[dict[str, Any]] = []
    first_failure_status: int | None = None
    first_failure_reason: str | None = None

    for index, event in enumerate(events):
        _apply_backend_scope(event, auth=auth, session_id=session_id)
        ok, reason, http_status = _classify(event)
        if ok:
            runtime.event_store.append(event, producer="client")
            accepted += 1
        else:
            rejected.append({"index": index, "reason": reason})
            if first_failure_status is None:
                first_failure_status = http_status
                first_failure_reason = reason

    if accepted == 0:
        raise HTTPException(
            status_code=first_failure_status or status.HTTP_400_BAD_REQUEST,
            detail=first_failure_reason or "no events accepted",
        )

    return {"accepted": accepted, "rejected": rejected}


def _apply_backend_scope(event: dict[str, Any], *, auth: AuthContext, session_id: UUID) -> None:
    """Overwrite scope fields with backend-resolved identity (never trust the client)."""
    event["tenant_id"] = auth.tenant_id
    event["actor_user_id"] = auth.user_id
    event["student_id"] = auth.user_id
    event["session_id"] = session_id
    payload = event.get("payload")
    if isinstance(payload, dict):
        payload["session_id"] = str(session_id)

def _classify(event: dict[str, Any]) -> tuple[bool, str | None, int | None]:
    try:
        validate_event(event, producer="client")
    except InvalidEventProducerError as exc:
        return False, str(exc), status.HTTP_403_FORBIDDEN
    except EventRegistryError as exc:
        return False, str(exc), status.HTTP_400_BAD_REQUEST

    event_type = event.get("event_type")
    if event_type not in CLIENT_EVENT_WHITELIST:
        return (
            False,
            f"event_type {event_type!r} is not accepted via this endpoint",
            status.HTTP_400_BAD_REQUEST,
        )

    payload = event["payload"]
    if event_type == "node_visited":
        if payload.get("visit_source") not in VISIT_SOURCES:
            return False, "visit_source is not an allowed value", status.HTTP_400_BAD_REQUEST
    elif event_type == "viewport_changed":
        scale = payload.get("scale")
        if isinstance(scale, bool) or not isinstance(scale, (int, float)):
            return False, "scale must be numeric", status.HTTP_400_BAD_REQUEST
        if not canvas_min_zoom() <= float(scale) <= canvas_max_zoom():
            return False, "scale outside [CANVAS_MIN_ZOOM, CANVAS_MAX_ZOOM]", status.HTTP_400_BAD_REQUEST
        if not isinstance(payload.get("visible_node_ids"), list):
            return False, "visible_node_ids must be a list", status.HTTP_400_BAD_REQUEST

    return True, None, None
