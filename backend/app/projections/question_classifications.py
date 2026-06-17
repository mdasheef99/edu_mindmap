"""Minimal analytic_rm.question_classifications projection."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping
from uuid import UUID


class InMemoryQuestionClassificationProjectionStore:
    """Analytic rows keyed by the classification event id."""

    def __init__(self) -> None:
        self._rows: dict[str, dict[str, Any]] = {}

    @property
    def rows(self) -> list[dict[str, Any]]:
        return list(self._rows.values())

    def upsert(self, row: Mapping[str, Any]) -> dict[str, Any]:
        stored_row = deepcopy(dict(row))
        self._rows[str(stored_row["event_id"])] = stored_row
        return stored_row


def project_question_classified(event: Mapping[str, Any]) -> dict[str, Any]:
    """Project one question_classified event into analytic_rm.question_classifications."""
    payload = event["payload"]
    return {
        "tenant_id": event["tenant_id"],
        "student_user_id": event["student_id"],
        "session_id": event["session_id"],
        "chapter_id": event["chapter_id"],
        "chapter_analysis_id": event["chapter_analysis_id"],
        "offer_set_id": event["offer_set_id"],
        "event_id": event["event_id"],
        "source_event_id": UUID(payload["source_event_id"]),
        "source_event_type": payload["source_event_type"],
        "source_event_recorded_at_max": payload["source_event_recorded_at_max"],
        "scores_payload": payload["scores_payload"],
        "entropy_payload": payload["entropy_payload"],
        "dispersion_payload": payload["dispersion_payload"],
        "projection_version": event["projection_version"],
        "prompt_version": event["prompt_version"],
        "model_id": event["model_id"],
        "generated_at": event["occurred_at"],
    }