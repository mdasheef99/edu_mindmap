# Canvas Position-Write Lifecycle Reconstruction — Software Design Document

**Document Version**: 1.0

**Status**: Locally complete — owner approval pending; no push or PR

**Phase / milestone**: Bounded post-M4, pre-M5 canvas stabilization; not a formal M4.5 milestone

**Base**: `origin/main` at `f1308fc71b5bb98f2c972d15d53a130e1ff012b0`

---

## 1. Goal and Boundary

Reconstruct reliable drag-end position delivery and the adjacent canvas interaction fixes onto the
post-PR-7 M4 tree. The increment makes completed drags ordered, observable, retryable, and
session-safe while preserving M4 authentication/curriculum behavior, existing backend contracts,
gesture-time SharedValues, layout semantics, edge semantics, node limits, and M5 scope.

Historical commits `c26853e666af84e8c0fdb2cd3066f84473a61889` and
`e324b9c9e5530d258b1fa403546385e11b12faf1` are implementation evidence only. No historical
completion status, test count, device claim, operational URL, or closure conclusion transfers to
this branch.

## 2. Source-of-Truth Traceability

- `docs/planning/development-approach.md` §5 M3-C: final drag positions persist through the
  existing PATCH seam; §§7.3 and 8: Zustand/Reanimated split, small reviewable increments, and
  red-first deterministic work.
- `docs/architecture/adr-log.md` ADR-0013: Skia edges, native node content, UI-thread gestures,
  and Zustand-owned canonical node positioning.
- `docs/architecture/adr-log-02.md` ADR-0016: deterministic `d3-hierarchy`, structural-only layout,
  and manual position overrides that survive later layout computation.
- `docs/planning/session-path-data-contract.md` §§5–11: session-scoped student-safe node state,
  resume/hydration, deletion-aware state, and the bounded offline boundary.
- `docs/planning/sdd/phase-3-m3-canvas-sdd.md` §§5–9: canonical/ephemeral ownership,
  write-once-on-end, gesture composition, Skia/native rendering, and culling.
- `docs/planning/sdd/phase-3-m3c-infrastructure-remediation-sdd.md` §§5–7: hydration,
  finite-coordinate PATCH, append-only `node_position_updated`, deletion reconciliation, and
  mobile event emission.
- `docs/planning/sdd/phase-3-m3-6-canvas-controls-sdd.md` §4: snap only at drag-end before local
  commit and persistence; pan/zoom limits and viewport behavior are unchanged.
- `docs/planning/sdd/phase-3-m4-curriculum-auth-sdd.md` §§5, 10–14 and the runtime-remediation SDD
  R2/R6: reuse the real token/session hydration path without redesigning M4.
- `docs/configuration-reference.md` §§3–4: zoom/node limits and
  `NODE_POSITION_PERSIST_MODE=drag_end` remain binding.

## 3. Approved Scope

### 3.1 Checked position delivery

- `patchNodePosition` returns a typed acknowledgement and rejects network, non-2xx, malformed,
  missing, or non-finite responses.
- Validate a completed position before it can enter visible/canonical state or the write queue.
- One FIFO queue exists per node. Completed drags are not coalesced; one write per node may be in
  flight while different nodes write concurrently.
- A failed head pauses only that node. Explicit Retry never duplicates an active request.
- Late callbacks from disposed sessions and deleted nodes are ignored.

### 3.2 Canonical position authority

- Extend the existing Zustand mind-map store only with session-scoped hydrated/manual position
  authority. Do not migrate the graph or viewport into this increment.
- Hydration initializes a session baseline without overwriting newer manual authority.
- Drag completion commits one finite manual override and marks it layout-authoritative.
- Acknowledgements preserve the latest manual intent; failure remains retryable without exposing
  invalid coordinates or resurrecting deleted nodes.
- Session replacement/sign-out resets the prior session authority. Deletion removes the deleted
  nodes' authority before stale callbacks can settle.
- The existing layout helper must continue to receive `positionOverridden: true` for manual
  authority when layout is explicitly computed. No new layout trigger is introduced.

### 3.3 Canvas rendering and gesture lifecycle

- Gesture frames mutate Reanimated SharedValues only. React, Zustand, coordinator, and network
  writes occur only at lifecycle transitions.
- A successful drag completion commits exactly once; cancellation commits zero times.
- Attached Skia edge/label geometry and native node/edge-plus overlays use the same active-drag
  SharedValues. Remove the per-frame UI-thread → JavaScript → React mirroring hook.
- Pan, zoom, hit-testing, culling, fit/reset, snap-to-grid, edge styling, and node caps retain
  their existing contracts.

### 3.4 Branch placement and discovery recovery

- Branch creation remains durable and separate from the child-position PATCH.
- Placement failure retains the created child, retries only its PATCH, or closes through one
  idempotent reload boundary. It never repeats branch creation.
- Edge-plus controls expose neutral loading/failure/retry feedback, share one request across the
  paired controls, and permit independent requests for different nodes.
- Only the first valid completion for the current discovery generation may own the active sheet.

## 4. Module Ownership

| Concern | Module |
|---|---|
| Typed checked PATCH | `mobile/canvas/apiClient.ts` |
| Pure FIFO lifecycle | `mobile/canvas/nodePositionCoordinator.ts` |
| Session/React adapter | `mobile/canvas/useNodePositionWrites.ts` |
| Canonical session positions | `mobile/canvas/store.ts` |
| Canvas composition/retry UI | `mobile/canvas/SkiaCanvas.tsx` |
| UI-thread edge geometry | `mobile/canvas/CanvasEdges.tsx` |
| One-off child placement | `mobile/canvas/EdgeOfferSetSheet.tsx` |
| Edge-plus request ownership | `mobile/canvas/EdgePlusButtons.tsx`, `useDiscoveryManager.ts` |

## 5. State and Failure Contract

For each current-session node, state distinguishes hydrated baseline, latest manual intent,
latest acknowledged position, queue status, and deletion. All public positions are finite.

1. Hydration seeds a node only when no newer manual/acknowledged authority exists.
2. Enqueue validates and exposes the newest completed intent, then dispatches the idle head.
3. Acknowledgement must name the same node and contain finite coordinates before it can advance
   the queue.
4. Failure pauses the head. A newer queued intent remains visible; otherwise the canonical manual
   intent remains visible and explicitly unsaved.
5. Retry dispatches the same head once.
6. Deletion invalidates the node queue and removes its canonical authority.
7. Session disposal invalidates every late callback and resets session-scoped authority.

The backend remains the sole appender of `node_position_updated`; the mobile client sends no
tenant identifier and never reads analytic state.

## 6. Red-First Test Plan

Before completing production behavior, observe intended failures for:

1. Checked PATCH network/non-2xx/malformed/non-finite acknowledgement behavior.
2. Finite input validation before visible/canonical/queued state.
3. One-node FIFO, cross-node concurrency, newest-intent visibility, failure/retry, and disposal.
4. Hydration → drag → rerender precedence and stale hydration protection.
5. Exactly one commit per completed drag and zero commits on cancellation/interruption.
6. Session switch/sign-out disposal and stale completion isolation.
7. Deletion with queued/failed writes preventing retry or resurrection.
8. Existing layout recomputation preserving a canonical manual override without a new trigger.
9. Pan/zoom, hit-test, culling, edges, and labels using the moved position.
10. UI-thread dragged edge/label/edge-plus synchronization without React-frame mirroring.
11. Placement failure/retry/close recovery without duplicate branch creation.
12. Edge-plus paired-control single-flight, failure/retry, independent nodes, and stale completion.
13. Existing backend PATCH → replay/hydration/resume preserving the moved coordinates.

The worklog must record the red command and intended reason before the corresponding production
behavior is completed.

## 7. Explicitly Deferred

- Viewport persistence; whole-graph Zustand ownership; persistent/offline write queues.
- Backend/API/event/schema/migration/RLS/tenancy/auth/curriculum/membership changes.
- New auto-layout triggers, runtime layout redesign, `{0,0}` fallback replacement, or
  `manual_reference` hierarchy correction.
- New node-deletion semantics, edge definitions, pan/zoom limits, dependency/lockfile changes,
  M5 checkpoints, and npm-audit remediation.
- New 40+ node performance or 65-node physical-device claims.

## 8. Verification and Closure Gates

This SDD remains in progress until focused lifecycle/rendering/recovery tests, full mobile Jest,
App and Canvas TypeScript, focused backend replay/PATCH/hydration/deletion/resume tests, full
pytest, Ruff format-check/lint, mypy, import-linter, `git diff --check`, artifact/secret scanning,
and zero remaining `.pyc` files are recorded from this branch.

Physical-device behavior and performance remain unverified unless separately rerun and recorded.

## 9. Branch-Local Verification Evidence (2026-07-13)

The approved lifecycle is implemented on `codex/integrate-canvas-position-lifecycle` from the
base named above. No backend, schema, migration, authentication, curriculum, membership, tenancy,
RLS, dependency, lockfile, viewport-persistence, or `App.tsx` behavior changed.

Red-first evidence was captured in three committed test slices before their production changes:

- checked PATCH, finite validation, FIFO/concurrency, store hydration/manual precedence,
  session disposal, deletion, and retry initially failed because the coordinator, hook, and
  session-scoped Zustand authority did not exist and PATCH returned `void`;
- render/gesture tests initially failed because writes were concurrent, edges/labels used static
  positions, cancellation had no finalizer, and render data still required the JS drag mirror;
- placement/discovery tests initially failed because failed placement completed the branch flow,
  edge-plus had no single-flight/retry state, and discovery had no completion ownership.

Final local gates:

- focused mobile lifecycle/rendering/recovery suites: green;
- full mobile Jest: 35 suites / 159 tests passed;
- App and Canvas TypeScript: green;
- focused backend PATCH/replay/hydration/deletion/resume: 22 passed;
- full Python: 164 passed / 3 skipped;
- Ruff format: 145 files already formatted; Ruff lint: green;
- mypy: 94 application source files green;
- import-linter: four contracts kept, zero broken;
- `git diff --check`: green; generated Python bytecode under `backend/` and `tests/`: zero.

The sibling worktree's own inherited virtual environment lacked declared `psycopg_pool`; backend
gates were therefore run against the already provisioned repository interpreter without changing
dependencies. Physical-device 40+ node performance and 65-node smoke were not rerun.
