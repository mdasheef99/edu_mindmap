# Testing Strategy

**Document Version**: 1.0 (draft)
**Status**: Proposed
**Related Documents**: `docs/planning/development-approach.md` (§6 disciplines, §8 method),
`docs/classification-reliability-protocol.md`, `docs/architecture/backend-architecture.md`,
`docs/architecture/llm-pipeline.md`, `docs/chapter-analysis-pipeline-specification.md`

---

## 1. Purpose and Principles

This document defines what is tested, at which layer, with what tooling, what gates CI, and —
equally important — what is deliberately **not** tested at MVP. It implements the testing
disciplines named in `development-approach.md` §6 as one coherent strategy.

Four principles decide every testing question:

1. **Test what carries a product guarantee first.** Category invisibility, append-only events,
   deterministic projections, tenant isolation, and version stamping are *documented product
   guarantees* (`backend-architecture.md` §2). Tests for these outrank coverage anywhere else.
2. **Pure functions get unit tests; everything around an LLM gets fixtures or golden sets.**
   LLM output is never asserted exactly in automated tests — prompts are validated by the
   golden-set protocol (`classification-reliability-protocol.md`) and pipeline verification
   gates, on their own cadence, never per-push.
3. **Projections and RLS are tested against real Postgres, never mocks.** The failure modes
   that matter (replay determinism, `SKIP LOCKED` semantics, RLS under pooled connections) do
   not exist in mocks.
4. **The CI gates are the reviewer of last resort** for AI-generated code
   (`development-approach.md` §8.3). A test that exists but does not run in CI is fiction.

---

## 2. Test Layers

### L1 — Unit tests: the pure arithmetic and rules (pytest, no I/O)

The load-bearing math is all pure functions; each gets exhaustive table-driven tests the day it
is written:

- Stage 2 code-side computation: medians, dispersion, entropy, flag thresholds
  (`classification-reliability-protocol.md` §5).
- P9 weighting formulas; P0 segmentation rules; deterministic edge-ID derivation
  (`edge_<type>_<from>_<to>`, normalized order) from the pipeline spec.
- Checkpoint trigger arithmetic (cosine similarity over engagement vectors).
- Offer-set assembly rules (discovery floor, budget caps) as far as they are code-side.
- Event payload schema validation against the registry.

### L2 — Projection replay tests (pytest + real Postgres)

For every projection, from the first one (`development-approach.md` §6.4):

- **Determinism**: append a fixture event sequence → build projection → truncate → rebuild →
  byte-identical rows (modulo `generated_at`).
- **Idempotency**: applying the same event twice changes nothing.
- **Stamping**: every derived row carries `projection_version` and source-event lineage stamps.
- **Order-independence within a batch** where the projection claims it.

### L3 — Boundary and guarantee tests

- **Import-linter contracts** (`backend-architecture.md` §4): `api/student` imports
  `domain/student` only; `generation` cannot import `classification`; etc. Runs as a CI step.
- **Category-invisibility serialization test**: for every `/v1/student/*` response model,
  assert by schema introspection that no dimensional/classification/coverage field is
  expressible. This is a structural test of `domain/student`, not a string search.
- **Tenant isolation under pooled connections** (`development-approach.md` §6.6): two tenants'
  fixture data; every student/teacher endpoint exercised through the pooled connection path;
  assert zero cross-tenant rows. Exists before any second real tenant.
- **Append-only enforcement**: UPDATE/DELETE on the events table fails at the DB privilege
  level, asserted by test.

### L4 — Integration tests (API → events → worker → projection)

One per release-critical flow (`planning/release-critical-user-flows.md`), with `llm_gateway`
replaced by recorded fixture responses:

- Phrase selection → offer set returned → `offer_set_impression` + `offer_set_choice` appended →
  `classify` job picked up via `SKIP LOCKED` → `question_classified` appended → `analytic_rm`
  row present with correct stamps.
- Node save durable before response returns; deletion cascade produces the contracted events;
  edge create/delete for both edge types; session resume returns persisted board state.
- Teacher endpoint authorization: role-gated access granted/denied per
  `teacher-access-control` rules; K-suppression applied on aggregate cells.

### L5 — LLM instrument validation (not in per-push CI)

Owned by existing protocols; this strategy only fixes their cadence:

- **Golden-set regression** per `classification-reliability-protocol.md`: runs on every Stage 2
  `prompt_version` / `model_id` change, via the replay mechanism. Deployment-gating.
- **Chapter pipeline verification gates + QA queue** per the pipeline spec (P10): run per
  chapter analysis, human-reviewed. Never automated away.
- **Stage 1 spot checks**: prompt changes require a fixed seed-input sheet re-run and eyeball
  review, recorded in the worklog. No numeric gate at MVP.

### L6 — Mobile tests

- **Jest unit tests** for Zustand store logic: board state transitions, deletion cascade
  computation, persistence serialization/deserialization round-trip, offline-reopen guards.
- **Contract fixtures shared with backend**: the session/path payloads used in L4 are the same
  fixtures the mobile tests parse, keeping the data contract honest from both sides.
- **Manual device checklist** (per milestone gate, on the reference mid-range Android device):
  gesture correctness, 60fps at 40+ nodes (M3 gate), phrase selection on both platforms,
  offline reopen, resume. No Detox/Maestro automation at MVP — its maintenance cost outweighs
  its value at this team size.

---

## 3. What Runs Where

| Trigger | Runs | Gate |
|---------|------|------|
| Every push (CI) | L1, L2, L3, L4 + import-linter + formatter | Merge-blocking |
| Stage 2 prompt/model change | L5 golden-set regression (replay) | Deployment-blocking per reliability protocol |
| Chapter analysis run | Pipeline verification gates + QA queue | Chapter-launch-blocking |
| Milestone gate | L6 manual device checklist + the milestone's named gate | Phase-gate-blocking (`development-approach.md` §5) |
| Stage 1 prompt change | L5 spot-check sheet | Worklog-recorded review |

### 3.1 Phase 2 test matrix — Curriculum Ingestion + Auth

Adds to the layers above for Phase 2
(`docs/planning/sdd/phase-2-curriculum-ingestion-sdd.md` §8). It introduces **no new layer**; it
binds Phase 2 guarantees to existing layers, so all rows are merge-blocking on every push.

| Guarantee | Layer | Test focus | Source |
|---|---|---|---|
| Ingestion determinism | **L2** | re-run P0–P4 over the same fixtures + recorded LLM responses → byte-identical `curriculum` rows (modulo timestamps) | dev-approach §6.4; SDD §8 L2 |
| Ingestion idempotency | **L2** | re-ingest same chapter → no duplicate rows; `chapter_analysis_id` + version stamps on every row | SDD §8 L2; backend-arch §7.5 |
| P0/P3/P4 determinism | L1 | deterministic segment IDs, normalized-label dedup, deterministic typed edge IDs | pipeline-spec P0/P3/P4; SDD §9 |
| Verification gate | L1 | reject uncited segment refs / malformed pass output | pipeline-spec §5 |
| Auth JWT → tenant | **L3** | JWT resolves backend tenant/role; mobile-supplied tenant ignored | backend-arch §5.4; SDD §7.3 |
| Curriculum RLS | **L3** | `curriculum` RLS denies cross-tenant rows through the pooled path | backend-arch §5.3; SDD §7.3 |
| Curriculum import rules | L3 | `chapter_analysis ⇏ classification`/`generation`/`api` | backend-arch §4; SDD §5 |
| Teacher render invisibility | L3 | `/v1/teacher/chapters/{id}` payload has no per-student fields | SDD §7.1 |
| Real-chapter session | L4 | ingest (fixtures) → `POST /v1/student/sessions` against real `chapter_id` → student-safe node | SDD §8 L4 |
| P1/P2/P4 LLM passes | L5 | fixture-keyed by `prompt_version`; schema/contract checks only, never exact text | §4; SDD §8 L5 |
| Mobile curriculum smoke | L6 | physical-device Expo smoke once the mobile curriculum surface exists (deferred) | SDD §7.4 |

---

## 4. Tooling and Fixtures

| Concern | Choice |
|---------|--------|
| Backend test runner | pytest + pytest-asyncio; httpx `TestClient` for API tests |
| Test database | Real Postgres via testcontainers (or `supabase start` locally); one schema per test session, truncate between tests |
| LLM stubbing | Recorded JSON fixture responses checked into the repo, keyed by prompt version — never live calls in CI |
| Canonical fixtures | The Phase 0 Electricity chapter artifacts (P0–P4 outputs) are the standing fixture set for everything downstream |
| Mobile | Jest + React Native Testing Library for store/logic tests |
| Static gates | import-linter, ruff (lint + format), mypy on `domain/`, `events/`, `projections/` at minimum |

---

## 5. Deliberately Not Tested at MVP

- **Load/performance testing** of the backend (single-container scale is sufficient; revisit
  per `scalability-analysis.md` triggers). The only performance gate is the M3 device gate.
- **Mobile E2E automation** (Detox/Maestro) — manual checklist instead, per §2 L6.
- **Visual regression testing** — premature before a design system exists.
- **Security penetration testing** — revisit at B2B pilot; RLS isolation (L3) is the bounded
  MVP security test.
- **Chaos/failure injection** — the worker retry path gets one L4 test (job fails → retries →
  dead-letters); nothing beyond that.

## 6. Definition of Done (per increment)

An increment (`development-approach.md` §8.2) is done when: its L1 tests exist and pass; any
new projection has L2 tests; any new endpoint has its L4 flow covered or extended; CI is green
including import-linter; and any prompt change followed its L5 cadence. Code merged without
these is not done, regardless of whether it works in a demo.
