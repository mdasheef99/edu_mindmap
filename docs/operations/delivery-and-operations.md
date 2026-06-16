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
- Anthropic API key
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

- [ ] CI green: tests, import-linter, formatter
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