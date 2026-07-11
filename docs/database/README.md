# Database Schema Specification Index

**Document Version**: 1.1 (M4 runtime alignment)
**Status**: Current database planning baseline  
**Scope**: Supabase PostgreSQL schema suite for the FastAPI modular monolith

---

## 1. Purpose

This folder defines the database schema specification for the Mindmap Learning Project. It covers the append-only event store, Postgres `SKIP LOCKED` job queue, tenancy/consent/curriculum tables, and the physically separate `student_rm` and `analytic_rm` read models.

These documents define the target MVP schema boundaries. Implementation must still follow the phase order in `docs/planning/development-approach.md`: Phase 1 builds only the Walking Skeleton tables/events/jobs needed for the first vertical slice, then later milestones add the remaining schema areas as they become necessary.

## 2. Hierarchy of Truth

When schema decisions conflict, apply this order:

1. `docs/planning/development-approach.md`
2. `docs/architecture/backend-architecture.md`
3. `docs/architecture/adr-log.md`
4. `docs/planning/session-path-data-contract.md`
5. `docs/api/README.md`
6. `docs/api/student-api-spec.md`
7. `docs/api/teacher-api-spec.md`
8. `docs/api/feature-endpoint-traceability.md`
9. `docs/operations/b2b-onboarding-runbook.md`
10. `docs/teacher-dashboard-specification.md`

Older drafts remain reference material only and do not override v1.3+ architecture.

## 3. Database Architecture Summary

The MVP database is Supabase PostgreSQL. The FastAPI modular monolith owns service behavior; Supabase provides PostgreSQL, Auth, and Storage.

Required database primitives:

- append-only `events` table
- Postgres `jobs` table claimed with `SELECT ... FOR UPDATE SKIP LOCKED`
- core operational tables for tenancy, membership, consent, curriculum, PYQ, and media metadata
- `student_rm` schema for student render/resume state
- `analytic_rm` schema for rebuildable teacher/research projections

## 4. Namespace Definitions

| Namespace / Schema | Purpose | Student Serializable |
|---|---|---|
| core/public operational tables | tenants, memberships, consent, curriculum, PYQ, media metadata | only student-safe subsets |
| event store | append-only raw history | no raw student access |
| jobs | async worker queue | no |
| `student_rm` | student render/resume state | yes, by endpoint contract |
| `analytic_rm` | classification, coverage, teacher projections | no |

## 5. Global Conventions

- Primary identifiers are UUIDs unless a source system requires another stable key.
- Every tenant-scoped table must carry `tenant_id`. Baseline tables received it in migration 0001;
  the legacy M4 catalog rows were forward-corrected by `0007_m4_runtime_remediation.sql` rather
  than rewriting the already-applied seed migration.
- Every event carries `event_id`, `event_type`, `event_version`, `tenant_id`, `occurred_at`, and `recorded_at`.
- Every derived analytic row carries `projection_version` and freshness metadata.
- Timestamps use timezone-aware UTC semantics.
- JSONB payloads are allowed only where the event registry or job payload contract owns schema validation.
- PII belongs in tenancy/identity/consent tables, not event payloads.

## 6. Category Invisibility Database Rule

`student_rm` must not contain analytic, dimensional, classification, coverage, teacher-support, or projection-confidence columns. This is not a convention; it is the structural enforcement mechanism from ADR-0003.

Forbidden in `student_rm` by default:

- `dimension`, `score`, `coverage`, `classification`, `entropy`, `dispersion`, `confidence`
- `gap`, `profile`, `vector`, `weight`, `propensity`, `probe`
- `teacher_followup`, `teacher_gap`, `analytic_status`, `projection_reason`

Any future learner-facing reflective feature must use a dedicated student-safe projection, not `analytic_rm` directly.

## 7. Legacy Dependencies Rejected for MVP

The database schema must not require:

- Redis
- Celery
- TimescaleDB
- Kafka or event broker infrastructure
- graph database
- shared student/analytic read model filtered by role
- direct mobile AI-provider calls

Redis/Celery may become a later queue transport through an outbox/dispatcher pattern, but Postgres remains the MVP durable queue.

## 8. Companion Documents

- `event-store-and-job-queue-schema.md`
- `core-operational-schema.md`
- `read-models-schema.md`
- `schema-traceability-and-validation.md`
