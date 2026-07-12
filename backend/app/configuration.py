"""Environment-backed process configuration."""

from __future__ import annotations

import os


def allowed_origins() -> list[str]:
    """Return explicitly configured CORS origins."""

    raw = os.getenv("CORS_ALLOWED_ORIGINS", "")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]
