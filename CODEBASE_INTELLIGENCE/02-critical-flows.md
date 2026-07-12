# 02 Critical Flows

**2026-07-13 update**: node movement, persistence retry, session disposal, and branch-placement
recovery are now explicit mobile lifecycle flows.

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

- Hydration seeds the current session's Zustand position authority. A finite drag-end commits once
  and enters a per-node FIFO; different nodes may write concurrently. Checked PATCH failure keeps
  the latest manual position visible and retryable.
- Session replacement/sign-out disposes old queues; deletion removes authority and prevents stale
  acknowledgement or retry from resurrecting a node. Replay still applies the latest persisted
  `node_position_updated` event.
- During drag, NodeChip, edge-plus, Skia edges, and labels consume the same UI-thread SharedValues;
  committed state continues to drive hit-testing and culling.
- `canvas_deletion.py` computes AI-path descendants, appends `edge_deleted` plus `node_deleted`, and
  replay removes them. Historical events are never updated or deleted.

## 7. Branch Placement Recovery

Choice selection creates the child branch once. Its separate checked position PATCH may be retried
without repeating creation, or the sheet closes through one reload boundary. Edge-plus controls
are single-flight with neutral retry feedback; only the first current-generation completion owns
the active offer sheet.
