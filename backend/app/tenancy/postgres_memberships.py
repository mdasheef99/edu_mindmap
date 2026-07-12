"""Postgres membership resolution and idempotent B2C bootstrap."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from app.tenancy.postgres_context import set_local_tenant


class PostgresMembershipStore:
    """Backend-owned membership store; mobile tenant/role claims are never read."""

    def __init__(self, connection: Any, *, individual_tenant_id: UUID) -> None:
        self.connection = connection
        self.individual_tenant_id = individual_tenant_id

    def ensure_student_membership(self, *, user_id: UUID, tenant_id: UUID) -> dict[str, Any]:
        with self.connection.transaction():
            set_local_tenant(self.connection, tenant_id)
            cursor = self.connection.execute(
                """
                INSERT INTO public.memberships (tenant_id, user_id, role, status)
                VALUES (%(tenant_id)s, %(user_id)s, 'student', 'active')
                ON CONFLICT (tenant_id, user_id, role)
                    WHERE status = 'active' AND active_to IS NULL
                DO UPDATE SET updated_at = public.memberships.updated_at
                RETURNING tenant_id, user_id, role
                """,
                {"tenant_id": tenant_id, "user_id": user_id},
            )
            return dict(cursor.fetchone())

    def get_memberships_for_user(self, user_id: UUID) -> list[dict[str, Any]]:
        # M4 is explicitly B2C-first, so the backend chooses ADR-0007's configured individual
        # tenant before the lookup. No client-supplied tenant participates in resolution.
        with self.connection.transaction():
            set_local_tenant(self.connection, self.individual_tenant_id)
            cursor = self.connection.execute(
                """
                SELECT tenant_id, user_id, role
                FROM public.memberships
                WHERE user_id = %(user_id)s
                  AND tenant_id = %(tenant_id)s
                  AND status = 'active'
                  AND active_to IS NULL
                ORDER BY active_from, membership_id
                """,
                {"user_id": user_id, "tenant_id": self.individual_tenant_id},
            )
            return [dict(row) for row in cursor.fetchall()]
