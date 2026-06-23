# Phase 3 M3-B Supplemental SDD: Canvas Feature Parity

Status: **LOCALLY COMPLETE** (authored 2026-06-22; F4 Manual Reference UI removed from
scope per owner direction; all TB-series tests green; 82/82 mobile Jest suite green as of
2026-06-22). Operational gates (Stage 2 device re-run at 40+ nodes, Stage 3 65-node smoke)
are deferred — non-blocking unless explicitly requested. Supplements
`docs/planning/sdd/phase-3-m3-canvas-sdd.md`; does not replace it. The M3 base scope
(pan/zoom, deterministic layout, edge Bézier rendering, edge/event registration, node
limits, Sentry) remains the closing gate for M3. This document adds the canvas frontend
features required for parity with `docs/mvp-features-specification.md` that are NOT
covered by the M3 base §3 scope.

Canon: red tests before production code (`00-canon.md`; M3 SDD §12). Every feature below
traces to a source-of-truth §. Conflicting MVP items are isolated in §10 and are NOT in
scope until an ADR resolves them.

## 1. Goal

Reconcile `mobile/` with `mvp-features-specification.md` Feature Group 3 (Mind Map Canvas)
and Feature 4.4 (Question Discovery), closing the discrepancies recorded in the M3 audit:
edge labels (Disc. B), edge-`+` UI (FG4.4), node selection/toolbar (FG3.3), and
native-view culling (M3 SDD §9 perf gap). Exit posture is
unchanged from M3: 60fps at 40+ nodes on the reference mid-range Android device.

## 2. Source-of-Truth References

- `mvp-features-specification.md`: §3.3 (Node Selection), §3.4 (Node Connections), §4.4
  lines 269–285 (Question Discovery: 44×44pt edge-`+`, 3–6 cards, edge labeled with
  question text), §4.3 line 260 (delete-with-cascade), Known Scope Notes line 516 (image
  nodes — see §10).
- `session-path-data-contract.md`: §3 (branching only via phrase/edge-`+`; no node-body
  editing), §10 (deletion cascade — F3 delete).
- `adr-log-02.md`: ADR-0013 (Skia edges + Native node views), ADR-0016 (d3-hierarchy
  deterministic layout, structural-trigger re-layout, drag-override).
- `phase-3-m3-canvas-sdd.md`: §4 (coordinate seam), §5 (dual-state), §6 (layout), §9
  (Skia + culling, `visibleNodeIds`), §11 (node limits).
- `configuration-reference.md` §3: `CANVAS_*` constants.
- `backend/app/events/registry.py`: `node_created` v1 (AI-provenance payload — see §10),
  `node_deleted` v1 (F3 delete-cascade).
- `backend/app/api/student/offer_sets.py`: `POST /v1/student/offer-sets/edge`,
  `POST /v1/student/offer-sets/phrase`; `offer_choices.py`:
  `POST /v1/student/offer-sets/{offer_set_id}/choices`.

## 3. Scope

**In scope (this SDD):**
- F1 AI-path edge labels (question text along the Bézier).
- F2 Question Discovery edge-`+` buttons + offer-set popup.
- F3 Node selection state + node-level action toolbar (includes delete trigger).
- F5 Native `NodeChip` viewport culling via `visibleNodeIds`.
- F6 Node-limit warning (50) / block (65) mobile UI (M3 SDD §11 mobile half).

**Out of scope:**
- Manual reference link UI (former F4; MVP §3.4). Removed from M3-B on owner direction
  (2026-06-22). NOTE: manual reference links are named M3 content in development-approach
  §5; the `edge_created`/`edge_deleted` plumbing + `buildManualReferenceEdgePayload` already
  exist from base M3 — only the draw-gesture UI is deferred, to be re-homed (base M3 SDD or a
  later track) by owner decision. No `POST /v1/student/edges` route is in M3-B scope.
- Curriculum, dashboard, checkpoints, PYQ, podcast (M4–M8; MVP FG1,2,5,6,7).
- Node Creation FAB / manual-text / image-node creation — see §10 (ADR-gated).
- Any `analytic_rm` read from `/v1/student`; no analytic fields surface to the canvas.

## 4. Architectural Constraints

**ADR-0013 — Hybrid placement (authoritative for every new surface):**

| Surface | Layer | Rationale |
|---|---|---|
| Edge Bézier + label | Skia | Label belongs to the edge geometry |
| NodeChip content | Native View | Text measure / a11y |
| Edge-`+` button | Native View | 44×44pt touch target needs RNGH |
| Node toolbar | Native View | Interactive chrome |

All seam math calls `boardToCanvas` / `canvasToBoard` only (§4). No inline coordinate
math in any new component.

**ADR-0016 — Layout invariance:** d3-hierarchy uses `parent_node_id` (ai_path) only.
Selection state MUST NOT trigger or alter layout. Re-layout stays structural-trigger-only
(node add/remove/reparent); drag-override (`positionOverridden`) is preserved.

## 5. Feature Designs

### 5.1 F1 — AI Path Edge Labels (Disc. B; MVP §4.4 line 281)

Pure placement in `mobile/canvas/edgeRendering.ts` (CI-testable, no device):

- `edgeLabelLayout(p0, p1, text, opts) → { position: Point; displayText: string }`
  - `position`: cubic Bézier point at `t=0.5` using the same control points as
    `cubicBezierPath` (control points on the midline) so the label sits on the curve.
  - `displayText`: truncate to `opts.maxChars` (default 28) with a trailing ellipsis,
    single line — the 2-line rule in MVP applies to popup cards, not edge labels.
- Only `ai_path` edges carry labels (`edge_kind === 'ai_path'`); `manual_reference` edges
  render no label.
- Rendering: `SkiaCanvas.tsx` draws the label with Skia text inside the same `<Group>` as
  the edge path. Label text is the edge's persisted `label` field (the selected
  question/option text recorded at branch creation).
- Culling: a label is drawn iff its edge survives `cullEdges` (§9); no separate pass.

### 5.2 F2 — Question Discovery Edge-`+` UI (MVP §4.4 lines 269–285)

- Native overlay buttons on the node's left and right vertical-edge midpoints.
- Tracking: Buttons read `scaleShared`, `translateXShared`, and `translateYShared` directly on the UI thread via `useAnimatedStyle`. This allows them to stay pinned to nodes during active panning/zooming, avoiding drift.
- Sizing: The touch target is fixed at a compliant 44×44pt (MVP line 277). The visible glyph is reduced to 24×24pt (centered inside the touch area) to read proportionally against the node edge without violating the accessibility invariant.
- Press → `POST /v1/student/offer-sets/edge` (`EdgeOfferSetRequest`: session_id,
  source_node_id, thread_context_id, launch side) → popup with 3–6 tappable question cards
  (max 2 lines + ellipsis, MVP line 279).
- Card tap → `POST /offer-sets/{offer_set_id}/choices` outcome=`selected`; dismiss →
  outcome=`dismissed`. The backend appends the offer-set + choice events and creates the
  child node + ai_path edge (the edge `label` feeds F1). Identical contract to the phrase
  flow — the client never fires `phrase_selected` / `offer_set_*` itself.
- Buttons are culled with their parent node (§5.4).

### 5.3 F3 — Node Selection & Toolbar (MVP §3.3)

- Hit-testing: new pure helper `hitTestNode(boardPoint, nodes, nodeSize) → nodeId | null`
  (`mobile/canvas/hitTest.ts`): returns the node whose board-space AABB
  (`nodeSize=[200,160]`, centered on stored position) contains the tapped board point;
  `canvasToBoard` converts the tap first. Topmost-on-overlap by insertion order.
- Selection state is canonical (Zustand): `selectedNodeId` (§6). A tap commits exactly one
  `selectNode(nodeId)` write (§7 write-once rule); tapping empty space clears it.
- Toolbar: Native View anchored above the selected node (position via `boardToCanvas`).
  Actions are category-neutral and exclude body editing (data-contract §3):
  - **Explore** → opens the edge-`+` offer-set flow (F2).
  - **Delete** → confirmation →
    `DELETE /v1/student/sessions/{session_id}/nodes/{node_id}?confirmed=true` (existing
    cascade endpoint; data-contract §10). No reattach — that remains ADR-blocked.
- Toolbar + selection are culled with the node (§5.4).

### 5.4 F5 — Native View Culling (M3 SDD §9 perf gap)

- Compute
  `visible = new Set(visibleNodeIds(positions, computeBoardViewport(transform, screen)))`
  in a `useMemo` keyed on the COMMITTED `transform` prop + node positions — never per
  gesture frame (§7 write-on-end; ADR-0016 structural trigger).
- Render `nodes.filter(n => visible.has(n.node_id))` instead of `nodes.map(...)`.
- Edge-`+` buttons (F2) and the toolbar (F3) render only for visible nodes.
- **Critical-path validation:** F5 is the perf lever for the 40+ node 60fps gate
  (`CANVAS_PERFORMANCE_GATE_NODES=40`), not a cosmetic optimization. ADR-0013 places node
  content on Native Views, so unbounded `NodeChip` mounts — not Skia draws — are the
  dominant cost as the board grows; culling bounds mounted Views to the viewport. M3 SDD §9
  names culling the §9 perf gap, and the M3 Stage 2 device gate PASSED at 40 nodes
  (2026-06-21) on the reference mid-range Android device. Without view culling that margin
  regresses as node count climbs toward the Stage 3 65-node ceiling, so F5 is a required
  M3-B deliverable that holds the established Stage 2/3 gate as the canvas scales.

### 5.5 F6 — Node-Limit Mobile UI (M3 SDD §11 mobile half)

- Active node count ≥ `CANVAS_NODE_WARNING_COUNT=50` → non-blocking warning banner.
- Active node count ≥ `CANVAS_NODE_HARD_LIMIT=65` → disable F2 creation affordances
  client-side; the backend 409 guard (`offer_workflow` / `offer_choices`) remains the
  authority (M3 SDD §11). Counts read from the canonical store node list.

## 6. State Architecture Extensions (Zustand canonical store, M3 SDD §5)

Add to the persisted canonical store (write-direction rule unchanged — writes on tap
commit / gesture end, never inside a worklet):

- `selectedNodeId: string | null`; actions `selectNode(id)`, `clearSelection()`.
- ai_path edges gain a persisted `label: string` (question/option text) for F1.

The canonical store lives at `mobile/canvas/store.ts` (created with this SDD — no Zustand
store exists in `mobile/` today). `selectNode` performs exactly one `set(...)` per call
(§7 write-once rule).

Ephemeral Reanimated SharedValues are unchanged. No analytic fields are added (Category
Invisibility).

## 7. Module Map

New / modified (all kept <300 lines; split if exceeded):

- `mobile/canvas/edgeRendering.ts` — add `edgeLabelLayout` (F1).
- `mobile/canvas/hitTest.ts` (new) — `hitTestNode` (F3).
- `mobile/canvas/store.ts` (new) — canonical Zustand store; selection state (§6).
- `mobile/canvas/SkiaCanvas.tsx` — Skia label draw (F1); native edge-`+` (F2), toolbar
  (F3); node culling + button/toolbar gating (F5); limit UI (F6).

## 8. Red Tests (canon §9 — written and committed RED before any production code)

Naming: TB-series, mirroring M3 §12. All device-independent (Skia / Reanimated / RNGH
mocked).

### TB1 — Edge labels (F1) · `mobile/app/__tests__/edgeLabel-test.tsx`
- `test_label_anchored_at_bezier_midpoint` — `edgeLabelLayout` position == cubic point at t=0.5.
- `test_label_truncated_with_ellipsis` — text over maxChars ends with `…` and length ≤ max.
- `test_only_ai_path_edges_labeled` — manual_reference yields no label.
- `test_label_dropped_when_edge_culled` — label absent when its edge fails `cullEdges`.

### TB2 — Edge-`+` UI (F2) · `mobile/app/__tests__/edgePlusButton-test.tsx`
- `test_plus_buttons_on_left_and_right_edges` — positions == `boardToCanvas(x±100, …)`.
- `test_plus_touch_target_is_44pt` — rendered hit area ≥ 44×44.
- `test_plus_press_posts_edge_offer_set` — press → fetch `POST /offer-sets/edge`.

### TB3 — Node selection (F3) · `mobile/app/__tests__/nodeSelection-test.tsx`
- `test_hit_test_returns_node_under_point` / `test_hit_test_null_outside`.
- `test_tap_writes_selected_node_once` — exactly one `selectNode` store write.
- `test_toolbar_has_no_body_edit_action` — no edit-content control (data-contract §3 guard).

### TB4 — Toolbar actions (F3) · same file
- `test_delete_calls_endpoint_with_confirmed_true`.

### TB6 — Native culling (F5) · extend `mobile/app/__tests__/skiaCanvas-test.tsx`
- `test_culling_removes_offscreen_node_chips`.
- `test_offscreen_plus_and_toolbar_culled_with_node`.

### TB7 — Node-limit UI (F6) · `mobile/app/__tests__/nodeLimitUi-test.tsx`
- `test_warning_banner_at_50` / `test_creation_disabled_at_65`.

### TB-REG — Regression
- Full mobile Jest + pytest suites remain green.

## 9. Definition of Done

- ✅ All TB-series tests written RED first, then green; full 82/82 mobile Jest suite green
  (2026-06-22). No pytest regressions (Python not modified in M3-B).
- ✅ F1–F5 implemented behind the named modules (see §7 module map); no inline seam math;
  ADR-0013 placement table honored; ADR-0016 layout invariance preserved.
- ✅ F6 node-limit UI wired; `nodeLimitState.creationBlocked` disables `EdgePlusButtons`.
- ✅ Node culling (F5) + button/toolbar gating active in `SkiaCanvas.tsx`.
- ✅ `SkiaCanvas.tsx` updated; `CanvasNode.thread_context_id?` and `CanvasEdge.label?`
  added as optional fields (backward-compatible; existing smoke tests unaffected).
- ✅ §10 conflicting items remain excluded (no FAB / image / manual-node creation code).
- ⏳ `.pyc` clean: Python not run in M3-B; N/A for this track.
- ⏳ worklog-v7 updated (see 2026-06-22 M3-B entry).
- ⏳ Stage-2 device 60fps re-run at 40+ nodes — deferred operational gate, non-blocking.
- ⏳ Stage-3 65-node smoke — deferred operational gate, non-blocking.
- ⚠️ `SkiaCanvas.tsx` is 372 lines — 22 lines over the 300–350 canon target. No new
  behaviour should be added to this file without first extracting `NodeChip` and the
  overlay layer into separate modules (refactor ticket for M4 cleanup).

## 10. Excluded Pending ADR — Manual / Media Node Creation

The following MVP items CONFLICT with higher-ranked docs and are NOT in this SDD:

- **Node Creation FAB (MVP §3.2)** and **manual text nodes**: data-contract §3 states
  branching happens only via phrase selection or edge-`+`, and learners do not edit node
  body/content. `node_created` v1 mandates AI-provenance payload (`source_node_id`,
  `source_offer_set_id`, `source_option_id`, `source_option_text`, `thread_context_id`),
  which structurally blocks a manually authored node.
- **Image nodes (MVP Known Scope Notes line 516)**: same `node_created` block, plus a new
  ADR-0013 native render variant for media.

Resolution required BEFORE any code: an ADR that (a) amends data-contract §3 to admit a
non-AI node origin, and (b) adds a `node_created` v2 (or a distinct `media_node_created`)
spec with a non-AI provenance payload. Until then these features stay blocked; this SDD
must not be read as authorizing them.

## 11. Traceability Matrix

| Feature | MVP § | Contract / ADR | Tests |
|---|---|---|---|
| F1 Edge labels | §4.4 L281 | ADR-0013; M3 §9 | TB1 |
| F2 Edge-`+` UI | §4.4 L269–285 | contract §3; `offer-sets/edge` | TB2 |
| F3 Selection/toolbar | §3.3; §4.3 L260 | contract §3,§10; ADR-0013 | TB3,TB4 |
| F5 Native culling | M3 §9 | ADR-0013,0016 | TB6 |
| F6 Node-limit UI | M3 §11 | config §3 | TB7 |
| FAB / Image (excluded) | §3.2; L516 | contract §3 (CONFLICT) | — (ADR first) |
