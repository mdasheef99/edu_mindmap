# AGENT ROTATION INSTRUCTION — READ FIRST

This is the active worklog as of 2026-07-10. Keep it below 350 lines and rotate before exceeding
that threshold.

## Legacy Context Summary

- `worklog-v9.md` is closed at 567 lines. It records the original M4 implementation and browser
  smoke debugging.
- M3-C, M3.5, and M3.6 remain closed. Do not reopen them.
- M4 is closed as of 2026-07-11; M5 Checkpoints is next and has not started.
- Parent SDD: `phase-3-m4-curriculum-auth-sdd.md` v0.6 (closed).
- Remediation SDD: `phase-3-m4-runtime-closure-remediation-sdd.md` v0.3 (closed).
- Supabase MCP is connected to the correct project `jbmqyxhrmcbdgardamrp`.
- Live migration `20260702173751 / m4_catalog_auth_seed` is applied.
- The original M4 code was a useful smoke prototype; the remediated API and worker now share the
  durable Postgres runtime.

## 2026-07-10 — M4 runtime audit and remediation opened

**Source sections**:

- `development-approach.md` §§5, 6, 8.1-8.2.
- `backend-architecture.md` §§3, 5.3-5.5, 6-8, 11-12.
- ADR-0002, ADR-0007, ADR-0008, ADR-0014, and new ADR-0017.
- `session-path-data-contract.md` §§5-11.
- Parent M4 SDD §§6, 8.4, 10, 12-14.
- Active remediation SDD §§2-5.

**Audit evidence**:

- Repository moved back to the configured workspace path without changing the dirty branch.
- Supabase MCP lists only `jbmqyxhrmcbdgardamrp`, status `ACTIVE_HEALTHY`.
- Live schema/migrations verified. Catalog seed rows exist, but memberships, events, jobs,
  consent records, and student sessions contain zero rows.
- `create_app()` defaults to `SessionRuntime.for_testing()` and seeds an in-memory catalog.
- Render API start command invokes that default runtime; the worker separately uses Postgres.
- Mobile is a fixed Electricity smoke screen without auth restore, dashboard, picker, or resume.
- Expo web lacks CanvasKit setup/deferred Skia loading.
- Backend M4 focus: 29/29 green with in-memory runtimes; final `.pyc` count 0.
- Mobile full Jest: 128/130; focused M4: 10/11; TypeScript red.

**Supabase advisor evidence**:

- Security: leaked-password protection warning only.
- Performance: missing covering indexes for four `public.chapters` foreign keys and
  `public.subjects.class_level_id`; unused-index notices expected on the empty runtime tables.

**Decision**: preserve reusable M4 feature code, reclassify it as a local smoke prototype, and
close production composition plus mobile closure gaps red-first under the remediation SDD.

## 2026-07-10 — M4 automated remediation complete; human gates pending

**Implemented and verified**:

- Added forward migration `0007_m4_runtime_remediation.sql`; applied live as
  `20260710075416 / m4_runtime_remediation` to Supabase project `jbmqyxhrmcbdgardamrp`.
- Default `create_app()` now fails closed without production configuration and composes pooled
  Postgres events, jobs, memberships, consent, catalog, curriculum, and student-session stores.
- Added structural runtime ports so workflows do not depend on `InMemory*` implementations.
- Aligned live JWT verification with Supabase ES256/JWKS through ADR-0017.
- Consent now requires the explicit mobile acknowledgement, writes one append-only audit event
  plus one durable entity, and leaves unacknowledged learners outside analytic projection.
- Added auth restoration/refresh/sign-out, secure session storage, dashboard Continue Learning,
  recent-session resume, API-derived curriculum selection, and real canvas handoff.
- Removed normal-path hard-coded Supabase/API credentials; production builds fail closed when
  `EXPO_PUBLIC_*` M4 configuration is absent.
- Added CanvasKit-first web entry, generated `public/canvaskit.wasm`, and corrected Metro's shared
  `mobile/{app,canvas,m4}` source root. Expo web export is green.
- Live durable smoke passed signup/bootstrap → acknowledged start → branch → runtime recreation →
  dashboard → resume/hydrate; Postgres worker completed the classify job and wrote its event/read
  model using the same database.
- Final consent-aware live session `0726e14d-2414-4038-9e7a-494da269b9d6` read back with one
  granted consent entity, one completed classify job, one `question_classified` event, and one
  `analytic_rm.question_classifications` row.

**Automated gates**:

- Backend: 145/145 non-import-linter tests green; 4/4 isolated import-linter contract tests green
  with workspace-local pytest temp; direct import-linter 4/4 contracts kept.
- Mobile: TypeScript green; Jest 27/27 suites and 133/133 tests green.
- Web: Expo production export green and includes `dist/canvaskit.wasm`.
- Python bytecode cleanup verified: `.pyc` count 0.

**Remaining before M4 closure**:

- Native Android stranger signup → dashboard → Electricity → canvas human gate.
- Interactive web browser render check for absence of `PictureRecorder` errors. The export gate is
  green, but the in-app browser control runtime was unavailable in this session.
- Stage/live app-role cross-tenant RLS smoke if the available database credential bypasses RLS.

## 2026-07-10 — Physical-device server opened

- Fresh import-linter run: 4/4 contracts kept, 0 broken.
- Fresh live schema readback: all 15 required catalog/operational/read-model tables expose
  `tenant_id` and have RLS enabled, including the five catalog tables remediated by migration 0007.
- Initial LAN manifest check exposed that the web-oriented Metro `projectRoot` change broke native
  asset lookup. Replaced it with a narrow Windows sibling-source resolver while retaining
  `mobile/app` as the Expo project/asset root.
- Durable backend is listening on `0.0.0.0:8000`; Expo Go LAN server is listening on `:8081` at
  `exp://192.168.31.183:8081`.
- Android manifest returned 200 and the cold Hermes bundle completed successfully: 1,822 modules,
  11,243,312 bytes. Physical-device user validation remains pending.

## 2026-07-10 — Canon, specification, and intelligence reconciliation

- Re-read the complete physical `.augment/rules/00-canon.md`, active SDD/worklog, full canonical
  source hierarchy, every file in `CODEBASE_INTELLIGENCE/`, and the relevant API/database/config
  specifications before updating documentation.
- Verified directly that `0007_m4_runtime_remediation.sql` adds and backfills `tenant_id` for the
  five affected public M4 catalog tables, makes it non-null, adds tenant foreign keys/indexes, and
  replaces permissive catalog policies with tenant-isolation RLS policies. This matches the fresh
  live readback already recorded above.
- Updated canon and the API/database traceability specs for M4 B2C auth bootstrap, explicit
  consent-aware session start, deterministic root-node creation, and the forward-only tenant
  remediation.
- Refreshed the complete codebase-intelligence pack from the old M2/in-memory snapshot to the
  durable M4 production runtime. Recorded honestly that Augment retrieval was unavailable in this
  session and that direct repository/live evidence was used instead.
- Corrected configuration references to the names actually read by `App.tsx`:
  `EXPO_PUBLIC_API_BASE_URL` and `EXPO_PUBLIC_SENTRY_DSN_MOBILE`; parent M4 SDD backend auth config
  now reflects live ES256/JWKS with HS256 secret limited to test fixtures.
- Documentation/config-only consistency gate: targeted stale-text scan clean, all intelligence
  files below the 300–350 line limit, and `git diff --check` clean. Full automated suites were not
  rerun because no production behavior changed; the latest green evidence remains the preceding
  149 backend / 133 mobile / 4 import-contract results.
- Restarted the physical-device services after the prior processes had exited. A first backend
  attempt with system Python correctly failed on missing `psycopg_pool`; restarted with the
  workspace `.venv`. Credential-safe DB probe passed; backend and Expo LAN endpoints both return
  200 at `192.168.31.183:{8000,8081}`. Python bytecode cleanup: 0 remaining `.pyc`.

## 2026-07-11 -- Physical-device M4 gate remediation

**Device evidence from the user**:

- Login works, recent sessions are visible, resume works, and the canvas opens after starting the
  Electricity session.
- Dashboard load is slow.
- Learning-data acknowledgement appears every time even after consent was given for the account.
- Sign-out returns to login, but signing in again can fail with `Student API failed: 401: Invalid
  Supabase token`.
- Only Electricity is visible. This matches the bounded M4 launch scope.

**Investigation evidence**:

- Supabase MCP remained available against project `jbmqyxhrmcbdgardamrp`.
- Supabase auth logs showed password sign-in returning HTTP 200 for the device account, including
  the re-login path, so the visible 401 was backend verification/session handling rather than bad
  credentials.
- Live consent readback showed an active behavioral-analytics grant for the account; the repeated
  prompt happened because bootstrap did not return consent state.
- Backend logs showed repeated JWKS endpoint calls during one M4 app initialization. The ES256
  verifier created a fresh `PyJWKClient` per authenticated request, violating the intended
  cached-key ADR-0017 path and adding latency/failure surface.
- A first consent-state implementation briefly introduced a transitive import-linter violation
  (`app.api.student.auth -> app.runtime.session_workflow -> app.projections.student_sessions`).
  That helper import was removed; the auth router now uses its injected consent port directly.

**Implemented**:

- Cached Supabase JWKS clients in `backend/app/tenancy/membership_auth.py`.
- Added `behavioral_analytics_consent_granted` to the bootstrap response and mobile API mapping.
- Suppressed the acknowledgement UI when bootstrap reports an active grant.
- Rendered dashboard state before the sequential curriculum path finishes loading.
- Added Supabase remote logout before local SecureStore clearing, retaining local clearing as the
  fallback on logout network failure.

**Verification**:

- Focused backend auth/bootstrap tests: 9/9 green.
- Focused mobile M4 screen/API tests: green.
- Full mobile Jest: 27/27 suites, 136/136 tests green.
- TypeScript: `npx.cmd tsc --noEmit` green.
- Backend behavior tests: 147 green.
- Import-linter subprocess tests: 4/4 green when run with the user-level executable outside the
  sandbox; direct import-linter output reports 4 kept, 0 broken.

**Remaining**:

- Restart physical-device backend and Expo services with the fixed code.
- Native Android retest: sign in, confirm faster dashboard, confirm consent stays recorded,
  sign out, sign in again, bootstrap/dashboard should not produce the invalid-token error.

## 2026-07-11 -- Physical-device JWT clock-skew remediation

**Device evidence**:

- Fresh Supabase password sign-in reached `Loading dashboard`, then bootstrap returned
  `401 Invalid Supabase token` repeatedly.
- Safe server-side diagnostics identified the exact PyJWT failure as
  `ImmatureSignatureError: The token is not yet valid (iat)`; signature/auth-server login had
  succeeded, but ES256 verification allowed zero clock difference.
- Windows time-change history showed repeated hardware-clock corrections, while PyJWT 2.9 uses
  zero leeway unless the verifier supplies one.

**Implemented**:

- Added a fixed 30-second clock-skew tolerance to the ADR-0017 ES256/JWKS decode path. Signature,
  issuer, audience, `iat`, `nbf`, and expiry validation remain enabled; a token 120 seconds in the
  future remains rejected.
- Temporarily added safe auth-failure diagnostics to identify the exact PyJWT exception without
  logging tokens; removed the diagnostic after confirming the bounded-tolerance fix live.
- Hardened all local M4 backend runners to load repository `.env` values explicitly and override
  unrelated parent-process configuration; LAN runners bind to `0.0.0.0:8000`.

**Verification**:

- Red-first ES256 boundary test: +20-second token initially returned 401.
- Focused bootstrap suite after implementation: 10/10 green.
- Broader auth integration set: 15/15 green.

**Remaining**:

- Explicitly repeat the native sign-out -> fresh sign-in sequence after the final correction.

**Live partial retest evidence**:

- After backend restart with the 30-second tolerance, the device restored its stored Supabase
  session without asking for credentials. Backend access logs show multiple bootstrap 200s,
  dashboard 200s, the complete Class 10 -> CBSE -> Science -> Electricity catalog path at 200,
  existing-session resume/hydration at 200, event ingest at 202, and offer creation/choice writes.
- The prior `ImmatureSignatureError` did not recur. This confirms auth restoration and active
  session use, but it does not substitute for an explicit post-fix sign-out -> sign-in retest.
- The current catalog contains only the bounded M4 launch path. The mobile client derives that
  path from API responses, but the UI intentionally does not present arbitrary class/exam/subject/
  chapter choices when there is only one supported path. General curriculum selection remains
  outside M4 per the active SDD section 6.

## 2026-07-11 -- M4 closed

**Final evidence**:

- The user reports the corrected physical-device flow is working. Live backend logs corroborate
  repeated bootstrap/dashboard/catalog 200s, session resume/hydration 200s, new session 201,
  event/choice 202s, branch creation 201s, and node-position persistence 200.
- The post-fix JWT path no longer emits `ImmatureSignatureError`; bounded +20-second tolerance and
  far-future rejection remain covered by tests.
- Live `test_real_postgres_rls_isolation_through_tenant_context` passed through the configured
  non-bypass `TEST_DATABASE_URL`, closing DB-2.
- Chrome extension control was unavailable, so no interactive-browser evidence is claimed.
  Interactive web is explicitly excluded from the native-first M4 closure gate under active SDD
  R7/definition-of-done item 9. The production Expo export with `canvaskit.wasm` remains green;
  interactive web rendering is a non-blocking follow-up.
- Curriculum loading is progressive but sequential across class, exam, subject, chapter, and
  concept-entry endpoints. A short delay is expected for the bounded one-path M4 catalog and is
  not a closure blocker.

**Status**: Phase 3 M4 Curriculum Entry + Supabase Auth is CLOSED. M5 Checkpoints is next and has
not started.

## 2026-07-11 -- Bounded pre-M5 canvas position-write stabilization

**Milestone boundary**:

- M4 remains closed and M5 remains frozen/not started.
- This is a bounded canvas stabilization increment, not a formal M4.5 milestone.
- Governing references are `development-approach.md` §§5 and 8,
  `configuration-reference.md` §4, the closed M3/M3-C/M3.6 canvas SDDs, ADR-0013, and
  `session-path-data-contract.md` §§6, 8, and 11.
- Active bounded design record: `canvas-position-write-lifecycle-sdd.md` v0.5.

**Investigation conclusions**:

- The prior drag-end helper was fire-and-forget, so network/non-2xx failure was not observable.
- Rapid completed drags had no per-node request-order guarantee; local overrides could mask
  unsettled durability and hydration lacked causal revision metadata.
- Branch creation and initial child positioning are separate durable operations. A failed child
  PATCH must retain the created branch and must not report full placement success.
- Deterministic layout is not part of the real hydration/branch path, missing positions can still
  reach the existing `{0,0}` fallback, and layout/manual-reference correction remains excluded.

**Implemented red-first**:

- Phase A: `patchNodePosition` is a typed checked promise; `nodePositionCoordinator.ts` provides
  independent per-node FIFO queues, newest-intent visibility, failure pause/retry, acknowledged
  fallback, and disposal safety. Completed drag writes are not coalesced.
- Phase B1: `useNodePositionWrites.ts` owns one coordinator per mounted session, subscribes through
  stable snapshots, reads refreshed credentials for later writes, preserves acknowledged/queued
  mounted-session authority over stale hydration, and exposes failed-node aggregation/retry.
  `SkiaCanvas` now enqueues at drag end and shows one neutral canvas-level retry status without
  adding gesture-frame React/network writes.
- Phase B2: `EdgeOfferSetSheet` uses the checked PATCH directly, keeps recovery local after durable
  branch creation, retries placement without repeating creation, and provides idempotent
  `Close and reload`. Initial creation and retry are single-flight; late settlement and unmount are
  guarded; a missing child id cannot trigger an unsafe retry or false success claim.
- No backend, schema, migration, event, layout, navigation, global test configuration, optimistic
  insertion, persistent retry, M5, or checkpoint behavior changed.

**Verification**:

- Focused B2 recovery: 12/12 green with no new act warnings, unhandled rejections, or open handles.
- Nearest branch/discovery/API/coordinator/hook/canvas regression set: 8 suites, 53/53 green.
- Full mobile Jest: 31 suites, 165/165 green.
- TypeScript: `npx.cmd tsc --noEmit` green.
- `git diff --check` green; `SkiaCanvas.tsx` is 310 lines and `EdgeOfferSetSheet.tsx` is 230 lines.
- Existing warning output in older phrase-selection, Skia canvas, node-selection, and SafeAreaView
  tests remains pre-existing; the new B2 file is clean in isolation.

**Physical-device readiness and remaining review**:

- Durable backend and Expo Go LAN endpoints return HTTP 200 at `192.168.31.183:{8000,8081}`; the
  Android manifest returns `application/expo+json`, and the phone established Metro connections.
- Direct learner validation of drag ordering, visible failure/retry behavior, branch-placement
  recovery, resume, and Android interaction quality remains pending. Server reachability is not
  recorded as behavioral proof.
- Known limits remain: no causal snapshot revision/watermark, no delivery guarantee across
  unmount/termination, non-atomic branch creation/placement, and the existing `{0,0}` fallback for
  an unpositioned child.

**Status**: completed bounded stabilization record; Android review accepted 2026-07-12.
M5 remains frozen.

## 2026-07-12 -- Canvas stabilization Android review and bounded follow-ons

**Observed and corrected**:

- Dragged edges briefly followed the committed node centre because their geometry took a
  UI-thread to JS to React-state path during movement. `CanvasEdges` now derives only edges
  attached to the actively dragged node from the same Reanimated SharedValues as the native node;
  React/canonical/coordinator updates remain drag-end only.
- Edge-plus controls had no immediate feedback or request guard. `EdgePlusButtons` now provides
  per-node shared left/right busy state, neutral loading/failure/retry feedback, and single-flight
  request protection. `useDiscoveryManager` accepts the first current discovery completion only,
  preventing later competing success/failure from replacing the sheet or surfacing stale error.

**Verification**:

- New edge-plus lifecycle tests: 5/5 independently; nearest edge-plus/discovery tests: 16/16.
- Focused edge/gesture/position regressions: 13 suites, 68/68.
- Final full mobile Jest: 32 suites, 170/170 green; TypeScript remains green.
- TypeScript and `git diff --check` green; final relevant runs reported no new warnings, open
  handles, or unhandled rejections.
- User physical-device review confirms both corrections are working.

**Boundary preserved**:

- No change to `useCanvasGestures`, Race/Simultaneous composition, backend endpoints/schemas,
  migrations, event contracts, position coordinator semantics, deterministic layout, `{0,0}`
  fallback, `manual_reference` hierarchy, navigation, or M5.
- The bounded stabilization record is complete, not a formal M4.5 milestone. M5 remains frozen
  until separately authorized.

**Still pending outside this completed slice**:

- Deferred M3 physical performance evidence: 40+ node 60fps rerun and 65-node smoke.
- Interactive web CanvasKit runtime review.
- A separately approved layout/position-quality slice, if desired, for deterministic hydration
  placement, missing-position fallback, and manual-reference hierarchy semantics.
