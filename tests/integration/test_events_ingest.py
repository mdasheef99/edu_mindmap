"""Seam A integration tests — POST /v1/student/sessions/{id}/events (M3-C R1).

Red-before-green per canon §9. Verifies the client-event ingest boundary:
whitelist + boundary validation (visit_source enum, scale range) and
worker-only producer rejection.

Traceability:
- docs/planning/sdd/phase-3-m3c-infrastructure-remediation-sdd.md §4, §9.1 (TA-1..TA-8)
- docs/api/student-api-spec.md §5 (POST /events whitelist)
- docs/planning/session-path-data-contract.md §8 (interaction event contract)
"""

from datetime import datetime, timezone
from uuid import uuid4

import jwt
from fastapi.testclient import TestClient


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


def _envelope(event_type, *, runtime, session_id, node_id=None, payload):
    env = {
        "event_id": str(uuid4()),
        "event_type": event_type,
        "event_version": 1,
        "tenant_id": str(runtime.tenant_id),
        "actor_user_id": str(runtime.student_user_id),
        "student_id": str(runtime.student_user_id),
        "session_id": str(session_id),
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }
    if node_id is not None:
        env["node_id"] = str(node_id)
    return env


def _node_visited(runtime, session_id, *, visit_source="tap", node_id=None):
    node_id = node_id or uuid4()
    return _envelope(
        "node_visited",
        runtime=runtime,
        session_id=session_id,
        node_id=node_id,
        payload={
            "node_id": str(node_id),
            "session_id": str(session_id),
            "visit_source": visit_source,
        },
    )


def _viewport_changed(runtime, session_id, *, scale=1.0):
    return _envelope(
        "viewport_changed",
        runtime=runtime,
        session_id=session_id,
        payload={
            "session_id": str(session_id),
            "scale": scale,
            "translate_x": 0.0,
            "translate_y": 0.0,
            "visible_node_ids": [],
        },
    )


def _post(client, session_id, events):
    return client.post(f"/v1/student/sessions/{session_id}/events", json={"events": events})


def test_ta1_post_valid_node_visited_accepted() -> None:
    client, runtime = _build_client_and_runtime()
    session_id = uuid4()
    response = _post(client, session_id, [_node_visited(runtime, session_id)])
    assert response.status_code == 202
    assert response.json()["accepted"] == 1


def test_ta2_post_valid_viewport_changed_accepted() -> None:
    client, runtime = _build_client_and_runtime()
    session_id = uuid4()
    response = _post(client, session_id, [_viewport_changed(runtime, session_id)])
    assert response.status_code == 202
    assert response.json()["accepted"] == 1


def test_ta3_unknown_event_type_rejected() -> None:
    client, runtime = _build_client_and_runtime()
    session_id = uuid4()
    bad = _envelope("totally_unknown", runtime=runtime, session_id=session_id, payload={})
    response = _post(client, session_id, [bad])
    assert response.status_code == 400


def test_ta4_worker_only_type_from_client_forbidden() -> None:
    client, runtime = _build_client_and_runtime()
    session_id = uuid4()
    worker_event = _envelope(
        "question_classified", runtime=runtime, session_id=session_id, payload={}
    )
    response = _post(client, session_id, [worker_event])
    assert response.status_code == 403


def test_ta5_invalid_visit_source_rejected() -> None:
    client, runtime = _build_client_and_runtime()
    session_id = uuid4()
    bad = _node_visited(runtime, session_id, visit_source="invalid_value")
    response = _post(client, session_id, [bad])
    assert response.status_code == 400


def test_ta6_scale_out_of_range_rejected() -> None:
    client, runtime = _build_client_and_runtime()
    session_id = uuid4()
    bad = _viewport_changed(runtime, session_id, scale=99.0)
    response = _post(client, session_id, [bad])
    assert response.status_code == 400


def test_ta7_batch_partial_acceptance() -> None:
    client, runtime = _build_client_and_runtime()
    session_id = uuid4()
    events = [
        _node_visited(runtime, session_id),
        _viewport_changed(runtime, session_id),
        _node_visited(runtime, session_id, visit_source="invalid_value"),
    ]
    response = _post(client, session_id, events)
    assert response.status_code == 202
    body = response.json()
    assert body["accepted"] == 2
    assert [r["index"] for r in body["rejected"]] == [2]


def test_ta8_accepted_event_appended_to_store() -> None:
    client, runtime = _build_client_and_runtime()
    session_id = uuid4()
    before = len(runtime.event_store.events)
    response = _post(client, session_id, [_node_visited(runtime, session_id)])
    assert response.status_code == 202
    assert len(runtime.event_store.events) == before + 1
