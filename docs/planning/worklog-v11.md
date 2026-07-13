# AGENT ROTATION INSTRUCTION — READ FIRST

This is the live tracker for the local post-PR-6 reconstruction of the historically closed M4
implementation. Keep it below 350 lines and rotate before exceeding that threshold.

## Legacy Context Summary

- `worklog-v9.md` and `worklog-v10.md` are immutable historical M4 evidence.
- Phase 3 M4 remains historically closed as of 2026-07-11; M5 has not started.
- The reconstruction base is the PR #6 merge on `main`.
- This work restores M4 without redesigning product behavior, API contracts, membership
  semantics, tenant isolation, database behavior, mobile flow, or closure evidence.
- Live Supabase migration application and physical-device testing are excluded from this local
  reconstruction stage.

## 2026-07-13 — Local M4 reconstruction opened

**Source sections**:

- `development-approach.md` §§5–8.
- `backend-architecture.md` §§5.3–5.5, 6–8, and 11–12.
- ADR-0017.
- `session-path-data-contract.md` §§5–11.
- Closed M4 parent SDD §§6, 8.4, 10, and 12–14.
- Closed M4 remediation SDD R1, R4, R5, PR-1, PR-2, and DB-1.

**Approved boundaries**:

- Reconstruct from the final M4 snapshot; do not cherry-pick the historical range.
- Preserve PR #6 CORS and fail-closed development configuration.
- Production authentication is ES256/JWKS only.
- HS256 exists only as an explicitly injected deterministic test-fixture verifier.
- `M4_INDIVIDUAL_TENANT_ID` is required production configuration.
- Preserve the applied M4 SQL artifacts unchanged; clarify their order with a manifest.
- Defer event-registry extraction and preserve current 401 handling for JWKS failures.

**Red-first evidence**:

- Added configuration, production-HS256 rejection, fixture-isolation, and migration-manifest
  tests before implementing the cleanup.
- Initial focused run: 18 failed / 7 passed for the intended missing M4/configuration boundaries.
- After implementation: 29/29 focused tests green.

**Implemented so far**:

- Typed fail-closed production configuration with explicit database, Supabase issuer/JWKS,
  individual tenant, and CORS inputs.
- Explicit ES256/JWKS production verifier and separate HS256 fixture verifier.
- Durable production composition contains no fallback secret or implicit tenant.
- Migration-source manifest distinguishes Alembic and applied Supabase histories without changing
  either applied SQL artifact.
- Historical M4 app shell is manually reconciled with PR #6 development Canvas configuration;
  no embedded credential or machine-specific URL is used.

**Local verification evidence**:

- Ruff format: 145 files already formatted; Ruff lint: all checks passed.
- Mypy: 94 application source files green.
- Import-linter: four contracts kept, zero broken.
- Full Python suite: 164 passed / 3 skipped.
- Focused configuration, authentication, tenant-isolation, runtime, migration-order, and session
  suite: 30 passed.
- Full mobile Jest suite: 28 suites / 139 tests passed.
- App and Canvas TypeScript checks: green.
- `git diff --check`: green after owner-approved removal of two trailing spaces from the closed
  remediation SDD header; no prose or behavior changed.
- Sensitive-value scan found no JWT-shaped tokens or private-key material. URL/credential-pattern
  hits are confined to immutable historical evidence, explicit example/test fixtures, and typed
  credential parameters; production configuration contains no embedded value.
- Only `.env.example` is present in the reconstruction worktree. Generated-file count is zero;
  Python bytecode count is zero.

**2026-07-13 final rerun**:

- Ruff format/lint, Mypy, and all four import-linter contracts are green.
- Full Python suite: 164 passed / 3 skipped using a worktree-local pytest temporary directory.
- Full mobile Jest suite: 28 suites / 139 tests passed; App and Canvas TypeScript are green.

**Physical-device reconstruction evidence**:

- The owner confirmed that the reconstructed M4 branch passed the current physical-device smoke
  check after the final local publication gates.
- The report did not enumerate the individual actions exercised, so this reconstruction record
  does not separately claim sign-up/sign-in, bootstrap, curriculum/dashboard loading,
  creation/resume, canvas hydration, restart restoration, or sign-out beyond the confirmed smoke
  result. Live Supabase/key-rotation and migration-application checks remain separately deferred.

**Remaining operational gates**:

- Live Supabase ES256/JWKS, key rotation, membership bootstrap, and applied-migration verification
  require explicit project configuration and credentials.
- The closed physical-device flow remains operational evidence and was not rerun in this local
  reconstruction stage.
- Create local commits only; do not push or open a PR without separate approval.

## 2026-07-13 — Canvas position lifecycle reconstruction locally complete

**Authority and boundary**:

- `development-approach.md` §§5, 7–8; ADR-0013; ADR-0016;
  `session-path-data-contract.md` §§5–11; the M3, M3-B, M3-C, M3.6, and closed M4 SDDs;
  `canvas-position-write-lifecycle-sdd.md` §§1–8.
- Bounded post-M4/pre-M5 stabilization only. No `App.tsx`, backend, API/schema, event, migration,
  authentication, curriculum, membership, tenancy/RLS, dependency, or lockfile change.

**Red-first evidence**:

- Core command failed 4/4 suites for intended missing checked PATCH, coordinator/hook, and Zustand
  position-session APIs before production implementation.
- Rendering command failed for intended concurrent drag writes, static edge/label geometry,
  missing cancellation finalizer, old render-data signature, and missing retry UI.
- Placement/discovery command failed for intended missing durable-placement recovery,
  edge-plus single-flight/retry state, and discovery generation ownership.

**Implemented**:

- Session-scoped finite canonical position authority in the existing Zustand store; hydration
  cannot overwrite manual authority, session switch/sign-out resets it, and deletion removes it.
- Checked position PATCH plus per-node FIFO coordinator, cross-node concurrency, latest-intent
  visibility, retry, and stale completion invalidation.
- One drag-end commit, zero cancellation commit, shared committed node/culling/hit-test authority,
  and UI-thread edge/label geometry. The JS/React drag mirroring hook and test were removed.
- Durable child branch placement recovery retries only PATCH or closes through one reload boundary.
  Edge-plus requests are single-flight/retryable and first valid discovery completion wins.

**Local verification**:

- Focused mobile lifecycle/rendering/recovery suites green; full mobile 35 suites / 159 tests.
- App and Canvas TypeScript green.
- Focused backend PATCH/replay/hydration/deletion/resume: 22 passed.
- Full Python: 164 passed / 3 skipped; Ruff format/lint, mypy, and 4/4 import contracts green.
- `git diff --check` green; Python bytecode count under source/test roots zero.
- No physical-device, 40+ node performance, 65-node smoke, live database, push, or PR action.

## 2026-07-13 — Placement-recovery publication blocker resolved

- Root cause was test-harness wall time, not production behavior: the component deliberately
  launches an async POST→PATCH chain from a `void` press callback, while the test relied on
  real-timer polling and cold native Modal/Button/ScrollView rendering inside one five-second case.
- The test now isolates those native wrappers, explicitly warms the renderer, and resolves the
  creation, failed placement, and successful retry promises inside controlled `act` scopes.
  Assertions still prove one branch POST, placement-only retry, durable failure UI, failure-state
  clearing, one completion callback, and close/reload recovery.
- Default-timeout target case: 1 passed; complete file: 2 passed; focused placement/discovery:
  4 suites / 15 tests passed.
- Three consecutive normal `npm test` runs passed: 35 suites / 159 tests each. App/Canvas
  TypeScript, Python 164 passed / 3 skipped, Ruff format/lint, mypy, and 4/4 import contracts are
  green. No timeout, worker-count, retry, or suite-selection override was used for full runs.
