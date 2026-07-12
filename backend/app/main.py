"""FastAPI composition root for the Phase 1 walking skeleton."""

from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.student.events import router as student_events_router
from app.api.student.nodes import router as node_router
from app.api.student.offer_choices import router as offer_choice_router
from app.api.student.offer_sets import router as offer_set_router
from app.api.student.sessions import router as student_router
from app.api.teacher.chapters import router as teacher_chapter_router
from app.configuration import allowed_origins
from app.observability.sentry import init_sentry
from app.runtime.session import SessionRuntime
from app.tenancy.memberships import InMemoryMembershipStore

__all__ = ["SessionRuntime", "InMemoryMembershipStore", "create_app"]


def create_app(runtime: SessionRuntime | None = None) -> FastAPI:
    init_sentry()
    app = FastAPI(title="Mindmap Phase 1 Walking Skeleton")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins(),
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )
    app.state.session_runtime = runtime or SessionRuntime.for_testing(
        tenant_id=uuid4(),
        student_user_id=uuid4(),
    )
    app.include_router(node_router)
    app.include_router(student_events_router)
    app.include_router(offer_choice_router)
    app.include_router(offer_set_router)
    app.include_router(student_router)
    app.include_router(teacher_chapter_router)
    return app
