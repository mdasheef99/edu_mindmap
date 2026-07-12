# Development Approach

**Document Version**: 1.0 (draft)
**Status**: Proposed — governing execution document
**Related Documents**: `docs/planning/mvp-execution-plan.md`, `docs/planning/backend-mvp-strategy.md`,
`docs/planning/session-path-data-contract.md`, `docs/planning/release-critical-user-flows.md`,
`docs/planning/testing-strategy.md`, `docs/architecture/backend-architecture.md`,
`docs/architecture/adr-log.md`, `docs/chapter-analysis-pipeline-specification.md`,
`docs/mvp-features-specification.md`

---

## 1. Purpose and Position

This document defines **how development proceeds from an empty repository**: the order in which
risk is retired, the phase gates, the engineering disciplines that must exist from day one, the
concrete technology stack, and the working method for a documentation-driven project built
primarily with AI-assisted development by a developer new to software engineering.

It deliberately does **not** restate scope. The division of labor in the planning set is:

| Document | Answers |
|----------|---------|
| `mvp-execution-plan.md` | *What* ships in the first slice, workstreams, acceptance criteria |
| `backend-mvp-strategy.md` | *What infrastructure* is required now vs deferred |
| `session-path-data-contract.md` | *What data shape* every layer shares |
| **This document** | *How* to actually build it: sequence, phase gates, disciplines, method |

If this document conflicts with the scope anchors above, the scope anchors win; resolve the
conflict explicitly here rather than overriding them silently.

### 1.1 Governing realities

Three facts shape every recommendation below; pretending otherwise produces a plan that fails.

1. **The documentation describes 12–18 months of work for a small experienced team.** The suite
   is internally consistent and implementation-ready, but it is large. Execution must be
   ruthlessly sequenced: build the smallest thing that retires the biggest open risk, ship it,
   then repeat. Nothing in this document licenses building ahead of the current phase.
2. **The developer is new to software engineering and will work with AI agents.** This changes
   the method (§8), not the standard: the spec suite is the source of truth, increments stay
   small and reviewed, and the CI gates in §6 exist precisely because human review alone cannot
   be relied on to catch guarantee-eroding drift.
3. **The product's riskiest claims are not buildable claims.** Whether students tap organic
   questions, and whether teachers act on gap cards, cannot be settled by architecture. The plan
   therefore front-loads the cheapest possible tests of the core bet (§3) and gets real users in
   front of partial builds at every phase rather than after a "complete" MVP.

---

## 2. Operating Principles

1. **Risk-first ordering.** Every phase exists to retire a named risk (§9). Work that retires no
   open risk is deferred regardless of how easy or appealing it is.
2. **Walking skeleton before any complete layer.** A thin vertical slice through every layer
   (mobile → API → event store → worker → LLM → projection) ships before any single layer is
   built out. Integration problems surface in week one, not month six.
3. **Instrumentation ships with the feature, never after.** Offer-set impressions, choices, and
   propensity logging are part of the *definition* of the offer-set feature
   (`measurement-and-experimentation.md`); a feature that works but does not log is incomplete.
   Retrofitted logging produces data whose interpretation is permanently suspect.
4. **Non-retrofittable disciplines start in migration 0001** (§6). Tenancy, version stamps, the
   event registry, and import boundaries are cheap on day one and infeasible to add later.
5. **Every phase ends with something a real person uses.** Each phase gate (§5) includes a
   human-in-front-of-it condition, not only passing tests.
6. **Defer without guilt.** The event-sourced design (`backend-architecture.md` §2.1, ADR-0001)
   guarantees that deferred interpretation layers can be added later by replay and projection,
   not migration. Deferral is therefore safe by construction; premature building is not.

---

## 3. Phase 0 — Validate the Core Bet (before any app code)

**Duration guide**: 2–4 weeks. **Cost**: a few dollars of API usage. **Infrastructure**: none —
plain Python scripts, one folder, no database, no backend, no mobile app.

The entire product rests on one assumption: *an LLM pipeline can extract a credible analysis of
an NCERT chapter, and generate from it organic questions a student would actually want to tap.*
This is testable for almost nothing, and if it fails, nothing downstream matters.

### 3.1 Work items

1. **P0 (segmentation) as pure code** against the Electricity chapter
   (`docs/research/electricity.pdf`), per the pipeline spec. No LLM involved — an ideal first
   programming project that also produces the system's first real artifact.
2. **P1–P4** (concept inventory, passage mapping, weighting inputs, edge extraction) as scripts,
   with outputs written to versioned JSON files and reviewed by eye.
3. **Hand-simulated runtime**: feed a concept's passage content into the Stage 1 prompt contract
   (`architecture/llm-pipeline.md`) and read the questions it produces. Repeat across ~10
   concepts and several prompt revisions.
4. **Subject-matter review**: someone who knows the chapter (a teacher, a tutor, the author)
   reviews the concept inventory, edges, and sample questions for credibility.

### 3.2 Phase gate (exit criteria)

- P0 segment boundaries are correct on visual inspection against the PDF.
- The P1 concept inventory and P4 edges survive subject-matter review with only minor edits.
- At least half of the generated sample questions pass the test: *"would a 15-year-old
  preparing for boards plausibly tap this?"* — judged by someone other than the developer.
- A short written verdict is added to this document's changelog: proceed / revise prompts /
  rethink. **If this gate fails, stop and revise the pipeline spec — a year is saved.**

---

## 4. Phase 1 — Walking Skeleton

**Goal**: the smallest deployed end-to-end loop touching every architectural layer, proving
every integration point at once.

### 4.1 Contents (and nothing more)

- **Repository**: monorepo (`backend/`, `mobile/`, `docs/`) — one history, shared contracts.
- **Backend**: FastAPI app with migration 0001 (`tenant_id` and version-stamp columns on every
  table — the explicitly non-retrofittable items), the append-only events table with the
  registry and three event types (`session_started`, `node_created`, `offer_set_choice`), one
  projection, the Postgres `SKIP LOCKED` job queue with one `classify` worker job, and the
  `llm_gateway` module as the single chokepoint for Anthropic calls.
- **Mobile**: one Expo screen rendering a single AI node; tapping a question calls the backend,
  which generates content and returns a child node. No canvas gestures yet, no curriculum entry.
- **Deployed**: backend API and worker deployed on Render next to Supabase;
  mobile via Expo dev build on one physical mid-range Android device.

### 4.2 Phase gate (exit criteria)

- The loop works on a physical device against the deployed backend, not just locally.
- An `offer_set_choice` event appended in the request path is classified asynchronously by the
  worker, and the projection rebuilds deterministically from the event log (replay test, §6.4).
- CI runs tests + import-linter on every push (§6.2); Sentry receives a deliberately thrown
  error from both apps.
- Tenant isolation is proven under pooled connections by an integration test (§6.6).

---

## 5. Phase 2 Onward — Milestone Build Order

This sequence implements the dependency order of `mvp-execution-plan.md` §7, refined by what
Phase 0/1 will have already built. Each milestone is shippable to a test user, and each names
the risk it retires. Do not start milestone *n+1* while milestone *n*'s gate is open.

| # | Milestone | Contents | Retires risk | Gate (beyond tests passing) |
|---|-----------|----------|--------------|------------------------------|
| M1 | Core loop deepening | Offer-set logging complete (impressions + choices + propensities), session persistence + resume, edge-`+` branching, deletion cascade with confirmation | "Our data can't be interpreted later" | One full session's path is reconstructable from events alone, without the board snapshot |
| M2 | Phrase selection | Reader bottom-sheet flow first (`mobile-features-core-ui.md` fallback); in-node selection deferred as enhancement | The fiddliest mobile interaction | A test user branches from a phrase they chose themselves, on Android and iOS |
| M3 | Canvas maturation | Pan/zoom/gestures via skia + reanimated, manual reference links (`edge_created`/`edge_deleted`), 65-node limits, layout | The highest engineering risk in the project (§9) | 60fps interaction at 40+ nodes on the reference mid-range Android device |
| M3-C | Infrastructure Remediation | Close three "compute-ready, transport-missing" seams discovered in the 2026-06-23 audit: Seam A — `POST /sessions/{id}/events` (client event ingest + whitelist + boundary type/enum validation); Seam B — `GET /sessions/{id}` with full canvas payload via `active_canvas_from_events`; Seam C — `PATCH /nodes/{id}` position persistence, `NodeToolbar` cascade-response reconciliation (G1), `PhraseSelectionReaderSheet.chooseOption` full-payload propagation (G1-v); Tier 2 — `node_visited`/`viewport_changed` emission wiring in `SkiaCanvas`; replace `DEV_NODES`/`DEV_EDGES` dev fixtures with real session hydration | "Walking Skeleton is not end-to-end: data-integrity frontier is transport-missing — client cannot emit events, server cannot hydrate canvas state, drag positions are lost on reload" | All three P1 phantom endpoints (`POST /events`, `GET /sessions/{id}`, `PATCH /nodes/{id}`) implemented and registered in `main.py`; integration tests for event→projection round-trip green (TA/TB/TC suites); `DEV_NODES`/`DEV_EDGES` removed from `App.tsx`; `student-api-spec.md` parity check signed off in SDD §8 (Discipline #10) |
| M3.6 | Canvas controls | Explicit zoom in/out toolbar buttons, fit-to-screen, reset view, zoom percentage readout, and optional snap-to-grid drag-end commit using the fixed MVP grid size | "Canvas is gesture-capable but lacks clear learner-facing controls for precision navigation and alignment" | Focused canvas-control Jest green; full mobile Jest green; no M4 auth/curriculum scope pulled forward |
| M4 | Curriculum entry + auth | Supabase Auth, exam/subject/chapter entry, dashboard re-entry, consent capture | None new — enables real-user testing | A stranger can install, sign up, and reach a chapter unaided |
| M5 | Checkpoints | Trigger policy (cosine arithmetic over existing classification data), Try Now / Not Sure Yet capture | Outcome-signal capture | Checkpoint events flow into `analytic_rm` with correct stamps |
| M6 | Teacher V1 + V2 | Web app (React + Vite + TanStack Query), roster/overview, chapter landscape (V2 needs **no student data** — it renders chapter analysis, so it can be built any time after Phase 0) | "Will teachers act on it?" — first real test | One real teacher uses it before a class and the §8 feedback control captures the verdict |
| M7 | Teacher V3 panels | 3a/3b first; 3c when coverage projections are trusted; 3g Phase 1 (`coverage_by_pair` + Stage 2 attribution) after that | Gap-card usefulness; topology Phase 1 | Golden-set agreement for attribution (topology spec §4.3) before any 3g card renders |
| M8 | Podcast | Session-derived script + TTS via worker, in-app playback | None — MVP completeness item | Release boundary statement of `mvp-execution-plan.md` §3 is fully met |

**Milestone status update (2026-07-02)**: M3-C Infrastructure Remediation and the bounded M3.6
Canvas Controls pre-M4 slice are **locally complete**. M3.6 added explicit zoom controls,
fit-to-screen, reset view, zoom readout, and optional snap-to-grid per
`phase-3-m3-6-canvas-controls-sdd.md` and `worklog-v8.md`; full mobile Jest was 119/119 green.
The pre-M4 mobile TypeScript `TS2688` Jest type-definition blocker was resolved on 2026-07-01
(`worklog-v8.md`). M4 is now the active milestone for implementation planning, with
`phase-3-m4-curriculum-auth-sdd.md` drafted and `worklog-v9.md` opened.

**Milestone status update (2026-07-11)**: M4 Curriculum Entry + Auth is **closed**. The durable
Postgres runtime, Supabase ES256/JWKS auth, consent, dashboard re-entry, API-derived Class 10 ->
CBSE -> Science -> Electricity launch path, resume/hydration, native Android flow, and non-bypass
pooled-RLS isolation gate are verified. Interactive web is excluded from the native-first M4
closure gate; its production CanvasKit export is green and interactive rendering remains a
non-blocking follow-up. M5 Checkpoints is next and has not started.

**Bounded integration update (2026-07-13)**: post-M4 canvas position-lifecycle stabilization is
locally complete from `f1308fc` under `canvas-position-write-lifecycle-sdd.md`. It adds checked
drag-end delivery, session-scoped Zustand position authority, per-node FIFO/retry, UI-thread
edge/label drag geometry, and recoverable child placement without changing M4 or starting M5.
Physical-device and canvas performance gates were not rerun for this integration.

**Deferred without guilt** (per §2.6 — these layer on later via replay/projection or are
post-MVP by existing decisions): image/video enrichment tiers, Perplexity integration, V4 and
all B2B admin surfaces, topology Phases 2–3, steering (ADR-0012 stays Proposed), content-library
promotion, broader offline behavior.

---

## 6. Day-One Disciplines (cheap now, impossible later)

These are restated from their owning specs because they are *sequencing-critical*: each must
exist before the code it governs, and several cannot be retrofitted at all.

1. **Migration 0001 carries `tenant_id` and version-stamp columns on every table**
   (`backend-architecture.md` §2.5). Retrofitting multi-tenancy onto an event store is not
   feasible.
2. **Import-linter contracts run in CI from the first push.** The category-invisibility
   guarantee is enforced by module boundaries (`api/student` may import `domain/student` only);
   if the check is not automated it is fiction. CI = GitHub Actions: tests + import-linter +
   formatter on every push.
3. **The event registry exists before the second event type.** Every event validates against
   the registry on append (`backend-architecture.md` §6); ad-hoc payloads are prohibited.
4. **Projection replay test harness in the first month.** Any projection must rebuild
   deterministically from the event log; this test is written alongside the *first* projection,
   not after the first schema migration goes wrong.
5. **Prompts are versioned files in the repo, never inline strings.** `prompt_version` stamping
   (`architecture/llm-pipeline.md`) requires it.
6. **Tenant-isolation integration test under pooled connections.** The `SET LOCAL
   app.tenant_id` RLS pattern works under pgbouncer transaction mode *only* if every request
   runs inside a transaction that sets the GUC. This test exists before any second tenant does.
7. **Pure-function arithmetic gets unit tests immediately.** Entropy, medians, dispersion, P9
   formulas, checkpoint cosine triggers — all trivially testable, all load-bearing.
8. **A golden set (~50 hand-labeled questions) the moment Stage 2 exists**, regression-run on
   every `prompt_version` bump (`classification-reliability-protocol.md`).
9. **Observability minimums**: Sentry in both apps, structured JSON logs, and the LLM cost
   counter in `llm_gateway` from its first call.
10. **Every SDD must include a `student-api-spec.md` parity check before closure.**
    Before any milestone SDD is marked closed, the developer must enumerate every
    `student-api-spec.md` endpoint the increment depends on, verify each has a matching
    FastAPI router function and is registered in `main.py`, and record the result in the
    SDD's Definition-of-Done section. A phantom endpoint — documented in the spec but
    absent from the router — in a closed SDD's dependency list is a merge-blocking defect
    regardless of whether unit tests pass. This discipline was added after the 2026-06-23
    infrastructure audit identified three Walking-Skeleton-critical phantom endpoints
    (`POST /events`, `GET /sessions/{id}`, `PATCH /nodes/{id}`) that accumulated silently
    across M1–M3 because no milestone gate checked API boundary completeness. The parity
    check applies to both backend endpoints and mobile `fetch` call sites: every `fetch`
    target in a milestone increment must correspond to a registered router path.

---

## 7. Technology Stack (pinned)

This is the consolidated reference. Where a document from this session conflicts with an older
version, the newer document governs. Backend runtime choices are fixed in
`backend-architecture.md` §3; mobile, dashboard, CI, and testing rows are decided by this
document.

### 7.1 Backend & Infrastructure

| Concern | Choice | Governing doc |
|---|---|---|
| Runtime | Python / FastAPI, single deployable unit + worker entrypoint | `backend-architecture.md` §3; this doc §7 |
| Hosting | Render for MVP backend API + worker service | This doc §7; `docs/operations/delivery-and-operations.md` |
| Database | PostgreSQL (via Supabase) — events, read models, queue, auth in one instance | This doc §7; `backend-architecture.md` §3 |
| Job queue | Postgres `SELECT ... FOR UPDATE SKIP LOCKED` | This doc §7; `backend-mvp-strategy.md` v1.1 §6 |
| Auth | Supabase Auth (JWT `user_id`; role/tenant resolved server-side) | This doc §7; `backend-architecture.md` §5 |
| Storage | Supabase Storage (podcast audio, media uploads) | This doc §7 |
| Tenancy | `tenant_id` on every table from migration 0001; B2B + B2C unified | `backend-architecture.md` §5; `backend-mvp-strategy.md` v1.1 §6 |

**Deferred to scale:** Redis, Celery, TimescaleDB, read replicas, CDN, multi-region.

### 7.2 AI & LLM

| Concern | Choice | Governing doc |
|---|---|---|
| LLM provider | Anthropic API (direct calls, no framework) | This doc §7; `adr-log.md` ADR-0009 |
| Generation model | Claude Sonnet 4 (`claude-sonnet-4-20250514`) — Stage 1 | `llm-pipeline.md` |
| Classification model | Claude Haiku 4 (`claude-haiku-4-20250514`) — Stage 2 median-of-3 | `classification-reliability-protocol.md` |
| Structured output | Pydantic / Instructor | This doc §7; `llm-pipeline.md` |
| TTS (podcast) | Backend-managed (OpenAI TTS or ElevenLabs — flexible) | `backend-mvp-strategy.md` v1.1 §7; `backend-architecture.md` §8.2 |

**Explicitly excluded:** LangChain, LlamaIndex, agent frameworks.

### 7.3 Mobile App (Student)

| Concern | Choice | Governing doc |
|---|---|---|
| Framework | **Expo (React Native), dev builds** | This doc §7; `system-architecture.md` v1.3 |
| Canvas rendering | **react-native-skia** (edges, board) + **Native Views** (node content) | This doc §7; `adr-log.md` ADR-0013 |
| Gestures / animation | **react-native-gesture-handler** + **react-native-reanimated** | This doc §7; `adr-log.md` ADR-0013 |
| State | **Zustand** | This doc §7 |
| Local persistence | **AsyncStorage** (session resume, narrow offline reopen) | This doc §7; `backend-mvp-strategy.md` v1.1 §9 |
| Performance gate | 60fps at 40+ nodes on physical mid-range Android | This doc §5 M3; `adr-log.md` ADR-0013 |

**Deferred:** MMKV (only if measured need), in-node text selection (Reader bottom-sheet is primary
MVP path), Supabase Realtime (no multi-user sync in MVP).

### 7.4 Teacher Dashboard (Web)

| Concern | Choice | Governing doc |
|---|---|---|
| Framework | React | This doc §7 |
| Build tool | Vite | This doc §7 |
| Data fetching | TanStack Query | This doc §7 |
| Design | Read-only, deliberately boring — no SSR | This doc §7 |

### 7.5 CI/CD & Observability

| Concern | Choice | Governing doc |
|---|---|---|
| CI | GitHub Actions (tests + import-linter + formatter on every push) | This doc §6; `testing-strategy.md` §3 |
| Error tracking | Sentry (backend + mobile + web) | This doc §7 |
| Logging | Structured JSON logs | This doc §6.9 |

### 7.6 Testing (Tooling)

| Concern | Choice | Governing doc |
|---|---|---|
| Backend unit | pytest + pytest-asyncio | `testing-strategy.md` §4 |
| Backend API | httpx `TestClient` | `testing-strategy.md` §4 |
| Test database | Real Postgres via testcontainers / `supabase start` | `testing-strategy.md` §4 |
| LLM stubbing | Recorded JSON fixtures (keyed by `prompt_version`), never live calls in CI | `testing-strategy.md` §4 |
| Mobile unit | Jest + React Native Testing Library | `testing-strategy.md` §6 |
| Static gates | import-linter, ruff, mypy on `domain/`, `events/`, `projections/` | `testing-strategy.md` §4 |

### 7.7 Content Pipeline (Chapter Analysis)

| Concern | Choice | Governing doc |
|---|---|---|
| PDF extraction | `pypdf` (not PyPDF2) | `chapter-analysis-pipeline-specification.md` P0 |
| Passes P0–P11 | Python scripts + LLM (Sonnet for P1–P4, P6–P8, P11; Haiku for P3) | `chapter-analysis-pipeline-specification.md` |
| Topology layer (P12–P13) | **Proposed** — deterministic edge IDs, code-side graph measures | `chapter-topology-specification.md` §3; `adr-log.md` ADR-0011 |

### 7.8 Explicitly Deferred (Never in MVP)

| Item | Reason | Governing doc |
|---|---|---|
| Redis | Postgres `SKIP LOCKED` handles queue; no performance need | `backend-mvp-strategy.md` v1.1 §6; `adr-log.md` ADR-0002 |
| Celery | Same as above | `backend-mvp-strategy.md` v1.1 §6 |
| TimescaleDB | Event store is the time-series; no specialized queries yet | `backend-mvp-strategy.md` v1.1 §6 |
| Graph database (Neo4j, etc.) | Pure code graph measures over Postgres | `backend-architecture.md` §13 |
| LangChain / LlamaIndex | Direct API is simpler and version-controllable | `adr-log.md` ADR-0009 |
| Microservices | Single modular monolith; extraction seams only if scale demands | `adr-log.md` ADR-0001 |
| Kafka / EventStoreDB | Append-only Postgres table is sufficient | `adr-log.md` ADR-0002 |
| Supabase Realtime | No multi-user sync in MVP | `backend-mvp-strategy.md` v1.1 §6; `system-architecture.md` v1.3 |
| MMKV | AsyncStorage is sufficient; replace only if measured | This doc §7 |
| In-node text selection | Reader bottom-sheet is primary; hybrid seam risk | `adr-log.md` ADR-0013 |

**Reference device rule**: all mobile performance gates (§5 M3) are judged on a physical
mid-range Android device matching `research/indian-student-market-analysis.md`, never on a
simulator or flagship.

---

## 8. Working Method (documentation-driven, AI-assisted, new developer)

1. **The spec suite is the source of truth — keep it that way.** Every work session starts from
   a named spec section, not from memory of it. When code and spec diverge, one of them is
   fixed *deliberately* and the change is traceable (ADR or spec edit), never absorbed
   silently.
2. **One spec section per increment.** Work proceeds in increments small enough to read and
   explain: one endpoint, one event type, one projection, one panel. Never accept a generated
   change too large to explain line by line — the architecture's guarantees (invisibility,
   append-only, stamps) erode through exactly the drift that oversized increments hide.
3. **The CI gates are the reviewer of last resort.** Import-linter, replay tests, and golden
   sets exist because human review — especially novice review of generated code — will miss
   guarantee violations. A red gate always wins an argument with generated code.
4. **Ask "which risk does this retire?" before starting anything.** If the answer is none, it
   goes to the deferred list (§5).
5. **Real users embarrassingly early.** One real student at M2, one real teacher at M6 — their
   behavior outranks any internal judgment about whether questions get tapped or cards get
   acted on.
6. **A worklog, not a wiki.** The active worklog records date, what shipped, gate status, and
   decisions taken — enough for any future contributor (human or AI) to reconstruct state without
   replaying chat history.

## 8.1 Documentation Governance

- Active high-growth files have a strict 350-line limit, starting with ADR logs and worklogs.
- When the active file would exceed 350 lines, rotate instead of appending: `adr-log-02.md`,
  `adr-log-03.md`; `worklog-v2.md`, `worklog-v3.md`.
- Every continuation file starts with `AGENT ROTATION INSTRUCTION — READ FIRST`, then a `Legacy
  Context Summary` linking to the previous file and summarizing final state, resolved decisions,
  active milestone, open blockers, and next action.
- Rotated files are closed archives. Do not append except to add the closed-file header.
- The active continuation file becomes the file future agents read first after the hierarchy docs.

## 8.2 Code Organization Standards

- No single source file should exceed **300–350 lines**. If a file approaches the limit, split it by
  responsibility before adding more behavior.
- Keep modules cohesive: routers orchestrate, domain modules hold pure rules, adapters isolate I/O,
  and shared infrastructure helpers replace repeated SQL/config/observability patterns.
- Generated or AI-assisted changes must stay reviewable: small diffs, typed boundaries, explicit
  tests, no hidden side effects, and no secrets in code, docs, tool arguments, or logs.

---

## 9. Risk Register

| Risk | Likelihood | Impact | Retired by |
|------|-----------|--------|------------|
| Generated questions aren't tappable (core bet) | Medium | Fatal | Phase 0 gate; M2 real-student test |
| Canvas performance/UX on mid-range Android | High | High | M3 gate on reference device; 65-node cap; Reader-sheet fallback before in-node selection |
| Event-sourcing execution discipline (payload versioning, idempotent projections) | Medium | High | §6.3–6.4 from week one |
| RLS + connection pooling tenant leak | Medium | Severe | §6.6 test before any second tenant |
| Solo-developer scope creep | High | High | Phase gates; §8.4 question; deferred list |
| Teachers don't act on signals | Medium | High | M6 with a real teacher + §8 feedback capture (dashboard spec §8) |
| LLM cost runaway | Low | Medium | `llm_gateway` budget counter from first call |

---

## 10. Other Documents Required

Previously blocking docs are written: API specs (`docs/api/`), database specs (`docs/database/`), configuration reference, testing strategy, delivery/operations baseline, and worklog. The deploy target remains a Phase 1 choice. Not needed now: design-system/UI-kit doc, expanded retention policy, or further architecture docs.
