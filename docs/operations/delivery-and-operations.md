# Delivery and Operations Runbook

**Document Version**: 1.0 (draft)  
**Status**: Pre-implementation baseline  
**Related Documents**: `docs/planning/development-approach.md`, `docs/planning/testing-strategy.md`, `docs/architecture/backend-architecture.md`, `docs/database/README.md`

---

## 1. Purpose

This runbook defines the minimum delivery and operations plan required before the Phase 1 Walking Skeleton is deployed. It covers environments, deployment shape, migrations, secrets, backup/restore, observability, and rollback boundaries.

## 2. MVP Deployment Shape

| Component | MVP Shape |
|---|---|
| Backend API | one FastAPI container on Render |
| Worker | same codebase, separate Render worker service/entrypoint |
| Database | Supabase PostgreSQL |
| Auth | Supabase Auth |
| Storage | Supabase Storage |
| Mobile | Expo dev build on physical Android device |
| Teacher web | React + Vite when teacher milestone begins |

Render is the current MVP deployment target. This choice can be revisited only if Phase 1 deployment or worker operation exposes a concrete blocker.

## 3. Environments

| Environment | Purpose | Notes |
|---|---|---|
| local | development and tests | use local Postgres/testcontainers or `supabase start` |
| staging | deployed integration testing | Render service connected to staging Supabase project |
| production | real users | Render service connected to production Supabase project; only after phase gates pass |

Every environment must have separate database, storage, Sentry project/config, and secrets.

## 4. Migration Runbook

Migration 0001 must include non-retrofittable primitives:

- `tenant_id` on tenant-scoped tables
- version-stamp columns where applicable
- append-only `events`
- Postgres `jobs`
- base tenancy/membership/consent tables
- `student_rm` and `analytic_rm` schemas

Migration rules:

- migrations are reviewed before deploy
- no destructive production migration without backup and rollback plan
- event-store mutations are append-only
- RLS/tenant isolation tests must pass before second real tenant

## 5. Secret Handling

Secrets must not be placed in source control, command history, URLs, screenshots, logs, tickets, or docs.

Backend-only secrets include:

- Supabase service role key
- LLM provider API key
- TTS provider key
- Sentry auth tokens if used

Client-safe values must be clearly separated from backend-only secrets.

## 6. Observability Minimum

Before Phase 1 gate:

- Sentry receives a deliberate backend error
- Sentry receives a deliberate mobile error
- backend emits structured JSON logs
- LLM Gateway records token/cost counters
- worker logs job claim, completion, retry, and dead-letter transitions

## 7. Backup and Restore

Minimum requirements before real users:

- confirm Supabase automated backup settings
- document manual backup trigger process
- document restore test process for staging
- define retention expectations for pilot stage

Event store retention and consent-withdrawal handling must follow the database and consent specs.

## 8. Worker Operations

The worker uses Postgres `SKIP LOCKED`; Redis/Celery are deferred.

Operational checks:

- queued job count
- running job count
- failed/dead job count
- oldest queued job age
- classification lag for teacher projections
- podcast generation failure count

## 9. Rollback Boundaries

Application rollback may redeploy the previous container image.

Database rollback is not assumed for append-only event history. Instead:

- fix forward when possible
- replay/rebuild projections when derived data is wrong
- preserve raw events
- record significant rollback/fix-forward decisions in the worklog

## 10. Pre-Deploy Checklist

- [ ] CI green: tests, import-linter, formatter, mypy
- [ ] Render staging backend deployed
- [ ] Render staging worker deployed
- [ ] migration reviewed
- [ ] tenant isolation test passing
- [ ] event append and replay test passing
- [ ] worker claims `SKIP LOCKED` job in staging
- [ ] LLM Gateway uses backend-only credentials
- [ ] Sentry test errors received
- [ ] backup settings confirmed
- [ ] worklog updated with release candidate status

### Current verification status (2026-06-18)

- [x] migrations `0001_phase_1_walking_skeleton`, `0002_security_and_performance_remediation`, and `0003_rls_policy_helper_optimization` applied to the connected Supabase project
- [x] Supabase security advisor returns no lints for the Phase 1 schema baseline
- [x] backend local validation green: `python -m pytest tests -v` → `35 passed, 2 skipped`
- [x] backend Sentry smoke verified in the `mindmap-backend` project
- [x] worker entrypoint uses Postgres-backed queue/store adapters
- [x] GitHub Actions CI run confirmed on remote for the Phase 1/2 baseline
- [x] Phase 3 M1 deterministic local gate complete: session resume, offer-set logging, edge branching,
  deletion cascade, and event-only session-path reconstruction are green locally
- [ ] Render staging backend deployed — **deferred / operationally pending**
- [ ] Render staging worker deployed — **deferred / operationally pending**
- [ ] physical-device Expo verification recorded — **deferred / operationally pending**

### Phase 3 M1 operational deferral note (2026-06-18)

Phase 3 M1 is considered **Locally Complete / Operationally Pending**.

The following gates are explicitly deferred and must not be marked complete until live evidence is
recorded in the worklog:

1. Render backend live verification against the deployed staging API.
2. Render worker live verification proving it can claim/process a Postgres `SKIP LOCKED` job.
3. Physical-device Expo smoke against the deployed backend, including the `/v1/student/sessions`
   response and mobile Sentry smoke evidence if enabled.

This deferral allows Phase 3 M2 local development to begin, but it does not close the operational gate.

## 11. Phase 1 Verification Commands

Run these only against staging or a disposable Supabase branch; they write smoke-test rows/events.

1. Apply the current Phase 1 migration baseline (`0001` + `0002` + `0003`) to the staging database.
2. Run CI locally or on GitHub Actions: `python -m pytest tests -q`, `lint-imports`, `ruff`, `mypy`.
3. Enable the opt-in real Postgres/RLS check with `TEST_DATABASE_URL`; if the role bypasses RLS,
   treat connection as verified but do not claim pooled-RLS proof until a non-bypass app role is used.
4. Send backend Sentry smoke after deploy: `python -m app.observability.sentry_smoke` (already verified locally once on 2026-06-17).
5. Use the Expo dev build with `mobile/Phase1WalkingSkeletonScreen.tsx` on a physical Android
   device and record the `/v1/student/sessions` response plus Sentry mobile smoke evidence in the
   worklog.