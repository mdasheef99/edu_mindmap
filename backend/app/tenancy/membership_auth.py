"""JWT verification and backend-owned membership resolution."""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Callable
from uuid import UUID

import jwt

from app.domain.auth import AuthContext, NoActiveMembershipError
from app.runtime.ports import MembershipStorePort

UserIdVerifier = Callable[[str], UUID]
SUPABASE_JWT_CLOCK_SKEW_SECONDS = 30


def build_supabase_es256_verifier(*, jwks_url: str, issuer: str) -> UserIdVerifier:
    """Build the live verifier; only ES256 Supabase access tokens are accepted."""

    if not jwks_url.strip() or not issuer.strip():
        raise ValueError("Supabase issuer and JWKS URL are required")

    def verify(token: str) -> UUID:
        header = jwt.get_unverified_header(token)
        if header.get("alg") != "ES256":
            raise jwt.InvalidAlgorithmError("Production Supabase tokens must use ES256")
        signing_key = _cached_jwks_client(jwks_url, jwt.PyJWKClient).get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            audience="authenticated",
            issuer=issuer,
            leeway=SUPABASE_JWT_CLOCK_SKEW_SECONDS,
        )
        return UUID(payload["sub"])

    return verify


def build_hs256_fixture_verifier(jwt_secret: str) -> UserIdVerifier:
    """Build the deterministic HS256 verifier used only by explicit test runtimes."""

    if not jwt_secret:
        raise ValueError("Fixture JWT secret is required")

    def verify(token: str) -> UUID:
        payload = jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
        return UUID(payload["sub"])

    return verify


@lru_cache(maxsize=8)
def _cached_jwks_client(jwks_url: str, client_type: type[Any]) -> Any:
    """Reuse the PyJWKClient so its signing-key cache spans authenticated requests."""

    return client_type(jwks_url)


def resolve_membership_auth(
    token: str,
    *,
    verify_user_id: UserIdVerifier,
    memberships: MembershipStorePort,
) -> AuthContext:
    """Verify identity and resolve tenant/role from backend-owned memberships."""

    user_id = verify_user_id(token)
    records = memberships.get_memberships_for_user(user_id)
    if not records:
        raise NoActiveMembershipError("No active membership for authenticated user")
    membership = records[0]
    return AuthContext(
        user_id=user_id,
        tenant_id=membership["tenant_id"],
        role=membership["role"],
    )
