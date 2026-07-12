# Phase 3 M3 Canvas Maturation — Software Design Document (SDD)

**Document Version**: 1.3
**Status**: Active — §12 red-tests-first drill COMPLETE (17/17 green); pan/zoom Skia rendering +
gesture integration + mobile Sentry init complete; Stage 1 CI gate GREEN and Stage 2 physical-device
gate PASSED (2026-06-21). M3→M4 unlock condition met; Stage 3 (65-node smoke, non-blocking) remains.
**Phase / milestone**: Phase 3 — M3 Canvas maturation
**Live tracker**: `docs/planning/worklog-v6.md`

---

## 1. Increment Identity

| Field | Value |
|---|---|
| Increment name | Gesture-driven canvas: pan/zoom, deterministic layout, Skia edges |
| Phase / milestone | Phase 3 — M3 |
| Owner | (developer) |
| Status | Active — red tests green; rendering complete; Stage 1 + Stage 2 PASSED (M3→M4 unlocked); Stage 3 pending |

Goal: mature the mindmap canvas into a 60fps gesture-driven surface. Skia renders the board and
edges; Native Views render node content (ADR-0013). Node positions come from a deterministic
`d3-hierarchy` layout (ADR-0016) with drag-override persistence. Pan/zoom run on the UI thread via
Reanimated SharedValues while Zustand holds canonical state, written only on gesture end. The exit
gate is 60fps at 40+ nodes on a physical reference mid-range Android device.

## 2. Source-of-Truth References

- `development-approach.md` §5 M3: canvas maturation follows M2; gate is 60fps at 40+ nodes on the
  reference mid-range Android device; 65-node cap.
- `development-approach.md` §7.3: locked mobile stack (Expo / React Native, Skia, Reanimated,
  Gesture Handler); reference device rule — never simulator, never flagship.
- `development-approach.md` §8: small traceable increments, red tests first.
- `development-approach.md` §9: "Canvas performance/UX" risk rated High/High; this SDD's gate retires
  it.
- `adr-log.md` ADR-0013: Hybrid Architecture (Skia board/edges + Native node content); the
  Skia↔Native coordinate seam is the highest engineering risk.
- `adr-log-02.md` ADR-0016: deterministic `d3-hierarchy` tidy-tree over physics `d3-force`; cites
  Organic-First and the 60fps gate; drag-override rule.
- `session-path-data-contract.md` §6–§9: node visits and viewport context must be reconstructable
  from append-only events.
- `configuration-reference.md` §3–§4: `CANVAS_NODE_WARNING_COUNT=50`, `CANVAS_NODE_HARD_LIMIT=65`,
  `CANVAS_MIN_ZOOM=0.25`, `CANVAS_MAX_ZOOM=4.0`, `CANVAS_PERFORMANCE_GATE_NODES=40`,
  `VIEWPORT_EVENT_THROTTLE_MS=1000`, `NODE_POSITION_PERSIST_MODE=drag_end`.
- `00-canon.md`: Category Invisibility, Organic-First, Event Sourcing, red-tests-first.
- `backend/app/events/registry.py`: in-code event-type registry; new client event specs land here.

## 3. Scope

**In scope:**
- Gesture-driven pan/zoom canvas (pinch + pan composition, UI thread only).
- `d3-hierarchy` deterministic tree layout with drag-override persistence.
- Skia edge Bézier rendering (ai_path and manual_reference edges) with viewport culling.
- Native View node rendering within the hybrid boundary (ADR-0013).
- Manual reference links: draw-gesture UI → `edge_created` with `edge_kind: manual_reference`.
- Node-count limits: warning at 50, hard block at 65 (`configuration-reference.md` §3).
- Backend event registration: `node_visited` v1, `viewport_changed` v1.
- Mobile Sentry init: install `@sentry/react-native` and initialize in `mobile/app/App.tsx`
  using `SENTRY_DSN_MOBILE` (`configuration-reference.md` §10). Backend Sentry is already wired
  (`backend/app/observability/sentry.py`, `init_sentry()` in `main.py`); mobile side is pending.
- 3-stage performance gate procedure (§13).

**Out of scope:**
- In-node text selection (Reader bottom-sheet is primary MVP path; ADR-0013).
- Curriculum entry, Supabase Auth, teacher surfaces, checkpoints, podcast (M4–M8).
- Any `analytic_rm` read from `/v1/student`; no analytic fields ever surface to the canvas.

## 4. Coordinate System Contract

ADR-0013 names the Skia↔Native coordinate seam as the highest engineering risk: node positions are
shared state read by both the Skia edge renderer and the Native node mapper. A single shared module,
`mobile/canvas/coordinateSystem.ts`, is the SOLE location for seam math. No component may contain
inline coordinate calculations.

Three coordinate spaces: **board space** (layout output, transform-independent), **screen space**
(post pan/zoom pixels), and the **gesture frame** (raw touch coordinates).

Seam formulas:

```
boardToCanvas(boardX, boardY, t):  screenX = boardX * t.scale + t.translateX
                                   screenY = boardY * t.scale + t.translateY
canvasToBoard(screenX, screenY, t): boardX = (screenX - t.translateX) / t.scale
                                    boardY = (screenY - t.translateY) / t.scale
```

`CanvasTransform = { scale, translateX, translateY }`. `boardToCanvas` feeds the Skia edge renderer
and Native node mapper; `canvasToBoard` feeds tap-to-node hit testing. The pair is round-trip
inverse and CI-testable without a device (T1).

## 5. State Architecture

Two stores with a strict write-direction rule:

- **Canonical (Zustand, persisted):** node graph (`node_id`, `parent_node_id`, board `position`,
  `positionOverridden`), edge list (`edge_id`, `source_node_id`, `target_node_id`, `edge_kind`),
  and the last-committed `CanvasTransform`. This is the durable, replay-derived projection.
- **Ephemeral (Reanimated SharedValues, UI thread):** live `scale`, `translateX`, `translateY`, and
  the in-flight dragged-node board position. These change every frame and never block on JS.

Write-direction rule: **SharedValues are written every frame; Zustand is written once, on gesture
end.** No Zustand write may occur inside a gesture worklet (frame-budget protection, §7).

## 6. Layout Engine (d3-hierarchy — ADR-0016)

`mobile/canvas/layout.ts` computes board-space positions via a `d3-hierarchy` tidy-tree, a pure
function of tree shape. Properties:

- **Deterministic:** identical input shape → byte-identical coordinates (root offset to origin,
  coordinates rounded to 0.1). Enables snapshot testing without a device.
- **Structural trigger only:** layout runs on node add/remove/reparent — never per frame, never
  during a gesture.
- **Drag-override persistence:** a node with `positionOverridden === true` keeps its stored
  `position` when siblings are re-laid-out; only non-overridden nodes are recomputed.
- **Spacing:** `nodeSize([200, 160])` board units; single root required (`parent_node_id === null`);
  nodes whose parent is absent are omitted.

## 7. Dual-State Sync

Implemented in `mobile/canvas/gestureSync.ts` as plain gesture-lifecycle controllers so the
"write once, on end" invariant holds independently of the Reanimated runtime.

- **Viewport controller:** `onStart` snapshots base translate; `onUpdate(dx, dy)` mutates only the
  ephemeral transform (no Zustand write inside the worklet); `onEnd` performs the single
  `store.setViewport(...)` write.
- **Node-drag controller:** `onUpdate(boardDx, boardDy)` tracks the live board position only; `onEnd`
  performs the single `store.setNodePosition(nodeId, position, { positionOverridden: true })`,
  flagging the node so §6 re-layout skips it.
- `viewport_changed` emission is throttled by `VIEWPORT_EVENT_THROTTLE_MS=1000` and
  node-position persistence is `NODE_POSITION_PERSIST_MODE=drag_end` (`configuration-reference.md`).

## 8. Gesture Handling

Pinch + pan composed via `Gesture.Simultaneous` (react-native-gesture-handler), driven on the UI
thread with Reanimated worklets. Scale is clamped to `[CANVAS_MIN_ZOOM=0.25, CANVAS_MAX_ZOOM=4.0]`.
Tap routes through `canvasToBoard` (§4) for node hit-testing. All committed state changes flow
through the §7 controllers' `onEnd`; no JS-thread work runs per frame.

## 9. Skia Rendering & Viewport Culling

Skia draws the board and edges; Native Views overlay node content (ADR-0013). Edge geometry is a
cubic Bézier between `boardToCanvas`-mapped endpoints. Edge styling is keyed by `edge_kind`:
`ai_path` (solid) vs `manual_reference` (dashed/distinct).

Culling (`mobile/canvas/viewportCulling.ts`) runs before each render pass. Board-space viewport box:

```
[translateX, translateY, translateX + screenW/scale, translateY + screenH/scale]
```

- `computeBoardViewport(transform, screen)` returns the box.
- `cullEdges(edges, nodePositions, viewport)` keeps an edge if **at least one** endpoint is inside.
- `visibleNodeIds(nodePositions, viewport)` produces the `visible_node_ids` list for the
  `viewport_changed` payload (§10).

## 10. Event Registration

Two client-produced event specs added to `backend/app/events/registry.py` following the existing
`EventTypeSpec` constructor pattern. Both are `allowed_producers={"client"}` and carry only
student-safe fields (Category Invisibility — no dimension/score/coverage/confidence fields).

- **`node_visited` v1** — envelope adds `actor_user_id`, `student_id`, `session_id`, `node_id` to
  `COMMON_REQUIRED_FIELDS`; required payload: `node_id`, `session_id`, `visit_source`. Served by the
  partial index `events_node_id_idx (tenant_id, node_id, recorded_at) WHERE node_id IS NOT NULL`
  (migration 0006). Satisfies the "ordered path of node visits" data contract.
- **`viewport_changed` v1** — envelope adds `actor_user_id`, `student_id`, `session_id`; required
  payload: `session_id`, `scale`, `translate_x`, `translate_y`, `visible_node_ids`. Client-throttled
  by `VIEWPORT_EVENT_THROTTLE_MS`.

## 11. Node-Limit UI & Backend Guard

- **Mobile:** show a warning when active node count reaches `CANVAS_NODE_WARNING_COUNT=50`; block new
  branch creation in the UI at `CANVAS_NODE_HARD_LIMIT=65`.
- **Backend (authoritative):** `backend/app/canvas/limits.py` exposes `canvas_node_hard_limit()`,
  `canvas_node_warning_count()`, and `NodeLimitExceeded`. A shared replay helper
  (`backend/app/runtime/canvas_state.py::count_active_nodes`) computes the active count from events
  (reused by `canvas_deletion.py`). `offer_workflow.py` raises `NodeLimitExceeded` **before**
  appending `node_created` once the limit is reached; `api/student/offer_choices.py` catches it and
  returns **HTTP 409**. No `node_created` event is appended when blocked (Event Sourcing integrity).

## 12. Red Tests (canon §9 — required before production code in each section)

All tests must be red (failing) and committed before the code they guard is written.

**Count: 17 named test cases across T1–T6** (T1=2, T2=4, T3=2, T4=2, T5=6, T6=1). T7 is an
existing-suite regression gate, not a new named case.

### T1 — Coordinate seam (§4)
`mobile/app/__tests__/coordinateSystem-test.tsx`: `boardToCanvas` applies scale+translate; round-trip
`canvasToBoard(boardToCanvas(p)) === p`.

### T2 — Layout engine (§6)
`mobile/app/__tests__/layout-test.tsx`: root-only tree at origin; two-node parent/child y-offset;
determinism (identical shape → identical coords); drag-override position preserved across re-layout.

### T3 — Dual-state sync (§7)
`mobile/app/__tests__/gestureSync-test.tsx`: no Zustand write during `onUpdate`; exactly one write on
`onEnd` (viewport and node-drag controllers).

### T4 — Viewport culling (§9)
`mobile/app/__tests__/viewportCulling-test.tsx`: edge kept when one endpoint visible; edge dropped
when both outside; `computeBoardViewport` box formula; `visibleNodeIds` membership.

### T5 — Event registry (§10)
`tests/architecture/test_event_registry.py`: `node_visited` v1 and `viewport_changed` v1 are
registered with `client` producer, correct required envelope + payload fields, and are rejected when
produced by `worker` (Category-Invisibility / producer guard).

### T6 — Node limit (§11)
`test_hard_limit_blocks_node_creation_at_65`: backend endpoint returns 409 when session has
`CANVAS_NODE_HARD_LIMIT` nodes; no `node_created` event is appended.

### T7 — Regression
All existing `tests/` suite (pytest) must remain green after registry additions (T5 red tests
turn green). No existing event-type tests may be broken.

## 13. Three-Stage Performance Gate

The §5 M3 exit gate is verified in three escalating stages (`development-approach.md` §5, §7.3, §9):

- **Stage 1 — CI render-count (merge-blocking):** a Jest render-count harness asserts the canvas
  render path stays under the 16 ms frame budget for 40 nodes. Deterministic, runs without a device.
  **Status: PASSED** (GREEN in CI, 55/55).
- **Stage 2 — Physical device profiling (M3→M4 gate):** on a physical reference mid-range Android
  device (never simulator, never flagship), GPU/JS profiling must show **≥95% of frames at ≥60fps**
  while panning/zooming a 40-node board. **Status: PASSED (2026-06-21)** on the reference mid-range
  Android device; zoom/pan confirmed via a board-space debug grid, and the residual "node size
  constant on zoom" issue was resolved by adding `transform: [{ scale }]` to the `NodeChip` animated
  style (worklog-v6 2026-06-21 entry). With Stage 1 + Stage 2 both green, the **M3→M4 unlock
  condition is met**.
- **Stage 3 — 65-node smoke:** repeat Stage 2 at the `CANVAS_NODE_HARD_LIMIT=65` ceiling to confirm
  graceful degradation; if it fails, the ADR-0016 escalation path (revisit layout/culling strategy)
  is triggered. Stage 3 is documented, not merge-blocking for M3→M4. **Status: NOT YET RUN.**
  Profile against production draw content only — remove the temporary board-space debug grid from
  `SkiaCanvas.tsx` before the 65-node frame-budget measurement.

## 14. Definition of Done

- All 17 §12 red tests written first, then turned green; full mobile Jest + pytest suites green.
- Coordinate seam, layout, dual-state sync, viewport culling implemented behind the shared modules
  named above; no inline seam math anywhere else.
- `node_visited` v1 and `viewport_changed` v1 registered; producer/payload guards enforced.
- Node-limit backend 409 guard live; no `node_created` appended when blocked.
- Skia pan/zoom rendering integrated with Native node overlay; manual_reference edges drawable.
- Mobile Sentry initialized in `App.tsx` via `SENTRY_DSN_MOBILE`.
- Stage 1 CI gate green and Stage 2 device gate passed on the reference Android device.
- `.pyc` artifacts cleaned (0 remaining); worklog-v6 updated; every requirement traces to a §.

## 15. Runtime Implementation Findings (2026-06-21)

Recorded after first physical-device run. All four defects are in `mobile/canvas/SkiaCanvas.tsx`;
no spec section is changed by these findings. Required fix is a targeted rewrite of that file only
(red-tests-first per §12 / canon §9). Worklog entry 2026-06-21 contains the full analysis.

### Defect A — Non-reactive render (violates §5, §8)
Reading `SharedValue.value` during the JS render phase does not subscribe to UI-thread mutations.
`currentTransform` is computed once at mount; canvas and node positions never update during
gestures. **Fix:** drive the Skia layer from `useDerivedValue` / a reactive Skia `<Group
transform>` so the transform path executes entirely on the UI thread without JS re-renders; drive
the native node overlay with `useAnimatedStyle`.

### Defect B — Worklet calling non-worklet functions (hard crash on first gesture, violates §8)
`babel-preset-expo` SDK 56 auto-workletizes gesture-handler callbacks. Those callbacks invoke
`applyPinch`, `applyPan`, and `clampScale` from `gestureTransform.ts`, which carry no `'worklet'`
directive. Reanimated 4 throws a runtime exception when a UI-thread worklet calls a plain-JS
function. **Fix:** annotate the three pure-function reducers with `'worklet';` as their first
statement.

### Defect C — Node chips invisible (UX regression)
`backgroundColor: '#f0f0f8'` on a white canvas; no border, no label. **Fix:** apply a visible
background (e.g. `#e8e4f8`), a 1-px border, and a node label so chips are identifiable during
visual audit.

### Defect D — §7 controller bypassed (architecture violation)
`createViewportGestureController` in `gestureSync.ts` owns the write-once-on-end invariant (§7),
but `SkiaCanvas` reimplements the lifecycle inline, making the invariant untestable in isolation.
**Fix:** compose `createViewportGestureController` on gesture end instead of the inline `runOnJS`
callback.
