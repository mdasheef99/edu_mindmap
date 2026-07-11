from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / ".m4-backend-keepalive.log"
ERR = ROOT / ".m4-backend-keepalive.err"

env = os.environ.copy()
env["PYTHONPATH"] = "backend"
env["SUPABASE_URL"] = "https://jbmqyxhrmcbdgardamrp.supabase.co"

with LOG.open("ab") as stdout, ERR.open("ab") as stderr:
    server = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:create_app",
            "--factory",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ],
        cwd=ROOT,
        env=env,
        stdout=stdout,
        stderr=stderr,
    )
    try:
        while server.poll() is None:
            time.sleep(1)
    finally:
        if server.poll() is None:
            server.terminate()
