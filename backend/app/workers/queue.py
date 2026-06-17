"""In-memory job queue boundary for early Phase 1 tests."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import UUID, uuid4


class InMemoryJobQueue:
    """Small queued-job store mirroring the Phase 1 Postgres jobs contract."""

    def __init__(self) -> None:
        self.jobs: list[dict[str, Any]] = []

    def enqueue_classify_from_offer_choice(
        self,
        event: Mapping[str, Any],
        *,
        student_user_id: UUID,
    ) -> dict[str, Any]:
        payload = event["payload"]
        idempotency_key = (
            f"classify:{event['tenant_id']}:{payload['offer_set_id']}"
            f":{student_user_id}:{payload['selected_option_id']}"
        )
        for existing_job in self.jobs:
            if existing_job["idempotency_key"] == idempotency_key:
                return deepcopy(existing_job)

        job = {
            "job_id": uuid4(),
            "job_type": "classify",
            "tenant_id": event["tenant_id"],
            "payload": {
                "event_id": str(event["event_id"]),
                "student_user_id": str(student_user_id),
                "session_id": payload["session_id"],
                "offer_set_id": payload["offer_set_id"],
                "selected_option_id": payload["selected_option_id"],
                "selected_option_text": payload["selected_option_text"],
                "thread_context_id": payload["thread_context_id"],
            },
            "status": "queued",
            "attempts": 0,
            "run_after": datetime.now(timezone.utc),
            "locked_at": None,
            "locked_by": None,
            "last_error": None,
            "idempotency_key": idempotency_key,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        stored_job = deepcopy(job)
        self.jobs.append(stored_job)
        return stored_job

    def claim_next_ready(self, *, job_type: str, worker_id: str) -> dict[str, Any] | None:
        now = datetime.now(timezone.utc)
        for job in self.jobs:
            if job["job_type"] != job_type or job["status"] != "queued":
                continue
            if job["run_after"] > now:
                continue
            job["status"] = "running"
            job["attempts"] += 1
            job["locked_at"] = now
            job["locked_by"] = worker_id
            job["updated_at"] = now
            return deepcopy(job)
        return None

    def mark_done(self, job_id: UUID) -> None:
        for job in self.jobs:
            if job["job_id"] == job_id:
                job["status"] = "done"
                job["updated_at"] = datetime.now(timezone.utc)
                return

    def mark_failed(self, job_id: UUID, *, error: str) -> None:
        for job in self.jobs:
            if job["job_id"] == job_id:
                job["status"] = "failed"
                job["last_error"] = error
                job["updated_at"] = datetime.now(timezone.utc)
                return