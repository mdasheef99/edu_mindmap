from uuid import uuid4

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


def _build_client_and_runtime():
    from app.main import SessionRuntime, create_app

    runtime = SessionRuntime.for_testing(
        tenant_id=uuid4(),
        student_user_id=uuid4(),
    )
    return TestClient(create_app(runtime=runtime)), runtime


def test_session_start_appends_session_started() -> None:
    """T3: POST /v1/student/sessions must append session_started."""
    client, runtime = _build_client_and_runtime()
    request_body = {
        "exam_id": str(uuid4()),
        "subject_id": str(uuid4()),
        "chapter_id": str(uuid4()),
        "concept_entry_id": str(uuid4()),
        "chapter_analysis_id": str(uuid4()),
    }

    response = client.post("/v1/student/sessions", json=request_body)

    assert response.status_code == 201
    session_id = response.json()["session_id"]

    assert len(runtime.event_store.events) == 1
    event = runtime.event_store.events[0]

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
        "chapter_analysis_id": request_body["chapter_analysis_id"],
    }


def test_session_start_writes_student_rm_session() -> None:
    """T4: session start must synchronously write student_rm.sessions."""
    client, runtime = _build_client_and_runtime()
    request_body = {
        "exam_id": str(uuid4()),
        "subject_id": str(uuid4()),
        "chapter_id": str(uuid4()),
        "concept_entry_id": str(uuid4()),
        "chapter_analysis_id": str(uuid4()),
    }

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
    assert str(session_row["chapter_analysis_id"]) == request_body["chapter_analysis_id"]
    assert session_row["status"] == "active"
    assert session_row["last_active_node_id"] is None
    assert session_row["started_at"] == session_row["last_active_at"]


def test_student_session_response_has_no_analytic_fields() -> None:
    """T5: student session response must remain category-invisible."""
    client, _ = _build_client_and_runtime()
    request_body = {
        "exam_id": str(uuid4()),
        "subject_id": str(uuid4()),
        "chapter_id": str(uuid4()),
        "concept_entry_id": str(uuid4()),
        "chapter_analysis_id": str(uuid4()),
    }

    response = client.post("/v1/student/sessions", json=request_body)

    assert response.status_code == 201
    response_fields = set(response.json())

    assert not any(
        forbidden in field
        for field in response_fields
        for forbidden in FORBIDDEN_ANALYTIC_FIELD_FRAGMENTS
    )


def test_student_api_exposes_no_raw_event_endpoint() -> None:
    """T24: /v1/student must not expose raw event history endpoints."""
    from app.main import create_app

    app = create_app()
    student_routes = {
        route.path for route in app.routes if getattr(route, "path", "").startswith("/v1/student")
    }

    assert "/v1/student/events" not in student_routes
    assert "/v1/student/sessions/{session_id}/events" not in student_routes
    assert not any(path.endswith("/events") for path in student_routes)
