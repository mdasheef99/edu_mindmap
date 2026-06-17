"""Phase 1 walking skeleton primitives.

Traceability:
- docs/planning/sdd/phase-1-walking-skeleton-sdd.md §§3, 6, 9, 10
- docs/architecture/backend-architecture.md §§5, 6, 8, 12
- docs/database/event-store-and-job-queue-schema.md §§2, 3, 7, 9
- docs/database/core-operational-schema.md §5
"""

from alembic import op

revision = "0001_phase_1_walking_skeleton"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE EXTENSION IF NOT EXISTS pgcrypto;
        CREATE SCHEMA IF NOT EXISTS student_rm;
        CREATE SCHEMA IF NOT EXISTS analytic_rm;

        CREATE TABLE tenants (
            tenant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            kind TEXT NOT NULL CHECK (kind IN ('individual', 'institutional')),
            name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            region TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );

        CREATE TABLE memberships (
            membership_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
            user_id UUID NOT NULL,
            role TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            active_from TIMESTAMPTZ NOT NULL DEFAULT now(),
            active_to TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, user_id, role, active_from)
        );

        CREATE TABLE events (
            event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            event_type TEXT NOT NULL,
            event_version SMALLINT NOT NULL,
            tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
            actor_user_id UUID,
            student_id UUID,
            session_id UUID,
            exam_id UUID,
            subject_id UUID,
            chapter_id UUID,
            chapter_analysis_id UUID,
            concept_entry_id UUID,
            node_id UUID,
            offer_set_id UUID,
            occurred_at TIMESTAMPTZ NOT NULL,
            recorded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            idempotency_key TEXT,
            producer TEXT NOT NULL CHECK (producer IN ('client', 'server', 'worker', 'admin', 'internal')),
            payload JSONB NOT NULL DEFAULT '{}'::jsonb,
            policy_version TEXT,
            prompt_version TEXT,
            model_id TEXT,
            projection_version TEXT,
            replay_id UUID
        );
        COMMENT ON COLUMN events.event_type IS
            'Registry validated in app.events.registry; Phase 1 includes session_started, node_created, offer_set_choice, question_classified, consent_recorded.';

        CREATE OR REPLACE FUNCTION prevent_events_update_delete()
        RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'events are append-only; UPDATE/DELETE is prohibited';
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER prevent_events_update_delete
            BEFORE UPDATE OR DELETE ON events
            FOR EACH ROW EXECUTE FUNCTION prevent_events_update_delete();

        REVOKE UPDATE, DELETE ON events FROM PUBLIC;
        CREATE INDEX events_tenant_session_recorded_idx ON events (tenant_id, session_id, recorded_at);
        CREATE INDEX events_tenant_type_recorded_idx ON events (tenant_id, event_type, recorded_at);

        CREATE TABLE consent_records (
            consent_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
            student_user_id UUID NOT NULL,
            consent_kind TEXT NOT NULL CHECK (consent_kind IN ('data_processing', 'behavioral_analytics')),
            state TEXT NOT NULL CHECK (state IN ('granted', 'withdrawn', 'pending')),
            grantor_user_id UUID,
            method TEXT NOT NULL,
            granted_at TIMESTAMPTZ,
            withdrawn_at TIMESTAMPTZ,
            source_ref TEXT,
            event_id UUID REFERENCES events(event_id),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        COMMENT ON TABLE consent_records IS
            'Consent entity audited by consent_recorded events; behavioral_analytics gates analytic_rm projections.';

        CREATE TABLE jobs (
            job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            job_type TEXT NOT NULL CHECK (job_type IN ('classify', 'compress', 'project', 'replay', 'podcast', 'chapter_analysis')),
            tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
            payload JSONB NOT NULL,
            status TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'running', 'done', 'failed', 'dead')),
            attempts INTEGER NOT NULL DEFAULT 0,
            run_after TIMESTAMPTZ NOT NULL DEFAULT now(),
            locked_at TIMESTAMPTZ,
            locked_by TEXT,
            last_error TEXT,
            idempotency_key TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, job_type, idempotency_key)
        );
        COMMENT ON TABLE jobs IS 'Claim queued rows with SELECT ... FOR UPDATE SKIP LOCKED.';
        CREATE INDEX jobs_claim_idx ON jobs (status, run_after, created_at) WHERE status = 'queued';

        CREATE TABLE llm_usage_records (
            usage_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID REFERENCES tenants(tenant_id),
            purpose TEXT NOT NULL CHECK (purpose IN ('generation', 'classification', 'analysis', 'podcast')),
            model_id TEXT NOT NULL,
            prompt_version TEXT NOT NULL,
            prompt_tokens INTEGER NOT NULL CHECK (prompt_tokens >= 0),
            completion_tokens INTEGER NOT NULL CHECK (completion_tokens >= 0),
            cost_usd NUMERIC(12, 6) NOT NULL DEFAULT 0,
            fixture BOOLEAN NOT NULL DEFAULT false,
            recorded_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        COMMENT ON TABLE llm_usage_records IS 'Per-call LLM Gateway usage/cost counter from the first model call.';

        CREATE TABLE student_rm.sessions (
            session_id UUID PRIMARY KEY,
            tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
            student_user_id UUID NOT NULL,
            exam_id UUID NOT NULL,
            subject_id UUID NOT NULL,
            chapter_id UUID NOT NULL,
            concept_entry_id UUID NOT NULL,
            chapter_analysis_id UUID NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('active', 'inactive', 'closed')),
            last_active_node_id UUID,
            started_at TIMESTAMPTZ NOT NULL,
            last_active_at TIMESTAMPTZ NOT NULL,
            closed_at TIMESTAMPTZ
        );

        CREATE TABLE student_rm.nodes (
            node_id UUID PRIMARY KEY,
            tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
            session_id UUID NOT NULL REFERENCES student_rm.sessions(session_id),
            student_user_id UUID NOT NULL,
            node_type TEXT NOT NULL,
            parent_node_id UUID,
            creation_source TEXT NOT NULL,
            content_payload JSONB NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );

        CREATE TABLE analytic_rm.question_classifications (
            classification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
            student_user_id UUID NOT NULL,
            session_id UUID NOT NULL,
            chapter_id UUID NOT NULL,
            chapter_analysis_id UUID NOT NULL,
            offer_set_id UUID NOT NULL,
            event_id UUID NOT NULL REFERENCES events(event_id),
            source_event_id UUID NOT NULL REFERENCES events(event_id),
            source_event_type TEXT NOT NULL,
            source_event_recorded_at_max TIMESTAMPTZ NOT NULL,
            scores_payload JSONB NOT NULL,
            entropy_payload JSONB NOT NULL,
            dispersion_payload JSONB NOT NULL,
            projection_version TEXT NOT NULL,
            prompt_version TEXT NOT NULL,
            model_id TEXT NOT NULL,
            generated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );

        ALTER TABLE events ENABLE ROW LEVEL SECURITY;
        ALTER TABLE consent_records ENABLE ROW LEVEL SECURITY;
        ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
        ALTER TABLE llm_usage_records ENABLE ROW LEVEL SECURITY;
        ALTER TABLE student_rm.sessions ENABLE ROW LEVEL SECURITY;
        ALTER TABLE student_rm.nodes ENABLE ROW LEVEL SECURITY;
        ALTER TABLE analytic_rm.question_classifications ENABLE ROW LEVEL SECURITY;

        CREATE POLICY events_tenant_isolation ON events
            USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
            WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
        CREATE POLICY consent_records_tenant_isolation ON consent_records
            USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
            WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
        CREATE POLICY jobs_tenant_isolation ON jobs
            USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
            WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
        CREATE POLICY llm_usage_records_tenant_isolation ON llm_usage_records
            USING (tenant_id IS NULL OR tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
            WITH CHECK (tenant_id IS NULL OR tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
        CREATE POLICY student_sessions_tenant_isolation ON student_rm.sessions
            USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
            WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
        CREATE POLICY student_nodes_tenant_isolation ON student_rm.nodes
            USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
            WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
        CREATE POLICY question_classifications_tenant_isolation ON analytic_rm.question_classifications
            USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
            WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS analytic_rm.question_classifications;
        DROP TABLE IF EXISTS student_rm.nodes;
        DROP TABLE IF EXISTS student_rm.sessions;
        DROP TABLE IF EXISTS llm_usage_records;
        DROP TABLE IF EXISTS jobs;
        DROP TABLE IF EXISTS consent_records;
        DROP TRIGGER IF EXISTS prevent_events_update_delete ON events;
        DROP FUNCTION IF EXISTS prevent_events_update_delete();
        DROP TABLE IF EXISTS events;
        DROP TABLE IF EXISTS memberships;
        DROP TABLE IF EXISTS tenants;
        DROP SCHEMA IF EXISTS analytic_rm;
        DROP SCHEMA IF EXISTS student_rm;
        """
    )
