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

from uuid import UUID, uuid4

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
from app.tenancy.memberships import InMemoryMembershipStore  # re-exported for backward compat
from app.projections.catalog import seed_m4_electricity_catalog
from app.projections.curriculum import CurriculumIngestInput, build_curriculum_rows

__all__ = ["SessionRuntime", "InMemoryMembershipStore", "create_app"]


def create_app(runtime: SessionRuntime | None = None) -> FastAPI:
    init_sentry()
    app = FastAPI(title="Mindmap Phase 1 Walking Skeleton")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:8099",
            "http://127.0.0.1:8099",
            "http://localhost:8100",
            "http://127.0.0.1:8100",
        ],
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )
    app.state.session_runtime = runtime or _m4_default_runtime()
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


def _m4_default_runtime() -> SessionRuntime:
    runtime = SessionRuntime.for_testing(
        tenant_id=UUID("00000000-0000-4000-8000-000000000010"),
        student_user_id=uuid4(),
    )
    seed = seed_m4_electricity_catalog(runtime.catalog, tenant_id=runtime.tenant_id)
    runtime.curriculum.ingest(
        build_curriculum_rows(
            CurriculumIngestInput(
                tenant_id=runtime.tenant_id,
                exam_id=seed.exam_id,
                subject_id=seed.subject_id,
                chapter_id=seed.chapter_id,
                title="Electricity",
                chapter_analysis_id=seed.chapter_analysis_id,
                segment_index_version="m4-fixture-v1",
                pipeline_version="m4-fixture-v1",
                prompt_version="fixture-electricity-v1",
                model_id="fixture",
                pages=["Electric current flows through a closed circuit."],
                named_concepts=[
                    {
                        "concept_id": str(seed.root_concept_entry_id),
                        "label": "Electricity overview",
                        "definition": "A chapter-level entry point.",
                        "category_tag": "overview",
                        "passage_refs": {
                            "definitional": [f"{seed.chapter_id}_para_001"],
                            "explanatory": [],
                            "application": [],
                        },
                    }
                ],
                embedded_concepts=[],
                edges=[],
            )
        )
    )
    return runtime
