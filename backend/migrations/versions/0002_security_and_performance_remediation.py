"""Security and performance remediation after Supabase advisor review.

Traceability:
- docs/planning/development-approach.md §§4.2, 6.6
- docs/planning/sdd/phase-1-walking-skeleton-sdd.md §10
- docs/architecture/backend-architecture.md §§5, 6, 8, 9, 12
"""

from alembic import op

revision = "0002_security_and_performance_remediation"
down_revision = "0001_phase_1_walking_skeleton"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE public.tenants ENABLE ROW LEVEL SECURITY;
        ALTER TABLE public.memberships ENABLE ROW LEVEL SECURITY;

        ALTER FUNCTION public.prevent_events_update_delete()
            SET search_path = public, pg_temp;

        CREATE INDEX IF NOT EXISTS memberships_tenant_id_idx
            ON public.memberships (tenant_id);
        CREATE INDEX IF NOT EXISTS consent_records_tenant_id_idx
            ON public.consent_records (tenant_id);
        CREATE INDEX IF NOT EXISTS consent_records_event_id_idx
            ON public.consent_records (event_id);
        CREATE INDEX IF NOT EXISTS llm_usage_records_tenant_id_idx
            ON public.llm_usage_records (tenant_id);
        CREATE INDEX IF NOT EXISTS student_sessions_tenant_id_idx
            ON student_rm.sessions (tenant_id);
        CREATE INDEX IF NOT EXISTS student_nodes_tenant_id_idx
            ON student_rm.nodes (tenant_id);
        CREATE INDEX IF NOT EXISTS student_nodes_session_id_idx
            ON student_rm.nodes (session_id);
        CREATE INDEX IF NOT EXISTS qclass_tenant_id_idx
            ON analytic_rm.question_classifications (tenant_id);
        CREATE INDEX IF NOT EXISTS qclass_event_id_idx
            ON analytic_rm.question_classifications (event_id);
        CREATE INDEX IF NOT EXISTS qclass_source_event_id_idx
            ON analytic_rm.question_classifications (source_event_id);

        DROP POLICY IF EXISTS tenants_tenant_isolation ON public.tenants;
        DROP POLICY IF EXISTS memberships_tenant_isolation ON public.memberships;
        DROP POLICY IF EXISTS events_tenant_isolation ON public.events;
        DROP POLICY IF EXISTS consent_records_tenant_isolation ON public.consent_records;
        DROP POLICY IF EXISTS jobs_tenant_isolation ON public.jobs;
        DROP POLICY IF EXISTS llm_usage_records_tenant_isolation ON public.llm_usage_records;
        DROP POLICY IF EXISTS student_sessions_tenant_isolation ON student_rm.sessions;
        DROP POLICY IF EXISTS student_nodes_tenant_isolation ON student_rm.nodes;
        DROP POLICY IF EXISTS question_classifications_tenant_isolation
            ON analytic_rm.question_classifications;

        CREATE POLICY tenants_tenant_isolation ON public.tenants
            USING (tenant_id = (SELECT NULLIF(current_setting('app.tenant_id', true), '')::uuid))
            WITH CHECK (tenant_id = (SELECT NULLIF(current_setting('app.tenant_id', true), '')::uuid));
        CREATE POLICY memberships_tenant_isolation ON public.memberships
            USING (tenant_id = (SELECT NULLIF(current_setting('app.tenant_id', true), '')::uuid))
            WITH CHECK (tenant_id = (SELECT NULLIF(current_setting('app.tenant_id', true), '')::uuid));
        CREATE POLICY events_tenant_isolation ON public.events
            USING (tenant_id = (SELECT NULLIF(current_setting('app.tenant_id', true), '')::uuid))
            WITH CHECK (tenant_id = (SELECT NULLIF(current_setting('app.tenant_id', true), '')::uuid));
        CREATE POLICY consent_records_tenant_isolation ON public.consent_records
            USING (tenant_id = (SELECT NULLIF(current_setting('app.tenant_id', true), '')::uuid))
            WITH CHECK (tenant_id = (SELECT NULLIF(current_setting('app.tenant_id', true), '')::uuid));
        CREATE POLICY jobs_tenant_isolation ON public.jobs
            USING (tenant_id = (SELECT NULLIF(current_setting('app.tenant_id', true), '')::uuid))
            WITH CHECK (tenant_id = (SELECT NULLIF(current_setting('app.tenant_id', true), '')::uuid));
        CREATE POLICY llm_usage_records_tenant_isolation ON public.llm_usage_records
            USING (
                tenant_id IS NULL
                OR tenant_id = (SELECT NULLIF(current_setting('app.tenant_id', true), '')::uuid)
            )
            WITH CHECK (
                tenant_id IS NULL
                OR tenant_id = (SELECT NULLIF(current_setting('app.tenant_id', true), '')::uuid)
            );
        CREATE POLICY student_sessions_tenant_isolation ON student_rm.sessions
            USING (tenant_id = (SELECT NULLIF(current_setting('app.tenant_id', true), '')::uuid))
            WITH CHECK (tenant_id = (SELECT NULLIF(current_setting('app.tenant_id', true), '')::uuid));
        CREATE POLICY student_nodes_tenant_isolation ON student_rm.nodes
            USING (tenant_id = (SELECT NULLIF(current_setting('app.tenant_id', true), '')::uuid))
            WITH CHECK (tenant_id = (SELECT NULLIF(current_setting('app.tenant_id', true), '')::uuid));
        CREATE POLICY question_classifications_tenant_isolation
            ON analytic_rm.question_classifications
            USING (tenant_id = (SELECT NULLIF(current_setting('app.tenant_id', true), '')::uuid))
            WITH CHECK (tenant_id = (SELECT NULLIF(current_setting('app.tenant_id', true), '')::uuid));
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP POLICY IF EXISTS tenants_tenant_isolation ON public.tenants;
        DROP POLICY IF EXISTS memberships_tenant_isolation ON public.memberships;
        ALTER TABLE public.tenants DISABLE ROW LEVEL SECURITY;
        ALTER TABLE public.memberships DISABLE ROW LEVEL SECURITY;
        """
    )
