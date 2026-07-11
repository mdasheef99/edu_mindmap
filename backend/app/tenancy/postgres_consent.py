"""Postgres-backed consent reader for worker projection gates."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from app.tenancy.postgres_context import set_local_tenant

HAS_VALID_BEHAVIORAL_ANALYTICS_SQL = """
SELECT 1
FROM public.consent_records
WHERE tenant_id = %(tenant_id)s
  AND student_user_id = %(student_user_id)s
  AND consent_kind = 'behavioral_analytics'
  AND state = 'granted'
  AND granted_at IS NOT NULL
  AND withdrawn_at IS NULL
ORDER BY granted_at DESC
LIMIT 1
"""


class PostgresConsentRecordStore:
    """Tenant-scoped consent reader used by the classify worker."""

    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def has_valid_behavioral_analytics(
        self,
        *,
        tenant_id: UUID,
        student_user_id: UUID,
    ) -> bool:
        with self.connection.transaction():
            set_local_tenant(self.connection, tenant_id)
            cursor = self.connection.execute(
                HAS_VALID_BEHAVIORAL_ANALYTICS_SQL,
                {"tenant_id": tenant_id, "student_user_id": student_user_id},
            )
            return cursor.fetchone() is not None

    def grant_behavioral_analytics(
        self,
        *,
        tenant_id: UUID,
        student_user_id: UUID,
        event_id: UUID | None = None,
    ) -> dict[str, Any]:
        with self.connection.transaction():
            set_local_tenant(self.connection, tenant_id)
            cursor = self.connection.execute(
                """
                INSERT INTO public.consent_records (
                    tenant_id, student_user_id, consent_kind, state,
                    grantor_user_id, method, granted_at, event_id
                ) VALUES (
                    %(tenant_id)s, %(student_user_id)s, 'behavioral_analytics', 'granted',
                    %(student_user_id)s, 'b2c_app_acknowledgement', now(), %(event_id)s
                )
                ON CONFLICT (tenant_id, student_user_id, consent_kind)
                    WHERE state = 'granted' AND withdrawn_at IS NULL
                DO UPDATE SET updated_at = public.consent_records.updated_at
                RETURNING *
                """,
                {
                    "tenant_id": tenant_id,
                    "student_user_id": student_user_id,
                    "event_id": event_id,
                },
            )
            return dict(cursor.fetchone())
