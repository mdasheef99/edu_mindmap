from pathlib import Path


def test_migration_0004_creates_curriculum_schema_tables_and_rls() -> None:
    """SDD §6 + §9: migration 0004 must create curriculum tables with RLS."""
    repo_root = Path(__file__).resolve().parents[2]
    migration = repo_root / "backend" / "migrations" / "versions" / "0004_curriculum_schema.py"

    assert migration.exists(), "migration 0004 must exist before curriculum schema checks can pass"

    migration_text = migration.read_text(encoding="utf-8").lower()
    required_fragments = [
        "create schema if not exists curriculum",
        "create table curriculum.chapters",
        "create table curriculum.segments",
        "create table curriculum.concepts",
        "create table curriculum.concept_edges",
        "alter table curriculum.chapters enable row level security",
        "alter table curriculum.segments enable row level security",
        "alter table curriculum.concepts enable row level security",
        "alter table curriculum.concept_edges enable row level security",
        "current_app_tenant_id()",
    ]

    for fragment in required_fragments:
        assert fragment in migration_text


def test_migration_0004_curriculum_tables_carry_tenant_and_analysis_stamps() -> None:
    """SDD §6 + backend-architecture §7.5: curriculum rows need tenant and version stamps."""
    repo_root = Path(__file__).resolve().parents[2]
    migration = repo_root / "backend" / "migrations" / "versions" / "0004_curriculum_schema.py"

    assert migration.exists(), "migration 0004 must exist before curriculum schema checks can pass"

    migration_text = migration.read_text(encoding="utf-8").lower()

    for fragment in [
        "chapter_analysis_id uuid not null",
        "tenant_id uuid not null",
        "segment_index_version text not null",
        "segment_type text not null",
        "char_span jsonb not null",
        "location text",
        "category_tag text not null",
        "passage_refs jsonb not null",
        "merged_from jsonb not null",
        "edge_id text primary key",
        "edge_kind text not null",
        "passage_support jsonb not null",
    ]:
        assert fragment in migration_text


def test_migration_0005_grants_curriculum_access_and_indexes_foreign_keys() -> None:
    """Phase 2 live ingest needs app-role grants and indexed curriculum foreign keys."""
    repo_root = Path(__file__).resolve().parents[2]
    migration = (
        repo_root
        / "backend"
        / "migrations"
        / "versions"
        / "0005_curriculum_privileges_and_indexes.py"
    )

    assert migration.exists(), "migration 0005 must preserve live curriculum access/indexes"

    migration_text = migration.read_text(encoding="utf-8").lower()
    for fragment in [
        "grant usage on schema curriculum to phase1_rls_tester",
        "grant select, insert, update on all tables in schema curriculum to phase1_rls_tester",
        "alter default privileges for role postgres in schema curriculum",
        "curriculum_chapters_tenant_id_idx",
        "curriculum_segments_chapter_id_idx",
        "curriculum_segments_tenant_id_idx",
        "curriculum_concepts_chapter_id_idx",
        "curriculum_concepts_tenant_id_idx",
        "curriculum_concept_edges_chapter_id_idx",
        "curriculum_concept_edges_tenant_id_idx",
        "curriculum_concept_edges_from_concept_id_idx",
        "curriculum_concept_edges_to_concept_id_idx",
    ]:
        assert fragment in migration_text


def test_migration_0005_downgrade_revokes_default_privileges_for_curriculum_role() -> None:
    """Migration 0005 downgrade must unwind the default-privilege grant symmetrically."""
    repo_root = Path(__file__).resolve().parents[2]
    migration = (
        repo_root
        / "backend"
        / "migrations"
        / "versions"
        / "0005_curriculum_privileges_and_indexes.py"
    )

    migration_text = migration.read_text(encoding="utf-8").lower()

    assert (
        "alter default privileges for role postgres in schema curriculum\n"
        "            revoke select, insert, update on tables from phase1_rls_tester"
    ) in migration_text
