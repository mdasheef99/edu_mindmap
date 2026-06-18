"""Student offer-choice router for selected and dismissed outcomes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.domain.auth import AuthContext
from app.domain.student.offer_choices import OfferChoiceRequest, OfferChoiceResponse
from app.tenancy.auth import get_auth_context

router = APIRouter(prefix="/v1/student", tags=["student"])


@router.post(
    "/offer-sets/{offer_set_id}/choices",
    response_model=OfferChoiceResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_202_ACCEPTED,
)
def record_offer_choice(
    offer_set_id: UUID,
    payload: OfferChoiceRequest,
    request: Request,
    auth: AuthContext = Depends(get_auth_context),
) -> OfferChoiceResponse:
    runtime = request.app.state.session_runtime
    choice = runtime.record_offer_choice(offer_set_id=offer_set_id, payload=payload, auth=auth)
    if choice is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return choice
