"""Postgres-backed curriculum schema adapter.

Traceability:
- docs/planning/sdd/phase-2-curriculum-ingestion-sdd.md §§6, 8-10
- docs/architecture/backend-architecture.md §§5.3, 7.5, 10
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any

from app.tenancy.postgres_context import set_local_tenant

UPSERT_CHAPTER_SQL = """
INSERT INTO curriculum.chapters (
    chapter_id, tenant_id, exam_id, subject_id, title, chapter_analysis_id,
    source_doc_hash, segment_index_version, pipeline_version
) VALUES (
    %(chapter_id)s, %(tenant_id)s, %(exam_id)s, %(subject_id)s, %(title)s,
    %(chapter_analysis_id)s, %(source_doc_hash)s, %(segment_index_version)s,
    %(pipeline_version)s
)
ON CONFLICT (chapter_id) DO UPDATE SET
    tenant_id = EXCLUDED.tenant_id,
    exam_id = EXCLUDED.exam_id,
    subject_id = EXCLUDED.subject_id,
    title = EXCLUDED.title,
    chapter_analysis_id = EXCLUDED.chapter_analysis_id,
    source_doc_hash = EXCLUDED.source_doc_hash,
    segment_index_version = EXCLUDED.segment_index_version,
    pipeline_version = EXCLUDED.pipeline_version
"""

UPSERT_SEGMENT_SQL = """
INSERT INTO curriculum.segments (
    segment_id, chapter_id, tenant_id, chapter_analysis_id, segment_type, text,
    page, char_span, location, pipeline_version
) VALUES (
    %(segment_id)s, %(chapter_id)s, %(tenant_id)s, %(chapter_analysis_id)s,
    %(segment_type)s, %(text)s, %(page)s, %(char_span)s::jsonb,
    %(location)s, %(pipeline_version)s
)
ON CONFLICT (segment_id) DO UPDATE SET
    chapter_id = EXCLUDED.chapter_id,
    tenant_id = EXCLUDED.tenant_id,
    chapter_analysis_id = EXCLUDED.chapter_analysis_id,
    segment_type = EXCLUDED.segment_type,
    text = EXCLUDED.text,
    page = EXCLUDED.page,
    char_span = EXCLUDED.char_span,
    location = EXCLUDED.location,
    pipeline_version = EXCLUDED.pipeline_version
"""

UPSERT_CONCEPT_SQL = """
INSERT INTO curriculum.concepts (
    concept_id, chapter_id, tenant_id, chapter_analysis_id, label, definition,
    category_tag, passage_refs, merged_from, pipeline_version, prompt_version, model_id
) VALUES (
    %(concept_id)s, %(chapter_id)s, %(tenant_id)s, %(chapter_analysis_id)s,
    %(label)s, %(definition)s, %(category_tag)s, %(passage_refs)s::jsonb,
    %(merged_from)s::jsonb, %(pipeline_version)s, %(prompt_version)s, %(model_id)s
)
ON CONFLICT (concept_id) DO UPDATE SET
    chapter_id = EXCLUDED.chapter_id,
    tenant_id = EXCLUDED.tenant_id,
    chapter_analysis_id = EXCLUDED.chapter_analysis_id,
    label = EXCLUDED.label,
    definition = EXCLUDED.definition,
    category_tag = EXCLUDED.category_tag,
    passage_refs = EXCLUDED.passage_refs,
    merged_from = EXCLUDED.merged_from,
    pipeline_version = EXCLUDED.pipeline_version,
    prompt_version = EXCLUDED.prompt_version,
    model_id = EXCLUDED.model_id
"""

UPSERT_EDGE_SQL = """
INSERT INTO curriculum.concept_edges (
    edge_id, chapter_id, tenant_id, chapter_analysis_id, edge_kind,
    from_concept_id, to_concept_id, passage_support, rationale,
    pipeline_version, prompt_version, model_id
) VALUES (
    %(edge_id)s, %(chapter_id)s, %(tenant_id)s, %(chapter_analysis_id)s,
    %(edge_kind)s, %(from_concept_id)s, %(to_concept_id)s,
    %(passage_support)s::jsonb, %(rationale)s, %(pipeline_version)s,
    %(prompt_version)s, %(model_id)s
)
ON CONFLICT (edge_id) DO UPDATE SET
    chapter_id = EXCLUDED.chapter_id,
    tenant_id = EXCLUDED.tenant_id,
    chapter_analysis_id = EXCLUDED.chapter_analysis_id,
    edge_kind = EXCLUDED.edge_kind,
    from_concept_id = EXCLUDED.from_concept_id,
    to_concept_id = EXCLUDED.to_concept_id,
    passage_support = EXCLUDED.passage_support,
    rationale = EXCLUDED.rationale,
    pipeline_version = EXCLUDED.pipeline_version,
    prompt_version = EXCLUDED.prompt_version,
    model_id = EXCLUDED.model_id
"""

FIND_CHAPTER_SQL = """
SELECT *
FROM curriculum.chapters
WHERE tenant_id = %(tenant_id)s
  AND exam_id = %(exam_id)s
  AND subject_id = %(subject_id)s
  AND chapter_id = %(chapter_id)s
"""


class PostgresCurriculumStore:
    """Tenant-scoped adapter for migration 0004 `curriculum` tables."""

    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def ingest(self, rows: Mapping[str, Sequence[Mapping[str, object]]]) -> None:
        tenant_id = _tenant_id_from(rows)
        with self.connection.transaction():
            set_local_tenant(self.connection, tenant_id)
            _execute_many(self.connection, UPSERT_CHAPTER_SQL, rows.get("chapters", ()))
            _execute_many(self.connection, UPSERT_SEGMENT_SQL, rows.get("segments", ()))
            _execute_many(self.connection, UPSERT_CONCEPT_SQL, rows.get("concepts", ()))
            _execute_many(self.connection, UPSERT_EDGE_SQL, rows.get("concept_edges", ()))

    def find_chapter(
        self, *, tenant_id: Any, exam_id: Any, subject_id: Any, chapter_id: Any
    ) -> dict[str, Any] | None:
        params = {
            "tenant_id": tenant_id,
            "exam_id": exam_id,
            "subject_id": subject_id,
            "chapter_id": chapter_id,
        }
        with self.connection.transaction():
            set_local_tenant(self.connection, tenant_id)
            cursor = self.connection.execute(FIND_CHAPTER_SQL, params)
            row = cursor.fetchone()
        return None if row is None else _row_to_dict(row)


def _execute_many(connection: Any, sql: str, rows: Sequence[Mapping[str, object]]) -> None:
    for row in rows:
        connection.execute(sql, _json_params(row))


def _json_params(row: Mapping[str, object]) -> dict[str, object]:
    params = dict(row)
    for key in ("char_span", "passage_refs", "merged_from", "passage_support"):
        if key in params:
            params[key] = json.dumps(params[key], default=str)
    return params


def _tenant_id_from(rows: Mapping[str, Sequence[Mapping[str, object]]]) -> object:
    for table_rows in rows.values():
        for row in table_rows:
            return row["tenant_id"]
    raise ValueError("curriculum ingest requires at least one row")


def _row_to_dict(row: Any) -> dict[str, Any]:
    if isinstance(row, Mapping):
        return dict(row)
    if hasattr(row, "_asdict"):
        return dict(row._asdict())
    return dict(row)
