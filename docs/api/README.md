# API Documentation Source of Truth

**Document Version**: 1.1 (M4 runtime alignment)
**Status**: Current API planning baseline  
**Scope**: FastAPI modular monolith API contracts for `/v1/student` and `/v1/teacher`

---

## 1. Purpose

This folder defines the API contract surface for the Mindmap Learning Project. The current API scope covers the student and teacher routers only. Admin and internal operations are referenced as prerequisites where required, but their endpoint contracts are deferred.

## 2. Hierarchy of Truth

When documents conflict, use this order:

1. `docs/planning/development-approach.md`
2. `docs/architecture/backend-architecture.md`
3. `docs/architecture/adr-log.md`
4. `docs/planning/session-path-data-contract.md`
5. `docs/prd/master-prd.md`
6. `docs/mvp-features-specification.md`
7. `docs/teacher-dashboard-specification.md`
8. `docs/teacher-support-mvp-specification.md`
9. `docs/operations/b2b-onboarding-runbook.md`
10. Mobile feature docs for interaction-level behavior

Older broad drafts remain reference material only. They do not override v1.3+ architecture.

## 3. Service Boundary

The backend is a **FastAPI modular monolith** backed by Supabase PostgreSQL, Supabase Auth, and Supabase Storage. Supabase is the data/auth/storage platform, not the full service boundary.

The FastAPI monolith owns:

- event append and validation
- student and teacher router contracts
- tenant and role resolution
- consent checks
- LLM Gateway access
- Postgres `SKIP LOCKED` job enqueueing
- synchronous writes to `student_rm`
- asynchronous projections into `analytic_rm`

## 4. Identity, Tenant Context, and Onboarding Boundary

The product uses one student app and one `/v1/student` learning API surface. The app may present individual and institutional entry paths, but backend context resolution happens before learning-session APIs are used.

Supabase Auth verifies identity. FastAPI resolves product context after identity verification or institutional activation-code redemption, including:

- `user_id`
- `tenant_id`
- role
- active membership
- active class memberships
- consent state
- active B2C or B2B context

The mobile client must not self-assign, trust, or persist authoritative `tenant_id`, role, or membership state. It may request a context, but the backend must verify that context against server-side memberships and consent records.

After context resolution, the same `/v1/student` learning endpoints serve both B2C and B2B learners. For B2C, curriculum selection may be manual. For B2B, curriculum/class context may be pre-filled or locked by roster/class assignment. A session is always created under exactly one active tenant context and never spans tenants.

Institutional activation, roster upload, guardian/institutional consent administration and
withdrawal, teacher invitation, class management, and tenant migration contracts are upstream
admin/auth/internal operations. M4 implements one narrow B2C exception: an explicit behavioral-
analytics acknowledgement on student session start is recorded idempotently by the backend. This
folder otherwise fixes the administrative boundary and defers those endpoint contracts to future
admin/internal API docs.

## 5. Routers Covered Here

| Router | Document | Scope |
|---|---|---|
| `/v1/student` | `student-api-spec.md` | Student-safe session, canvas, AI branching, checkpoint, podcast, PYQ, and resume APIs |
| `/v1/teacher` | `teacher-api-spec.md` | Consent-gated teacher dashboard APIs backed by analytic projections |
| `/v1/admin` | Future `admin-api-spec.md` | Institution, class, roster, activation, consent-recording operations |
| `/v1/internal` | Future internal spec | Replay, tenant migration, platform support, privileged operations |

## 6. Category Invisibility

Category Invisibility is enforced structurally, not by response filtering alone.

| Surface | Read Model | Rule |
|---|---|---|
| `/v1/student` | `student_rm` | Contains render/resume state only; no dimensional or analytic columns exist |
| `/v1/teacher` | `analytic_rm` | Contains classified/projection data; tenant-scoped and consent-gated |

Student responses must never include:

- dimension names or category vocabulary
- classification scores or coverage values
- engagement vectors or gap labels
- teacher interpretations or suggested follow-ups
- propensities, probe flags, or policy internals
- raw event history or analytic projection metadata

## 7. Event-Sourced Persistence

The append-only event store is the source of truth for path reconstruction, offer-set history, deletion evidence, checkpoint signals, teacher access, and feedback. Read models are derived state.

Events are validated against an in-code registry and carry `event_version`. Derived artifacts carry relevant stamps such as `prompt_version`, `model_id`, `policy_version`, `chapter_analysis_id`, and `projection_version`.

## 8. Async Worker Lane

MVP async work uses a Postgres `jobs` table claimed with `SELECT ... FOR UPDATE SKIP LOCKED`.

| Job Type | Purpose |
|---|---|
| `classify` | Post-hoc classification after learner selection |
| `compress` | Node summary compression |
| `project` | Update analytic projections from events |
| `replay` | Rebuild classifications/projections under a new version |
| `podcast` | Script and audio generation |
| `chapter_analysis` | Chapter-analysis pipeline when enabled |

Redis, Celery, and high-scale worker fleets are deferred scale forms.

## 9. Legacy Assumptions Rejected

The current API contracts explicitly reject:

- mobile-side Anthropic/OpenAI/Perplexity calls
- client-side provider credentials or SDKs
- Supabase-only backend behavior
- Redis/Celery as MVP queue requirements
- TimescaleDB as an MVP dependency
- student raw-event export endpoints
- student-visible analytic categories
- teacher grading, ranking, mastery, or diagnosis endpoints
- teacher-assigned checkpoints in MVP
- offline queued sync or conflict-resolution APIs

## 10. Common API Conventions

- Resource-heavy REST is used for entities: sessions, nodes, edges, podcasts, classes, students, chapters.
- Workflow-style endpoints are allowed only for AI generation acts such as `POST /v1/student/offer-sets/phrase`.
- Mutations should support idempotency keys where retry is likely.
- Teacher projection responses include freshness metadata.
- Student session-state responses remain student-safe and do not embed checkpoint eligibility.

## 11. Companion Docs

- `student-api-spec.md`
- `teacher-api-spec.md`
- `feature-endpoint-traceability.md`
- Future: `admin-api-spec.md`, `internal-api-spec.md`, `docs/database-schema-specification.md`, `docs/configuration-reference.md`
