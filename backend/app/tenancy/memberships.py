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

    def ensure_student_membership(self, *, user_id: UUID, tenant_id: UUID) -> dict[str, Any]:
        """Create or return the B2C student membership for a user.

        Traceability:
        - phase-3-m4-curriculum-auth-sdd.md §6.3
        - backend-architecture.md §§5.4-5.5
        """
        existing = [
            record
            for record in self._records.get(user_id, [])
            if record["tenant_id"] == tenant_id and record["role"] == "student"
        ]
        if existing:
            return existing[0]
        record = {"user_id": user_id, "tenant_id": tenant_id, "role": "student"}
        self._records.setdefault(user_id, []).append(record)
        return record

    def get_memberships_for_user(self, user_id: UUID) -> list[dict[str, Any]]:
        return self._records.get(user_id, [])
