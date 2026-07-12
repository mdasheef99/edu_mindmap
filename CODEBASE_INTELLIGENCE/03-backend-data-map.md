# 03 Backend and Data Map

**2026-07-11 update**: M4 is closed. The bounded canvas position lifecycle changes only mobile
delivery/feedback around the existing event-sourced node-position endpoint; backend contracts,
schemas, and migrations are unchanged.

**Snapshot**: 2026-07-10.
**Primary authority**: `docs/architecture/backend-architecture.md` §§5-8 and 11-12.

## API and Runtime Composition

- FastAPI routers live in `backend/app/api/`; `backend/app/main.py` wires them to one runtime in
  `app.state.session_runtime`.
- Normal startup requires `DATABASE_URL` and `SUPABASE_URL` and builds
  `PostgresSessionRuntime` through `backend/app/runtime/postgres_runtime.py`.
- Tests inject `SessionRuntime.for_testing()`; an in-memory test passing is not evidence of live
  durability.
- Mobile API calls live in `mobile/m4/studentApi.ts` for M4 and `mobile/canvas/apiClient.ts` for
  canvas operations.
- `patchNodePosition` is a checked typed helper: network and non-2xx failures reject, while success
  returns the accepted node id and coordinates. It sends no tenant id; the authenticated backend
  resolves tenancy and appends through the existing node-position workflow.

## Postgres Adapters

- `backend/app/tenancy/postgres_pool.py`: pooled connection/transaction proxy.
- `backend/app/tenancy/postgres_context.py`: `SET LOCAL app.tenant_id` helper.
- `backend/app/events/postgres_store.py`: append-only events.
- `backend/app/workers/postgres_queue.py`: `FOR UPDATE SKIP LOCKED` jobs.
- `backend/app/tenancy/postgres_memberships.py`: backend-owned membership bootstrap/resolution.
- `backend/app/tenancy/postgres_consent.py`: durable consent entity state.
- `backend/app/projections/postgres_catalog.py`: public M4 catalog reads.
- `backend/app/projections/curriculum_postgres.py`: Phase 2 curriculum reads.
- `backend/app/projections/postgres_student_sessions.py`: durable student session projection.
- `backend/app/projections/postgres_question_classifications.py`: consent-gated analytic output.

Every tenant-scoped query must use the backend-resolved tenant. The pooled runtime opens a
transaction, sets the tenant GUC locally, performs the operation, and commits or rolls back so
tenant state cannot leak across pooled requests. RLS is the database backstop.

## Auth and Consent

- Supabase Auth owns credential identity.
- `backend/app/tenancy/membership_auth.py` verifies live Supabase ES256 tokens with JWKS and issuer
  checks through a cached JWKS client. `SUPABASE_JWT_SECRET` exists only for deterministic HS256
  local/test fixtures.
- `backend/app/tenancy/auth.py` resolves authenticated requests to server-owned membership context.
- `POST /v1/student/auth/bootstrap` idempotently creates the M4 B2C membership in the configured
  individual tenant and reports active behavioral-consent state; mobile tenant/role claims are
  ignored.
- Session start records the explicit B2C behavioral-analytics acknowledgement as both an
  append-only event and a durable consent entity. Analytic worker writes remain consent-gated.

## Schemas and Migrations

- `public`: operational tables, events, jobs, memberships, consent, and M4 launch catalog.
- `curriculum`: Phase 2 chapter content, segments, concepts, and concept edges.
- `student_rm`: student-safe session state only.
- `analytic_rm`: classifications and future teacher/research projections; never read by student API.
- `backend/migrations/source_sql/0007_m4_runtime_remediation.sql` adds/backfills missing catalog
  `tenant_id`, constraints, indexes, and RLS. Live readback on 2026-07-10 found `tenant_id` and RLS
  enabled on all 15 audited operational/catalog/read-model tables.

## Jobs, AI, and Storage

- The MVP queue is Postgres only; `JOB_MAX_ATTEMPTS=5` dead-letters repeated failures.
- Selected offer-set choices enqueue classification asynchronously; generation never imports or
  waits for classification.
- M4 generation is deterministic fixture-backed. Future/live providers must pass through
  `backend/app/llm_gateway/`, with recorded fixtures in CI and usage accounting from the first call.
- Supabase Storage is the planned byte store for podcast/media artifacts; database rows retain
  metadata and authorization context.

## Closed M4 Operational Evidence

The pooled non-bypass app-role cross-tenant isolation test passed before M4 closure. The bounded
canvas position lifecycle changes no tenancy, schema, migration, or backend composition behavior.
