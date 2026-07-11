"""Structural ports shared by in-memory tests and durable Postgres runtime adapters.

Traceability: M4 runtime-closure remediation SDD R1; backend-architecture.md §§5-8.
"""

from __future__ import annotations

from contextlib import AbstractContextManager
from typing import Any, Mapping, Protocol
from uuid import UUID

from app.domain.curriculum import TeacherChapterGraph


class EventStorePort(Protocol):
    @property
    def events(self) -> list[dict[str, Any]]: ...

    def append(self, event: Mapping[str, Any], *, producer: str) -> dict[str, Any]: ...

    def rollback_to(self, event_count: int) -> None: ...


class JobQueuePort(Protocol):
    def enqueue_classify_from_offer_choice(
        self, event: Mapping[str, Any], *, student_user_id: UUID
    ) -> dict[str, Any]: ...


class StudentSessionStorePort(Protocol):
    def upsert(self, session_row: Mapping[str, Any]) -> dict[str, Any]: ...

    def get_for_tenant(
        self, session_id: str | UUID, tenant_id: UUID
    ) -> dict[str, Any] | None: ...

    def mark_resumed(self, resume_row: Mapping[str, Any]) -> dict[str, Any] | None: ...


class CurriculumStorePort(Protocol):
    def find_chapter(
        self, *, tenant_id: UUID, exam_id: UUID, subject_id: UUID, chapter_id: UUID
    ) -> Mapping[str, Any] | None: ...

    def render_chapter_graph(
        self, *, tenant_id: UUID, chapter_id: UUID
    ) -> TeacherChapterGraph | None: ...


class ConsentRecordStorePort(Protocol):
    def has_valid_behavioral_analytics(
        self, *, tenant_id: UUID, student_user_id: UUID
    ) -> bool: ...

    def grant_behavioral_analytics(
        self, *, tenant_id: UUID, student_user_id: UUID, event_id: UUID
    ) -> Any: ...


class TenantConnectionPort(Protocol):
    def fetch_session(self, session_id: str) -> Mapping[str, Any] | None: ...

    def fetch_session_for_student(
        self, session_id: str, student_user_id: UUID
    ) -> Mapping[str, Any] | None: ...

    def list_recent_sessions(
        self, *, student_user_id: UUID, limit: int
    ) -> list[Mapping[str, Any]]: ...


class TenantPoolPort(Protocol):
    def transaction(self, tenant_id: UUID) -> AbstractContextManager[TenantConnectionPort]: ...


class MembershipStorePort(Protocol):
    def ensure_student_membership(
        self, *, user_id: UUID, tenant_id: UUID
    ) -> dict[str, Any]: ...

    def get_memberships_for_user(self, user_id: UUID) -> list[dict[str, Any]]: ...
