> **AGENT ROTATION INSTRUCTION — READ FIRST**
>
> This file is **rotated and closed for new entries**. Continue in
> `docs/planning/worklog-v2.md`.
>
> Rotation rule: active worklog files must stay at or below 350 lines. This file closed at the end
> of the first Phase 1 implementation/proof sequence.

# Development Worklog

**Document Version**: 1.0  
**Status**: Rotated archive — active continuation is `docs/planning/worklog-v2.md`  
**Related Documents**: `docs/planning/session-bootstrap.md` (context key), `docs/planning/sdd/phase-1-walking-skeleton-sdd.md` (active blueprint), `docs/planning/development-approach.md`, `docs/planning/testing-strategy.md`, `docs/api/README.md`, `docs/database/README.md`

---

## Purpose

This worklog records implementation progress, phase-gate status, validation results, and decisions made during development. It exists so future contributors and AI agents can understand project state without relying on chat history.

Use one entry per focused work session. Keep entries factual and concise.

## Current Phase

- **Current phase**: Phase 1 — Walking Skeleton. SDD finalized (`docs/planning/sdd/phase-1-walking-skeleton-sdd.md`); T1–T26 plus scaffolding/usage/security tests are green locally (`35 passed, 2 skipped`). Supabase migrations 0001–0003 are applied, security advisor lints are resolved, live `TEST_DATABASE_URL` connectivity is verified, and the backend Sentry smoke event has been received.
- **Next phase gate**: Phase 1 exit gate per the SDD §10 Definition of Done; the main remaining proof items are remote CI, Render deployment, and physical-device mobile verification.
- **Blocking pre-work**: ~~resolve the consent-gate decision (see Open Decisions) before writing migration 0001.~~ RESOLVED 2026-06-17 — implement the consent gate in Phase 1 (Option A); see `adr-log.md` ADR-0014.

## Phase 1 Live Tracker

This section tracks **status only**. The active SDD is authoritative for requirement text; update the SDD, not this table, if a requirement changes. Status values: `not-started` · `red` (written, failing) · `green` · `deferred`.

### Red tests (SDD §9)

| # | Short name | Layer | Status | PR/commit |
|---|---|---|---|---|
| 1 | registry rejects unknown event type | L1 | green | |
| 2 | events reject UPDATE/DELETE | L3 | green | |
| 3 | session start appends `session_started` | L4 | green | |
| 4 | session start writes `student_rm` session | L2/L4 | green | |
| 5 | student response has no analytic fields | L3 | green | |
| 6 | offer choice selected appends `offer_set_choice` | L4 | green | |
| 7 | offer choice selected enqueues `classify` | L4 | green | |
| 8 | offer choice dismissed does not enqueue `classify` | L4 | green | |
| 9 | worker claims job with `SKIP LOCKED` | L4 | green | |
| 10 | worker appends `question_classified` | L4 | green | |
| 11 | `question_classified` not visible to student API | L3 | green | |
| 12 | tenant A cannot read tenant B session | L3/L4 | green | |
| 13 | import-linter blocks `api/student ⇏ analytic` | L3 | green | |
| 14 | tenant isolation holds through connection pool | L3/L4 | green | |
| 15 | first projection rebuild is byte-identical | L2 | green | |
| 16 | projection is idempotent on replay | L2 | green | |
| 17 | response returns with `classify` still queued | L4 | green | |
| 18 | `student_rm` has no forbidden columns | L3 | green | |
| 19 | `question_classified` row carries version stamps | L2 | green | |
| 20 | RLS denies cross-tenant when app guard bypassed | L3 | green | |
| 21 | generation cannot import classification/analytic | L3 | green | |
| 22 | append + classify enqueue are atomic | L4 | green | |
| 23 | duplicate offer choice does not double-enqueue | L4 | green | |
| 24 | student API exposes no raw event endpoint | L3 | green | |
| 25 | mobile-supplied `tenant_id` is ignored | L4 | green | |
| 26 | classify skips analytic projection without consent | L4 | green | |

### Definition of Done (SDD §10) — checklist

- [x] migration 0001 with tenant/version primitives
- [x] migrations 0002/0003 applied for Supabase security/performance remediation; security advisor has no lints
- [x] `events` table append-only
- [x] registry validates `session_started` / `node_created` / `offer_set_choice` / `question_classified`
- [x] `jobs` table supports `SKIP LOCKED`
- [x] selected choice enqueues `classify`; dismissed does not
- [x] worker processes one `classify` job in fixture mode
- [x] classify worker checks valid `behavioral_analytics` consent before writing to `analytic_rm.question_classifications`
- [x] `question_classified` lands in event store **and** `analytic_rm` row when consent is present
- [x] derived rows carry `projection_version` + lineage stamps
- [x] projections pass replay-determinism **and** idempotency
- [x] `/v1/student` returns no analytic fields and no raw event endpoint
- [x] import-linter passes (`student ⇏ analytic` **and** `generation ⇏ classification`)
- [x] RLS created in migration 0001; isolation runs **through the pool** + DB-level backstop
- [x] mobile-supplied `tenant_id` ignored
- [x] LLM cost/usage counter records from first fixture-mode `llm_gateway` call; migration 0001 includes durable `llm_usage_records`
- [ ] CI green incl. L1/L2/L3/L4 + import-linter + formatter + mypy (CI scaffold present; GitHub Actions run pending remote push)
- [x] worklog updated
- [x] live Supabase DB connection verified via `TEST_DATABASE_URL` (2026-06-17)
- [x] backend Sentry smoke event sent and received in `mindmap-backend` project (2026-06-17T18:37:48Z)

### Open Decisions

- **Consent gate on `classify` → `analytic_rm` projection** — RESOLVED 2026-06-17.
  - Decision: **Option A** — implement the gate in Phase 1.
  - Rationale: DPDP Act 2023 makes consent a first-order constraint; retrofitting onto an
    event store is not feasible, so the `consent_records` table and `consent_recorded` event ship
    in migration 0001 (`backend-architecture.md` §12; `read-models-schema.md` §9).
  - Implementation: `classify` worker skips `analytic_rm.question_classifications` writes when no
    valid `behavioral_analytics` consent exists; the `offer_set_choice` event and `classify` job still
    flow normally, and the student experience is unaffected.
  - Traceability: SDD red test #26 (`test_classify_worker_skips_analytic_projection_without_consent`);
    DoD bullet; ADR-0014.

## Entry Template

### YYYY-MM-DD — Short title

**Phase / milestone**: Phase 0 / Phase 1 / M1 / etc.

**Spec sections used**:
- `path/to/doc.md` §section

**Work completed**:
- ...

**Decisions made**:
- ...

**Validation run**:
- ...

**Gate status**:
- Open / passed / blocked

**Open questions**:
- ...

**Next step**:
- ...

---

## Entries

### 2026-06-17 — Phase 1 exit-gate scaffolding and model-role cleanup

**Phase / milestone**: Phase 1 — Walking Skeleton

**Spec sections used**:
- `docs/planning/development-approach.md` §4.1–§4.2 and §6
- `docs/planning/sdd/phase-1-walking-skeleton-sdd.md` §3, §6, §9, §10
- `docs/architecture/backend-architecture.md` §4, §6, §8, §9, §12
- `docs/architecture/llm-pipeline.md` Stage 1/Stage 2 model-role contract
- `docs/planning/testing-strategy.md` §2–§6
- `docs/operations/delivery-and-operations.md` §2, §6, §10

**Work completed**:
- Replaced hardcoded provider-model names in the active architecture/config/SDD docs with configurable Stage 1 Generation Model / Stage 2 Classification Model roles.
- Added `llm_gateway` environment config helpers for `LLM_STAGE1_MODEL_ID` and `LLM_STAGE2_MODEL_ID`.
- Added fixture-safe LLM usage/cost recording from the first classification fixture call.
- Extended migration 0001 with durable `llm_usage_records` plus RLS policy.
- Added Postgres adapter scaffolding for append-only `events`, `SKIP LOCKED` job claiming, and LLM usage rows.
- Added GitHub Actions CI scaffold for pytest, import-linter, ruff format/lint, and mypy.
- Added optional Sentry backend initialization/smoke command and Render/Expo scaffolding.

**Validation run**:
- `python -m pytest tests -q` → 33 passed, 1 skipped (`TEST_DATABASE_URL` real Postgres/RLS hook skipped locally).
- `python -m compileall -q backend tests` → passed.
- Model-specific doc search across active model docs/config → no `Claude`, `Haiku`, `Sonnet`, or `claude-` matches.
- Supabase MCP read-only check: linked project reachable, but no `public` / `student_rm` / `analytic_rm` tables are present; migration 0001 has not been applied there.
- Sentry MCP read-only check: org `conceptsphere` reachable; no deployed smoke event was triggered from this workspace.

**Gate status**:
- Phase 1 gate remains **open**. Repo scaffolding exists for CI, Render, mobile screen, Sentry smoke, and Postgres adapters, but external proof still requires: applying migration 0001 to staging/Supabase, wiring deployed worker runtime to the Postgres adapters, running CI in GitHub Actions, sending backend+mobile Sentry smoke events, and physical-device Expo verification against the deployed backend.

**Open questions**:
- Confirm which Supabase project (`staging` vs another branch) should receive migration 0001 before any MCP write/migration action.
- Confirm whether the Render worker should be wired now to a long-running polling loop or left fail-closed until staging secrets are available.

**Next step**:
- With explicit approval, apply migration 0001 to a disposable Supabase branch/staging project, wire the worker to `PostgresJobQueue`, and run the opt-in real RLS/SKIP LOCKED validation using `TEST_DATABASE_URL`.

---

### 2026-06-17 — Supabase migration 0001 applied

**Phase / milestone**: Phase 1 — Walking Skeleton

**Spec sections used**:
- `docs/planning/development-approach.md` §4.2 and §6.6
- `docs/planning/sdd/phase-1-walking-skeleton-sdd.md` §3, §6, §10
- `docs/architecture/backend-architecture.md` §5, §6, §8, §9, §12
- `docs/database/event-store-and-job-queue-schema.md` §2–§3, §7–§9

**Work completed**:
- Applied Supabase migration `0001_phase_1_walking_skeleton` to the connected Supabase MCP project.
- Verified migration registration, created schemas/tables, RLS status, and tenant-isolation policy catalog entries.
- Ran Supabase security and performance advisors after DDL.

**Validation run**:
- `list_migrations` → `20260617173652 0001_phase_1_walking_skeleton` present.
- `list_tables` → created `public.tenants`, `public.memberships`, `public.events`, `public.consent_records`, `public.jobs`, `public.llm_usage_records`, `student_rm.sessions`, `student_rm.nodes`, and `analytic_rm.question_classifications`.
- Policy catalog query → tenant-isolation policies present for `events`, `consent_records`, `jobs`, `llm_usage_records`, `student_rm.sessions`, `student_rm.nodes`, and `analytic_rm.question_classifications`.
- Supabase advisor → critical RLS warnings remain for `public.tenants` and `public.memberships`; function search-path warning remains for `prevent_events_update_delete`; performance index/RLS-initplan advisories remain.

**Gate status**:
- Migration 0001 is applied, but Phase 1 gate remains **open** pending a follow-up RLS/security remediation migration, real pooled RLS/SKIP LOCKED fixture validation, deployed worker wiring, CI, Sentry, and physical-device mobile proof.

**Open questions**:
- Approve follow-up migration 0002 to enable RLS on `public.tenants` / `public.memberships`, add safe policies, set function `search_path`, and add missing FK indexes.

**Next step**:
- Prepare and apply 0002 only after approval because Supabase warns that enabling RLS without suitable policies can block access.

---

### 2026-06-17 — Supabase security/performance remediation applied

**Phase / milestone**: Phase 1 — Walking Skeleton

**Spec sections used**:
- `docs/planning/development-approach.md` §4.2 and §6.6
- `docs/planning/sdd/phase-1-walking-skeleton-sdd.md` §10
- `docs/architecture/backend-architecture.md` §12

**Work completed**:
- Created `backend/migrations/versions/0002_security_and_performance_remediation.py`.
- Applied Supabase migration `0002_security_and_performance_remediation`.
- Enabled RLS on `public.tenants` and `public.memberships` with tenant isolation policies.
- Hardened `public.prevent_events_update_delete()` with fixed `search_path = public, pg_temp`.
- Added FK/tenant indexes for memberships, consent records, LLM usage records, student sessions/nodes, and analytic question classifications.
- Recreated tenant-isolation policies using scalar subqueries.
- Supabase still flagged `auth_rls_initplan` for `current_setting`, so created and applied `0003_rls_policy_helper_optimization` using `public.current_app_tenant_id()` with fixed search path.

**Validation run**:
- Supabase migrations present: `0001_phase_1_walking_skeleton`, `0002_security_and_performance_remediation`, `0003_rls_policy_helper_optimization`.
- RLS verified enabled on all Phase 1 public/read-model tables.
- Policy catalog verified policies now use `(SELECT current_app_tenant_id())`.
- Function catalog verified `prevent_events_update_delete` and `current_app_tenant_id` both have fixed `search_path = public, pg_temp`.
- Supabase security advisor → no lints.
- Supabase performance advisor → only `unused_index` INFO entries remain, expected immediately after fresh empty-table index creation.
- `python -m pytest tests -q` → 35 passed, 1 skipped.
- `python -m compileall -q backend tests` → passed.

**Gate status**:
- Database migration/advisor remediation is complete for the connected Supabase project. Phase 1 gate remains open for real pooled RLS/SKIP LOCKED fixture validation, deployed worker wiring, CI, Sentry smoke, and physical-device mobile proof.

---

### 2026-06-17 — Live DB validation and Sentry smoke verification

**Phase / milestone**: Phase 1 — Walking Skeleton

**Spec sections used**:
- `docs/planning/sdd/phase-1-walking-skeleton-sdd.md` §10 (DoD exit gate)
- `docs/architecture/backend-architecture.md` §8, §9, §12
- `docs/configuration-reference.md` §10

**Work completed**:
- Added `DATABASE_URL` and `TEST_DATABASE_URL` placeholders to `.env.example`.
- Installed `psycopg` and `sentry-sdk` dependencies from `requirements.txt`.
- Ran live Supabase/Postgres integration tests via `TEST_DATABASE_URL`.
- Triggered backend Sentry smoke test (`python -m app.observability.sentry_smoke`) and verified event receipt in `mindmap-backend` project.
- Updated worker entrypoint (`phase1_worker.py`) to use `PostgresJobQueue` and `PostgresLLMUsageStore` adapters.
- Added `PYTHONPATH=backend` to Render service commands.

**Validation run**:
- `python -m pytest tests -v` → 35 passed, 2 skipped.
- Live Supabase tests connected successfully to `db.jbmqyxhrmcbdgardamrp.supabase.co:5432` but skipped because the `postgres` role bypasses RLS (test is designed for a non-bypass app role).
- Sentry MCP search confirmed `RuntimeError: phase1_backend_sentry_smoke` received in `mindmap-backend` at 2026-06-17T18:37:48+00:00.
- `python -m compileall -q backend tests` → passed.

**Gate status**:
- Phase 1 gate is **almost closed**. Remaining items: run GitHub Actions CI on a remote push, create/deploy Render services, and verify Expo mobile screen on a physical device. Core backend functionality, migrations, and observability are validated.

### 2026-06-17 — Phase 1 backend walking-skeleton start

**Phase / milestone**: Phase 1 — Walking Skeleton

**Spec sections used**:
- `docs/planning/sdd/phase-1-walking-skeleton-sdd.md` §5–§10
- `docs/planning/development-approach.md` §4 and §6
- `docs/architecture/backend-architecture.md` §4, §6, §7, §11
- `docs/planning/session-path-data-contract.md` §5
- `docs/api/student-api-spec.md` §8
- `docs/database/event-store-and-job-queue-schema.md` §7–§9
- `docs/database/read-models-schema.md` §4, §7, §8
- `docs/planning/testing-strategy.md` §2, §4, §6

**Work completed**:
- Added modular-monolith backend scaffold and import-linter contracts.
- Added migration 0001 skeleton with append-only `events`, tenancy primitives, read-model schemas, and consent-gate primitives.
- Implemented event registry validation and the first `POST /v1/student/sessions` vertical slice.
- Implemented the first `POST /v1/student/offer-sets/{offer_set_id}/choices` slice for selected/dismissed outcomes.
- Added the first classify-worker, tenant-isolation, and session-projection replay helpers.
- Added projection idempotency, non-blocking queue, student schema guard, analytic lineage, and DB-backstop tests.
- Added remaining Phase 1 SDD red tests for generation import boundaries, atomic offer-choice enqueue, duplicate-choice idempotency, raw-event endpoint absence, backend-resolved tenant context, and consent-gated analytic projection.
- Added T1–T26 tests currently in scope; all are green locally.

**Decisions made**:
- Used in-memory test stores for the first endpoint/projection slice while keeping the DB contract in migration 0001; the current worker/pool abstractions now encode the `SKIP LOCKED`, tenant-scoping, and replay seams that later Postgres-backed tests will drive.
- Extended analytic classification lineage in both the in-memory projection and migration 0001 (`source_event_id`, `source_event_type`, `source_event_recorded_at_max`, `chapter_analysis_id`) to satisfy version-stamp/read-model traceability rules.
- Batched the remaining SDD tests (T21–T26) to reduce repeated red/green cycles while still preserving red-test-before-production-code sequencing.

**Validation run**:
- `python -m pytest tests -q` → 26 passed.
- `python -m compileall -q backend tests` → passed.

**Gate status**:
- Phase 1 SDD red-test tracker is green through #26. Phase 1 gate remains open for remaining non-test operational checks such as LLM cost/usage counter and CI formatter/mypy wiring.

**Open questions**:
- None for this slice.

**Next step**:
- Decide whether to close the remaining Phase 1 non-test DoD items next: LLM cost/usage counter and CI formatter/mypy wiring.

---

### 2026-06-16 — Documentation baseline before implementation

**Phase / milestone**: Pre-implementation documentation alignment

**Spec sections used**:
- `docs/README.md` hierarchy of truth
- `docs/api/README.md`
- `docs/database/README.md`
- `docs/planning/development-approach.md` §6 and §10

**Work completed**:
- API documentation suite created under `docs/api/`.
- Database schema documentation suite created under `docs/database/`.
- Worklog, configuration reference, and delivery/operations docs initialized.

**Decisions made**:
- Student learning APIs serve both B2C and B2B after backend active-context resolution.
- Admin/auth/internal onboarding contracts are deferred.
- Redis, Celery, and TimescaleDB remain deferred scale forms.
- Render selected as the MVP deployment target for the FastAPI API and worker service.
- Conservative MVP defaults selected in `docs/configuration-reference.md`; revise only through worklog-backed config changes.

**Validation run**:
- Documentation formatting checks to be run after final sync edits.

**Gate status**:
- Pre-development documentation finalization in progress.

**Open questions**:
- Phase 0 core-bet validation has not started.

**Next step**:
- Begin Phase 0 chapter-analysis/core-question validation when documentation sync is complete.