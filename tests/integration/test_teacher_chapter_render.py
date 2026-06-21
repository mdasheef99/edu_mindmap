"""Teacher Dashboard V1 render endpoint tests for Phase 2."""

from uuid import uuid4

import jwt
from fastapi.testclient import TestClient

FORBIDDEN_PER_STUDENT_FIELD_FRAGMENTS = (
    "student",
    "classification",
    "coverage",
    "gap",
    "score",
    "confidence",
    "entropy",
    "vector",
    "profile",
    "propensity",
    "probe",
)


def _build_client_and_runtime(jwt_secret: str = "test-secret"):
    from app.main import SessionRuntime, create_app

    tenant_id = uuid4()
    teacher_user_id = uuid4()
    runtime = SessionRuntime.for_testing(
        tenant_id=tenant_id,
        student_user_id=uuid4(),
        jwt_secret=jwt_secret,
    )
    runtime.memberships.add_membership(
        user_id=teacher_user_id,
        tenant_id=tenant_id,
        role="teacher",
    )
    client = TestClient(create_app(runtime=runtime))
    token = jwt.encode({"sub": str(teacher_user_id)}, jwt_secret, algorithm="HS256")
    client.headers["Authorization"] = f"Bearer {token}"
    return client, runtime


def _seed_curriculum(runtime):
    from app.projections.curriculum import CurriculumIngestInput, build_curriculum_rows

    chapter_id = uuid4()
    chapter_analysis_id = uuid4()
    runtime.curriculum.ingest(
        build_curriculum_rows(
            CurriculumIngestInput(
                tenant_id=runtime.tenant_id,
                exam_id=uuid4(),
                subject_id=uuid4(),
                chapter_id=chapter_id,
                title="Electricity",
                chapter_analysis_id=chapter_analysis_id,
                segment_index_version="segment-index-v1",
                pipeline_version="chapter-analysis-p0-p4-v1",
                prompt_version="chapter-analysis-p1p2p4-fixture-v1",
                model_id="recorded-fixture-model",
                pages=["Electric current is charge flow.\n\nWhy does current need a circuit?"],
                named_concepts=[
                    {
                        "concept_id": "electric_current",
                        "label": "Electric current",
                        "definition": "Rate of flow of charge.",
                        "category_tag": "quantity",
                        "passage_refs": {
                            "definitional": [f"{chapter_id}_para_001"],
                            "explanatory": [],
                            "application": [],
                        },
                    },
                    {
                        "concept_id": "circuit",
                        "label": "Circuit",
                        "definition": "A closed path for electric current.",
                        "category_tag": "structure",
                        "passage_refs": {
                            "definitional": [f"{chapter_id}_para_001"],
                            "explanatory": [],
                            "application": [f"{chapter_id}_question_001"],
                        },
                    },
                ],
                embedded_concepts=[],
                edges=[
                    {
                        "from_concept": "electric_current",
                        "to_concept": "circuit",
                        "type": "CONNECTS",
                        "passage_support": [f"{chapter_id}_question_001"],
                        "rationale": "The question connects current to circuits.",
                    }
                ],
            )
        )
    )
    return str(chapter_id), str(chapter_analysis_id)


def _flatten_keys(value):
    if isinstance(value, dict):
        for key, nested in value.items():
            yield str(key)
            yield from _flatten_keys(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _flatten_keys(nested)


def test_teacher_chapter_render_returns_ingested_graph_without_per_student_fields() -> None:
    """SDD §9 T15: teacher render returns curriculum graph with no per-student fields."""
    client, runtime = _build_client_and_runtime()
    chapter_id, chapter_analysis_id = _seed_curriculum(runtime)

    response = client.get(f"/v1/teacher/chapters/{chapter_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["chapter_id"] == chapter_id
    assert body["chapter_analysis_id"] == chapter_analysis_id
    assert body["title"] == "Electricity"
    assert body["concepts"]
    assert body["edges"]
    assert all("text" not in segment for segment in body["segments"])
    assert not any(
        forbidden in key
        for key in _flatten_keys(body)
        for forbidden in FORBIDDEN_PER_STUDENT_FIELD_FRAGMENTS
    )


def test_teacher_chapter_render_requires_teacher_role() -> None:
    """Teacher render is not available to student memberships."""
    client, runtime = _build_client_and_runtime()
    chapter_id, _ = _seed_curriculum(runtime)
    student_user_id = uuid4()
    runtime.memberships.add_membership(
        user_id=student_user_id,
        tenant_id=runtime.tenant_id,
        role="student",
    )
    token = jwt.encode({"sub": str(student_user_id)}, runtime.jwt_secret, algorithm="HS256")

    response = client.get(
        f"/v1/teacher/chapters/{chapter_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
