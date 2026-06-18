import re
from uuid import UUID

TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
EXAM_ID = UUID("22222222-2222-2222-2222-222222222222")
SUBJECT_ID = UUID("33333333-3333-3333-3333-333333333333")
CHAPTER_ID = UUID("44444444-4444-4444-4444-444444444444")
CHAPTER_ANALYSIS_ID = UUID("55555555-5555-5555-5555-555555555555")
SEGMENT_ID_PATTERN = re.compile(rf"^{CHAPTER_ID}_(para|question)_[0-9]{{3}}$")


def _fixture_input():
    from app.projections.curriculum import CurriculumIngestInput

    return CurriculumIngestInput(
        tenant_id=TENANT_ID,
        exam_id=EXAM_ID,
        subject_id=SUBJECT_ID,
        chapter_id=CHAPTER_ID,
        title="Electricity",
        chapter_analysis_id=CHAPTER_ANALYSIS_ID,
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
                    "definitional": [f"{CHAPTER_ID}_para_001"],
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
                    "definitional": [f"{CHAPTER_ID}_para_001"],
                    "explanatory": [],
                    "application": [f"{CHAPTER_ID}_question_001"],
                },
            },
        ],
        embedded_concepts=[
            {
                "concept_id": "electric_currents",
                "label": "electric currents",
                "definition": "Movement of charge through a path.",
                "category_tag": "quantity",
                "passage_refs": {
                    "definitional": [],
                    "explanatory": [f"{CHAPTER_ID}_para_001"],
                    "application": [f"{CHAPTER_ID}_question_001"],
                },
            }
        ],
        edges=[
            {
                "from_concept": "electric_current",
                "to_concept": "circuit",
                "type": "CONNECTS",
                "passage_support": [f"{CHAPTER_ID}_question_001"],
                "rationale": "The question connects current to circuits.",
            }
        ],
    )


def test_curriculum_ingest_is_idempotent_on_reingest() -> None:
    """SDD §9 T6: re-ingesting the same chapter must not duplicate curriculum rows."""
    from app.projections.curriculum import InMemoryCurriculumStore, build_curriculum_rows

    store = InMemoryCurriculumStore()
    rows = build_curriculum_rows(_fixture_input())

    store.ingest(rows)
    first_counts = store.row_counts()
    store.ingest(rows)

    assert store.row_counts() == first_counts
    assert first_counts == {"chapters": 1, "segments": 2, "concepts": 2, "concept_edges": 1}


def test_curriculum_ingest_rebuild_is_byte_identical() -> None:
    """SDD §9 T7: same fixture inputs must rebuild byte-identical curriculum rows."""
    from app.projections.curriculum import InMemoryCurriculumStore, build_curriculum_rows

    first = InMemoryCurriculumStore()
    second = InMemoryCurriculumStore()

    first.ingest(build_curriculum_rows(_fixture_input()))
    second.ingest(build_curriculum_rows(_fixture_input()))

    assert first.snapshot_bytes() == second.snapshot_bytes()


def test_curriculum_rows_carry_tenant_and_chapter_analysis_id() -> None:
    """SDD §9 T8: every curriculum row carries tenant, analysis id, and version stamps."""
    from app.projections.curriculum import build_curriculum_rows

    rows = build_curriculum_rows(_fixture_input())

    for table_rows in rows.values():
        for row in table_rows:
            assert row["tenant_id"] == TENANT_ID
            assert row["chapter_analysis_id"] == CHAPTER_ANALYSIS_ID
            assert row["pipeline_version"] == "chapter-analysis-p0-p4-v1"

    assert rows["chapters"][0]["segment_index_version"] == "segment-index-v1"
    assert rows["chapters"][0]["source_doc_hash"]
    assert rows["concepts"][0]["prompt_version"] == "chapter-analysis-p1p2p4-fixture-v1"
    assert rows["concept_edges"][0]["model_id"] == "recorded-fixture-model"


def test_curriculum_segment_ids_follow_p0_convention() -> None:
    """Pipeline spec P0: segment IDs must be [chapter_id]_[segment_type]_[NNN]."""
    from app.projections.curriculum import build_curriculum_rows

    rows = build_curriculum_rows(_fixture_input())

    assert rows["segments"]
    for segment in rows["segments"]:
        segment_id = str(segment["segment_id"])
        assert SEGMENT_ID_PATTERN.fullmatch(segment_id)
        assert segment_id.startswith(f"{segment['chapter_id']}_")


def test_curriculum_segment_rows_include_nullable_location_for_postgres_adapter() -> None:
    """Pipeline spec P0: segment rows always carry location, null for non-question rows."""
    from app.projections.curriculum import build_curriculum_rows

    rows = build_curriculum_rows(_fixture_input())

    para_segment = next(
        segment for segment in rows["segments"] if segment["segment_type"] == "para"
    )
    question_segment = next(
        segment for segment in rows["segments"] if segment["segment_type"] == "question"
    )

    assert para_segment["location"] is None
    assert question_segment["location"] == "in_text"
