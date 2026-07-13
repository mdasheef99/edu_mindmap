# 01 System Map

**2026-07-13 update**: canvas positions now use session-scoped Zustand authority with checked
per-node FIFO delivery; edge and label drag geometry remains entirely on UI-thread SharedValues.

**Snapshot**: 2026-07-10 — M4 automated remediation complete; human gates pending.
**Authority**: `docs/planning/development-approach.md` §§5-8,
`docs/architecture/backend-architecture.md` §§3-8 and 11-12, ADR-0017, and the active M4
runtime-remediation SDD.

## Backend

The backend is an event-sourced FastAPI modular monolith with physically separate student and
analytic read boundaries.

- `backend/app/main.py` is the production composition root. With no injected test runtime it fails
  closed unless `DATABASE_URL` and `SUPABASE_URL` exist, then calls
  `backend/app/runtime/postgres_runtime.py::build_postgres_runtime`.
- `backend/app/api/` owns thin student and teacher routers.
- `backend/app/domain/` owns typed requests, responses, and event builders.
- `backend/app/runtime/` owns orchestration. `session.py` is the shared facade;
  `session_workflow.py`, `curriculum_workflow.py`, `offer_workflow.py`,
  `node_position_workflow.py`, and `canvas_deletion.py` contain workflows; `ports.py` prevents
  workflows from depending on concrete in-memory stores.
- `backend/app/events/` owns the validated append-only event registry and in-memory/Postgres stores.
- `backend/app/projections/` owns student-safe session/catalog and analytic projections.
- `backend/app/tenancy/` owns ES256/JWKS identity verification with cached JWKS clients,
  membership resolution, consent, pooled transaction context, and `SET LOCAL app.tenant_id`.
- `backend/app/workers/` and `backend/app/worker/phase1_worker.py` own Postgres
  `FOR UPDATE SKIP LOCKED` jobs and worker orchestration.
- `backend/app/generation/fixture_electricity.py` is the deterministic M4 Electricity generator.
  It deliberately does not call a live LLM.
- `backend/app/llm_gateway/` remains the only backend gateway for future live model calls and owns
  recorded-fixture mode and usage accounting.

`SessionRuntime.for_testing()` and `InMemory*` adapters remain test-only conveniences. Normal
`create_app()` routes use pooled Postgres adapters for events, jobs, memberships, consent,
catalog, and student sessions.

## Mobile

The Expo/React Native entry is `mobile/app/index.ts` → `mobile/app/App.tsx`.

- The default M4 surface is `mobile/M4CurriculumAuthScreen.tsx`.
- `mobile/m4/supabaseAuth.ts` handles email/password signup, sign-in, refresh, and Supabase remote
  sign-out calls before local clearing.
- `mobile/m4/sessionStore.ts` persists the Supabase refresh session with Expo SecureStore.
- `mobile/m4/useM4AppFlow.ts` restores auth, calls B2C bootstrap, loads dashboard before the
  sequential curriculum path, records or reuses consent state through session start, and resumes
  recent sessions.
- `mobile/m4/studentApi.ts` is the typed M4 API client. It never supplies authoritative tenancy.
- `mobile/canvas/` owns the hybrid canvas. `store.ts` holds session-scoped canonical position
  overrides, `nodePositionCoordinator.ts` owns per-node FIFO/retry/disposal, and
  `useNodePositionWrites.ts` adapts hydration and credentials. Skia edges and native overlays share
  Reanimated drag values; there is no UI-thread-to-React frame mirror.
- `mobile/app/index.web.ts` prepares CanvasKit before the web app loads.
- `EXPO_PUBLIC_SHOW_CANVAS` and `EXPO_PUBLIC_SHOW_M2_SMOKE` expose closed-milestone smoke surfaces;
  they are not the normal M4 path.

## Data and Runtime Paths

- Supabase PostgreSQL stores operational data, append-only events, jobs, `student_rm`, and
  `analytic_rm`; Supabase Auth owns credentials; Supabase Storage is reserved for media.
- Live project: `jbmqyxhrmcbdgardamrp`. Do not use the old Bookconnect project.
- Applied M4 migrations: `20260702173751 / m4_catalog_auth_seed` and
  `20260710075416 / m4_runtime_remediation`.
- Migration `backend/migrations/source_sql/0007_m4_runtime_remediation.sql` forward-adds and
  backfills missing catalog `tenant_id`, constraints, indexes, and RLS without rewriting the
  applied seed.

Runtime paths:

- Write: API → validated event append → synchronous student projection and/or durable job.
- Read: API → tenant-scoped operational/`student_rm` data or event-replayed canvas.
- Async: selected choice → classify job → worker event → consent-gated `analytic_rm` projection.
- Student APIs must never import or serialize analytic internals.
