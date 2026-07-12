"""M4 app-facing catalog and manual SQL tests.

Traceability:
- docs/planning/sdd/phase-3-m4-curriculum-auth-sdd.md §§7, 12.2, 12.4
- docs/database/core-operational-schema.md §6
- docs/database/schema-traceability-and-validation.md §§2-7
"""

import typing
from pathlib import Path
from uuid import uuid4

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


def test_catalog_store_lists_launch_path():
    """BC-1..BC-4: app catalog lists Class 10 -> CBSE -> Science -> Electricity."""
    from app.projections.catalog import InMemoryCatalogStore, seed_m4_electricity_catalog

    tenant_id = uuid4()
    catalog = InMemoryCatalogStore()
    seed = seed_m4_electricity_catalog(catalog, tenant_id=tenant_id)

    classes = catalog.list_classes()
    exams = catalog.list_exams(class_level_id=seed.class_level_id)
    subjects = catalog.list_subjects(
        class_level_id=seed.class_level_id,
        exam_id=seed.exam_id,
    )
    chapters = catalog.list_chapters(
        tenant_id=tenant_id,
        class_level_id=seed.class_level_id,
        exam_id=seed.exam_id,
        subject_id=seed.subject_id,
    )

    assert [row.label for row in classes] == ["Class 10"]
    assert [row.name for row in exams] == ["CBSE"]
    assert [row.name for row in subjects] == ["Science"]
    assert [row.title for row in chapters] == ["Electricity"]


def test_catalog_filters_unlaunchable_chapters():
    """BC-4: chapter list returns launchable chapters only."""
    from app.projections.catalog import InMemoryCatalogStore, seed_m4_electricity_catalog

    tenant_id = uuid4()
    catalog = InMemoryCatalogStore()
    seed = seed_m4_electricity_catalog(catalog, tenant_id=tenant_id)
    catalog.add_chapter(
        tenant_id=tenant_id,
        chapter_id=uuid4(),
        subject_id=seed.subject_id,
        chapter_analysis_id=uuid4(),
        slug="draft-magnetism",
        title="Magnetism",
        status="draft",
    )

    chapters = catalog.list_chapters(
        tenant_id=tenant_id,
        class_level_id=seed.class_level_id,
        exam_id=seed.exam_id,
        subject_id=seed.subject_id,
    )

    assert [row.title for row in chapters] == ["Electricity"]


def test_catalog_response_models_have_no_analytic_fields():
    """Category Invisibility: catalog/dashboard DTOs cannot express analytic fields."""
    from app.domain.student.curriculum import (
        ChapterDetailResponse,
        ChapterListResponse,
        ClassListResponse,
        ConceptEntryListResponse,
        DashboardResponse,
        ExamListResponse,
        SubjectListResponse,
    )

    for model in (
        ClassListResponse,
        ExamListResponse,
        SubjectListResponse,
        ChapterListResponse,
        ChapterDetailResponse,
        ConceptEntryListResponse,
        DashboardResponse,
    ):
        field_names = _field_names(model)
        assert not any(
            forbidden in field_name
            for field_name in field_names
            for forbidden in FORBIDDEN_ANALYTIC_FIELD_FRAGMENTS
        )


def test_m4_manual_sql_declares_catalog_tables_rls_and_project_warning():
    """DB-1/DB-2: local manual SQL creates catalog tables and warns about project ref."""
    sql_path = Path("backend/migrations/source_sql/0006_m4_catalog_auth_seed.sql")
    sql = sql_path.read_text(encoding="utf-8").lower()

    for table in (
        "curriculum_classes",
        "exams",
        "subjects",
        "chapters",
        "concept_entries",
        "chapter_analysis_versions",
    ):
        assert f"create table if not exists public.{table}" in sql

    assert "enable row level security" in sql
    assert "on conflict" in sql
    assert "jbmqyxhrmcbdgardamrp" in sql
    assert "ahntbtktjjmvfosgkmgn" in sql
    assert "bookconnect" in sql


def test_m4_forward_remediation_migration_carries_tenancy_and_indexes():
    """DB-1: applied 0006 is corrected only by a forward migration."""
    sql_path = Path("backend/migrations/source_sql/0007_m4_runtime_remediation.sql")
    sql = sql_path.read_text(encoding="utf-8").lower()

    for table in (
        "curriculum_classes",
        "exams",
        "subjects",
        "chapter_analysis_versions",
        "concept_entries",
    ):
        assert f"alter table public.{table}" in sql
        assert "tenant_id" in sql

    assert "chapter_analysis_versions_chapter_id" in sql
    for index_name in (
        "chapters_class_level_id_idx",
        "chapters_exam_id_idx",
        "chapters_subject_id_idx",
        "chapters_chapter_analysis_id_idx",
        "subjects_class_level_id_idx",
    ):
        assert index_name in sql


def test_m4_source_sql_manifest_distinguishes_local_and_live_migration_order():
    """R5: historical source SQL has an explicit order without rewriting applied migrations."""
    manifest = Path("backend/migrations/source_sql/README.md").read_text(encoding="utf-8")

    assert "0006_m3_schema_alignment" in manifest
    assert "0006_m4_catalog_auth_seed.sql" in manifest
    assert "0007_m4_runtime_remediation.sql" in manifest
    assert "20260702173751" in manifest
    assert "20260710075416" in manifest
    assert manifest.index("0006_m4_catalog_auth_seed.sql") < manifest.index(
        "0007_m4_runtime_remediation.sql"
    )
    assert "Do not rename or rewrite" in manifest


def _field_names(model: type) -> set[str]:
    names: set[str] = set()
    for name, field in model.model_fields.items():
        names.add(name.lower())
        annotation = getattr(field, "annotation", None)
        candidates = (annotation, *typing.get_args(annotation))
        for candidate in candidates:
            nested = getattr(candidate, "model_fields", None)
            if nested:
                names.update(_field_names(candidate))
    return names
