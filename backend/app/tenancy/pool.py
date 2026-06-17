"""Tenant-context helpers that mimic pooled connection access."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator
from uuid import UUID

from app.projections.student_sessions import InMemoryStudentSessionProjectionStore


class InMemoryTenantScopedConnection:
    """Single pooled connection carrying per-transaction tenant context."""

    def __init__(self, session_store: InMemoryStudentSessionProjectionStore) -> None:
        self._session_store = session_store
        self._tenant_id: UUID | None = None

    def set_local_tenant(self, tenant_id: UUID) -> None:
        self._tenant_id = tenant_id

    def clear_local_tenant(self) -> None:
        self._tenant_id = None

    def fetch_session(self, session_id: str) -> dict | None:
        if self._tenant_id is None:
            return None
        return self._session_store.get_for_tenant(session_id, self._tenant_id)

    def fetch_session_bypassing_app_guard(self, session_id: str) -> dict | None:
        """Direct table-style read protected only by the tenant context backstop."""
        return self.fetch_session(session_id)


class InMemoryTenantConnectionPool:
    """Shared pooled path that resets tenant context per transaction."""

    def __init__(self, session_store: InMemoryStudentSessionProjectionStore) -> None:
        self.connection = InMemoryTenantScopedConnection(session_store)

    @contextmanager
    def transaction(self, tenant_id: UUID) -> Iterator[InMemoryTenantScopedConnection]:
        self.connection.set_local_tenant(tenant_id)
        try:
            yield self.connection
        finally:
            self.connection.clear_local_tenant()