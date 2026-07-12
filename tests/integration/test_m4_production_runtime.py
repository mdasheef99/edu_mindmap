"""M4 production composition boundary tests.

Traceability:
- phase-3-m4-runtime-closure-remediation-sdd.md §§3 R1-R2, 4 PR-1/PR-2
- development-approach.md §6 disciplines 6 and 10
- backend-architecture.md §§3, 5.3, 6-8, 11
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock
from uuid import uuid4

import pytest


def test_default_app_fails_closed_without_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    """PR-2: an implicit in-memory API must never be the production fallback."""
    from app.main import create_app

    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        create_app()


def test_default_app_builds_postgres_runtime_from_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """PR-1: default API composition delegates to the durable runtime factory."""
    import app.main as main_module

    durable_runtime = Mock(name="durable_runtime")
    builder = Mock(return_value=durable_runtime)
    tenant_id = uuid4()
    monkeypatch.setenv("DATABASE_URL", "postgresql://app:secret@db.example.test:5432/app")
    monkeypatch.setenv("SUPABASE_URL", "https://project-ref.supabase.co")
    monkeypatch.setenv("M4_INDIVIDUAL_TENANT_ID", str(tenant_id))
    monkeypatch.setattr(main_module, "build_postgres_runtime", builder)

    app = main_module.create_app()

    assert app.state.session_runtime is durable_runtime
    builder.assert_called_once_with(
        database_url="postgresql://app:secret@db.example.test:5432/app",
        auth_issuer="https://project-ref.supabase.co/auth/v1",
        jwks_url="https://project-ref.supabase.co/auth/v1/.well-known/jwks.json",
        individual_tenant_id=tenant_id,
    )


def test_default_app_fails_closed_without_individual_tenant_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """R1/R4: production never chooses an implicit individual tenant."""
    from app.main import create_app

    monkeypatch.setenv("DATABASE_URL", "postgresql://app:secret@db.example.test:5432/app")
    monkeypatch.setenv("SUPABASE_URL", "https://project-ref.supabase.co")
    monkeypatch.delenv("M4_INDIVIDUAL_TENANT_ID", raising=False)

    with pytest.raises(RuntimeError, match="M4_INDIVIDUAL_TENANT_ID"):
        create_app()


def test_render_api_declares_supabase_and_database_runtime_configuration() -> None:
    """R1/R4: the deployed API declares the inputs used by production composition."""
    render_yaml = Path("render.yaml").read_text(encoding="utf-8")
    api_section = render_yaml.split("- type: worker", maxsplit=1)[0]

    assert "DATABASE_URL" in api_section
    assert "SUPABASE_URL" in api_section
    assert "M4_INDIVIDUAL_TENANT_ID" in api_section
    assert "CORS_ALLOWED_ORIGINS" in api_section
    assert "SUPABASE_JWT_SECRET" not in api_section
