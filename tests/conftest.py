"""Pytest local environment bootstrap helpers."""

from __future__ import annotations

import os
from pathlib import Path


def pytest_configure() -> None:
    """Load opt-in local integration settings without printing secret values."""

    _load_env_key_if_missing("TEST_DATABASE_URL")


def _load_env_key_if_missing(key: str) -> None:
    if os.getenv(key):
        return

    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        name, raw_value = stripped.split("=", 1)
        if name.strip() == key:
            os.environ[key] = _unquote(raw_value.strip())
            return


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value
