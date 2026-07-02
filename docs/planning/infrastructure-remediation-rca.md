# Phase 3 Infrastructure Remediation — Root Cause Analysis

**Document Version**: 1.0
**Date**: 2026-06-23
**Status**: Closed — T1/T2 gaps remediated (2026-06-24); T3/T4 endpoints remain deferred per M3-C scope
**Milestone context**: Phase 3 M3/M3-B/M3-C LOCALLY COMPLETE; M3-C remediation increment closed.
M4 (Curriculum entry + Supabase Auth) is now unblocked.
**Worklog**: `docs/planning/worklog-v7.md` (2026-06-23 infrastructure-audit entry)

---

## 1. Executive Summary

Exhaustive infrastructure audit (2026-06-23) confirmed that the Phase 3 M3/M3-B Canvas
implementation is **render-complete but transport-incomplete**. The backend logic for event
validation, canvas reconstruction, and cascade deletion was built and unit-tested in M1–M3.
The API boundaries that expose that logic to the mobile client were never added. The mobile
client therefore cannot emit events, hydrate canvas state from the server, or persist node
positions across sessions. This is a consistent architectural failure mode, not isolated bugs.

Three Walking-Skeleton-critical P1 phantom endpoints (not yet implemented but documented in
`student-api-spec.md`) must be built before M4 can begin:

| Phantom | Spec § | Seam | Tier |
|---------|--------|------|------|
| `POST /v1/student/sessions/{id}/events` | §5 | A — Event Transport | T1 |
| `GET /v1/student/sessions/{id}` | §5 | B — Hydration | T1 |
| `PATCH /v1/student/sessions/{id}/nodes/{node_id}` | §6 | C — Write-back | T1 |

---

## 2. Gap Registry

### 2.1 Reconciliation Gaps (G-series from audit)

| ID | Location | Description | Seam | Tier |
|----|----------|-------------|------|------|
| G1 | `NodeToolbar.tsx:58` | `confirmDelete` discards `NodeDeletionResponse`; `deleted_node_ids`/`deleted_edge_ids` never applied to local canvas state | C | T1 |
| G1-v | `PhraseSelectionReaderSheet.tsx:114` | `chooseOption` consumes only `child_node_id`; ignores `node_created`/`edge_created` payload so branch cannot render on canvas | C | T1 |
| G2 | `backend/app/api/student/` | `POST /sessions/{id}/events` endpoint missing; `node_visited`/`viewport_changed` have no transport path | A | T1 |
| G3 | `backend/app/api/student/sessions.py:42` | `POST /sessions/{id}/resume` and `GET /sessions/{id}` both missing canvas payload (nodes/edges/positions/viewport); `StudentSession` model has no canvas fields | B | T1 |
| G4 | `mobile/canvas/SkiaCanvas.tsx` | `node_visited` event never emitted on node tap; trigger point undefined | A | T2 |
| G5 | `mobile/canvas/SkiaCanvas.tsx` | `viewport_changed` event never emitted on `onTransformEnd`; trigger point undefined | A | T2 |
| G6 | `mobile/canvas/NodeChip.tsx` | `thread_context_id` falls back to `""` for dev-fixture nodes; edge-`+` POST will carry a blank field | B | T2 |
| G7 | `tests/integration/` | No integration tests for `/events` → projection pipeline; `validate_event` never exercised at the API boundary | A | T2 |

### 2.2 Phantom Endpoints (documented in spec but still absent from routers; edge routes are contract-parity expectations rather than phantom routes)

| Endpoint | Spec § | Impact | Tier |
|----------|--------|--------|------|
| `POST /sessions/{id}/events` | §5 | All client event emission blocked (= G2) | T1 |
| `GET /sessions/{id}` | §5 | Canvas hydration on resume impossible (= G3 root cause) | T1 |
| `PATCH /sessions/{id}/nodes/{node_id}` | §6 | Drag positions never persisted; lost on reload | T1 |
| `POST /sessions/{id}/close` | §5 | Session lifecycle incomplete | T3 |
| `GET /sessions/{id}/nodes/{node_id}` | §6 | Individual node fetch | T3 |
| `POST /sessions/{id}/nodes/{node_id}/summary` | §6 | Student summary | T3 |
| `POST /v1/student/sessions/{session_id}/edges`; `DELETE /v1/student/sessions/{session_id}/edges/{edge_id}` | §7 | Already published in the student API spec; treat as a parity-check expectation rather than a phantom endpoint | T3 |
| All curriculum, checkpoint, podcast, PYQ endpoints | §4/9/10/11 | Future milestones; intentionally deferred | T4/post-MVP |

---

## 3. Root Cause Analysis

### 3.1 Pattern: "Compute-Ready, Transport-Missing"

Every discovered gap shares one structural cause: **the domain/projection layer was built
and tested in isolation, and the API boundary connecting it to the mobile client was never
added**. Evidence across all three seams:

- **Seam A**: `validate_event` in `registry.py` + `InMemoryEventStore.append()` fully
  enforce payload rules; `node_visited` and `viewport_changed` are registered. Yet no
  `POST /events` endpoint exists. The registry has been exercised only by server-side and
  worker-side appends, never by a client HTTP call.
- **Seam B**: `active_canvas_from_events()` in `canvas_state.py` correctly reconstructs
  nodes/edges from the event log. `StudentSession` model exists and is returned by resume.
  Yet neither the model nor any endpoint exposes the canvas payload. The reconstruction
  function is used by the deletion workflow but is unreachable from the mobile app.
- **Seam C**: `NodeDeletionResponse` carries `deleted_node_ids` and `deleted_edge_ids`.
  `canvas_deletion.py` correctly builds and appends cascade events. Yet `NodeToolbar`
  discards the entire response body, leaving orphaned nodes on the local canvas.

### 3.2 Contributing Cause: Milestone SDDs Did Not Mandate API Parity Verification

M1–M3 SDDs defined scope by feature slice (offer-set flow, phrase flow, canvas rendering)
rather than by API contract completeness. No SDD check-list item required a developer to
verify that every `student-api-spec.md` endpoint their feature depended on was implemented
before the SDD was marked closed. This allowed "compute-ready, transport-missing" to
accumulate across three consecutive milestones without triggering a gate failure.

### 3.3 Contributing Cause: Mobile Dev Fixtures Masked the Gap

`App.tsx` feeds `DEV_NODES`/`DEV_EDGES`/`DEV_TRANSFORM` directly to `SkiaCanvas`. Because
the canvas rendered correctly from fixtures, there was no runtime signal that hydration from
the server was broken. The smoke screen (`M2PhraseSmokeScreen`) tested the phrase-selection
flow in isolation, which passed — masking the fact that the created branch node was never
inserted into the canvas component that a real user session would render.

---

## 4. Systematic Gap & Fix Plan (Three Seams)

### Tier 1 — Walking Skeleton P1 Blockers (must close before M4)

| Ref | Work item | Seam | Files | Dependency |
|-----|-----------|------|-------|-----------|
| R1 | Implement `POST /sessions/{id}/events`; validate whitelist; append to store | A | `backend/app/api/student/events.py` (new); `main.py` | None |
| R1-type | Add boundary type/enum checks (`visit_source` enum, numeric `scale`, list `visible_node_ids`) | A | `events.py` + `registry.py` | R1 |
| R1-bis | Implement `GET /sessions/{id}` returning `StudentSession` + canvas payload via `active_canvas_from_events` | B | `sessions.py`; extend `StudentSession` model | None |
| R2 | Implement `PATCH /sessions/{id}/nodes/{node_id}` for position + title update; emit `node_position_updated` or reuse `node_updated` | C | `nodes.py`; registry if new event type | R1 |
| R2-fix | Consume `NodeDeletionResponse` in `NodeToolbar.confirmDelete`; pass `deleted_node_ids`/`deleted_edge_ids` to `onDeleted`; reconcile in `SkiaCanvas` | C | `NodeToolbar.tsx`; `SkiaCanvas.tsx` | None |
| R3 | Replace `DEV_NODES`/`DEV_EDGES` in `App.tsx` with real `GET /sessions/{id}` call on session resume | B | `App.tsx` | R1-bis |
| R-choices | Consume full `node_created`/`edge_created` payload in `PhraseSelectionReaderSheet.chooseOption`; insert into canvas state | C | `PhraseSelectionReaderSheet.tsx`; `SkiaCanvas.tsx` | R1-bis |

### Tier 2 — Event Parity (P1 completeness for DoD event-emission requirement)

| Ref | Work item | Seam | Dependency |
|-----|-----------|------|-----------|
| R4 | Emit `node_visited` on `handleTap` → `selectNode`; fire `POST /events` | A | R1 |
| R5 | Emit `viewport_changed` in `onTransformEnd` throttled at `VIEWPORT_EVENT_THROTTLE_MS`; fire `POST /events` | A | R1 |
| G7 | Integration tests: `POST /events` → `node_visited`/`viewport_changed` → projection round-trip | A | R1 |

### Tier 3 — MVP Completeness (P2, after Walking Skeleton is green)

Edge-`+` question-card popup consumer; phrase-selection popup integrated into canvas;
real AI node content replacing `MOCK_NODE_TEXT`; `session_close` endpoint;
`GET /nodes/{id}` and `POST /summary`.

### Tier 4 — Future Milestones (M4+, intentionally deferred)

Curriculum, checkpoint, podcast, PYQ, offline sync — unchanged from `development-approach.md` §5.

---

## 5. Interface-First Protocol (Prevention)

The following protocol has been added to `development-approach.md` §6 as Day-One Discipline #10
(the list already contained items 1–9). The amendment was applied during the M3-C planning
session (2026-06-23).

**Proposed text** (for owner review):

> **10. Every SDD must include a `student-api-spec.md` parity check before closure.**
> Before any milestone SDD is marked closed, the developer must list every `student-api-spec.md`
> endpoint their feature depends on, confirm each is implemented (router + `main.py` registration),
> and sign off that no transport boundary is left phantom. This check is documented in the SDD's
> Definition-of-Done section. A phantom endpoint in a closed SDD's dependency list is a
> merge-blocking defect regardless of whether unit tests pass.

---

## 6. SDD Strategy for M3-C

**Recommendation: Single "Phase 3 M3-C Infrastructure Remediation SDD"** covering all three
seams as one increment, not three separate SDDs.

**Rationale**:
- The seams are tightly coupled: R1 (`POST /events`) is a dependency of R4/R5 (event
  emission). R1-bis (`GET /sessions/{id}`) is a dependency of R3 (mobile hydration) and
  R-choices (canvas branch rendering). A single SDD allows the test plan to sequence
  across seam boundaries and define the integration test that proves end-to-end connectivity.
- Splitting into three SDDs would require cross-SDD dependency tracking and risk leaving
  one seam "done" while another remains broken — which is exactly the pattern that created
  this situation.
- The total scope (3 new backend endpoints + 3 mobile reconciliation fixes + integration
  tests) is comparable to a single M1/M2 increment; one SDD of 120–150 lines is appropriate.

**SDD file**: `docs/planning/sdd/phase-3-m3c-infrastructure-remediation-sdd.md`
**Test plan structure** (TDD — red before green, per canon §9):
1. Red: `tests/integration/test_events_ingest.py` — `POST /events` with `node_visited`.
2. Red: `tests/integration/test_session_canvas_state.py` — `GET /sessions/{id}` returns nodes.
3. Red: `tests/integration/test_node_patch.py` — `PATCH /nodes/{id}` updates position.
4. Red: mobile `NodeToolbar` test — `onDeleted` receives full cascade payload.
5. Red: mobile `chooseOption` test — canvas state includes `node_created` fields.
6. Turn green; CI gate; device smoke.

---

## 7. Documents Requiring Amendment

| Document | Amendment required | Owner action? |
|----------|--------------------|---------------|
| `docs/planning/development-approach.md` §6 | Add Day-One Discipline #8 (Interface-First protocol) | **Yes — SoT rank #1; owner sign-off required** |
| `docs/planning/development-approach.md` §5 | Add M3-C row: "Infrastructure Remediation" as a prerequisite before M4 begins | **Yes — SoT rank #1; owner sign-off required** |
| `docs/api/student-api-spec.md` | Add `visit_source` enum values to `node_visited` spec; document canvas payload shape in `GET /sessions/{id}` | Developer-level; no owner gate |
| `docs/planning/worklog-v7.md` | Record this audit and M3-C priority shift | **Done** (see worklog 2026-06-23 entry) |

---

## 8. Closure Summary

All T1/T2 gaps identified in the 2026-06-23 audit were remediated with red-before-green TDD
(canon §9). The execution plan in the previous version of this section is complete.

| Seam | Deliverable | Status |
|---|---|---|
| A | `POST /v1/student/sessions/{id}/events` + whitelist + boundary validation | ✅ implemented, 8 integration tests green |
| B | `GET /v1/student/sessions/{id}` with `canvas_snapshot_from_events` payload | ✅ implemented, 8 integration tests green |
| C | `PATCH /v1/student/sessions/{id}/nodes/{node_id}`; `NodeToolbar` cascade reconcile; `PhraseSelectionReaderSheet` full-payload propagation | ✅ implemented, backend + mobile tests green |
| Tier 2 | `SkiaCanvas` emits `node_visited`/`viewport_changed` via `apiClient.ts` | ✅ implemented, 2 mobile tests green |
| R3 | `App.tsx` real hydration via `useSessionHydration` | ✅ implemented, 2 smoke tests green |

**Final verification** (2026-06-24):
- Backend pytest suite: **120 passed**
- Mobile Jest suite: **92 passed**
- Import linter: **green**
- `backend/` `.pyc` cleanup: **0 files**
- `student-api-spec.md` parity check: **signed off** in SDD §8

**Next action**: M4 (Curriculum entry + Supabase Auth) begins per `development-approach.md` §5 M4.
T3/T4 endpoints (session close, node summary, edges router, curriculum, checkpoint, podcast, PYQ)
remain deferred and are explicitly out of M3-C scope.
