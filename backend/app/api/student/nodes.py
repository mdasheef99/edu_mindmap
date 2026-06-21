"""Student node endpoints for confirmed deletion cascade."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.domain.auth import AuthContext
from app.domain.student.deletions import DeletionConfirmationRequired, NodeDeletionResponse
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
