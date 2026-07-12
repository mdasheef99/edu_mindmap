"""Student-safe curriculum catalog endpoints for M4."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request

from app.domain.auth import AuthContext
from app.domain.student.curriculum import (
    ChapterDetailResponse,
    ChapterListResponse,
    ClassListResponse,
    ConceptEntryListResponse,
    ExamListResponse,
    SubjectListResponse,
)
from app.tenancy.auth import get_auth_context

router = APIRouter(prefix="/v1/student", tags=["student"])


@router.get("/curriculum/classes", response_model=ClassListResponse)
def list_classes(
    request: Request,
    auth: AuthContext = Depends(get_auth_context),
) -> ClassListResponse:
    _require_student(auth)
    return ClassListResponse(items=request.app.state.session_runtime.catalog.list_classes())


@router.get("/curriculum/exams", response_model=ExamListResponse)
def list_exams(
    class_id: UUID,
    request: Request,
    auth: AuthContext = Depends(get_auth_context),
) -> ExamListResponse:
    _require_student(auth)
    return ExamListResponse(
        items=request.app.state.session_runtime.catalog.list_exams(class_level_id=class_id)
    )


@router.get("/curriculum/subjects", response_model=SubjectListResponse)
def list_subjects(
    class_id: UUID,
    exam_id: UUID,
    request: Request,
    auth: AuthContext = Depends(get_auth_context),
) -> SubjectListResponse:
    _require_student(auth)
    return SubjectListResponse(
        items=request.app.state.session_runtime.catalog.list_subjects(
            class_level_id=class_id,
            exam_id=exam_id,
        )
    )


@router.get("/curriculum/chapters", response_model=ChapterListResponse)
def list_chapters(
    class_id: UUID,
    exam_id: UUID,
    subject_id: UUID,
    request: Request,
    auth: AuthContext = Depends(get_auth_context),
) -> ChapterListResponse:
    _require_student(auth)
    return ChapterListResponse(
        items=request.app.state.session_runtime.catalog.list_chapters(
            tenant_id=auth.tenant_id,
            class_level_id=class_id,
            exam_id=exam_id,
            subject_id=subject_id,
        )
    )


@router.get("/chapters/{chapter_id}", response_model=ChapterDetailResponse)
def get_chapter(
    chapter_id: UUID,
    request: Request,
    auth: AuthContext = Depends(get_auth_context),
) -> ChapterDetailResponse:
    _require_student(auth)
    catalog = request.app.state.session_runtime.catalog
    chapter = catalog.get_chapter(tenant_id=auth.tenant_id, chapter_id=chapter_id)
    if chapter is None:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return ChapterDetailResponse(
        chapter=chapter,
        concept_entries=catalog.list_concept_entries(chapter_id=chapter_id),
    )


@router.get("/chapters/{chapter_id}/concept-entries", response_model=ConceptEntryListResponse)
def list_concept_entries(
    chapter_id: UUID,
    request: Request,
    auth: AuthContext = Depends(get_auth_context),
) -> ConceptEntryListResponse:
    _require_student(auth)
    chapter = request.app.state.session_runtime.catalog.get_chapter(
        tenant_id=auth.tenant_id,
        chapter_id=chapter_id,
    )
    if chapter is None:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return ConceptEntryListResponse(
        items=request.app.state.session_runtime.catalog.list_concept_entries(chapter_id=chapter_id)
    )


def _require_student(auth: AuthContext) -> None:
    if auth.role != "student":
        raise HTTPException(status_code=403, detail="Student membership required")
