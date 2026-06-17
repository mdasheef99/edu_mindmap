from pathlib import Path


def test_security_remediation_migration_addresses_supabase_advisors() -> None:
    """Migration 0002 should remediate the Phase 1 Supabase advisor findings."""
    repo_root = Path(__file__).resolve().parents[2]
    migration = (
        repo_root
        / "backend"
        / "migrations"
        / "versions"
        / "0002_security_and_performance_remediation.py"
    )

    text = migration.read_text(encoding="utf-8").lower()

    for fragment in [
        "alter table public.tenants enable row level security",
        "alter table public.memberships enable row level security",
        "alter function public.prevent_events_update_delete()",
        "set search_path = public, pg_temp",
        "create index if not exists qclass_event_id_idx",
        "create index if not exists qclass_source_event_id_idx",
        "create index if not exists consent_records_event_id_idx",
        "create policy tenants_tenant_isolation",
        "create policy memberships_tenant_isolation",
        "select nullif(current_setting('app.tenant_id', true), '')::uuid",
    ]:
        assert fragment in text


def test_rls_helper_migration_removes_current_setting_from_policy_definitions() -> None:
    """Follow-up migration should keep current_setting out of policy expressions."""
    repo_root = Path(__file__).resolve().parents[2]
    migration = (
        repo_root / "backend" / "migrations" / "versions" / "0003_rls_policy_helper_optimization.py"
    )

    text = migration.read_text(encoding="utf-8").lower()

    assert "create or replace function public.current_app_tenant_id()" in text
    assert "set search_path = public, pg_temp" in text
    assert "select public.current_app_tenant_id()" in text
    assert "create policy tenants_tenant_isolation" in text
