"""Create the Phase 2 curriculum content schema.

Traceability:
- docs/planning/sdd/phase-2-curriculum-ingestion-sdd.md §§6, 9, 10
- docs/architecture/backend-architecture.md §§5.3, 7.5, 10
- docs/chapter-analysis-pipeline-specification.md P0–P4
"""

from alembic import op

revision = "0004_curriculum_schema"
down_revision = "0003_rls_policy_helper_optimization"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE SCHEMA IF NOT EXISTS curriculum;

        CREATE TABLE curriculum.chapters (
            chapter_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES public.tenants(tenant_id),
            exam_id UUID,
            subject_id UUID,
            title TEXT NOT NULL,
            chapter_analysis_id UUID NOT NULL UNIQUE,
            source_doc_hash TEXT NOT NULL,
            segment_index_version TEXT NOT NULL,
            pipeline_version TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );

        CREATE TABLE curriculum.segments (
            segment_id TEXT PRIMARY KEY,
            chapter_id UUID NOT NULL REFERENCES curriculum.chapters(chapter_id) ON DELETE CASCADE,
            tenant_id UUID NOT NULL REFERENCES public.tenants(tenant_id),
            chapter_analysis_id UUID NOT NULL,
            segment_type TEXT NOT NULL,
            text TEXT NOT NULL,
            page INTEGER NOT NULL,
            char_span JSONB NOT NULL,
            location TEXT,
            pipeline_version TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );

        CREATE TABLE curriculum.concepts (
            concept_id TEXT PRIMARY KEY,
            chapter_id UUID NOT NULL REFERENCES curriculum.chapters(chapter_id) ON DELETE CASCADE,
            tenant_id UUID NOT NULL REFERENCES public.tenants(tenant_id),
            chapter_analysis_id UUID NOT NULL,
            label TEXT NOT NULL,
            definition TEXT NOT NULL,
            category_tag TEXT NOT NULL,
            passage_refs JSONB NOT NULL,
            merged_from JSONB NOT NULL DEFAULT '[]'::jsonb,
            pipeline_version TEXT NOT NULL,
            prompt_version TEXT,
            model_id TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );

        CREATE TABLE curriculum.concept_edges (
            edge_id TEXT PRIMARY KEY,
            chapter_id UUID NOT NULL REFERENCES curriculum.chapters(chapter_id) ON DELETE CASCADE,
            tenant_id UUID NOT NULL REFERENCES public.tenants(tenant_id),
            chapter_analysis_id UUID NOT NULL,
            edge_kind TEXT NOT NULL CHECK (edge_kind IN ('PREREQUISITE_OF', 'CONNECTS', 'CONTRASTS_WITH')),
            from_concept_id TEXT NOT NULL REFERENCES curriculum.concepts(concept_id) ON DELETE CASCADE,
            to_concept_id TEXT NOT NULL REFERENCES curriculum.concepts(concept_id) ON DELETE CASCADE,
            passage_support JSONB NOT NULL,
            rationale TEXT,
            pipeline_version TEXT NOT NULL,
            prompt_version TEXT,
            model_id TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );

        ALTER TABLE curriculum.chapters ENABLE ROW LEVEL SECURITY;
        ALTER TABLE curriculum.segments ENABLE ROW LEVEL SECURITY;
        ALTER TABLE curriculum.concepts ENABLE ROW LEVEL SECURITY;
        ALTER TABLE curriculum.concept_edges ENABLE ROW LEVEL SECURITY;

        CREATE POLICY curriculum_chapters_tenant_isolation ON curriculum.chapters
            USING (tenant_id = (SELECT public.current_app_tenant_id()))
            WITH CHECK (tenant_id = (SELECT public.current_app_tenant_id()));
        CREATE POLICY curriculum_segments_tenant_isolation ON curriculum.segments
            USING (tenant_id = (SELECT public.current_app_tenant_id()))
            WITH CHECK (tenant_id = (SELECT public.current_app_tenant_id()));
        CREATE POLICY curriculum_concepts_tenant_isolation ON curriculum.concepts
            USING (tenant_id = (SELECT public.current_app_tenant_id()))
            WITH CHECK (tenant_id = (SELECT public.current_app_tenant_id()));
        CREATE POLICY curriculum_concept_edges_tenant_isolation ON curriculum.concept_edges
            USING (tenant_id = (SELECT public.current_app_tenant_id()))
            WITH CHECK (tenant_id = (SELECT public.current_app_tenant_id()));
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS curriculum.concept_edges;
        DROP TABLE IF EXISTS curriculum.concepts;
        DROP TABLE IF EXISTS curriculum.segments;
        DROP TABLE IF EXISTS curriculum.chapters;
        DROP SCHEMA IF EXISTS curriculum;
        """
    )
