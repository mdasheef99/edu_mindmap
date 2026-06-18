"""FastAPI composition root for the Phase 1 walking skeleton."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4

from fastapi import FastAPI

from app.api.student.offer_choices import router as offer_choice_router
from app.api.student.sessions import router as student_router
from app.api.teacher.chapters import router as teacher_chapter_router
from app.domain.auth import AuthContext, NoActiveMembershipError
from app.domain.curriculum import ChapterGraphNotFoundError, TeacherChapterGraph
from app.domain.student.offer_choices import (
    OfferChoiceContext,
    OfferChoiceRequest,
    OfferChoiceResponse,
    build_offer_set_choice,
)
from app.domain.student.sessions import (
    ChapterLaunchNotFoundError,
    SessionContext,
    SessionStartRequest,
    StudentSession,
    build_session_resumed,
    build_session_started,
)
from app.events.store import InMemoryEventStore
from app.llm_gateway.usage import InMemoryLLMUsageStore
from app.observability.sentry import init_sentry
from app.projections.curriculum import InMemoryCurriculumStore
from app.projections.question_classifications import (
    InMemoryQuestionClassificationProjectionStore,
)
from app.projections.student_sessions import (
    InMemoryStudentSessionProjectionStore,
    project_session_resumed,
    project_session_started,
)
from app.tenancy.consent import InMemoryConsentRecordStore
from app.tenancy.pool import InMemoryTenantConnectionPool
from app.workers.queue import InMemoryJobQueue


class InMemoryMembershipStore:
    """In-memory membership records for test fixture auth resolution."""

    def __init__(self) -> None:
        self._records: dict[UUID, list[dict[str, Any]]] = {}

    def add_membership(self, *, user_id: UUID, tenant_id: UUID, role: str) -> None:
        self._records.setdefault(user_id, []).append(
            {"user_id": user_id, "tenant_id": tenant_id, "role": role}
        )

    def get_memberships_for_user(self, user_id: UUID) -> list[dict[str, Any]]:
        return self._records.get(user_id, [])


@dataclass
class SessionRuntime:
    tenant_id: UUID
    student_user_id: UUID
    event_store: InMemoryEventStore = field(default_factory=InMemoryEventStore)
    job_queue: InMemoryJobQueue = field(default_factory=InMemoryJobQueue)
    student_sessions: InMemoryStudentSessionProjectionStore = field(
        default_factory=InMemoryStudentSessionProjectionStore
    )
    analytic_question_classifications: InMemoryQuestionClassificationProjectionStore = field(
        default_factory=InMemoryQuestionClassificationProjectionStore
    )
    consent_records: InMemoryConsentRecordStore = field(default_factory=InMemoryConsentRecordStore)
    llm_usage: InMemoryLLMUsageStore = field(default_factory=InMemoryLLMUsageStore)
    curriculum: InMemoryCurriculumStore = field(default_factory=InMemoryCurriculumStore)
    tenant_pool: InMemoryTenantConnectionPool | None = None
    jwt_secret: str = "test-secret"
    memberships: InMemoryMembershipStore = field(default_factory=InMemoryMembershipStore)
    _seen_users: set[UUID] = field(default_factory=set)

    def __post_init__(self) -> None:
        if self.tenant_pool is None:
            self.tenant_pool = InMemoryTenantConnectionPool(self.student_sessions)

    def resolve_auth(self, token: str) -> AuthContext:
        """Verify JWT and resolve user_id → tenant/role from memberships."""
        import jwt

        payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
        user_id = UUID(payload["sub"])
        memberships = self.memberships.get_memberships_for_user(user_id)
        if not memberships:
            raise NoActiveMembershipError("No active membership for authenticated user")
        # Pick the first active membership for the test fixture
        membership = memberships[0]
        return AuthContext(
            user_id=user_id,
            tenant_id=membership["tenant_id"],
            role=membership["role"],
        )

    @classmethod
    def for_testing(
        cls,
        *,
        tenant_id: UUID,
        student_user_id: UUID,
        event_store: InMemoryEventStore | None = None,
        job_queue: InMemoryJobQueue | None = None,
        student_sessions: InMemoryStudentSessionProjectionStore | None = None,
        analytic_question_classifications: InMemoryQuestionClassificationProjectionStore
        | None = None,
        consent_records: InMemoryConsentRecordStore | None = None,
        llm_usage: InMemoryLLMUsageStore | None = None,
        curriculum: InMemoryCurriculumStore | None = None,
        tenant_pool: InMemoryTenantConnectionPool | None = None,
        jwt_secret: str | None = None,
        memberships: InMemoryMembershipStore | None = None,
    ) -> "SessionRuntime":
        session_store = student_sessions or InMemoryStudentSessionProjectionStore()
        return cls(
            tenant_id=tenant_id,
            student_user_id=student_user_id,
            event_store=event_store or InMemoryEventStore(),
            job_queue=job_queue or InMemoryJobQueue(),
            student_sessions=session_store,
            analytic_question_classifications=analytic_question_classifications
            or InMemoryQuestionClassificationProjectionStore(),
            consent_records=consent_records or InMemoryConsentRecordStore(),
            llm_usage=llm_usage or InMemoryLLMUsageStore(),
            curriculum=curriculum or InMemoryCurriculumStore(),
            tenant_pool=tenant_pool or InMemoryTenantConnectionPool(session_store),
            jwt_secret=jwt_secret or "test-secret",
            memberships=memberships or InMemoryMembershipStore(),
        )

    def start_session(
        self, payload: SessionStartRequest, *, auth: AuthContext | None = None
    ) -> StudentSession:
        resolved = auth or AuthContext(
            user_id=self.student_user_id, tenant_id=self.tenant_id, role="student"
        )
        request = self._resolve_session_request(payload, tenant_id=resolved.tenant_id)

        if resolved.user_id not in self._seen_users:
            self._seen_users.add(resolved.user_id)
            from datetime import datetime, timezone

            consent_event = {
                "event_id": uuid4(),
                "event_type": "consent_recorded",
                "event_version": 1,
                "tenant_id": resolved.tenant_id,
                "actor_user_id": resolved.user_id,
                "student_id": resolved.user_id,
                "occurred_at": datetime.now(timezone.utc),
                "payload": {
                    "user_id": str(resolved.user_id),
                    "consent_kind": "behavioral_analytics",
                    "grantor": "self",
                },
            }
            self.event_store.append(consent_event, producer="server")

        event, _, response_model = build_session_started(
            context=SessionContext(
                tenant_id=resolved.tenant_id,
                student_user_id=resolved.user_id,
            ),
            request=request,
        )
        stored_event = self.event_store.append(event, producer="server")
        self.student_sessions.upsert(project_session_started(stored_event))
        return response_model

    def _resolve_session_request(
        self, payload: SessionStartRequest, *, tenant_id: UUID
    ) -> SessionStartRequest:
        chapter = self.curriculum.find_chapter(
            tenant_id=tenant_id,
            exam_id=payload.exam_id,
            subject_id=payload.subject_id,
            chapter_id=payload.chapter_id,
        )
        if chapter is None:
            raise ChapterLaunchNotFoundError("Chapter not found in curriculum")
        return payload.model_copy(update={"chapter_analysis_id": chapter["chapter_analysis_id"]})

    def get_student_session(self, session_id: str) -> StudentSession | None:
        session_row = self.student_sessions.get_for_tenant(session_id, self.tenant_id)
        if session_row is None:
            return None
        return StudentSession.model_validate(session_row)

    def get_student_session_via_pool(self, session_id: str) -> StudentSession | None:
        assert self.tenant_pool is not None
        with self.tenant_pool.transaction(self.tenant_id) as connection:
            session_row = connection.fetch_session(session_id)
        if session_row is None:
            return None
        return StudentSession.model_validate(session_row)

    def list_recent_student_sessions(
        self, *, auth: AuthContext, limit: int = 5
    ) -> list[StudentSession]:
        assert self.tenant_pool is not None
        with self.tenant_pool.transaction(auth.tenant_id) as connection:
            rows = connection.list_recent_sessions(student_user_id=auth.user_id, limit=limit)
        return [StudentSession.model_validate(row) for row in rows]

    def resume_student_session(
        self, *, session_id: UUID, auth: AuthContext
    ) -> StudentSession | None:
        assert self.tenant_pool is not None
        with self.tenant_pool.transaction(auth.tenant_id) as connection:
            session_row = connection.fetch_session_for_student(str(session_id), auth.user_id)
        if session_row is None:
            return None

        event = build_session_resumed(
            context=SessionContext(tenant_id=auth.tenant_id, student_user_id=auth.user_id),
            session_id=session_id,
        )
        stored_event = self.event_store.append(event, producer="server")
        updated_row = self.student_sessions.mark_resumed(project_session_resumed(stored_event))
        return StudentSession.model_validate(updated_row or session_row)

    def render_teacher_chapter(self, *, chapter_id: UUID, auth: AuthContext) -> TeacherChapterGraph:
        graph = self.curriculum.render_chapter_graph(
            tenant_id=auth.tenant_id,
            chapter_id=chapter_id,
        )
        if graph is None:
            raise ChapterGraphNotFoundError("Chapter graph not found")
        return graph

    def record_offer_choice(
        self,
        *,
        offer_set_id: UUID,
        payload: OfferChoiceRequest,
        auth: AuthContext | None = None,
    ) -> OfferChoiceResponse:
        resolved = auth or AuthContext(
            user_id=self.student_user_id, tenant_id=self.tenant_id, role="student"
        )
        event, response_model = build_offer_set_choice(
            context=OfferChoiceContext(
                tenant_id=resolved.tenant_id,
                student_user_id=resolved.user_id,
            ),
            offer_set_id=offer_set_id,
            request=payload,
        )
        event_count = len(self.event_store.events)
        try:
            stored_event = self.event_store.append(event, producer="server")
            if payload.outcome == "selected":
                self.job_queue.enqueue_classify_from_offer_choice(
                    stored_event,
                    student_user_id=resolved.user_id,
                )
        except Exception:
            self.event_store.rollback_to(event_count)
            raise
        return response_model

    def grant_behavioral_analytics_consent(self, *, auth: AuthContext | None = None) -> None:
        resolved = auth or AuthContext(
            user_id=self.student_user_id, tenant_id=self.tenant_id, role="student"
        )
        self.consent_records.grant_behavioral_analytics(
            tenant_id=resolved.tenant_id,
            student_user_id=resolved.user_id,
        )


def create_app(runtime: SessionRuntime | None = None) -> FastAPI:
    init_sentry()
    app = FastAPI(title="Mindmap Phase 1 Walking Skeleton")
    app.state.session_runtime = runtime or SessionRuntime.for_testing(
        tenant_id=uuid4(),
        student_user_id=uuid4(),
    )
    app.include_router(offer_choice_router)
    app.include_router(student_router)
    app.include_router(teacher_chapter_router)
    return app
