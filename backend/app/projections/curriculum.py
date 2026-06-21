"""Curriculum schema ingest builder for Phase 2 chapter analysis outputs.

Traceability:
- docs/planning/sdd/phase-2-curriculum-ingestion-sdd.md §§8-10
- docs/architecture/backend-architecture.md §7.5
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping, MutableMapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from app.chapter_analysis.edges import assign_edge_ids
from app.chapter_analysis.merge import merge_concept_records
from app.chapter_analysis.segments import segment_chapter_text
from app.chapter_analysis.verification import verify_cited_segment_ids
from app.domain.curriculum import TeacherChapterGraph
from app.projections.curriculum_postgres import PostgresCurriculumStore

CurriculumRows = dict[str, list[dict[str, object]]]

__all__ = [
    "CurriculumIngestInput",
    "InMemoryCurriculumStore",
    "PostgresCurriculumStore",
    "build_curriculum_rows",
]


@dataclass(frozen=True)
class CurriculumIngestInput:
    tenant_id: UUID
    exam_id: UUID
    subject_id: UUID
    chapter_id: UUID
    title: str
    chapter_analysis_id: UUID
    segment_index_version: str
    pipeline_version: str
    prompt_version: str | None
    model_id: str | None
    pages: Sequence[str]
    named_concepts: Sequence[dict[str, object]]
    embedded_concepts: Sequence[dict[str, object]]
    edges: Sequence[dict[str, object]]


class InMemoryCurriculumStore:
    """Deterministic in-memory stand-in for curriculum.* table upserts."""

    def __init__(self) -> None:
        self.chapters: dict[str, dict[str, object]] = {}
        self.segments: dict[str, dict[str, object]] = {}
        self.concepts: dict[str, dict[str, object]] = {}
        self.concept_edges: dict[str, dict[str, object]] = {}

    def ingest(self, rows: Mapping[str, Sequence[Mapping[str, object]]]) -> None:
        _upsert_many(self.chapters, rows.get("chapters", ()), "chapter_id")
        _upsert_many(self.segments, rows.get("segments", ()), "segment_id")
        _upsert_many(self.concepts, rows.get("concepts", ()), "concept_id")
        _upsert_many(self.concept_edges, rows.get("concept_edges", ()), "edge_id")

    def row_counts(self) -> dict[str, int]:
        return {
            "chapters": len(self.chapters),
            "segments": len(self.segments),
            "concepts": len(self.concepts),
            "concept_edges": len(self.concept_edges),
        }

    def find_chapter(
        self,
        *,
        tenant_id: UUID,
        exam_id: UUID,
        subject_id: UUID,
        chapter_id: UUID,
    ) -> dict[str, object] | None:
        chapter = self.chapters.get(str(chapter_id))
        if chapter is None:
            return None
        if (
            chapter["tenant_id"] != tenant_id
            or chapter["exam_id"] != exam_id
            or chapter["subject_id"] != subject_id
        ):
            return None
        return deepcopy(chapter)

    def render_chapter_graph(
        self, *, tenant_id: UUID, chapter_id: UUID
    ) -> TeacherChapterGraph | None:
        chapter = self.chapters.get(str(chapter_id))
        if chapter is None or chapter["tenant_id"] != tenant_id:
            return None

        segments = [
            _teacher_segment(row)
            for row in self.segments.values()
            if row["tenant_id"] == tenant_id and row["chapter_id"] == chapter_id
        ]
        concepts = [
            _teacher_concept(row)
            for row in self.concepts.values()
            if row["tenant_id"] == tenant_id and row["chapter_id"] == chapter_id
        ]
        edges = [
            _teacher_edge(row)
            for row in self.concept_edges.values()
            if row["tenant_id"] == tenant_id and row["chapter_id"] == chapter_id
        ]
        return TeacherChapterGraph.model_validate(
            {
                "chapter_id": chapter["chapter_id"],
                "chapter_analysis_id": chapter["chapter_analysis_id"],
                "title": chapter["title"],
                "segment_index_version": chapter["segment_index_version"],
                "pipeline_version": chapter["pipeline_version"],
                "segments": sorted(segments, key=lambda row: row["segment_id"]),
                "concepts": sorted(concepts, key=lambda row: row["concept_id"]),
                "edges": sorted(edges, key=lambda row: row["edge_id"]),
            }
        )

    def snapshot_bytes(self) -> bytes:
        payload = {
            "chapters": self.chapters,
            "segments": self.segments,
            "concepts": self.concepts,
            "concept_edges": self.concept_edges,
        }
        return json.dumps(payload, sort_keys=True, default=_json_default).encode("utf-8")


def build_curriculum_rows(source: CurriculumIngestInput) -> CurriculumRows:
    """Build curriculum.* row dictionaries from deterministic P0-P4 fixture outputs."""

    segments = segment_chapter_text(str(source.chapter_id), source.pages)
    concepts = merge_concept_records(source.named_concepts, source.embedded_concepts)
    _verify_concept_refs(concepts, segments)

    enriched_edges = assign_edge_ids(source.edges)
    _verify_edge_refs(enriched_edges, segments, concepts)

    return {
        "chapters": [_chapter_row(source)],
        "segments": [_segment_row(source, segment) for segment in segments],
        "concepts": [
            _concept_row(source, concept) for concept in sorted(concepts, key=_concept_id)
        ],
        "concept_edges": [_edge_row(source, edge) for edge in sorted(enriched_edges, key=_edge_id)],
    }


def _chapter_row(source: CurriculumIngestInput) -> dict[str, object]:
    return {
        "chapter_id": source.chapter_id,
        "tenant_id": source.tenant_id,
        "exam_id": source.exam_id,
        "subject_id": source.subject_id,
        "title": source.title,
        "chapter_analysis_id": source.chapter_analysis_id,
        "source_doc_hash": hashlib.sha256("\f".join(source.pages).encode()).hexdigest(),
        "segment_index_version": source.segment_index_version,
        "pipeline_version": source.pipeline_version,
    }


def _segment_row(source: CurriculumIngestInput, segment: Mapping[str, object]) -> dict[str, object]:
    return dict(segment) | {
        "chapter_id": source.chapter_id,
        "tenant_id": source.tenant_id,
        "chapter_analysis_id": source.chapter_analysis_id,
        "location": segment.get("location"),
        "pipeline_version": source.pipeline_version,
    }


def _concept_row(source: CurriculumIngestInput, concept: Mapping[str, object]) -> dict[str, object]:
    return {
        "concept_id": concept["concept_id"],
        "chapter_id": source.chapter_id,
        "tenant_id": source.tenant_id,
        "chapter_analysis_id": source.chapter_analysis_id,
        "label": concept["label"],
        "definition": concept["definition"],
        "category_tag": concept["category_tag"],
        "passage_refs": concept.get("passage_refs", {}),
        "merged_from": concept.get("merged_from", []),
        "pipeline_version": source.pipeline_version,
        "prompt_version": source.prompt_version,
        "model_id": source.model_id,
    }


def _edge_row(source: CurriculumIngestInput, edge: Mapping[str, object]) -> dict[str, object]:
    return {
        "edge_id": edge["edge_id"],
        "chapter_id": source.chapter_id,
        "tenant_id": source.tenant_id,
        "chapter_analysis_id": source.chapter_analysis_id,
        "edge_kind": edge["type"],
        "from_concept_id": edge["from_concept"],
        "to_concept_id": edge["to_concept"],
        "passage_support": edge.get("passage_support", []),
        "rationale": edge.get("rationale"),
        "pipeline_version": source.pipeline_version,
        "prompt_version": source.prompt_version,
        "model_id": source.model_id,
    }


def _verify_concept_refs(
    concepts: Sequence[Mapping[str, object]], segments: Sequence[Mapping[str, object]]
) -> None:
    verify_cited_segment_ids(_passage_ref_values(concepts), segments)


def _verify_edge_refs(
    edges: Sequence[Mapping[str, object]],
    segments: Sequence[Mapping[str, object]],
    concepts: Sequence[Mapping[str, object]],
) -> None:
    concept_ids = {str(concept["concept_id"]) for concept in concepts}
    for edge in edges:
        missing_from = str(edge["from_concept"]) not in concept_ids
        missing_to = str(edge["to_concept"]) not in concept_ids
        if missing_from or missing_to:
            raise ValueError("Concept edge references unknown concept ids")
    verify_cited_segment_ids(_edge_ref_values(edges), segments)


def _passage_ref_values(concepts: Iterable[Mapping[str, object]]) -> list[str]:
    refs: list[str] = []
    for concept in concepts:
        passage_refs = concept.get("passage_refs", {})
        if isinstance(passage_refs, dict):
            for values in passage_refs.values():
                if isinstance(values, list):
                    refs.extend(str(value) for value in values)
    return refs


def _edge_ref_values(edges: Iterable[Mapping[str, object]]) -> list[str]:
    refs: list[str] = []
    for edge in edges:
        raw_refs = edge.get("passage_support", [])
        if isinstance(raw_refs, list):
            refs.extend(str(value) for value in raw_refs)
    return refs


def _upsert_many(
    target: MutableMapping[str, dict[str, object]], rows: Sequence[Mapping[str, object]], key: str
) -> None:
    for row in rows:
        target[str(row[key])] = deepcopy(dict(row))


def _concept_id(concept: Mapping[str, object]) -> str:
    return str(concept["concept_id"])


def _edge_id(edge: Mapping[str, object]) -> str:
    return str(edge["edge_id"])


def _teacher_segment(row: Mapping[str, object]) -> dict[str, object]:
    return {
        "segment_id": row["segment_id"],
        "segment_type": row["segment_type"],
        "page": row["page"],
        "char_span": row["char_span"],
        "location": row.get("location"),
    }


def _teacher_concept(row: Mapping[str, object]) -> dict[str, object]:
    return {
        "concept_id": row["concept_id"],
        "label": row["label"],
        "definition": row["definition"],
        "category_tag": row["category_tag"],
        "passage_refs": row.get("passage_refs", {}),
    }


def _teacher_edge(row: Mapping[str, object]) -> dict[str, object]:
    return {
        "edge_id": row["edge_id"],
        "edge_kind": row["edge_kind"],
        "from_concept_id": row["from_concept_id"],
        "to_concept_id": row["to_concept_id"],
        "passage_support": row.get("passage_support", []),
        "rationale": row.get("rationale"),
    }


def _json_default(value: Any) -> str:
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)
