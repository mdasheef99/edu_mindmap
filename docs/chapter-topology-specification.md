# Chapter Topology Specification

**Document Version**: 0.1 (draft proposal)
**Status**: Proposed — extends `docs/chapter-analysis-pipeline-specification.md` (P12–P13), Stage 2 runtime, and the teacher dashboard (V3/V4)
**Related Documents**: `docs/chapter-analysis-pipeline-specification.md`, `docs/teacher-dashboard-specification.md`, `docs/architecture/data-collection.md`, `docs/architecture/llm-pipeline.md`, `docs/framework-design-philosophy.md`, `docs/measurement-and-experimentation.md`, `docs/architecture/backend-architecture.md`

---

## 1. Purpose

A chapter is not a bag of concepts; it is an argument with a shape. The existing pipeline extracts
the concepts (P1–P3) and the typed relationships the chapter establishes between them (P4), but
nothing yet captures the authority's *intended conceptual argument* — the traversal order, the
emphasis distribution, and the subgraph its own end-of-chapter outcomes exercise. Nor does the
runtime record student exploration as a graph: today's `coverage_by_concept` is a flat matrix that
cannot express "knows resistance, knows current, never crossed V = IR."

This specification defines:

1. **Intended topology** — two new pipeline passes (P12 code, P13 LLM) that complete the
   authority's-intent extraction.
2. **Realized subgraph** — runtime edge-level attribution and a rebuildable projection of the
   student's exploration as a graph over the same nodes.
3. **Graph diff** — code-only measures comparing the two, for the teacher dashboard.
4. **Surfaces and steering** — a V3 chapter-map panel, a V4 class overlay, and a bounded,
   logged offer-set steering policy (shipped separately, behind an experiment flag).

### 1.1 Relationship to the framework

This layer is **post-hoc interpretation applied to a structural axis**, parallel to the
8-dimension analytic axis. It obeys the same invariants:

- Generation (Stage 1 / Section A) remains blind to everything defined here. No intended-topology
  artifact enters Section A.
- Nothing defined here renders on a student-facing surface. The map is the teacher's instrument;
  the student feels it, at most, as well-placed questions.
- All outputs are probabilistic signals with "so far / not yet" framing, never verdicts, per
  `docs/framework-design-philosophy.md` §7 and the dashboard vocabulary rules.
- All arithmetic is computed in code, never by the model (pipeline cross-cutting rule).
- Everything is a rebuildable projection over the existing event store; no new event families are
  required except where noted (§7).

---

## 2. The Intended Topology (four layers)

| Layer | Source | Status |
|-------|--------|--------|
| Concept graph (nodes + typed edges) | P1–P4 | Exists |
| Traversal order (exposition sequence) | P0 segment order, derived in P12 | **New (code)** |
| Emphasis distribution (authors vote with pages) | P5 reverse index, derived in P12 | **New (code)** |
| Outcome-anchored subgraph (end questions/activities) | P0 `question`/`activity` segments, mapped in P13 | **New (LLM)** |

The intended topology for a chapter is the tuple
`(P4 graph, P12 order, P12 emphasis, P12 criticality, P13 outcome map)`, stored in **Section C**
under the same versioned `chapter_analysis_id` envelope as all other passes.

---

## P12 — Structural Metrics & Emphasis Weights (Code)

**Runs after P5** (and recomputes whenever P10 corrections touch P4, same rule as P9).
**Inputs**: P0 segment index, P4 edge list, P5 reverse index. No LLM.

**Computations**:

1. **Exposition order**: for each concept, `first_position` = `char_span` start of its
   definitional segment (P2 concepts: first explanatory segment). Output: the authority's linear
   traversal sequence over the merged inventory.
2. **Emphasis weight**: from the P5 reverse index,
   `emphasis(c) = Σ type_weight(segment_type)` over segments citing `c`, normalized to [0, 1]
   across the chapter. `type_weight` is per-subject config (initial values:
   `example: 1.5`, `activity: 1.5`, `para: 1.0`, `summary_point: 0.75`, `figure_caption: 0.5`,
   `table: 0.5`); the table is versioned in `pass_versions.P12`.
3. **Edge criticality (structural)**: edge betweenness centrality on the P4 graph (treating
   PREREQUISITE_OF as directed, CONNECTS/CONTRASTS_WITH as undirected), plus the set of
   **articulation points** (nodes whose removal disconnects the graph). Computed with standard
   graph routines (networkx); trivially cheap at N ≤ 60.
4. **Composite edge criticality** (consumed by §5 and §7):
   `criticality(e) = z(betweenness(e)) + z(mean emphasis of endpoints) + outcome_count(e)`
   where `outcome_count(e)` = number of P13 outcomes requiring `e` (recomputed after P13;
   formula and constants versioned in `pass_versions.P12`).

**Storage**: Section C only. **Verification**: pure code; no gate. Determinism: same inputs →
same outputs.

---

## P13 — Outcome-to-Subgraph Mapping (LLM, Sonnet)

**Purpose**: the end-of-chapter questions and in-text activities are the authority's own revealed
specification of what understanding should look like. Each implicitly requires certain concepts
and — crucially — certain **edges**. Mapping them yields the exam-relevant subgraph.

**Runs after P4** (P12 step 4 consumes its output). **Input**: P0 segments of type `question` and
`activity` + merged concept inventory (labels + definitions) + P4 edge list (with edge IDs).

**SYSTEM PROMPT:**

> You are mapping each end-of-chapter question and in-text activity of a textbook chapter onto
> the concepts and relationships it exercises. The chapter's concept inventory and relationship
> graph are provided. For each outcome item produce:
> - `outcome_id`: the segment ID of the question/activity
> - `required_concepts`: concept IDs from the provided inventory only
> - `required_edges`: edge IDs from the provided graph only. An edge is required **only if
>   answering demands reasoning across the relationship** — not if the two concepts merely
>   appear in the answer.
> - `missing_edge_candidates`: if answering plainly requires a relationship that is absent from
>   the provided graph, describe it as `{from_concept, to_concept, rationale}` instead of
>   inventing an edge ID.
> - `rationale`: one sentence on what the item asks the student to do.

**USER PROMPT:**

> Concept inventory: [MERGED CONCEPT LIST]
>
> Relationship graph: [P4 EDGES with edge IDs]
>
> Outcome segments: [P0 SEGMENTS of type question/activity, with segment IDs]
>
> Map every outcome. Produce output as a JSON object with an `outcomes` array.

**DO NOT:**
- Cite a concept or edge ID not present in the provided inputs
- Mark an edge required when the item only mentions both endpoint concepts
- Import outside knowledge of what "should" be tested — map only what each item actually demands

**Verification**: gate checks 1, 2, 4, 6. New code rule: every `missing_edge_candidates` entry is
emitted to `qa_review_queue` as a warn — the authority's own questions are a recall test on P4,
and a recurring missing edge usually means P4 under-extracted.

**P10 additions**: checklist item 7 — verify ≥ 5 outcome mappings against the actual item text;
confirm or reject each `missing_edge_candidate` (accepted ones become P4 edges and trigger the
P12 recompute).

**Storage**: Section C only.

---

## 4. The Realized Subgraph (runtime)

The student's exploration is recorded as a graph over the same merged concept inventory. No new
student-facing behavior; one extension to Stage 2 and one new projection.

### 4.1 Edge-level attribution (extends Stage 2 classification)

Stage 2 already runs async post-selection (Haiku, median-of-3, structured output). Add to the
same call — no new pass:

- `engaged_concepts`: 0–2 secondary concept IDs from the merged inventory that the question
  substantively engages, beyond the source concept (which code supplies from node context).
- `relation_engaged`: boolean — does the question reason about the relationship between the
  source concept and a secondary concept itself, or merely mention both?

**Code (never the model)** then resolves `(source, secondary)` pairs against the P4 edge list:
match → `edge_id`; no match → `candidate_edge` record (off-graph engagement, itself a signal).
Attribution is taken by majority vote across the 3 classification runs; disagreement on
`relation_engaged` resolves to `false` (conservative). Records carry `chapter_analysis_id` and
classifier `prompt_version`, as today.

**Unselected offers**: edge semantics in §5 require knowing what was *offered*, not only what was
selected. Unselected offer-set options are classified in a nightly batch queue at Haiku rates,
lowest priority — they gate nothing in-session, so latency is irrelevant. Batch coverage lag is
acceptable and stamped (`attributed_through` timestamp on the projection).

### 4.2 Manual reference links (high-signal evidence)

`Connection creation` events already exist (`docs/architecture/data-collection.md`). A projection
step resolves both endpoint nodes to their attributed concepts and matches against P4:

- **Matches a P4 edge** → strongest available traversal evidence: the student asserted the
  connection unprompted.
- **No P4 counterpart** → `student_asserted_edge` record. Teacher-facing phrasing (per the
  dashboard §7 catalog): "The student drew a connection the chapter doesn't make — possibly an
  insight, possibly a misconception; worth a brief look." Never auto-judged.

### 4.3 Evidence tiers

| Tier | Evidence | Edge state |
|------|----------|-----------|
| T1 | Manual link matching a P4 edge; selected question with `relation_engaged = true` | **Traversed** |
| T2 | Selected question engaging both endpoints with `relation_engaged = false`; branch transition A→B | **Approached** |
| T3 | Both endpoints visited/dwelled, no joint engagement | **Adjacent only** |

Tier definitions and any thresholds are config, versioned with the projection.

### 4.4 The projection

`realized_subgraph(student_id, chapter_id, chapter_analysis_id)` is a rebuildable `analytic_rm`
projection over existing events (`node_visited`, `node_created`, `offer_set_*`,
`question_classified` with attribution, connection-creation events). Contents: engaged node set
(with engagement strength), edge set with evidence tier and supporting event references,
`student_asserted_edge` records, and stamps (`projection_version`, `chapter_analysis_id`,
`attributed_through`). It lives in `analytic_rm` only — never in `student_rm`.

---

## 5. The Graph Diff (code-only measures)

`graph_diff(student_id, chapter_id, chapter_analysis_id)` compares the realized subgraph against
the intended topology. Three measures, all computed in code:

### 5.1 Untraversed edges

Intended edges with no T1/T2 evidence, ranked by P12 composite criticality. Each carries exactly
one status, joined from the offer-set log and §4.1 attribution:

| Status | Meaning | Reading |
|--------|---------|---------|
| `never_surfaced` | No offered option was attributed to this edge | **System/content gap** — not a student signal; counts against generation coverage, not the student |
| `offered_not_selected` | ≥ k attributed opportunities existed (k in config) | Cautious student signal, same logic as dashboard 3d persistence |

The two statuses must render distinguishably; conflating them misattributes system gaps to
students.

### 5.2 Conceptual islands

Connected-components analysis on the realized subgraph (engaged nodes, T1/T2 edges). Report:
component count versus the intended graph (typically 1), and the **missing bridges** — the
minimal set of intended edges that would reconnect the components, ranked by criticality.
Phrasing pattern: "Exploration so far falls into two separate clusters — [A-cluster] and
[B-cluster] — that the chapter connects through [bridge edge]."

### 5.3 Outcome-subgraph shortfall

Per the P13 map: an outcome is **covered** when all `required_concepts` are engaged and all
`required_edges` have ≥ T2 evidence; **partially covered** when ≥ half of each; otherwise
**not yet covered**. Report the covered count ("the path so far covers the territory of 7 of 11
chapter-end questions"), the not-yet-covered list, and a greedy set-cover (code, trivial at this
scale) of the 1–3 edges whose traversal would unlock the most uncovered outcomes.

**Claim boundary**: coverage means *the exploration has crossed the required territory* — it is
never rendered as a prediction that the student can or cannot answer the item, and never as a
readiness score. Time qualifiers ("so far") are mandatory on every rendering.

---

## 6. Teacher Dashboard Surfaces

### 6.1 V3 panel 3g — Chapter Map

Augments, not replaces, the 3c attention-gap matrix: the dimensions answer *how* the student
engages; the map answers *what shape* the engagement has. Orthogonal diagnoses.

Render the intended graph with:

- **Nodes**: solid (engaged) / faded (touched) / ghost outline (untouched), sized by P12 emphasis.
- **Edges**: solid (T1) / dashed (T2) / absent-but-intended rendered as ghost. Untraversed edges
  visually distinguish `never_surfaced` from `offered_not_selected` (§5.1).
- **Student-asserted off-graph edges**: distinct accent color, tappable to the 4.2 card.
- **Islands and missing bridges** (§5.2) and the outcome shortfall sentence (§5.3) render as
  insight cards beside the map, each paired with its evidence per dashboard display conventions.

Data contract row (extends dashboard §6): `V3g map | realized_subgraph × graph_diff | P4 edges,
P12 metrics, P13 map | qa_status = "passed" analyses only; all stamps`. Feedback control per
dashboard §8 (per-card "Was this useful?").

### 6.2 V4 — class edge overlay

The same map as a class heat overlay: per intended edge, the share of students with ≥ T2
evidence, K = 5 suppressed, distribution shapes only, no rankings — within the V4 boundary
already defined. An edge untraversed by ≥ a configurable share of the class is a whole-class
finding ("most of the class hasn't crossed from resistance into Ohm's law yet") and, aggregated
across classes, upstream feedback about the chapter itself: the material is not making that
bridge inviting. That aggregate flows to the research/validation track, not to any scoring.

### 6.3 Student surfaces

None. The map, the diff, and every quantity in this document are teacher- and research-facing
only. A student-facing "territory to fill" display would convert curiosity into
checkbox-clearing and corrupt every signal upstream of it. Enforced structurally: all artifacts
live in `analytic_rm` behind the teacher router, per backend §7/§11.

---

## 7. Steering (separate ship decision, experiment-flagged)

### 7.1 The tension, named

The pipeline spec §6.3 bans engineered bridge questions in generation, and Section A never sees
the intended topology. Steering students toward missing edges therefore **must not** touch
generation. It operates at the **offer-set selection policy** — an already-logged, versioned
decision point with propensities (`docs/measurement-and-experimentation.md` §4).

### 7.2 Mechanism

- Stage 1 generates candidates exactly as today: Section A only, organic, blind to the diff.
  P7 productive pairs already seed relational candidates naturally.
- When composing an offer set at node A, if edge A–B is high-criticality and untraversed, the
  policy *prefers* a candidate whose §4.1 attribution engages A–B — **if one exists in the
  pool**. No candidate is fabricated; the menu is curated, never the mandate.
- **Budget**: max k structural steers per session (config; initial k = 2). Without the cap this
  rebuilds covert adaptive sequencing and destroys the exploration data the system exists to
  collect.
- Every steer is logged on the offer-set record: `steer_reason: {edge_id, criticality,
  policy_version}`. Refusals are captured by existing offered-but-not-selected logging and feed
  §5.1 status.
- **Checkpoint trigger**: a new `trigger_type: structural_islands` for Reflective Checkpoints —
  when two islands cross a size threshold, the Sensemaking Pause invites a connecting reflection
  ("you've explored how current flows and separately what resistance does — how do you think
  they fit together?"). Subject to the same opt-out semantics as all checkpoints.

### 7.3 Required amendment

Pipeline spec §6.3's "no engineered bridge questions" clause is amended to read precisely: *no
engineered bridges in generation prompts; structural preference in offer-set curation is
permitted, budgeted, and logged as policy.* Steering ships behind an experiment flag so its
effect on exploration quality is itself measurable; if steered sessions show degraded organic
exploration, the flag turns off without touching the map (§6), which is independently valuable.

---

## 8. Phased Implementation

The one load-bearing runtime change is §4.1 attribution; everything else is code-side.

| Phase | Contents | Depends on |
|-------|----------|-----------|
| 1 | §4.1 Stage 2 attribution + `coverage_by_pair` projection (per P4 edge / P7 pair: `surfaced_count`, `selected_count`, `joint_engagement_count`, `manual_link_count`); add `offered_count`/`selected_count` to `coverage_by_concept`; V3 renders a ranked **"Connections not yet explored"** list (edge label + P4 `passage_support` + 3f-style suggested phrasing) | Nothing new in the pipeline |
| 2 | P12 + P13 passes; `realized_subgraph` + `graph_diff` projections; V3 3g map + V4 overlay | Phase 1 attribution |
| 3 | §7 steering, experiment-flagged | Phase 2 + measurement review |

Phase 1 alone delivers the "offered vs. never-surfaced" split and relational gap visibility with
no graph machinery; Phases 2–3 layer on without rework because the attribution substrate is the
same.

---

## 9. Invariants (non-negotiable)

1. No intended-topology artifact enters Section A; the Stage 1 assembler remains structurally
   unable to reference it (separate storage keys and read APIs, as for Sections B/C).
2. Nothing in this document renders on a student-facing surface, ever.
3. The diff is an agenda for the teacher, never a score against the student: "not yet visited,"
   never "deficient." The intended topology is the authority's hope, not ground truth of
   understanding; a student who traverses differently is not wrong.
4. All arithmetic in code; LLM outputs are attributions and mappings only.
5. Every artifact stamps `chapter_analysis_id`, `projection_version`, and prompt/model versions;
   all projections are rebuildable from the event store.
6. Steering is budgeted, logged, and experiment-flagged; the map ships independently of it.

---

## 10. Open Items

1. Initial config values: emphasis `type_weight` table, evidence-tier thresholds, untraversed-edge
   opportunity threshold k, steering budget, V4 class-share threshold.
2. Map rendering at N ≈ 40–60 concepts: full graph vs. neighborhood-focused view; UX prototyping
   decision (this spec constrains content, not form).
3. Whether P13 runs per chapter in one call or batched per 10 outcomes (output-quality test).
4. Nightly-batch classification cost envelope for unselected offers at expected session volumes.
5. Hindi/regional phrasings for the new insight cards (same vocabulary-rule review as dashboard §7).

---

*Document Version 0.1 (draft) | Chapter Topology Specification*
*Platform: Path-Based Conceptual Exploration and Teacher-Support System*
