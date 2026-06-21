import os
from pathlib import Path
from uuid import uuid4

import pytest

PDF_FIXTURE_PATH = Path(__file__).resolve().parents[2] / "docs" / "research" / "electricity.pdf"


def _test_database_url_missing() -> bool:
    return os.getenv("TEST_DATABASE_URL") is None


@pytest.mark.skipif(
    _test_database_url_missing(),
    reason="Requires explicit TEST_DATABASE_URL for non-bypass real chapter ingest proof.",
)
def test_real_electricity_chapter_ingests_through_non_bypass_postgres_role() -> None:
    """SDD §8 L4/L5: real PDF + fixture P1/P2/P4 rows persist under tenant RLS."""
    psycopg = pytest.importorskip("psycopg")
    from app.chapter_analysis.merge import merge_concept_records
    from app.chapter_analysis.passes import (
        run_p1_named_concept_extraction,
        run_p2_embedded_concept_extraction,
        run_p4_relationship_extraction,
    )
    from app.chapter_analysis.segments import extract_pdf_pages, segment_chapter_text
    from app.llm_gateway.usage import InMemoryLLMUsageStore
    from app.projections.curriculum import (
        CurriculumIngestInput,
        PostgresCurriculumStore,
        build_curriculum_rows,
    )
    from app.tenancy.postgres_context import set_local_tenant
    from psycopg.rows import dict_row

    tenant_id = uuid4()
    exam_id = uuid4()
    subject_id = uuid4()
    chapter_id = uuid4()
    chapter_analysis_id = uuid4()
    pages = extract_pdf_pages(PDF_FIXTURE_PATH.read_bytes())
    segments = segment_chapter_text(str(chapter_id), pages)
    usage_store = InMemoryLLMUsageStore()

    p1 = run_p1_named_concept_extraction(segments, tenant_id=tenant_id, usage_store=usage_store)
    p2 = run_p2_embedded_concept_extraction(
        segments,
        p1["concepts"],
        tenant_id=tenant_id,
        usage_store=usage_store,
    )
    merged = merge_concept_records(p1["concepts"], p2["concepts"])
    p4 = run_p4_relationship_extraction(
        segments, merged, tenant_id=tenant_id, usage_store=usage_store
    )
    rows = build_curriculum_rows(
        CurriculumIngestInput(
            tenant_id=tenant_id,
            exam_id=exam_id,
            subject_id=subject_id,
            chapter_id=chapter_id,
            title="Electricity",
            chapter_analysis_id=chapter_analysis_id,
            segment_index_version="segment-index-v1",
            pipeline_version="chapter-analysis-p0-p4-v1",
            prompt_version="chapter-analysis-p1p2p4-fixture-v1",
            model_id=str(p1["model_id"]),
            pages=pages,
            named_concepts=p1["concepts"],
            embedded_concepts=p2["concepts"],
            edges=p4["edges"],
        )
    )

    conn = psycopg.connect(os.environ["TEST_DATABASE_URL"], row_factory=dict_row)
    try:
        if _current_role_bypasses_rls(conn):
            pytest.skip("TEST_DATABASE_URL role bypasses RLS; use a non-bypass app role.")
        if _curriculum_schema_missing(conn):
            pytest.skip(
                "TEST_DATABASE_URL database has not applied migration 0004 curriculum schema."
            )
        conn.execute("BEGIN")
        try:
            set_local_tenant(conn, tenant_id)
            conn.execute(
                "INSERT INTO public.tenants (tenant_id, kind, name) "
                "VALUES (%s, 'institutional', %s)",
                (tenant_id, "real electricity ingest test"),
            )
            store = PostgresCurriculumStore(conn)
            store.ingest(rows)
            found = store.find_chapter(
                tenant_id=tenant_id,
                exam_id=exam_id,
                subject_id=subject_id,
                chapter_id=chapter_id,
            )

            assert found is not None
            assert found["chapter_analysis_id"] == chapter_analysis_id
            assert len(usage_store.records) == 3
        finally:
            conn.rollback()
    finally:
        conn.close()


def _current_role_bypasses_rls(conn) -> bool:
    row = conn.execute(
        "SELECT rolsuper OR rolbypassrls AS bypasses_rls FROM pg_roles WHERE rolname = current_user"
    ).fetchone()
    return bool(row["bypasses_rls"])


def _curriculum_schema_missing(conn) -> bool:
    row = conn.execute("SELECT to_regclass('curriculum.chapters') AS chapters_table").fetchone()
    return row["chapters_table"] is None
