"""Student-safe edge offer-set models and deterministic event construction."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

from pydantic import BaseModel


class OfferSetContext(BaseModel):
    tenant_id: UUID
    student_user_id: UUID


class EdgeOfferSetRequest(BaseModel):
    session_id: UUID
    source_node_id: UUID
    thread_context_id: UUID


class StudentOfferOption(BaseModel):
    option_id: UUID
    text: str
    rank_position: int


class EdgeOfferSetResponse(BaseModel):
    offer_set_id: UUID
    session_id: UUID
    source_node_id: UUID
    launch_method: Literal["edge_plus"]
    options: list[StudentOfferOption]


FIXTURE_EDGE_OPTION_TEXTS = (
    "How does current change when resistance increases?",
    "Why does a bulb dim when more components share the circuit?",
    "What would happen if the circuit path is broken here?",
)


def build_edge_offer_set(
    *,
    context: OfferSetContext,
    request: EdgeOfferSetRequest,
    now: datetime | None = None,
    offer_set_id: UUID | None = None,
    created_event_id: UUID | None = None,
    impression_event_id: UUID | None = None,
) -> tuple[dict[str, Any], dict[str, Any], EdgeOfferSetResponse]:
    occurred_at = now or datetime.now(timezone.utc)
    resolved_offer_set_id = offer_set_id or uuid4()
    resolved_created_event_id = created_event_id or uuid4()
    resolved_impression_event_id = impression_event_id or uuid4()
    randomization_id = str(
        uuid5(NAMESPACE_URL, f"mindmap:edge-offer-set:{resolved_offer_set_id}:randomization")
    )
    propensities = (0.55, 0.3, 0.15)

    created_options = []
    response_options = []
    for rank_position, (text, propensity) in enumerate(
        zip(FIXTURE_EDGE_OPTION_TEXTS, propensities, strict=True),
        start=1,
    ):
        option_id = uuid5(
            NAMESPACE_URL,
            f"mindmap:edge-offer-set:{resolved_offer_set_id}:option:{rank_position}",
        )
        created_options.append(
            {
                "option_id": str(option_id),
                "text": text,
                "rank_position": rank_position,
                "propensity": propensity,
                "is_probe": rank_position == 2,
                "randomization_id": randomization_id,
            }
        )
        response_options.append(
            StudentOfferOption(
                option_id=option_id,
                text=text,
                rank_position=rank_position,
            )
        )

    created_payload = {
        "offer_set_id": str(resolved_offer_set_id),
        "session_id": str(request.session_id),
        "source_node_id": str(request.source_node_id),
        "launch_method": "edge_plus",
        "options": created_options,
        "policy_name": "fixture_edge_offer_set",
        "policy_version": "v1",
        "mode": "discovery",
        "gen_ms": 12,
        "rank_ms": 3,
        "total_ms": 15,
    }
    created_event = {
        "event_id": resolved_created_event_id,
        "event_type": "offer_set_created",
        "event_version": 1,
        "tenant_id": context.tenant_id,
        "actor_user_id": context.student_user_id,
        "student_id": context.student_user_id,
        "session_id": request.session_id,
        "node_id": request.source_node_id,
        "offer_set_id": resolved_offer_set_id,
        "occurred_at": occurred_at,
        "payload": created_payload,
    }
    impression_event = {
        "event_id": resolved_impression_event_id,
        "event_type": "offer_set_impression",
        "event_version": 1,
        "tenant_id": context.tenant_id,
        "actor_user_id": context.student_user_id,
        "student_id": context.student_user_id,
        "session_id": request.session_id,
        "node_id": request.source_node_id,
        "offer_set_id": resolved_offer_set_id,
        "occurred_at": occurred_at,
        "payload": {
            "offer_set_id": str(resolved_offer_set_id),
            "session_id": str(request.session_id),
            "source_node_id": str(request.source_node_id),
            "visible_option_ids": [option["option_id"] for option in created_options],
            "ui_positioning": [option["option_id"] for option in created_options],
        },
    }
    response = EdgeOfferSetResponse(
        offer_set_id=resolved_offer_set_id,
        session_id=request.session_id,
        source_node_id=request.source_node_id,
        launch_method="edge_plus",
        options=response_options,
    )
    return created_event, impression_event, response
