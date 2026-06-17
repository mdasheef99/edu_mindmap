"""FastAPI composition root for the Phase 1 walking skeleton."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from fastapi import FastAPI

from app.api.student.offer_choices import router as offer_choice_router
from app.api.student.sessions import router as student_router
from app.domain.student.offer_choices import (
    OfferChoiceContext,
    OfferChoiceRequest,
    OfferChoiceResponse,
    build_offer_set_choice,
)
from app.domain.student.sessions import (
    SessionContext,
    SessionStartRequest,
    StudentSession,
    build_session_started,
)
from app.events.store import InMemoryEventStore
from app.llm_gateway.usage import InMemoryLLMUsageStore
from app.observability.sentry import init_sentry
from app.projections.question_classifications import (
    InMemoryQuestionClassificationProjectionStore,
)
from app.projections.student_sessions import (
    InMemoryStudentSessionProjectionStore,
    project_session_started,
)
from app.tenancy.consent import InMemoryConsentRecordStore
from app.tenancy.pool import InMemoryTenantConnectionPool
from app.workers.queue import InMemoryJobQueue


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
    tenant_pool: InMemoryTenantConnectionPool | None = None

    def __post_init__(self) -> None:
        if self.tenant_pool is None:
            self.tenant_pool = InMemoryTenantConnectionPool(self.student_sessions)

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
        tenant_pool: InMemoryTenantConnectionPool | None = None,
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
            tenant_pool=tenant_pool or InMemoryTenantConnectionPool(session_store),
        )

    def start_session(self, payload: SessionStartRequest) -> StudentSession:
        event, _, response_model = build_session_started(
            context=SessionContext(
                tenant_id=self.tenant_id,
                student_user_id=self.student_user_id,
            ),
            request=payload,
        )
        stored_event = self.event_store.append(event, producer="server")
        self.student_sessions.upsert(project_session_started(stored_event))
        return response_model

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

    def record_offer_choice(
        self,
        *,
        offer_set_id: UUID,
        payload: OfferChoiceRequest,
    ) -> OfferChoiceResponse:
        event, response_model = build_offer_set_choice(
            context=OfferChoiceContext(
                tenant_id=self.tenant_id,
                student_user_id=self.student_user_id,
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
                    student_user_id=self.student_user_id,
                )
        except Exception:
            self.event_store.rollback_to(event_count)
            raise
        return response_model

    def grant_behavioral_analytics_consent(self) -> None:
        self.consent_records.grant_behavioral_analytics(
            tenant_id=self.tenant_id,
            student_user_id=self.student_user_id,
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
    return app
