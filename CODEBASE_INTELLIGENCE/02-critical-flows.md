# 02 Critical Flows

**2026-07-11 update**: M4 is closed. Bounded pre-M5 canvas stabilization adds checked, ordered
drag-end writes and recoverable branch-child placement without starting M5.

**Snapshot**: 2026-07-10. These are the current M4 production-runtime flows, not the legacy M2
smoke path.

## 1. Auth Restore, Signup, and Bootstrap

1. `mobile/m4/useM4AppFlow.ts` restores a refresh session through
   `mobile/m4/sessionStore.ts`, or the learner signs up/signs in through
   `mobile/m4/supabaseAuth.ts`.
2. Supabase returns an ES256 access token; the mobile app calls
   `POST /v1/student/auth/bootstrap` through `mobile/m4/studentApi.ts`.
3. `backend/app/api/student/auth.py` verifies the token and asks the runtime to idempotently ensure
   one B2C `student` membership in the accepted individual tenant.
4. The backend returns resolved `user_id`, `tenant_id`, role, and persisted
   `behavioral_analytics_consent_granted`. Client tenant/role input is not authoritative.
5. Sign-out calls Supabase `/auth/v1/logout` and then clears local SecureStore state.

## 2. Dashboard and Curriculum Entry

1. After bootstrap, the mobile flow calls `GET /v1/student/dashboard`, renders dashboard state, and
   then finishes the sequential curriculum endpoint calls.
2. `backend/app/api/student/dashboard.py` returns Continue Learning, recent sessions, and launch
   suggestions from tenant-scoped Postgres stores.
3. `backend/app/api/student/curriculum.py` and
   `backend/app/runtime/curriculum_workflow.py` validate the Class 10 → CBSE → Science →
   Electricity chain from API data.
4. The current M4 UI presents the accepted Electricity path. It is API-derived but is not yet a
   general-purpose arbitrary curriculum picker.

## 3. Consent-Aware Session Start

1. The learner explicitly accepts behavioral-analytics consent in
   `mobile/M4CurriculumAuthScreen.tsx`, unless bootstrap already reported an active grant.
2. `POST /v1/student/sessions` includes curriculum identifiers and
   `behavioral_analytics_consent: true`; it does not include authoritative tenancy.
3. `backend/app/runtime/session_workflow.py` resolves the full curriculum chain under the backend
   tenant, idempotently persists the first active consent grant, and appends `consent_recorded`.
4. It appends `session_started`, projects `student_rm.sessions`, then appends the deterministic
   Electricity root `node_created` event from `backend/app/generation/fixture_electricity.py`.
5. `mobile/app/App.tsx` hands the real session id/token to the canvas.

## 4. Branching and Organic-First Classification

1. Phrase selection or edge `+` requests an offer set through the student API.
2. `backend/app/runtime/offer_workflow.py` returns category-neutral options. In the M4 simulator,
   nodes/options come from the deterministic Electricity fixture; CI never needs a live model.
3. A selected choice appends choice, child `node_created`, and `edge_created` events and enqueues
   `classify`; dismissal enqueues no classify job.
4. The response does not wait for classification.
5. `backend/app/worker/phase1_worker.py` claims the Postgres job with `SKIP LOCKED`, appends
   `question_classified`, and writes `analytic_rm` only when active consent exists.

## 5. Resume and Canvas Hydration

1. `GET /v1/student/dashboard` exposes the learner's tenant-scoped recent session.
2. Resume calls `POST /v1/student/sessions/{session_id}/resume`, appending `session_resumed`.
3. `GET /v1/student/sessions/{session_id}` calls
   `backend/app/runtime/canvas_state.py::canvas_snapshot_from_events`.
4. `mobile/canvas/useSessionHydration.ts` maps the student-safe snapshot into canvas nodes/edges;
   `mobile/canvas/SkiaCanvas.tsx` renders it.
5. Runtime recreation does not lose the session because the normal API and worker share Postgres.

## 6. Node Position and Deletion

- A completed drag ends in `SkiaCanvas`, which enqueues the board-space position through
  `useNodePositionWrites.ts` into `nodePositionCoordinator.ts`. One write per node may be in flight;
  completed drags remain FIFO and are not coalesced, while different nodes may write independently.
- `mobile/canvas/apiClient.ts::patchNodePosition` rejects network/non-2xx failure and returns the
  backend acknowledgement. `node_position_workflow.py` validates accepted coordinates and appends
  `node_position_updated`; replay applies the latest durable position.
- The newest mounted-session intent remains visible while older writes settle. Hydration seeds the
  baseline but cannot overwrite newer queued/acknowledged mounted-session authority because the API
  exposes no causal position revision or event watermark.
- A failed per-node head pauses that node and exposes one neutral canvas retry boundary. Retry does
  not duplicate an active write; disposal/session replacement invalidates late callbacks, but the
  queue is intentionally not durable across unmount, restart, or termination.
- Edge-plus branch creation remains separate from initial child positioning. `EdgeOfferSetSheet`
  uses the checked PATCH directly; placement failure retains the durable branch, retries only the
  PATCH, or closes through one canonical reload. No optimistic insertion or layout fallback is
  introduced.
- `canvas_deletion.py` computes AI-path descendants, appends `edge_deleted` plus `node_deleted`, and
  replay removes them. Historical events are never updated or deleted.

## 2026-07-12 Canvas Interaction Follow-on

During a drag, only affected Skia edge geometry derives from the same SharedValues as the node;
the drag-end position lifecycle remains the sole persistence boundary. Edge-plus first press gives
local neutral feedback and starts one paired-control request; retry is single-flight. Independent
nodes may request concurrently, but only the first current completion can own the active sheet.
