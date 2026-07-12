"""Student node endpoints for confirmed deletion cascade and position persistence."""

from __future__ import annotations

from math import isfinite
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.domain.auth import AuthContext
from app.domain.student.deletions import DeletionConfirmationRequired, NodeDeletionResponse
from app.domain.student.nodes import NodePositionResponse, NodePositionUpdate
from app.tenancy.auth import get_auth_context

router = APIRouter(prefix="/v1/student", tags=["student"])


@router.delete(
    "/sessions/{session_id}/nodes/{node_id}",
    response_model=NodeDeletionResponse,
)
def delete_node(
    session_id: UUID,
    node_id: UUID,
    request: Request,
    confirmed: bool = False,
    auth: AuthContext = Depends(get_auth_context),
) -> NodeDeletionResponse:
    runtime = request.app.state.session_runtime
    try:
        deletion = runtime.delete_student_node(
            session_id=session_id,
            node_id=node_id,
            confirmed=confirmed,
            auth=auth,
        )
    except DeletionConfirmationRequired as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Deletion requires confirmed=true",
        ) from exc
    if deletion is None:
        raise HTTPException(status_code=404, detail="Node not found")
    return deletion


@router.patch(
    "/sessions/{session_id}/nodes/{node_id}",
    response_model=NodePositionResponse,
)
def update_node_position(
    session_id: UUID,
    node_id: UUID,
    payload: NodePositionUpdate,
    request: Request,
    auth: AuthContext = Depends(get_auth_context),
) -> NodePositionResponse:
    if not (isfinite(payload.position_x) and isfinite(payload.position_y)):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="position_x and position_y must be finite numbers",
        )
    runtime = request.app.state.session_runtime
    updated = runtime.update_node_position(
        session_id=session_id,
        node_id=node_id,
        payload=payload,
        auth=auth,
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="Node not found")
    return updated
