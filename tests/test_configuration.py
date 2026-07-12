"""Production configuration boundaries for the reconstructed M4 runtime."""

from __future__ import annotations

from uuid import uuid4

import pytest

TEST_TENANT_ID = uuid4()


def _environment(**overrides: str) -> dict[str, str]:
    values = {
        "DATABASE_URL": "postgresql://app:password@db.example.test:5432/app",
        "SUPABASE_URL": "https://project-ref.supabase.co",
        "M4_INDIVIDUAL_TENANT_ID": str(TEST_TENANT_ID),
        "CORS_ALLOWED_ORIGINS": "https://app.example.test, https://admin.example.test",
    }
    values.update(overrides)
    return values


def test_production_runtime_configuration_is_explicit_and_derived() -> None:
    from app.configuration import load_production_runtime_config

    config = load_production_runtime_config(_environment())

    assert config.database_url.startswith("postgresql://")
    assert config.supabase_url == "https://project-ref.supabase.co"
    assert config.auth_issuer == "https://project-ref.supabase.co/auth/v1"
    assert config.jwks_url == "https://project-ref.supabase.co/auth/v1/.well-known/jwks.json"
    assert config.individual_tenant_id == TEST_TENANT_ID
    assert config.cors_allowed_origins == (
        "https://app.example.test",
        "https://admin.example.test",
    )


@pytest.mark.parametrize(
    ("missing_name", "message"),
    [
        ("DATABASE_URL", "DATABASE_URL"),
        ("SUPABASE_URL", "SUPABASE_URL"),
        ("M4_INDIVIDUAL_TENANT_ID", "M4_INDIVIDUAL_TENANT_ID"),
    ],
)
def test_production_runtime_configuration_fails_closed_when_required_value_is_missing(
    missing_name: str,
    message: str,
) -> None:
    from app.configuration import load_production_runtime_config

    environment = _environment()
    environment.pop(missing_name)

    with pytest.raises(RuntimeError, match=message):
        load_production_runtime_config(environment)


def test_production_runtime_configuration_rejects_malformed_tenant_id() -> None:
    from app.configuration import load_production_runtime_config

    with pytest.raises(RuntimeError, match="M4_INDIVIDUAL_TENANT_ID"):
        load_production_runtime_config(_environment(M4_INDIVIDUAL_TENANT_ID="not-a-uuid"))


def test_explicit_issuer_and_jwks_override_derived_values() -> None:
    from app.configuration import load_production_runtime_config

    config = load_production_runtime_config(
        _environment(
            SUPABASE_AUTH_URL="https://issuer.example.test/auth/v1",
            SUPABASE_JWT_JWKS_URL="https://keys.example.test/jwks.json",
        )
    )

    assert config.auth_issuer == "https://issuer.example.test/auth/v1"
    assert config.jwks_url == "https://keys.example.test/jwks.json"


def test_production_configuration_ignores_hs256_fixture_secret() -> None:
    from app.configuration import load_production_runtime_config

    config = load_production_runtime_config(
        _environment(SUPABASE_JWT_SECRET="must-not-enter-production-composition")
    )

    assert not hasattr(config, "jwt_secret")
