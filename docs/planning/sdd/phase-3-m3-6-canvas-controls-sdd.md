# Phase 3 M3.6 Canvas Controls — Software Design Document (SDD)

**Document Version**: 1.0
**Status**: Locally complete (2026-06-30)
**Phase / milestone**: Phase 3 — M3.6 (bounded pre-M4 canvas-control slice)
**Owner**: (developer)
**Live tracker**: `docs/planning/worklog-v8.md`

---

## 1. Increment Summary

| Item | Value |
|---|---|
| Increment name | Canvas controls: explicit zoom, fit, reset, and snap-to-grid |
| Phase / milestone | Phase 3 — M3.6 |
| Status | Locally complete |

**Goal**: add explicit learner-facing canvas controls before M4 begins, without changing curriculum
entry, authentication, backend product endpoints, analytic interpretation, or the existing
event-sourced persistence model.

---

## 2. Source-of-Truth References

- `development-approach.md` §5 M3 (pan/zoom/gestures, 65-node canvas limit, 60fps interaction)
  and §5 M4 (Curriculum entry + Supabase Auth remains next non-canvas milestone).
- `mvp-features-specification.md` Feature Group 3 (Mind Map Canvas), Feature 3.1 and Feature 3.5.
- `mobile-features-core-ui.md` §3.1 (Canvas navigation), §3.3 (Layout), §3.4 (Grid and Snap),
  §3.6 (Canvas constraints).
- `adr-log.md` ADR-0013 (Hybrid Mobile Canvas Architecture: Skia board/edges, native node views,
  gesture handling via Reanimated/Gesture Handler).
- `adr-log-02.md` ADR-0016 (layout invariance and UI-thread SharedValue boundary).
- `configuration-reference.md` §3 (`CANVAS_MIN_ZOOM`, `CANVAS_MAX_ZOOM`,
  `CANVAS_GRID_SIZE_PX`, `VIEWPORT_EVENT_THROTTLE_MS`).
- `phase-3-m3-canvas-sdd.md` §4, §5, §7, §9 (coordinate seam, dual-state rule,
  write-once-on-end, culling).
- `phase-3-m3c-infrastructure-remediation-sdd.md` §7 (node position persistence) and §8
  (viewport-changed event emission).

---

## 3. Scope

### In Scope

| Ref | Description |
|-----|-------------|
| C1 | Bottom canvas toolbar controls for zoom in and zoom out. |
| C2 | Fit-to-screen action that frames all live nodes within the viewport. |
| C3 | Reset-view action that returns to the default starting transform without moving nodes. |
| C4 | Visible zoom percentage readout derived from the canonical viewport scale. |
| C5 | Snap-to-grid toggle that rounds final drag-end board-space node positions to `CANVAS_GRID_SIZE_PX`. |

### Out of Scope

- M4 curriculum entry, Supabase Auth, dashboard routing, and real session selection.
- Backend schema changes, new endpoints, or new analytic projections.
- Visible grid rendering, custom grid size controls, alignment guides, minimap, auto-layout,
  multi-select, lasso selection, and undo/redo.
- Live snapping during drag; snapping applies only at drag-end commit.

---

## 4. Behavioral Requirements

1. Zoom controls must share the same bounded transform model as pinch zoom and clamp scale to
   `CANVAS_MIN_ZOOM` / `CANVAS_MAX_ZOOM`.
2. Fit-to-screen must compute a board-space bounding box from live nodes and update viewport
   transform without altering node positions.
3. Reset view must update only the viewport transform.
4. Toolbar transform changes must use the same transform-end path as gesture transforms so
   `viewport_changed` emission remains throttled and consistent.
5. Snap-to-grid must be optional and learner-facing as a simple toolbar toggle.
6. When snap-to-grid is enabled, only the final drag-end position is rounded before local state
   update and node-position persistence. Ephemeral drag SharedValues remain unsnapped during drag.
7. Snap-to-grid must not create a visible grid or any analytic/category-visible learner text.

---

## 5. Implementation Notes

- Keep viewport math in small helpers or hooks rather than adding bulk to `SkiaCanvas.tsx`.
- Preserve the ADR-0013 / ADR-0016 split: Reanimated SharedValues drive gesture-time state;
  canonical React/Zustand state updates only at commit boundaries.
- Use `CANVAS_GRID_SIZE_PX=15` from `configuration-reference.md` §3 for MVP.
- The toolbar should use compact icon controls and avoid expanding the existing node toolbar scope.

---

## 6. Test Plan

Red tests must precede production code.

| ID | Coverage |
|----|----------|
| T1 | Zoom-in and zoom-out clamp to configured min/max scale. |
| T2 | Fit-to-screen frames all live nodes and leaves node positions unchanged. |
| T3 | Reset view restores the default transform and leaves node positions unchanged. |
| T4 | Zoom readout reflects the current viewport scale. |
| T5 | Snap-to-grid disabled preserves the drag-end position. |
| T6 | Snap-to-grid enabled rounds the drag-end position to `CANVAS_GRID_SIZE_PX` before persistence. |
| T7 | Toolbar transform actions use the same viewport event emission path as gesture transform end. |

---

## 7. Definition of Done

- `docs/mvp-features-specification.md`, `docs/mobile-features-core-ui.md`, and this SDD align.
- Focused mobile Jest tests for canvas controls are green.
- Full mobile Jest is green, or any existing unrelated blocker is documented in the worklog.
- No backend/Python tests are required unless backend files are touched. If Python tests are run,
  generated `*.pyc` files must be deleted and the remaining `.pyc` count verified as 0.
- Worklog entry records implementation results and residual risks before M4 resumes.

---

## 8. Implementation Results

M3.6 is locally complete as a bounded pre-M4 canvas-control slice.

| Area | Result |
|------|--------|
| Toolbar controls | Added bottom canvas toolbar with zoom out, zoom in, fit-to-screen, reset-view, snap-to-grid toggle, and zoom percentage readout. |
| Viewport math | Added `canvasControls` helpers for clamped zoom, fit-to-screen, reset transform, zoom readout, and grid snapping. |
| Transform commit path | Toolbar actions update the same canonical transform end path used by gesture transforms, preserving existing viewport event emission. |
| Snap-to-grid | Drag-end node positions are rounded to `CANVAS_GRID_SIZE_PX` only when the learner-facing toggle is enabled. Live drag motion remains unsnapped. |
| Position persistence | Added focused API helper coverage for `PATCH /v1/student/sessions/{sessionId}/nodes/{nodeId}` payload shape. |
| File-size discipline | `SkiaCanvas.tsx` remains under the canon band after extracting `CanvasToolbar.tsx`. |

Touched implementation files:
- `mobile/canvas/canvasControls.ts`
- `mobile/canvas/CanvasToolbar.tsx`
- `mobile/canvas/SkiaCanvas.tsx`
- `mobile/canvas/apiClient.ts`
- `mobile/canvas/__tests__/canvasControls-test.ts`
- `mobile/canvas/__tests__/apiClient-test.ts`
- `mobile/app/__tests__/skiaCanvas-test.tsx`

## 9. Verification Results

Red-first coverage was added before production code.

| Check | Result |
|-------|--------|
| Focused canvas/control Jest | Passed: 3 suites / 19 tests. |
| Full mobile Jest | Passed: 24 suites / 119 tests. |
| TypeScript | Blocked by existing `TS2688: Cannot find type definition file for 'jest'` in the canvas tsconfig path. |
| Backend/Python | Not run; no backend files touched and no `.pyc` cleanup required. |

Known non-blocking test-output warnings remain in mobile Jest output: React `act(...)`, hook-order,
and SafeAreaView warnings already carried from the M3.5 frontend readiness residuals.

## 10. Residual Risks

- `tsc --noEmit -p ..\canvas\tsconfig.json` remains blocked by the pre-existing Jest
  type-definition resolution issue.
- M4 auth/curriculum/session selection remains out of scope; canvas controls still operate within
  the existing hydrated session surface.
- Visible grid rendering, minimap, custom grid sizing, alignment guides, multi-select, and
  undo/redo remain deliberately deferred.
