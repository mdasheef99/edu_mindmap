"""Postgres-backed student session projection reader for workers."""

from __future__ import annotations

from typing import Any
from uuid import UUID


SELECT_SESSION_SQL = """
SELECT *
FROM student_rm.sessions
WHERE session_id = %(session_id)s
  AND tenant_id = %(tenant_id)s
"""


class PostgresStudentSessionStore:
    """Tenant-scoped reader for `student_rm.sessions`."""

    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def get_for_tenant(self, session_id: str | UUID, tenant_id: UUID) -> dict[str, Any] | None:
        with self.connection.transaction():
            self.connection.execute("SET LOCAL app.tenant_id = %s", (str(tenant_id),))
            cursor = self.connection.execute(
                SELECT_SESSION_SQL,
                {"session_id": session_id, "tenant_id": tenant_id},
            )
            row = cursor.fetchone()
        return None if row is None else dict(row)