---
type: always_apply
---
# Mindmap Canon (v1.3+) — merge-blocking

ACTIVE MILESTONE: Phase 3 — M3-C Infrastructure Remediation LOCALLY COMPLETE (2026-06-24).
Seams A/B/C and Tier 2 event-emission wiring are implemented and tested: backend pytest
120/120 green, mobile Jest 92/92 green, import-linter green. M3-C closes the three
"compute-ready, transport-missing" gaps discovered in the 2026-06-23 audit (RCA). Next
milestone: M4 Curriculum entry + Supabase Auth.
SkiaCanvas orchestrator refactor COMPLETE (2026-06-25): SkiaCanvas.tsx reduced from 372 to
242 lines (canon limit resolved) by extracting useDeletionReconciliation, useDiscoveryManager,
useLiveDragOverride, and useCanvasRenderData; 17 new unit tests; 22 suites / 112 mobile Jest
green. M3-B/M3-C carried housekeeping item closed. commit 4645bbd on phase-3-m3.
Phase 3 M3 + M3-B Canvas maturation is CLOSED locally (2026-06-22): M3 base (pan/zoom/gestures
via skia + reanimated, node visualization, 65-node limits, 60fps at 40+ nodes —
development-approach.md §5 M3) and M3-B supplemental (edge labels F1, edge-`+` discovery UI F2,
node selection/toolbar F3, native view culling F5, node-limit mobile UI F6) are both locally
complete: 82/82 mobile Jest green. Deferred operational gates remain non-blocking: Stage 2 device
60fps re-run at 40+ nodes and Stage 3 65-node smoke.
Phase 3 M2 Phrase Selection is CLOSED (2026-06-20): the §5 M2 user/device gate was met on
a physical Android device; the "questions aren't tappable" fatal risk (§9) is retired.
Phase 3 M1 is Locally Complete / Operationally Pending: session persistence/resume,
offer-set logging, edge-`+` branching, deletion cascade, and event-only session-path
reconstruction are green locally; Render backend+worker live verification and physical-
device Expo smoke remain deferred operational gates. Do not attempt operational verification
unless explicitly requested.
Phase 1 and Phase 2 are CLOSED locally (2026-06-18). Do not reopen closed items unless
explicitly requested.
ACTIVE SDD: docs/planning/sdd/phase-3-m3c-infrastructure-remediation-sdd.md (M3-C, LOCALLY
COMPLETE 2026-06-24; Seam A/B/C + Tier 2 event emission + App.tsx real hydration). Prior
closed SDDs: docs/planning/sdd/phase-3-m3-canvas-sdd.md + phase-3-m3b-canvas-feature-parity-sdd.md
(M3/M3-B, closed 2026-06-22); docs/planning/sdd/phase-3-phrase-selection-sdd.md (M2, closed
2026-06-20).
LIVE TRACKER: docs/planning/worklog-v8.md (worklog-v7.md rotated at 405 lines, 2026-06-25;
worklog-v6.md rotated past the ~350-line threshold, 2026-06-21; worklog-v5.md rotated at 346 lines).
CLOSED DECISION (Phase 1): consent gate on `classify` → `analytic_rm` — RESOLVED 2026-06-17.
See ADR-0014, worklog.md Open Decisions.

## Source-of-Truth Hierarchy (authoritative, in order — on conflict, higher wins)

1. `docs/planning/development-approach.md`
2. `docs/architecture/backend-architecture.md`
3. `docs/architecture/adr-log.md` then active continuation `docs/architecture/adr-log-02.md`
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

## Code organization constraints
- Source files should stay under 300–350 lines. If a file approaches or exceeds
  the limit, refactor into cohesive modules before adding behavior.
- Prefer small, typed, reviewable diffs; keep routers, domain logic, adapters,
  projections, worker orchestration, and observability helpers separated.
- Repeated infrastructure patterns (tenant GUCs, RLS helpers, queue claims,
  usage accounting) belong in shared helpers with tests, not copy-paste blocks.

## Behavioral rules
- Every requirement/edit must cite a source-of-truth §. Never originate requirements.
- Red tests before production code (active SDD §9).
- Deterministic logic → TDD; LLM output → fixtures + schema/contract checks, never
  assert exact model text.
- After running Python tests, delete generated `*.pyc` files before ending the work session
  and verify the remaining `.pyc` count is 0.
- FIRST ACTION: read the active SDD + worklog + hierarchy before proposing or editing
  anything. State current milestone status back to the user before acting.
