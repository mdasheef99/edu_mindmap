---
type: always_apply
---
# Mindmap Canon (v1.3+) — merge-blocking

ACTIVE MILESTONE: Phase 1 — Walking Skeleton (precedes M1). Do not design Phase 2/3
work (Teacher V3, advanced analytics, podcast, checkpoints) unless explicitly opened.
ACTIVE SDD (the ONLY increment in flight): docs/planning/sdd/phase-1-walking-skeleton-sdd.md
LIVE TRACKER: docs/planning/worklog.md (Phase 1 Live Tracker + Open Decisions).
OPEN DECISION: consent gate on `classify` → `analytic_rm` projection — RESOLVED 2026-06-17.
Decision: implement the gate in Phase 1 (Option A). The `consent_records` table and
`consent_recorded` event ship in migration 0001; the `classify` worker skips `analytic_rm`
writes without valid `behavioral_analytics` consent. See ADR-0014, SDD red test #26, and
`docs/planning/worklog.md` Open Decisions.

## Source-of-Truth Hierarchy (authoritative, in order — on conflict, higher wins)

1. `docs/planning/development-approach.md`
2. `docs/architecture/backend-architecture.md`
3. `docs/architecture/adr-log.md`
4. `docs/planning/session-path-data-contract.md`
5. `docs/prd/master-prd.md`
6. `docs/mvp-features-specification.md`

Supporting (must trace upward): `docs/api/*`, `docs/database/*`,
`docs/planning/testing-strategy.md`, `docs/configuration-reference.md`, the active SDD.

### Document-usage instruction
The agent must refer to this Source-of-Truth hierarchy to resolve any ambiguity or
design doubt. Every requirement or code edit must be traceable to a specific section
(§) in these documents. If a conflict arises, higher-ranked documents in the hierarchy
take precedence. Do not originate requirements outside of this framework.

## IGNORE / DO NOT CITE (superseded, pre-v1.3)
`docs/documentation-gap-analysis.md` and anything proposing Redis Streams, Celery,
TimescaleDB, `exploration_events` / `learning_sessions` / `path_patterns` tables, or
`docs/{database,api}-specification.md`.

## Non-negotiable invariants (executable, merge-blocking)
- **Category Invisibility** — physical `student_rm` vs `analytic_rm` split; `/v1/student`
  NEVER reads `analytic_rm`, returns no analytic fields, exposes no raw event endpoint.
  Forbidden `student_rm` columns: dimension/classification/coverage/gap/score/
  confidence/entropy/vector/profile/weight/propensity/probe/teacher_*.
- **Organic-First** — classification is post-hoc & async. SELECTED `offer_set_choice`
  enqueues `classify`; DISMISSED enqueues nothing. Student response NEVER waits on a
  job. generation ⇏ classification; api/student ⇏ analytic (import-linter).
- **Tenant Isolation under POOLED connections** — tenant_id on every row; backend-
  resolved tenant (mobile-supplied tenant_id is NEVER authoritative); SET LOCAL
  app.tenant_id; RLS as DB-level backstop. Isolation tests run THROUGH the pool.
- **Event Sourcing** — append-only `events` (no UPDATE/DELETE); in-code registry
  validates type+version; worker-only events (`question_classified`) rejected from
  clients; every derived row carries projection_version + prompt_version/model_id +
  lineage; projections are replay-deterministic (byte-identical) and idempotent.

## Job queue & constraints
- Postgres `SELECT … FOR UPDATE SKIP LOCKED` ONLY (ADR-0002). JOB_MAX_ATTEMPTS=5
  dead-letter; JOB_QUEUE_BACKEND=postgres_skip_locked. No Redis/Celery in MVP.
- No mobile-side AI/TTS credentials (backend gateway only). LLM in CI = recorded
  fixtures (LLM_CI_MODE). Cost/usage counter from first call.
- Constants: K=5 small-cohort suppression; 0.35 checkpoint cosine threshold.

## Behavioral rules
- Every requirement/edit must cite a source-of-truth §. Never originate requirements.
- Red tests before production code (active SDD §9).
- Deterministic logic → TDD; LLM output → fixtures + schema/contract checks, never
  assert exact model text.
- FIRST ACTION: read the active SDD + worklog + hierarchy before proposing or editing
  anything. State current Phase 1 status back to the user before acting.
