# Phase 2 Curriculum Ingestion — Software Design Document (SDD)

**Document Version**: 1.0 (draft — kickoff)
**Status**: Active — Phase 2 in flight (the only increment open)
**Phase / milestone**: Phase 2 — Curriculum Ingestion (`development-approach.md` §3 + §5 M4/M6 note)
**Related Documents**: `docs/planning/sdd/phase-1-walking-skeleton-sdd.md` (closed predecessor), `docs/planning/worklog-v2.md` (active live tracker), `docs/planning/sdd-template.md`, `docs/planning/development-approach.md`, `docs/architecture/backend-architecture.md`, `docs/architecture/adr-log-02.md`, `docs/chapter-analysis-pipeline-specification.md`, `docs/planning/testing-strategy.md`, `docs/configuration-reference.md`, `docs/database/read-models-schema.md`

---

## 1. Increment Identity

| Field | Value |
|---|---|
| Increment name | Phase 2 — Curriculum Ingestion (real chapter spine + auth + teacher render) |
| Phase / milestone | Phase 2 (first milestone after the Walking Skeleton) |
| Owner | (developer) |
| Status | Active — kickoff; no production code until §9 red tests are written first |

Goal: take the Phase 0 P0–P4 pipeline (`development-approach.md` §3.1) from review-by-eye scripts
into the `chapter_analysis` module (`backend-architecture.md` §4), land one real NCERT chapter's
concept graph in the database, attach Supabase Auth identity + tenant resolution
(`backend-architecture.md` §5.4), and render that chapter analysis in a minimal Teacher Dashboard
V1. This replaces fixture-backed sessions with a real curriculum spine.

### 1.1 Sequencing note (traceable composition, not new requirements)

`development-approach.md` §5 splits this work across Phase 0 (P0–P4 as scripts), M4 (curriculum
entry + Supabase Auth), and M6 (Teacher V1/V2). Phase 2 deliberately composes the *non-student-data*
parts of these into one curriculum spine, justified by the §5 M6 note that **Teacher V2 "needs no
student data — it renders chapter analysis, so it can be built any time after Phase 0."** No new
requirement is originated; each scope item below cites its owning section. Canvas maturation (M3),
phrase selection (M2), checkpoints (M5), and teacher V3 panels (M7) remain out of scope.

## 2. Source-of-Truth References (mandatory)

- `development-approach.md` §3 (Phase 0 P0–P4 work items + gate), §5 (M4 curriculum entry + auth;
  M6 Teacher V2 render note), §6 (day-one disciplines carried forward), §7.1 (auth stack), §7.7
  (content pipeline tooling: `pypdf`, P0–P4 model assignment), §8 (working method)
- `backend-architecture.md` §3 (deployment), §4 (`chapter_analysis` module + import contracts),
  §5.1/§5.3/§5.4 (tenancy entity model, RLS, identity + tenant resolution), §6 (event store +
  registry), §7 (read models), §9 (LLM Gateway), §11 (API surface — `/v1/student`, `/v1/teacher`)
- `adr-log.md` ADR-0001/0002/0003/0004 (carried invariants); `adr-log-02.md` ADR-0015 (Supabase
  Auth JWT strategy — to be accepted in this phase)
- `chapter-analysis-pipeline-specification.md` P0 (segmentation/ingestion), P1 (named concepts),
  P2 (embedded concepts), P3 (merge/dedup), P4 (typed relationship graph), §5 (verification gate)
- `read-models-schema.md` §4 (`student_rm.sessions` curriculum context columns:
  `exam_id`/`subject_id`/`chapter_id`/`chapter_analysis_id`), §7 (`analytic_rm` coverage tables
  keyed by `concept_id`), §8 (freshness/stamp fields)
- `session-path-data-contract.md` §5–§6 (session/node shape carrying `chapter_id`)
- `testing-strategy.md` §2 (L1–L6 layers), §3 (CI gates), §4 (fixtures)
- `configuration-reference.md` §9 (LLM Gateway), §10 (env var names)

## 3. Scope of Increment

**In scope:**
- **Deferred Phase 1 items, taken first (see §3.1 priority order)**: Render backend + worker
  deployment verification (`development-approach.md` §4.1, §4.2); physical-device Expo smoke
  (`development-approach.md` §4.2) — gated on a mobile curriculum surface existing.
- **`chapter_analysis` module** productionizing P0–P4 (`backend-architecture.md` §4;
  `chapter-analysis-pipeline-specification.md` P0–P4): P0 segmentation via `pypdf` (restructure the
  existing `extract_pdf.py` seed), P1/P2 concept extraction, P3 merge/dedup, P4 typed edge graph —
  all model calls through `llm_gateway` (`backend-architecture.md` §4.4, §9), LLM in CI = fixtures
  (`configuration-reference.md` §9).
- **Migration 0004 — `curriculum` schema** persisting P0–P4 outputs (segments, merged concept
  inventory, typed edges, `chapter_analysis` envelope) with `tenant_id` + version stamps on every
  row (`backend-architecture.md` §2.5, §10) and RLS (§5.3). `chapter_analysis_id` is the pinned
  version already referenced by `read-models-schema.md` §4.
- **Supabase Auth integration**: JWT validation on `/v1/student` and `/v1/teacher`
  (`backend-architecture.md` §5.4, §11); `tenancy` module resolves `user_id → memberships →
  tenant/role` server-side; mobile-supplied tenant remains non-authoritative.
- **Consent capture at first sign-in**: `consent_recorded` event (already in the registry and
  migration 0001) emitted via the auth flow (`backend-architecture.md` §12.1; ADR-0014).
- **Teacher Dashboard V1 (render-only)**: a `/v1/teacher` read endpoint serving the ingested
  chapter's concept graph; no student analytic data (`backend-architecture.md` §7.4 K-suppression
  not yet needed because no per-student aggregates render; `development-approach.md` §5 M6 note).
- **Real-chapter student session**: `POST /v1/student/sessions` resolves a real `chapter_id` +
  `chapter_analysis_id` from the `curriculum` schema instead of fixture constants.

**Out of scope (name the gate that owns it):**
- Canvas gestures / 65-node limits (M3); phrase selection (M2); edge-`+` branching + deletion
  cascade (M1); checkpoints (M5); teacher V3 panels + coverage projections (M7); podcast (M8).
- P5–P13 passes (dimension audit, productive pairs, weighting, topology) — open as their
  milestones do (`chapter-analysis-pipeline-specification.md` P6+; `development-approach.md` §5).
- `compress`, `project`, `replay`, `podcast` worker jobs beyond what ingestion needs.

### 3.1 Implementation priority order

1. **Render deployment verification** (deferred Phase 1; no frontend dependency).
2. **Supabase Auth + tenant resolution** on existing `/v1/student` (unblocks real sessions).
3. **`chapter_analysis` P0–P4 + migration 0004 `curriculum` schema** (the spine).
4. **Real-chapter student session** wiring (replaces fixtures).
5. **Teacher Dashboard V1 render endpoint**.
6. **Physical-device Expo smoke** (deferred Phase 1; gated on a mobile curriculum surface — see
   §7.4 and the deferral note in the worklog).

## 4. Traceability Row(s)

Descends from `api/feature-endpoint-traceability.md` and
`database/schema-traceability-and-validation.md`.

| Feature | Endpoint | Event | Read Model | Worker Job | Table(s) |
|---|---|---|---|---|---|
| Ingest NCERT chapter (P0–P4) | `api/internal` operator trigger (`backend-architecture.md` §8.2 `chapter_analysis`) | none (pipeline writes curriculum, not events) | `curriculum` | `chapter_analysis` | `curriculum.chapters`, `curriculum.segments`, `curriculum.concepts`, `curriculum.concept_edges` |
| Sign in + resolve tenant | Supabase Auth + `/v1/*` JWT middleware | `consent_recorded` (first sign-in) | tenancy tables | none | `events`, `memberships`, `consent_records` |
| Start real-chapter session | `POST /v1/student/sessions` | `session_started` | `student_rm` | none | `events`, `student_rm.sessions`, `curriculum.chapters` |
| Render chapter analysis | `GET /v1/teacher/chapters/{chapter_id}` | none | reads `curriculum` only | none | `curriculum.*` |

## 5. Module Placement & Import Rules

Per `backend-architecture.md` §4. Phase 2 activates the `chapter_analysis` module (already named in
the package layout) and the `auth` surface inside `tenancy`/`api`; it adds **no** new student↔analytic
edge.

| Concern | Module | Import rule enforced |
|---|---|---|
| P0–P4 pipeline | `chapter_analysis/` | calls models only via `llm_gateway` (§4.4); must not import `classification`, `generation`, or `api/*` |
| Curriculum persistence | `projections/` (or a dedicated `curriculum` writer) | only this writer writes `curriculum` tables; routers are read-only on them (§4.5 mirror) |
| Curriculum read types | `domain/` (curriculum types) | `domain` imports nothing (§4.6); no dimensional fields |
| Auth/JWT validation | `tenancy/` + `api/*` middleware | tenant resolved server-side from JWT (§5.4); mobile-supplied tenant ignored |
| Teacher render | `api/teacher` | may import `domain/analytic` + `tenancy` (§4); reads `curriculum`, not `student_rm` |
| Student session | `api/student` | unchanged Phase 1 contract: must not import `domain/analytic`/`classification`/dimensional `projections` (§4.1) |
| Model calls | `llm_gateway/` | sole constructor of model clients (§4.4); fixture mode in CI |

**New import-linter contracts (Phase 2):**
- `chapter_analysis ⇏ classification` and `chapter_analysis ⇏ generation` (Section A isolation
  mirror, `backend-architecture.md` §4.2).
- `chapter_analysis ⇏ api/*` (pipeline is operator/worker-driven, not request-driven).
- existing `api/student ⇏ analytic` and `generation ⇏ classification` remain merge-blocking.

## 6. Event / Payload / Schema Deltas

- **Registry**: no new student/worker event *types* are required for ingestion (the pipeline writes
  the `curriculum` read schema, not the event log — `backend-architecture.md` §6.3.3 "aggregates are
  never written to events"). `consent_recorded` is already registered (Phase 1). If an auditable
  "chapter ingested" marker is wanted, add it as a worker-only event in a follow-up, not by default.
- **Migration 0004 — `curriculum` schema** (`chapter-analysis-pipeline-specification.md` P0–P4
  outputs; `backend-architecture.md` §2.5, §10):
  - `curriculum.chapters` — `chapter_id`, `exam_id`, `subject_id`, `chapter_analysis_id`,
    `segment_index_version`, `tenant_id`, version stamps.
  - `curriculum.segments` — P0 segment index (`segment_id`, `segment_type`, `text`, `page`,
    `char_span`, `location` for questions), `tenant_id`.
  - `curriculum.concepts` — merged P1+P2→P3 inventory (`concept_id`, `label`, `definition`,
    `category_tag`, `passage_refs`, `merged_from`), `tenant_id`.
  - `curriculum.concept_edges` — P4 typed edges (`edge_kind` ∈ {PREREQUISITE_OF, CONNECTS,
    CONTRASTS_WITH}, `from_concept_id`, `to_concept_id`, `passage_support`), deterministic edge IDs
    (`testing-strategy.md` §2 L1; `chapter-analysis-pipeline-specification.md` P4), `tenant_id`.
  - RLS enabled on all `curriculum` tables routed through `current_app_tenant_id()`
    (`backend-architecture.md` §5.3), matching the 0002/0003 baseline; Supabase advisor must stay
    clean.
- **Auth config bindings** (`configuration-reference.md` §9–§10): Supabase Auth JWT verification
  secret/JWKS + auth URL (new placeholders, §added this phase); no mobile-side provider credentials.

## 7. Invariant Enforcement

### 7.1 Category Invisibility
Enforced by: `curriculum` is content (not student behavior) and is teacher/operator-facing; the
ingested chapter graph carries **no** per-student dimensional data; `/v1/student` still serializes
from `domain/student` only. Tests: L3 import-linter (`api/student ⇏ analytic`); L3 student DTO
forbidden-field test (unchanged); L3 assert `/v1/teacher/chapters` payload contains no per-student
fields.

### 7.2 Organic-First
Enforced by: ingestion never triggers classification; generation still does not read `analytic_rm`.
Tests: L3 `chapter_analysis ⇏ classification`/`generation`; Phase 1 organic-first L4 tests remain
green.

### 7.3 Tenant Isolation (incl. auth)
Enforced by: `tenant_id` on every `curriculum` row; backend-resolved tenant from JWT
(`backend-architecture.md` §5.4); mobile-supplied tenant ignored; RLS backstop on `curriculum`.
Tests: L3 JWT→tenant resolution contract; L3 RLS denies cross-tenant `curriculum` rows through the
pool; L3 `test_mobile_supplied_tenant_id_is_ignored` extended to authenticated requests.

### 7.4 Deferred-item gating
Render deployment has no frontend dependency (priority 1). Physical-device Expo smoke
(`development-approach.md` §4.2) requires a mobile surface that renders a real chapter; it is gated
on priority 4 (real-chapter session) existing and may be deferred until that mobile surface is
built — recorded explicitly in `worklog-v2.md`.

## 8. Test Plan by Layer

| Layer | Tests Required |
|---|---|
| L1 | P0 segmentation rules (deterministic `[chapter_segment_NNN]` IDs, same bytes → same IDs); P3 normalized label-match dedup; deterministic P4 edge-ID derivation; P5-verification-gate code checks (`chapter-analysis-pipeline-specification.md` §5) |
| L2 | `curriculum` ingestion is a projection-like build: **determinism** (re-run P0–P4 over the same fixtures + recorded LLM responses → byte-identical `curriculum` rows modulo timestamps); **idempotency** (re-ingest same chapter = no duplicate rows); **stamping** (`chapter_analysis_id` + version on every row) |
| L3 | new import-linter contracts (§5); auth JWT→tenant resolution contract; `curriculum` RLS through the pool; teacher render payload has no per-student fields; student DTO forbidden-field (carried) |
| L4 | end-to-end: ingest real chapter (fixtures) → start `/v1/student/sessions` against real `chapter_id` → returns student-safe node; authenticated request resolves correct tenant; teacher `GET /v1/teacher/chapters/{id}` returns the ingested graph |
| L5 | P1/P2/P4 LLM passes validated via recorded fixtures keyed by `prompt_version` (`testing-strategy.md` §4); never assert exact model text (schema/contract checks only) |
| L6 | physical-device Expo smoke against the deployed backend, once the mobile curriculum surface exists (deferred per §7.4) |

## 9. First Red Tests

Write these before implementation (`development-approach.md` §6; `00-canon.md` behavioral rules):

1. `test_p0_segmentation_ids_are_deterministic` (same bytes → same segment IDs)
2. `test_p0_segment_index_records_required_fields` (type/text/page/char_span/location)
3. `test_p3_merge_keeps_named_label_and_unions_passage_refs`
4. `test_p4_edge_ids_are_deterministic_and_typed`
5. `test_verification_gate_rejects_uncited_segment_refs` (`chapter-analysis-pipeline-specification.md` §5)
6. `test_curriculum_ingest_is_idempotent_on_reingest`
7. `test_curriculum_ingest_rebuild_is_byte_identical` (L2 determinism)
8. `test_curriculum_rows_carry_tenant_and_chapter_analysis_id`
9. `test_jwt_resolves_backend_tenant_and_role`
10. `test_authenticated_request_ignores_mobile_supplied_tenant_id`
11. `test_curriculum_rls_denies_cross_tenant_through_pool`
12. `test_chapter_analysis_cannot_import_classification_or_generation`
13. `test_chapter_analysis_cannot_import_api`
14. `test_session_start_resolves_real_chapter_from_curriculum`
15. `test_teacher_chapter_render_has_no_per_student_fields`
16. `test_first_signin_appends_consent_recorded`

## 10. Definition of Done

This increment is done only when:

- Render backend + worker deployment is verified live (deferred Phase 1 item closed).
- `chapter_analysis` P0–P4 run end-to-end on one real NCERT chapter with all model calls through
  `llm_gateway`; CI uses recorded fixtures (no live LLM).
- migration 0004 creates the `curriculum` schema with `tenant_id` + version stamps and RLS;
  Supabase security advisor returns no new lints.
- ingestion passes **determinism** (rebuild → byte-identical) and **idempotency** (re-ingest = no-op)
  L2 tests; every `curriculum` row carries `chapter_analysis_id` + version stamps.
- Supabase Auth JWT validation is enforced on `/v1/student` and `/v1/teacher`; tenant/role are
  backend-resolved; mobile-supplied tenant is ignored; first sign-in appends `consent_recorded`.
- `POST /v1/student/sessions` starts a session against a real `chapter_id`/`chapter_analysis_id`
  from `curriculum`; `/v1/student` still returns no analytic fields and no raw event endpoint.
- Teacher Dashboard V1 `GET /v1/teacher/chapters/{id}` renders the ingested graph with no
  per-student fields.
- new import-linter contracts pass (`chapter_analysis ⇏ classification`/`generation`/`api`); all
  Phase 1 contracts remain green.
- CI is green including L1/L2/L3/L4, import-linter, formatter, and mypy (`testing-strategy.md`
  §3/§6); ADR-0015 (Supabase Auth) is Accepted.
- physical-device Expo smoke is either recorded or explicitly re-deferred with a reason
  (`worklog-v2.md`), per §7.4.
- worklog is updated.

## 11. Worklog Entry Required

After each verified proof item, append an entry to `docs/planning/worklog-v2.md` (rotate to
`worklog-v3.md` at the 350-line cap) with: source sections used, pipeline passes / endpoints /
tables implemented, migrations applied, tests run, invariant-test status, deferred-item status, and
next-step recommendation.
