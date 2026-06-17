"""Student offer-choice router for selected and dismissed outcomes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Request, status

from app.domain.student.offer_choices import OfferChoiceRequest, OfferChoiceResponse


router = APIRouter(prefix="/v1/student", tags=["student"])


@router.post(
    "/offer-sets/{offer_set_id}/choices",
    response_model=OfferChoiceResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def record_offer_choice(
    offer_set_id: UUID,
    payload: OfferChoiceRequest,
    request: Request,
) -> OfferChoiceResponse:
    runtime = request.app.state.session_runtime
    return runtime.record_offer_choice(offer_set_id=offer_set_id, payload=payload)