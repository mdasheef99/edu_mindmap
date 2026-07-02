"""Student B2C auth bootstrap routes for M4."""

from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, Request
from jwt import PyJWTError

from app.domain.student.auth import StudentAuthBootstrapResponse

router = APIRouter(prefix="/v1/student/auth", tags=["student"])


@router.post("/bootstrap", response_model=StudentAuthBootstrapResponse)
def bootstrap_student_membership(
    request: Request,
    authorization: str | None = Header(None),
) -> StudentAuthBootstrapResponse:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization[7:]
    runtime = request.app.state.session_runtime
    try:
        auth = runtime.bootstrap_b2c_student_membership(token)
    except (PyJWTError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Invalid Supabase token") from exc
    return StudentAuthBootstrapResponse(
        user_id=auth.user_id,
        tenant_id=auth.tenant_id,
        role=auth.role,
    )
