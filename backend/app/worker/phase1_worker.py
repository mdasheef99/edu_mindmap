"""Phase 1 Postgres-backed worker entrypoint.

Traceability:
- docs/planning/sdd/phase-1-walking-skeleton-sdd.md §10
- docs/architecture/backend-architecture.md §8, §9, §12
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass

from psycopg.rows import dict_row

from app.events.postgres_store import PostgresEventStore
from app.llm_gateway.postgres_usage import PostgresLLMUsageStore
from app.projections.postgres_question_classifications import (
    PostgresQuestionClassificationProjectionStore,
)
from app.projections.postgres_student_sessions import PostgresStudentSessionStore
from app.tenancy.postgres_consent import PostgresConsentRecordStore
from app.workers.classify import ClassifyWorker
from app.workers.postgres_queue import PostgresJobQueue


@dataclass
class PostgresWorkerRuntime:
    event_store: PostgresEventStore
    job_queue: PostgresJobQueue
    student_sessions: PostgresStudentSessionStore
    consent_records: PostgresConsentRecordStore
    analytic_question_classifications: PostgresQuestionClassificationProjectionStore
    llm_usage: PostgresLLMUsageStore


def build_runtime(connection) -> PostgresWorkerRuntime:
    return PostgresWorkerRuntime(
        event_store=PostgresEventStore(connection),
        job_queue=PostgresJobQueue(connection),
        student_sessions=PostgresStudentSessionStore(connection),
        consent_records=PostgresConsentRecordStore(connection),
        analytic_question_classifications=PostgresQuestionClassificationProjectionStore(connection),
        llm_usage=PostgresLLMUsageStore(connection),
    )


def run_once(connection, *, worker_id: str) -> bool:
    worker = ClassifyWorker(build_runtime(connection))
    return worker.run_next(worker_id=worker_id) is not None


def run_loop(connection, *, worker_id: str, poll_seconds: float = 2.0) -> None:
    while True:
        did_work = run_once(connection, worker_id=worker_id)
        if not did_work:
            time.sleep(poll_seconds)


def main() -> None:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is required for the Phase 1 Postgres worker.")

    import psycopg

    worker_id = os.getenv("WORKER_ID", "phase1-worker")
    once = os.getenv("PHASE1_WORKER_ONCE", "false").lower() == "true"
    poll_seconds = float(os.getenv("PHASE1_WORKER_POLL_SECONDS", "2"))

    with psycopg.connect(database_url, row_factory=dict_row) as connection:
        if once:
            run_once(connection, worker_id=worker_id)
        else:
            run_loop(connection, worker_id=worker_id, poll_seconds=poll_seconds)


if __name__ == "__main__":
    main()
