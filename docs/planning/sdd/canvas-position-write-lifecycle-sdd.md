# Canvas Position-Write Lifecycle — Software Design Document

**Document Version**: 0.6

**Status**: Completed bounded stabilization record — Android review accepted 2026-07-12

**Phase / milestone**: Bounded post-M4, pre-M5 canvas stabilization; not a formal M4.5 milestone

**Owner**: developer

---

## 1. Increment Identity

| Field | Value |
|---|---|
| Increment name | Reliable drag-end position writes |
| Phase / milestone | Bounded post-M4, pre-M5 canvas stabilization |
| Status | Completed bounded stabilization record — Android review accepted 2026-07-12 |

Goal: make every completed node drag produce an ordered, observable position write without
changing the backend contract, layout behavior, gesture-time SharedValues, or M5 scope. Phase A
delivers the checked API helper and a pure per-node FIFO coordinator. Phase B1 integrates that
coordinator with `SkiaCanvas`; Phase B2 adds sheet-local recovery for a created child's separate
initial position write.

## 2. Source-of-Truth References

- `docs/planning/development-approach.md` §5 M3-C: `PATCH /nodes/{id}` prevents drag positions
  being lost on reload; §8: small traceable increments and red-first deterministic work.
- `docs/configuration-reference.md` §4: `NODE_POSITION_PERSIST_MODE=drag_end`; persist the final
  position from each drag while intermediate movement samples remain omitted.
- `docs/planning/sdd/phase-3-m3-canvas-sdd.md` §§5, 7: SharedValues own frame-by-frame state and
  canonical state is written once on gesture end.
- `docs/planning/sdd/phase-3-m3c-infrastructure-remediation-sdd.md` §§4.2, 7: the existing PATCH
  endpoint appends `node_position_updated` and returns accepted coordinates.
- `docs/planning/sdd/phase-3-m3-6-canvas-controls-sdd.md` §4 requirements 4 and 6: drag-end
  positions use the established commit/persistence path, including snap-to-grid.
- `docs/architecture/adr-log.md` ADR-0013: hybrid Skia/native canvas with UI-thread gesture state.
- `docs/planning/session-path-data-contract.md` §§6, 8, 11: student-safe session state is durable;
  broader offline queues and conflict resolution are outside the MVP boundary.

## 3. Scope

### Phase A — in scope

- Change the existing position PATCH helper from fire-and-forget `void` to a typed promise that
  rejects network/non-2xx failures and returns the accepted coordinate acknowledgement.
- Add a small pure coordinator with independent per-node FIFO queues.
- Enqueue every completed drag; do not coalesce completed drag-end writes.
- Permit one in-flight write per node and concurrent writes for different nodes.
- Preserve newest visible intent while older writes settle.
- Pause one node's queue on a failed head and support an explicit, non-duplicating retry command.
- Track hydrated baseline, acknowledged position, visible position, and save status through a
  deliberate public coordinator contract.
- Ignore callbacks invalidated by coordinator disposal/session generation.
- Add focused deterministic tests before completing production behavior.

### Phase B1 — approved canvas integration

- Add a focused `useNodePositionWrites` hook that owns coordinator lifetime, credential refs,
  baseline synchronization, subscription, visible-position derivation, failed-node aggregation,
  and retry commands.
- Keep `SkiaCanvas` as an orchestrator and below the canon's 300–350 line band.
- Replace direct position PATCH calls with drag-end FIFO enqueueing.
- Render coordinator-derived visible positions without per-frame React, Zustand, coordinator, or
  network writes.
- Expose one neutral canvas-level status with the failed-node count and one Retry action that
  retries every currently failed head exactly once.
- Verify that refreshed credentials are used by later queued/retried writes without rebuilding the
  coordinator.
- Verify disposal/generation isolation. The production app has no current path that changes
  `sessionId` while the same canvas instance remains mounted, so B1 adds no speculative navigation
  blocking or queue-draining UI.

### Phase B2 — approved child-position recovery

- Keep branch creation and initial child positioning as two explicit operations.
- Use the checked `patchNodePosition` helper directly from `EdgeOfferSetSheet`; branch placement is
  not part of the drag-position FIFO.
- After successful creation, retain only the child identity, intended position, and placement
  lifecycle needed for sheet-local recovery.
- A failed placement must retain the durable branch, keep the sheet open, avoid a success claim,
  and offer `Retry placement` plus `Close and reload`.
- Retry only the existing child's PATCH with current credentials; never recreate the branch.
- Route every close/dismissal after a placement failure through one idempotent canonical reload
  boundary. Before creation, ordinary close behavior remains unchanged.
- Prevent dismissal while initial branch creation is unresolved. Once the branch is durable,
  recovery dismissal remains available while a placement retry is pending.
- Treat a successful creation response without a usable child identity as incomplete placement:
  do not PATCH or claim full success, offer canonical reload, and do not offer an unsafe retry.
- Guard late position completion after recovery close or unmount so it neither updates local state
  nor invokes the completion/reload callback again.
- Do not add optimistic insertion, deterministic layout, persistent retry, or a general async-task
  framework.

### Out of scope

- M5/checkpoints; deterministic layout; `{0,0}` fallback replacement; `manual_reference` hierarchy.
- Backend, endpoint, event registry, schema, migration, replay, tenancy, or projection changes.
- Persistent delivery across unmount, session replacement, termination, or restart.
- Offline queues, automatic indefinite retry, cross-device freshness, snapshot revisions/watermarks.
- Optimistic child insertion, Zustand migration, or broad canvas state refactoring.

## 4. Traceability

| Feature | Endpoint | Event | Read model | Worker | Tables |
|---|---|---|---|---|---|
| Drag-end position persistence | `PATCH /v1/student/sessions/{session_id}/nodes/{node_id}` | `node_position_updated` v1 | replayed student canvas snapshot | none | existing append-only `events` |

No API parity change is introduced: the endpoint and registered router already exist.

## 5. Module Placement

| Concern | Module | Boundary |
|---|---|---|
| Typed HTTP helper | `mobile/canvas/apiClient.ts` | existing tenant-safe student PATCH only |
| Pure FIFO lifecycle | `mobile/canvas/nodePositionCoordinator.ts` | no React, canvas renderer, backend, or analytic imports |
| React integration | `mobile/canvas/useNodePositionWrites.ts` | coordinator ownership/subscription only; latest credentials through refs |
| Canvas composition | `mobile/canvas/SkiaCanvas.tsx` | drag-end enqueue, derived positions, neutral retry UI |
| Branch placement recovery | `mobile/canvas/EdgeOfferSetSheet.tsx` | one created child; checked PATCH and sheet-local recovery only |
| Phase A tests | `mobile/canvas/__tests__/` | public helper/coordinator contract only |
| Phase B2 tests | `mobile/app/__tests__/EdgeOfferSetSheet-positionFailure-test.tsx` | observable requests, controls, and callbacks only |

## 6. Event, Schema, and Configuration Deltas

- Event types: none.
- Payload/schema changes: none.
- Migrations: none.
- Backend changes: none.
- Governing configuration remains `NODE_POSITION_PERSIST_MODE=drag_end`.

## 7. Invariants

- **Category Invisibility**: position requests contain only position coordinates and existing
  path identifiers; no analytic vocabulary or tenant input is introduced.
- **Event Sourcing**: every completed drag is dispatched through the existing PATCH endpoint so
  the backend remains the sole builder/appender of `node_position_updated`.
- **Tenant Isolation**: mobile sends no `tenant_id`; the existing authenticated backend resolves it.
- **Dual-state canvas**: Phase A has no gesture worklet or per-frame writes. Future integration may
  enqueue only at the existing drag-end commit boundary. B1 subscription updates occur only on
  meaningful lifecycle transitions, never gesture frames.
- **Organic-First**: generation/classification paths are untouched.

## 8. Test Plan

| Layer | Coverage |
|---|---|
| L1 | pure FIFO ordering, independent nodes, acknowledgements, failure pause/retry, visible state, disposal |
| L6 | typed API helper plus hook/component integration, credential refresh, stable snapshots, retry UI |

Backend suites are not required because Phase A changes no backend behavior.

## 9. First Red Tests

1. API helper rejects network failure and non-2xx responses; success returns accepted coordinates.
2. Two and three completed drags for one node dispatch FIFO with one in flight.
3. Two nodes dispatch independently.
4. Newer intent stays visible while an older write is pending or fails.
5. A failed head pauses only that node; retry does not duplicate and resumes FIFO order.
6. Acknowledgements advance in queue order.
7. Latest-intent failure derives the last acknowledged position or hydrated baseline as rollback.
8. Disposed/invalidated callbacks cannot change observable state.

## 10. Phase A Definition of Done

- [x] All §9 tests are red before their production behavior is completed.
- [x] API helper and coordinator focused tests pass independently and together.
- [x] Nearest existing API/canvas-control tests remain green.
- [x] TypeScript passes for changed Phase A files.
- [x] No canvas/branch UI integration, backend changes, or M5 work is included.
- [x] Phase A public API and state transitions are reported for review before Phase B.

## 11. Phase B1 Design Contract

### 11.1 Subscription and snapshots

- Extend the coordinator with `subscribe(listener)` and an immutable aggregate snapshot getter.
- The snapshot getter returns the same object identity until a meaningful transition occurs.
- Meaningful transitions are enqueue, acknowledgement, failure, retry, changed hydrated baseline,
  and explicit lifecycle invalidation. Unchanged baselines are no-ops and do not notify.
- Internal maps/queues remain private; component tests observe only hook/component outputs.

### 11.2 React ownership and cleanup

- `useNodePositionWrites` creates one coordinator per mounted session identity.
- The write adapter reads current `apiBaseUrl` and `authorizationToken` refs. Token refresh does not
  rebuild the coordinator and later queued/retried writes use the refreshed token.
- Cleanup unsubscribes React listeners before disposing the coordinator.
- Disposal invalidates late callbacks and must not notify an unmounted subscriber.
- The hook may use `useSyncExternalStore`; no render-time snapshot allocation loop is permitted.

### 11.3 Visible state and retry

- Hydrated positions seed baselines; acknowledged/queued mounted-session authority remains above
  later hydration without causal freshness evidence.
- The newest completed drag remains visible while older writes settle.
- If one or more node heads fail, one category-neutral canvas status shows the affected-node count.
- One Retry action retries each currently failed head once; writing/idle nodes are skipped and
  repeated presses cannot duplicate requests.
- Later queued positions behind a failed head remain visible but are not described as saved.

### 11.4 B1 red-first tests

1. Coordinator snapshots are referentially stable until a meaningful transition; unchanged
   baselines neither notify nor change snapshot identity.
2. Hook uses current credentials for later queued/retried writes without coordinator recreation.
3. Hook derives visible positions, failed-node count, and Retry-all behavior.
4. Cleanup unsubscribes before disposal and late completion does not update mounted UI.
5. `SkiaCanvas` drag-end enqueues through the coordinator and renders newest visible intent.
6. Acknowledgement, older failure, latest failure fallback, retry, independent nodes, and hydration
   precedence are observable through focused hook/component boundaries.
7. Existing gesture-hook callbacks may be captured and `NodeChip` may be replaced with a test-local
   position probe; tests must not inspect coordinator internals.

## 12. Phase B1 Definition of Done

- [x] §11.4 tests are red before B1 production behavior is completed.
- [x] Hook tests, component tests, API/coordinator tests, and nearest canvas tests are green.
- [x] TypeScript is green with no new unhandled promises, leaked subscriptions, or open handles.
- [x] `SkiaCanvas.tsx` remains below the canon line limit (310 lines after B1 extraction).
- [x] No Phase B2, layout, backend, navigation, M5, or global test-infrastructure changes land.
- [x] B1 stops for review before branch integration or the full mobile suite.

## 13. Phase B2 Design Contract

### 13.1 Sheet-local state and authority

- Before creation, the sheet owns only ordinary submission state.
- After creation, the backend-created branch is canonical and must never be represented as undone
  merely because its separate position PATCH fails.
- Recovery retains the child ID when present, the intended child position, and a placement phase;
  it does not retain or forward the full branch payload unless an existing consumer requires it.
- The existing `onBranchCreated` callback remains the single canonical close-and-rehydrate
  boundary and is invoked at most once per mounted sheet flow.

### 13.2 Success, failure, and recovery

- Normal success is creation POST once, checked position PATCH once, then the canonical callback
  once.
- HTTP or network placement failure keeps the sheet open with neutral `Branch created` and
  `Placement was not saved` feedback.
- `Retry placement` sends only the PATCH, uses current component credentials, and is guarded
  against duplicate presses while active. Failure remains recoverable; success invokes the
  canonical callback once.
- `Close and reload`, the post-creation Close action, and platform dismissal all invoke the same
  idempotent canonical callback without retrying placement or claiming it was saved.
- Initial creation cannot be dismissed while unresolved. A placement retry may be abandoned via
  canonical reload because the branch is already durable.
- A creation result without a usable child ID offers canonical reload but no placement retry.
- Unmount and recovery completion invalidate pending position callbacks. Late settlement must not
  update state, invoke callbacks twice, or create an unhandled rejection.

### 13.3 B2 red-first tests

1. Normal creation plus placement success preserves the existing callback flow.
2. HTTP and network placement failures retain neutral recovery UI and do not report success.
3. Retry sends only PATCH, never repeats creation, and duplicate active retries are ignored.
4. Failed retry remains recoverable; successful retry completes exactly once.
5. Close/reload performs no extra PATCH and late success cannot complete twice.
6. Unmount absorbs late failure without state updates or unhandled rejection.
7. Retry uses credentials from the latest render.
8. Initial submission remains single-flight, including dismissal protection.
9. Missing child identity cannot trigger PATCH or a false placement-success claim.

## 14. Phase B2 Acceptance Evidence

- [x] Focused B2 suite passes independently: 12/12 tests.
- [x] Nearest branch/discovery, API, coordinator, hook, and canvas tests pass: 53/53 tests.
- [x] TypeScript passes with `tsc --noEmit`.
- [x] Complete mobile Jest suite passes: 31 suites, 165/165 tests.
- [x] The focused B2 test has no act warnings, unhandled rejections, or open-handle output.
- [x] Existing broader-suite warning categories remain outside B2; no new category originates from
  `EdgeOfferSetSheet-positionFailure-test.tsx`.
- [x] `EdgeOfferSetSheet.tsx` remains within the canon size band at 230 lines.
- [x] No backend, schema, event, layout, navigation, coordinator, `SkiaCanvas`, or M5 change is
  included in Phase B2.

## 15. Known Limitations

- In-memory queued delivery is not guaranteed across unmount, session replacement, application
  termination, or restart. Phase A must not claim otherwise.
- The API has no causal position revision or event watermark; cross-device freshness is undefined.
- Unpositioned child recovery remains owned by the later layout/hydration slice.
- A child retained through Close and reload may hydrate at the existing `{0,0}` missing-position
  fallback. Phase B2 neither corrects that fallback nor introduces deterministic layout.
- Branch creation and initial positioning remain non-atomic backend operations. Phase B2 does not
  implement an atomic branch command or persistent placement retry.

## 16. Physical-Device Review Boundary

- The existing durable backend and Expo Go LAN server were made reachable at
  `http://192.168.31.183:8000` and `exp://192.168.31.183:8081` on 2026-07-11; both returned HTTP
  200 and the Android Expo manifest used `application/expo+json`.
- This service-readiness check does not prove learner-visible position ordering, retry messaging,
  restart durability, or Android interaction quality. Those remain pending direct user review on
  the physical device.
- Device review must remain bounded to the implemented canvas position lifecycle. It must not be
  treated as authorization to start M5, implement layout, change the `{0,0}` fallback, add offline
  persistence, or alter backend branch atomicity.

## 17. Follow-on Android Corrections (2026-07-12)

Physical-device review identified two interaction defects adjacent to, but not expanding, the
position-write boundary. Both were corrected as bounded follow-on checkpoints under the same
canvas invariants and were confirmed working by direct Android review.

### 17.1 Dragged-edge UI-thread synchronization

- `CanvasEdges` derives geometry only for edges attached to the actively dragged node from the
  same Reanimated SharedValues used by the native node overlay.
- The prior UI-thread to JS to React-state path for dragged-edge geometry was removed; drag-end
  remains the only canonical/coordinator commit boundary.
- Edge type and label rendering, unaffected edges, gesture composition, backend behavior, layout,
  and M5 were not changed.

### 17.2 Edge-plus immediate feedback and request protection

- Each node's left/right edge-plus controls share a local busy state. A valid first press shows
  neutral loading feedback and permits one request in flight.
- HTTP/network failure clears busy state, shows neutral retry feedback, and permits one new
  single-flight retry. Unmount/culling invalidates late completion callbacks.
- Separate nodes may begin discovery independently; the existing discovery boundary accepts only
  the first successful current-generation result, so a later result cannot replace/reopen the
  active sheet or raise stale global failure feedback.
- Gesture composition, backend endpoints/schemas, node-position coordinator, layout, navigation,
  and M5 were not changed.

### 17.3 Evidence

- Edge-plus lifecycle tests: 5/5 independently; nearest edge-plus/discovery tests: 16/16.
- Focused canvas/edge/gesture/position regression run: 13 suites, 68/68.
- TypeScript and `git diff --check` passed. The final relevant runs reported no new warnings,
  open handles, or unhandled rejections.
- Direct Android review confirmed the dragged-edge and edge-plus corrections work. This does not
  close the separately deferred 40+ node performance or 65-node smoke gates.
