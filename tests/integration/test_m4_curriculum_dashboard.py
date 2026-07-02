"""M4 student curriculum and dashboard endpoint tests.

Traceability:
- docs/api/student-api-spec.md §§4-5
- docs/planning/sdd/phase-3-m4-curriculum-auth-sdd.md §§8.1-8.2, 12.2
"""

from uuid import UUID, uuid4

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
    "teacher",
    "analytic",
)


def _build_client_runtime_and_seed():
    from app.main import SessionRuntime, create_app
    from app.projections.catalog import InMemoryCatalogStore, seed_m4_electricity_catalog
    from app.projections.curriculum import CurriculumIngestInput, build_curriculum_rows

    jwt_secret = "test-secret"
    tenant_id = uuid4()
    user_id = uuid4()
    runtime = SessionRuntime.for_testing(
        tenant_id=tenant_id,
        student_user_id=user_id,
        jwt_secret=jwt_secret,
    )
    runtime.memberships.add_membership(user_id=user_id, tenant_id=tenant_id, role="student")

    catalog = InMemoryCatalogStore()
    seed = seed_m4_electricity_catalog(catalog, tenant_id=tenant_id)
    runtime.catalog = catalog

    runtime.curriculum.ingest(
        build_curriculum_rows(
            CurriculumIngestInput(
                tenant_id=tenant_id,
                exam_id=seed.exam_id,
                subject_id=seed.subject_id,
                chapter_id=seed.chapter_id,
                title="Electricity",
                chapter_analysis_id=seed.chapter_analysis_id,
                segment_index_version="p0-v1",
                pipeline_version="p0-p4-v1",
                prompt_version="fixtures-v1",
                model_id="fixture-model",
                pages=["Electric current flows through a closed circuit."],
                named_concepts=[
                    {
                        "concept_id": str(seed.root_concept_entry_id),
                        "label": "Electricity overview",
                        "definition": "A chapter-level entry point.",
                        "category_tag": "overview",
                        "passage_refs": {
                            "definitional": [f"{seed.chapter_id}_para_001"],
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

    client = TestClient(create_app(runtime=runtime))
    token = jwt.encode({"sub": str(user_id)}, jwt_secret, algorithm="HS256")
    client.headers["Authorization"] = f"Bearer {token}"
    return client, runtime, seed


def test_curriculum_endpoints_return_electricity_launch_path():
    client, _, seed = _build_client_runtime_and_seed()

    classes = client.get("/v1/student/curriculum/classes")
    exams = client.get(f"/v1/student/curriculum/exams?class_id={seed.class_level_id}")
    subjects = client.get(
        "/v1/student/curriculum/subjects"
        f"?class_id={seed.class_level_id}&exam_id={seed.exam_id}"
    )
    chapters = client.get(
        "/v1/student/curriculum/chapters"
        f"?class_id={seed.class_level_id}&exam_id={seed.exam_id}&subject_id={seed.subject_id}"
    )
    concept_entries = client.get(
        f"/v1/student/chapters/{seed.chapter_id}/concept-entries"
    )

    assert classes.status_code == 200
    assert exams.status_code == 200
    assert subjects.status_code == 200
    assert chapters.status_code == 200
    assert concept_entries.status_code == 200
    assert classes.json()["items"][0]["label"] == "Class 10"
    assert exams.json()["items"][0]["name"] == "CBSE"
    assert subjects.json()["items"][0]["name"] == "Science"
    assert chapters.json()["items"][0]["title"] == "Electricity"
    assert concept_entries.json()["items"][0]["title"] == "Electricity overview"


def test_chapter_metadata_is_student_safe():
    client, _, seed = _build_client_runtime_and_seed()

    response = client.get(f"/v1/student/chapters/{seed.chapter_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["chapter"]["title"] == "Electricity"
    _assert_no_forbidden_fields(body)


def test_dashboard_without_sessions_shows_electricity_suggestion():
    client, _, _ = _build_client_runtime_and_seed()

    response = client.get("/v1/student/dashboard")

    assert response.status_code == 200
    body = response.json()
    assert body["continue_learning"] is None
    assert body["recent_sessions"] == []
    assert [row["title"] for row in body["launch_suggestions"]] == ["Electricity"]
    _assert_no_forbidden_fields(body)


def test_dashboard_after_session_start_shows_continue_learning_and_recent():
    client, _, seed = _build_client_runtime_and_seed()
    session_response = client.post(
        "/v1/student/sessions",
        json={
            "exam_id": str(seed.exam_id),
            "subject_id": str(seed.subject_id),
            "chapter_id": str(seed.chapter_id),
            "concept_entry_id": str(seed.root_concept_entry_id),
        },
    )

    response = client.get("/v1/student/dashboard")

    assert session_response.status_code == 201
    assert response.status_code == 200
    session_id = session_response.json()["session_id"]
    body = response.json()
    assert body["continue_learning"]["session_id"] == session_id
    assert body["continue_learning"]["chapter_title"] == "Electricity"
    assert [row["session_id"] for row in body["recent_sessions"]] == [session_id]
    _assert_no_forbidden_fields(body)


def _assert_no_forbidden_fields(value: object) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            lowered = key.lower()
            assert not any(fragment in lowered for fragment in FORBIDDEN_ANALYTIC_FIELD_FRAGMENTS)
            _assert_no_forbidden_fields(nested)
    elif isinstance(value, list):
        for item in value:
            _assert_no_forbidden_fields(item)
    elif isinstance(value, UUID):
        return
