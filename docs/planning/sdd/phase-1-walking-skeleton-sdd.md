# Phase 1 Walking Skeleton — Software Design Document (SDD)

**Document Version**: 1.1  
**Status**: Active — implementation near Phase 1 exit gate  
**Phase / milestone**: Phase 1 — Walking Skeleton (`development-approach.md` §4)  
**Related Documents**: `docs/planning/session-bootstrap.md` (context key), `docs/planning/worklog-v2.md` (active live tracker), `docs/planning/worklog.md` (rotated archive), `docs/planning/sdd-template.md`, `docs/planning/development-approach.md`, `docs/architecture/backend-architecture.md`, `docs/planning/testing-strategy.md`, `docs/configuration-reference.md`

---

## 1. Increment Identity

| Field | Value |
|---|---|
| Increment name | Phase 1 Walking Skeleton — thin end-to-end loop |
| Phase / milestone | Phase 1 (precedes M1) |
| Owner | (developer) |
| Status | Active — local and GitHub Actions CI gates green; live non-bypass Supabase RLS verified; backend Sentry smoke received; deploy/mobile proof still open |

Goal (`development-approach.md` §4.1): the smallest deployed end-to-end loop touching every architectural layer (mobile → API → event store → worker → LLM → projection), proving every integration point at once.

Current implementation status (`development-approach.md` §4.1, §6; `testing-strategy.md` §6): the backend walking skeleton is implemented and validated locally. A dedicated non-bypass Supabase role now backs `TEST_DATABASE_URL`, so the live RLS / `SKIP LOCKED` contract runs actively and passes instead of skipping for `BYPASSRLS`.

## 2. Source-of-Truth References (mandatory)

- `development-approach.md` §4 (Phase 1 scope + exit gate), §6 (day-one disciplines), §8 (working method)
- `backend-architecture.md` §3 (deployment + stack), §4 (module boundaries + import contracts), §6 (event store + registry), §8 (Postgres `SKIP LOCKED` job queue), §9 (LLM Gateway)
- `adr-log.md` ADR-0001 (event-sourced monolith), ADR-0002 (`SKIP LOCKED`), ADR-0003 (two read models), ADR-0004 (organic-first post-hoc classification)
- `session-path-data-contract.md` §5 (session), §6 (node), §8 (interaction events), §9 (offer-set / thread context)
- `api/student-api-spec.md` §5 (session endpoints), §8 (AI offer-set workflow)
- `database/event-store-and-job-queue-schema.md` §2–§3 (events + append rules), §7–§9 (jobs + `SKIP LOCKED`)
- `database/read-models-schema.md` §3–§4 (`student_rm` allowed scope + tables), §7 (`analytic_rm.question_classifications`)
- `configuration-reference.md` §5 (`JOB_MAX_ATTEMPTS=5`, `JOB_QUEUE_BACKEND=postgres_skip_locked`), §9 (`LLM_STAGE1_MODEL_ID`, `LLM_STAGE2_MODEL_ID`, `LLM_CI_MODE=recorded fixtures`)
- `testing-strategy.md` §2 (layers L1–L6), §6 (Definition of Done)

## 3. Scope of Increment

**In scope:**
- Migration 0001 with non-retrofittable primitives (`development-approach.md` §6.1,
  `backend-architecture.md` §12): `tenant_id` + version-stamp columns on every table;
  append-only `events`; `jobs` table for `SKIP LOCKED`; `student_rm` + `analytic_rm` schemas;
  base tenancy tables; `consent_records` table + `consent_recorded` event so the `classify`
  worker can gate projection into `analytic_rm` from the first migration.
- Supabase remediation migrations 0002 and 0003: RLS enabled on tenancy tables, fixed function
  search paths, FK/tenant indexes added, and RLS policies optimized via `current_app_tenant_id()`;
  Supabase security advisor lints are resolved.
- Event registry (`events/registry.py`) validating the three Phase 1 client/server events `session_started`, `node_created`, `offer_set_choice` plus the worker-only `question_classified` (`development-approach.md` §4.1).
- `POST /v1/student/sessions` (start chapter-scoped session) and `POST /v1/student/offer-sets/{offer_set_id}/choices` (selected and dismissed outcomes).
- One `classify` worker job claimed via `SELECT ... FOR UPDATE SKIP LOCKED`, running in `llm_gateway` fixture mode.
- Minimal projection into `student_rm.sessions` / `student_rm.nodes`; minimal `analytic_rm.question_classifications` row from the worker.
- One Expo screen rendering a single AI node, only if the mobile surface is part of this increment (`development-approach.md` §4.1).

**Out of scope (deferred — name the gate that owns it):**
- Canvas gestures / 65-node limits (M3); curriculum entry + Supabase Auth + consent capture (M4).
- Edge-`+` branching, manual reference links, deletion cascade (M1).
- Phrase-selection flow (M2); checkpoints (M5); teacher surface V1/V2/V3 (M6/M7); podcast (M8).
- `compress`, `project`, `replay`, `podcast`, `chapter_analysis` jobs (added as their milestones open).

## 4. Traceability Row(s)

Phase 1 narrows the audited matrices to the minimum loop. Rows below descend from `api/feature-endpoint-traceability.md` and `database/schema-traceability-and-validation.md`.

| Feature | Endpoint | Event | Read Model | Worker Job | Table(s) |
|---|---|---|---|---|---|
| Start chapter-scoped session | `POST /v1/student/sessions` | `session_started` (+ optional `node_created`) | `student_rm` | none in Phase 1 | `events`, `student_rm.sessions`, `student_rm.nodes` |
| Select offer-set option | `POST /v1/student/offer-sets/{offer_set_id}/choices` | `offer_set_choice`, `node_created` | `student_rm`, later `analytic_rm` | `classify` | `events`, `student_rm.nodes`, `jobs` |
| Dismiss offer set | same choice endpoint | `offer_set_choice` (no-selection outcome) | `student_rm` | none (no `classify`) | `events`, `jobs` (unchanged) |
| Post-hoc classification | no student endpoint | `question_classified` | `analytic_rm` | `classify` | `events`, `analytic_rm.question_classifications` |

## 5. Module Placement & Import Rules

Per `backend-architecture.md` §4 (the contracts that carry product guarantees).

| Concern | Module | Import rule enforced |
|---|---|---|
| Append + registry validation | `events/` | only `events` may write the event store (§4.3); clients cannot submit worker-only events |
| Student session/node types | `domain/student` | `domain` imports nothing (§4.6); no dimensional fields exist here |
| Student router | `api/student` | must not import `domain/analytic`, `classification`, or dimensional `projections` builders (§4.1) |
| Offer-set generation | `generation/` | must not import `classification`; calls models only via `llm_gateway` (§4.2, §4.4) |
| Stage 2 classification | `classification/` + `workers/` | scoring/entropy arithmetic lives here; reads models only through `llm_gateway` |
| Read-model writes | `projections/` | only `projections` writes read-model tables; routers are read-only (§4.5) |
| Tenant resolution | `tenancy/` | everything except `domain` may import `tenancy` (§4.6); mobile-supplied tenant is never authoritative |
| Model calls | `llm_gateway/` | sole constructor of model clients (§4.4); fixture mode in CI (`configuration-reference.md` §9) |
| Job queue transport | `workers/queue.py` | thin `SKIP LOCKED` interface so a later Redis swap changes one module (`backend-architecture.md` §8) |

## 6. Event / Payload / Schema Deltas

- **Registry** (`events/registry.py`): register `session_started`, `node_created`, `offer_set_choice` with `producer` in {`client`,`server`}; register `question_classified` as `producer: worker` only — client batches that submit it are rejected (`event-store-and-job-queue-schema.md` §3).
- **Stamps made non-nullable per type** (`backend-architecture.md` §6.2): `tenant_id` + `event_version` on all four; `question_classified` additionally carries `prompt_version`, `model_id`, and projection lineage (`projection_version`).
- **Migration 0001 (non-retrofittable, `development-approach.md` §6.1,
  `backend-architecture.md` §12)**: `tenant_id` + version-stamp columns on every table; `events`
  UPDATE/DELETE revoked at the DB privilege level; `jobs` with `status`, `attempts`, `run_after`,
  `locked_at`, `locked_by` supporting `SKIP LOCKED`; `student_rm` + `analytic_rm` schemas; base
  tenancy tables; `consent_records` table with `consent_kind`, `grantor`, `granted_at`,
  `withdrawn_at`, and the `consent_recorded` event so `classify` can gate `analytic_rm` writes
  from day one.
- **Migrations 0002–0003 (Supabase advisor remediation)**: `tenants` and `memberships` have RLS
  enabled; all Phase 1 tenant policies use `(SELECT public.current_app_tenant_id())`; trigger/helper
  functions use fixed `search_path = public, pg_temp`; FK/tenant indexes are present. Supabase
  security advisor returns no lints after application.
- **Config bindings** (`configuration-reference.md`): `JOB_MAX_ATTEMPTS=5` (dead-letter, ADR-0002), `JOB_QUEUE_BACKEND=postgres_skip_locked`, `LLM_STAGE1_MODEL_ID`, `LLM_STAGE2_MODEL_ID`, and `LLM_CI_MODE=recorded fixtures`.

## 7. Invariant Enforcement

### 7.1 Category Invisibility

Enforced by:

- physical `student_rm` / `analytic_rm` schemas
- student DTO introspection test
- import-linter
- no student raw event endpoint
- no `analytic_rm` repository import in `api/student`

Tests:

- L3: student DTO forbidden-field test
- L3: import-linter contract
- L3: `student_rm` forbidden-column schema test

### 7.2 Organic-First

Enforced by:

- classification job enqueued only after selected `offer_set_choice`
- no classification in synchronous student response
- no `classify` for dismissed/no-selection outcomes
- generation path does not read `analytic_rm`

Tests:

- L4: selected choice appends event, returns student-safe node, then enqueues `classify`
- L4: dismissed choice appends event but does not enqueue `classify`
- L3: student response contains no classification fields

### 7.3 Tenant Isolation

Enforced by:

- `tenant_id` on all rows
- backend-resolved tenant context
- no trust in mobile-supplied tenant
- RLS as backstop
- tenant-isolation integration test before second tenant

Tests:

- L3/L4: tenant A cannot read tenant B session
- L3: every tenant-scoped table includes `tenant_id`
- L4: worker job includes tenant context

---

## 8. Test Plan by Layer

| Layer | Tests Required |
|---|---|
| L1 | event registry accepts known events and rejects unknown types; job backoff calculator; idempotency key validation |
| L2 | Phase 1 builds the system's first projections, so these are **mandatory, not conditional** (`development-approach.md` §6.4): minimal event → `student_rm.sessions` / `student_rm.nodes` projection; **replay-determinism** (rebuild → byte-identical row); **idempotency** (apply-twice = no-op); **version-stamp** assertion on the derived `analytic_rm.question_classifications` row (`projection_version` + `prompt_version`/`model_id` + lineage) |
| L3 | append-only event DB grants; import-linter; student DTO forbidden fields; `student_rm` forbidden-column check |
| L4 | session start integration; offer choice selected integration; offer dismissal integration; worker classify integration |
| L5 | fixture-based classification response schema validation through `llm_gateway` fixture mode |
| L6 | minimal physical-device smoke only if mobile screen is part of this increment |

---

## 9. First Red Tests

Write these before implementation:

1. `test_event_registry_rejects_unknown_event_type`
2. `test_events_table_rejects_update_and_delete`
3. `test_session_start_appends_session_started`
4. `test_session_start_writes_student_rm_session`
5. `test_student_session_response_has_no_analytic_fields`
6. `test_offer_choice_selected_appends_offer_set_choice`
7. `test_offer_choice_selected_enqueues_classify_job`
8. `test_offer_choice_dismissed_does_not_enqueue_classify`
9. `test_classify_worker_claims_job_with_skip_locked`
10. `test_classify_worker_appends_question_classified`
11. `test_question_classified_not_visible_to_student_api`
12. `test_tenant_a_cannot_read_tenant_b_session`
13. `test_api_student_import_linter_blocks_analytic_imports`

Gap-closing additions (G1–G12), required before the Phase 1 gate:

14. `test_tenant_isolation_holds_through_connection_pool` (G1 — exercise the pooled path with `SET LOCAL app.tenant_id`, not a fresh single connection; `development-approach.md` §6.6, `testing-strategy.md` §2 L3)
15. `test_first_projection_rebuild_is_byte_identical` (G2 — replay-determinism; `development-approach.md` §6.4)
16. `test_projection_is_idempotent_on_replay` (G2 — apply-twice = no-op; `testing-strategy.md` §2 L2)
17. `test_offer_choice_response_returns_with_classify_still_queued` (G3 — non-blocking async proof; `backend-architecture.md` §8, ADR-0004)
18. `test_student_rm_has_no_forbidden_columns` (G5 — `read-models-schema.md` §5, `schema-traceability-and-validation.md` §3)
19. `test_question_classified_row_carries_version_stamps` (G6 — `backend-architecture.md` §2.4, `read-models-schema.md` §8)
20. `test_rls_denies_cross_tenant_when_app_guard_bypassed` (G7 — DB-level backstop distinct from app check; `backend-architecture.md` §5.3)
21. `test_generation_cannot_import_classification_or_analytic` (G8 — `backend-architecture.md` §4.2)
22. `test_offer_choice_append_and_classify_enqueue_are_atomic` (G9 — `event-store-and-job-queue-schema.md` §9)
23. `test_duplicate_offer_choice_does_not_double_enqueue_classify` (G10 — idempotency key; `event-store-and-job-queue-schema.md` §3/§9)
24. `test_student_api_exposes_no_raw_event_endpoint` (G11 — `schema-traceability-and-validation.md` §3)
25. `test_mobile_supplied_tenant_id_is_ignored` (G12 — `backend-architecture.md` §5.4)
26. `test_classify_worker_skips_analytic_projection_without_consent` (consent-gate resolution —
    `backend-architecture.md` §12.3, `read-models-schema.md` §9): a selected offer choice with no
    valid `behavioral_analytics` consent record must enqueue the `classify` job but the worker must
    skip writing to `analytic_rm.question_classifications`; the student app remains unaffected.

---

## 10. Definition of Done

This increment is done only when:

- migration 0001 exists with tenant/version primitives
- Supabase migrations 0001, 0002, and 0003 are applied; security advisor returns no lints
- `events` table is append-only
- event registry validates at least:
  - `session_started`
  - `node_created`
  - `offer_set_choice`
  - `question_classified`
- `jobs` table supports `SKIP LOCKED`
- selected offer choice enqueues `classify`
- dismissed offer choice does not enqueue `classify`
- worker processes one `classify` job in fixture mode
- the `classify` worker checks valid `behavioral_analytics` consent before writing to `analytic_rm.question_classifications`; without consent the job succeeds but produces no analytic row (`backend-architecture.md` §12.3, `read-models-schema.md` §9)
- `question_classified` lands in the event store **and** the minimal `analytic_rm.question_classifications` row (ADR-0003/0004 — not either/or) **when consent is present**
- every derived row carries `projection_version` + lineage stamps (`prompt_version`/`model_id`); `analytic_rm` row stamping verified
- the first projections pass **replay-determinism** (rebuild → byte-identical) and **idempotency** (apply-twice = no-op) tests (`development-approach.md` §6.4)
- `/v1/student` never returns analytic fields and exposes no raw event endpoint
- import-linter passes (`api/student ⇏ analytic` **and** `generation ⇏ classification`)
- RLS policies created in migration 0001; the tenant-isolation test runs **through the connection pool** and passes for at least two test tenants, with a DB-level backstop test that denies cross-tenant rows when the app guard is bypassed
- mobile-supplied `tenant_id` is ignored in favor of backend-resolved context
- LLM cost/usage counter records from the first `llm_gateway` call, using the configured Stage 1/Stage 2 model id rather than a hardcoded provider model name (`development-approach.md` §6.9)
- CI is green including L1/L2/L3/L4 relevant tests, import-linter, **formatter, and mypy** (`testing-strategy.md` §3/§6)
- worklog is updated

---

## 11. Worklog Entry Required

After implementation, add an entry to `docs/planning/worklog.md` with:

- source sections used
- events implemented
- tables created
- endpoints implemented
- tests run
- invariant tests status
- open issues
- next milestone recommendation
