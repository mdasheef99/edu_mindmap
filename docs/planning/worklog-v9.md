# AGENT ROTATION INSTRUCTION - READ FIRST

This is the active worklog as of 2026-07-02. Read this file after the source-of-truth hierarchy
and before making M4 code or schema changes.

Legacy context:

- `docs/planning/worklog-v8.md` is now a closed archive. It covers post-M3-C housekeeping,
  M3.5 frontend readiness verification, M3.6 canvas controls, the canvas TypeScript/Jest config
  blocker resolution, and the M4 SDD draft.
- M3-C, M3.5, and M3.6 are locally complete. Do not reopen them unless explicitly requested.
- M4 is the active milestone: curriculum entry, Supabase Auth, dashboard re-entry, consent
  capture, and fixture-backed Electricity canvas flow.
- Active SDD: `docs/planning/sdd/phase-3-m4-curriculum-auth-sdd.md`.
- Supabase MCP currently exposes the wrong project: `ahntbtktjjmvfosgkmgn`
  (`Bookconnect_reactexpo`). The local Mindmap `.env` points at project ref
  `jbmqyxhrmcbdgardamrp`. Do not apply migrations through MCP in this session unless the MCP
  account/project access changes and is re-verified.
- The owner intends to run the generated SQL manually against the correct Supabase database.

Required reading order for M4 implementation sessions:

1. `.augment/rules/00-canon.md`
2. `docs/planning/development-approach.md`
3. `docs/architecture/backend-architecture.md`
4. `docs/architecture/adr-log.md`
5. `docs/architecture/adr-log-02.md`
6. `docs/planning/session-path-data-contract.md`
7. `docs/prd/master-prd.md`
8. `docs/mvp-features-specification.md`
9. `docs/api/student-api-spec.md`
10. `docs/database/core-operational-schema.md`
11. `docs/database/schema-traceability-and-validation.md`
12. `docs/configuration-reference.md`
13. `docs/planning/testing-strategy.md`
14. `docs/planning/sdd/phase-3-m4-curriculum-auth-sdd.md`
15. `docs/planning/worklog-v9.md`

Current implementation status:

- M4 SDD is drafted, not implemented.
- B2C individual signup is first. School/B2B roster or invite activation is deferred.
- Auth path is Supabase email/password for M4. Phone/OTP is deferred behind the same Supabase
  identity model.
- Real LLM generation is deferred. M4 uses a deterministic fixture-backed Electricity generation
  provider that mimics real node creation through the backend/event/canvas boundaries.
- Launch curriculum path is Class 10 -> CBSE -> Science -> Electricity, with about 10
  fixture-backed Electricity nodes.

---

### 2026-07-02 - Worklog v9 opened for M4 implementation planning

**Milestone context**: M4 is active planning/implementation-next. M3-C, M3.5, and M3.6 are locally
complete.

**Spec sections used**:
- `development-approach.md` Section 5 M4 and Section 8.1 worklog rotation guidance.
- `.augment/rules/00-canon.md` active milestone and source-of-truth hierarchy.
- `phase-3-m4-curriculum-auth-sdd.md` Sections 3, 7, 13, and 14.

**Work completed**:
- Rotated `docs/planning/worklog-v8.md` to closed archive status.
- Created this `docs/planning/worklog-v9.md` as the active tracker for M4.
- Recorded required M4 reading order for a fresh implementation session.
- Preserved the Supabase project warning: MCP-visible project is not the Mindmap project.
- Updated `.augment/rules/00-canon.md`, `docs/planning/development-approach.md`,
  `docs/planning/session-bootstrap.md`, `.augment/hooks/session-context.sh`, and
  `.augment/commands/bootstrap.md` so new sessions point at M4, the M4 SDD, and this worklog.

**Gate status**: Ready for M4 implementation planning after user approval of the SDD.

---

### 2026-07-02 - M4 implementation plan split for execution

**Milestone context**: M4 remains active and not implemented. The SDD stays as the governing
milestone design; implementation will proceed through smaller red-test-first execution slices.

**Spec sections used**:
- `development-approach.md` Section 8.1 documentation governance and Section 8.2 small,
  explainable increments.
- `.augment/rules/00-canon.md` code/document organization constraints and active M4 milestone.
- `phase-3-m4-curriculum-auth-sdd.md` Sections 4, 12, 13, and 14.

**Work completed**:
- Replaced the oversized single M4 implementation plan with a short index:
  `docs/superpowers/plans/2026-07-02-phase-3-m4-curriculum-auth.md`.
- Split execution into four focused plans:
  `2026-07-02-m4-backend-auth-bootstrap.md`,
  `2026-07-02-m4-curriculum-dashboard-sql.md`,
  `2026-07-02-m4-fixture-electricity-flow.md`, and
  `2026-07-02-m4-mobile-auth-canvas-handoff.md`.
- Preserved the required sequence: backend auth/bootstrap first, then curriculum/dashboard/SQL,
  then fixture Electricity session/generation, then mobile auth/curriculum/canvas handoff.
- Confirmed the post-cleanup git status contains only disposable local `.err` log files as
  untracked items; no implementation code has started in this session.

**Gate status**: Ready to start M4 Slice 1 (Backend Auth + B2C Bootstrap) after the user confirms
whether to ignore or remove the remaining local `.err` files.

---

### 2026-07-02 - M4 Slice 1 backend auth bootstrap implemented

**Milestone context**: M4 remains active. Slice 1 implements the backend-only B2C membership
bootstrap primitive; no curriculum/dashboard/mobile implementation has started.

**Spec sections used**:
- `phase-3-m4-curriculum-auth-sdd.md` Sections 6.2, 6.3, and 12.1.
- `backend-architecture.md` Sections 5.4, 5.5, and 11.
- `adr-log-02.md` ADR-0015.

**Work completed**:
- Added red-first tests in `tests/integration/test_m4_auth_bootstrap.py`.
- Added idempotent `InMemoryMembershipStore.ensure_student_membership`.
- Added `verify_supabase_user_id` to `app.tenancy.membership_auth` so bootstrap verifies the
  Supabase HS256 JWT and extracts only `sub`.
- Added `SessionRuntime.bootstrap_b2c_student_membership`, which ignores tenant-like token/client
  claims and creates a `student` membership in the configured individual tenant.
- Added missing `httpx==0.28.1` to `requirements.txt` because existing FastAPI `TestClient`
  integration tests require it.

**Verification**:
- Red baseline: `.\.venv\Scripts\python.exe -m pytest tests/integration/test_m4_auth_bootstrap.py -q`
  -> 3 failed, 2 passed; failures were the missing bootstrap runtime method.
- Focused green: same command -> 5 passed.
- Adjacent regression: `.\.venv\Scripts\python.exe -m pytest tests/integration/test_auth.py tests/integration/test_m4_auth_bootstrap.py -q`
  -> 10 passed.
- `.pyc` cleanup: removed generated bytecode and verified remaining `.pyc` count = 0. The first
  cleanup command hit an access-denied warning while traversing `.pytest_cache`; the follow-up
  verification with denied paths suppressed reported zero `.pyc` files.

**Gate status**: Slice 1 locally complete. Next slice: Curriculum Catalog + Dashboard + Manual SQL.

---

### 2026-07-02 - M4 Slice 2 curriculum catalog, dashboard, and manual SQL implemented

**Milestone context**: M4 remains active. Slice 2 adds the student-safe app-facing launch catalog,
dashboard endpoint, and local manual SQL artifact for the Class 10 -> CBSE -> Science ->
Electricity path. Fixture node generation and mobile auth remain pending.

**Spec sections used**:
- `phase-3-m4-curriculum-auth-sdd.md` Sections 7, 8.1, 8.2, 12.2, 12.4, and 13.
- `student-api-spec.md` Sections 4 and 5.
- `core-operational-schema.md` Section 6.
- `schema-traceability-and-validation.md` Sections 2 through 7.

**Work completed**:
- Added student-safe catalog/dashboard DTOs in `backend/app/domain/student/curriculum.py`.
- Added app-facing in-memory catalog store and deterministic M4 Electricity seed helper in
  `backend/app/projections/catalog.py`.
- Added local manual SQL artifact:
  `backend/migrations/source_sql/0006_m4_catalog_auth_seed.sql`.
- Added authenticated student curriculum router:
  `backend/app/api/student/curriculum.py`.
- Added authenticated student dashboard router:
  `backend/app/api/student/dashboard.py`.
- Registered the new routers in `backend/app/main.py`.
- Added catalog dependency wiring to `SessionRuntime`.

**Verification**:
- Red baseline: `.\.venv\Scripts\python.exe -m pytest tests/database/test_m4_catalog_sql.py -q`
  -> 4 failed because catalog modules/SQL did not exist.
- Catalog/SQL green: same command -> 4 passed.
- Red endpoint baseline:
  `.\.venv\Scripts\python.exe -m pytest tests/integration/test_m4_curriculum_dashboard.py -q`
  -> 4 failed with 404s for missing routes.
- Endpoint/dashboard green: same command -> 4 passed.
- Combined Slice 2 focused green:
  `.\.venv\Scripts\python.exe -m pytest tests/database/test_m4_catalog_sql.py tests/integration/test_m4_curriculum_dashboard.py -q`
  -> 8 passed.
- `.pyc` cleanup/verification after user continuation: remaining `.pyc` count = 0.

**Gate status**: Slice 2 locally complete. Next slice: Fixture Electricity Session + Generation Flow.

---

### 2026-07-02 - M4 Slice 3 fixture Electricity session generation implemented

**Milestone context**: M4 remains active. Slice 3 adds the deterministic, fixture-backed
Electricity generation path for session start and selected offer choices. This remains local
fixture generation only; live LLM generation is still deferred.

**Spec sections used**:
- `phase-3-m4-curriculum-auth-sdd.md` Sections 8.3, 9, 12.3, and 13.
- `student-api-spec.md` Sections 5 and 8.
- `backend-architecture.md` Sections 6, 7.1, 9, 10, and 11.

**Work completed**:
- Added the generation provider boundary in `backend/app/generation/provider.py`.
- Added the Class 10 CBSE Science Electricity fixture provider in
  `backend/app/generation/fixture_electricity.py` with ten deterministic student-safe nodes.
- Added root-node event construction for M4 session start, including fixture node key,
  prompt version, model id, and lineage stamps.
- Wired `SessionRuntime` with the fixture provider and passed it into session and offer-choice
  workflows.
- Updated selected offer-choice handling so fixture-backed source nodes produce fixture child
  nodes while non-fixture sources keep the existing placeholder behavior.
- Added red-first integration coverage in `tests/integration/test_m4_fixture_sessions.py`.

**Verification**:
- Provider red baseline:
  `.\.venv\Scripts\python.exe -m pytest tests/integration/test_m4_fixture_sessions.py -q`
  -> 3 failures for missing generation modules before implementation.
- Session root red baseline: same command -> 2 failures because session start did not append a
  root `node_created` event and GET session returned an empty canvas.
- Fixture child red baseline:
  `.\.venv\Scripts\python.exe -m pytest tests/integration/test_m4_fixture_sessions.py::test_selected_offer_choice_from_root_uses_fixture_child_node -q`
  -> 1 failure because selected choices still returned `Explore: ...` placeholder content.
- Focused green:
  `.\.venv\Scripts\python.exe -m pytest tests/integration/test_m4_fixture_sessions.py -q`
  -> 5 passed after root-node wiring.
- Offer-choice regression green:
  `.\.venv\Scripts\python.exe -m pytest tests/integration/test_offer_choice.py -q`
  -> 7 passed after fixture child wiring.
- Combined M4 backend focus green:
  `.\.venv\Scripts\python.exe -m pytest tests/integration/test_m4_auth_bootstrap.py tests/database/test_m4_catalog_sql.py tests/integration/test_m4_curriculum_dashboard.py tests/integration/test_m4_fixture_sessions.py tests/integration/test_offer_choice.py -q`
  -> 26 passed.

**Gate status**: Slice 3 locally complete; `.pyc` cleanup verified with remaining count = 0.
Next slice: Mobile signup/login + launch route wiring.

---

### 2026-07-02 - M4 Slice 4 mobile B2C auth and Electricity launch wiring implemented

**Milestone context**: M4 remains active. Slice 4 adds the mobile B2C email/password auth surface
and launch path wiring for Class 10 -> CBSE -> Science -> Electricity. Phone/OTP, B2B
roster/invite activation, admin/content panels, and live LLM generation remain deferred.

**Spec sections used**:
- `phase-3-m4-curriculum-auth-sdd.md` Sections 6.1, 6.2, 8.1, 8.2, 8.3, 12.1, 12.2, and 13.
- `student-api-spec.md` Sections 4, 5, and 8.
- `configuration-reference.md` Section 10.

**Work completed**:
- Added mobile Supabase email/password auth helpers in `mobile/m4/supabaseAuth.ts`.
- Added mobile student API helpers in `mobile/m4/studentApi.ts` for the fixed M4 launch path and
  `POST /v1/student/sessions`.
- Added `mobile/M4CurriculumAuthScreen.tsx` with B2C signup/sign-in, Class 10/CBSE/Science
  Electricity launch state, and session start.
- Updated `mobile/app/App.tsx` so M4 is the default first screen, while preserving the M3 canvas
  and M2 phrase smoke screens behind explicit env flags.
- Documented Expo public config variables in `docs/configuration-reference.md`.

**Verification**:
- Service red baseline:
  `npm.cmd test -- --runInBand __tests__/m4StudentApi-test.ts`
  -> failed because `../../m4/supabaseAuth` did not exist.
- Screen red baseline:
  `npm.cmd test -- --runInBand __tests__/M4CurriculumAuthScreen-test.tsx`
  -> failed because `../../M4CurriculumAuthScreen` did not exist.
- Focused M4 mobile green:
  `npm.cmd test -- --runInBand __tests__/m4StudentApi-test.ts __tests__/M4CurriculumAuthScreen-test.tsx`
  -> 2 suites passed, 6 tests passed.
- Full mobile Jest green:
  `npm.cmd test -- --runInBand`
  -> 26 suites passed, 125 tests passed.
- TypeScript check attempted:
  `npx.cmd tsc --noEmit`
  -> failed on existing broad mobile type setup issues, including missing `global` test typings
  and sibling `../canvas` module type resolution. No focused M4 Jest failure remains.

**Gate status**: Slice 4 locally complete. Next slice: final backend/mobile regression pass,
manual SQL instructions, and implementation review.

---

### 2026-07-02 - M4 Supabase project verified and catalog migration applied

**Milestone context**: M4 implementation has backend, mobile, and live catalog schema/seed work in
place. The Supabase MCP connector was rechecked after plugin reinstall before applying any
migration.

**Spec sections used**:
- `phase-3-m4-curriculum-auth-sdd.md` Sections 6.2, 7, 8.1, 8.2, 12.2, 12.4, and 13.
- `core-operational-schema.md` Section 6.
- `schema-traceability-and-validation.md` Sections 2 through 7.
- `configuration-reference.md` Section 10.

**Work completed**:
- Verified the Supabase connector lists the correct project only:
  `jbmqyxhrmcbdgardamrp` / `conceptsphereai-lab's Project`, region `ap-southeast-2`,
  status `ACTIVE_HEALTHY`.
- Confirmed the previous wrong project ref `ahntbtktjjmvfosgkmgn` was not listed by the
  connector.
- Checked live migration history before applying M4 SQL. Existing live migrations were:
  `0001_phase_1_walking_skeleton` through `0006_m3_schema_alignment`.
- Preflighted live prerequisites: `public.tenants` and `public.current_app_tenant_id()` existed.
- Found the live `public.tenants` table was empty, so updated the local M4 SQL artifact to seed
  the shared individual launch tenant idempotently before inserting the Electricity chapter.
- Applied the reviewed SQL to project `jbmqyxhrmcbdgardamrp` through Supabase migration tooling
  as migration `m4_catalog_auth_seed`.
- Verified live migration history now includes `20260702173751 / m4_catalog_auth_seed`.
- Verified live seed rows for Class 10, CBSE, Science, Electricity, Electricity overview, and
  the individual tenant.

**Verification**:
- Local SQL/catalog test after SQL artifact update:
  `.\.venv\Scripts\python.exe -m pytest tests/database/test_m4_catalog_sql.py -q`
  -> 4 passed.
- Supabase migration application:
  `apply_migration(project_id="jbmqyxhrmcbdgardamrp", name="m4_catalog_auth_seed", ...)`
  -> `success: true`.
- Live migration verification:
  `_list_migrations(project_id="jbmqyxhrmcbdgardamrp")`
  -> includes `20260702173751 / m4_catalog_auth_seed`.
- Live seed verification queries returned:
  `class-10 / Class 10` and `cbse / science / electricity / Electricity /
  electricity-overview / individual`.
- Post-migration backend M4 focus:
  `.\.venv\Scripts\python.exe -m pytest tests/integration/test_m4_auth_bootstrap.py tests/database/test_m4_catalog_sql.py tests/integration/test_m4_curriculum_dashboard.py tests/integration/test_m4_fixture_sessions.py tests/integration/test_offer_choice.py -q`
  -> 26 passed.
- Post-migration focused mobile M4:
  `npm.cmd test -- --runInBand __tests__/m4StudentApi-test.ts __tests__/M4CurriculumAuthScreen-test.tsx`
  -> 2 suites passed, 6 tests passed.
- `.pyc` cleanup after Python tests: remaining `.pyc` count = 0.

**Gate status**: Live catalog migration is applied to the correct Supabase project. Remaining M4
gate before calling the milestone closed: run live Supabase email/password signup/login plus
student launch/session smoke against the deployed/local backend configured for this project.

---

### 2026-07-02 - M4 docs refreshed and gates rerun

**Milestone context**: M4 remains implemented locally with the live catalog migration applied to
the correct Supabase project. The remaining milestone closure gate is still the live
email/password signup/login and launch/session smoke.

**Docs updated**:
- `.augment/rules/00-canon.md` now records M4 as implemented locally with migration
  `20260702173751 / m4_catalog_auth_seed` applied to `jbmqyxhrmcbdgardamrp`.
- `docs/planning/sdd/phase-3-m4-curriculum-auth-sdd.md` is bumped to v0.2 and now reflects
  implementation status, correct Supabase project verification, and the remaining live smoke gate.

**Verification**:
- Backend M4 focus:
  `.\.venv\Scripts\python.exe -m pytest tests/integration/test_m4_auth_bootstrap.py tests/database/test_m4_catalog_sql.py tests/integration/test_m4_curriculum_dashboard.py tests/integration/test_m4_fixture_sessions.py tests/integration/test_offer_choice.py -q`
  -> 26 passed.
- Focused mobile M4:
  `npm.cmd test -- --runInBand __tests__/m4StudentApi-test.ts __tests__/M4CurriculumAuthScreen-test.tsx`
  -> 2 suites passed, 6 tests passed.
- `.pyc` cleanup after Python tests: remaining `.pyc` count = 0.

**Gate status**: Docs and local automated gates are current. M4 is not closed until live
Supabase signup/login plus student launch/session smoke passes.

---

### 2026-07-03 - M4 pre-commit review fixes

**Milestone context**: M4 remains implemented locally with live catalog migration applied; final
live signup/session smoke remains pending before closure.

**Review fixes completed**:
- Root `node_created` payload now uses UUID-shaped provenance for `source_offer_set_id` and
  `source_option_id` instead of a non-UUID sentinel.
- The Electricity fixture provider now marks the end-of-chapter path explicitly with
  `is_terminal=true` and `lineage.completion_state=terminal`.
- Mobile M4 student API calls now use `AbortController` timeouts and preserve backend error
  details such as FastAPI `detail`.
- Supabase JWT verification validates `aud=authenticated` when present while preserving local
  legacy test-token compatibility for tokens that omit `aud`.

**Verification**:
- Focused backend review fix check:
  `.\.venv\Scripts\python.exe -m pytest tests/integration/test_m4_auth_bootstrap.py tests/integration/test_m4_fixture_sessions.py -q`
  -> 12 passed.
- Focused mobile API review fix check:
  `npm.cmd test -- --runInBand __tests__/m4StudentApi-test.ts`
  -> 1 suite passed, 6 tests passed.
- Final pre-commit backend M4 focus:
  `.\.venv\Scripts\python.exe -m pytest tests/integration/test_m4_auth_bootstrap.py tests/database/test_m4_catalog_sql.py tests/integration/test_m4_curriculum_dashboard.py tests/integration/test_m4_fixture_sessions.py tests/integration/test_offer_choice.py -q`
  -> 27 passed.
- Final pre-commit focused mobile M4:
  `npm.cmd test -- --runInBand __tests__/m4StudentApi-test.ts __tests__/M4CurriculumAuthScreen-test.tsx`
  -> 2 suites passed, 8 tests passed.
- `.pyc` cleanup after Python tests: remaining `.pyc` count = 0.
