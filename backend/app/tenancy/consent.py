"""In-memory consent records for the Phase 1 worker consent gate."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4


class InMemoryConsentRecordStore:
    """Tracks tenant-scoped consent state used by worker-side projections."""

    def __init__(self) -> None:
        self.records: list[dict[str, Any]] = []

    def grant_behavioral_analytics(
        self,
        *,
        tenant_id: UUID,
        student_user_id: UUID,
        event_id: UUID | None = None,
    ) -> dict[str, Any]:
        for record in reversed(self.records):
            if (
                record["tenant_id"] == tenant_id
                and record["student_user_id"] == student_user_id
                and record["consent_kind"] == "behavioral_analytics"
                and record["state"] == "granted"
                and record["withdrawn_at"] is None
            ):
                return deepcopy(record)
        record = {
            "consent_id": uuid4(),
            "tenant_id": tenant_id,
            "student_user_id": student_user_id,
            "consent_kind": "behavioral_analytics",
            "state": "granted",
            "granted_at": datetime.now(timezone.utc),
            "withdrawn_at": None,
            "event_id": event_id,
        }
        self.records.append(deepcopy(record))
        return record

    def has_valid_behavioral_analytics(
        self,
        *,
        tenant_id: UUID,
        student_user_id: UUID,
    ) -> bool:
        for record in reversed(self.records):
            if record["tenant_id"] != tenant_id:
                continue
            if record["student_user_id"] != student_user_id:
                continue
            if record["consent_kind"] != "behavioral_analytics":
                continue
            return record["state"] == "granted" and record["withdrawn_at"] is None
        return False
