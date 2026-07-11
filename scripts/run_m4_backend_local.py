from __future__ import annotations

import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True

import uvicorn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))


def load_workspace_env() -> None:
    """Load repository configuration, overriding unrelated parent-process values."""
    for raw_line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        os.environ[name.strip()] = value.strip().strip('"').strip("'")

if __name__ == "__main__":
    load_workspace_env()
    uvicorn.run(
        "app.main:create_app",
        factory=True,
        host="0.0.0.0",
        port=8000,
    )
