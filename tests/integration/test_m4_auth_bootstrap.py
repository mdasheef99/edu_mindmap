"""M4 auth + B2C bootstrap tests.

Traceability:
- docs/planning/sdd/phase-3-m4-curriculum-auth-sdd.md §§6.2-6.3, 12.1
- docs/architecture/adr-log-02.md ADR-0015
- docs/architecture/backend-architecture.md §§5.4-5.5, 11
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi.testclient import TestClient


def _make_jwt(user_id: str, secret: str, **claims: str) -> str:
    return jwt.encode({"sub": user_id, **claims}, secret, algorithm="HS256")


def _build_client_and_runtime(*, jwt_secret: str = "test-secret"):
    from app.main import SessionRuntime, create_app

    runtime = SessionRuntime.for_testing(
        tenant_id=uuid4(),
        student_user_id=uuid4(),
        jwt_secret=jwt_secret,
    )
    return TestClient(create_app(runtime=runtime)), runtime


def test_valid_jwt_with_existing_membership_resolves_server_tenant_and_role():
    """BA-1: existing membership resolves backend-owned tenant/role."""
    jwt_secret = "test-secret"
    jwt_user = uuid4()
    resolved_tenant = uuid4()
    _, runtime = _build_client_and_runtime(jwt_secret=jwt_secret)
    runtime.memberships.add_membership(
        user_id=jwt_user,
        tenant_id=resolved_tenant,
        role="student",
    )

    auth = runtime.resolve_auth(_make_jwt(str(jwt_user), jwt_secret))

    assert auth.user_id == jwt_user
    assert auth.tenant_id == resolved_tenant
    assert auth.role == "student"


def test_bootstrap_ignores_mobile_supplied_tenant_id():
    """BA-2/BA-3: bootstrap uses configured individual tenant, never mobile tenant."""
    jwt_secret = "test-secret"
    jwt_user = uuid4()
    attacker_tenant = uuid4()
    _, runtime = _build_client_and_runtime(jwt_secret=jwt_secret)
    token = _make_jwt(str(jwt_user), jwt_secret, tenant_id=str(attacker_tenant))

    auth = runtime.bootstrap_b2c_student_membership(token)

    assert auth.user_id == jwt_user
    assert auth.tenant_id == runtime.tenant_id
    assert auth.tenant_id != attacker_tenant
    assert auth.role == "student"


def test_bootstrap_creates_one_student_membership_idempotently():
    """BA-3: first-run B2C bootstrap creates exactly one student membership."""
    jwt_secret = "test-secret"
    jwt_user = uuid4()
    _, runtime = _build_client_and_runtime(jwt_secret=jwt_secret)
    token = _make_jwt(str(jwt_user), jwt_secret)

    first_auth = runtime.bootstrap_b2c_student_membership(token)
    second_auth = runtime.bootstrap_b2c_student_membership(token)

    records = runtime.memberships.get_memberships_for_user(jwt_user)
    assert first_auth == second_auth
    assert records == [{"user_id": jwt_user, "tenant_id": runtime.tenant_id, "role": "student"}]


def test_http_bootstrap_enables_student_api_access():
    """BA-6: B2C bootstrap endpoint makes signed-in student endpoints usable."""
    jwt_secret = "test-secret"
    jwt_user = uuid4()
    client, _ = _build_client_and_runtime(jwt_secret=jwt_secret)
    token = _make_jwt(str(jwt_user), jwt_secret)

    bootstrap = client.post(
        "/v1/student/auth/bootstrap",
        headers={"Authorization": f"Bearer {token}"},
    )
    recent = client.get(
        "/v1/student/sessions/recent",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert bootstrap.status_code == 200
    assert bootstrap.json()["role"] == "student"
    assert recent.status_code == 200


def test_http_bootstrap_accepts_supabase_es256_jwks_token(monkeypatch):
    """ADR-0017: live Supabase ES256/JWKS tokens can bootstrap M4 membership."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()
    jwt_user = uuid4()
    client, runtime = _build_client_and_runtime(jwt_secret="unused-for-es256")
    token = jwt.encode(
        {
            "iss": "https://issuer.example.test/auth/v1",
            "sub": str(jwt_user),
            "aud": "authenticated",
            "role": "authenticated",
        },
        private_key,
        algorithm="ES256",
        headers={"kid": "test-key"},
    )

    class _SigningKey:
        key = public_key

    class _FakeJwksClient:
        def __init__(self, url: str) -> None:
            self.url = url

        def get_signing_key_from_jwt(self, received_token: str):
            assert received_token == token
            return _SigningKey()

    monkeypatch.setattr(jwt, "PyJWKClient", _FakeJwksClient)
    from app.tenancy.membership_auth import build_supabase_es256_verifier

    runtime.verify_user_id = build_supabase_es256_verifier(
        jwks_url="https://keys.example.test/jwks.json",
        issuer="https://issuer.example.test/auth/v1",
    )

    bootstrap = client.post(
        "/v1/student/auth/bootstrap",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert bootstrap.status_code == 200
    assert bootstrap.json()["user_id"] == str(jwt_user)
    assert bootstrap.json()["role"] == "student"


def test_es256_jwks_client_is_reused_across_authenticated_requests(monkeypatch):
    """ADR-0017: repeated M4 requests reuse one key-caching JWKS client."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()
    jwt_user = uuid4()
    client, runtime = _build_client_and_runtime(jwt_secret="unused-for-es256")
    issuer = "https://issuer.example.test/auth/v1"
    jwks_url = f"{issuer}/.well-known/cache-test-jwks.json"
    token = jwt.encode(
        {"iss": issuer, "sub": str(jwt_user), "aud": "authenticated"},
        private_key,
        algorithm="ES256",
        headers={"kid": "cache-test-key"},
    )
    created_clients: list[str] = []

    class _SigningKey:
        key = public_key

    class _FakeJwksClient:
        def __init__(self, url: str) -> None:
            created_clients.append(url)

        def get_signing_key_from_jwt(self, received_token: str):
            assert received_token == token
            return _SigningKey()

    monkeypatch.setattr(jwt, "PyJWKClient", _FakeJwksClient)
    from app.tenancy.membership_auth import build_supabase_es256_verifier

    runtime.verify_user_id = build_supabase_es256_verifier(
        jwks_url=jwks_url,
        issuer=issuer,
    )

    first = client.post(
        "/v1/student/auth/bootstrap",
        headers={"Authorization": f"Bearer {token}"},
    )
    second = client.post(
        "/v1/student/auth/bootstrap",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert created_clients == [jwks_url]


def test_es256_accepts_small_clock_skew_but_rejects_far_future_iat(monkeypatch):
    """ADR-0017: tolerate 30s clock skew without accepting far-future tokens."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()
    issuer = "https://issuer.example.test/auth/v1"
    client, runtime = _build_client_and_runtime(jwt_secret="unused-for-es256")
    jwks_url = f"{issuer}/.well-known/leeway-test-jwks.json"

    class _SigningKey:
        key = public_key

    class _FakeJwksClient:
        def __init__(self, _url: str) -> None:
            pass

        def get_signing_key_from_jwt(self, _received_token: str):
            return _SigningKey()

    monkeypatch.setattr(jwt, "PyJWKClient", _FakeJwksClient)
    from app.tenancy.membership_auth import build_supabase_es256_verifier

    runtime.verify_user_id = build_supabase_es256_verifier(
        jwks_url=jwks_url,
        issuer=issuer,
    )

    def token_with_iat(seconds_ahead: int) -> str:
        return jwt.encode(
            {
                "iss": issuer,
                "sub": str(uuid4()),
                "aud": "authenticated",
                "iat": datetime.now(timezone.utc) + timedelta(seconds=seconds_ahead),
            },
            private_key,
            algorithm="ES256",
            headers={"kid": "leeway-test-key"},
        )

    within_tolerance = client.post(
        "/v1/student/auth/bootstrap",
        headers={"Authorization": f"Bearer {token_with_iat(20)}"},
    )
    outside_tolerance = client.post(
        "/v1/student/auth/bootstrap",
        headers={"Authorization": f"Bearer {token_with_iat(120)}"},
    )

    assert within_tolerance.status_code == 200
    assert outside_tolerance.status_code == 401


def test_bootstrap_reports_existing_behavioral_analytics_consent():
    """R3: a durable grant suppresses repeat mobile acknowledgement."""
    jwt_secret = "test-secret"
    jwt_user = uuid4()
    client, runtime = _build_client_and_runtime(jwt_secret=jwt_secret)
    token = _make_jwt(str(jwt_user), jwt_secret)

    first = client.post(
        "/v1/student/auth/bootstrap",
        headers={"Authorization": f"Bearer {token}"},
    )
    auth = runtime.resolve_auth(token)
    runtime.grant_behavioral_analytics_consent(auth=auth)
    second = client.post(
        "/v1/student/auth/bootstrap",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert first.json()["behavioral_analytics_consent_granted"] is False
    assert second.json()["behavioral_analytics_consent_granted"] is True


def test_invalid_bootstrap_jwt_is_rejected():
    """BA-4: invalid bootstrap token is still unauthorized."""
    _, runtime = _build_client_and_runtime(jwt_secret="expected-secret")
    token = _make_jwt(str(uuid4()), "wrong-secret")

    try:
        runtime.bootstrap_b2c_student_membership(token)
    except Exception as exc:
        assert exc.__class__.__name__ in {"InvalidSignatureError", "DecodeError"}
    else:
        raise AssertionError("Invalid bootstrap JWT was accepted")


def test_production_es256_verifier_rejects_hs256_even_when_fixture_secret_is_present(
    monkeypatch,
):
    """ADR-0017: production never selects HS256 from token metadata or environment."""
    from app.tenancy.membership_auth import build_supabase_es256_verifier

    monkeypatch.setenv("SUPABASE_JWT_SECRET", "ignored-fixture-secret")
    verifier = build_supabase_es256_verifier(
        jwks_url="https://project-ref.supabase.co/auth/v1/.well-known/jwks.json",
        issuer="https://project-ref.supabase.co/auth/v1",
    )
    token = _make_jwt(str(uuid4()), "ignored-fixture-secret")

    with pytest.raises(jwt.InvalidAlgorithmError):
        verifier(token)


def test_hs256_is_available_only_through_explicit_fixture_verifier():
    """ADR-0017: deterministic HS256 remains an explicitly injected test facility."""
    from app.tenancy.membership_auth import build_hs256_fixture_verifier

    user_id = uuid4()
    verifier = build_hs256_fixture_verifier("fixture-secret")

    assert verifier(_make_jwt(str(user_id), "fixture-secret")) == user_id


def test_valid_jwt_without_membership_on_non_bootstrap_endpoint_returns_403():
    """BA-5: non-bootstrap student endpoints stay strict."""
    jwt_secret = "test-secret"
    jwt_user = uuid4()
    client, _ = _build_client_and_runtime(jwt_secret=jwt_secret)
    token = _make_jwt(str(jwt_user), jwt_secret)

    response = client.get(
        "/v1/student/sessions/recent",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "No active membership for authenticated user"
