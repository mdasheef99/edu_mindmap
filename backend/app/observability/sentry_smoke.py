"""CLI for sending the deliberate Phase 1 backend Sentry smoke error."""

from __future__ import annotations

from app.observability.sentry import capture_phase1_smoke_error, init_sentry


def main() -> None:
    initialized = init_sentry()
    captured = capture_phase1_smoke_error({"phase": "phase_1_walking_skeleton"})
    if not initialized or not captured:
        raise SystemExit("Sentry smoke was not sent; check SENTRY_DSN_BACKEND and sentry-sdk.")


if __name__ == "__main__":
    main()