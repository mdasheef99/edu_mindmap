"""Student-safe offer-choice models and event construction."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, model_validator

from app.generation.provider import GeneratedNode


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
    child_node_id: UUID | None = None
    edge_id: UUID | None = None
    child_node_type: Literal["ai"] | None = None
    child_content: str | None = None


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


def build_selected_child_path(
    *,
    context: OfferChoiceContext,
    offer_set_id: UUID,
    request: OfferChoiceRequest,
    choice_event: dict[str, Any],
    now: datetime | None = None,
    child_node_id: UUID | None = None,
    edge_id: UUID | None = None,
    node_event_id: UUID | None = None,
    edge_event_id: UUID | None = None,
    generated_node: GeneratedNode | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    occurred_at = now or datetime.now(timezone.utc)
    resolved_child_node_id = child_node_id or uuid4()
    resolved_edge_id = edge_id or uuid4()
    child_content = (
        generated_node.node_body
        if generated_node is not None
        else f"Explore: {request.selected_option_text}"
    )

    node_payload = {
        "node_id": str(resolved_child_node_id),
        "session_id": str(request.session_id),
        "node_type": "ai",
        "content": child_content,
        "source_node_id": str(request.source_node_id),
        "source_offer_set_id": str(offer_set_id),
        "source_option_id": str(request.selected_option_id),
        "source_option_text": request.selected_option_text,
        "thread_context_id": str(request.thread_context_id),
    }
    if generated_node is not None:
        node_payload |= {
            "fixture_node_key": generated_node.node_key,
            "node_title": generated_node.node_title,
            "prompt_version": generated_node.prompt_version,
            "model_id": generated_node.model_id,
            "lineage": generated_node.lineage,
            "is_terminal": generated_node.is_terminal,
        }
    edge_payload = {
        "edge_id": str(resolved_edge_id),
        "session_id": str(request.session_id),
        "source_node_id": str(request.source_node_id),
        "target_node_id": str(resolved_child_node_id),
        "edge_kind": "ai_path",
        "created_by": "offer_set_choice",
        "source_offer_set_id": str(offer_set_id),
        "source_choice_event_id": str(choice_event["event_id"]),
        "label": generated_node.edge_label if generated_node is not None else request.selected_option_text,
    }
    node_event = {
        "event_id": node_event_id or uuid4(),
        "event_type": "node_created",
        "event_version": 1,
        "tenant_id": context.tenant_id,
        "actor_user_id": context.student_user_id,
        "student_id": context.student_user_id,
        "session_id": request.session_id,
        "node_id": resolved_child_node_id,
        "occurred_at": occurred_at,
        "payload": node_payload,
    }
    edge_event = {
        "event_id": edge_event_id or uuid4(),
        "event_type": "edge_created",
        "event_version": 1,
        "tenant_id": context.tenant_id,
        "actor_user_id": context.student_user_id,
        "student_id": context.student_user_id,
        "session_id": request.session_id,
        "node_id": request.source_node_id,
        "edge_id": resolved_edge_id,
        "occurred_at": occurred_at,
        "payload": edge_payload,
    }
    child_response = {
        "child_node_id": resolved_child_node_id,
        "edge_id": resolved_edge_id,
        "child_node_type": "ai",
        "child_content": child_content,
    }
    return node_event, edge_event, child_response
