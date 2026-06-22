# Worklog v7 — Phase 3 M3 Canvas Maturation (cont.) → M4 transition

AGENT ROTATION INSTRUCTION — READ FIRST: This is the live worklog after `worklog-v6.md` exceeded
the ~350-line canon threshold (`.augment/rules/00-canon.md`). Read `.augment/rules/00-canon.md`,
`docs/planning/development-approach.md` §5, and the active SDD
(`docs/planning/sdd/phase-3-m3-canvas-sdd.md`) before making changes. Prior trackers:
`docs/planning/worklog-v6.md` (rotated 2026-06-21), `worklog-v5.md`, `worklog.md`.

## Legacy Context Summary (state carried in from worklog-v6)

- **Phase 1 & Phase 2**: CLOSED locally (2026-06-18). Do not reopen unless explicitly requested.
- **Phase 3 M1 (session persistence/branching)**: Locally Complete / **Operationally Pending** —
  session resume, offer-set logging, edge `+` branching, deletion cascade, and event-only
  session-path reconstruction are green locally. **Deferred operational gates** (must not be claimed
  here): Render backend+worker live verification and physical-device Expo smoke.
- **Phase 3 M2 (phrase selection)**: **CLOSED** (2026-06-20) — §5 M2 user/device gate met on a
  physical Android device; "questions aren't tappable" fatal risk (§9) retired.
- **M3 schema groundwork**: complete — ADR-0016 (d3-hierarchy), schema doc reconciled,
  migration 0006 (`events_node_id_idx`) live in DB; schema audit closed.

### Phase 3 M3 Canvas — current state (2026-06-21)

- **§12 red-tests-first drill**: COMPLETE — 17/17 named tests green across T1–T7 (coordinate seam,
  layout, dual-state sync, viewport culling, event registry, node-limit 409, regression).
- **§14 DoD implementation tasks 1–5**: COMPLETE — mobile Sentry init (`@sentry/react-native` in
  `App.tsx`), gesture zoom-clamp + focal-preserving pinch, Skia Bézier edge rendering +
  `edgeStyleForKind`, manual-reference edge payload builder, Stage 1 CI render-count gate.
- **Event registration (§10)**: `node_visited` v1 and `viewport_changed` v1 registered in
  `backend/app/events/registry.py` with `client` producer + worker-rejection guards (T5 green).
- **Node-limit (§11)**: backend 409 guard live (`canvas/limits.py`, `offer_workflow.py`,
  `api/student/offer_choices.py`); no `node_created` appended when blocked (T6 green).
- **SkiaCanvas reactive rewrite**: Defects A–D resolved (commit `d53f94b`). Reactive
  `<Group transform>` (UI-thread, no per-frame React re-render); `'worklet'` on gesture reducers
  and coordinate seam; visible node chips with labels; §7 `createViewportGestureController`
  composed for write-once-on-end.
- **Stage 1 — CI render-count gate (merge-blocking)**: **GREEN** (55/55 Jest).
- **Stage 2 — physical-device 60fps gate (M3→M4 gate)**: **PASSED** (2026-06-21) on the reference
  mid-range Android device. Zoom/pan confirmed via a temporary board-space debug grid; the residual
  "node size constant on zoom" issue was resolved by adding `transform: [{ scale }]` to the
  `NodeChip` animated style. **The debug grid has since been removed** (production cleanup; the
  `NodeChip` scale fix is retained as a permanent production fix).
- **M3 → M4 unlock**: **UNLOCKED** — Stage 1 + Stage 2 both green (SDD §13 M3→M4 condition met).
- **Stage 3 — 65-node smoke**: **NOT YET RUN**. Documented, **not merge-blocking** for M3→M4
  (SDD §13). On failure, trigger the ADR-0016 escalation path (revisit layout/culling).

### Open / repo-state items carried in

- **Uncommitted on branch `phase-3-m3`** (vs. `d53f94b`, branch unpushed): `mobile/app/package-lock.json`
  (from the approved `npx expo install` of Skia/Reanimated/worklets/gesture-handler),
  `mobile/canvas/SkiaCanvas.tsx` (NodeChip scale fix; debug grid added then removed), and the
  v6/v7/SDD doc updates. Recommendation on record: commit the lockfile with the canvas changes on
  `phase-3-m3`. **Do not push without explicit user approval.**
- **Tooling**: use **Supabase MCP** for any DB/schema/migration verification and **Sentry MCP** for
  error triage — verify against live systems, never assume. `adb` is NOT installed on the host
  (logcat unavailable; use Metro console + device red-box for device runs).
- **Canon reminders**: red-tests-first (§9); SkiaCanvas under 300–350-line limit; delete generated
  `*.pyc` after Python test runs (verify 0 remaining); `@testing-library/react-native` v14
  `render` is async (`await render(...)`).

---

### 2026-06-21 — Worklog rotated to v7; debug grid removed; M3 DoD audit recorded

**Phase / milestone**: Phase 3 — M3 Canvas maturation (→ M4 transition pending Stage 3)

**Spec sections used**:
- `phase-3-m3-canvas-sdd.md` §9 (Skia reactive render), §13 (3-stage gate; Stage 3 profiling note),
  §14 (Definition of Done).
- `development-approach.md` §5 (milestone ladder M3–M8; reference-device rule), §9 (canvas risk).
- `.augment/rules/00-canon.md` (line-count rotation threshold; LIVE TRACKER pointer).

**Work completed**:
- **Worklog rotated** to `worklog-v7.md` (`worklog-v6.md` exceeded the ~350-line threshold). Canon
  `LIVE TRACKER` pointer updated to v7.
- **Debug grid removed** from `mobile/canvas/SkiaCanvas.tsx`: deleted the `gridPath` `useMemo` block
  and its `<Path>` render inside the Skia `<Group>`. The `NodeChip` `transform: [{ scale }]` fix is
  preserved (permanent production fix). File now ~257 lines (< 350 canon limit).
- **Validation**: Mobile Jest **12 suites, 55/55 passed** ✅ (grid removal is render-only; no logic
  change). No new diagnostics on `SkiaCanvas.tsx`.

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
