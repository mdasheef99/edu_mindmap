# 07 Deployment and Operations Map

**2026-07-11 update**: the physical-device run should be restarted after the JWKS cache,
progressive dashboard, persisted consent, and remote sign-out fixes. Retest sign out -> sign in
again on the same account.

**Snapshot**: 2026-07-10.

## Services

- `render.yaml` defines the FastAPI web service and `backend/app/worker/phase1_worker.py` worker.
- Both use the same Supabase Postgres database. The API composes the durable pooled runtime; the
  worker claims Postgres `SKIP LOCKED` jobs.
- Expo/EAS owns native delivery; Expo web export includes CanvasKit support.
- Supabase provides PostgreSQL, Auth, and Storage.

## Required Configuration

Backend/API:

- `DATABASE_URL`
- `SUPABASE_URL`
- optional explicit `SUPABASE_JWT_JWKS_URL` / `SUPABASE_AUTH_URL`
- `SENTRY_DSN_BACKEND`

Worker/model path:

- `DATABASE_URL`, `SUPABASE_URL`, `JOB_QUEUE_BACKEND=postgres_skip_locked`
- `LLM_PROVIDER`, model ids, and backend-only `LLM_PROVIDER_API_KEY` when live models are enabled

Expo M4 app:

- `EXPO_PUBLIC_API_BASE_URL`
- `EXPO_PUBLIC_SUPABASE_URL`
- `EXPO_PUBLIC_SUPABASE_ANON_KEY`
- optional `EXPO_PUBLIC_SENTRY_DSN_MOBILE`

Production deployment does not consume an HS256 JWT secret. Deterministic tests inject their
fixture verifier explicitly. Never expose database, service-role, JWT fixture, or LLM provider
secrets through `EXPO_PUBLIC_*`.

## Database Operations

- Live project ref: `jbmqyxhrmcbdgardamrp`; the old Bookconnect project is out of scope.
- Applied migrations: `20260702173751 / m4_catalog_auth_seed` and
  `20260710075416 / m4_runtime_remediation`.
- Keep `backend/migrations/source_sql/0007_m4_runtime_remediation.sql` forward-only; do not edit the
  already-applied seed to hide migration history.
- A release gate must use a non-bypass app-role `TEST_DATABASE_URL` to verify pooled RLS isolation.

## Observability and Run Health

- Backend Sentry initialization: `backend/app/observability/sentry.py`.
- Mobile Sentry initialization: `mobile/app/observability/sentry.ts`.
- Monitor API health/restarts, worker completion/dead letters, Postgres/RLS errors, slow session
  replay, and LLM usage accounting.
- Production startup should fail on missing database/auth configuration. Treat any fallback to
  in-memory state as a defect.

## Current Local Device Run

As recorded in `docs/planning/worklog-v10.md`, the durable backend is bound to `0.0.0.0:8000` and
Expo Go LAN to `exp://192.168.31.183:8081`. The LAN address is process-local operational data and
must not be committed as app configuration.
