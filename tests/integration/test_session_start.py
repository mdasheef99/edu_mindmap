from uuid import uuid4

import jwt
from fastapi.testclient import TestClient

FORBIDDEN_ANALYTIC_FIELD_FRAGMENTS = (
    "dimension",
    "classification",
    "coverage",
    "gap",
    "score",
    "confidence",
    "entropy",
    "vector",
    "profile",
    "weight",
    "propensity",
    "probe",
    "teacher_",
)


def _build_client_and_runtime(jwt_secret: str = "test-secret"):
    from app.main import SessionRuntime, create_app

    tenant_id = uuid4()
    student_user_id = uuid4()
    runtime = SessionRuntime.for_testing(
        tenant_id=tenant_id,
        student_user_id=student_user_id,
        jwt_secret=jwt_secret,
    )
    runtime.memberships.add_membership(
        user_id=student_user_id,
        tenant_id=tenant_id,
        role="student",
    )
    client = TestClient(create_app(runtime=runtime))
    token = jwt.encode({"sub": str(student_user_id)}, jwt_secret, algorithm="HS256")
    client.headers["Authorization"] = f"Bearer {token}"
    return client, runtime


def _seed_curriculum(runtime):
    from app.projections.curriculum import CurriculumIngestInput, build_curriculum_rows

    chapter_id = uuid4()
    chapter_analysis_id = uuid4()
    concept_id = uuid4()
    runtime.curriculum.ingest(
        build_curriculum_rows(
            CurriculumIngestInput(
                tenant_id=runtime.tenant_id,
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


def _session_start_body(seed: dict[str, str]) -> dict[str, str]:
    return {
        "exam_id": seed["exam_id"],
        "subject_id": seed["subject_id"],
        "chapter_id": seed["chapter_id"],
        "concept_entry_id": seed["concept_entry_id"],
    }


def test_session_start_appends_session_started() -> None:
    """T3: POST /v1/student/sessions must append session_started."""
    client, runtime = _build_client_and_runtime()
    seeded = _seed_curriculum(runtime)
    request_body = _session_start_body(seeded)

    response = client.post("/v1/student/sessions", json=request_body)

    assert response.status_code == 201
    session_id = response.json()["session_id"]

    session_events = [e for e in runtime.event_store.events if e["event_type"] == "session_started"]
    assert len(session_events) == 1
    event = session_events[0]

    assert event["event_type"] == "session_started"
    assert event["producer"] == "server"
    assert str(event["tenant_id"]) == str(runtime.tenant_id)
    assert str(event["student_id"]) == str(runtime.student_user_id)
    assert str(event["session_id"]) == session_id
    assert event["payload"] == {
        "session_id": session_id,
        "student_user_id": str(runtime.student_user_id),
        "exam_id": request_body["exam_id"],
        "subject_id": request_body["subject_id"],
        "chapter_id": request_body["chapter_id"],
        "concept_entry_id": request_body["concept_entry_id"],
        "chapter_analysis_id": seeded["chapter_analysis_id"],
    }


def test_session_start_writes_student_rm_session() -> None:
    """T4: session start must synchronously write student_rm.sessions."""
    client, runtime = _build_client_and_runtime()
    seeded = _seed_curriculum(runtime)
    request_body = _session_start_body(seeded)

    response = client.post("/v1/student/sessions", json=request_body)

    assert response.status_code == 201
    body = response.json()
    session_row = runtime.student_sessions.sessions[body["session_id"]]

    assert str(session_row["tenant_id"]) == str(runtime.tenant_id)
    assert str(session_row["student_user_id"]) == str(runtime.student_user_id)
    assert str(session_row["exam_id"]) == request_body["exam_id"]
    assert str(session_row["subject_id"]) == request_body["subject_id"]
    assert str(session_row["chapter_id"]) == request_body["chapter_id"]
    assert str(session_row["concept_entry_id"]) == request_body["concept_entry_id"]
    assert str(session_row["chapter_analysis_id"]) == seeded["chapter_analysis_id"]
    assert session_row["status"] == "active"
    assert session_row["last_active_node_id"] is None
    assert session_row["started_at"] == session_row["last_active_at"]


def test_student_session_response_has_no_analytic_fields() -> None:
    """T5: student session response must remain category-invisible."""
    client, runtime = _build_client_and_runtime()
    request_body = _session_start_body(_seed_curriculum(runtime))

    response = client.post("/v1/student/sessions", json=request_body)

    assert response.status_code == 201
    response_fields = set(response.json())

    assert not any(
        forbidden in field
        for field in response_fields
        for forbidden in FORBIDDEN_ANALYTIC_FIELD_FRAGMENTS
    )


def test_session_start_resolves_real_chapter_from_curriculum() -> None:
    """SDD §9 T14: session start must resolve pinned chapter_analysis_id from curriculum."""
    client, runtime = _build_client_and_runtime()
    seeded = _seed_curriculum(runtime)

    response = client.post(
        "/v1/student/sessions",
        json=_session_start_body(seeded),
    )

    assert response.status_code == 201
    assert response.json()["chapter_analysis_id"] == seeded["chapter_analysis_id"]
    session_events = [e for e in runtime.event_store.events if e["event_type"] == "session_started"]
    session_event = session_events[0]
    assert str(session_event["chapter_analysis_id"]) == seeded["chapter_analysis_id"]


def test_student_api_exposes_no_raw_event_endpoint() -> None:
    """T24: /v1/student must not expose raw event history (read) endpoints.

    Category Invisibility forbids *returning* raw event history. The M3-C Seam A
    ingest endpoint (POST /sessions/{id}/events, student-api-spec.md §5) is a
    write-only whitelist boundary — it is permitted, but must never offer a GET
    that reads back the event log.
    """
    from app.main import create_app

    app = create_app()
    student_routes = {
        route.path for route in app.routes if getattr(route, "path", "").startswith("/v1/student")
    }

    # No top-level raw event collection endpoint.
    assert "/v1/student/events" not in student_routes

    # The only "/events" path is the session-scoped ingest, and it is POST-only.
    events_routes = [
        route
        for route in app.routes
        if getattr(route, "path", "").startswith("/v1/student")
        and getattr(route, "path", "").endswith("/events")
    ]
    assert {route.path for route in events_routes} == {
        "/v1/student/sessions/{session_id}/events"
    }
    for route in events_routes:
        assert set(getattr(route, "methods", set()) or set()) <= {"POST"}
