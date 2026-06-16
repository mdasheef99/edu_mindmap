# Architecture Decision Record (ADR) Log

**Document Version**: 1.0
**Status**: Living document — append new ADRs; never edit accepted ones (supersede instead)

This log records significant architectural decisions already embedded in the documentation
suite, so their context and consequences survive personnel and time. It extends (does not
replace) the rationale sections of `docs/architecture/backend-architecture.md`,
`docs/chapter-analysis-pipeline-specification.md`, and `docs/planning/backend-mvp-strategy.md`
by giving each decision a stable number and status.

**Template**: each ADR records *Status* (Proposed / Accepted / Superseded by ADR-NNNN),
*Context* (the forces in play), *Decision* (what was chosen), *Consequences* (what follows,
good and bad), and *References* (where the decision is specified in detail).

**Conventions**: numbered ADR-0001 upward in decision order; a reversed decision is never
deleted — it is marked Superseded with a pointer to its replacement.

---

## ADR-0001 — Event-sourced modular monolith over microservices

**Status**: Accepted

**Context**: The framework is revisable by design — classification is post-hoc, categories are
provisional, and interpretation policies will change. Every analytic artifact must be
re-derivable from raw history under new versions. Meanwhile the team is small, and the
boundaries that actually carry product guarantees are *data-visibility* boundaries (student
vs. analytic), not deployment boundaries.

**Decision**: One deployable FastAPI application plus a worker process sharing one codebase and
one Postgres. The write path is an append-only event store; everything derived is a rebuildable
projection. Module boundaries are logical, enforced by import-linter contracts in CI, and serve
as extraction seams only if scale later demands it.

**Consequences**:
- Replay/reinterpretation is structurally cheap — the framework's revisability is real.
- One unit to deploy, debug, and reason about; no distributed-systems tax at MVP scale.
- Discipline lives in import rules and DB grants rather than network boundaries; CI must
  actually enforce the contracts or the boundaries rot.
- Event-store growth requires partitioning and archival policy (accepted: monthly partitions).

**References**: `docs/architecture/backend-architecture.md` §2–§4, §6, §13.

---

## ADR-0002 — Postgres `SKIP LOCKED` jobs table instead of Redis/Celery for MVP

**Status**: Accepted

**Context**: Classification, compression, projections, replay, and podcast generation need an
async lane. Redis + Celery is the conventional choice but adds infrastructure, configuration,
and failure modes before any load justifies them. `docs/planning/backend-mvp-strategy.md`
explicitly guards against premature scale infrastructure.

**Decision**: MVP queue is a `jobs` table in the existing Postgres, claimed with
`SELECT ... FOR UPDATE SKIP LOCKED`, one worker process, retries with exponential backoff,
dead-lettering at 5 attempts. The queue interface is one thin module (`workers/queue.py`) so a
later swap to Redis changes one module, not the handlers.

**Consequences**:
- Zero new infrastructure; transactional enqueue with the events it reacts to.
- Adequate to thousands of jobs/minute — far beyond MVP needs.
- Polling latency and queue-on-the-database load are accepted at this scale; the swap path is
  pre-designed and triggered by queue-depth/latency data, not anticipation.

**References**: `docs/architecture/backend-architecture.md` §8.1; `docs/planning/backend-mvp-strategy.md` §10.

---

## ADR-0003 — Two physically separate read models for category invisibility

**Status**: Accepted

**Context**: Category invisibility to students is a hard product guarantee — students must
never see dimensional labels, scores, or coverage. A single read model filtered per role at the
response layer fails open: one missed filter leaks the framework to students.

**Decision**: Two schemas: `student_rm` (render/resume state only — **cannot express**
dimensional data; no such columns exist) and `analytic_rm` (everything dimensional;
rebuildable by definition). Separate API routers serialize from separate type universes;
`api/student` cannot import analytic domain types (import-linter contract), so a leak is a type
error before it is a runtime bug.

**Consequences**:
- Invisibility is structural, not disciplinary — enforced by schema, types, and CI.
- Some data is modeled twice; projections do the bridging work.
- Cross-cutting features (e.g., future learner-facing guidance) must consume *translated*,
  category-neutral signals via explicit new projections rather than peeking at `analytic_rm`.

**References**: `docs/architecture/backend-architecture.md` §2.2, §4, §7, §11.

---

## ADR-0004 — Organic-first generation with post-hoc classification

**Status**: Accepted

**Context**: The 8-dimension framework could drive generation directly (generate "a *delimit*
question"). But dimension-targeted generation produces stilted questions, leaks framework
vocabulary into student surfaces, and — worst — makes the observational data circular: paths
would reflect our targeting, not student inclination. The framework's categories are
provisional and must remain falsifiable.

**Decision**: Stage 1 generates questions organically (grounded in chapter material, no
dimension targeting, meta-language prohibited). Stage 2 classifies *after* selection, async,
invisibly. Classification never blocks or shapes the student's immediate experience; a 30%
organic-discovery floor protects against steering even at the ranking layer.

**Consequences**:
- Path data reflects genuine student choice — the framework can be tested against it.
- Classification lag is irrelevant by design; the async lane (ADR-0002) is sufficient.
- Coverage cannot be "forced"; gaps are evidence, not failures to remediate by generation.
- Cold-start needs seed questions (chapter-analysis P8) since runtime cannot target gaps.

**References**: `docs/framework-design-philosophy.md`; `docs/architecture/llm-pipeline.md`;
`docs/chapter-analysis-pipeline-specification.md` §6.2–§6.3; `docs/measurement-and-experimentation.md` §1.

---

## ADR-0005 — Median-of-3 classification with dispersion logging

**Status**: Accepted

**Context**: Single LLM classification calls are noisy even at temperature 0 (API-level
nondeterminism, near-tie instability). Downstream consumers (teacher-support views, shift
detection) need to know not just the scores but how trustworthy each classification is.

**Decision**: Every question is classified three times (temperature 0); code takes the
per-dimension median as the stored vector and logs per-dimension dispersion (max − min).
Dispersion > 0.3 on any dimension flags `needs_review`. Scores use the discrete ordinal scale
{0.0, 0.3, 0.6, 0.9} so disagreement is a real category step, not jitter.

**Consequences**:
- 3× classification cost — acceptable because Haiku is cheap and classification is async.
- Per-question reliability becomes a stored, filterable quantity rather than a guess.
- Agreement statistics (Krippendorff's α, ICC) become meaningful on the discrete scale.

**References**: `docs/chapter-analysis-pipeline-specification.md` §6.2;
`docs/classification-reliability-protocol.md` §5.

---

## ADR-0006 — All arithmetic in code, never by the LLM

**Status**: Accepted

**Context**: An earlier classifier spec asked the model to compute and return its own Shannon
entropy (`classification_entropy` in `docs/architecture/llm-pipeline.md`). LLMs are unreliable
at arithmetic, and a model grading its own confidence with a number it computed itself is
unauditable. The same risk applies to richness scores, weight modifiers, medians, and
statistics anywhere in the pipeline.

**Decision**: LLMs return *judgments only* (scores, verdicts, text). Every computed quantity —
entropy, medians, dispersion, richness, weight modifiers, cosine distances, agreement
statistics, flags — is computed in code (`classification`, `llm_gateway`, chapter-analysis P9).
Any prompt requesting a computed quantity fails review.

**Consequences**:
- Quantities are exact, reproducible, and unit-testable; threshold changes need no prompt edits.
- Supersedes the `classification_entropy` field and prompt instruction in
  `docs/architecture/llm-pipeline.md` (annotation pending there).
- Slightly larger code surface; the `llm_gateway`/`classification` modules own the arithmetic.

**References**: `docs/architecture/backend-architecture.md` §9.3;
`docs/chapter-analysis-pipeline-specification.md` P9, §6.2, Appendix A;
`docs/classification-reliability-protocol.md` §11.

---

## ADR-0007 — Single shared `individual` tenant for all B2C users

**Status**: Accepted

**Context**: Multi-tenancy is required for B2B schools (tenant = isolation unit). B2C users
need isolation too, but one tenant per consumer would mean millions of tenant rows and a
divergent query model between B2C and B2B code paths.

**Decision**: All individual consumers live in one shared tenant of `kind = individual`; their
isolation unit within it is `student_id` (ownership RLS policies). Every query in the system is
therefore tenant-scoped first, then ownership-scoped — one uniform model for both businesses.

**Consequences**:
- No per-user tenant bookkeeping; B2C and B2B share every code path.
- Product behavior is identical across kinds; differences confine to account management,
  analytic visibility, and consent path.
- Moves between kinds (family joins a school plan) are explicit, audited `tenant_migration`
  events; historical-event transfer is a consent decision, not a technical default.

**References**: `docs/architecture/backend-architecture.md` §5.1, §5.5.

---

## ADR-0008 — Application-level tenancy as mechanism, RLS as backstop

**Status**: Accepted

**Context**: Tenant isolation can be enforced in the application (resolve memberships, scope
every query) or in the database (Postgres Row-Level Security). Each alone is insufficient:
application checks can be forgotten on one endpoint; RLS policies are hard to express for
role-and-relationship rules (e.g., teacher scope = active membership × active assignment).

**Decision**: Both, with defined roles. The `tenancy` module is the *mechanism*: it resolves
`(user → memberships → tenant, role, classes)` once per request and injects an authorization
context every router consumes. RLS on every table (policies on `tenant_id`, set per-connection
via `SET LOCAL app.tenant_id`) is the *backstop* that catches any application-layer mistake.

**Consequences**:
- A missed application check fails closed (RLS blocks), not open.
- Every table must carry `tenant_id` from migration 0001 — retrofitting onto an event store
  is not feasible, so this shipped as a day-one rule.
- Modest per-request overhead for membership resolution; cacheable if it ever matters.

**References**: `docs/architecture/backend-architecture.md` §2.5, §5.3, §5.4.

---

## ADR-0009 — Direct Anthropic API calls; no LangChain or agent frameworks

**Status**: Accepted

**Context**: The system makes many LLM calls (generation, classification, chapter analysis,
compression, podcast scripts), all of which need strict structured output, version stamping,
cost accounting, and budget guards. Orchestration frameworks (LangChain et al.) abstract the
API surface but obscure prompts, add dependency churn, and make exact-prompt versioning — which
the measurement design depends on — harder, while providing abstractions (chains, agents,
memory) this product does not use.

**Decision**: Direct Anthropic API calls through a single `llm_gateway` module — the only
module permitted to construct a model client (import rule). Structured output via tool-use JSON
schema / Instructor with Pydantic. No LangChain, no agent framework.

**Consequences**:
- Prompts are first-class, versioned artifacts; `prompt_version`/`model_id` stamping is exact.
- One chokepoint implements retries, cost rows, budget guards, and key custody.
- Provider portability is a deliberate trade-away; switching providers means touching one
  module, which is acceptable.

**References**: `docs/architecture/backend-architecture.md` §3, §4.4, §9;
`docs/architecture/llm-pipeline.md`.

---

## ADR-0010 — No ML training in Phases 1–3; statistics over projections only

**Status**: Accepted

**Context**: The obvious ed-tech move is training models on behavioral data (mastery
prediction, recommendation). But the framework's categories are provisional and unvalidated —
training on them would bake unproven constructs into opaque models; DPDP constraints on
children's behavioral data make trained per-student models a compliance hazard; and trained
models would compromise the interpretability the teacher-facing claims depend on.

**Decision**: Phases 1–3 use no trained/learned models on student data. All interpretation is
deterministic statistics over event projections (coverage, distributions, shift detection by
cosine distance, agreement statistics). LLMs are used for generation and classification but are
not trained or fine-tuned on student data. No feature stores, no training infrastructure.

**Consequences**:
- Every teacher-facing claim is traceable to countable events — auditable and explainable.
- Personalization ceiling is accepted: ranking policies stay rule-based/statistical with
  logged propensities (which also makes future off-policy evaluation possible).
- The framework must be validated (measurement spec, reliability protocol, outcome
  instrumentation) *before* any learning system could be justified in later phases.

**References**: `docs/architecture/backend-architecture.md` §13;
`docs/framework-design-philosophy.md`; `docs/measurement-and-experimentation.md`;
`docs/teacher-dashboard-specification.md` §8.3.

---

## ADR-0011 — Chapter topology as a second post-hoc analytic axis

**Status**: Proposed (spec drafted at v0.1)

**Context**: The dimensional framework measures *how* a student engages each concept but is
blind to structure — a chapter is an argument with a shape (concepts, typed edges, traversal
order, outcome-anchored subgraphs), and `coverage_by_concept` is a bag-of-nodes measure. The
authority's intended topology is recoverable from material the pipeline already stores (P0
segment order, P4 edges, P5 reverse index, end-of-chapter questions).

**Decision**: Add a structural axis as pure post-hoc interpretation: two offline passes (P12
code-only metrics, P13 outcome-to-subgraph mapping), deterministic code-assigned edge IDs after
P4, edge-level attribution in the existing Stage 2 call (`engaged_concepts` +
`relation_engaged`, majority vote across 3 runs, disagreement → `false`), and rebuildable
projections (`coverage_by_pair`, `realized_subgraph`, `graph_diff`). Graph measures are computed
in code (extending ADR-0006); no graph database (reaffirming the backend's rejected-alternatives
table). Students never see the map (extending ADR-0003: nothing topological enters `student_rm`).

**Consequences**:
- The teacher surface gains relational claims ("explored both, never crossed between them")
  traceable to countable events and citable passages.
- One added field set in an existing LLM call; everything else is offline passes and SQL/code
  projections — no new runtime latency.
- Edge-level claims require golden-set attribution validation at P10 before rendering; below
  threshold, surfaces degrade to node-level coverage.

**References**: `docs/chapter-topology-specification.md`;
`docs/chapter-analysis-pipeline-specification.md` §6.2 item 6, P4 edge IDs;
`docs/teacher-dashboard-specification.md` §5.3 panel 3g.

---

## ADR-0012 — Offer-set steering as curation, never generation

**Status**: Proposed (ships separately, experiment-flagged; pipeline spec §6.3 unamended until then)

**Context**: The graph diff identifies high-criticality edges a student has not traversed.
Pushing students there by *generating* targeted bridge questions would violate organic-first
(ADR-0004) and make path data unreadable as evidence of genuine choice.

**Decision**: Steering, if shipped, operates only at the offer-set ranking layer: among
organically generated candidates, the policy may *prefer* one whose attribution engages a
missing edge — if one exists in the pool. No candidate is fabricated; Stage 1 stays blind to
the diff. Budget-capped per session (initial k = 2), logged with `steer_reason` and
propensities, and subject to the 30% discovery floor.

**Consequences**:
- The menu is curated, never the mandate; off-policy evaluation remains possible because
  steering is fully logged.
- Generation provenance stays clean: every question remains attributable to chapter material
  and session context alone.
- Requires a precise amendment to the pipeline spec's "no engineered bridge questions" clause
  at ship time (topology spec §7.3); until then the clause stands as written.

**References**: `docs/chapter-topology-specification.md` §7;
`docs/measurement-and-experimentation.md` (discovery floor, propensity logging).

---

## ADR-0013 — Hybrid Mobile Canvas Architecture

**Status**: Accepted

**Context**: The learner's primary interaction surface is a gesture-driven mind-map canvas with
up to 65 nodes, requiring 60fps pan/zoom performance on mid-range Android devices. A purely
native canvas (e.g., SVG) does not scale to 40+ connected nodes with Bézier edge rendering at
target frame rates. A purely Skia/GL canvas sacrifices native text selection, which is required
for the primary branching mechanism (phrase-selection inside AI node content, per
`mobile-features-core-ui.md` §4.1).

**Decision**: Adopt a hybrid architecture for the mobile canvas:
- `react-native-skia` renders the board background and all edges (Bézier curves) at 60fps;
- `react-native-gesture-handler` + `react-native-reanimated` drive pan/zoom on the UI thread;
- `Native Views` (standard React Native components) render the content of each node, preserving
  native text selection, accessibility, and input behavior;
- `Expo` (dev builds) is the delivery framework; `Zustand` manages state; `AsyncStorage`
  persists session state locally; `MMKV` adoption is deferred until a measured performance
  need arises.

**Consequences**:
- The integration seam between Skia (coordinates) and native Views (coordinates) is the
  highest engineering risk in the mobile codebase; layout math must be maintained in both
  systems and kept consistent.
- Node positioning must be shared state between Zustand (board layout) and native View props.
- Performance gates (M3, `development-approach.md` §5) are judged on a physical mid-range
  Android device, never a simulator.
- The "Reader bottom-sheet" fallback for phrase selection (per `mobile-features-core-ui.md`)
  is the primary path at MVP; in-node text selection is an enhancement after the seam is
  proven stable.

**References**: `docs/planning/development-approach.md` §7; `docs/mobile-features-core-ui.md`
§4.1; `research/indian-student-market-analysis.md` (device targets).

---

## Index

| ADR | Title | Status |
|-----|-------|--------|
| 0001 | Event-sourced modular monolith over microservices | Accepted |
| 0002 | Postgres `SKIP LOCKED` jobs table instead of Redis/Celery for MVP | Accepted |
| 0003 | Two physically separate read models for category invisibility | Accepted |
| 0004 | Organic-first generation with post-hoc classification | Accepted |
| 0005 | Median-of-3 classification with dispersion logging | Accepted |
| 0006 | All arithmetic in code, never by the LLM | Accepted |
| 0007 | Single shared `individual` tenant for all B2C users | Accepted |
| 0008 | Application-level tenancy as mechanism, RLS as backstop | Accepted |
| 0009 | Direct Anthropic API calls; no LangChain or agent frameworks | Accepted |
| 0010 | No ML training in Phases 1–3; statistics over projections only | Accepted |
| 0011 | Chapter topology as a second post-hoc analytic axis | Proposed |
| 0012 | Offer-set steering as curation, never generation | Proposed |
| 0013 | Hybrid Mobile Canvas Architecture | Accepted |

---

*Document Version 1.0 | Architecture Decision Record Log*
*Platform: Path-Based Conceptual Exploration and Teacher-Support System*
