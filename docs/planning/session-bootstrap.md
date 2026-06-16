# Session Bootstrap — Context Key (v1.3+)

**Document Version**: 1.0  
**Status**: Active — paste at the start of every new AI session  
**Related Documents**: `docs/planning/sdd/phase-1-walking-skeleton-sdd.md` (active blueprint), `docs/planning/worklog.md` (live progress tracker)

---

## Purpose

This is the canonical **Context Key** in the project's Context Continuity Framework. It exists so a new AI session re-establishes the milestone, the source-of-truth hierarchy, and the non-negotiable invariants *before* reading anything else — preventing silent re-derivation of rejected legacy patterns.

## Framework map (three artifacts)

| Artifact | Role | File |
|---|---|---|
| Blueprint | Authoritative design for the current increment | `docs/planning/sdd/phase-1-walking-skeleton-sdd.md` |
| Tracker | Live status of red tests, DoD items, migrations | `docs/planning/worklog.md` |
| Context Key | This file — hierarchy + invariants + blacklist | `docs/planning/session-bootstrap.md` |

## How a new session must use this

1. Read this Context Key first.
2. Open the **active SDD** (Blueprint) and the **worklog tracker** (Tracker).
3. Cross-reference: identify current development state, files in scope, and the governing strategy.
4. **State the current Phase 1 status back to the user before proposing or editing anything.**

## Maintenance rule

Keep one canonical copy. Update this file in the **same change** as any primary-doc or milestone change (swap the ACTIVE SDD line and OPEN DECISION block when an increment closes). Never retype the header from memory — paste the block below verbatim.

---

## Bootstrap Header (copy-paste at session start)

```
=== MINDMAP PROJECT — CONTEXT BOOTSTRAP (v1.3+) ===

ACTIVE MILESTONE: Phase 1 — Walking Skeleton (precedes M1).
ACTIVE SDD (the ONLY increment in flight):
  docs/planning/sdd/phase-1-walking-skeleton-sdd.md
LIVE TRACKER: docs/planning/worklog.md (Phase 1 status table).
Do not design Phase 2/3 work (Teacher V3, advanced analytics, podcast,
checkpoints) unless explicitly opened. Defer-without-guilt.

SOURCE-OF-TRUTH HIERARCHY (authoritative, in order — on conflict, higher wins):
  1. docs/planning/development-approach.md
  2. docs/architecture/backend-architecture.md
  3. docs/architecture/adr-log.md
  4. docs/planning/session-path-data-contract.md
  5. docs/prd/master-prd.md
  6. docs/mvp-features-specification.md
Supporting (must trace upward): docs/api/*, docs/database/*,
docs/planning/testing-strategy.md, docs/configuration-reference.md, active SDD.

IGNORE / DO NOT CITE (superseded, pre-v1.3): docs/documentation-gap-analysis.md
and anything proposing Redis Streams, Celery, TimescaleDB, exploration_events /
learning_sessions / path_patterns tables, or docs/{database,api}-specification.md.

NON-NEGOTIABLE INVARIANTS (executable, merge-blocking):
  • Category Invisibility — physical student_rm vs analytic_rm split; /v1/student
    NEVER reads analytic_rm, returns no analytic fields, exposes no raw event endpoint.
    Forbidden student_rm columns: dimension/classification/coverage/gap/score/
    confidence/entropy/vector/profile/weight/propensity/probe/teacher_*.
  • Organic-First — classification is post-hoc & async. SELECTED offer_set_choice
    enqueues `classify`; DISMISSED enqueues nothing. Student response NEVER waits
    on a job. generation ⇏ classification; api/student ⇏ analytic (import-linter).
  • Tenant Isolation under POOLED connections — tenant_id on every row; backend-
    resolved tenant (mobile-supplied tenant_id is NEVER authoritative); SET LOCAL
    app.tenant_id; RLS as DB-level backstop. Isolation tests run THROUGH the pool.
  • Event Sourcing — append-only `events` (no UPDATE/DELETE); in-code registry
    validates type+version; worker-only events (question_classified) rejected from
    clients; every derived row carries projection_version + prompt_version/model_id
    + lineage; projections are replay-deterministic (byte-identical) and idempotent.

JOB QUEUE: Postgres SELECT … FOR UPDATE SKIP LOCKED ONLY (ADR-0002).
  JOB_MAX_ATTEMPTS=5 dead-letter; JOB_QUEUE_BACKEND=postgres_skip_locked.
  No Redis/Celery in MVP. No mobile-side AI/TTS credentials (backend gateway only).
  LLM in CI = recorded fixtures (LLM_CI_MODE). Cost/usage counter from first call.
CONSTANTS: K=5 small-cohort suppression; 0.35 checkpoint cosine threshold.

OPEN DECISION (resolve before migration 0001): consent gate on the classify →
analytic_rm projection (DPDP; backend-architecture §12 "from the first migration";
read-models-schema §9). Either gate it in Phase 1 or record an explicit deferral
ADR — do NOT silently omit.

BEHAVIORAL RULES:
  • Every requirement/edit must cite a source-of-truth §. Never originate requirements.
  • Red tests before production code (active SDD §9).
  • Deterministic logic → TDD; LLM output → fixtures + schema/contract checks, never
    assert exact model text.
  • FIRST ACTION: read the active SDD + worklog + hierarchy before proposing or
    editing anything. State current Phase 1 status back before acting.
=== END BOOTSTRAP ===
```
