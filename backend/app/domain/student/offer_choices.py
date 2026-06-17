"""Student-safe offer-choice models and event construction."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, model_validator


class OfferChoiceRequest(BaseModel):
    session_id: UUID
    source_node_id: UUID
    outcome: Literal["selected", "dismissed"]
    selected_option_id: UUID | None = None
    selected_option_text: str | None = None
    thread_context_id: UUID

    @model_validator(mode="after")
    def selected_choices_carry_option(self) -> "OfferChoiceRequest":
        if self.outcome == "selected" and (
            self.selected_option_id is None or not self.selected_option_text
        ):
            raise ValueError("selected choices require selected_option_id and selected_option_text")
        return self


class OfferChoiceContext(BaseModel):
    tenant_id: UUID
    student_user_id: UUID


class OfferChoiceResponse(BaseModel):
    offer_set_id: UUID
    outcome: Literal["selected", "dismissed"]
    recorded: bool


def build_offer_set_choice(
    *,
    context: OfferChoiceContext,
    offer_set_id: UUID,
    request: OfferChoiceRequest,
    now: datetime | None = None,
    event_id: UUID | None = None,
) -> tuple[dict[str, Any], OfferChoiceResponse]:
    occurred_at = now or datetime.now(timezone.utc)
    resolved_event_id = event_id or uuid4()
    payload = {
        "offer_set_id": str(offer_set_id),
        "session_id": str(request.session_id),
        "source_node_id": str(request.source_node_id),
        "outcome": request.outcome,
        "selected_option_id": str(request.selected_option_id)
        if request.selected_option_id
        else None,
        "selected_option_text": request.selected_option_text,
        "thread_context_id": str(request.thread_context_id),
    }
    event = {
        "event_id": resolved_event_id,
        "event_type": "offer_set_choice",
        "event_version": 1,
        "tenant_id": context.tenant_id,
        "actor_user_id": context.student_user_id,
        "student_id": context.student_user_id,
        "session_id": request.session_id,
        "node_id": request.source_node_id,
        "offer_set_id": offer_set_id,
        "occurred_at": occurred_at,
        "payload": payload,
    }
    response = OfferChoiceResponse(
        offer_set_id=offer_set_id,
        outcome=request.outcome,
        recorded=True,
    )
    return event, response
