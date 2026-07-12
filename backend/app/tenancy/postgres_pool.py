"""Pooled Postgres request/transaction helpers for the API runtime.

Traceability: backend-architecture.md §5.3; development-approach.md §6.6;
phase-3-m4-runtime-closure-remediation-sdd.md R1-R2.
"""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Iterator
from uuid import UUID

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.tenancy.postgres_context import set_local_tenant


class PooledConnectionProxy:
    """Expose one request-scoped pooled connection to existing connection adapters."""

    def __init__(self, database_url: str) -> None:
        self.pool = ConnectionPool(
            conninfo=database_url,
            min_size=1,
            max_size=10,
            open=True,
            kwargs={"row_factory": dict_row},
            name="mindmap-api",
        )
        self._current: ContextVar[Any | None] = ContextVar(
            "mindmap_postgres_connection", default=None
        )

    @contextmanager
    def connection_scope(self) -> Iterator[Any]:
        current = self._current.get()
        if current is not None:
            yield current
            return
        with self.pool.connection() as connection:
            token = self._current.set(connection)
            try:
                yield connection
            finally:
                self._current.reset(token)

    @contextmanager
    def transaction(self) -> Iterator["PooledConnectionProxy"]:
        with self.connection_scope() as connection:
            with connection.transaction():
                yield self

    def execute(self, query: Any, params: Any = None) -> Any:
        connection = self._current.get()
        if connection is None:
            raise RuntimeError("Postgres execute requires an active connection scope")
        return connection.execute(query, params)

    def close(self) -> None:
        self.pool.close()


class PostgresTenantScopedConnection:
    """Session reader guarded by the transaction-local tenant GUC and owner predicate."""

    def __init__(self, connection: PooledConnectionProxy, tenant_id: UUID) -> None:
        self.connection = connection
        self.tenant_id = tenant_id

    def fetch_session(self, session_id: str) -> dict[str, Any] | None:
        cursor = self.connection.execute(
            "SELECT * FROM student_rm.sessions "
            "WHERE tenant_id = %(tenant_id)s AND session_id = %(session_id)s",
            {"tenant_id": self.tenant_id, "session_id": session_id},
        )
        row = cursor.fetchone()
        return None if row is None else dict(row)

    def fetch_session_for_student(
        self, session_id: str, student_user_id: UUID
    ) -> dict[str, Any] | None:
        cursor = self.connection.execute(
            "SELECT * FROM student_rm.sessions "
            "WHERE tenant_id = %(tenant_id)s AND session_id = %(session_id)s "
            "AND student_user_id = %(student_user_id)s",
            {
                "tenant_id": self.tenant_id,
                "session_id": session_id,
                "student_user_id": student_user_id,
            },
        )
        row = cursor.fetchone()
        return None if row is None else dict(row)

    def list_recent_sessions(
        self, *, student_user_id: UUID, limit: int = 5
    ) -> list[dict[str, Any]]:
        cursor = self.connection.execute(
            "SELECT * FROM student_rm.sessions "
            "WHERE tenant_id = %(tenant_id)s AND student_user_id = %(student_user_id)s "
            "ORDER BY last_active_at DESC, started_at DESC, session_id DESC LIMIT %(limit)s",
            {
                "tenant_id": self.tenant_id,
                "student_user_id": student_user_id,
                "limit": limit,
            },
        )
        return [dict(row) for row in cursor.fetchall()]

    def fetch_session_bypassing_app_guard(self, session_id: str) -> dict[str, Any] | None:
        return self.fetch_session(session_id)


class PostgresTenantConnectionPool:
    """Acquire a pooled connection, transaction, and `SET LOCAL` tenant context."""

    def __init__(self, connection: PooledConnectionProxy) -> None:
        self.connection = connection

    @contextmanager
    def transaction(self, tenant_id: UUID) -> Iterator[PostgresTenantScopedConnection]:
        with self.connection.transaction():
            set_local_tenant(self.connection, tenant_id)
            yield PostgresTenantScopedConnection(self.connection, tenant_id)
