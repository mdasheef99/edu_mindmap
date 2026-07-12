<!-- worklog-v8.md — CLOSED ARCHIVE. Opened 2026-06-25; rotated from worklog-v7.md (405 lines, past ~350 threshold). -->
<!-- Rotated forward to docs/planning/worklog-v9.md on 2026-07-02 before M4 implementation planning. -->
<!-- Prior history: worklog-v7.md | worklog-v6.md | worklog-v5.md -->

---

### 2026-06-25 — `backend/app/main.py` God-Object decomposition: complete

**Phase / milestone**: Phase 3 — pre-M4 housekeeping (composition root clean-up).

**Spec sections used**:
- `CODEBASE_INTELLIGENCE/01-system-map.md` §Backend (Modular Monolith layer responsibilities).
- `00-canon.md` (300–350-line source-file canon limit; Category Invisibility; import-linter contracts).
- `backend-architecture.md` §2 (layered module responsibilities; api ⇏ analytic invariant).

**Context**: `backend/app/main.py` had grown to 416 lines, acting as a "God Object" containing
the `SessionRuntime` DI container (session lifecycle, curriculum, offer, node, and consent
orchestration), `InMemoryMembershipStore`, JWT auth resolution, and the FastAPI composition root
all in one file. This violated the 300–350-line canon limit and concentrated unrelated
responsibilities that would make the upcoming M4 Supabase Auth integration riskier.

**Work completed** (commits on `phase-3-m3`):

*New modules extracted:*
- `backend/app/tenancy/memberships.py` (22 lines) — `InMemoryMembershipStore`; tenant role registry.
- `backend/app/tenancy/membership_auth.py` (41 lines) — `resolve_membership_auth`; JWT decode + role
  lookup; decoupled from `SessionRuntime` to allow duck-typed caller in `app/tenancy/auth.py`.
- `backend/app/runtime/session.py` (304 lines) — `SessionRuntime` dataclass + `for_testing` factory;
  all public methods are thin delegators to dedicated workflow functions; no orchestration inline.
- `backend/app/runtime/session_workflow.py` (117 lines) — `start_session_workflow`,
  `resume_student_session_workflow`, `get_student_session_with_canvas_workflow`.
- `backend/app/runtime/curriculum_workflow.py` (56 lines) — `resolve_session_request`,
  `render_teacher_chapter_graph`.
- `backend/app/runtime/node_position_workflow.py` (65 lines) — `update_node_position_workflow`.

*Composition root reduction:*
- `backend/app/main.py`: **416 → 58 lines**. Now a pure composition root: app instantiation,
  CORS + Sentry middleware, router inclusion, and re-exports of `SessionRuntime` /
  `InMemoryMembershipStore` via `__all__` for backward compatibility.

*Post-refactor cleanup (commit `590faf3`):*
- Deleted orphaned `_resolve_session_request` delegator from `session.py` (zero callers; left
  behind when `start_session` was rewritten to delegate through `start_session_workflow`).
- Removed now-unused `resolve_session_request` import from `session.py`.
- Typed `curriculum: InMemoryCurriculumStore` in `start_session_workflow` (stale "avoided circular"
  comment removed; no cycle existed — the dependency edge to `app.projections.curriculum` was
  already present transitively via `curriculum_workflow`).
- `session.py`: **313 → 304 lines** after cleanup.

**Backward compatibility preserved**:
- `from app.main import SessionRuntime, InMemoryMembershipStore, create_app` continues to work
  via `__all__` re-exports. Zero changes required to any of the 15+ integration test files or
  `dev_smoke_bootstrap.py`.
- Duck-typed `request.app.state.session_runtime` pattern in all API routers unchanged —
  no circular-import risk introduced.

**Verification**:
- Import-linter: **4/4 contracts kept** (`Student API must not import analytic internals`,
  `Generation must not import classification or analytic internals`,
  `Chapter analysis must not import generation or classification`,
  `Chapter analysis must not import API modules`) — Category Invisibility intact.
- Full pytest: **121/121 passed** — zero regressions across all integration suites.
- `.pyc` cleanup: **0 files remain** after each step.

**File-size summary post-cleanup**:

| File | Lines | Status |
|---|---|---|
| `backend/app/main.py` | 58 | ✅ Pure composition root |
| `backend/app/runtime/session.py` | 304 | ✅ Within 300–350 band |
| `backend/app/runtime/session_workflow.py` | 117 | ✅ |
| `backend/app/runtime/curriculum_workflow.py` | 56 | ✅ |
| `backend/app/runtime/node_position_workflow.py` | 65 | ✅ |
| `backend/app/tenancy/memberships.py` | 22 | ✅ |
| `backend/app/tenancy/membership_auth.py` | 41 | ✅ |

**Watch item**: `session.py` at 304 lines has limited headroom. M4 Supabase Auth will touch
`resolve_auth` and may add membership/role wiring; plan where that lands before adding behaviour
to avoid crossing the 350-line ceiling mid-feature.

**Gate status**: housekeeping complete; no new behaviour; 121/121 green; M4 not yet begun.

**Next required actions**:
1. Begin M4 (Curriculum entry + Supabase Auth) per `development-approach.md` §5 M4.
2. `useSessionHydration` `DEV_*` constant wiring → real Supabase session (M4 auth work, carried
   from M3-C housekeeping).

---

### 2026-06-25 — Phase 3 M3.5 Frontend Readiness bridge verified / complete

**Phase / milestone**: Phase 3 — M3.5 bridge (post-M3-C, pre-M4).

**Spec sections used**:
- `docs/planning/sdd/phase-3-m3-5-frontend-readiness-sdd.md` F1-F7.
- `.augment/rules/00-canon.md` (red-tests-first, Category Invisibility, file-size canon, source-of-truth hierarchy).
- `docs/planning/development-approach.md` §5 (M3 canvas maturation, M4 next milestone).
- `docs/planning/sdd/phase-3-m3b-canvas-feature-parity-sdd.md` §1-§9 (edge labels, edge `+`, node selection/toolbar, culling, node limits).
- `docs/planning/sdd/phase-3-m3c-infrastructure-remediation-sdd.md` §5, §8 (session hydration, real canvas snapshot).

**Context**: M3-C closed the infrastructure remediation gaps; M3.5 was a bounded hardening pass to
make the already-built learner-facing canvas credible before attaching real M4 auth/curriculum
entry. The focus was F1-F7: learner-safe UI states, node text, edge `+` error handling, branch
reload reconciliation, phrase-selection smoke visibility, delete/position UI tests, and canon file
size discipline.

**Work completed** (no new production code — documentation/verification closure only):

- Updated `docs/planning/sdd/phase-3-m3-5-frontend-readiness-sdd.md`:
  - Status transitioned from "Locally complete" to **Verified / Complete**.
  - Implementation Notes (§9) now explicitly state that NodeChip, useSessionHydration, and
    SkiaCanvas changes were verified by both automated Jest tests and physical device Expo Go
    inspection.
  - Verification Results (§10) reconciled mobile Jest count from M3-C baseline of 92 to
    **97 passing tests** (18 suites), and documented the increase as the 5 new M3.5 tests.
  - Physical device verification paragraph added: pan/zoom, node chips, edge `+` buttons, node
    selection toolbar, and neutral error banner inspected on-device with
    `EXPO_PUBLIC_SHOW_CANVAS=true`.
  - Residual Risks (§11) clarified that the TS2688 `jest` type-definition issue remains a
    known, pre-existing, non-blocking config blocker.

- Updated `.augment/rules/00-canon.md`:
  - Added M3.5 bridge as **VERIFIED / COMPLETE** with 18 suites / 97 mobile Jest green and
    physical device Expo Go smoke passed.
  - Changed active SDD to `docs/planning/sdd/phase-3-m3-5-frontend-readiness-sdd.md`.

**Verification**:
- Mobile Jest: **18 suites / 97 tests passed** (M3-C baseline was 92/92; +5 new tests).
- Focused M3.5 test run: **5 suites / 35 tests passed** (nodeChip-test, useSessionHydration-test,
  skiaCanvas-test, PhraseSelectionReaderSheet-test, edgePlusButton-test).
- Physical device: M3.5 canvas launched in Expo Go; node chips render learner-safe text, edge `+`
  failure shows the neutral banner, pan/zoom and selection toolbar behave as expected.
- TypeScript: `tsc --noEmit -p ..\canvas\tsconfig.json` still blocked by existing `TS2688` Jest
  type-definition resolution issue. No source changes made; no `.pyc` cleanup required.

**Residual risks carried into M4**:
- TS2688 type-check config remains a non-blocking blocker for full `tsc` verification.
- App still uses dev constants for `apiBaseUrl`, `sessionId`, and auth token until M4.
- Full offline reopen and real auth/curriculum/dashboard are out of scope for M3.5.

**Gate status**: M3.5 bridge closed. No new behaviour; 97/97 mobile Jest green; device smoke passed.
M4 (Curriculum entry + Supabase Auth) is now the next canonical milestone.

**Next required actions**:
1. Begin M4 per `development-approach.md` §5 M4 (Supabase Auth + curriculum entry).
2. Replace `App.tsx` `DEV_API_BASE_URL`, `DEV_SESSION_ID`, and `DEV_AUTH_TOKEN` with real
   Supabase/curriculum wiring.

---

### 2026-06-30 — Phase 3 M3.6 Canvas Controls: locally complete pre-M4 slice

**Milestone context**: M3-C and M3.5 are locally complete. M4 remains the next non-canvas milestone,
but the owner approved a small pre-M4 canvas-control slice to promote already-specified core UI
controls into the consolidated MVP scope before implementation.

**Protocol order**:
1. Update `docs/mvp-features-specification.md` first to record the MVP scope change under Feature
   Group 3.
2. Align supporting feature/spec docs already referenced by the MVP spec.
3. Create the bounded M3.6 SDD only after the MVP and supporting docs agree.
4. Implement red-first mobile Jest coverage before production code.

**Spec sections used**:
- `development-approach.md` §5 M3 (canvas pan/zoom/gesture maturity) and §5 M4 (next milestone).
- `docs/mvp-features-specification.md` Feature Group 3 (Mind Map Canvas), Feature 3.1 and
  Feature 3.5.
- `docs/mobile-features-core-ui.md` §3.1 (Navigation), §3.3 (Layout), §3.4 (Grid and Snap),
  §3.6 (Canvas constraints).
- `docs/configuration-reference.md` §3 (`CANVAS_MIN_ZOOM`, `CANVAS_MAX_ZOOM`,
  `CANVAS_GRID_SIZE_PX`, `VIEWPORT_EVENT_THROTTLE_MS`).
- `docs/architecture/adr-log.md` ADR-0013 and `docs/architecture/adr-log-02.md` ADR-0016.
- `docs/planning/sdd/phase-3-m3-6-canvas-controls-sdd.md`.

**Implemented scope**:
- Zoom in / zoom out toolbar buttons.
- Fit to screen.
- Reset view.
- Visible zoom percentage readout.
- Snap-to-grid toolbar toggle that snaps only final drag-end node positions to the fixed 15px grid.

**Explicit non-scope**:
- M4 auth/curriculum/dashboard work.
- Visible grid rendering, custom grid size, minimap, auto-layout, alignment guides, multi-select,
  lasso selection, and undo/redo.

**Work completed**:
- Updated `docs/mvp-features-specification.md` first, then aligned
  `docs/mobile-features-core-ui.md`, then created
  `docs/planning/sdd/phase-3-m3-6-canvas-controls-sdd.md`.
- Added red-first pure helper coverage for zoom clamping, fit-to-screen, reset transform, zoom
  readout, and grid snapping in `mobile/canvas/__tests__/canvasControls-test.ts`.
- Added `mobile/canvas/canvasControls.ts` for bounded viewport math and snap rounding.
- Added `mobile/canvas/CanvasToolbar.tsx` as a separate compact toolbar component to keep
  `SkiaCanvas.tsx` under the canon line band.
- Wired toolbar actions through the same transform-end path used by canvas gestures, preserving
  existing viewport event emission behavior.
- Wired the snap-to-grid toggle into drag-end commit only; live drag remains unsnapped.
- Added focused API helper coverage for node-position PATCH payloads in
  `mobile/canvas/__tests__/apiClient-test.ts`.

**Verification**:
- Focused M3.6 Jest: **3 suites / 19 tests passed**
  (`canvasControls-test`, `apiClient-test`, `skiaCanvas-test`).
- Full mobile Jest: **24 suites / 119 tests passed**.
- TypeScript: `npx.cmd tsc --noEmit -p ..\canvas\tsconfig.json` remains blocked by the existing
  `TS2688: Cannot find type definition file for 'jest'` config issue.
- Backend/Python tests not run; no backend files touched and no `.pyc` cleanup required.

**Residual risks carried into M4**:
- Existing React `act(...)`, hook-order, and SafeAreaView warnings still appear in mobile Jest
  output, but tests pass.
- The TS2688 Jest type-definition config issue remains non-blocking for this slice.
- M4 still owns real auth/curriculum/session entry wiring.

**Gate status**: M3.6 Canvas Controls locally complete; 119/119 mobile Jest green; M4 remains the
next canonical milestone.

**Next required actions**:
1. Begin M4 per `development-approach.md` §5 M4 (Supabase Auth + curriculum entry).
2. Fix or carry the canvas TypeScript `TS2688` Jest type-definition config issue before using
   `tsc --noEmit` as a blocking mobile gate.

---

### 2026-07-01 - Canvas TypeScript/Jest config blocker resolved before M4

**Milestone context**: M3.6 Canvas Controls is locally complete and M4 remains the next canonical
milestone. This entry resolves the pre-M4 TypeScript verification blocker recorded in the M3.6
entry above.

**Spec sections used**:
- `development-approach.md` §5 M3.6 (canvas controls gate) and §5 M4 (next milestone remains
  Curriculum entry + Supabase Auth).
- `docs/planning/sdd/phase-3-m3-6-canvas-controls-sdd.md` §7 and §9 (focused canvas-control Jest,
  full mobile Jest, worklog result before M4 resumes).

**Root cause**:
- `mobile/canvas/tsconfig.json` extends `mobile/app/tsconfig.json`, inheriting
  `compilerOptions.types = ["jest"]`.
- The canvas project sits outside `mobile/app`, so TypeScript could not discover
  `mobile/app/node_modules/@types/jest` from the canvas project root and stopped at
  `TS2688: Cannot find type definition file for 'jest'`.
- After the Jest type path was fixed, the compiler exposed strict source/test errors that had been
  hidden behind the resolver failure.

**Work completed**:
- Updated `mobile/canvas/tsconfig.json` with `typeRoots` pointing at
  `../app/node_modules/@types` and corrected the `react` path alias to resolve React types.
- Fixed strict TypeScript errors in canvas source/tests:
  - `apiClient-test.ts` now uses typed `globalThis.fetch` mocking.
  - `useLiveDragOverride-test.tsx` now uses typed Reanimated `SharedValue` helpers.
  - `CanvasEdges.tsx` now uses Skia's current `fontFamily` font-style key.
  - `layout.ts` guards d3-hierarchy coordinates before arithmetic.
- Raised the timeout for the Modal-heavy `PhraseSelectionReaderSheet` Jest file after full-suite
  verification showed it passes alone but can exceed Jest's default 5s timeout in the full in-band
  run.

**Verification**:
- TypeScript: `npx.cmd tsc --noEmit -p ..\canvas\tsconfig.json` from `mobile/app` - **passed**.
- Focused M3.6 Jest: `npm.cmd test -- --runInBand ../canvas/__tests__/canvasControls-test.ts
  ../canvas/__tests__/apiClient-test.ts __tests__/skiaCanvas-test.tsx` - **3 suites / 19 tests
  passed**.
- Full mobile Jest: `npm.cmd test -- --runInBand` - **24 suites / 119 tests passed**.
- Backend/Python tests not run; no backend files touched and no `.pyc` cleanup required.

**Residual risks carried into M4**:
- Existing React `act(...)`, hook-order, and SafeAreaView warnings still appear in mobile Jest
  output, but tests pass.
- The root workspace does not have a TypeScript install; use the mobile workspace compiler path
  (`mobile/app`) for the canvas TypeScript gate unless a root package is introduced.

**Gate status**: The canvas TypeScript `TS2688` blocker is resolved. M3.6 verification is now
TypeScript green plus 119/119 mobile Jest green; M4 remains the next canonical milestone.

---

### 2026-07-02 - M4 SDD drafted: B2C auth, curriculum entry, and fixture-backed Electricity flow

**Milestone context**: M3-C, M3.5, and M3.6 are locally complete. M4 is the next canonical
milestone per `development-approach.md` Section 5.

**Spec sections used**:
- `development-approach.md` Section 5 M4 and Section 7.1.
- `backend-architecture.md` Sections 5.3-5.5, 6, 7.1, 9, 10, and 11.
- `adr-log-02.md` ADR-0015.
- `student-api-spec.md` Sections 2-5.
- `core-operational-schema.md` Sections 2 and 6.
- `schema-traceability-and-validation.md` curriculum/session traceability rows.
- `master-prd.md` core product concept, MVP scope, primary user journey, and minimum viable
  chapter coverage.
- `mvp-features-specification.md` Feature Groups 1-4.
- `configuration-reference.md` Sections 9-10.
- `phase-3-m3c-infrastructure-remediation-sdd.md` M3-C transport/canvas seams.

**Work completed**:
- Created `docs/planning/sdd/phase-3-m4-curriculum-auth-sdd.md` as a draft for user review.
- Locked the M4 planning scope to B2C individual signup first, using Supabase email/password auth.
- Deferred phone/OTP auth to a later provider path.
- Deferred live LLM generation and replaced it with an explicit fixture-backed Electricity
  generation simulator behind the future generation-provider boundary.
- Set the launch curriculum path to Class 10 -> CBSE -> Science -> Electricity, with about 10
  fixture-backed Electricity nodes.
- Recorded that Supabase MCP currently exposes `ahntbtktjjmvfosgkmgn` (`Bookconnect_reactexpo`),
  while local Mindmap `.env` points at project ref `jbmqyxhrmcbdgardamrp`; migrations must be
  produced locally and manually applied by the owner to the correct Supabase database.

**Verification**:
- Documentation-only change; no backend or mobile tests run.
- SDD self-review checked for unfinished `TBD`/`TODO` markers, scope conflicts, and API parity
  coverage.

**Gate status**: M4 SDD is drafted, not approved or implemented. Next action is user review of the
SDD before writing an implementation plan.
