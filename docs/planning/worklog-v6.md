# Worklog v6 — Phase 3 M3 Canvas Maturation

AGENT ROTATION INSTRUCTION — READ FIRST: This is the live worklog after `worklog-v5.md` reached the
line-count threshold (346 lines as of 2026-06-21). Read `.augment/rules/00-canon.md`,
`docs/planning/development-approach.md` §5, and the active SDD before making changes.

## Legacy Context Summary

- Previous tracker: `docs/planning/worklog-v5.md`.
- **Phase 3 M2 Phrase Selection is CLOSED** (2026-06-20): the §5 M2 user/device gate was met on a
  physical Android device (a test user branched from a self-chosen phrase); the "questions aren't
  tappable" fatal risk (§9) is retired.
- **Phase 3 M1 is Locally Complete / Operationally Pending**: session resume, offer-set logging,
  edge `+` branching, deletion cascade, and event-only session-path reconstruction are green locally.
  Render backend/worker live verification and physical-device Expo smoke remain deferred operational
  gates — must not be claimed here.
- **M3 schema groundwork is complete** (2026-06-21, worklog-v5.md):
  - ADR-0016 authored (`docs/architecture/adr-log-02.md`): adopts deterministic `d3-hierarchy` over
    `d3-force` for M3 canvas layout. Cites §5 M3, §7.3, ADR-0013, and Organic-First invariant.
  - Schema doc reconciled (`docs/database/event-store-and-job-queue-schema.md` v1.1): phantom columns
    `edge_id`, `teacher_id`, `policy_name` removed; payload-stored-identifiers note added.
  - Migration 0006 applied to live DB (`backend/migrations/versions/0006_m3_schema_alignment.py`):
    `events_node_id_idx ON events (tenant_id, node_id, recorded_at) WHERE node_id IS NOT NULL`.
    Confirmed live via `pg_indexes`. Schema audit closed.
- **Active milestone**: Phase 3 — M3 Canvas maturation.
- **Active SDD**: `docs/planning/sdd/phase-3-m3-canvas-sdd.md` (authored 2026-06-21).
- Canon §9 red-tests-first rule: no M3 production code may be written before the SDD's §12 test
  names exist and fail.

---

### 2026-06-21 — M3 SDD authored; worklog rotated; canon updated; escalation thresholds verified

**Phase / milestone**: Phase 3 — M3 Canvas maturation

**Spec sections used**:
- `development-approach.md` §5 M3 (gate: 60fps at 40+ nodes on reference mid-range Android device),
  §7.3 (locked mobile stack; reference device rule), §9 (risk: Canvas performance/UX — High/High).
- `configuration-reference.md` §3 (`CANVAS_NODE_WARNING_COUNT=50`, `CANVAS_NODE_HARD_LIMIT=65`,
  `CANVAS_PERFORMANCE_GATE_NODES=40`, `CANVAS_MIN_ZOOM=0.25`, `CANVAS_MAX_ZOOM=4.0`,
  `VIEWPORT_EVENT_THROTTLE_MS=1000`).
- `adr-log.md` ADR-0013 (Hybrid Architecture; Skia↔Native seam as highest engineering risk).
- `adr-log-02.md` ADR-0016 (d3-hierarchy; deterministic layout; drag-override rule).
- `00-canon.md` (Organic-First; Category Invisibility; red-tests-first).

**Work completed**:
- **Escalation thresholds verified** against SoT (`development-approach.md` §5, §7.3, §9 and
  `configuration-reference.md` §3 only — `docs/architecture-feature-mapping.md` excluded per prior
  instruction). Confirmed:
  - Performance gate: 60fps at `CANVAS_PERFORMANCE_GATE_NODES=40` nodes on physical reference device.
  - Hard node limit: `CANVAS_NODE_HARD_LIMIT=65`; warning at `CANVAS_NODE_WARNING_COUNT=50`.
  - "Never simulator or flagship" is explicit in §7.3 Reference device rule.
- **Worklog rotated** to `worklog-v6.md` (`worklog-v5.md` was at 346 lines).
- **M3 Canvas SDD authored** (`docs/planning/sdd/phase-3-m3-canvas-sdd.md`, v1.0, 353 lines):
  - §4 Coordinate System Contract: `boardToCanvas(x, y, t)` / `canvasToBoard` seam formula; single
    shared module rule; resolves ADR-0013 highest engineering risk.
  - §5–§6 State Architecture + Layout Engine: Zustand schema, Reanimated SharedValue catalogue,
    d3-hierarchy trigger rules (structural change only, not per-frame), drag-override persistence.
  - §7–§8 Dual-State Sync + Gesture Handling: no Zustand writes during gesture worklets; all writes
    deferred to `onEnd`; pinch+pan `Gesture.Simultaneous`; scale clamped to [0.25, 4.0].
  - §9 Skia Rendering: edge Bézier spec, viewport culling, ai_path vs manual_reference style.
  - §10 Event Registration: `node_visited` v1 and `viewport_changed` v1 registry specs (envelope
    + payload fields; `EventTypeSpec` constructor pattern; Category Invisibility enforced).
  - §11 Node Limit UI: warning at 50, block at 65; backend 409 before `node_created` append.
  - §12 Red Tests: 17 named test cases across T1–T6 (T1=2, T2=4, T3=2, T4=2, T5=6, T6=1); T7 is
    an existing-suite regression gate. All required before production code.
  - §13 3-Stage Performance Gate: Stage 1 (CI <16ms), Stage 2 (device ≥95% frames ≥60fps at 40),
    Stage 3 (65-node smoke); M3→M4 requires Stage 1 + Stage 2 passing.
  - §14 Definition of Done.
- **Canon updated** (`00-canon.md`): ACTIVE SDD now points to phase-3-m3-canvas-sdd.md; LIVE
  TRACKER now points to worklog-v6.md.

**Validation run**:
- No Python/JS source files were modified; no tests needed for doc-only changes.
- Diagnostics on all edited files: no issues reported.

**Gate status**:
- §5 M2 user/device gate remains **CLOSED**.
- M3 SDD is active. Canon §9 red-tests-first rule blocks all M3 production code until §12 tests
  are written and failing. Next step: write the §12 red tests, then implement section by section.

---

### 2026-06-21 — Session-rotation verification (Sentry, DB, test-count)

**Phase / milestone**: Phase 3 — M3 Canvas maturation

**Verification performed before rotating to a fresh session**:

- **Sentry audit**:
  - Backend **verified**: `init_sentry()` (`backend/app/observability/sentry.py`) is wired into
    `create_app()` (`backend/app/main.py`), with `sentry_smoke.py` CLI and regression test
    `tests/integration/test_observability_sentry.py`.
  - Mobile **pending (M3 task)**: `mobile/app/App.tsx` renders only `M2PhraseSmokeScreen`; no
    `@sentry/react-native` import and the package is absent from `mobile/app/package.json`.
    `SENTRY_DSN_MOBILE` config slot exists (`configuration-reference.md` §10) but is unused.
    Action for M3: `npx expo install @sentry/react-native` and initialize in `App.tsx`.
- **Database verification (via Supabase MCP `execute_sql`)**:
  - `events_node_id_idx` is **LIVE**: `CREATE INDEX events_node_id_idx ON public.events USING
    btree (tenant_id, node_id, recorded_at) WHERE (node_id IS NOT NULL)`.
  - Live `events` columns contain **no** `edge_id`, `teacher_id`, or `policy_name` (lineage columns
    `policy_version`, `prompt_version`, `model_id`, `projection_version` are distinct and expected).
    Doc reconciliation confirmed; **no further schema changes required**.
- **Test-count correction**: §12 of the M3 SDD has **17** named test cases across T1–T6
  (T1=2, T2=4, T3=2, T4=2, T5=6, T6=1), not 14. T7 is an existing-suite regression gate. SDD §12
  and the prior worklog entry corrected to 17.

**Tooling guidance for the next agent (use MCP wherever needed)**:
- **Supabase MCP** (`execute_sql`, `list_tables`, `apply_migration`) for any DB state check,
  index verification, or migration — never assume schema; verify against the live DB.
- **Sentry MCP** for triaging production errors once mobile/backend Sentry is emitting: query
  issues/events and use Seer for root-cause + fix suggestions before manual debugging.

---

### 2026-06-21 — M3 §12 Red-Tests-First drill COMPLETE (T1–T7 all green)

**Phase / milestone**: Phase 3 — M3 Canvas maturation

**Spec sections used**:
- `phase-3-m3-canvas-sdd.md` §4 (coordinate seam), §6 (layout), §7 (dual-state sync),
  §9 (viewport culling), §10 (event registry), §11 (node-limit 409), §12 (17 red tests), §14 (DoD).
- `adr-log-02.md` ADR-0016 (d3-hierarchy deterministic layout).
- `configuration-reference.md` §3 (`CANVAS_NODE_HARD_LIMIT=65`, `CANVAS_NODE_WARNING_COUNT=50`).
- `00-canon.md` (red-tests-first, Organic-First, Category Invisibility, DRY shared helpers).

**Work completed**:

- **T1 — Coordinate seam (§4)**: 2 tests in `mobile/app/__tests__/coordinateSystem-test.tsx`;
  production: `mobile/canvas/coordinateSystem.ts` (`boardToCanvas` / `canvasToBoard`). ✅

- **T3 — Dual-state sync (§7)**: 2 tests in `mobile/app/__tests__/gestureSync-test.tsx`;
  production: `mobile/canvas/gestureSync.ts`. ✅

- **T4 — Viewport culling (§9)**: 4 tests in `mobile/app/__tests__/viewportCulling-test.tsx`;
  production: `mobile/canvas/viewportCulling.ts`. ✅

- **T5 — Event registry (§10)**: 6 pytest tests added to
  `tests/architecture/test_event_registry.py`; production: `node_visited` v1 and
  `viewport_changed` v1 `EventTypeSpec` entries added to `backend/app/events/registry.py`. ✅

- **T6 — Node-limit 409 (§11)**:
  - 1 pytest test `test_hard_limit_blocks_node_creation_at_65` added to
    `tests/integration/test_edge_branching.py`.
  - Production: `backend/app/canvas/__init__.py` + `backend/app/canvas/limits.py`
    (`canvas_node_hard_limit()`, `canvas_node_warning_count()`, `NodeLimitExceeded`);
    `backend/app/runtime/canvas_state.py` (shared replay helper, `count_active_nodes`);
    `backend/app/runtime/canvas_deletion.py` refactored to use shared helper;
    `backend/app/runtime/offer_workflow.py` guard: raises `NodeLimitExceeded` before appending
    `node_created` when limit reached; `backend/app/api/student/offer_choices.py` catches
    `NodeLimitExceeded` → HTTP 409. ✅

- **T2 — Layout engine (§6)**: 4 tests in `mobile/app/__tests__/layout-test.tsx`
  (root-only, two-node y-offset, determinism, drag-override preservation);
  production: `mobile/canvas/layout.ts` using `d3-hierarchy` tidy-tree;
  `d3-hierarchy@^3` + `@types/d3-hierarchy` installed via npm;
  `mobile/app/package.json` `transformIgnorePatterns` extended to transform `d3-hierarchy`
  ESM under Jest. ✅

- **T7 — Regression + cleanup**:
  - Mobile Jest: **29/29 passed**, 6 suites.
  - Python pytest: **100/100 passed**.
  - `.pyc` cleanup: **0 remaining**.

**Files created**:
- `mobile/canvas/coordinateSystem.ts`, `mobile/canvas/gestureSync.ts`,
  `mobile/canvas/viewportCulling.ts`, `mobile/canvas/layout.ts`
- `mobile/app/__tests__/coordinateSystem-test.tsx`, `gestureSync-test.tsx`,
  `viewportCulling-test.tsx`, `layout-test.tsx`
- `backend/app/canvas/__init__.py`, `backend/app/canvas/limits.py`
- `backend/app/runtime/canvas_state.py`

**Files modified**:
- `backend/app/events/registry.py` (two new `EventTypeSpec` entries)
- `backend/app/runtime/canvas_deletion.py` (use shared `canvas_state` helper)
- `backend/app/runtime/offer_workflow.py` (node-limit guard)
- `backend/app/api/student/offer_choices.py` (catch `NodeLimitExceeded` → 409)
- `tests/architecture/test_event_registry.py` (6 new T5 tests)
- `tests/integration/test_edge_branching.py` (T6 test + `_seed_node_created_events` helper)
- `mobile/app/package.json` (added `d3-hierarchy`; updated `transformIgnorePatterns`)

**Gate status**:
- All 17 SDD §12 red tests → green. ✅
- M3 §12 red-tests-first drill is **COMPLETE**.
- Remaining M3 work (mobile Sentry init, pan/zoom Skia rendering, performance gate) is
  not yet started and requires explicit task assignment in the next session.

---

### NEW SESSION START — Phase 3 M3 Canvas (handoff prompt)

**Read first (in order):**
1. `.augment/rules/00-canon.md` — invariants, active-milestone status, red-tests-first rule.
2. `docs/planning/worklog-v6.md` — this live tracker (M2 CLOSED; rotated from v5 at 346 lines).
3. `docs/planning/sdd/phase-3-m3-canvas-sdd.md` — active SDD (the design contract for all M3 work).
4. `docs/configuration-reference.md` — canvas constants (node limits, zoom, throttle, Sentry DSNs).
5. `backend/app/events/registry.py` — event-type registry (target for `node_visited` /
   `viewport_changed` v1 specs per SDD §10).

**Immediate objective:** implement the **17 red tests** specified in §12 of the M3 SDD.

**Red-Tests-First drill (canon §9 — non-negotiable):** for each SDD section, write and **commit the
failing tests first**, then write production code until they pass. Example order:
1. §4 Coordinate System → T1 (2 tests) → then `mobile/canvas/coordinateSystem.ts`.
2. §6 Layout engine → T2 (4 tests) → then the `d3-hierarchy` hook.
3. §7 Dual-state sync → T3 (2 tests).
4. §9 Viewport culling → T4 (2 tests).
5. §10 Event registry → T5 (6 tests) → then `registry.py` specs.
6. §11 Node limit → T6 (1 test) → then backend 409 guard.
Do not write production code for a section before its tests exist and are red.

**State carried in:**
- Phase 3 **M2 is CLOSED** (2026-06-20, physical-device gate met). Do not reopen.
- Phase 3 **M1 Locally Complete / Operationally Pending** (Render + device smoke deferred).
- Worklog rotated to **v6**; `events_node_id_idx` live; schema reconciled.
- Mobile Sentry init (`@sentry/react-native` in `App.tsx`) is a pending M3 task.

**MCP usage:** use **Supabase MCP** for all DB/schema/migration verification and **Sentry MCP**
for error triage; verify against live systems rather than assuming.

---

### 2026-06-21 — M3 §14 DoD tasks 1–5 complete (Sentry, gesture, edges, manual-ref, Stage-1 CI gate)

**Phase / milestone**: Phase 3 — M3 Canvas maturation

**Spec sections used**:
- `phase-3-m3-canvas-sdd.md` §3 (Sentry init, manual-reference edge payload), §8 (gesture
  zoom-clamp + focal-preserving pinch), §9 (Skia edge Bézier + viewport-culled edge count),
  §13 (3-Stage performance gate; Stage 1 deterministic CI harness), §14 (Definition of Done).
- `configuration-reference.md` §3 (`CANVAS_MIN_ZOOM=0.25`, `CANVAS_MAX_ZOOM=4.0`,
  `CANVAS_PERFORMANCE_GATE_NODES=40`).
- `backend/app/events/registry.py` — `edge_created` v1 `required_payload_fields` contract.
- `student-api-spec.md` §7 — manual reference links are not path progression.

**Work completed**:

- **Task 1 — Mobile Sentry init (§3, §14)**: red test (`sentry-test.tsx`, 3 cases) → green.
  - `mobile/app/observability/sentry.ts`: reads `EXPO_PUBLIC_SENTRY_DSN_MOBILE` from env,
    calls `Sentry.init({ dsn, enableAutoSessionTracking: true })`; no-op when DSN absent.
  - `mobile/app/App.tsx`: imports and invokes `initSentry()` at load.
  - `@sentry/react-native` installed via `npx expo install`; plugin registered in `app.json`.
  - Commit: `e04f829`

- **Task 2 — Gesture zoom-clamp + focal-preserving pinch (§8, §14)**: red test
  (`gestureTransform-test.tsx`, 6 cases) → green.
  - `mobile/canvas/gestureTransform.ts`: pure-function reducers `clampScale`, `applyPan`,
    `applyPinch`; scale clamped to `[CANVAS_MIN_ZOOM, CANVAS_MAX_ZOOM]`; pinch preserves
    focal point via `boardToCanvas`-based offset formula.
  - Commit: `5c20466`

- **Task 3 — Skia edge Bézier rendering + edge-kind styling (§9, §14)**: red test
  (`edgeRendering-test.tsx`, 5 cases) → green.
  - `mobile/canvas/edgeRendering.ts`: deterministic `cubicBezierPath(p0, p1) → string`
    (30 % control-point offset; byte-identical for same inputs); `edgeStyleForKind` maps
    `ai_path` → solid (strokeWidth 2, no dash) and `manual_reference` → dashed (strokeWidth
    1.5, dash [6,4]).
  - Commit: `5deca9b`

- **Task 4 — Manual-reference link event payload builder (§3, §9, §14)**: red test
  (`edgeEvents-test.tsx`, 4 cases) → green.
  - `mobile/canvas/edgeEvents.ts`: `MANUAL_REFERENCE_CREATED_BY = "manual_link"`;
    `buildManualReferenceEdgePayload` emits all 6 `edge_created` v1 required_payload_fields
    with `edge_kind` pinned to `manual_reference` (student-api-spec.md §7: learner links are
    not path progression).
  - Commit: `b682931`

- **Task 5 — Stage 1 CI render-count gate (§13, §14)**: red test (`renderBudget-test.tsx`,
  2 cases) → green.
  - `mobile/canvas/renderBudget.ts`: `CANVAS_PERFORMANCE_GATE_NODES = 40`;
    `countRenderPrimitives(positions, edges, transform, screen)` composes the §9 culling
    helpers (`computeBoardViewport`, `visibleNodeIds`, `cullEdges`) to count visible nodes +
    culled-visible edges — the real per-frame draw path.
  - Invariants verified: (1) 40-node board render path bounded by node budget; (2) viewport
    culling collapses render path to visible content when zoomed.
  - Merge-blocking Stage 1 gate is now **GREEN** in CI. Stage 2 (physical-device 60 fps) and
    Stage 3 (65-node smoke) remain deferred operational gates.
  - Commit: `500ee44`

**Full regression run**:
- Mobile Jest: **11 suites, 47 tests, 0 failures** ✅
- Python pytest: **100/100 passed** ✅
- `.pyc` cleanup: **0 remaining** ✅

**Files created**:
- `mobile/app/observability/sentry.ts`
- `mobile/canvas/gestureTransform.ts`
- `mobile/canvas/edgeRendering.ts`
- `mobile/canvas/edgeEvents.ts`
- `mobile/canvas/renderBudget.ts`
- `mobile/app/__tests__/sentry-test.tsx`, `gestureTransform-test.tsx`,
  `edgeRendering-test.tsx`, `edgeEvents-test.tsx`, `renderBudget-test.tsx`

**Files modified**:
- `mobile/app/App.tsx` (calls `initSentry()`)
- `mobile/app/app.json` (`@sentry/react-native` plugin entry)
- `mobile/app/package.json` (`@sentry/react-native` dependency)

**Gate status**:
- M3 §14 DoD tasks 1–5: **COMPLETE** ✅
- Stage 1 CI render-count gate: **GREEN** (merge-blocking) ✅
- Stage 2 physical-device 60fps gate: **DEFERRED** (requires reference mid-range Android)
- Stage 3 65-node smoke: **DEFERRED** (requires physical device)
- M3 → M4 unlock gate: awaiting Stage 2 physical-device verification.
