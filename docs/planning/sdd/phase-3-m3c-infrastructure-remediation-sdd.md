# Phase 3 M3-C Infrastructure Remediation — Software Design Document (SDD)

**Document Version**: 1.0
**Status**: Closed — locally complete (2026-06-24)
**Phase / milestone**: Phase 3 — M3-C (prerequisite gate for M4)
**Owner**: (developer)
**Live tracker**: `docs/planning/worklog-v7.md`
**RCA source**: `docs/planning/infrastructure-remediation-rca.md`

---

## 1. Increment Identity

| Field | Value |
|---|---|
| Increment name | Walking Skeleton transport closure: event ingest, canvas hydration, write-back |
| Phase / milestone | Phase 3 — M3-C |
| Status | Closed — locally complete (2026-06-24) |

**Goal**: close the three "compute-ready, transport-missing" seams found in the 2026-06-23
infrastructure audit (RCA §3). After this increment the mobile client can emit events to the
server (Seam A), hydrate canvas state on session resume (Seam B), and persist node positions
and reconcile cascade deletions without local-only workarounds (Seam C). This is the required
gate before M4 (Curriculum entry + Supabase Auth) begins.

---

## 2. Source-of-Truth References

- `development-approach.md` §5 M3-C gate; §6 #10 (Discipline #10 parity check).
- `student-api-spec.md` §5 (`POST /events`, `GET /sessions/{id}`); §6 (`PATCH /nodes/{id}`).
- `session-path-data-contract.md` §6 (node contract), §8 (interaction event contract).
- `infrastructure-remediation-rca.md` §2 (G1–G7 gap registry), §4 (Tier 1/2 fix plan).
- `backend-architecture.md` §6 (event registry — all appends validate against registry).
- `adr-log-02.md` ADR-0013 (Hybrid Canvas; `onTransformEnd` write-once-on-end rule).
- `configuration-reference.md` §3 (`VIEWPORT_EVENT_THROTTLE_MS`, `CANVAS_MIN_ZOOM`,
  `CANVAS_MAX_ZOOM`, `NODE_POSITION_PERSIST_MODE=drag_end`).
- `00-canon.md`: Category Invisibility, Event Sourcing, Organic-First, red-tests-first.

---

## 3. Scope

### In Scope — Tier 1 (P1 Walking Skeleton)

| Ref | Description | Gap |
|-----|-------------|-----|
| R1 | New `POST /v1/student/sessions/{id}/events` endpoint with whitelist + boundary type/enum validation | G2 |
| R1-bis | New `GET /v1/student/sessions/{id}` returning `StudentSessionWithCanvas` via `canvas_snapshot_from_events` | G3 |
| R2 | New `PATCH /v1/student/sessions/{id}/nodes/{node_id}` for position persistence; emits `node_position_updated` v1 | new phantom |
| R2-fix | `NodeToolbar.confirmDelete`: consume full `NodeDeletionResponse`; pass `deleted_node_ids`/`deleted_edge_ids` to `onDeleted` | G1 |
| R-choices | `PhraseSelectionReaderSheet.chooseOption`: propagate full `node_created`/`edge_created` payload via `onBranchCreated` | G1-v |
| R3 | `App.tsx`: replace `DEV_NODES`/`DEV_EDGES`/`DEV_TRANSFORM` with `GET /sessions/{id}` call | G3 mobile side |

### In Scope — Tier 2 (P1 completeness — event emission)

| Ref | Description | Gap |
|-----|-------------|-----|
| R4 | `SkiaCanvas.handleTap → selectNode`: emit `node_visited` via `POST /events` | G4 |
| R5 | `SkiaCanvas.onTransformEnd`: emit `viewport_changed` throttled at `VIEWPORT_EVENT_THROTTLE_MS` | G5 |
| G7 | Integration test suites TA / TB / TC verifying event→projection round-trips | G7 |

### Out of Scope (deferred — do not build in M3-C)

- `POST /sessions/{id}/close`, `GET /nodes/{id}`, `POST /nodes/{id}/summary` — Tier 3.
- Manual-reference edge create/delete endpoints — no edges router; deferred per ADR-0013.
- `NodeChip` real AI content (replaces `MOCK_NODE_TEXT`) — Tier 3.
- `SkiaCanvas.tsx` NodeChip refactor (372-line housekeeping) — deferred to M4 cleanup.

---

## 4. Seam A — Event Ingest: `POST /sessions/{id}/events`

### 4.1 New file: `backend/app/api/student/events.py`

Router prefix `/v1/student`, tags `["student"]`.

**Client-event whitelist** (all others → `400 Bad Request`):

| Event type | Version | Boundary validation (beyond `validate_event` presence checks) |
|---|---|---|
| `node_visited` | 1 | `visit_source` ∈ `{"tap", "edge_plus", "session_resume"}` |
| `viewport_changed` | 1 | `scale` is numeric ∈ `[CANVAS_MIN_ZOOM, CANVAS_MAX_ZOOM]`; `visible_node_ids` is a list |

Worker-only types from `client` producer → `403 Forbidden` (enforced by `validate_event`).

**Request body**: `{ "events": [ <event_envelope>, … ] }` — batch, 1–20 events per call.
**Response** `202 Accepted`: `{ "accepted": N, "rejected": [{ "index": i, "reason": "…" }] }`.
Partial acceptance: valid events in the batch are appended even if siblings are rejected.

**Registration**: add `from app.api.student.events import router as events_router` and
`app.include_router(events_router)` to `backend/app/main.py`.

**Import-linter constraint**: `events.py` may import from `app.domain.student` and `app.events`
only — zero analytic imports (Category Invisibility).

### 4.2 New event type in `backend/app/events/registry.py`

`node_position_updated` v1 (used by Seam C PATCH; **not** in the client-batch whitelist):
- `allowed_producers`: `frozenset({"client"})`
- `required_fields`: `COMMON_REQUIRED_FIELDS | {"actor_user_id", "student_id", "session_id", "node_id"}`
- `required_payload_fields`: `{"node_id", "session_id", "position_x", "position_y"}`

---

## 5. Seam B — Canvas Hydration: `GET /sessions/{id}`

### 5.1 New helper: `canvas_snapshot_from_events` in `backend/app/runtime/canvas_state.py`

Add alongside `active_canvas_from_events` (file currently 99 lines; stays under 150 after addition).

```python
def canvas_snapshot_from_events(
    events: list[dict[str, Any]],
    *,
    session_id: UUID,
    tenant_id: UUID,
    student_user_id: UUID,
) -> dict[str, Any]:
    """Return {"nodes": [...], "edges": [...]} for GET /sessions/{id}.

    Replays node_created, edge_created, edge_deleted, node_deleted,
    and node_position_updated in temporal order. node_position_updated
    supersedes the initial position for any node_id it names.
    Returns only student-safe (student_rm) fields — no analytic data.
    """
```

Return shape:
```
{
  "nodes": [{"node_id": str, "node_type": str, "content": str,
             "position_x": float|None, "position_y": float|None,
             "thread_context_id": str|None}],
  "edges": [{"edge_id": str, "source_node_id": str, "target_node_id": str,
             "edge_kind": str, "label": str|None}]
}
```

`position_x`/`position_y` default to `None` until a `node_position_updated` event is
replayed. The mobile client applies d3-hierarchy layout for nodes with `None` positions.

### 5.2 New Pydantic models in `backend/app/domain/student/sessions.py`

```python
class CanvasNodeSnapshot(BaseModel):
    node_id: UUID
    node_type: str
    content: str
    position_x: float | None = None
    position_y: float | None = None
    thread_context_id: UUID | None = None

class CanvasEdgeSnapshot(BaseModel):
    edge_id: UUID
    source_node_id: UUID
    target_node_id: UUID
    edge_kind: str
    label: str | None = None

class CanvasSnapshot(BaseModel):
    nodes: list[CanvasNodeSnapshot]
    edges: list[CanvasEdgeSnapshot]

class StudentSessionWithCanvas(StudentSession):
    canvas: CanvasSnapshot
```

`CanvasNodeSnapshot` must never include analytic fields (Category Invisibility invariant).

### 5.3 New endpoint in `backend/app/api/student/sessions.py`

```python
@router.get("/sessions/{session_id}", response_model=StudentSessionWithCanvas)
def get_session(session_id: UUID, request: Request,
                auth: AuthContext = Depends(get_auth_context)) -> StudentSessionWithCanvas:
```

Handler logic:
1. Fetch `StudentSession` from `runtime.student_sessions` for `(session_id, auth.tenant_id, auth.user_id)` — `404` if absent.
2. Call `canvas_snapshot_from_events(runtime.event_store.events, session_id=..., tenant_id=..., student_user_id=...)`.
3. Construct `CanvasSnapshot` from the returned dict.
4. Return `StudentSessionWithCanvas(canvas=canvas_snapshot, **session.model_dump())`.

**Router ordering**: `GET /sessions/{session_id}` must be declared **after**
`GET /sessions/recent` in the router file to prevent FastAPI matching `"recent"` as a UUID.

---

## 6. Seam C — Write-back Reconciliation

### 6.1 G1 fix — `mobile/canvas/NodeToolbar.tsx`

`onDeleted` prop type changes from `(node: CanvasNode) => void` to
`(result: NodeDeletionResponse) => void`.

```ts
// Before — discards response body (G1)
if (response.ok) onDeleted?.(node);

// After — consume full cascade payload
if (response.ok) {
  const body: NodeDeletionResponse = await response.json();
  onDeleted?.(body);
}
```

`SkiaCanvas` reconcile handler update: remove all `result.deleted_node_ids` from local
`nodes` state and all `result.deleted_edge_ids` from local `edges` state atomically.

### 6.2 G1-v fix — `mobile/PhraseSelectionReaderSheet.tsx`

`onBranchCreated` prop type changes from `(nodeId: string) => void` to
`(result: OfferChoiceResponse) => void`.

```ts
// Before — partial (G1-v)
if (body.child_node_id) onBranchCreated?.(body.child_node_id);

// After — full payload
if (response.ok) {
  const body: OfferChoiceResponse = await response.json();
  onBranchCreated?.(body);
}
```

Canvas consumer inserts `body.node_created` into local nodes and `body.edge_created` into
local edges when both are present (branch node rendered on-canvas immediately).

### 6.3 New endpoint — `PATCH /v1/student/sessions/{session_id}/nodes/{node_id}`

Add to `backend/app/api/student/nodes.py`.

Request body:
```python
class NodePositionUpdate(BaseModel):
    position_x: float
    position_y: float
```

Handler: validate `position_x`/`position_y` are finite floats; build and append a
`node_position_updated` v1 event (§4.2); return `{ "node_id": ..., "position_x": ...,
"position_y": ... }` with `200 OK`. Return `404` if node not found in active canvas.

Mobile call site: `SkiaCanvas` — fire after drag commit (existing `onTransformEnd` hook,
`NODE_POSITION_PERSIST_MODE=drag_end`, ADR-0013 §7 write-once-on-end rule).

---

## 7. Tier 2 — Mobile Event Emission (G4, G5)

### 7.1 `node_visited` — G4

**Trigger**: `SkiaCanvas.handleTap → hitTestNode → selectNode` (existing M3-B F3 flow).
**Fire-and-forget** after `selectNode(hit.node_id)`:

```ts
postClientEvent(apiBaseUrl, sessionId, authorizationToken, {
  event_type: "node_visited", event_version: 1,
  node_id: hit.node_id, session_id: sessionId,
  payload: { node_id: hit.node_id, session_id: sessionId, visit_source: "tap" }
});
```

`postClientEvent` is a small shared helper (`mobile/canvas/apiClient.ts`, new) that
wraps `POST /sessions/{id}/events`. It is fire-and-forget; the gesture handler does not
`await` it. All required envelope fields (`event_id`, `tenant_id`, `occurred_at`, etc.)
are constructed client-side before posting.

### 7.2 `viewport_changed` — G5

**Trigger**: `onTransformEnd` in `SkiaCanvas` (write-once-on-end per ADR-0013 §7).
**Throttled** at `VIEWPORT_EVENT_THROTTLE_MS` (default 1000ms, `configuration-reference.md` §3):

```ts
throttledPostViewport(apiBaseUrl, sessionId, authorizationToken, {
  event_type: "viewport_changed", event_version: 1,
  session_id: sessionId,
  payload: { session_id: sessionId, scale, translate_x, translate_y,
             visible_node_ids: Array.from(visIds) }
});
```

---

## 8. Definition-of-Done — Discipline #10 Parity Check

Per `development-approach.md` §6 #10, the following parity table must be signed off before
this SDD is marked closed. Every row must be ✅.

| `student-api-spec.md` endpoint | Router file | `main.py` registration |
|---|---|---|
| `POST /sessions/{id}/events` | `events.py` (new, this increment) | ✅ added in R1 |
| `GET /sessions/{id}` | `sessions.py` (new handler, this increment) | ✅ already registered router |
| `PATCH /sessions/{id}/nodes/{node_id}` | `nodes.py` (new handler, this increment) | ✅ already registered router |
| `DELETE /sessions/{id}/nodes/{node_id}` | `nodes.py` | ✅ existing |
| `POST /sessions/{id}/resume` | `sessions.py` | ✅ existing |
| `POST /sessions` | `sessions.py` | ✅ existing |
| `GET /sessions/recent` | `sessions.py` | ✅ existing |
| `POST /offer-sets/phrase` | `offer_sets.py` | ✅ existing |
| `POST /offer-sets/edge` | `offer_sets.py` | ✅ existing |
| `POST /offer-sets/{id}/choices` | `offer_choices.py` | ✅ existing |

Tier 3/T4 endpoints (`/close`, `/summary`, edges, curriculum, checkpoint, podcast, PYQ)
remain phantom and are explicitly out of M3-C scope — do not block closure.

Mobile `fetch` parity: every `fetch` URL introduced in R4/R5 (`POST /events`) and R3
(`GET /sessions/{id}`) must resolve to a registered router path — verified by test TA-M1,
TA-M2, and the R3 smoke test.

---

## 9. TDD Test Plan — Red-Before-Green (canon §9)

All test files must exist with failing tests **before** any production code is written.
Run the full suite after each seam is green; do not merge until all three seams pass.

### 9.1 Seam A — `tests/integration/test_events_ingest.py`

| ID | Scenario | Expected |
|----|----------|----------|
| TA-1 | POST valid `node_visited` envelope | `202`, `accepted=1` |
| TA-2 | POST valid `viewport_changed` envelope | `202`, `accepted=1` |
| TA-3 | POST unknown event type | `400` |
| TA-4 | POST `question_classified` from `client` producer | `403` |
| TA-5 | POST `node_visited` with `visit_source="invalid_value"` | `400` |
| TA-6 | POST `viewport_changed` with `scale` outside `[CANVAS_MIN_ZOOM, CANVAS_MAX_ZOOM]` | `400` |
| TA-7 | Batch of 3: 2 valid + 1 invalid `visit_source` | `202`, `accepted=2`, `rejected=[{index:2}]` |
| TA-8 | POST `node_visited` → verify event store length increases by 1 | event count += 1 |

### 9.2 Seam B — `tests/integration/test_session_canvas_state.py`

| ID | Scenario | Expected |
|----|----------|----------|
| TB-1 | GET `/sessions/{id}` — no canvas events yet | `200`, `canvas.nodes=[]`, `canvas.edges=[]` |
| TB-2 | GET after a `node_created` event appended | `canvas.nodes` has 1 entry with correct `node_id`, `content` |
| TB-3 | GET after `node_created` + `node_deleted` | `canvas.nodes=[]` |
| TB-4 | GET after `edge_created` + `edge_deleted` | `canvas.edges=[]` |
| TB-5 | GET after `node_position_updated` | `canvas.nodes[0].position_x` matches PATCH value |
| TB-6 | GET with wrong `auth.tenant_id` | `404` |
| TB-7 | Category Invisibility: response JSON contains no analytic keys | assert no forbidden keys |
| TB-8 | `GET /sessions/recent` still resolves correctly (router ordering regression) | `200` list response |

### 9.3 Seam C backend — `tests/integration/test_node_patch.py`

| ID | Scenario | Expected |
|----|----------|----------|
| TC-1 | PATCH `/nodes/{id}` with valid `position_x`, `position_y` | `200`, response echoes both values |
| TC-2 | PATCH appends `node_position_updated` event to store | event store length += 1; `event_type=="node_position_updated"` |
| TC-3 | PATCH with non-finite float | `422` validation error |
| TC-4 | PATCH on wrong `session_id` or non-existent `node_id` | `404` |

### 9.4 Seam C mobile — extend `mobile/canvas/__tests__/nodeToolbar-test.tsx`

| ID | Scenario | Expected |
|----|----------|----------|
| TC-M1 | `confirmDelete` mock returns `{ deleted_node_ids: ["n1","n2"], deleted_edge_ids: ["e1"] }` | `onDeleted` called with full object, not just the tapped node |
| TC-M2 | `onDeleted` propagation in `SkiaCanvas` | nodes `"n1"`, `"n2"` removed from canvas state; edge `"e1"` removed |

### 9.5 Seam C mobile — extend `mobile/app/__tests__/PhraseSelectionReaderSheet-test.tsx`

| ID | Scenario | Expected |
|----|----------|----------|
| TC-M3 | `chooseOption` response has `node_created` + `edge_created` | `onBranchCreated` called with full body object |
| TC-M4 | Category Invisibility: `chooseOption` request body has no analytic fields | assert no forbidden keys in POST body |

### 9.6 Seam A mobile — extend `mobile/canvas/__tests__/skiaCanvas-test.tsx`

| ID | Scenario | Expected |
|----|----------|----------|
| TA-M1 | Node tap with `sessionId` prop set → `POST /events` fired | fetch called with URL containing `/events`; body `event_type=="node_visited"`, `visit_source=="tap"` |
| TA-M2 | `onTransformEnd` with `sessionId` → `POST /events` fired | fetch called; payload `event_type=="viewport_changed"`; `scale`/`translate_x`/`translate_y` match committed transform |

---

## 10. Traceability

| Work item | RCA gap ID | `student-api-spec.md` § | `session-path-data-contract.md` § |
|---|---|---|---|
| `POST /events` endpoint (R1) | G2 — phantom, Seam A | §5 row 5 | §8 (interaction event contract) |
| `GET /sessions/{id}` endpoint (R1-bis) | G3 — phantom, Seam B | §5 row 3 | §5 (session contract), §6 (node contract) |
| `canvas_snapshot_from_events` helper | G3 — hydration depth | §5 session-state note | §6 (layout/system metadata needed to reopen) |
| `CanvasNodeSnapshot` / `StudentSessionWithCanvas` models | G3 — model gap | §5 | §6 |
| `PATCH /nodes/{id}` endpoint (R2) | new phantom, Seam C | §6 row 3 | §6 (layout/system metadata) |
| `node_position_updated` v1 event type | new (supports Seam C) | §6 (PATCH emits canvas event) | §6 (position) |
| `NodeToolbar` cascade reconciliation (R2-fix) | G1 — full discard | §6 (DELETE response) | §10 (deletion cascade) |
| `chooseOption` full-payload propagation (R-choices) | G1-v — partial reconcile | §8 (offer choice response) | §9 (offer-set and thread-context) |
| `node_visited` emission (R4) | G4 | §5 (`POST /events` whitelist) | §8 (node viewed/visited) |
| `viewport_changed` emission (R5) | G5 | §5 (`POST /events` whitelist) | §8 (viewport changes) |
| `App.tsx` real hydration (R3) | G3 mobile side | §5 (`GET /sessions/{id}`) | §5 (resume behavior) |
| Integration test suites TA / TB / TC | G7 — no boundary tests | §5–§6 | §8 |
| Discipline #10 parity check (§8 of this SDD) | root cause (RCA §3.2) | all §5–§6 | — |

---

## 11. Definition of Done — M3-C Closure

All red tests written before production code; all three seams green end-to-end. Verification
results: backend pytest **120 passed**, mobile Jest **92 passed** (17 suites), import-linter green,
`DEV_NODES`/`DEV_EDGES`/`DEV_TRANSFORM` fixtures removed from `App.tsx`, `student-api-spec.md`
parity check signed off, Category Invisibility verified, and 0 `.pyc` files remain in `backend/`.
M3-C is the prerequisite gate for M4 (Curriculum entry + Supabase Auth).

---

## 12. Post-Closure Addendum — Composition Root Remediation (2026-06-25)

**Status**: Complete. Recorded in `docs/planning/worklog-v8.md` (2026-06-25 entry).

After M3-C closed, `backend/app/main.py` remained at 416 lines — a "God Object" combining
the `SessionRuntime` DI container, membership store, JWT auth, and the FastAPI composition root.
This violated the 300–350-line canon limit and was remediated as a pre-M4 housekeeping step.

**Logic distributed**:

| Destination | Responsibility | Lines |
|---|---|---|
| `app/tenancy/memberships.py` | `InMemoryMembershipStore` | 22 |
| `app/tenancy/membership_auth.py` | `resolve_membership_auth` (JWT + role) | 41 |
| `app/runtime/session.py` | `SessionRuntime` thin DI facade + `for_testing` | 304 |
| `app/runtime/session_workflow.py` | Session lifecycle orchestration | 117 |
| `app/runtime/curriculum_workflow.py` | Chapter lookup + teacher render | 56 |
| `app/runtime/node_position_workflow.py` | Position update orchestration | 65 |
| `app/main.py` (retained) | Pure composition root (app, middleware, routers, re-exports) | **58** |

**Invariants preserved**:
- Backward compatibility: `from app.main import SessionRuntime, InMemoryMembershipStore,
  create_app` works unchanged via `__all__` re-exports. Zero modifications to the 15+
  integration test files or `dev_smoke_bootstrap.py`.
- **4/4 import-linter contracts kept** — Category Invisibility intact.
- **121/121 pytest passed** — full regression suite, zero failures.
- 0 `.pyc` files after cleanup.
