"""M4 fixture-backed Electricity session and generation tests.

Traceability:
- docs/planning/sdd/phase-3-m4-curriculum-auth-sdd.md §§8.3, 9, 12.3
- docs/api/student-api-spec.md §§5, 8
- docs/architecture/backend-architecture.md §§6, 7.1, 9-11
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


def test_fixture_provider_has_about_ten_student_safe_nodes():
    """BG provider: Electricity fixture covers the M4 chapter path."""
    from app.generation.fixture_electricity import ElectricityFixtureProvider

    provider = ElectricityFixtureProvider()

    assert 9 <= len(provider.node_keys()) <= 11
    assert provider.node_keys() == [
        "overview",
        "electric-current",
        "potential-difference",
        "ohms-law",
        "resistance",
        "factors-affecting-resistance",
        "series-combination",
        "parallel-combination",
        "heating-effect",
        "electric-power",
    ]


def test_fixture_provider_root_has_required_stamps_and_lineage():
    """BG provider: root output mimics real generation stamps without live LLM."""
    from app.generation.fixture_electricity import ElectricityFixtureProvider

    root = ElectricityFixtureProvider().root()

    assert root.node_key == "overview"
    assert root.node_title == "Electricity - chapter overview"
    assert root.prompt_version == "fixture-electricity-v1"
    assert root.model_id == "fixture"
    assert root.lineage["provider"] == "fixture_electricity_v1"
    assert root.lineage["source"] == "m4_seed"
    _assert_no_forbidden_fields(root.model_dump())


def test_fixture_provider_unknown_path_returns_typed_fallback():
    """BG-6: unknown fixture path returns typed fallback, not an unhandled error."""
    from app.generation.fixture_electricity import ElectricityFixtureProvider

    result = ElectricityFixtureProvider().child_for_choice(
        source_key="unknown",
        selected_option_text="What is drift velocity?",
    )

    assert result.kind == "fallback"
    assert result.node_key == "overview"
    assert result.prompt_version == "fixture-electricity-v1"
    assert result.model_id == "fixture"


def test_start_electricity_session_appends_session_and_root_node():
    """BG-1: starting Electricity creates session_started and root node_created."""
    client, runtime, seed = _build_client_runtime_and_seed()

    response = client.post("/v1/student/sessions", json=_session_body(seed))

    assert response.status_code == 201
    event_types = [event["event_type"] for event in runtime.event_store.events]
    assert event_types == ["consent_recorded", "session_started", "node_created"]
    root_event = runtime.event_store.events[-1]
    assert root_event["payload"]["content"].startswith("Electricity studies")
    UUID(root_event["payload"]["source_offer_set_id"])
    UUID(root_event["payload"]["source_option_id"])
    assert root_event["payload"]["fixture_node_key"] == "overview"
    assert root_event["payload"]["prompt_version"] == "fixture-electricity-v1"
    assert root_event["payload"]["model_id"] == "fixture"


def test_start_electricity_session_persists_worker_visible_consent():
    """PR-6: the consent event and consent entity cannot diverge."""
    client, runtime, seed = _build_client_runtime_and_seed()

    first = client.post("/v1/student/sessions", json=_session_body(seed))
    second = client.post("/v1/student/sessions", json=_session_body(seed))

    assert first.status_code == 201
    assert second.status_code == 201
    assert runtime.consent_records.has_valid_behavioral_analytics(
        tenant_id=runtime.tenant_id,
        student_user_id=runtime.student_user_id,
    )
    consent_events = [
        event for event in runtime.event_store.events if event["event_type"] == "consent_recorded"
    ]
    assert len(consent_events) == 1
    assert len(runtime.consent_records.records) == 1


def test_fetch_session_after_start_contains_root_canvas_node():
    """BG-2: GET /sessions/{id} hydrates root fixture node."""
    client, _, seed = _build_client_runtime_and_seed()
    start_response = client.post("/v1/student/sessions", json=_session_body(seed))
    session_id = start_response.json()["session_id"]

    response = client.get(f"/v1/student/sessions/{session_id}")

    assert response.status_code == 200
    nodes = response.json()["canvas"]["nodes"]
    assert len(nodes) == 1
    assert nodes[0]["node_type"] == "ai"
    assert nodes[0]["content"].startswith("Electricity studies")
    _assert_no_forbidden_fields(response.json())


def test_selected_offer_choice_from_root_uses_fixture_child_node():
    """BG-3: selected edge from fixture root creates the next Electricity node."""
    client, runtime, seed = _build_client_runtime_and_seed()
    start_response = client.post("/v1/student/sessions", json=_session_body(seed))
    session_id = start_response.json()["session_id"]
    root_event = runtime.event_store.events[-1]
    offer_set_id = uuid4()
    option_id = uuid4()

    response = client.post(
        f"/v1/student/offer-sets/{offer_set_id}/choices",
        json={
            "session_id": session_id,
            "source_node_id": str(root_event["node_id"]),
            "outcome": "selected",
            "selected_option_id": str(option_id),
            "selected_option_text": "What is electric current?",
            "thread_context_id": str(seed.root_concept_entry_id),
        },
    )

    assert response.status_code == 202
    body = response.json()
    assert body["child_content"].startswith("Electric current is the rate")
    node_events = [event for event in runtime.event_store.events if event["event_type"] == "node_created"]
    child_payload = node_events[-1]["payload"]
    assert child_payload["fixture_node_key"] == "electric-current"
    assert child_payload["prompt_version"] == "fixture-electricity-v1"
    assert child_payload["model_id"] == "fixture"
    assert child_payload["lineage"]["provider"] == "fixture_electricity_v1"
    _assert_no_forbidden_fields(body)


def test_fixture_provider_marks_terminal_node_at_end_of_chapter():
    """BG-5: final Electricity fixture path is explicitly marked complete."""
    from app.generation.fixture_electricity import ElectricityFixtureProvider

    result = ElectricityFixtureProvider().child_for_choice(
        source_key="electric-power",
        selected_option_text="What should I study next?",
    )

    assert result.node_key == "electric-power"
    assert result.is_terminal is True
    assert result.lineage["completion_state"] == "terminal"


def _assert_no_forbidden_fields(value: object) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            lowered = key.lower()
            assert not any(fragment in lowered for fragment in FORBIDDEN_ANALYTIC_FIELD_FRAGMENTS)
            _assert_no_forbidden_fields(nested)
    elif isinstance(value, list):
        for item in value:
            _assert_no_forbidden_fields(item)


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


def _session_body(seed) -> dict[str, str | bool]:
    return {
        "exam_id": str(seed.exam_id),
        "subject_id": str(seed.subject_id),
        "chapter_id": str(seed.chapter_id),
        "concept_entry_id": str(seed.root_concept_entry_id),
        "behavioral_analytics_consent": True,
    }
