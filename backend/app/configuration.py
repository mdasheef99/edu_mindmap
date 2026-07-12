"""Environment-backed process configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping
from uuid import UUID


@dataclass(frozen=True)
class ProductionRuntimeConfig:
    """Validated inputs for the durable M4 API runtime."""

    database_url: str
    supabase_url: str
    auth_issuer: str
    jwks_url: str
    individual_tenant_id: UUID
    cors_allowed_origins: tuple[str, ...]


def allowed_origins() -> list[str]:
    """Return explicitly configured CORS origins."""

    raw = os.getenv("CORS_ALLOWED_ORIGINS", "")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def load_production_runtime_config(
    environment: Mapping[str, str] | None = None,
) -> ProductionRuntimeConfig:
    """Load explicit production inputs and fail closed when any are invalid."""

    values = os.environ if environment is None else environment
    database_url = _required(values, "DATABASE_URL")
    supabase_url = _required(values, "SUPABASE_URL").rstrip("/")
    tenant_value = _required(values, "M4_INDIVIDUAL_TENANT_ID")
    try:
        individual_tenant_id = UUID(tenant_value)
    except ValueError as exc:
        raise RuntimeError("M4_INDIVIDUAL_TENANT_ID must be a valid UUID") from exc

    auth_issuer = values.get("SUPABASE_AUTH_URL", "").strip().rstrip("/")
    if not auth_issuer:
        auth_issuer = f"{supabase_url}/auth/v1"
    jwks_url = values.get("SUPABASE_JWT_JWKS_URL", "").strip()
    if not jwks_url:
        jwks_url = f"{auth_issuer}/.well-known/jwks.json"
    origins = tuple(
        origin.strip()
        for origin in values.get("CORS_ALLOWED_ORIGINS", "").split(",")
        if origin.strip()
    )
    return ProductionRuntimeConfig(
        database_url=database_url,
        supabase_url=supabase_url,
        auth_issuer=auth_issuer,
        jwks_url=jwks_url,
        individual_tenant_id=individual_tenant_id,
        cors_allowed_origins=origins,
    )


def _required(environment: Mapping[str, str], name: str) -> str:
    value = environment.get(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is required for the production API runtime")
    return value
