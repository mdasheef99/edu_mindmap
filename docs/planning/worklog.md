# Development Worklog

**Document Version**: 1.0  
**Status**: Active once implementation starts  
**Related Documents**: `docs/planning/session-bootstrap.md` (context key), `docs/planning/sdd/phase-1-walking-skeleton-sdd.md` (active blueprint), `docs/planning/development-approach.md`, `docs/planning/testing-strategy.md`, `docs/api/README.md`, `docs/database/README.md`

---

## Purpose

This worklog records implementation progress, phase-gate status, validation results, and decisions made during development. It exists so future contributors and AI agents can understand project state without relying on chat history.

Use one entry per focused work session. Keep entries factual and concise.

## Current Phase

- **Current phase**: Phase 1 — Walking Skeleton. SDD finalized (`docs/planning/sdd/phase-1-walking-skeleton-sdd.md`); red tests not yet started.
- **Next phase gate**: Phase 1 exit gate per the SDD §10 Definition of Done.
- **Blocking pre-work**: ~~resolve the consent-gate decision (see Open Decisions) before writing migration 0001.~~ RESOLVED 2026-06-17 — implement the consent gate in Phase 1 (Option A); see `adr-log.md` ADR-0014.

## Phase 1 Live Tracker

This section tracks **status only**. The active SDD is authoritative for requirement text; update the SDD, not this table, if a requirement changes. Status values: `not-started` · `red` (written, failing) · `green` · `deferred`.

### Red tests (SDD §9)

| # | Short name | Layer | Status | PR/commit |
|---|---|---|---|---|
| 1 | registry rejects unknown event type | L1 | not-started | |
| 2 | events reject UPDATE/DELETE | L3 | not-started | |
| 3 | session start appends `session_started` | L4 | not-started | |
| 4 | session start writes `student_rm` session | L2/L4 | not-started | |
| 5 | student response has no analytic fields | L3 | not-started | |
| 6 | offer choice selected appends `offer_set_choice` | L4 | not-started | |
| 7 | offer choice selected enqueues `classify` | L4 | not-started | |
| 8 | offer choice dismissed does not enqueue `classify` | L4 | not-started | |
| 9 | worker claims job with `SKIP LOCKED` | L4 | not-started | |
| 10 | worker appends `question_classified` | L4 | not-started | |
| 11 | `question_classified` not visible to student API | L3 | not-started | |
| 12 | tenant A cannot read tenant B session | L3/L4 | not-started | |
| 13 | import-linter blocks `api/student ⇏ analytic` | L3 | not-started | |
| 14 | tenant isolation holds through connection pool | L3/L4 | not-started | |
| 15 | first projection rebuild is byte-identical | L2 | not-started | |
| 16 | projection is idempotent on replay | L2 | not-started | |
| 17 | response returns with `classify` still queued | L4 | not-started | |
| 18 | `student_rm` has no forbidden columns | L3 | not-started | |
| 19 | `question_classified` row carries version stamps | L2 | not-started | |
| 20 | RLS denies cross-tenant when app guard bypassed | L3 | not-started | |
| 21 | generation cannot import classification/analytic | L3 | not-started | |
| 22 | append + classify enqueue are atomic | L4 | not-started | |
| 23 | duplicate offer choice does not double-enqueue | L4 | not-started | |
| 24 | student API exposes no raw event endpoint | L3 | not-started | |
| 25 | mobile-supplied `tenant_id` is ignored | L4 | not-started | |

### Definition of Done (SDD §10) — checklist

- [ ] migration 0001 with tenant/version primitives
- [ ] `events` table append-only
- [ ] registry validates `session_started` / `node_created` / `offer_set_choice` / `question_classified`
- [ ] `jobs` table supports `SKIP LOCKED`
- [ ] selected choice enqueues `classify`; dismissed does not
- [ ] worker processes one `classify` job in fixture mode
- [ ] `question_classified` lands in event store **and** `analytic_rm` row
- [ ] derived rows carry `projection_version` + lineage stamps
- [ ] projections pass replay-determinism **and** idempotency
- [ ] `/v1/student` returns no analytic fields and no raw event endpoint
- [ ] import-linter passes (`student ⇏ analytic` **and** `generation ⇏ classification`)
- [ ] RLS created in migration 0001; isolation runs **through the pool** + DB-level backstop
- [ ] mobile-supplied `tenant_id` ignored
- [ ] LLM cost/usage counter records from first call
- [ ] CI green incl. L1/L2/L3/L4 + import-linter + formatter + mypy
- [ ] worklog updated

### Open Decisions

- **Consent gate on `classify` → `analytic_rm` projection** — RESOLVED 2026-06-17.
  - Decision: **Option A** — implement the gate in Phase 1.
  - Rationale: DPDP Act 2023 makes consent a first-order constraint; retrofitting onto an
    event store is not feasible, so the `consent_records` table and `consent_recorded` event ship
    in migration 0001 (`backend-architecture.md` §12; `read-models-schema.md` §9).
  - Implementation: `classify` worker skips `analytic_rm.question_classifications` writes when no
    valid `behavioral_analytics` consent exists; the `offer_set_choice` event and `classify` job still
    flow normally, and the student experience is unaffected.
  - Traceability: SDD red test #26 (`test_classify_worker_skips_analytic_projection_without_consent`);
    DoD bullet; ADR-0014.

## Entry Template

### YYYY-MM-DD — Short title

**Phase / milestone**: Phase 0 / Phase 1 / M1 / etc.

**Spec sections used**:
- `path/to/doc.md` §section

**Work completed**:
- ...

**Decisions made**:
- ...

**Validation run**:
- ...

**Gate status**:
- Open / passed / blocked

**Open questions**:
- ...

**Next step**:
- ...

---

## Entries

### 2026-06-16 — Documentation baseline before implementation

**Phase / milestone**: Pre-implementation documentation alignment

**Spec sections used**:
- `docs/README.md` hierarchy of truth
- `docs/api/README.md`
- `docs/database/README.md`
- `docs/planning/development-approach.md` §6 and §10

**Work completed**:
- API documentation suite created under `docs/api/`.
- Database schema documentation suite created under `docs/database/`.
- Worklog, configuration reference, and delivery/operations docs initialized.

**Decisions made**:
- Student learning APIs serve both B2C and B2B after backend active-context resolution.
- Admin/auth/internal onboarding contracts are deferred.
- Redis, Celery, and TimescaleDB remain deferred scale forms.
- Render selected as the MVP deployment target for the FastAPI API and worker service.
- Conservative MVP defaults selected in `docs/configuration-reference.md`; revise only through worklog-backed config changes.

**Validation run**:
- Documentation formatting checks to be run after final sync edits.

**Gate status**:
- Pre-development documentation finalization in progress.

**Open questions**:
- Phase 0 core-bet validation has not started.

**Next step**:
- Begin Phase 0 chapter-analysis/core-question validation when documentation sync is complete.