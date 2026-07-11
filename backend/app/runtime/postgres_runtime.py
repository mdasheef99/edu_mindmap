"""Durable Postgres composition for the FastAPI student runtime."""

from __future__ import annotations

import os
from functools import wraps
from typing import Any, Callable, TypeVar
from uuid import UUID

from app.events.postgres_store import PostgresEventStore
from app.generation.fixture_electricity import ElectricityFixtureProvider
from app.llm_gateway.postgres_usage import PostgresLLMUsageStore
from app.projections.curriculum_postgres import PostgresCurriculumStore
from app.projections.postgres_catalog import PostgresCatalogStore
from app.projections.postgres_question_classifications import (
    PostgresQuestionClassificationProjectionStore,
)
from app.projections.postgres_student_sessions import PostgresStudentSessionStore
from app.runtime.session import SessionRuntime
from app.tenancy.postgres_consent import PostgresConsentRecordStore
from app.tenancy.postgres_context import set_local_tenant
from app.tenancy.postgres_memberships import PostgresMembershipStore
from app.tenancy.postgres_pool import PooledConnectionProxy, PostgresTenantConnectionPool
from app.workers.postgres_queue import PostgresJobQueue

_F = TypeVar("_F", bound=Callable[..., Any])


def _atomic(method: _F) -> _F:
    """Run one runtime operation on one pooled connection/outer transaction."""

    @wraps(method)
    def wrapped(self: "PostgresSessionRuntime", *args: Any, **kwargs: Any) -> Any:
        with self.database.transaction():
            set_local_tenant(self.database, self.tenant_id)
            return method(self, *args, **kwargs)

    return wrapped  # type: ignore[return-value]


class PostgresSessionRuntime(SessionRuntime):
    """SessionRuntime behavior with atomic pooled Postgres operations."""

    database: PooledConnectionProxy

    @_atomic
    def resolve_auth(self, *args: Any, **kwargs: Any) -> Any:
        return super().resolve_auth(*args, **kwargs)

    @_atomic
    def bootstrap_b2c_student_membership(self, *args: Any, **kwargs: Any) -> Any:
        return super().bootstrap_b2c_student_membership(*args, **kwargs)

    @_atomic
    def start_session(self, *args: Any, **kwargs: Any) -> Any:
        return super().start_session(*args, **kwargs)

    @_atomic
    def get_student_session(self, *args: Any, **kwargs: Any) -> Any:
        return super().get_student_session(*args, **kwargs)

    @_atomic
    def get_student_session_via_pool(self, *args: Any, **kwargs: Any) -> Any:
        return super().get_student_session_via_pool(*args, **kwargs)

    @_atomic
    def list_recent_student_sessions(self, *args: Any, **kwargs: Any) -> Any:
        return super().list_recent_student_sessions(*args, **kwargs)

    @_atomic
    def get_student_session_with_canvas(self, *args: Any, **kwargs: Any) -> Any:
        return super().get_student_session_with_canvas(*args, **kwargs)

    @_atomic
    def resume_student_session(self, *args: Any, **kwargs: Any) -> Any:
        return super().resume_student_session(*args, **kwargs)

    @_atomic
    def render_teacher_chapter(self, *args: Any, **kwargs: Any) -> Any:
        return super().render_teacher_chapter(*args, **kwargs)

    @_atomic
    def record_offer_choice(self, *args: Any, **kwargs: Any) -> Any:
        return super().record_offer_choice(*args, **kwargs)

    @_atomic
    def create_edge_offer_set(self, *args: Any, **kwargs: Any) -> Any:
        return super().create_edge_offer_set(*args, **kwargs)

    @_atomic
    def create_phrase_offer_set(self, *args: Any, **kwargs: Any) -> Any:
        return super().create_phrase_offer_set(*args, **kwargs)

    @_atomic
    def delete_student_node(self, *args: Any, **kwargs: Any) -> Any:
        return super().delete_student_node(*args, **kwargs)

    @_atomic
    def update_node_position(self, *args: Any, **kwargs: Any) -> Any:
        return super().update_node_position(*args, **kwargs)

    @_atomic
    def grant_behavioral_analytics_consent(self, *args: Any, **kwargs: Any) -> Any:
        return super().grant_behavioral_analytics_consent(*args, **kwargs)

    def close(self) -> None:
        self.database.close()


def build_postgres_runtime(*, database_url: str, supabase_url: str) -> PostgresSessionRuntime:
    """Compose the API and worker-facing stores over one pooled Postgres database."""
    tenant_id = UUID(
        os.getenv("M4_INDIVIDUAL_TENANT_ID", "00000000-0000-4000-8000-000000000010")
    )
    database = PooledConnectionProxy(database_url)
    issuer = os.getenv("SUPABASE_AUTH_URL") or f"{supabase_url.rstrip('/')}/auth/v1"
    jwks_url = os.getenv("SUPABASE_JWT_JWKS_URL") or f"{issuer}/.well-known/jwks.json"
    sessions = PostgresStudentSessionStore(database)
    runtime = PostgresSessionRuntime(
        tenant_id=tenant_id,
        student_user_id=UUID("00000000-0000-4000-8000-000000000000"),
        event_store=PostgresEventStore(database),
        job_queue=PostgresJobQueue(database),
        student_sessions=sessions,
        analytic_question_classifications=PostgresQuestionClassificationProjectionStore(database),
        consent_records=PostgresConsentRecordStore(database),
        llm_usage=PostgresLLMUsageStore(database),
        catalog=PostgresCatalogStore(database, tenant_id=tenant_id),
        curriculum=PostgresCurriculumStore(database),
        generation_provider=ElectricityFixtureProvider(),
        tenant_pool=PostgresTenantConnectionPool(database),
        jwt_secret=os.getenv("SUPABASE_JWT_SECRET", "test-fixture-only"),
        jwt_jwks_url=jwks_url,
        jwt_issuer=issuer,
        memberships=PostgresMembershipStore(database, individual_tenant_id=tenant_id),
    )
    runtime.database = database
    return runtime

