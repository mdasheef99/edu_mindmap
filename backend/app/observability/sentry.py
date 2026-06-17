"""Optional Sentry wiring for Phase 1 smoke verification."""

from __future__ import annotations

import os
from typing import Any


def init_sentry() -> bool:
    """Initialize Sentry when `SENTRY_DSN_BACKEND` and sentry-sdk are available."""
    dsn = os.getenv("SENTRY_DSN_BACKEND")
    if not dsn:
        return False
    try:
        import sentry_sdk
    except ImportError:
        return False

    sentry_sdk.init(dsn=dsn, traces_sample_rate=0.0)
    return True


def capture_phase1_smoke_error(extra: dict[str, Any] | None = None) -> bool:
    """Send a deliberate non-fatal exception to Sentry for the Phase 1 gate."""
    try:
        import sentry_sdk
    except ImportError:
        return False

    try:
        raise RuntimeError("phase1_backend_sentry_smoke")
    except RuntimeError as exc:
        with sentry_sdk.push_scope() as scope:
            for key, value in (extra or {}).items():
                scope.set_extra(key, value)
            sentry_sdk.capture_exception(exc)
        sentry_sdk.flush(timeout=5)
    return True
