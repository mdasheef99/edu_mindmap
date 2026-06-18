from uuid import UUID

TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
EXAM_ID = UUID("22222222-2222-2222-2222-222222222222")
SUBJECT_ID = UUID("33333333-3333-3333-3333-333333333333")
CHAPTER_ID = UUID("44444444-4444-4444-4444-444444444444")
CHAPTER_ANALYSIS_ID = UUID("55555555-5555-5555-5555-555555555555")


class _Cursor:
    def __init__(self, row=None) -> None:
        self._row = row

    def fetchone(self):
        return self._row


class _Transaction:
    def __init__(self, connection) -> None:
        self.connection = connection

    def __enter__(self):
        self.connection.transactions += 1
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None


class _Connection:
    def __init__(self, *, row=None) -> None:
        self.calls = []
        self.row = row
        self.transactions = 0

    def transaction(self):
        return _Transaction(self)

    def execute(self, sql, params=None):
        self.calls.append((sql, params))
        return _Cursor(self.row)


def _rows() -> dict[str, list[dict[str, object]]]:
    return {
        "chapters": [
            {
                "chapter_id": CHAPTER_ID,
                "tenant_id": TENANT_ID,
                "exam_id": EXAM_ID,
                "subject_id": SUBJECT_ID,
                "title": "Electricity",
                "chapter_analysis_id": CHAPTER_ANALYSIS_ID,
                "source_doc_hash": "abc123",
                "segment_index_version": "segment-index-v1",
                "pipeline_version": "chapter-analysis-p0-p4-v1",
            }
        ],
        "segments": [
            {
                "segment_id": f"{CHAPTER_ID}_para_001",
                "chapter_id": CHAPTER_ID,
                "tenant_id": TENANT_ID,
                "chapter_analysis_id": CHAPTER_ANALYSIS_ID,
                "segment_type": "paragraph",
                "text": "Electric current is charge flow.",
                "page": 1,
                "char_span": {"start": 0, "end": 32},
                "location": None,
                "pipeline_version": "chapter-analysis-p0-p4-v1",
            }
        ],
        "concepts": [
            {
                "concept_id": "electric_current",
                "chapter_id": CHAPTER_ID,
                "tenant_id": TENANT_ID,
                "chapter_analysis_id": CHAPTER_ANALYSIS_ID,
                "label": "Electric current",
                "definition": "Rate of flow of charge.",
                "category_tag": "quantity",
                "passage_refs": {"definitional": [f"{CHAPTER_ID}_para_001"]},
                "merged_from": [],
                "pipeline_version": "chapter-analysis-p0-p4-v1",
                "prompt_version": "fixture-v1",
                "model_id": "fixture-model",
            }
        ],
        "concept_edges": [
            {
                "edge_id": "edge_001",
                "chapter_id": CHAPTER_ID,
                "tenant_id": TENANT_ID,
                "chapter_analysis_id": CHAPTER_ANALYSIS_ID,
                "edge_kind": "CONNECTS",
                "from_concept_id": "electric_current",
                "to_concept_id": "electric_current",
                "passage_support": [f"{CHAPTER_ID}_para_001"],
                "rationale": "Fixture relation.",
                "pipeline_version": "chapter-analysis-p0-p4-v1",
                "prompt_version": "fixture-v1",
                "model_id": "fixture-model",
            }
        ],
    }


def test_postgres_curriculum_store_upserts_all_tables_under_tenant_context() -> None:
    """SDD §8 L2/§10: curriculum persistence must be idempotent and tenant-scoped."""
    from app.projections.curriculum import PostgresCurriculumStore

    connection = _Connection()
    store = PostgresCurriculumStore(connection)

    store.ingest(_rows())

    executed_sql = "\n".join(sql.lower() for sql, _ in connection.calls)
    assert connection.transactions == 1
    assert "set_config('app.tenant_id'" in executed_sql
    assert "insert into curriculum.chapters" in executed_sql
    assert "insert into curriculum.segments" in executed_sql
    assert "insert into curriculum.concepts" in executed_sql
    assert "insert into curriculum.concept_edges" in executed_sql
    assert "on conflict" in executed_sql


def test_postgres_curriculum_store_finds_chapter_for_launch_under_tenant_context() -> None:
    """SDD §9 T14: session launch lookup reads curriculum through resolved tenant context."""
    from app.projections.curriculum import PostgresCurriculumStore

    expected = _rows()["chapters"][0]
    connection = _Connection(row=expected)
    store = PostgresCurriculumStore(connection)

    found = store.find_chapter(
        tenant_id=TENANT_ID,
        exam_id=EXAM_ID,
        subject_id=SUBJECT_ID,
        chapter_id=CHAPTER_ID,
    )

    executed_sql = "\n".join(sql.lower() for sql, _ in connection.calls)
    assert found == expected
    assert connection.transactions == 1
    assert "set_config('app.tenant_id'" in executed_sql
    assert "from curriculum.chapters" in executed_sql
    assert "tenant_id" in executed_sql
