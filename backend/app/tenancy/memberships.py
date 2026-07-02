"""In-memory membership store for test-fixture auth resolution."""

from __future__ import annotations

from typing import Any
from uuid import UUID


class InMemoryMembershipStore:
    """In-memory membership records for test fixture auth resolution."""

    def __init__(self) -> None:
        self._records: dict[UUID, list[dict[str, Any]]] = {}

    def add_membership(self, *, user_id: UUID, tenant_id: UUID, role: str) -> None:
        self._records.setdefault(user_id, []).append(
            {"user_id": user_id, "tenant_id": tenant_id, "role": role}
        )

    def get_memberships_for_user(self, user_id: UUID) -> list[dict[str, Any]]:
        return self._records.get(user_id, [])
