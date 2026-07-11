"""Red tests for SDD \u00a79 auth + tenant resolution (Phase 2 priority 2)."""

from uuid import uuid4

import jwt
from fastapi.testclient import TestClient


def _make_jwt(user_id: str, secret: str) -> str:
    return jwt.encode({"sub": user_id}, secret, algorithm="HS256")


def _build_client_and_runtime(
    *,
    runtime_tenant_id=None,
    runtime_student_id=None,
    jwt_secret: str = "test-secret",
):
    from app.main import SessionRuntime, create_app

    tenant_id = runtime_tenant_id or uuid4()
    student_id = runtime_student_id or uuid4()
    runtime = SessionRuntime.for_testing(
        tenant_id=tenant_id,
        student_user_id=student_id,
        jwt_secret=jwt_secret,
    )
    return TestClient(create_app(runtime=runtime)), runtime


def _seed_curriculum(runtime, *, tenant_id=None):
    from app.projections.curriculum import CurriculumIngestInput, build_curriculum_rows

    launch_tenant = tenant_id or runtime.tenant_id
    chapter_id = uuid4()
    chapter_analysis_id = uuid4()
    concept_id = uuid4()
    runtime.curriculum.ingest(
        build_curriculum_rows(
            CurriculumIngestInput(
                tenant_id=launch_tenant,
                exam_id=uuid4(),
                subject_id=uuid4(),
                chapter_id=chapter_id,
                title="Electricity",
                chapter_analysis_id=chapter_analysis_id,
                segment_index_version="p0-v1",
                pipeline_version="p0-p4-v1",
                prompt_version="fixtures-v1",
                model_id="fixture-model",
                pages=["Electric current flows through a closed circuit."],
                named_concepts=[
                    {
                        "concept_id": str(concept_id),
                        "label": "Electric current",
                        "definition": "Flow of charge in a circuit.",
                        "category_tag": "definition",
                        "passage_refs": {
                            "definitional": [f"{chapter_id}_para_001"],
                            "explanatory": [],
                            "application": [],
                        },
                    }
                ],
                embedded_concepts=[],
                edges=[],
            )
        )
    )
    chapter_row = next(iter(runtime.curriculum.chapters.values()))
    return {
        "exam_id": str(chapter_row["exam_id"]),
        "subject_id": str(chapter_row["subject_id"]),
        "chapter_id": str(chapter_id),
        "concept_entry_id": str(concept_id),
        "chapter_analysis_id": str(chapter_analysis_id),
    }


def _session_start_body(runtime, *, tenant_id=None):
    seeded = _seed_curriculum(runtime, tenant_id=tenant_id)
    return {
        "exam_id": seeded["exam_id"],
        "subject_id": seeded["subject_id"],
        "chapter_id": seeded["chapter_id"],
        "concept_entry_id": seeded["concept_entry_id"],
    }


def _single_event_of_type(runtime, event_type: str):
    events = [event for event in runtime.event_store.events if event["event_type"] == event_type]
    assert len(events) == 1
    return events[0]


def test_missing_auth_returns_401():
    """T??: request without Authorization header must return 401."""
    client, runtime = _build_client_and_runtime()

    response = client.post("/v1/student/sessions", json=_session_start_body(runtime))

    assert response.status_code == 401


def test_jwt_resolves_backend_tenant_and_role():
    """T??: valid JWT must resolve tenant/role from memberships, overriding runtime defaults."""
    jwt_secret = "test-secret"
    runtime_tenant = uuid4()
    jwt_user = uuid4()
    resolved_tenant = uuid4()

    client, runtime = _build_client_and_runtime(
        runtime_tenant_id=runtime_tenant,
        jwt_secret=jwt_secret,
    )
    runtime.memberships.add_membership(
        user_id=jwt_user,
        tenant_id=resolved_tenant,
        role="student",
    )
    token = _make_jwt(str(jwt_user), jwt_secret)

    response = client.post(
        "/v1/student/sessions",
        json=_session_start_body(runtime, tenant_id=resolved_tenant),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    event = _single_event_of_type(runtime, "session_started")
    assert event["tenant_id"] == resolved_tenant
    assert event["student_id"] == jwt_user
    # Ensure it did NOT use the hardcoded runtime defaults
    assert event["tenant_id"] != runtime_tenant


def test_authenticated_request_ignores_mobile_supplied_tenant_id():
    """T??: mobile-supplied tenant_id must be ignored even when JWT auth is present."""
    jwt_secret = "test-secret"
    runtime_tenant = uuid4()
    jwt_user = uuid4()
    resolved_tenant = uuid4()
    attacker_tenant = uuid4()

    client, runtime = _build_client_and_runtime(
        runtime_tenant_id=runtime_tenant,
        jwt_secret=jwt_secret,
    )
    runtime.memberships.add_membership(
        user_id=jwt_user,
        tenant_id=resolved_tenant,
        role="student",
    )
    token = _make_jwt(str(jwt_user), jwt_secret)
    body = _session_start_body(runtime, tenant_id=resolved_tenant)
    body["tenant_id"] = str(attacker_tenant)

    response = client.post(
        "/v1/student/sessions",
        json=body,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    event = _single_event_of_type(runtime, "session_started")
    assert event["tenant_id"] == resolved_tenant
    assert event["tenant_id"] != attacker_tenant


def test_valid_jwt_without_membership_returns_membership_error():
    """ADR-0015: valid user JWT with no tenant membership is not an invalid token."""
    jwt_secret = "test-secret"
    jwt_user = uuid4()
    client, runtime = _build_client_and_runtime(jwt_secret=jwt_secret)
    token = _make_jwt(str(jwt_user), jwt_secret)

    response = client.post(
        "/v1/student/sessions",
        json=_session_start_body(runtime),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "No active membership for authenticated user"


def test_acknowledged_first_session_appends_consent_recorded():
    """M4 §6.4: an explicit acknowledgement appends consent_recorded once."""
    jwt_secret = "test-secret"
    jwt_user = uuid4()
    resolved_tenant = uuid4()

    client, runtime = _build_client_and_runtime(jwt_secret=jwt_secret)
    runtime.memberships.add_membership(
        user_id=jwt_user,
        tenant_id=resolved_tenant,
        role="student",
    )
    token = _make_jwt(str(jwt_user), jwt_secret)

    response = client.post(
        "/v1/student/sessions",
        json={
            **_session_start_body(runtime, tenant_id=resolved_tenant),
            "behavioral_analytics_consent": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    event_types = [e["event_type"] for e in runtime.event_store.events]
    assert "session_started" in event_types
    assert "consent_recorded" in event_types
    consent_events = [
        e for e in runtime.event_store.events if e["event_type"] == "consent_recorded"
    ]
    assert len(consent_events) == 1
    assert consent_events[0]["tenant_id"] == resolved_tenant
    assert consent_events[0]["student_id"] == jwt_user
