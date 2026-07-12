"""Live M4 signup -> durable session -> branch -> restart -> resume smoke.

Requires DATABASE_URL, SUPABASE_URL, and SUPABASE_ANON_KEY. It never prints credentials or tokens.
The created Supabase user/session rows are intentional smoke evidence for the active M4 SDD.
"""

from __future__ import annotations

import json
import os
import secrets
from uuid import uuid4

import httpx
from fastapi.testclient import TestClient

from app.configuration import ProductionRuntimeConfig, load_production_runtime_config
from app.main import create_app
from app.runtime.postgres_runtime import build_postgres_runtime


def _required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} is required")
    return value


def _signup(supabase_url: str, anon_key: str) -> str:
    response = httpx.post(
        f"{supabase_url.rstrip('/')}/auth/v1/signup",
        headers={"apikey": anon_key, "Authorization": f"Bearer {anon_key}"},
        json={
            "email": f"m4-runtime-smoke-{uuid4()}@example.com",
            "password": secrets.token_urlsafe(24),
        },
        timeout=20,
    )
    response.raise_for_status()
    token = response.json().get("access_token")
    if not token:
        raise RuntimeError("Supabase signup requires email confirmation; no access token returned")
    return str(token)


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _build_runtime(config: ProductionRuntimeConfig):
    return build_postgres_runtime(
        database_url=config.database_url,
        auth_issuer=config.auth_issuer,
        jwks_url=config.jwks_url,
        individual_tenant_id=config.individual_tenant_id,
    )


def _launch_path(client: TestClient, headers: dict[str, str]) -> dict[str, str]:
    class_id = client.get("/v1/student/curriculum/classes", headers=headers).json()["items"][0][
        "class_level_id"
    ]
    exam_id = client.get(
        "/v1/student/curriculum/exams", params={"class_id": class_id}, headers=headers
    ).json()["items"][0]["exam_id"]
    subject_id = client.get(
        "/v1/student/curriculum/subjects",
        params={"class_id": class_id, "exam_id": exam_id},
        headers=headers,
    ).json()["items"][0]["subject_id"]
    chapter_id = client.get(
        "/v1/student/curriculum/chapters",
        params={"class_id": class_id, "exam_id": exam_id, "subject_id": subject_id},
        headers=headers,
    ).json()["items"][0]["chapter_id"]
    concept_id = client.get(
        f"/v1/student/chapters/{chapter_id}/concept-entries", headers=headers
    ).json()["items"][0]["concept_entry_id"]
    return {
        "exam_id": exam_id,
        "subject_id": subject_id,
        "chapter_id": chapter_id,
        "concept_entry_id": concept_id,
    }


def main() -> None:
    config = load_production_runtime_config()
    token = _signup(config.supabase_url, _required("SUPABASE_ANON_KEY"))
    headers = _auth(token)

    runtime = _build_runtime(config)
    with TestClient(create_app(runtime=runtime)) as client:
        bootstrap = client.post("/v1/student/auth/bootstrap", headers=headers)
        bootstrap.raise_for_status()
        user_id = bootstrap.json()["user_id"]
        launch = _launch_path(client, headers)
        started = client.post(
            "/v1/student/sessions",
            json={**launch, "behavioral_analytics_consent": True},
            headers=headers,
        )
        started.raise_for_status()
        session_id = started.json()["session_id"]
        hydrated = client.get(f"/v1/student/sessions/{session_id}", headers=headers)
        hydrated.raise_for_status()
        root = hydrated.json()["canvas"]["nodes"][0]

        offer = client.post(
            "/v1/student/offer-sets/edge",
            json={
                "session_id": session_id,
                "source_node_id": root["node_id"],
                "thread_context_id": launch["concept_entry_id"],
            },
            headers=headers,
        )
        offer.raise_for_status()
        option = offer.json()["options"][0]
        choice = client.post(
            f"/v1/student/offer-sets/{offer.json()['offer_set_id']}/choices",
            json={
                "session_id": session_id,
                "source_node_id": root["node_id"],
                "outcome": "selected",
                "selected_option_id": option["option_id"],
                "selected_option_text": option["text"],
                "thread_context_id": launch["concept_entry_id"],
            },
            headers=headers,
        )
        choice.raise_for_status()

    restarted = _build_runtime(config)
    with TestClient(create_app(runtime=restarted)) as client:
        dashboard = client.get("/v1/student/dashboard", headers=headers)
        dashboard.raise_for_status()
        resumed = client.post(f"/v1/student/sessions/{session_id}/resume", headers=headers)
        resumed.raise_for_status()
        hydrated = client.get(f"/v1/student/sessions/{session_id}", headers=headers)
        hydrated.raise_for_status()
        body = hydrated.json()

        with restarted.database.transaction():
            job_count = restarted.database.execute(
                "SELECT count(*) AS count FROM public.jobs "
                "WHERE tenant_id = %(tenant_id)s AND payload->>'student_user_id' = %(user_id)s",
                {"tenant_id": restarted.tenant_id, "user_id": user_id},
            ).fetchone()["count"]

    print(
        json.dumps(
            {
                "bootstrap": "ok",
                "session_id": session_id,
                "dashboard_resume": "ok",
                "nodes_after_restart": len(body["canvas"]["nodes"]),
                "edges_after_restart": len(body["canvas"]["edges"]),
                "classify_jobs": int(job_count),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
