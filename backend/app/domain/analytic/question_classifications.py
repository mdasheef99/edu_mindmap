"""Pure worker-side construction for question_classified events."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import UUID, uuid4


QUESTION_CLASSIFICATION_PROJECTION_VERSION = "analytic-question-classification-v1"


def build_question_classified(
    *,
    tenant_id: UUID,
    student_user_id: UUID,
    session_row: Mapping[str, Any],
    source_event: Mapping[str, Any],
    classification: Mapping[str, Any],
    now: datetime | None = None,
    event_id: UUID | None = None,
) -> dict[str, Any]:
    occurred_at = now or datetime.now(timezone.utc)
    resolved_event_id = event_id or uuid4()
    payload = {
        "source_event_id": str(source_event["event_id"]),
        "source_event_type": source_event["event_type"],
        "source_event_recorded_at_max": source_event.get(
            "recorded_at",
            source_event["occurred_at"],
        ),
        "offer_set_id": str(source_event["offer_set_id"]),
        "session_id": str(source_event["session_id"]),
        "selected_option_id": source_event["payload"]["selected_option_id"],
        "selected_option_text": classification["selected_option_text"],
        "thread_context_id": source_event["payload"]["thread_context_id"],
        "scores_payload": classification["scores_payload"],
        "entropy_payload": classification["entropy_payload"],
        "dispersion_payload": classification["dispersion_payload"],
    }
    return {
        "event_id": resolved_event_id,
        "event_type": "question_classified",
        "event_version": 1,
        "tenant_id": tenant_id,
        "student_id": student_user_id,
        "session_id": session_row["session_id"],
        "chapter_id": session_row["chapter_id"],
        "chapter_analysis_id": session_row["chapter_analysis_id"],
        "offer_set_id": source_event["offer_set_id"],
        "occurred_at": occurred_at,
        "prompt_version": classification.get("prompt_version", "question-classifier-fixture-v1"),
        "model_id": classification.get("model_id", "stage-2-classification-fixture-model"),
        "projection_version": QUESTION_CLASSIFICATION_PROJECTION_VERSION,
        "payload": payload,
    }