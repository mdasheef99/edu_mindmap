"""Membership-based JWT auth resolution (tenancy layer).

Extracted from SessionRuntime.resolve_auth so the auth concern
lives entirely in app/tenancy/ and can be swapped independently
of the runtime DI container.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

import jwt

from app.domain.auth import AuthContext, NoActiveMembershipError


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
    payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
    user_id = UUID(payload["sub"])
    records = memberships.get_memberships_for_user(user_id)
    if not records:
        raise NoActiveMembershipError("No active membership for authenticated user")
    membership = records[0]
    return AuthContext(
        user_id=user_id,
        tenant_id=membership["tenant_id"],
        role=membership["role"],
    )
