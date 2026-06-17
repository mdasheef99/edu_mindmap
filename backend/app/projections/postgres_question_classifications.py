"""Postgres-backed analytic question-classification projection writer."""

from __future__ import annotations

import json
from typing import Any, Mapping

from app.tenancy.postgres_context import set_local_tenant

INSERT_QUESTION_CLASSIFICATION_SQL = """
INSERT INTO analytic_rm.question_classifications (
    tenant_id, student_user_id, session_id, chapter_id, chapter_analysis_id,
    offer_set_id, event_id, source_event_id, source_event_type,
    source_event_recorded_at_max, scores_payload, entropy_payload,
    dispersion_payload, projection_version, prompt_version, model_id, generated_at
) VALUES (
    %(tenant_id)s, %(student_user_id)s, %(session_id)s, %(chapter_id)s,
    %(chapter_analysis_id)s, %(offer_set_id)s, %(event_id)s, %(source_event_id)s,
    %(source_event_type)s, %(source_event_recorded_at_max)s, %(scores_payload)s::jsonb,
    %(entropy_payload)s::jsonb, %(dispersion_payload)s::jsonb, %(projection_version)s,
    %(prompt_version)s, %(model_id)s, %(generated_at)s
)
RETURNING *
"""


class PostgresQuestionClassificationProjectionStore:
    """Append projection rows under tenant RLS context."""

    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def upsert(self, row: Mapping[str, Any]) -> dict[str, Any]:
        params = dict(row)
        for key in ("scores_payload", "entropy_payload", "dispersion_payload"):
            params[key] = json.dumps(params[key], default=str)
        with self.connection.transaction():
            set_local_tenant(self.connection, row["tenant_id"])
            cursor = self.connection.execute(INSERT_QUESTION_CLASSIFICATION_SQL, params)
            stored = cursor.fetchone()
        return dict(stored)
