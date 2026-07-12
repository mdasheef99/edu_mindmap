"""M3 schema alignment: index events.node_id for node-scoped replay.

Traceability:
- docs/planning/development-approach.md §5 M3 (Canvas maturation; node_visited replay)
- docs/database/event-store-and-job-queue-schema.md §2 (events envelope; node_id column)
- docs/architecture/backend-architecture.md §5.3 (event store / replay)

Notes:
- The two session/type indexes (events_tenant_session_recorded_idx,
  events_tenant_type_recorded_idx) already exist from migration 0001 and are
  NOT recreated here.
- No envelope columns are added. edge_id/policy_name remain payload-stored and
  teacher_id is a forward declaration, per the schema-doc reconciliation note.
"""

from alembic import op

revision = "0006_m3_schema_alignment"
down_revision = "0005_curriculum_privileges_and_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS events_node_id_idx
            ON events (tenant_id, node_id, recorded_at)
            WHERE node_id IS NOT NULL;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP INDEX IF EXISTS events_node_id_idx;
        """
    )
