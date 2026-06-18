"""Student edge offer-set router for deterministic logging slice."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.domain.auth import AuthContext
from app.domain.student.offer_sets import EdgeOfferSetRequest, EdgeOfferSetResponse
from app.tenancy.auth import get_auth_context

router = APIRouter(prefix="/v1/student", tags=["student"])


@router.post(
    "/offer-sets/edge",
    response_model=EdgeOfferSetResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_edge_offer_set(
    payload: EdgeOfferSetRequest,
    request: Request,
    auth: AuthContext = Depends(get_auth_context),
) -> EdgeOfferSetResponse:
    runtime = request.app.state.session_runtime
    offer_set = runtime.create_edge_offer_set(payload=payload, auth=auth)
    if offer_set is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return offer_set
