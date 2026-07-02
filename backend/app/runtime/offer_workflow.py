"""Offer-set workflow orchestration kept out of the FastAPI composition root."""

from __future__ import annotations

from uuid import UUID

from app.domain.auth import AuthContext
from app.domain.student.offer_choices import (
    OfferChoiceContext,
    OfferChoiceRequest,
    OfferChoiceResponse,
    build_offer_set_choice,
    build_selected_child_path,
)
from app.domain.student.offer_sets import (
    EdgeOfferSetRequest,
    EdgeOfferSetResponse,
    OfferSetContext,
    PhraseOfferSetRequest,
    PhraseOfferSetResponse,
    build_edge_offer_set,
    build_phrase_offer_set,
)
from app.canvas.limits import NodeLimitExceeded, canvas_node_hard_limit
from app.events.store import InMemoryEventStore
from app.generation.provider import GenerationProvider, GeneratedNode
from app.runtime.canvas_state import count_active_nodes
from app.tenancy.pool import InMemoryTenantConnectionPool
from app.workers.queue import InMemoryJobQueue


def record_offer_choice_workflow(
    *,
    offer_set_id: UUID,
    payload: OfferChoiceRequest,
    auth: AuthContext | None,
    fallback_user_id: UUID,
    fallback_tenant_id: UUID,
    tenant_pool: InMemoryTenantConnectionPool,
    event_store: InMemoryEventStore,
    job_queue: InMemoryJobQueue,
    generation_provider: GenerationProvider | None = None,
) -> OfferChoiceResponse | None:
    resolved = auth or AuthContext(
        user_id=fallback_user_id, tenant_id=fallback_tenant_id, role="student"
    )
    with tenant_pool.transaction(resolved.tenant_id) as connection:
        session_row = connection.fetch_session_for_student(
            str(payload.session_id), resolved.user_id
        )
    if session_row is None:
        return None

    context = OfferChoiceContext(tenant_id=resolved.tenant_id, student_user_id=resolved.user_id)
    choice_event, response_model = build_offer_set_choice(
        context=context,
        offer_set_id=offer_set_id,
        request=payload,
    )
    event_count = len(event_store.events)
    try:
        stored_choice_event = event_store.append(choice_event, producer="server")
        if payload.outcome == "selected":
            active_node_count = count_active_nodes(
                event_store.events,
                session_id=payload.session_id,
                tenant_id=resolved.tenant_id,
                student_user_id=resolved.user_id,
            )
            if active_node_count >= canvas_node_hard_limit():
                raise NodeLimitExceeded(
                    "Canvas node limit reached; no new node can be created"
                )
            node_event, edge_event, child_response = build_selected_child_path(
                context=context,
                offer_set_id=offer_set_id,
                request=payload,
                choice_event=stored_choice_event,
                generated_node=_fixture_child_for_source(
                    events=event_store.events,
                    source_node_id=payload.source_node_id,
                    selected_option_text=payload.selected_option_text or "",
                    generation_provider=generation_provider,
                ),
            )
            event_store.append(node_event, producer="server")
            event_store.append(edge_event, producer="server")
            response_model = response_model.model_copy(update=child_response)
            job_queue.enqueue_classify_from_offer_choice(
                stored_choice_event,
                student_user_id=resolved.user_id,
            )
    except Exception:
        event_store.rollback_to(event_count)
        raise
    return response_model


def _fixture_child_for_source(
    *,
    events: list[dict],
    source_node_id: UUID,
    selected_option_text: str,
    generation_provider: GenerationProvider | None,
) -> GeneratedNode | None:
    if generation_provider is None:
        return None
    for event in reversed(events):
        if event.get("event_type") != "node_created":
            continue
        payload = event.get("payload")
        if not isinstance(payload, dict):
            continue
        if str(payload.get("node_id")) == str(source_node_id):
            source_key = payload.get("fixture_node_key")
            if isinstance(source_key, str):
                return generation_provider.child_for_choice(
                    source_key=source_key,
                    selected_option_text=selected_option_text,
                )
            return None
    return None


def create_edge_offer_set_workflow(
    *,
    payload: EdgeOfferSetRequest,
    auth: AuthContext | None,
    fallback_user_id: UUID,
    fallback_tenant_id: UUID,
    tenant_pool: InMemoryTenantConnectionPool,
    event_store: InMemoryEventStore,
) -> EdgeOfferSetResponse | None:
    resolved = auth or AuthContext(
        user_id=fallback_user_id, tenant_id=fallback_tenant_id, role="student"
    )
    with tenant_pool.transaction(resolved.tenant_id) as connection:
        session_row = connection.fetch_session_for_student(
            str(payload.session_id), resolved.user_id
        )
    if session_row is None:
        return None

    created_event, impression_event, response_model = build_edge_offer_set(
        context=OfferSetContext(tenant_id=resolved.tenant_id, student_user_id=resolved.user_id),
        request=payload,
    )
    event_count = len(event_store.events)
    try:
        event_store.append(created_event, producer="server")
        event_store.append(impression_event, producer="server")
    except Exception:
        event_store.rollback_to(event_count)
        raise
    return response_model


def create_phrase_offer_set_workflow(
    *,
    payload: PhraseOfferSetRequest,
    auth: AuthContext | None,
    fallback_user_id: UUID,
    fallback_tenant_id: UUID,
    tenant_pool: InMemoryTenantConnectionPool,
    event_store: InMemoryEventStore,
) -> PhraseOfferSetResponse | None:
    resolved = auth or AuthContext(
        user_id=fallback_user_id, tenant_id=fallback_tenant_id, role="student"
    )
    with tenant_pool.transaction(resolved.tenant_id) as connection:
        session_row = connection.fetch_session_for_student(
            str(payload.session_id), resolved.user_id
        )
    if session_row is None:
        return None

    phrase_event, created_event, impression_event, response_model = build_phrase_offer_set(
        context=OfferSetContext(tenant_id=resolved.tenant_id, student_user_id=resolved.user_id),
        request=payload,
    )
    event_count = len(event_store.events)
    try:
        event_store.append(phrase_event, producer="server")
        event_store.append(created_event, producer="server")
        event_store.append(impression_event, producer="server")
    except Exception:
        event_store.rollback_to(event_count)
        raise
    return response_model
