"""Membership-based JWT auth resolution (tenancy layer).

Extracted from SessionRuntime.resolve_auth so the auth concern
lives entirely in app/tenancy/ and can be swapped independently
of the runtime DI container.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

import jwt
from jwt import MissingRequiredClaimError

from app.domain.auth import AuthContext, NoActiveMembershipError


def verify_supabase_user_id(token: str, *, jwt_secret: str) -> UUID:
    """Verify a Supabase HS256 JWT and return only the subject user_id."""
    try:
        payload = jwt.decode(
            token, jwt_secret, algorithms=["HS256"], audience="authenticated"
        )
    except MissingRequiredClaimError as exc:
        if exc.claim != "aud":
            raise
        payload = jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
    return UUID(payload["sub"])


def resolve_membership_auth(
    token: str,
    *,
    jwt_secret: str,
    memberships: Any,  # InMemoryMembershipStore (or any duck-typed equivalent)
) -> AuthContext:
    """Verify *token* and resolve user_id → tenant/role from *memberships*.

    Raises:
        jwt.DecodeError / jwt.ExpiredSignatureError: on bad/expired token.
        NoActiveMembershipError: if the authenticated user has no membership record.
    """
    user_id = verify_supabase_user_id(token, jwt_secret=jwt_secret)
    records = memberships.get_memberships_for_user(user_id)
    if not records:
        raise NoActiveMembershipError("No active membership for authenticated user")
    membership = records[0]
    return AuthContext(
        user_id=user_id,
        tenant_id=membership["tenant_id"],
        role=membership["role"],
    )
