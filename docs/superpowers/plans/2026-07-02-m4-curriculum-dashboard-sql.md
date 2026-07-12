# M4 Curriculum Catalog + Dashboard + Manual SQL Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add student-safe curriculum endpoints, dashboard re-entry data, and local SQL for the Class 10 -> CBSE -> Science -> Electricity launch catalog.

**Architecture:** App-facing catalog tables are operational curriculum metadata, distinct from analytic read models. Dashboard reads student-safe sessions and launchable catalog suggestions only.

**Traceability:** M4 SDD Sections 7, 8.1, 8.2, 12.2, 12.4, 13; `student-api-spec.md` Sections 4-5; `core-operational-schema.md` Section 6.

---

## Files

- Create: `backend/app/domain/student/curriculum.py`
- Create: `backend/app/projections/catalog.py`
- Create: `backend/app/projections/catalog_postgres.py`
- Create: `backend/app/api/student/curriculum.py`
- Create: `backend/app/api/student/dashboard.py`
- Create: `backend/migrations/source_sql/0006_m4_catalog_auth_seed.sql`
- Modify: `backend/app/main.py`
- Modify: `backend/app/runtime/session.py`
- Test: `tests/database/test_m4_catalog_sql.py`
- Test: `tests/integration/test_m4_curriculum_dashboard.py`

## Task 1: Catalog And SQL Red Tests

- [ ] Test in-memory catalog lists Class 10, CBSE, Science, Electricity.
- [ ] Test only launchable chapters are returned.
- [ ] Test Pydantic catalog/dashboard response models contain no forbidden analytic field fragments.
- [ ] Test SQL contains required tables, indexes, RLS enablement, and the project-ref warning.

Run:

```powershell
pytest tests/database/test_m4_catalog_sql.py -q
```

Expected: fail because catalog models/SQL do not exist.

## Task 2: Implement Catalog Store And SQL

- [ ] Model `curriculum_classes`, `exams`, `subjects`, `chapters`, `concept_entries`, `chapter_analysis_versions`.
- [ ] Use stable slugs and sort order.
- [ ] Include tenant discipline where tables are tenant-scoped.
- [ ] Write idempotent manual SQL.
- [ ] Add SQL header: run only against Supabase project `jbmqyxhrmcbdgardamrp`; do not run against MCP-visible Bookconnect project.

## Task 3: Curriculum Endpoint Red Tests

- [ ] Test `GET /v1/student/curriculum/classes`.
- [ ] Test `GET /v1/student/curriculum/exams?class_id=...`.
- [ ] Test `GET /v1/student/curriculum/subjects?class_id=...&exam_id=...`.
- [ ] Test `GET /v1/student/curriculum/chapters?class_id=...&exam_id=...&subject_id=...`.
- [ ] Test `GET /v1/student/chapters/{chapter_id}` student-safe metadata.
- [ ] Test `GET /v1/student/chapters/{chapter_id}/concept-entries`.

Run:

```powershell
pytest tests/integration/test_m4_curriculum_dashboard.py -q
```

Expected: fail with 404 for new routes.

## Task 4: Implement Curriculum Router

- [ ] Add `backend/app/api/student/curriculum.py`.
- [ ] Register router in `backend/app/main.py`.
- [ ] Require authenticated student context.
- [ ] Filter by server-resolved context and launch status.
- [ ] Return student-safe fields only.

## Task 5: Dashboard Red Tests

- [ ] Test dashboard with no sessions returns `continue_learning = None`.
- [ ] Test dashboard with no sessions suggests launchable Electricity.
- [ ] Test dashboard after session start returns Continue Learning and recent session.

Run:

```powershell
pytest tests/integration/test_m4_curriculum_dashboard.py -q
```

Expected: dashboard tests fail until router/runtime support exists.

## Task 6: Implement Dashboard

- [ ] Add `backend/app/api/student/dashboard.py`.
- [ ] Register router in `backend/app/main.py`.
- [ ] Read recent student-safe sessions.
- [ ] Read launchable curriculum suggestions.
- [ ] Do not return raw events, analytic fields, checkpoint vectors, or teacher fields.

## Task 7: Green And Cleanup

Run:

```powershell
pytest tests/database/test_m4_catalog_sql.py tests/integration/test_m4_curriculum_dashboard.py -q
```

After Python tests:

```powershell
Get-ChildItem -Path . -Recurse -Filter *.pyc | Remove-Item -Force
$pycCount = (Get-ChildItem -Path . -Recurse -Filter *.pyc | Measure-Object).Count
if ($pycCount -ne 0) { throw "Remaining .pyc count: $pycCount" }
```

Expected: tests pass and `.pyc` count is zero.
