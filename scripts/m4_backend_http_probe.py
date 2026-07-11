from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
ENV: dict[str, str] = {}
for line in (ROOT / "mobile" / "app" / ".env").read_text(encoding="utf-8").splitlines():
    if line.strip() and not line.lstrip().startswith("#") and "=" in line:
        key, value = line.split("=", 1)
        ENV[key.strip()] = value.strip()


def main() -> int:
    env = os.environ.copy()
    env["PYTHONPATH"] = "backend"
    env["SUPABASE_URL"] = "https://jbmqyxhrmcbdgardamrp.supabase.co"
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
            "--log-level",
            "debug",
        ],
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        for _ in range(30):
            try:
                httpx.get("http://127.0.0.1:8000/docs", timeout=1)
                break
            except Exception:
                time.sleep(0.5)
        email = f"codex.m4.probe.{time.time_ns()}@gmail.com"
        signup = httpx.post(
            f"{ENV['EXPO_PUBLIC_SUPABASE_URL']}/auth/v1/signup",
            headers={
                "Content-Type": "application/json",
                "apikey": ENV["EXPO_PUBLIC_SUPABASE_ANON_KEY"],
                "Authorization": f"Bearer {ENV['EXPO_PUBLIC_SUPABASE_ANON_KEY']}",
            },
            json={"email": email, "password": "M4SmokePass123!"},
            timeout=20,
        )
        print("signup", signup.status_code)
        signup_body = signup.json()
        token = signup_body.get("access_token")
        if not token:
            print("signup failed or requires email confirmation:", signup_body)
            return 1
        bootstrap = httpx.post(
            "http://127.0.0.1:8000/v1/student/auth/bootstrap",
            headers={"Authorization": f"Bearer {token}"},
            timeout=20,
        )
        print("bootstrap", bootstrap.status_code, bootstrap.text[:500])
        classes = httpx.get(
            "http://127.0.0.1:8000/v1/student/curriculum/classes",
            headers={"Authorization": f"Bearer {token}"},
            timeout=20,
        )
        print("classes", classes.status_code, classes.text[:500])
        return 0
    finally:
        server.terminate()
        try:
            stdout, stderr = server.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
            stdout, stderr = server.communicate(timeout=5)
        print("--- uvicorn stdout ---")
        print(stdout)
        print("--- uvicorn stderr ---")
        print(stderr)


if __name__ == "__main__":
    raise SystemExit(main())
