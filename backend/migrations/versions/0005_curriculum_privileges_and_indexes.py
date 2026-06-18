"""Grant app-role curriculum access and index curriculum foreign keys.

Traceability:
- docs/planning/sdd/phase-2-curriculum-ingestion-sdd.md §§8-10
- docs/architecture/backend-architecture.md §§5.3, 7.5, 10
"""

from alembic import op

revision = "0005_curriculum_privileges_and_indexes"
down_revision = "0004_curriculum_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        GRANT USAGE ON SCHEMA curriculum TO phase1_rls_tester;
        GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA curriculum TO phase1_rls_tester;
        ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA curriculum
            GRANT SELECT, INSERT, UPDATE ON TABLES TO phase1_rls_tester;

        CREATE INDEX IF NOT EXISTS curriculum_chapters_tenant_id_idx
            ON curriculum.chapters (tenant_id);
        CREATE INDEX IF NOT EXISTS curriculum_segments_chapter_id_idx
            ON curriculum.segments (chapter_id);
        CREATE INDEX IF NOT EXISTS curriculum_segments_tenant_id_idx
            ON curriculum.segments (tenant_id);
        CREATE INDEX IF NOT EXISTS curriculum_concepts_chapter_id_idx
            ON curriculum.concepts (chapter_id);
        CREATE INDEX IF NOT EXISTS curriculum_concepts_tenant_id_idx
            ON curriculum.concepts (tenant_id);
        CREATE INDEX IF NOT EXISTS curriculum_concept_edges_chapter_id_idx
            ON curriculum.concept_edges (chapter_id);
        CREATE INDEX IF NOT EXISTS curriculum_concept_edges_tenant_id_idx
            ON curriculum.concept_edges (tenant_id);
        CREATE INDEX IF NOT EXISTS curriculum_concept_edges_from_concept_id_idx
            ON curriculum.concept_edges (from_concept_id);
        CREATE INDEX IF NOT EXISTS curriculum_concept_edges_to_concept_id_idx
            ON curriculum.concept_edges (to_concept_id);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP INDEX IF EXISTS curriculum.curriculum_concept_edges_to_concept_id_idx;
        DROP INDEX IF EXISTS curriculum.curriculum_concept_edges_from_concept_id_idx;
        DROP INDEX IF EXISTS curriculum.curriculum_concept_edges_tenant_id_idx;
        DROP INDEX IF EXISTS curriculum.curriculum_concept_edges_chapter_id_idx;
        DROP INDEX IF EXISTS curriculum.curriculum_concepts_tenant_id_idx;
        DROP INDEX IF EXISTS curriculum.curriculum_concepts_chapter_id_idx;
        DROP INDEX IF EXISTS curriculum.curriculum_segments_tenant_id_idx;
        DROP INDEX IF EXISTS curriculum.curriculum_segments_chapter_id_idx;
        DROP INDEX IF EXISTS curriculum.curriculum_chapters_tenant_id_idx;
        REVOKE SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA curriculum FROM phase1_rls_tester;
        ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA curriculum
            REVOKE SELECT, INSERT, UPDATE ON TABLES FROM phase1_rls_tester;
        REVOKE USAGE ON SCHEMA curriculum FROM phase1_rls_tester;
        """
    )
