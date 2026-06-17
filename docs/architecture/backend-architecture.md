# Backend Architecture Specification

**Document Version**: 1.0 (draft)
**Status**: Proposed
**Related Documents**: `docs/system-architecture.md`, `docs/architecture/llm-pipeline.md`,
`docs/architecture/data-collection.md`, `docs/measurement-and-experimentation.md`,
`docs/chapter-analysis-pipeline-specification.md`, `docs/teacher-support-mvp-specification.md`,
`docs/teacher-access-control-specification.md`, `docs/planning/backend-mvp-strategy.md`,
`docs/planning/session-path-data-contract.md`

---

## 1. Purpose

This document specifies the backend as an **event-sourced modular monolith with CQRS-style read
separation and an async worker lane**, and extends it with **multi-tenant institutional (B2B)
support** alongside individual (B2C) accounts.

It refines — and where noted, supersedes — the application/data-layer sketches in
`docs/system-architecture.md`. It respects the MVP guardrails in
`docs/planning/backend-mvp-strategy.md`: where this document describes scale-oriented
infrastructure (Redis, worker fleets), §8 defines the MVP-light form that ships first.

---

## 2. Architectural Principles

Each principle is derived from a structural property of the framework. They are not preferences;
violating any of them breaks a documented product guarantee.

| # | Framework property | Architectural consequence |
|---|--------------------|---------------------------|
| 1 | The framework is revisable by design (post-hoc classification, provisional categories) | **Append-only event store**; every analytic artifact is a rebuildable projection. Aggregates are never the source of truth. |
| 2 | Category invisibility to students is mandatory | **Two physically separate read models** (student vs analytic) with separate schemas, storage keys, and API routers. Filtering one shared model at the response layer is prohibited. |
| 3 | Classification is post-hoc and never blocks the student | **Async worker lane** for classification, compression, projections, and replay. The synchronous path contains only what the student is waiting for. |
| 4 | Claims are probabilistic and condition-dependent | **Version stamping is a first-class column** on every event and derived row (`policy_version`, `prompt_version`, `model_id`, `chapter_analysis_id`, `projection_version`). |
| 5 | The product is sold to schools as well as individuals | **Tenancy is a first-class column** (`tenant_id`) on every row from the first migration. Retrofitting multi-tenancy onto an event store is not feasible; it ships in migration 0001. |

---

## 3. Topology

```
                ┌──────────────────────────────────────────────────────┐
                │              Modular monolith (FastAPI)              │
                │                                                      │
 Student app ──▶│  api/student ──▶ generation ──▶ llm_gateway          │
 (RN mobile)    │       │                              │               │
                │       ▼                              ▼               │
 Teacher/admin ─▶  api/teacher    events (append-only event store)     │
 (web)          │  api/admin           │                               │
                │       ▲              ▼  job queue                    │
                │       │   workers: classify · compress · project ·   │
                │       │             replay · podcast                 │
                │       │              │                               │
                │       └── analytic projections ◀┘                    │
                └──────────────────────────────────────────────────────┘
                  Supabase PostgreSQL (events + both read models + queue)
                  Supabase Auth (identity)  ·  Supabase Storage (media)
```

**Deployment**: one deployable unit (single container/service) plus a worker process running the
same codebase with a different entrypoint. Both read the same Postgres. No microservices; no
serverless-per-function. Module boundaries (§4) are logical, enforced by import rules, and become
extraction seams only if scale demands it later.

**Phase 1 implementation note**: the current backend worker entrypoint is already wired to the
Postgres-backed queue/store adapters described in §8 and §9. Local validation is green and the
backend Sentry smoke has been received; remaining operational proof is the remote CI run plus
Render/mobile deployment verification.

**Technology** (consistent with `docs/system-architecture.md` Key Technical Decisions):

| Concern | Choice | Notes |
|---------|--------|-------|
| API runtime | Python / FastAPI | Single app, multiple routers (§11) |
| Database | PostgreSQL (Supabase) | Events, read models, queue, tenancy via RLS |
| Identity | Supabase Auth | JWT carries `user_id`; role and tenant resolved server-side (§5.4) |
| Job queue (MVP) | Postgres table + `SELECT ... FOR UPDATE SKIP LOCKED` | No new infrastructure; see §8.1 |
| Job queue (scale) | Redis + worker pool | Deferred per `docs/planning/backend-mvp-strategy.md` §10 |
| LLM access | Direct provider API via the `llm_gateway` module | Provider/model ids are environment-configured; no LangChain; structured output mandatory |
| Media | Supabase Storage + platform players | Podcast audio, uploaded images |

---

## 4. Module Boundaries and Import Rules

The codebase is one Python package with strictly layered modules. Import rules are enforced with
`import-linter` (contracts in CI); a build that violates them fails.

```
app/
  domain/            # Pure types and invariants. Imports nothing below.
    student/         #   student-facing types — NO dimensional fields exist here
    analytic/        #   dimensional vectors, coverage, audit types
    tenancy/         #   tenant, institution, class, membership types
  events/            # Event store: append API, event type registry, schemas
  projections/       # Projection builders: event log → read models
  generation/        # Stage 1 runtime: prompt assembly (Section A only), offer sets
  classification/    # Stage 2 runtime: scoring, entropy/median arithmetic
  chapter_analysis/  # P0–P11 pipeline (docs/chapter-analysis-pipeline-specification.md)
  llm_gateway/       # Single chokepoint for all model calls
  workers/           # Job handlers: classify, compress, project, replay, podcast
  api/
    student/         # Student-facing routers — may import domain/student only
    teacher/         # Teacher-support routers — may import domain/analytic + tenancy
    admin/           # School-admin + platform-admin routers
    internal/        # Ops: replay, projection rebuild, QA tooling
  tenancy/           # Tenant resolution, membership checks, RLS session helpers
```

**Enforced contracts** (the boundary rules that carry product guarantees):

1. `api/student` **must not import** `domain/analytic`, `classification`, or `projections`
   builders that emit dimensional data. The student response types contain no dimensional
   fields, so a leak is a type error before it is a runtime bug.
2. `generation` **must not import** `classification` or read Section B/C storage keys
   (mirror of the chapter-analysis Section A rule).
3. Only `events` may write to the event store; all other modules append through its API.
4. Only `llm_gateway` may construct model API clients. `generation`, `classification`, and
   `chapter_analysis` call through it.
5. `projections` is the only writer of read-model tables; API routers are read-only on them.
6. Everything except `domain` may import `tenancy`; `domain` imports nothing.

---

## 5. Tenancy and the Institutional Model (B2B + B2C)

### 5.1 Entity model

```
tenants (1) ──< institutions (0..1 per tenant for B2B; absent for B2C)
tenants (1) ──< users (via memberships)
institutions (1) ──< classes (a.k.a. batches)
classes (M) >──< students   (class_memberships)
classes (M) >──< teachers   (teaching_assignments)
```

- **`tenants`**: the isolation unit. Two kinds: `institutional` (one school) and
  `individual` (the shared consumer tenant; see §5.5).
- **`institutions`**: school profile — name, board (CBSE/state), verification status,
  contract/billing reference, admin contacts.
- **`classes`**: a teaching group ("Class 10-B Physics", "NEET Batch A") with subject,
  grade band, and academic-year fields. Maps to the teacher-support notion of a roster.
- **`class_memberships`** / **`teaching_assignments`**: student↔class and teacher↔class
  links, with `active_from` / `active_to` (history is preserved; rosters change mid-year).


```sql
CREATE TYPE tenant_kind AS ENUM ('institutional', 'individual');

CREATE TABLE tenants (
    tenant_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kind        tenant_kind NOT NULL,
    name        TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE institutions (
    institution_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(tenant_id) UNIQUE,
    name            TEXT NOT NULL,
    board           TEXT,                    -- 'CBSE', state board code, etc.
    verified        BOOLEAN NOT NULL DEFAULT FALSE,
    billing_ref     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE classes (
    class_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(tenant_id),
    institution_id  UUID NOT NULL REFERENCES institutions(institution_id),
    name            TEXT NOT NULL,           -- 'Class 10-B', 'NEET Batch A'
    subject         TEXT,
    grade_band      TEXT,                    -- aligns with segment_key axes
    academic_year   TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE memberships (                   -- user's role within a tenant
    membership_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(tenant_id),
    user_id         UUID NOT NULL,           -- references auth.users(id)
    role            user_role NOT NULL,      -- enum from teacher-access-control spec:
                                             -- student | teacher | approved_teacher | admin
                                             -- extended with: school_admin
    active_from     TIMESTAMPTZ NOT NULL DEFAULT now(),
    active_to       TIMESTAMPTZ,             -- NULL = active
    UNIQUE (tenant_id, user_id, role)
);

CREATE TABLE class_memberships (
    class_id    UUID NOT NULL REFERENCES classes(class_id),
    student_id  UUID NOT NULL,
    tenant_id   UUID NOT NULL REFERENCES tenants(tenant_id),
    active_from TIMESTAMPTZ NOT NULL DEFAULT now(),
    active_to   TIMESTAMPTZ,
    PRIMARY KEY (class_id, student_id, active_from)
);

CREATE TABLE teaching_assignments (
    class_id    UUID NOT NULL REFERENCES classes(class_id),
    teacher_id  UUID NOT NULL,
    tenant_id   UUID NOT NULL REFERENCES tenants(tenant_id),
    active_from TIMESTAMPTZ NOT NULL DEFAULT now(),
    active_to   TIMESTAMPTZ,
    PRIMARY KEY (class_id, teacher_id, active_from)
);
```

This extends (does not replace) the `user_role` enum and `user_profiles` table in
`docs/teacher-access-control-specification.md` §3: that spec's roles remain the capability
hierarchy; `memberships` scopes a role to a tenant, and adds `school_admin` (institution-level
administration without platform-admin powers).

### 5.2 School-managed student onboarding

Two flows, both producing ordinary student accounts that differ only in how identity and consent
were established:

**Roster bulk enrollment (primary B2B flow)**
1. School admin uploads a roster (CSV: name, class, parent contact) via `api/admin`.
2. Backend creates **provisional accounts**: a `users` row, a `memberships` row
   (`role = student`), and `class_memberships` rows. No login credentials yet.
3. Per-student **activation codes** (or parent-phone OTP links) are generated for distribution
   by the school. First login binds the credential and records the consent artifact (§12).
4. Roster changes (student joins/leaves a class) close and open `class_memberships`
   intervals; history is never deleted, because analytic projections must be able to answer
   "who was in this class during this window".

**Invite flow (small schools / pilots)**: teacher generates a class invite code; student signs up
B2C-style, enters the code, and an approval by the teacher creates the membership rows.

**Teacher onboarding**: school admin invites teachers by email; accepting creates a
`memberships(role=teacher)` row. Credential verification (per the access-control spec) remains a
platform-level step; an institutional membership does not bypass it.

### 5.3 Tenant-scoped data isolation

- **Every table carries `tenant_id`** — events, read models, sessions, nodes, podcasts, all of it.
  No exceptions, including tables that "obviously" belong to one tenant via a join.
- **Postgres Row-Level Security** on every table: policies compare `tenant_id` against the
  request's resolved tenant (set per-connection via `SET LOCAL app.tenant_id = ...` by the
  `tenancy` module). Supabase RLS is already part of the chosen stack.
- **Phase 1 migration baseline**: migrations `0001_phase_1_walking_skeleton`,
  `0002_security_and_performance_remediation`, and `0003_rls_policy_helper_optimization` are the
  current Supabase baseline. They enable RLS for all Phase 1 tables, fix function search paths,
  add FK/tenant indexes, and route policies through `(SELECT public.current_app_tenant_id())` so
  Supabase security advisor lints are clear.
- **Application-level checks are still mandatory** (RLS is the backstop, not the mechanism):
  the `tenancy` module resolves `(user_id → memberships → tenant, role, classes)` once per
  request and injects an authorization context that every router dependency consumes.
- **Teacher scope rule** (consistent with `docs/teacher-support-mvp-specification.md`): a teacher
  reads analytic data only for students with an *active* `class_membership` in a class where the
  teacher holds an *active* `teaching_assignment`. School admins see class-level aggregates for
  their institution; individual-student drill-down stays with the teaching relationship.
- **Cross-tenant reads** exist only in `api/internal` (platform operations, research aggregates)
  behind the platform `admin` role, MFA, and audit logging per the access-control spec.

### 5.4 Identity and tenant resolution

Supabase Auth JWTs identify the **user**, never the tenant. On each request the `tenancy` module
resolves active memberships. Users with multiple memberships (e.g., a teacher at a school who is
also a B2C learner) select an active context; the chosen `tenant_id` is stamped on every event the
session emits. A session never spans tenants.

### 5.5 B2C and B2B coexistence

- All individual consumers live in **one shared `individual` tenant**; their isolation unit is
  `student_id` (enforced by ownership RLS policies, as today). This avoids per-user tenant rows
  while keeping one uniform query model: *every* query is tenant-scoped, then ownership-scoped.
- Product behavior is identical across kinds — same canvas, same generation, same invisibility
  rules. The differences are confined to: who manages the account (§5.2), who may view analytic
  projections (§5.3), and the consent path (§12).
- **Migration between kinds** (a B2C student's family joins a school plan, or a student leaves a
  school): create the new membership, close the old one, and emit a `tenant_migration` event.
  Whether historical events transfer to the new tenant is a consent decision (§12), not a
  technical one; the event store supports either via re-stamping under an explicit, audited
  migration record.

---

## 6. The Append-Only Event Store

### 6.1 Schema

One table, append-only (no UPDATE/DELETE grants to the application role), partitioned by month.

```sql
CREATE TABLE events (
    event_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type      TEXT NOT NULL,            -- registry-validated, §6.2
    event_version   SMALLINT NOT NULL,        -- per-type payload schema version
    occurred_at     TIMESTAMPTZ NOT NULL,
    recorded_at     TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- Tenancy and join keys (promoted to columns for indexing)
    tenant_id       UUID NOT NULL,
    student_id      UUID,                     -- pseudonymous learner id
    session_id      UUID,
    chapter_id      TEXT,
    node_id         UUID,
    offer_set_id    UUID,

    -- Instrument-condition stamps (framework demand #4)
    policy_name     TEXT,
    policy_version  TEXT,
    prompt_version  TEXT,
    model_id        TEXT,
    chapter_analysis_id UUID,
    app_version     TEXT,
    client_platform TEXT,
    segment_key     JSONB,
    segment_schema_version TEXT,

    payload         JSONB NOT NULL            -- full event body, schema per (type, version)
) PARTITION BY RANGE (occurred_at);

CREATE INDEX ON events (tenant_id, student_id, occurred_at);
CREATE INDEX ON events (event_type, occurred_at);
CREATE INDEX ON events (offer_set_id) WHERE offer_set_id IS NOT NULL;
```

### 6.2 Event type registry

Event types are registered in code (`events/registry.py`) with a Pydantic payload schema per
`(event_type, event_version)`. Appends validate against the registry; unknown types are rejected.
Initial registry, consolidating `docs/measurement-and-experimentation.md` §4 and
`docs/architecture/data-collection.md`:

| Family | Event types |
|--------|------------|
| Offer sets | `offer_set_created`, `offer_set_impression`, `offer_set_choice` |
| Phrase flow | `phrase_selected`, `phrase_offer_set_created`, `phrase_offer_set_choice` |
| Canvas | `node_created`, `node_visited`, `node_deleted`, `edge_created` (`ai_path` vs `manual_reference` in payload), `edge_deleted` (`edge_kind` + `deletion_cause: user_action \| node_cascade` in payload — a user-removed manual link is a retraction of relational evidence, not data loss), `viewport_changed` |
| Session lifecycle | `session_started`, `session_resumed`, `app_backgrounded`, `app_foregrounded` — dwell-time projections subtract backgrounded intervals; without these, mobile backgrounding inflates dwell into a corrupted engagement signal |
| Content | `node_content_generated`, `node_summary_compressed`, `podcast_requested`, `podcast_generated` |
| Classification | `question_classified` (scores, dispersion, entropy, flags — written by the worker) |
| Reflection | `checkpoint_offered`, `checkpoint_response` (Try Now / Not Sure Yet / Snooze / Skip) |
| Outcomes | `learning_outcome` (typed, `instrument_version`) |
| Tenancy/admin | `roster_uploaded`, `membership_changed`, `consent_recorded`, `tenant_migration` |
| Teacher | `teacher_view_accessed`, `teacher_feedback` (useful / not useful) |

Payload requirements for offer-set events (options, propensities, `is_probe`, randomization ids,
latencies) are exactly as specified in `docs/measurement-and-experimentation.md` §4.2–4.6 and are
not restated here.

### 6.3 Invariants

1. **Append-only is enforced by grants**, not discipline: the application DB role has INSERT and
   SELECT on `events`, nothing else.
2. **No raw PII in payloads** (measurement spec §4.7). Names, parent contacts, and consent
   artifacts live in tenancy tables; events carry pseudonymous ids only.
3. **Aggregates are never written here.** Anything derived goes to projections (§7).
4. **Every event carries `tenant_id`** and whatever instrument stamps apply to its family;
   the registry schema makes required stamps non-nullable per type.


---

## 7. The Two Read Models

### 7.1 Student read model (`student_rm` schema)

What the mobile client needs to render and resume — nothing else.

- `sessions`, `nodes` (content, position, type), `edges` (`ai_path` | `manual_reference`),
  `node_summaries`, `podcasts`, `current_offer_sets`.
- **Contains no dimensional columns, no classification data, no coverage data — the schema
  cannot express them.** This is the structural enforcement of category invisibility: the
  student API serializes from `domain/student` types, which have no dimensional fields.
- Written synchronously for interaction state (node save must be durable before the response
  returns) and by projections for anything derived.

### 7.2 Analytic read model (`analytic_rm` schema)

Everything dimensional, derived, and teacher/research-facing. **Rebuildable from the event log
by definition** — dropping any table here loses nothing.

- `question_classifications` (median scores, dispersion, entropy, flags, all stamps)
- `student_engagement_profiles` (cumulative vectors, trajectory, velocity, gap persistence —
  per `docs/framework-design-philosophy.md` path-capture spec)
- `coverage_by_concept`, `dimensional_shift_log` (shift monitor outputs)
- `coverage_by_pair`, `realized_subgraph`, `graph_diff` (topology layer, per
  `docs/chapter-topology-specification.md` §4.4–§5 — phased; `coverage_by_pair` is Phase 1)
- `class_aggregates`, `institution_aggregates` (§7.4)
- `teacher_support_views` (the bounded MVP surface per `docs/teacher-support-mvp-specification.md`)

Every row carries `projection_version` and the `chapter_analysis_id` / `policy_version` stamps of
the events it was derived from.

### 7.3 Projection rules

1. Projections are **deterministic functions of the event log** — no projection reads another
   projection's output as input (re-derive from events instead). This keeps every projection
   independently rebuildable.
2. Each projection tracks its position (`last_event_recorded_at` watermark) and is idempotent
   over replays.
3. Projection code changes bump `projection_version`; rebuilt outputs are written alongside old
   versions until the old version is explicitly retired. Consumers pin a version.

### 7.4 Class- and school-level aggregation (B2B views)

- `class_aggregates`: per class × chapter × week — engagement-vector distributions, coverage
  spread, checkpoint-response mix, participation counts. Built from events joined through
  `class_memberships` *as of the event time* (interval join), so roster changes don't corrupt
  history.
- `institution_aggregates`: per school × grade band × subject — rollups of class aggregates'
  inputs (recomputed from events, per rule 7.3.1), for school-admin views.
- **Small-cohort suppression**: any aggregate cell covering fewer than `K = 5` students renders
  as "insufficient data" in teacher/admin APIs. Prevents de-anonymization of individuals through
  aggregate views and keeps probabilistic signals from being over-read on tiny samples.
- Teacher individual-student views remain governed by §5.3 scope rules and the
  teacher-support MVP boundary; school admins get aggregates only.

---

## 8. The Async Worker Lane

### 8.1 Queue

**MVP form** (respecting `docs/planning/backend-mvp-strategy.md` §10 — no Redis/Celery yet):
a `jobs` table in Postgres claimed with `SELECT ... FOR UPDATE SKIP LOCKED`, one worker process.
The Phase 1 worker entrypoint uses the Postgres-backed queue/store adapters in fixture mode; it
must not run an in-memory queue in staging or production.

Runtime validation note: the opt-in live Postgres check using `TEST_DATABASE_URL` now verifies
connectivity to the Supabase instance and correctly skips the RLS assertion when the supplied role
has `BYPASSRLS`; use a non-bypass app role for the final pooled-RLS proof required by the Phase 1
exit gate.

```sql
CREATE TABLE jobs (
    job_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_type     TEXT NOT NULL,        -- classify | compress | project | replay | podcast
    tenant_id    UUID NOT NULL,
    payload      JSONB NOT NULL,
    status       TEXT NOT NULL DEFAULT 'queued',   -- queued|running|done|failed|dead
    attempts     SMALLINT NOT NULL DEFAULT 0,
    run_after    TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Retries with exponential backoff; `attempts >= 5` → `dead` + alert. The queue interface is a thin
module (`workers/queue.py`) so swapping the backend to Redis later changes one module, not the
handlers.

**Scale form**: same handlers behind Redis (as cache *and* queue) with a worker pool — adopt only
when queue depth or latency data demands it.

### 8.2 Job types

| Job | Trigger | What it does |
|-----|---------|--------------|
| `classify` | `offer_set_choice` event; quiz question generation; nightly batch over unselected offer-set options (lowest priority — gates nothing in-session) | Stage 2 Classification Model median-of-3 via `llm_gateway`; code computes entropy/dispersion/flags and resolves concept attribution against P4 edge IDs (topology spec §4.1); appends `question_classified` event; updates `analytic_rm.question_classifications` |
| `compress` | `node_created` (AI node) | Node summary compression via the configured compression-capable model per chapter-analysis spec §6.1; terminology scan in code |
| `project` | New events past a watermark (poll or NOTIFY) | Incrementally update analytic projections |
| `replay` | Operator request via `api/internal` | Re-run classification or projections over an event range under a new `prompt_version`/`projection_version`, writing results alongside old ones |
| `podcast` | `podcast_requested` event | Session-derived script + TTS; stores audio to Supabase Storage; appends `podcast_generated` |
| `chapter_analysis` | Operator request | Runs P0–P11 (plus P12/P13 once the topology layer ships) with verification gates and QA queue |

**Ordering rule**: the synchronous request path appends events and returns. Nothing the student
waits for ever depends on a job completing. Classification lag is invisible by design
(post-hoc property); podcast generation surfaces as an in-app "ready" state.

### 8.3 Replay (the framework's revisability, operationalized)

`replay` is a first-class operation, not a script:

1. Operator specifies: event range (time/chapter/tenant), target (classifier prompt vN /
   projection vN), and a `replay_id`.
2. Worker re-processes; outputs are stamped with the new version **and** `replay_id`, written
   alongside existing rows — never overwriting.
3. Comparison queries (old vs new version on the same events) are the acceptance test for any
   prompt or framework revision, per the golden-set regression protocol in
   `docs/architecture/llm-pipeline.md`.
4. Cutover = consumers re-pin to the new version; rollback = re-pin back. Data is never lost.

---

## 9. The LLM Gateway Module

The single chokepoint for every model call (runtime and chapter-analysis pipeline). No other
module constructs a provider client (import rule §4.4). Provider and model ids are configured
with environment variables (`LLM_PROVIDER`, `LLM_STAGE1_MODEL_ID`, `LLM_STAGE2_MODEL_ID`) and
stamped onto events/rows as `model_id`; product logic must refer to Stage 1/Stage 2 roles, not
hardcoded provider model names.

**Responsibilities**:

1. **Structured output enforcement** — tool-use JSON schema / Instructor on every call;
   schema-invalid responses are retried once, then surfaced as typed failures.
2. **Version stamping** — every call logs `model_id`, `prompt_version`, latency, token counts;
   callers receive these to stamp onto events.
3. **All arithmetic in code** — entropy, medians, dispersion, confidence bands live here (or in
   `classification`), never in prompts. This is the structural fix for the
   entropy-computed-by-model bug noted against `docs/architecture/llm-pipeline.md`.
4. **Cost accounting** — per-call cost rows keyed by `tenant_id`, purpose
   (generation/classification/analysis/podcast), and model. B2B contracts need per-school cost
   visibility; this is where it comes from.
5. **Budget guards** — per-tenant and global daily token budgets with degradation behavior
   (serve from content library/cache first, queue non-urgent jobs) rather than hard failure.
6. **Key custody** — API keys exist only in this module's environment; the mobile client never
   holds credentials (consistent with `docs/planning/backend-mvp-strategy.md` boundary rule).


---

## 10. Versioning and Stamping Rules (consolidated)

| Artifact | Version field(s) | Where stamped |
|----------|------------------|---------------|
| Serving/ranking policy | `policy_name`, `policy_version` | Offer-set events |
| Generation prompt | `prompt_version`, `model_id` | Offer-set events, node content |
| Classification prompt | `prompt_version`, `model_id` | `question_classified` events + analytic rows |
| Chapter analysis | `chapter_analysis_id` (envelope carries pipeline/pass versions) | All chapter-dependent events |
| Segment schema | `segment_schema_version` | All events with `segment_key` |
| Event payload schema | `event_version` | Every event |
| Projection code | `projection_version` | Every analytic row |
| Outcome instrument | `instrument_version` | `learning_outcome` events |
| Replay run | `replay_id` | Replayed outputs |

**Rules**: (1) no LLM output or derived row exists without its instrument stamps; (2) version
values come from code constants/config bumped in the same commit as the change; (3) audit trail
for policy changes per `docs/measurement-and-experimentation.md` §4.7.

---

## 11. API Surface Organization

One FastAPI app, four routers with separate response-type universes:

| Router | Audience | Auth requirement | Response types from |
|--------|----------|------------------|---------------------|
| `/v1/student/*` | Mobile client (learner) | `student` membership | `domain/student` only — dimensional fields inexpressible |
| `/v1/teacher/*` | Teacher web dashboard | `teacher`/`approved_teacher` + active teaching assignment | `domain/analytic` scoped per §5.3 |
| `/v1/admin/*` | School admin web | `school_admin` membership | Tenancy + aggregate types (no individual drill-down) |
| `/v1/internal/*` | Platform ops | Platform `admin` + MFA | Replay, projection rebuild, chapter-analysis QA, registry tooling |

**Surface sketch** (full endpoint contract belongs in a separate API specification — see gap
list):

- Student: session CRUD/resume, node save, edge create/delete, phrase selection → offer set,
  question selection → node generation, podcast request/status, checkpoint responses,
  event batch ingestion (client-captured interaction events).
- Teacher: roster view, class chapter view, bounded teacher-support views, useful/not-useful
  feedback, export.
- Admin: institution profile, class management, roster upload, activation-code lifecycle,
  teacher invitations, school-level aggregates, consent records view.
- Internal: replay, rebuild, QA queue, golden-set runs, cost dashboards.

**Rules**: client event capture goes through an ingestion endpoint that validates against the
event registry (clients cannot invent event types). Errors and pagination are uniform across
routers; the student router's error bodies never leak analytic vocabulary.

---

## 12. Consent and Data Governance for School-Managed Minors (DPDP Act 2023)

The DPDP Act 2023 requires **verifiable parental/guardian consent for processing personal data of
children (< 18)**, and prohibits behavioral tracking and targeted advertising directed at
children. This product's core mechanism *is* behavioral capture, so this is a first-order design
constraint, not a compliance afterthought. Architectural consequences:

1. **Consent is an entity, not a checkbox**: a `consent_records` table — student, consent kind
   (data processing; behavioral analytics for teacher support), grantor (parent/guardian),
   method (OTP link, signed school form reference), timestamp, withdrawal timestamp. The
   `consent_recorded` event provides the audit trail.
2. **School-managed accounts do not inherit consent from the school.** The school is the conduit
   for obtaining parental consent (activation flow §5.2 step 3), but the record names the
   guardian. Whether the school may act as the consent-collecting agent should be reviewed by
   counsel; the schema supports either answer.
3. **Consent gates processing, structurally**: the `classify` and `project` workers skip students
   whose behavioral-analytics consent is absent or withdrawn (raw events are still captured for
   service operation, but no dimensional profile is built and no teacher view renders them —
   "consent pending" state). This degrades gracefully: the student can still explore.
4. **Withdrawal and erasure**: consent withdrawal stops projection inclusion immediately
   (rebuild without the student — the event-sourced design makes this a replay, not surgery).
   Erasure requests delete tenancy-table PII and tombstone the pseudonymous id; whether raw
   events must also be purged versus irreversibly de-identified needs legal review — the
   pseudonymization boundary (§6.3.2) was designed to make de-identification defensible.
5. **The behavioral-tracking prohibition needs a documented legal position**: the product's
   defense is that tracking serves the child's own learning support, is never used for
   advertising/profiling beyond the educational purpose, and is teacher/guardian-visible. This
   position, plus Significant Data Fiduciary obligations if user volume triggers them, belongs in
   the dedicated data-governance document (see gap list) — flagged here, not resolved here.
6. **Data residency**: keep the Supabase project (and any replicas/backups) in an Indian region;
   note this in vendor configuration as a deployment requirement.

---

## 13. Explicitly Avoided

| Avoided | Reason |
|---------|--------|
| Microservices / serverless-per-function | The boundaries that matter are data-visibility boundaries, enforced by import rules and schemas — not deployment units |
| Kafka / EventStoreDB | Event sourcing here is a discipline over one Postgres table; volume does not justify a log platform |
| Graph database for concept graphs | Per-chapter, small, read-mostly; Postgres tables suffice |
| Shared read model filtered per role | Filtering leaks; separate schemas + separate types make leaks structurally impossible |
| Aggregates as source of truth | Destroys framework revisability (§2.1) |
| Per-school database / schema-per-tenant | Operational burden without isolation benefit at this scale; RLS + `tenant_id` achieves the guarantee. Revisit only for a contractually demanded dedicated deployment |
| ML feature stores / training infra | Phases 1–3 prohibit trained models; statistical queries over projections suffice |

---

## 14. Open Items

1. Exact endpoint contract — requires the API specification document (gap list).
2. Counsel review of DPDP positions in §12 (consent agency, erasure scope, tracking defense).
3. `K` suppression threshold (§7.4) and per-tenant budget defaults (§9.5) — provisional values, config not constants.
4. Whether `viewport_changed` events are sampled/throttled client-side (volume vs analytic value).
5. Reconciliation: `docs/system-architecture.md` data-layer table lists Redis/TimescaleDB as
   current; per `docs/planning/backend-mvp-strategy.md` and this document they are deferred.
   `docs/system-architecture.md` should be annotated accordingly.
