---
type: always_apply
---
# Mindmap Canon (v1.3+) — merge-blocking

ACTIVE MILESTONE: Phase 3 — M4 Curriculum entry + Supabase Auth, **CLOSED** (2026-07-11).
INTEGRATION STATUS: the closed M4 implementation is reconstructed on `main`. A bounded post-M4,
pre-M5 canvas position-lifecycle stabilization is locally complete on
`codex/integrate-canvas-position-lifecycle` from `f1308fc`; all branch-local gates are green and
owner approval is pending before any push or draft PR. M5 remains frozen and has not started.
Next milestone is M5 Checkpoints; it has not started. The earlier browser path was a local in-memory
smoke prototype, not a durable production-runtime verification. Production API composition,
live restart durability, consent-aware worker projection, TypeScript/Jest/pytest/import-linter,
Android bundling, native user flow, and non-bypass pooled-RLS isolation are verified.
The 2026-07-11 physical-device gate found dashboard latency, repeated consent prompting, and
post-signout re-login `Invalid Supabase token` failures. Remediation cached Supabase JWKS clients,
returned persisted behavioral consent from bootstrap, moved dashboard rendering ahead of the
sequential curriculum fetches, performs Supabase remote logout before local session clearing, and
adds a bounded 30-second ES256 clock-skew tolerance after live diagnostics identified a zero-leeway
`ImmatureSignatureError`. Final physical-device validation verifies post-fix sign-in/restoration,
dashboard, the API-derived Electricity path, resume/hydration, new-session creation, branching, and
active writes. The live non-bypass pooled-RLS test is green. Interactive web is explicitly excluded
from the M4 closure gate; Expo web export with CanvasKit remains green and interactive browser smoke
is retained as a non-blocking follow-up.
M4 scope: B2C individual signup first via Supabase email/password, Class 10 → CBSE → Science →
Electricity launch curriculum path, dashboard re-entry, consent capture, and a deterministic
fixture-backed Electricity generation simulator (~10 nodes) that mimics real backend/event/canvas
node creation. Phone/OTP auth, B2B roster/invite activation, admin/content panels, and live LLM
generation are deferred. Supabase MCP was reinstalled and verified against the correct Mindmap
project `jbmqyxhrmcbdgardamrp`; migrations `20260702173751 / m4_catalog_auth_seed` and
`20260710075416 / m4_runtime_remediation` are applied there. The forward migration adds/backfills
required catalog `tenant_id` columns, constraints, indexes, and RLS policies. Fresh live readback
confirms all 15 required operational/catalog/read-model tables have `tenant_id` and RLS enabled.
The old wrong project (`ahntbtktjjmvfosgkmgn`, `Bookconnect_reactexpo`) must not be used.
Current branch-local automated gates: backend 164 passed / 3 skipped, direct import-linter 4/4
contracts kept, mobile 35 suites / 159 tests passed, App/Canvas TypeScript green, Ruff format/lint
green, and mypy green. Expo Android bundle and physical-device evidence remain historical; the
canvas stabilization did not rerun performance or physical-device gates.
Phase 3 M3.6 Canvas Controls is LOCALLY COMPLETE (2026-06-30): explicit zoom in/out toolbar
controls, fit-to-screen, reset view, zoom percentage readout, and optional snap-to-grid drag-end
toggle. The pre-M4 TypeScript/Jest config blocker was resolved on 2026-07-01; canvas TypeScript and
full mobile Jest were green in `worklog-v8.md`.
Seams A/B/C and Tier 2 event-emission wiring are implemented and tested: backend pytest
120/120 green, mobile Jest 92/92 green, import-linter green. M3-C closes the three
"compute-ready, transport-missing" gaps discovered in the 2026-06-23 audit (RCA).
SkiaCanvas orchestrator refactor COMPLETE (2026-06-25); the later 2026-07-13 position-lifecycle
stabilization removed `useLiveDragOverride` after edge/label drag geometry moved entirely to
UI-thread SharedValues. `SkiaCanvas.tsx` remains within the 300–350 line source limit.
Phase 3 M3.5 Frontend Readiness bridge is VERIFIED / COMPLETE (2026-06-25): learner-safe
NodeChip text, SkiaCanvas edge-`+` neutral error banner, and useSessionHydration title/content
persistence are implemented and verified by automated Jest tests plus physical device Expo Go
smoke; 18 suites / 97 mobile Jest green. The former TS2688 Jest type-definition blocker was
resolved before M4; current `tsc --noEmit` is green.
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
ACTIVE LOCAL INTEGRATION SDD: `docs/planning/sdd/canvas-position-write-lifecycle-sdd.md`
(locally complete 2026-07-13; owner approval pending). CLOSED SDD:
docs/planning/sdd/phase-3-m4-runtime-closure-remediation-sdd.md v0.3 (M4 remediation;
production Postgres composition, durable auth/consent/session flow, mobile dashboard/resume, and
platform closure gates; closed 2026-07-11). Parent SDD:
phase-3-m4-curriculum-auth-sdd.md v0.6 (closed 2026-07-11).
Prior closed SDDs: docs/planning/sdd/phase-3-m3-6-canvas-controls-sdd.md (M3.6, LOCALLY COMPLETE
2026-06-30; toolbar zoom controls, fit/reset view, zoom readout, snap-to-grid drag-end toggle);
docs/planning/sdd/phase-3-m3-5-frontend-readiness-sdd.md (M3.5,
VERIFIED / COMPLETE 2026-06-25; F1-F7 frontend readiness + physical device Expo Go smoke);
docs/planning/sdd/phase-3-m3c-infrastructure-remediation-sdd.md (M3-C, 2026-06-24);
docs/planning/sdd/phase-3-m3-canvas-sdd.md + phase-3-m3b-canvas-feature-parity-sdd.md
(M3/M3-B, closed 2026-06-22); docs/planning/sdd/phase-3-phrase-selection-sdd.md (M2, closed
2026-06-20).
LIVE TRACKER: docs/planning/worklog-v11.md (`worklog-v10.md` preserved/closed at 348 lines;
`worklog-v9.md` preserved/closed at 567 lines).
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
