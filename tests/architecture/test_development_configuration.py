"""Configuration boundaries for development-only credentials and origins."""

import importlib.util
from pathlib import Path

import pytest
from app.configuration import allowed_origins


def _load_dev_smoke_module():
    path = Path(__file__).resolve().parents[2] / "backend" / "scripts" / "dev_smoke_bootstrap.py"
    spec = importlib.util.spec_from_file_location("dev_smoke_bootstrap", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_allowed_origins_are_empty_when_not_configured(monkeypatch) -> None:
    monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)
    assert allowed_origins() == []


def test_allowed_origins_are_parsed_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://one.invalid, https://two.invalid")
    assert allowed_origins() == ["https://one.invalid", "https://two.invalid"]


def test_dev_smoke_secret_is_required(monkeypatch) -> None:
    module = _load_dev_smoke_module()
    monkeypatch.delenv("DEV_JWT_SECRET", raising=False)
    with pytest.raises(RuntimeError, match="DEV_JWT_SECRET"):
        module._dev_jwt_secret()


def test_dev_smoke_secret_comes_from_environment(monkeypatch) -> None:
    module = _load_dev_smoke_module()
    monkeypatch.setenv("DEV_JWT_SECRET", "disposable-test-value")
    assert module._dev_jwt_secret() == "disposable-test-value"
