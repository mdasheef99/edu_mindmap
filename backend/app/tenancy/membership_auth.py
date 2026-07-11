"""Membership-based JWT auth resolution (tenancy layer).

Extracted from SessionRuntime.resolve_auth so the auth concern
lives entirely in app/tenancy/ and can be swapped independently
of the runtime DI container.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Any
from uuid import UUID

import jwt
from jwt import MissingRequiredClaimError

from app.domain.auth import AuthContext, NoActiveMembershipError
from app.runtime.ports import MembershipStorePort


def verify_supabase_user_id(
    token: str,
    *,
    jwt_secret: str,
    jwks_url: str | None = None,
    issuer: str | None = None,
) -> UUID:
    """Verify a Supabase JWT and return only the subject user_id."""
    header = jwt.get_unverified_header(token)
    if header.get("alg") == "ES256":
        payload = _decode_es256_supabase_jwt(
            token,
            jwks_url=jwks_url,
            issuer=issuer,
        )
        return UUID(payload["sub"])
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


def _decode_es256_supabase_jwt(
    token: str,
    *,
    jwks_url: str | None,
    issuer: str | None,
) -> dict[str, Any]:
    resolved_jwks_url = jwks_url or os.getenv("SUPABASE_JWT_JWKS_URL")
    resolved_issuer = issuer or os.getenv("SUPABASE_AUTH_URL")
    if not resolved_jwks_url:
        supabase_url = os.getenv("SUPABASE_URL")
        if supabase_url:
            resolved_issuer = resolved_issuer or f"{supabase_url.rstrip('/')}/auth/v1"
            resolved_jwks_url = f"{supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
    if not resolved_jwks_url:
        raise jwt.DecodeError("SUPABASE_JWT_JWKS_URL or SUPABASE_URL is required for ES256")

    signing_key = _cached_jwks_client(
        resolved_jwks_url,
        jwt.PyJWKClient,
    ).get_signing_key_from_jwt(token)
    decode_args: dict[str, Any] = {
        "algorithms": ["ES256"],
        "audience": "authenticated",
    }
    if resolved_issuer:
        decode_args["issuer"] = resolved_issuer
    return jwt.decode(token, signing_key.key, **decode_args)


@lru_cache(maxsize=8)
def _cached_jwks_client(jwks_url: str, client_type: type[Any]) -> Any:
    """Reuse the PyJWKClient so its signing-key cache spans authenticated requests."""
    return client_type(jwks_url)


def resolve_membership_auth(
    token: str,
    *,
    jwt_secret: str,
    memberships: MembershipStorePort,
    jwks_url: str | None = None,
    issuer: str | None = None,
) -> AuthContext:
    """Verify *token* and resolve user_id → tenant/role from *memberships*.

    Raises:
        jwt.DecodeError / jwt.ExpiredSignatureError: on bad/expired token.
        NoActiveMembershipError: if the authenticated user has no membership record.
    """
    user_id = verify_supabase_user_id(
        token,
        jwt_secret=jwt_secret,
        jwks_url=jwks_url,
        issuer=issuer,
    )
    records = memberships.get_memberships_for_user(user_id)
    if not records:
        raise NoActiveMembershipError("No active membership for authenticated user")
    membership = records[0]
    return AuthContext(
        user_id=user_id,
        tenant_id=membership["tenant_id"],
        role=membership["role"],
    )
