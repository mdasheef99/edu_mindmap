"""Use a fixed-search-path tenant helper to avoid RLS initplan warnings.

Traceability:
- docs/planning/development-approach.md §6.6
- docs/architecture/backend-architecture.md §12
"""

from alembic import op


revision = "0003_rls_policy_helper_optimization"
down_revision = "0002_security_and_performance_remediation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION public.current_app_tenant_id()
        RETURNS uuid
        LANGUAGE sql
        STABLE
        SET search_path = public, pg_temp
        AS $$
            SELECT NULLIF(current_setting('app.tenant_id', true), '')::uuid
        $$;

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
            USING (tenant_id = (SELECT public.current_app_tenant_id()))
            WITH CHECK (tenant_id = (SELECT public.current_app_tenant_id()));
        CREATE POLICY memberships_tenant_isolation ON public.memberships
            USING (tenant_id = (SELECT public.current_app_tenant_id()))
            WITH CHECK (tenant_id = (SELECT public.current_app_tenant_id()));
        CREATE POLICY events_tenant_isolation ON public.events
            USING (tenant_id = (SELECT public.current_app_tenant_id()))
            WITH CHECK (tenant_id = (SELECT public.current_app_tenant_id()));
        CREATE POLICY consent_records_tenant_isolation ON public.consent_records
            USING (tenant_id = (SELECT public.current_app_tenant_id()))
            WITH CHECK (tenant_id = (SELECT public.current_app_tenant_id()));
        CREATE POLICY jobs_tenant_isolation ON public.jobs
            USING (tenant_id = (SELECT public.current_app_tenant_id()))
            WITH CHECK (tenant_id = (SELECT public.current_app_tenant_id()));
        CREATE POLICY llm_usage_records_tenant_isolation ON public.llm_usage_records
            USING (tenant_id IS NULL OR tenant_id = (SELECT public.current_app_tenant_id()))
            WITH CHECK (tenant_id IS NULL OR tenant_id = (SELECT public.current_app_tenant_id()));
        CREATE POLICY student_sessions_tenant_isolation ON student_rm.sessions
            USING (tenant_id = (SELECT public.current_app_tenant_id()))
            WITH CHECK (tenant_id = (SELECT public.current_app_tenant_id()));
        CREATE POLICY student_nodes_tenant_isolation ON student_rm.nodes
            USING (tenant_id = (SELECT public.current_app_tenant_id()))
            WITH CHECK (tenant_id = (SELECT public.current_app_tenant_id()));
        CREATE POLICY question_classifications_tenant_isolation
            ON analytic_rm.question_classifications
            USING (tenant_id = (SELECT public.current_app_tenant_id()))
            WITH CHECK (tenant_id = (SELECT public.current_app_tenant_id()));
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP FUNCTION IF EXISTS public.current_app_tenant_id();
        """
    )