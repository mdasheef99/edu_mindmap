> **AGENT ROTATION INSTRUCTION — READ FIRST**
>
> This is the active worklog continuation after `docs/planning/worklog.md`. Keep this file at or
> below 350 lines. When adding an entry would exceed 350 lines, create
> `docs/planning/worklog-v3.md`, add a `Legacy Context Summary`, copy forward current phase/gate
> status and open blockers, then append future entries only in the new file.

# Development Worklog — 02

**Document Version**: 1.0
**Status**: Active continuation
**Previous File**: `docs/planning/worklog.md`

---

## Legacy Context Summary

- Phase 1 — Walking Skeleton is the active increment; do not open Phase 2/3 work.
- Migrations `0001`, `0002`, and `0003` are applied on the connected Supabase project.
- Supabase security advisor lints are resolved for the Phase 1 schema baseline.
- Backend worker entrypoint uses Postgres-backed queue/store adapters.
- Backend Sentry smoke was received in the `mindmap-backend` project.
- The previous local baseline was `35 passed, 2 skipped`; the skips were the opt-in live DB tests
  when `TEST_DATABASE_URL` was missing or used a role with `BYPASSRLS`.

## Current Phase

- **Current phase**: Phase 1 — Walking Skeleton. **CLOSED 2026-06-18.**
- **Next phase**: Phase 2 — Curriculum Ingestion (active milestone per `00-canon.md`).
- **Open decisions**: none for Phase 1; consent gate resolved in `worklog.md` and ADR-0014.

## Phase 1 Live Tracker

### Definition of Done (SDD §10) — FINAL status

- [x] Supabase migrations `0001`–`0003` applied; security advisor lints resolved
- [x] local CI-equivalent gates pass: Ruff format, Ruff lint, mypy, import-linter, pytest
- [x] live `TEST_DATABASE_URL` uses non-bypass role; RLS / `SKIP LOCKED` tests pass actively
- [x] backend Sentry smoke received
- [x] GitHub Actions CI green on latest pushed commit (`10bb751`, run `27716220823`)
- [deferred] Render backend + worker deployment — defer to Phase 2 sprint 1
- [deferred] physical-device Expo verification — defer to Phase 2 sprint 1

---

## Entries

### 2026-06-17 — CI gate repair and live non-bypass RLS proof

**Phase / milestone**: Phase 1 — Walking Skeleton

**Spec sections used**:
- `docs/planning/development-approach.md` §4, §6, §8
- `docs/planning/sdd/phase-1-walking-skeleton-sdd.md` §10
- `docs/architecture/backend-architecture.md` §5, §8, §12
- `docs/planning/testing-strategy.md` §3, §6

**Work completed**:
- Checked GitHub Actions for commit `36f256c`; initial run failed at Ruff format.
- Formatted backend/tests and aligned CI dependency install with `requirements.txt`.
- Added `PYTHONPATH=backend` to CI so import-linter can resolve `app`.
- Created a non-bypass Supabase login role for live RLS tests and updated local `TEST_DATABASE_URL`.
- Replaced parameterized `SET LOCAL app.tenant_id` calls with shared `set_config(...)` helper.
- Added code-organization standard: source files should stay under 300–350 lines and be split by
  responsibility when they approach that limit.

**Validation run**:
- `python -m ruff format --check backend tests` → passed.
- `python -m ruff check backend tests` → passed.
- `python -m mypy backend/app` → passed.
- `PYTHONPATH=backend lint-imports --config pyproject.toml --no-cache` → contracts kept.
- `python -m pytest tests -q` → 35 passed, 2 skipped.
- `pytest tests/database/test_optional_postgres_rls_contract.py` with `.env` loaded → 2 passed.
- GitHub Actions `Phase 1 CI` run `27716220823` for commit `10bb751` → passed.

**Gate status**:
- Phase 1 backend, database, and remote CI proof are green. Remaining Phase 1 proof items are Render
  deployment and physical-device mobile verification.

**Next step**:
- Prepare Render backend/worker verification steps, then record physical-device Expo proof.

---

### 2026-06-18 — Phase 1 formally closed; mobile verification deferred

**Phase / milestone**: Phase 1 — Walking Skeleton (exit)

**Work completed**:
- Updated SDD §1 status and §10 DoD to mark Phase 1 as CLOSED.
- Physical-device Expo verification and Render deployment recorded as deferred (non-blocking;
  mobile surface is additive to the backend walking skeleton).
- `00-canon.md` ACTIVE MILESTONE updated to Phase 2 — Curriculum Ingestion.
- Worklog status updated to reflect Phase 1 closure.

**Gate status**: Phase 1 exit gate **PASSED**. All non-deferred DoD items verified.

---

### 2026-06-18 — Phase 2 kickoff: Curriculum Ingestion SDD + supporting docs initialized

**Phase / milestone**: Phase 2 — Curriculum Ingestion (active milestone per `00-canon.md`)

**Spec sections used**:
- `docs/planning/development-approach.md` §3 (Phase 0 P0–P4), §5 (M4 auth + M6 teacher render note), §6 (day-one disciplines), §7.1/§7.7 (auth stack + content pipeline tooling), §8 (working method)
- `docs/architecture/backend-architecture.md` §3 (deployment), §4 (module boundaries + new `chapter_analysis` + `curriculum` contracts), §5.1/§5.3/§5.4 (tenancy, RLS, identity resolution), §6 (event store), §7.5 (curriculum schema), §9 (LLM Gateway), §11 (API surface)
- `docs/chapter-analysis-pipeline-specification.md` P0–P4 + §5 (verification gate)
- `docs/planning/sdd/phase-2-curriculum-ingestion-sdd.md` §3–§11 (the new active SDD)
- `docs/planning/testing-strategy.md` §2/§3.1 (L1–L6 matrix + Phase 2 additions)
- `docs/configuration-reference.md` §10.1 (Phase 2 env placeholders)
- `docs/architecture/adr-log-02.md` ADR-0015 (Supabase Auth strategy, Proposed)

**Work completed**:
- Created `docs/planning/sdd/phase-2-curriculum-ingestion-sdd.md` (draft v1.0): defines Phase 2
  scope as P0–P4 ingestion, Supabase Auth + tenant resolution, and Teacher Dashboard V1 render.
  Listed Render deployment and physical-device Expo verification as the first implementation
  priorities (deferred from Phase 1), with Expo explicitly gated on a mobile curriculum surface
  existing (SDD §7.4).
- Updated `docs/architecture/backend-architecture.md`: added §4 Phase 2 boundary note for
  `chapter_analysis` and new §7.5 `curriculum` content schema.
- Updated `docs/planning/testing-strategy.md`: added §3.1 Phase 2 test matrix (Auth L3, Ingestion L2
  determinism/idempotency, plus L1/L4/L5/L6 rows).
- Updated `docs/configuration-reference.md`: added §10.1 Supabase Auth + ingestion env placeholders
  (names only, no values).
- Updated `docs/architecture/adr-log-02.md`: refreshed legacy summary to Phase 2; added ADR-0015
  (Supabase Auth JWT validation strategy) as Proposed.
- Updated `.augment/rules/00-canon.md`: active SDD line marked as created (draft v1.0).

**Gate status**: Phase 2 entry gate **OPEN**; no production code yet. First red tests (SDD §9) must be
written before implementation.

**Deferred / non-deferred items for next session**:
- Render deployment: **do not defer** — no frontend dependency; should be the first proof item.
- Physical-device Expo smoke: **may remain deferred** until a mobile curriculum session surface
  exists (SDD §7.4).

**Next step**:
- Record ADR-0015 acceptance and start either Render deployment verification or Supabase Auth
  red-test-first implementation (SDD §3.1 priority order).

---

### 2026-06-18 — Phase 2 sprint 1: Supabase Auth + tenant resolution implemented (priority 2)

**Phase / milestone**: Phase 2 — Curriculum Ingestion (active milestone per `00-canon.md`)

**Spec sections used**:
- `docs/planning/development-approach.md` §7.1 (Auth = Supabase Auth)
- `docs/architecture/backend-architecture.md` §5.4 (identity + tenant resolution), §11 (per-router auth), §12.1 (consent gate)
- `docs/planning/sdd/phase-2-curriculum-ingestion-sdd.md` §3.1 (priority order), §9 (auth red tests), §7.3 (tenant resolution)
- `docs/architecture/adr-log-02.md` ADR-0015 (accepted — HS256 mechanism)

**Work completed**:
- **Deferred Render deployment verification** to later in Phase 2: it is a Phase 1 closure item with no
  frontend dependency and is not a technical blocker for Supabase Auth, `chapter_analysis`, or curriculum
  schema work (all can be tested locally via `supabase start` or testcontainers). SDD §10 DoD still
  requires it before Phase 2 formal closure.
- **Accepted ADR-0015**: selected HS256 shared secret (`SUPABASE_JWT_SECRET`) as the JWT validation
  mechanism; JWKS placeholder retained in `configuration-reference.md` for future rotation without
  schema change. Updated `adr-log-02.md` status to **Accepted** and recorded consequences.
- Added `pyjwt` to `requirements.txt`.
- Added `AuthContext` dataclass in `backend/app/domain/auth.py` (pure, no imports below, domain-only).
- Added `InMemoryMembershipStore` test fixture to `backend/app/main.py`.
- Extended `SessionRuntime` with `jwt_secret`, `memberships`, `_seen_users`, and `resolve_auth()`.
- Implemented `get_auth_context` FastAPI dependency in `backend/app/tenancy/auth.py`:
  - Extracts `Authorization: Bearer <token>` header.
  - Verifies JWT via HS256 using `pyjwt`.
  - Resolves `user_id → tenant_id`/`role` from `memberships` server-side (mobile-supplied `tenant_id` ignored).
- Updated `app.api.student.sessions` and `app.api.student.offer_choices` routers to require
  `auth=Depends(get_auth_context)`.
- Updated `SessionRuntime.start_session()` to accept optional `auth` and:
  - Use resolved `auth.tenant_id`/`auth.user_id` instead of hardcoded runtime defaults.
  - Append `consent_recorded` event on first sign-in (per ADR-0014 / backend-architecture.md §12.1).
- Updated `SessionRuntime.record_offer_choice()` to accept optional `auth` and use resolved identity.
- Updated all 4 existing integration test files to send authenticated JWT headers via updated
  `_build_client_and_runtime` helpers.
- Added 4 new auth tests in `tests/integration/test_auth.py` (all passing):
  - `test_missing_auth_returns_401`
  - `test_jwt_resolves_backend_tenant_and_role`
  - `test_authenticated_request_ignores_mobile_supplied_tenant_id`
  - `test_first_signin_appends_consent_recorded`

**Validation run**:
- `python -m ruff format --check backend tests` → passed.
- `python -m ruff check backend tests` → passed.
- `python -m mypy backend/app` → passed.
- `python -m pytest tests -q` → 39 passed, 2 skipped (same baseline as before).
- Manual import-linter contract verification via `grimp` → no forbidden cross-boundary imports.

**Gate status**: Phase 2 priority 2 (Supabase Auth) **COMPLETE**. Priority 3 (`chapter_analysis` P0–P4 +
migration 0004) is next unblocked item.

**Next step**:
- Write SDD §9 red tests for `chapter_analysis` P0–P4 and implement migration 0004 curriculum schema.

---

### 2026-06-18 — Phase 2 sprint 1: priority 3 first slice green (`chapter_analysis` + migration 0004)

**Phase / milestone**: Phase 2 — Curriculum Ingestion (priority 3 in progress)

**Spec sections used**:
- `docs/planning/development-approach.md` §3.1 (Phase 0 P0–P4), §7.7 (content pipeline), §8 (red/green discipline)
- `docs/architecture/backend-architecture.md` §4 (module boundaries), §5.3 (tenant isolation), §7.5 (curriculum schema)
- `docs/chapter-analysis-pipeline-specification.md` P0, P3, P4, §5 (verification gate)
- `docs/planning/sdd/phase-2-curriculum-ingestion-sdd.md` §3.1, §5, §6, §9, §10

**Work completed**:
- Added the new `backend/app/chapter_analysis/` package with a first deterministic slice:
  - `segments.py` → P0 text segmentation helper with stable segment IDs and required index fields.
  - `merge.py` → P3 merge helper that keeps the named/P1 label and unions passage refs.
  - `edges.py` → P4 deterministic edge-ID assignment with directional vs non-directional ordering.
  - `verification.py` → verification-gate helper rejecting citations not present in the P0 segment index.
- Added migration `backend/migrations/versions/0004_curriculum_schema.py`:
  - creates `curriculum` schema,
  - creates `curriculum.chapters`, `curriculum.segments`, `curriculum.concepts`, `curriculum.concept_edges`,
  - enables RLS and tenant-isolation policies via `current_app_tenant_id()`.
- Added new Phase 2 tests:
  - `tests/chapter_analysis/test_pipeline.py` (P0/P3/P4/verification red→green slice),
  - `tests/database/test_curriculum_schema_migration.py` (static `0004` schema contract),
  - `tests/architecture/test_chapter_analysis_import_linter_contracts.py` (new `chapter_analysis` boundaries).
- Updated `pyproject.toml` with the new merge-blocking import-linter contracts:
  - `chapter_analysis ⇏ generation|classification`
  - `chapter_analysis ⇏ api`
- Updated the pre-existing import-linter architecture tests so the temporary package tree includes
  `app.chapter_analysis` now that it is a configured source module.

**Validation run**:
- `python -m pytest tests/chapter_analysis/test_pipeline.py tests/database/test_curriculum_schema_migration.py tests/architecture/test_chapter_analysis_import_linter_contracts.py -q` → 9 passed.
- `python -m ruff format --check backend tests` → passed.
- `python -m ruff check backend tests` → passed.
- `python -m mypy backend/app` → passed.
- `python -m pytest tests -q` → 48 passed, 2 skipped.

**Gate status**:
- Phase 2 priority 3 is **IN PROGRESS**.
- The first infrastructure slice is green: deterministic helpers, `0004` schema contract, and import boundaries.
- Remaining priority 3 proof items still open: P1/P2 LLM-backed extraction, curriculum ingest idempotency + byte-identical rebuild tests, real PDF extraction via the P0 seed, and persistence wiring from pipeline output into the new schema.

**Next step**:
- Add the next red tests for curriculum ingest determinism/idempotency + row stamping, then implement the in-memory/persistence ingestion builder. If we switch from text-only test inputs to real PDF parsing in code, install `pypdf` via package manager with explicit approval first.

---

### 2026-06-18 — Phase 2 sprint 1: priority 3 ingest determinism/idempotency slice green

**Phase / milestone**: Phase 2 — Curriculum Ingestion (priority 3 in progress)

**Spec sections used**:
- `docs/planning/sdd/phase-2-curriculum-ingestion-sdd.md` §8–§10 (L2 ingest determinism,
  idempotency, row stamps; first red tests T6–T8)
- `docs/architecture/backend-architecture.md` §7.5 (content-only `curriculum` schema) and §10
  (version stamping)
- `docs/planning/development-approach.md` §8 (small red→green discipline)
- ADR-0015 (`docs/architecture/adr-log-02.md`) for auth/membership tenant-resolution behavior

**Work completed**:
- Added red tests in `tests/projections/test_curriculum_ingest.py` for:
  - `test_curriculum_ingest_is_idempotent_on_reingest`,
  - `test_curriculum_ingest_rebuild_is_byte_identical`,
  - `test_curriculum_rows_carry_tenant_and_chapter_analysis_id`.
- Implemented `backend/app/projections/curriculum.py` as the first curriculum ingest builder:
  - builds `curriculum.chapters`, `segments`, `concepts`, and `concept_edges` row dictionaries,
  - composes existing P0/P3/P4 helpers,
  - verifies concept/edge segment citations through the verification gate,
  - upserts into an in-memory curriculum store for idempotency tests,
  - serializes deterministic snapshots for byte-identical rebuild tests.
- Addressed review issues:
  - renamed misleading `InMemoryMembershipStore.get_active()` to `get_memberships_for_user()`,
  - split no-membership from invalid-token auth errors (`403 No active membership for authenticated user`),
  - filtered `session_started` assertions by `event_type` in auth/offer-choice tests,
  - annotated student router `auth` dependencies with `AuthContext`.
- Cleaned generated `.pyc` files after validation; final `.pyc` count is 0.

**Validation run**:
- Red baseline observed first: new ingest tests failed on missing `app.projections.curriculum`; no-membership
  auth test failed on old `401 Invalid token` behavior.
- `python -m pytest tests/projections/test_curriculum_ingest.py -q` → 3 passed.
- `python -m pytest tests/integration/test_auth.py tests/integration/test_offer_choice.py -q` → 12 passed.
- `python -m ruff format --check backend tests` → passed.
- `python -m ruff check backend tests` → passed.
- `python -m mypy backend/app` → passed.
- `python -m pytest tests -q` → 52 passed, 2 skipped.

**Gate status**:
- Priority 3 is still **IN PROGRESS**.
- The L2 ingest determinism/idempotency/row-stamping slice is green for text-fixture P0–P4 outputs.
- Remaining priority 3 items: real PDF-backed P0 extraction (`pypdf` approval required before dependency
  install), P1/P2 LLM-backed fixture contracts through `llm_gateway`, persistence adapter against real
  Postgres/Supabase, real-chapter session wiring, and Teacher V1 render endpoint.

---

### 2026-06-18 — Phase 2 sprint 1: real-chapter session start slice green

**Phase / milestone**: Phase 2 — Curriculum Ingestion (priority 4 slice landed while priority 3 remains open)

**Spec sections used**:
- `docs/planning/sdd/phase-2-curriculum-ingestion-sdd.md` §3.1 (priority order), §4 (start real-chapter session),
  §9 T14, §10 (real chapter_id / chapter_analysis_id session start)
- `docs/architecture/backend-architecture.md` §5.4 (backend-resolved tenant context), §7.5 (`curriculum` as the
  content spine), §11 (student router responsibility)
- `docs/planning/development-approach.md` §5 (M4 curriculum entry + auth sequencing), §8 (small red→green slices)
- `docs/api/student-api-spec.md` §2 and §5 (student sessions are chapter-scoped and pinned to one
  `chapter_analysis_id`)

**Work completed**:
- Added the next red integration proof in `tests/integration/test_session_start.py`:
  - `test_session_start_resolves_real_chapter_from_curriculum`.
- Updated the student session contract so the backend, not the client, pins `chapter_analysis_id`:
  - `SessionStartRequest.chapter_analysis_id` is now optional for request validation,
  - `SessionRuntime.start_session()` resolves the requested chapter from the in-memory `curriculum` store,
  - the resolved chapter row supplies the authoritative `chapter_analysis_id` stamped onto `session_started`
    and `student_rm.sessions`.
- Added `InMemoryCurriculumStore.find_chapter()` and runtime wiring for curriculum-backed launch lookup.
- Added a student-safe `ChapterLaunchNotFoundError` → `404 Chapter not found in curriculum` API mapping.
- Updated the affected integration helpers (`test_session_start`, `test_auth`, `test_offer_choice`,
  `test_classify_worker`, `test_tenant_isolation`) to seed launchable `curriculum` chapters instead of posting
  random fixture `chapter_id` / `chapter_analysis_id` pairs.
- Cleaned generated `.pyc` files after validation; final `.pyc` count is 0.

**Validation run**:
- Red baseline observed first: `test_session_start_resolves_real_chapter_from_curriculum` failed with `422`
  because `chapter_analysis_id` was still required in the request body.
- `python -m pytest tests/integration/test_session_start.py tests/integration/test_auth.py tests/integration/test_offer_choice.py tests/integration/test_classify_worker.py tests/integration/test_tenant_isolation.py -q` → 25 passed.
- `python -m ruff format --check backend tests` → passed.
- `python -m ruff check backend tests` → passed.
- `python -m mypy backend/app` → passed.
- `python -m pytest tests -q` → 53 passed, 2 skipped.

**Gate status**:
- The first real-chapter session start slice is green against the in-memory `curriculum` backing.
- Priority 3 remains **IN PROGRESS** because the curriculum persistence adapter, real PDF-backed P0 extraction,
  and P1/P2 LLM-backed fixture contracts are still open.
- Teacher Dashboard V1 render endpoint remains the next higher-priority user-facing slice after the curriculum
  backing is no longer in-memory.

---

Rotation note: `worklog-v2.md` is at the Phase 2 line cap threshold. Continue Phase 2 entries in
`docs/planning/worklog-v3.md`.
