"""Postgres tenant-context helpers for RLS-backed adapters."""

from __future__ import annotations

from typing import Any

SET_LOCAL_TENANT_SQL = "SELECT set_config('app.tenant_id', %s, true)"


def set_local_tenant(connection: Any, tenant_id: Any) -> None:
    """Set the transaction-local tenant GUC using parameter-safe SQL."""
    connection.execute(SET_LOCAL_TENANT_SQL, (str(tenant_id),))
