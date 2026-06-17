"""Minimal classify worker for the first Phase 1 async slice."""

from __future__ import annotations

from typing import Any, Mapping

from app.domain.analytic.question_classifications import build_question_classified
from app.llm_gateway.classification_fixture import classify_selected_option
from app.projections.question_classifications import project_question_classified


class ClassifyWorker:
    """Claims one classify job, appends question_classified, and projects analytic state."""

    def __init__(self, runtime: Any) -> None:
        self.runtime = runtime

    def claim_next(self, *, worker_id: str) -> dict[str, Any] | None:
        return self.runtime.job_queue.claim_next_ready(
            job_type="classify",
            worker_id=worker_id,
        )

    def run_next(self, *, worker_id: str) -> Mapping[str, Any] | None:
        job = self.claim_next(worker_id=worker_id)
        if job is None:
            return None

        session_row = self.runtime.student_sessions.get_for_tenant(
            job["payload"]["session_id"],
            job["tenant_id"],
        )
        if session_row is None:
            self.runtime.job_queue.mark_failed(job["job_id"], error="session_not_found")
            return None

        source_event = self._get_source_event(
            job["payload"]["event_id"], tenant_id=job["tenant_id"]
        )
        classification = classify_selected_option(
            job["payload"]["selected_option_text"],
            tenant_id=job["tenant_id"],
            usage_store=getattr(self.runtime, "llm_usage", None),
        )
        event = build_question_classified(
            tenant_id=job["tenant_id"],
            student_user_id=session_row["student_user_id"],
            session_row=session_row,
            source_event=source_event,
            classification=classification,
        )
        stored_event = self.runtime.event_store.append(event, producer="worker")
        if self.runtime.consent_records.has_valid_behavioral_analytics(
            tenant_id=job["tenant_id"],
            student_user_id=session_row["student_user_id"],
        ):
            self.runtime.analytic_question_classifications.upsert(
                project_question_classified(stored_event)
            )
        self.runtime.job_queue.mark_done(job["job_id"])
        return stored_event

    def _get_source_event(
        self, event_id: str, *, tenant_id: Any | None = None
    ) -> Mapping[str, Any]:
        if hasattr(self.runtime.event_store, "get_event_by_id"):
            return self.runtime.event_store.get_event_by_id(event_id, tenant_id=tenant_id)
        return next(
            event
            for event in reversed(self.runtime.event_store.events)
            if str(event["event_id"]) == event_id
        )
