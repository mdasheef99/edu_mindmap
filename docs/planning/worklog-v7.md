
### 2026-06-23 — Phase 3 Infrastructure Audit: "Compute-Ready, Transport-Missing" gaps identified

**Phase / milestone**: Phase 3 — M3/M3-B CLOSED for rendering; M3-C Infrastructure Remediation
now required before M4 can begin.

**Spec sections used**:
- `student-api-spec.md` §5 (session endpoints), §6 (node PATCH/GET), §7 (edge endpoints).
- `session-path-data-contract.md` §6–§9 (node_visited, viewport_changed, cascade events).
- `infrastructure-remediation-rca.md` §2–§8 (canonical gap registry, three-seam analysis,
  execution plan).

**Audit scope**: API implementation parity (spec vs. actual FastAPI routers), state reconciliation
across all mobile `fetch` call sites, event validation integrity in `registry.py`/`store.py`,
and session hydration depth beyond the canvas layer.

**Findings — confirmed pattern across all three seams**:
- **Seam A (Event Transport)**: `POST /v1/student/sessions/{id}/events` is documented in
  `student-api-spec.md` §5 but not implemented. `validate_event` + `InMemoryEventStore` are
  fully ready; the API boundary was never added. `node_visited` and `viewport_changed` have
  never been exercised at the API boundary.
- **Seam B (Hydration)**: `GET /v1/student/sessions/{id}` is documented but absent. `resume`
  endpoint returns `StudentSession` metadata only — no nodes/edges/viewport. `active_canvas_
  from_events()` reconstruction logic exists but is unreachable from the mobile client. `App.tsx`
  still feeds `DEV_NODES`/`DEV_EDGES`/`DEV_TRANSFORM` (dev fixtures mask the gap).
- **Seam C (Write-back)**: `NodeToolbar.confirmDelete` discards `NodeDeletionResponse` body
  (G1 — full discard). `PhraseSelectionReaderSheet.chooseOption` consumes only `child_node_id`,
  ignoring `node_created`/`edge_created` (G1-variant — partial reconcile). `PATCH /nodes/{id}`
  endpoint missing; drag positions are write-only-to-local and lost on reload.

**Root cause**: Milestone SDDs (M1–M3) defined scope by feature slice, not by API contract
completeness. No DoD item required verifying that each spec endpoint their feature depended on
was actually implemented. See RCA §3 for full analysis.

**Gap count**: 3 phantom endpoints (P1 Walking-Skeleton-critical), 5 reconciliation defects
(G1–G7 reduced set), 2 event emission gaps (G4/G5), and 1 validation depth gap (G7).
Full registry: `docs/planning/infrastructure-remediation-rca.md` §2.

**Priority impact**: **M3-C Infrastructure Remediation increment is now required before M4.**
M4 (Curriculum entry + Supabase Auth) cannot begin until the Walking Skeleton is truly
end-to-end: client emits events → server ingests → canvas hydrates from server state.

**Next required actions** (in order; TDD — red before green per canon §9):
1. Draft `docs/planning/sdd/phase-3-m3c-infrastructure-remediation-sdd.md`.
2. **Seam A**: write red integration test → implement `POST /events` endpoint → turn green.
3. **Seam B**: write red test → implement `GET /sessions/{id}` with canvas payload → turn green.
4. **Seam C**: write red tests → fix `NodeToolbar` cascade reconcile + add `PATCH /nodes/{id}`.
5. **Tier 2**: wire `node_visited` and `viewport_changed` emission from `SkiaCanvas`.
6. Replace `App.tsx` dev fixtures with real session hydration.
7. CI gate + device smoke → M3-C closure → M4 begins.
8. **Owner action required**: amend `development-approach.md` §5 (add M3-C row) and §6
   (add Interface-First protocol as Discipline #10). See RCA §7.

**RCA document**: `docs/planning/infrastructure-remediation-rca.md` (created 2026-06-23).


---

**M3 §14 Definition-of-Done audit** (status at rotation):
- 17 §12 red tests green; full mobile Jest + pytest suites green — **DONE**.
- Coordinate seam / layout / dual-state sync / viewport culling behind shared modules — **DONE**.
- `node_visited` v1 + `viewport_changed` v1 registered; producer/payload guards — **DONE**.
- Node-limit backend 409 guard; no `node_created` when blocked — **DONE**.
- Skia pan/zoom integrated with Native node overlay; manual_reference edges drawable — **DONE**.
- Mobile Sentry initialized in `App.tsx` via `SENTRY_DSN_MOBILE` — **DONE**.
- Stage 1 CI gate green **and** Stage 2 device gate passed — **DONE** (M3→M4 unlocked).
- `.pyc` cleaned; worklog updated; requirements trace to a § — **DONE** (this entry).
- **Conclusion**: every §14 DoD line item is satisfied. **Stage 3 (65-node smoke) is the sole
  remaining M3 activity**, and it is explicitly non-blocking for the M3→M4 transition (SDD §13).

**Gate status**:
- Stage 1 CI gate: **GREEN** ✅ | Stage 2 device gate: **PASSED** ✅ | M3→M4: **UNLOCKED** ✅
- Stage 3 65-node smoke: **NOT YET RUN** (documented, non-blocking).

**Next required action**:
1. (Optional, non-blocking) Run Stage 3: load a `CANVAS_NODE_HARD_LIMIT=65`-node board on the
   reference mid-range Android device; repeat pan/zoom profiling; record graceful degradation here.
   On failure → ADR-0016 escalation (revisit layout/culling). Profile against production draw
   content (debug grid already removed).
2. Resolve the `phase-3-m3` commit (lockfile + SkiaCanvas + docs); do **not** push without explicit
   user approval.
3. Begin M4 scoping (Curriculum entry + Supabase Auth) per `development-approach.md` §5 M4.

---

### 2026-06-21 — Advanced mindmap-feature roadmap audit (§5 / §7.3 / §7.8 cross-reference)

**Phase / milestone**: Phase 3 — M3 closed for maturation; M4 is next per `development-approach.md` §5.

**Spec sections used**:
- `development-approach.md` §5 (milestone ladder M1–M8; "Deferred without guilt" list, lines 151–154),
  §2.6 (#6 "Defer without guilt" — replay/projection adds layers later, lines 66–68), §7.3 (locked
  mobile stack + "Deferred", lines 233–234), §7.8 ("Explicitly Deferred (Never in MVP)", line 285),
  §9 (canvas risk row — Reader-sheet fallback before in-node selection, line 342), M3 row (line 144).
- `adr-log.md` ADR-0013 (Skia↔Native hybrid seam; in-node selection seam risk).

**Audit question**: are "advanced" mindmap features (rich-media nodes, advanced connectivity,
mindmap-specific UX) slated for M4–M8, or do they need a new Phase 4?

**Findings (traceable; no requirements originated — canon document-usage rule)**:
1. **Rich-media (image/video) nodes** — §5 deferred list (line 152) lists "image/video enrichment
   tiers" as **Deferred without guilt**, justified by §2.6 #6: event-sourcing lets such layers be
   added later via replay/projection. They are **post-MVP**; **no milestone in M1–M8** owns them.
2. **Advanced connectivity** beyond M3's two edge kinds (`ai_path` solid, `manual_reference` dashed —
   M3 row, line 144) — **none scheduled** in M4–M8. Related deferred items (topology Phases 2–3,
   ADR-0012 "steering" still Proposed; §5 line 153) are teacher-side analytic graph measures, **not**
   student-canvas edge types. New student-canvas connectivity = post-MVP / requires a new decision.
3. **Mindmap-specific UX** — **in-node text selection** is the strongest deferral: §7.8 lists it as
   **"Never in MVP"** (line 285; Reader bottom-sheet is the primary path, hybrid-seam risk per
   ADR-0013), reinforced by §7.3 (line 233), §5 M2 (line 143), and the §9 risk row (line 342).
   Enrichment tiers are post-MVP (item 1). The MVP canvas (M3) gate is **purely performance**
   (60fps@40 nodes); the SoT treats the canvas as MVP-complete at M3.

**Determination**:
- **None of these features belong to M4–M8.** M4–M8 are fixed and non-canvas: M4 Curriculum+Auth,
  M5 Checkpoints, M6 Teacher V1/V2, M7 Teacher V3, M8 Podcast (§5 lines 145–149).
- They are **post-MVP / "Never in MVP"** by existing SoT decisions, addable later via
  replay/projection without migration (§2.6 #6).
- **A "Phase 4" is NOT defined in any source-of-truth document.** Per canon's document-usage rule
  ("Do not originate requirements outside of this framework"), introducing a Phase 4 or rescheduling
  any deferred feature is an **owner-level amendment to `development-approach.md` §5 (SoT rank #1)**,
  not something this worklog may originate.

**Priority impact**: **NONE.** The audit confirms the existing sequence is correct; advanced
mindmap features remain deferred by design. The "Next required action" below is **unchanged in
priority** — M4 remains the next milestone; advanced-feature scheduling is flagged as a pending
owner decision only.

**Revised "Next required action" (post-audit)**:
1. (Optional, non-blocking) Run Stage 3 65-node smoke on the reference device (as above).
2. Resolve the `phase-3-m3` commit; **do not push without explicit user approval**.
3. **Begin M4 (Curriculum entry + Supabase Auth)** per §5 M4 — this is the priority path.
4. **Do NOT schedule** rich-media nodes, advanced connectivity, or in-node selection. They stay
   deferred/Never-in-MVP (§5, §7.8) until the owner explicitly amends `development-approach.md` §5.
   If the owner wants any of them, raise it as an ADR / §5 amendment first.

---


### 2026-06-23 — Phase 3 M3 Canvas fixes: Drag attachment, Culling expansion, UI refinement

**Phase / milestone**: Phase 3 — M3 / M3-B fixes.

**Work completed**:
- **Culling viewport fix**: Expanded the canvas bounding box (`visIds`) by half the chip size (`CHIP_W/(2*scale)` and `CHIP_H/(2*scale)`) so nodes aren't culled the instant their center crosses the screen boundary. Wired `onTransformEnd` in `App.tsx` so the culling box tracks live viewport pans instead of sticking to the initial mount transform.
- **Node-drag edges**: Updated the `nodePositions` culling and path-drawing array to merge the currently dragged node's live position override (`dragCurrBX` / `dragCurrBY`). This ensures Bézier edges stay anchored to the node *during* a drag, rather than snapping after the drag commits.
- **`EdgePlusButtons` live tracking**: Upgraded the `+` buttons to read from the live UI-thread SharedValues (`scaleShared`, `translateXShared`, `translateYShared`) via `useAnimatedStyle`. They now stick perfectly to nodes during panning instead of drifting on a stale committed transform.
- **`EdgePlusButtons` visual refinement**: Retained the 44pt touch-target accessibility invariant (`MVP L277`) but shrank the visual indigo circle to 24pt, so it reads as a proportional dot on the chip's vertical edge.
- **Test sync**: Adjusted Reanimated mock to allow no-op `useAnimatedReaction`; rewrote `edgePlusButton-test.tsx` props for shared-value injection; 16 suites / 84 mobile Jest tests remain green.

**Next required actions**:
1. (Optional, non-blocking) Run Stage 2 device re-run and Stage 3 65-node smoke.
2. Resolve the `phase-3-m3` commit; **do not push without explicit user approval**.
3. **Begin M4 (Curriculum entry + Supabase Auth)**.

### 2026-06-22 — Phase 3 M3-B Canvas Feature Parity: LOCALLY COMPLETE

**Phase / milestone**: Phase 3 — M3-B Canvas Feature Parity (supplemental to M3 base).

**Spec sections used**:
- `phase-3-m3b-canvas-feature-parity-sdd.md` §1–§9 (all features F1–F3, F5–F6; TB-series tests).
- `mvp-features-specification.md` §3.3 (node selection), §4.4 L269–285 (edge-`+` UI, edge labels),
  §4.3 L260 (delete cascade).
- `session-path-data-contract.md` §3 (no body editing), §10 (deletion cascade).
- `adr-log-02.md` ADR-0013 (Skia/Native placement), ADR-0016 (layout invariance).
- `phase-3-m3-canvas-sdd.md` §4 (coordinate seam), §5 (dual-state), §7 (write-once-on-end),
  §9 (viewport culling, `visibleNodeIds`), §11 (node limits).
- `configuration-reference.md` §3 (`CANVAS_NODE_WARNING_COUNT=50`, `CANVAS_NODE_HARD_LIMIT=65`).

**Work completed**:

*Red-test-first (all suites written RED, then turned GREEN):*
- **TB1** `edgeLabel-test.tsx` — `edgeLabelLayout` Bézier-midpoint anchor + truncation → **GREEN**.
- **TB2** `edgePlusButton-test.tsx` — EdgePlusButtons positioning, 44pt touch target, POST
  `/v1/student/offer-sets/edge` → **GREEN**.
- **TB3/TB4** `nodeSelection-test.tsx` — `hitTestNode` AABB, store write-once, toolbar actions,
  `DELETE ?confirmed=true` → **GREEN**.
- **TB6** `skiaCanvas-test.tsx` (extended) — off-screen chip culled, edge-`+` & toolbar culled with
  off-screen node → **GREEN**.
- **TB7** `nodeLimitUi-test.tsx` — warning banner at 50, creation disabled at 65 → **GREEN**.

*New modules (all <300 lines; `mobile/canvas/`):*
- `edgeRendering.ts` — added `edgeLabelLayout`, `cubicBezierPoint`, `EDGE_LABEL_MAX_CHARS=28` (F1).
- `hitTest.ts` (new) — `hitTestNode` pure AABB helper (F3).
- `store.ts` (new) — `useMindMapStore` Zustand store: `selectedNodeId`, `selectNode`,
  `clearSelection`; single `set(...)` per call (§7 write-once rule) (F3).
- `nodeLimits.ts` (new) — `nodeLimitState(count): {showWarning, creationBlocked}` (F6).
- `NodeLimitBanner.tsx` (new) — warning banner Native View overlay (F6).
- `nodeOverlay.ts` (new) — `edgePlusButtonPositions` + `toolbarPosition` screen-space helpers;
  `NODE_SIZE=[200,160]` (F2/F3).
- `EdgePlusButtons.tsx` (new) — 44pt left/right TouchableOpacity buttons, POSTs edge offer-set (F2).
- `NodeToolbar.tsx` (new) — Explore + confirm-gated Delete toolbar; DELETEs cascade endpoint (F3).

*SkiaCanvas.tsx wiring (F1 / F2 / F3 / F5 / F6):*
- **Imports**: added `Platform`, `SkiaText`, `matchFont`, `canvasToBoard`, `visibleNodeIds`,
  `edgeLabelLayout`, `hitTestNode`, `useMindMapStore`, `NODE_SIZE`, `EdgePlusButtons`,
  `NodeToolbar`, `NodeLimitBanner`, `nodeLimitState`.
- **Types**: `CanvasNode.thread_context_id?` (F2 passthrough); `CanvasEdge.label?` (F1);
  `SkiaCanvasProps.apiBaseUrl?` / `authorizationToken?` / `sessionId?` (F2/F3 opt-in chrome).
- **F1**: `edgeLabels` memo → `SkiaText` inside Skia `<Group>` (board space, auto-scaled).
- **F3**: `useMindMapStore` selection; tap gesture (`Gesture.Race(tap, Simultaneous(pinch, pan))`)
  → `handleTap` → `hitTestNode` → `selectNode`/`clearSelection`.
- **F5**: `visIds = new Set(visibleNodeIds(...))` memo; `NodeChip`, `EdgePlusButtons`, `NodeToolbar`
  all gated to `visIds.has(n.node_id)`.
- **F2**: `EdgePlusButtons` rendered per visible node when `discoveryEnabled`; `disabled` when
  `limitState.creationBlocked`.
- **F6**: `NodeLimitBanner activeCount={nodes.length}` always rendered (self-nulls below threshold).

**Test result**: **82/82 mobile Jest** ✅ (16 suites — up from 55 at M3 base, via 27 new M3-B tests).
No pytest run (Python not modified in M3-B).

**Gate status**:
- CI (Stage 1) Jest gate: **GREEN** ✅ (82/82)
- Device (Stage 2) 60fps re-run at 40+ nodes: **DEFERRED** — operational gate, non-blocking.
- Stage 3 65-node smoke: **DEFERRED** — operational gate, non-blocking (carried from M3 base).

**Known housekeeping item** (RESOLVED 2026-06-25):
~~`SkiaCanvas.tsx` is **372 lines** (22 over the 300–350 canon target). No new behaviour may be
added to this file without first extracting `NodeChip` and the overlay layer into separate modules.
Refactor ticket deferred to M4 cleanup (no behaviour change required).~~
→ Resolved: `SkiaCanvas.tsx` reduced to **242 lines** by hook-extraction refactor (see 2026-06-25 entry).

**Next required actions**:
1. Commit `phase-3-m3` branch (lockfile + all M3 + M3-B changes); **do not push without explicit
   user approval**.
2. (Optional, non-blocking) Run Stage 2 device re-run and Stage 3 65-node smoke on the reference
   device; record results here.
3. **Begin M4 (Curriculum entry + Supabase Auth)** per `development-approach.md` §5 M4 —
   this is the next priority milestone.
4. Early M4 refactor: extract `NodeChip` + canvas overlay layer from `SkiaCanvas.tsx` to bring
   the file under the 350-line canon limit before adding any M4 behaviour.

---

### 2026-06-24 — Phase 3 M3-C Infrastructure Remediation: locally complete

**Milestone context**: Phase 3 M3-C closed (prerequisite gate for M4). All three Walking-Skeleton
transport seams (A/B/C) and Tier 2 event-emission wiring are implemented, tested, and green.

**Spec sections used**:
- `phase-3-m3c-infrastructure-remediation-sdd.md` §4–§11 (Seam A/B/C, TDD test plan, closure DoD).
- `student-api-spec.md` §5 (`POST /events`, `GET /sessions/{id}`), §6 (`PATCH /nodes/{id}`).
- `session-path-data-contract.md` §6, §8, §10 (node contract, interaction events, deletion cascade).
- `infrastructure-remediation-rca.md` §2 (G1–G7 gap registry) — all T1/T2 gaps now remediated.

**What shipped**:
- **Seam A**: `backend/app/api/student/events.py` + `main.py` registration; `node_visited` v1 and
  `viewport_changed` v1 client whitelist with boundary validation; 8 integration tests (TA-1..TA-8).
- **Seam B**: `canvas_snapshot_from_events` helper; `CanvasNodeSnapshot` / `CanvasEdgeSnapshot` /
  `CanvasSnapshot` / `StudentSessionWithCanvas` models; `GET /v1/student/sessions/{id}` endpoint;
  8 integration tests (TB-1..TB-8) including Category Invisibility and router-ordering regression.
- **Seam C**: `PATCH /v1/student/sessions/{id}/nodes/{node_id}` endpoint emitting
  `node_position_updated` v1; `NodeToolbar` full `NodeDeletionResponse` reconcile;
  `PhraseSelectionReaderSheet.chooseOption` full-payload propagation; 4 backend + 4 mobile tests
  (TC-1..TC-4, TC-M1..TC-M4).
- **Tier 2**: `mobile/canvas/apiClient.ts` (`postClientEvent`, `throttledPostViewport`);
  `SkiaCanvas` fires `node_visited` on tap and `viewport_changed` on transform end;
  2 mobile tests (TA-M1, TA-M2).
- **R3 mobile hydration**: `mobile/canvas/useSessionHydration.ts` fetches `GET /sessions/{id}` and
  maps the student-safe snapshot into `CanvasNode[]`/`CanvasEdge[]`; `App.tsx` dev fixtures
  `DEV_NODES`/`DEV_EDGES`/`DEV_TRANSFORM` removed; 2 smoke tests (TR3-1, TR3-2).

**Test results**:
- Backend pytest: **120 passed** (full regression, Seam A/B/C integration suites green).
- Mobile Jest: **92 passed** (17 suites, including new M3-C tests).
- Import linter: **green** (no boundary violations).
- `.pyc` cleanup: **0 files remain** in `backend/`.

**Gate status**:
- M3-C CI gate (pytest + import-linter + mobile Jest): **GREEN** ✅
- M3-C student-api-spec parity check: **GREEN** ✅
- Category Invisibility: **VERIFIED** ✅
- Stage 2 device re-run / Stage 3 65-node smoke: **DEFERRED** (operational, non-blocking, carried from M3).

**Known housekeeping items**:
- ~~`SkiaCanvas.tsx` remains 372 lines; refactor `NodeChip` + overlay layer into separate modules
  before adding M4 behaviour.~~ → **RESOLVED 2026-06-25** (242 lines after hook-extraction refactor).
- `useSessionHydration` currently sources `apiBaseUrl`/`sessionId` from `DEV_*` constants; wire
  to authenticated Supabase session once M4 auth/session selection is built. *(carried to M4)*

**Next required action**:
1. Commit the M3-C slice (backend + mobile + docs); **do not push without explicit user approval**.
2. Begin M4 (Curriculum entry + Supabase Auth) per `development-approach.md` §5 M4.
---

### 2026-06-25 - Phase 3 M3.5 Frontend Readiness: locally complete

**Milestone context**: M3.5 is a bounded frontend-readiness bridge before M4. It hardens already
claimed M1-M3/M3-C learner surfaces without adding auth, curriculum entry, dashboard routing, or
new backend product endpoints.

**Spec sections used**:
- `.augment/rules/00-canon.md` (active milestone, source-of-truth order, SDD/TDD discipline,
  file-size constraints, Category Invisibility).
- `docs/mvp-features-specification.md` Feature Group 3 (Mind Map Canvas), Feature Group 4
  (AI Exploration Nodes), Feature 7.1 (session persistence/basic offline reopen boundary).
- `phase-3-m3-5-frontend-readiness-sdd.md` sections 1-11.
- `phase-3-m3b-canvas-feature-parity-sdd.md` edge `+`, node display, culling, node-limit context.
- `phase-3-m3c-infrastructure-remediation-sdd.md` session hydration and branch/reconcile context.

**Work completed**:
- Created `docs/planning/sdd/phase-3-m3-5-frontend-readiness-sdd.md` before production edits.
- Added red-first `nodeChip-test.tsx` coverage for learner-safe node display: `title` + `content`
  when present, compact id fallback only when no learner text exists.
- Updated `mobile/canvas/NodeChip.tsx` to remove the dev-only mock photosynthesis body and stop
  presenting full raw UUIDs as the primary learner label.
- Extended `useSessionHydration-test.tsx` red-first to prove session canvas snapshots preserve
  learner-facing `title`/`content`.
- Updated `mobile/canvas/useSessionHydration.ts` to map optional `title` and `content` from
  backend session snapshots into canvas nodes.
- Added red-first `skiaCanvas-test.tsx` coverage for failed edge `+` offer-set loading.
- Updated `mobile/canvas/SkiaCanvas.tsx` to show a visible, category-neutral edge discovery error
  and clear it after a successful offer-set response.

**Verification**:
- Focused readiness command:
  `npm.cmd test -- --runInBand nodeChip-test.tsx useSessionHydration-test.tsx skiaCanvas-test.tsx PhraseSelectionReaderSheet-test.tsx edgePlusButton-test.tsx`
  - Result: **35/35 passed** across 5 suites.
- Full mobile Jest:
  `npm.cmd test -- --runInBand`
  - Result: **97/97 passed** across 18 suites.
- TypeScript:
  `npx.cmd tsc --noEmit -p ..\canvas\tsconfig.json`
  - Result: **blocked by existing config**: `TS2688: Cannot find type definition file for 'jest'`.
  - The check exits before validating changed source files.
- No Python tests were run in M3.5; no `.pyc` cleanup required.

**Known residuals**:
- Existing React `act(...)` warnings remain in mobile Jest output.
- Existing canvas gesture hook-order warning remains visible in the test output.
- TypeScript verification remains blocked by the Jest type-definition configuration.
- Browser/web remains an inspection surface; native mobile remains the MVP target.
- M4 auth, curriculum entry, dashboard shell, and real session selection are still not implemented
  by design.

**Next required actions**:
1. Review and commit the M3.5 slice when ready; do not push without explicit user approval.
2. Resolve the Jest type-resolution issue so `npx.cmd tsc --noEmit -p ..\canvas\tsconfig.json`
   can become a real gate.
3. Begin M4 only after the M3.5 readiness slice is accepted.

---

### 2026-06-25 — SkiaCanvas orchestrator refactor: canon-limit compliance

**Phase / milestone**: Phase 3 — housekeeping (M3-B/M3-C carried item, resolved before M4).

**Spec sections used**:
- `phase-3-m3-canvas-sdd.md` §4, §5, §7, §9 (dual-state rule, write-once-on-end, culling).
- `phase-3-m3b-canvas-feature-parity-sdd.md` §5.2 (edge-`+` discovery state).
- `phase-3-m3c-infrastructure-remediation-sdd.md` §6, §7 (soft-deletion reconcile, event wiring).
- `00-canon.md` (300–350-line source-file canon limit; §5/§7 dual-state invariant; TDD rule).

**Context**: `SkiaCanvas.tsx` was flagged at 372 lines in both the M3-B (2026-06-22) and M3-C
(2026-06-24) entries as a carried housekeeping item. The file violated the 300-line canon limit
and concentrated domain logic that belonged in dedicated, individually-testable hooks.

**Work completed** (red-first; commit `4645bbd` on `phase-3-m3`):

*Four hooks extracted (`mobile/canvas/`):*
- `useDeletionReconciliation.ts` (47 lines) — soft-deletion filter; accumulates
  `NodeDeletionResponse` payloads; produces `liveNodes`/`liveEdges`/`handleDeleted`
  (M3-C SDD §6, §9.4).
- `useDiscoveryManager.ts` (53 lines) — edge-`+` offer-set sheet state machine; clears
  error on new offer-set, calls `onReloadCanvas` on branch-created (M3-B SDD §5.2).
- `useLiveDragOverride.ts` (51 lines) — `useAnimatedReaction` UI-thread → JS bridge;
  mirrors dragged node's live board position to React state for edge-path rendering;
  ephemeral SharedValues never leak to canonical state (M3 SDD §7 dual-state rule).
- `useCanvasRenderData.ts` (51 lines) — consolidated `nodePositions` / `viewport` /
  `visIds` / `visibleEdges` memos; single source for the render pipeline (M3 SDD §9).

*Orchestrator reduction:*
- `SkiaCanvas.tsx`: **372 → 242 lines** (–35%); now a pure composition layer.
- All domain logic delegated to hooks; dual-state boundary (`ephemeral SharedValues` vs.
  `canonical Zustand/Props`) correctly preserved.

*Tests (red-first, `mobile/canvas/__tests__/`):*
- `useDeletionReconciliation-test.tsx` — 4 tests: pass-through, cascade filter,
  multi-call accumulation, callback wiring.
- `useDiscoveryManager-test.tsx` — 5 tests: initial state, error clearing, error message
  text, branch-created reload, explicit close.
- `useLiveDragOverride-test.tsx` — 4 tests: null when idle, active position, drag-end
  clear, out-of-bounds index guard.
- `useCanvasRenderData-test.tsx` — 4 tests: position map, drag override, viewport
  culling, edge culling.
- `skiaCanvas-test.tsx` — refocused to integration seams (mount, prop wiring, event
  emission contracts); hook-internal tests removed.

*Infrastructure:*
- `mobile/app/package.json` `jest.roots` extended to include `../canvas` so the new
  hook tests are discovered by the existing `npm test` run.

**Test results**:
- Mobile Jest: **22 suites / 112 tests passed** (--runInBand, no failures).
- No Python tests run (backend not modified).

**Resolved carried items**:
- M3-B housekeeping: `SkiaCanvas.tsx` over canon limit → **RESOLVED** (242 lines).
- M3-C housekeeping: same item → **RESOLVED**.

**Next required actions**:
1. Begin M4 (Curriculum entry + Supabase Auth) per `development-approach.md` §5 M4.
2. `useSessionHydration` `DEV_*` constant wiring → real Supabase session (M4 auth work).

