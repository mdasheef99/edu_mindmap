"""FastAPI dependency for Supabase Auth JWT verification + tenant resolution."""

from __future__ import annotations

from fastapi import Header, HTTPException, Request

from app.domain.auth import AuthContext, NoActiveMembershipError


def get_auth_context(
    request: Request,
    authorization: str | None = Header(None),
) -> AuthContext:
    """Verify JWT and resolve user_id → tenant/role from in-memory memberships."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization[7:]
    runtime = request.app.state.session_runtime

    try:
        return runtime.resolve_auth(token)
    except NoActiveMembershipError as exc:
        raise HTTPException(
            status_code=403,
            detail="No active membership for authenticated user",
        ) from exc
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc
