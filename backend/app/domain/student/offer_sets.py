"""Student-safe offer-set models and deterministic event construction."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal, cast
from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

from pydantic import BaseModel


class OfferSetContext(BaseModel):
    tenant_id: UUID
    student_user_id: UUID


class EdgeOfferSetRequest(BaseModel):
    session_id: UUID
    source_node_id: UUID
    thread_context_id: UUID


class PhraseOfferSetRequest(BaseModel):
    session_id: UUID
    source_node_id: UUID
    thread_context_id: UUID
    selected_phrase: str
    source_excerpt: str
    selection_start: int | None = None
    selection_end: int | None = None


class StudentOfferOption(BaseModel):
    option_id: UUID
    text: str
    rank_position: int


class PhraseOfferOption(BaseModel):
    option_id: UUID
    text: str
    rank_position: int
    action_type: Literal["elaborate", "custom", "recommended"]


class EdgeOfferSetResponse(BaseModel):
    offer_set_id: UUID
    session_id: UUID
    source_node_id: UUID
    launch_method: Literal["edge_plus"]
    options: list[StudentOfferOption]


class PhraseOfferSetResponse(BaseModel):
    offer_set_id: UUID
    session_id: UUID
    source_node_id: UUID
    thread_context_id: UUID
    launch_method: Literal["phrase_selection"]
    selected_phrase: str
    actions: list[PhraseOfferOption]
    recommended_questions: list[PhraseOfferOption]


FIXTURE_EDGE_OPTION_TEXTS = (
    "How does current change when resistance increases?",
    "Why does a bulb dim when more components share the circuit?",
    "What would happen if the circuit path is broken here?",
)

FIXTURE_PHRASE_RECOMMENDATION_TEMPLATES = (
    "Why is {phrase} important here?",
    "What changes if {phrase} is not present?",
    "How does {phrase} connect to the rest of the circuit?",
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


def build_phrase_offer_set(
    *,
    context: OfferSetContext,
    request: PhraseOfferSetRequest,
    now: datetime | None = None,
    offer_set_id: UUID | None = None,
    phrase_event_id: UUID | None = None,
    created_event_id: UUID | None = None,
    impression_event_id: UUID | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], PhraseOfferSetResponse]:
    occurred_at = now or datetime.now(timezone.utc)
    resolved_offer_set_id = offer_set_id or uuid4()
    resolved_phrase_event_id = phrase_event_id or uuid4()
    resolved_created_event_id = created_event_id or uuid4()
    resolved_impression_event_id = impression_event_id or uuid4()
    randomization_id = str(
        uuid5(NAMESPACE_URL, f"mindmap:phrase-offer-set:{resolved_offer_set_id}:randomization")
    )
    phrase = request.selected_phrase.strip()
    created_options, response_options = _build_phrase_options(
        offer_set_id=resolved_offer_set_id,
        phrase=phrase,
        randomization_id=randomization_id,
    )
    phrase_event = {
        "event_id": resolved_phrase_event_id,
        "event_type": "phrase_selected",
        "event_version": 1,
        "tenant_id": context.tenant_id,
        "actor_user_id": context.student_user_id,
        "student_id": context.student_user_id,
        "session_id": request.session_id,
        "node_id": request.source_node_id,
        "occurred_at": occurred_at,
        "payload": {
            "session_id": str(request.session_id),
            "source_node_id": str(request.source_node_id),
            "thread_context_id": str(request.thread_context_id),
            "selected_phrase": phrase,
            "source_excerpt": request.source_excerpt,
            "selection_start": request.selection_start,
            "selection_end": request.selection_end,
            "selection_surface": "reader_bottom_sheet",
        },
    }
    created_event = {
        "event_id": resolved_created_event_id,
        "event_type": "phrase_offer_set_created",
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
            "thread_context_id": str(request.thread_context_id),
            "launch_method": "phrase_selection",
            "selected_phrase": phrase,
            "source_phrase_event_id": str(resolved_phrase_event_id),
            "options": created_options,
            "policy_name": "fixture_phrase_offer_set",
            "policy_version": "v1",
            "mode": "reader_bottom_sheet",
            "gen_ms": 14,
            "rank_ms": 4,
            "total_ms": 18,
        },
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
    response = PhraseOfferSetResponse(
        offer_set_id=resolved_offer_set_id,
        session_id=request.session_id,
        source_node_id=request.source_node_id,
        thread_context_id=request.thread_context_id,
        launch_method="phrase_selection",
        selected_phrase=phrase,
        actions=response_options[:2],
        recommended_questions=response_options[2:],
    )
    return phrase_event, created_event, impression_event, response


def _build_phrase_options(
    *, offer_set_id: UUID, phrase: str, randomization_id: str
) -> tuple[list[dict[str, Any]], list[PhraseOfferOption]]:
    option_specs = [
        (f'Elaborate on "{phrase}"', "elaborate", 1, 0.34, False),
        (f'Ask a custom question about "{phrase}"', "custom", 2, 0.33, False),
    ]
    option_specs.extend(
        (template.format(phrase=phrase), "recommended", rank, propensity, rank == 4)
        for rank, (template, propensity) in enumerate(
            zip(FIXTURE_PHRASE_RECOMMENDATION_TEMPLATES, (0.14, 0.11, 0.08), strict=True),
            start=3,
        )
    )
    created_options: list[dict[str, Any]] = []
    response_options: list[PhraseOfferOption] = []
    for text, action_type, rank_position, propensity, is_probe in option_specs:
        option_id = uuid5(
            NAMESPACE_URL,
            f"mindmap:phrase-offer-set:{offer_set_id}:option:{rank_position}",
        )
        created_options.append(
            {
                "option_id": str(option_id),
                "text": text,
                "rank_position": rank_position,
                "action_type": action_type,
                "propensity": propensity,
                "is_probe": is_probe,
                "randomization_id": randomization_id,
            }
        )
        response_options.append(
            PhraseOfferOption(
                option_id=option_id,
                text=text,
                rank_position=rank_position,
                action_type=cast(Literal["elaborate", "custom", "recommended"], action_type),
            )
        )
    return created_options, response_options
