"""Postgres `SKIP LOCKED` job queue implementation."""

from __future__ import annotations

import json
from typing import Any, Mapping
from uuid import UUID


ENQUEUE_CLASSIFY_SQL = """
INSERT INTO jobs (job_type, tenant_id, payload, idempotency_key)
VALUES ('classify', %(tenant_id)s, %(payload)s::jsonb, %(idempotency_key)s)
ON CONFLICT (tenant_id, job_type, idempotency_key) DO UPDATE
SET updated_at = jobs.updated_at
RETURNING *
"""

CLAIM_NEXT_SQL = """
WITH claimed AS (
    SELECT job_id
    FROM jobs
    WHERE job_type = %(job_type)s
      AND status = 'queued'
      AND run_after <= now()
    ORDER BY created_at
    FOR UPDATE SKIP LOCKED
    LIMIT 1
)
UPDATE jobs
SET status = 'running',
    attempts = attempts + 1,
    locked_at = now(),
    locked_by = %(worker_id)s,
    updated_at = now()
WHERE job_id IN (SELECT job_id FROM claimed)
RETURNING *
"""


class PostgresJobQueue:
    """Queue adapter backed by migration 0001 `jobs`."""

    def __init__(self, connection: Any) -> None:
        self.connection = connection

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
        params = {
            "tenant_id": event["tenant_id"],
            "payload": json.dumps({
                "event_id": str(event["event_id"]),
                "student_user_id": str(student_user_id),
                "session_id": payload["session_id"],
                "offer_set_id": payload["offer_set_id"],
                "selected_option_id": payload["selected_option_id"],
                "selected_option_text": payload["selected_option_text"],
                "thread_context_id": payload["thread_context_id"],
            }),
            "idempotency_key": idempotency_key,
        }
        cursor = self.connection.execute(ENQUEUE_CLASSIFY_SQL, params)
        return _row_to_dict(cursor.fetchone())

    def claim_next_ready(self, *, job_type: str, worker_id: str) -> dict[str, Any] | None:
        cursor = self.connection.execute(
            CLAIM_NEXT_SQL,
            {"job_type": job_type, "worker_id": worker_id},
        )
        row = cursor.fetchone()
        return None if row is None else _row_to_dict(row)

    def mark_done(self, job_id: UUID) -> None:
        self.connection.execute(
            "UPDATE jobs SET status = 'done', updated_at = now() WHERE job_id = %s",
            (job_id,),
        )

    def mark_failed(self, job_id: UUID, *, error: str) -> None:
        self.connection.execute(
            "UPDATE jobs SET status = 'failed', last_error = %s, updated_at = now() WHERE job_id = %s",
            (error, job_id),
        )


def _row_to_dict(row: Any) -> dict[str, Any]:
    if isinstance(row, Mapping):
        result = dict(row)
        return _decode_payload(result)
    if hasattr(row, "_asdict"):
        return _decode_payload(dict(row._asdict()))
    return _decode_payload(dict(row))


def _decode_payload(row: dict[str, Any]) -> dict[str, Any]:
    payload = row.get("payload")
    if isinstance(payload, str):
        row["payload"] = json.loads(payload)
    return row