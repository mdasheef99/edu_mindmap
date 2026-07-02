"""M4 auth + B2C bootstrap tests.

Traceability:
- docs/planning/sdd/phase-3-m4-curriculum-auth-sdd.md §§6.2-6.3, 12.1
- docs/architecture/adr-log-02.md ADR-0015
- docs/architecture/backend-architecture.md §§5.4-5.5, 11
"""

from uuid import uuid4

import jwt
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
    assert records == [
        {"user_id": jwt_user, "tenant_id": runtime.tenant_id, "role": "student"}
    ]


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
