"""FastAPI composition root for the Phase 1 walking skeleton.

Responsibilities:
- FastAPI app instantiation via ``create_app``.
- CORS + Sentry middleware configuration.
- Router inclusions.
- Re-exports ``SessionRuntime`` and ``InMemoryMembershipStore`` for backward
  compatibility so existing tests and scripts continue to import from here.

Traceability: CODEBASE_INTELLIGENCE/01-system-map.md §Backend → Composition Root
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.student.auth import router as student_auth_router
from app.api.student.curriculum import router as curriculum_router
from app.api.student.dashboard import router as dashboard_router
from app.api.student.events import router as student_events_router
from app.api.student.nodes import router as node_router
from app.api.student.offer_choices import router as offer_choice_router
from app.api.student.offer_sets import router as offer_set_router
from app.api.student.sessions import router as student_router
from app.api.teacher.chapters import router as teacher_chapter_router
from app.observability.sentry import init_sentry
from app.runtime.session import SessionRuntime  # re-exported for backward compat
from app.runtime.postgres_runtime import build_postgres_runtime
from app.tenancy.memberships import InMemoryMembershipStore  # re-exported for backward compat

__all__ = ["SessionRuntime", "InMemoryMembershipStore", "create_app"]


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    close = getattr(app.state.session_runtime, "close", None)
    if callable(close):
        close()


def create_app(runtime: SessionRuntime | None = None) -> FastAPI:
    init_sentry()
    if runtime is None:
        database_url = os.getenv("DATABASE_URL")
        supabase_url = os.getenv("SUPABASE_URL")
        if not database_url:
            raise RuntimeError("DATABASE_URL is required for the production API runtime")
        if not supabase_url:
            raise RuntimeError("SUPABASE_URL is required for ES256/JWKS token verification")
        runtime = build_postgres_runtime(
            database_url=database_url,
            supabase_url=supabase_url,
        )

    app = FastAPI(title="Mindmap M4 Student API", lifespan=_lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:8099",
            "http://127.0.0.1:8099",
            "http://localhost:8100",
            "http://127.0.0.1:8100",
            "http://localhost:8081",
            "http://127.0.0.1:8081",
        ],
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )
    app.state.session_runtime = runtime
    app.include_router(student_auth_router)
    app.include_router(node_router)
    app.include_router(curriculum_router)
    app.include_router(dashboard_router)
    app.include_router(student_events_router)
    app.include_router(offer_choice_router)
    app.include_router(offer_set_router)
    app.include_router(student_router)
    app.include_router(teacher_chapter_router)

    return app
