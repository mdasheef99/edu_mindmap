"""Postgres-backed student session projection reader for workers."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from app.tenancy.postgres_context import set_local_tenant

SELECT_SESSION_SQL = """
SELECT *
FROM student_rm.sessions
WHERE session_id = %(session_id)s
  AND tenant_id = %(tenant_id)s
"""

UPSERT_SESSION_SQL = """
INSERT INTO student_rm.sessions (
    session_id, tenant_id, student_user_id, exam_id, subject_id, chapter_id,
    concept_entry_id, chapter_analysis_id, status, last_active_node_id,
    started_at, last_active_at, closed_at
) VALUES (
    %(session_id)s, %(tenant_id)s, %(student_user_id)s, %(exam_id)s,
    %(subject_id)s, %(chapter_id)s, %(concept_entry_id)s,
    %(chapter_analysis_id)s, %(status)s, %(last_active_node_id)s,
    %(started_at)s, %(last_active_at)s, %(closed_at)s
)
ON CONFLICT (session_id) DO UPDATE SET
    status = EXCLUDED.status,
    last_active_node_id = EXCLUDED.last_active_node_id,
    last_active_at = EXCLUDED.last_active_at,
    closed_at = EXCLUDED.closed_at
RETURNING *
"""


class PostgresStudentSessionStore:
    """Tenant-scoped reader for `student_rm.sessions`."""

    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def get_for_tenant(self, session_id: str | UUID, tenant_id: UUID) -> dict[str, Any] | None:
        with self.connection.transaction():
            set_local_tenant(self.connection, tenant_id)
            cursor = self.connection.execute(
                SELECT_SESSION_SQL,
                {"session_id": session_id, "tenant_id": tenant_id},
            )
            row = cursor.fetchone()
        return None if row is None else dict(row)

    def upsert(self, session_row: Any) -> dict[str, Any]:
        params = dict(session_row)
        with self.connection.transaction():
            set_local_tenant(self.connection, params["tenant_id"])
            cursor = self.connection.execute(UPSERT_SESSION_SQL, params)
            return dict(cursor.fetchone())

    def get_for_tenant_and_student(
        self, session_id: str | UUID, tenant_id: UUID, student_user_id: UUID
    ) -> dict[str, Any] | None:
        with self.connection.transaction():
            set_local_tenant(self.connection, tenant_id)
            cursor = self.connection.execute(
                "SELECT * FROM student_rm.sessions "
                "WHERE session_id = %(session_id)s AND tenant_id = %(tenant_id)s "
                "AND student_user_id = %(student_user_id)s",
                {
                    "session_id": session_id,
                    "tenant_id": tenant_id,
                    "student_user_id": student_user_id,
                },
            )
            row = cursor.fetchone()
        return None if row is None else dict(row)

    def list_recent_for_tenant_and_student(
        self, *, tenant_id: UUID, student_user_id: UUID, limit: int = 5
    ) -> list[dict[str, Any]]:
        with self.connection.transaction():
            set_local_tenant(self.connection, tenant_id)
            cursor = self.connection.execute(
                "SELECT * FROM student_rm.sessions "
                "WHERE tenant_id = %(tenant_id)s AND student_user_id = %(student_user_id)s "
                "ORDER BY last_active_at DESC, started_at DESC, session_id DESC LIMIT %(limit)s",
                {"tenant_id": tenant_id, "student_user_id": student_user_id, "limit": limit},
            )
            return [dict(row) for row in cursor.fetchall()]

    def mark_resumed(self, resume_row: Any) -> dict[str, Any] | None:
        params = dict(resume_row)
        with self.connection.transaction():
            set_local_tenant(self.connection, params["tenant_id"])
            cursor = self.connection.execute(
                "UPDATE student_rm.sessions SET status = 'active', "
                "last_active_at = %(last_active_at)s "
                "WHERE session_id = %(session_id)s AND tenant_id = %(tenant_id)s "
                "AND student_user_id = %(student_user_id)s RETURNING *",
                params,
            )
            row = cursor.fetchone()
        return None if row is None else dict(row)
