"""SessionRuntime DI container — the in-process runtime facade.

Each method is a thin delegator to a dedicated workflow module so that
the class itself stays under 300 lines and logic stays layered.

Traceability: CODEBASE_INTELLIGENCE/01-system-map.md §Backend → Runtime
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, cast
from uuid import UUID

from app.domain.auth import AuthContext
from app.domain.curriculum import TeacherChapterGraph
from app.domain.student.deletions import NodeDeletionResponse
from app.domain.student.nodes import NodePositionResponse, NodePositionUpdate
from app.domain.student.offer_choices import OfferChoiceRequest, OfferChoiceResponse
from app.domain.student.offer_sets import (
    EdgeOfferSetRequest,
    EdgeOfferSetResponse,
    PhraseOfferSetRequest,
    PhraseOfferSetResponse,
)
from app.domain.student.sessions import (
    SessionStartRequest,
    StudentSession,
    StudentSessionWithCanvas,
)
from app.events.store import InMemoryEventStore
from app.generation.fixture_electricity import ElectricityFixtureProvider
from app.generation.provider import GenerationProvider
from app.llm_gateway.usage import InMemoryLLMUsageStore
from app.projections.catalog import InMemoryCatalogStore
from app.projections.curriculum import InMemoryCurriculumStore
from app.projections.question_classifications import (
    InMemoryQuestionClassificationProjectionStore,
)
from app.projections.student_sessions import InMemoryStudentSessionProjectionStore
from app.runtime.canvas_deletion import delete_node_cascade_workflow
from app.runtime.curriculum_workflow import render_teacher_chapter_graph
from app.runtime.node_position_workflow import update_node_position_workflow
from app.runtime.offer_workflow import (
    create_edge_offer_set_workflow,
    create_phrase_offer_set_workflow,
    record_offer_choice_workflow,
)
from app.runtime.ports import (
    ConsentRecordStorePort,
    EventStorePort,
    JobQueuePort,
    MembershipStorePort,
    StudentSessionStorePort,
    TenantPoolPort,
)
from app.runtime.session_workflow import (
    get_student_session_with_canvas_workflow,
    record_behavioral_analytics_consent_workflow,
    resume_student_session_workflow,
    start_session_workflow,
)
from app.tenancy.consent import InMemoryConsentRecordStore
from app.tenancy.membership_auth import (
    UserIdVerifier,
    build_hs256_fixture_verifier,
    resolve_membership_auth,
)
from app.tenancy.memberships import InMemoryMembershipStore
from app.tenancy.pool import InMemoryTenantConnectionPool
from app.workers.queue import InMemoryJobQueue


@dataclass
class SessionRuntime:
    """In-process runtime DI container used by the FastAPI composition root.

    All domain orchestration is delegated to typed workflow functions;
    this class is responsible only for wiring and for the ``for_testing``
    convenience factory used by every integration test.
    """

    tenant_id: UUID
    student_user_id: UUID
    verify_user_id: UserIdVerifier
    event_store: EventStorePort = field(default_factory=InMemoryEventStore)
    job_queue: JobQueuePort = field(default_factory=InMemoryJobQueue)
    student_sessions: StudentSessionStorePort = field(
        default_factory=InMemoryStudentSessionProjectionStore
    )
    analytic_question_classifications: Any = field(
        default_factory=InMemoryQuestionClassificationProjectionStore
    )
    consent_records: ConsentRecordStorePort = field(default_factory=InMemoryConsentRecordStore)
    llm_usage: Any = field(default_factory=InMemoryLLMUsageStore)
    catalog: Any = field(default_factory=InMemoryCatalogStore)
    curriculum: Any = field(default_factory=InMemoryCurriculumStore)
    generation_provider: GenerationProvider = field(default_factory=ElectricityFixtureProvider)
    tenant_pool: TenantPoolPort | None = None
    jwt_secret: str | None = None
    memberships: MembershipStorePort = field(default_factory=InMemoryMembershipStore)

    def __post_init__(self) -> None:
        if self.tenant_pool is None:
            session_store = cast(InMemoryStudentSessionProjectionStore, self.student_sessions)
            self.tenant_pool = cast(
                TenantPoolPort,
                InMemoryTenantConnectionPool(session_store),
            )

    def resolve_auth(self, token: str) -> AuthContext:
        """Verify JWT and resolve user_id → tenant/role from memberships."""
        return resolve_membership_auth(
            token,
            verify_user_id=self.verify_user_id,
            memberships=self.memberships,
        )

    def bootstrap_b2c_student_membership(self, token: str) -> AuthContext:
        """Verify JWT and idempotently create the M4 B2C student membership."""
        user_id = self.verify_user_id(token)
        membership = self.memberships.ensure_student_membership(
            user_id=user_id,
            tenant_id=self.tenant_id,
        )
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
        catalog: InMemoryCatalogStore | None = None,
        curriculum: InMemoryCurriculumStore | None = None,
        generation_provider: GenerationProvider | None = None,
        tenant_pool: InMemoryTenantConnectionPool | None = None,
        jwt_secret: str | None = None,
        memberships: InMemoryMembershipStore | None = None,
    ) -> "SessionRuntime":
        session_store = student_sessions or InMemoryStudentSessionProjectionStore()
        fixture_secret = jwt_secret or "test-secret"
        return cls(
            tenant_id=tenant_id,
            student_user_id=student_user_id,
            verify_user_id=build_hs256_fixture_verifier(fixture_secret),
            event_store=event_store or InMemoryEventStore(),
            job_queue=job_queue or InMemoryJobQueue(),
            student_sessions=session_store,
            analytic_question_classifications=analytic_question_classifications
            or InMemoryQuestionClassificationProjectionStore(),
            consent_records=consent_records or InMemoryConsentRecordStore(),
            llm_usage=llm_usage or InMemoryLLMUsageStore(),
            catalog=catalog or InMemoryCatalogStore(),
            curriculum=curriculum or InMemoryCurriculumStore(),
            generation_provider=generation_provider or ElectricityFixtureProvider(),
            tenant_pool=cast(
                TenantPoolPort,
                tenant_pool or InMemoryTenantConnectionPool(session_store),
            ),
            jwt_secret=fixture_secret,
            memberships=memberships or InMemoryMembershipStore(),
        )

    # ── Session lifecycle ────────────────────────────────────────────────────

    def start_session(
        self, payload: SessionStartRequest, *, auth: AuthContext | None = None
    ) -> StudentSession:
        resolved = auth or AuthContext(
            user_id=self.student_user_id, tenant_id=self.tenant_id, role="student"
        )
        return start_session_workflow(
            payload,
            auth=resolved,
            event_store=self.event_store,
            student_sessions=self.student_sessions,
            curriculum=self.curriculum,
            generation_provider=self.generation_provider,
            consent_records=self.consent_records,
        )

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

    def get_student_session_with_canvas(
        self, *, session_id: UUID, auth: AuthContext
    ) -> StudentSessionWithCanvas | None:
        assert self.tenant_pool is not None
        return get_student_session_with_canvas_workflow(
            session_id=session_id,
            auth=auth,
            event_store=self.event_store,
            tenant_pool=self.tenant_pool,
        )

    def resume_student_session(
        self, *, session_id: UUID, auth: AuthContext
    ) -> StudentSession | None:
        assert self.tenant_pool is not None
        return resume_student_session_workflow(
            session_id=session_id,
            auth=auth,
            event_store=self.event_store,
            student_sessions=self.student_sessions,
            tenant_pool=self.tenant_pool,
        )

    # ── Teacher / curriculum ──────────────────────────────────────────────────

    def render_teacher_chapter(self, *, chapter_id: UUID, auth: AuthContext) -> TeacherChapterGraph:
        return render_teacher_chapter_graph(
            chapter_id=chapter_id,
            auth=auth,
            curriculum=self.curriculum,
        )

    # ── Offer workflows ───────────────────────────────────────────────────────

    def record_offer_choice(
        self,
        *,
        offer_set_id: UUID,
        payload: OfferChoiceRequest,
        auth: AuthContext | None = None,
    ) -> OfferChoiceResponse | None:
        assert self.tenant_pool is not None
        return record_offer_choice_workflow(
            offer_set_id=offer_set_id,
            payload=payload,
            auth=auth,
            fallback_user_id=self.student_user_id,
            fallback_tenant_id=self.tenant_id,
            tenant_pool=self.tenant_pool,
            event_store=self.event_store,
            job_queue=self.job_queue,
            generation_provider=self.generation_provider,
        )

    def create_edge_offer_set(
        self,
        *,
        payload: EdgeOfferSetRequest,
        auth: AuthContext | None = None,
    ) -> EdgeOfferSetResponse | None:
        assert self.tenant_pool is not None
        return create_edge_offer_set_workflow(
            payload=payload,
            auth=auth,
            fallback_user_id=self.student_user_id,
            fallback_tenant_id=self.tenant_id,
            tenant_pool=self.tenant_pool,
            event_store=self.event_store,
        )

    def create_phrase_offer_set(
        self,
        *,
        payload: PhraseOfferSetRequest,
        auth: AuthContext | None = None,
    ) -> PhraseOfferSetResponse | None:
        assert self.tenant_pool is not None
        return create_phrase_offer_set_workflow(
            payload=payload,
            auth=auth,
            fallback_user_id=self.student_user_id,
            fallback_tenant_id=self.tenant_id,
            tenant_pool=self.tenant_pool,
            event_store=self.event_store,
        )

    # ── Node operations ───────────────────────────────────────────────────────

    def delete_student_node(
        self,
        *,
        session_id: UUID,
        node_id: UUID,
        confirmed: bool,
        auth: AuthContext,
    ) -> NodeDeletionResponse | None:
        assert self.tenant_pool is not None
        return delete_node_cascade_workflow(
            session_id=session_id,
            node_id=node_id,
            confirmed=confirmed,
            auth=auth,
            tenant_pool=self.tenant_pool,
            event_store=self.event_store,
        )

    def update_node_position(
        self,
        *,
        session_id: UUID,
        node_id: UUID,
        payload: NodePositionUpdate,
        auth: AuthContext,
    ) -> NodePositionResponse | None:
        assert self.tenant_pool is not None
        return update_node_position_workflow(
            session_id=session_id,
            node_id=node_id,
            payload=payload,
            auth=auth,
            event_store=self.event_store,
            tenant_pool=self.tenant_pool,
        )

    # ── Consent ───────────────────────────────────────────────────────────────

    def grant_behavioral_analytics_consent(self, *, auth: AuthContext | None = None) -> None:
        resolved = auth or AuthContext(
            user_id=self.student_user_id, tenant_id=self.tenant_id, role="student"
        )
        record_behavioral_analytics_consent_workflow(
            auth=resolved,
            event_store=self.event_store,
            consent_records=self.consent_records,
        )
