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
