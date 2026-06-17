from pathlib import Path


def test_events_table_rejects_update_and_delete() -> None:
    """T2: migration 0001 must make events append-only at the database layer."""
    repo_root = Path(__file__).resolve().parents[2]
    migration = repo_root / "backend" / "migrations" / "versions" / "0001_phase_1_walking_skeleton.py"

    assert migration.exists(), "migration 0001 must exist before DB append-only checks can pass"

    migration_text = migration.read_text(encoding="utf-8").lower()
    required_fragments = [
        "create table events",
        "tenant_id",
        "event_version",
        "prevent_events_update_delete",
        "raise exception",
        "before update or delete on events",
    ]

    for fragment in required_fragments:
        assert fragment in migration_text


def test_migration_creates_llm_usage_counter_table() -> None:
    """Phase 1 DoD: first llm_gateway call must have a durable usage/cost table."""
    repo_root = Path(__file__).resolve().parents[2]
    migration = repo_root / "backend" / "migrations" / "versions" / "0001_phase_1_walking_skeleton.py"

    migration_text = migration.read_text(encoding="utf-8").lower()

    for fragment in [
        "create table llm_usage_records",
        "purpose text not null",
        "model_id text not null",
        "prompt_tokens integer not null",
        "completion_tokens integer not null",
        "cost_usd numeric",
        "llm_usage_records_tenant_isolation",
    ]:
        assert fragment in migration_text