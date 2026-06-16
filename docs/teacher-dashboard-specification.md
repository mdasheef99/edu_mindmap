# Teacher Dashboard Specification

**Document Version**: 1.0 (draft)
**Status**: Proposed — concrete surface for the teacher-support layer
**Related Documents**: `docs/teacher-support-mvp-specification.md`, `docs/teacher-access-control-specification.md`, `docs/framework-design-philosophy.md`, `docs/measurement-and-experimentation.md`, `docs/architecture/backend-architecture.md`, `docs/chapter-analysis-pipeline-specification.md`, `docs/subject-weighting-specification.md`

---

## 1. Purpose

This document specifies the teacher dashboard: its views, the parameters each view shows, the data
contract behind each parameter, the actionable insight each is designed to produce, scope rules,
feedback capture, and deliberate exclusions.

It is the delivery surface for the job-to-be-done in `docs/teacher-support-mvp-specification.md`
§3 — *"before the next class, decide what to ask next, which concept to revisit, or where targeted
scaffolding may help"* — plus the bounded class-level layer that the B2B tenancy model
(`docs/architecture/backend-architecture.md` §5, §7.4) makes possible.

The dashboard is a **web application** consuming the `/v1/teacher` router
(backend architecture §11). It is read-only: no intervention, authoring, or export tooling. Under
the v1.3+ architecture, `/v1/teacher` reads from consent-gated `analytic_rm` projections and must
verify tenant membership, active teaching assignment, active student class membership, and
behavioral-analytics consent before returning analytic panels. Student-facing `student_rm` state and
category-neutral learner APIs remain physically and semantically separate.

---

## 2. Position in the Documentation Set

| Document | Relationship |
|----------|--------------|
| `docs/teacher-support-mvp-specification.md` | Remains the authority on what teacher support *claims* and the checkpoint-interpretation rules (§7). This document specifies the surface that delivers it. Where this document adds the class-aggregate view (V4), it **extends** that spec's MVP boundary deliberately, following the B2B commitment in backend architecture §7.4; the extension is bounded in §5.4 below. |
| `docs/teacher-access-control-specification.md` | Later-phase reference (Tier 2 interventions, privilege workflows). Nothing here grants intervention privileges. Where its vocabulary conflicts with claim boundaries (e.g., "diagnostic concern analysis"), **this document supersedes the phrasing**: the dashboard never uses "diagnostic". Its Tier 1 "export reports" capability is deferred per teacher-support MVP §8. |
| `docs/framework-design-philosophy.md` | Governs all claims and language (§6 principle 5, §7 reporting rules). |
| `docs/measurement-and-experimentation.md` | Governs version stamping carried in every payload. |
| `docs/architecture/backend-architecture.md` | Governs data sources (`analytic_rm` projections, §7), scope enforcement (§5.3), and the API surface (§11). |
| `docs/chapter-analysis-pipeline-specification.md` | Governs Section C inputs (P6 audit, P9 profiles/modifiers, P11 backlog, P10 QA labels). |

---

## 3. Design Principles

1. **Signals, not verdicts.** Every displayed interpretation is probabilistic — a pattern worth a
   teacher's attention. The dashboard never asserts that a student understands, lacks
   understanding, has mastered, or has failed anything.
2. **Availability before gap.** A dimension may be flagged as under-explored for a concept **only
   if** the chapter analysis (P6) shows that dimension AVAILABLE or PARTIALLY_AVAILABLE for that
   concept **and** its effective weight passes the display threshold. A student cannot be flagged
   for not exploring material the chapter does not contain.
3. **Aggregates over instances.** Cumulative profiles and distributions are shown; per-question
   dimensional vectors are not (a single classification is noisy by design; see §9).
4. **Checkpoint evidence is displayed separately from coverage** and never reduces or overwrites a
   coverage value (teacher-support MVP §7).
5. **Every number is traceable.** Each payload carries `projection_version`,
   `chapter_analysis_id`, and the classification `prompt_version`/`model_id` lineage of the rows
   it derives from.
6. **Everything is instrumented.** Every view render emits `teacher_view_accessed`; every panel
   carries useful/not-useful capture emitting `teacher_feedback` (§8).
7. **One-way visibility.** Teacher surfaces render category-visible interpretation; no dashboard
   artifact is ever rendered into a student-facing surface.

---

## 4. Access and Scope Rules

Per backend architecture §5.3, §7.4, and §11:

1. **Role**: `teacher` or `approved_teacher` membership in an institutional tenant, resolved per
   request by the `tenancy` module. Responses serialize from `domain/analytic` types only.
2. **Student-level visibility**: a teacher sees a student's views only while the student holds an
   *active* `class_membership` in a class where the teacher holds an *active*
   `teaching_assignment`. The data shown spans the student's activity during that class
   membership's interval; activity from before the student joined the class is not shown.
3. **Aggregate suppression**: any aggregate cell covering fewer than **K = 5** students renders as
   "insufficient data" (K is config, not a constant).
4. **School admins** (`school_admin`) see class/institution aggregates only, via `/v1/admin` —
   never individual-student drill-down. The teacher dashboard does not serve them.
5. **B2C students** (shared `individual` tenant) have no teacher relationship; no teacher surface
   exists for them. Pilot classes using the invite flow (backend §5.2) behave as institutional.
6. **Consent gate**: students whose behavioral-analytics consent is absent or withdrawn (backend
   §12.3) appear in rosters as "consent pending" with no analytic panels rendered.
7. Every view access is logged (`teacher_view_accessed` with view id, target refs, and stamps).

---

## 5. Views

### 5.1 V1 — Class Overview (entry point)

The minimum overview needed before drilling into a single student (resolves teacher-support MVP
§9 open item 3).

| Parameter | Content |
|-----------|---------|
| Roster | Students with active membership; alphabetical order (never ranked) |
| Last activity | Most recent session timestamp per student |
| Chapters touched | Which launched chapters the student has opened |
| Participation | Session count and selection count over the last 7/30 days |
| Checkpoint participation | Counts of checkpoint responses by type (Try Now / Not Sure Yet), aggregate only |
| Consent state | active / pending / withdrawn (renders per §4.6) |

**Insight**: operational only — *who has and hasn't engaged recently*. Activity volume is not a
framework signal and no learning interpretation is attached. "No recent activity" is a fact, not
a concern flag.

### 5.2 V2 — Chapter Landscape (student-independent preparation)

A direct render of chapter-analysis Section C for a launched chapter. Useful before teaching the
chapter at all, independent of any student data.

| Parameter | Source | Teacher use |
|-----------|--------|-------------|
| Chapter availability vector | P9 `availability[d]` per dimension | Which kinds of engagement this chapter's material can actually support — gaps in high-availability dimensions are meaningful; gaps in low-availability dimensions are not |
| Per-concept richness profiles | P9 richness (0.0–8.0) + P6 verdicts per dimension | Which concepts offer broad engagement material vs. thin ones |
| `low_material` flags | P9 (richness < 1.5) | Concepts likely to generate poorly and to warrant teacher-supplied depth |
| Dimension evidence | P6 cited passages + `gap_note` per concept × dimension | Ready references into the textbook for class preparation |
| Prior-conceptions backlog | P11 records, each badged **UNVALIDATED** | "Things to listen for" in class — research-grounded candidate misconceptions. Never matched to individual students (Phases 1–3 prohibition on `trigger_spec` runtime use) |
| Effective weights | `subject_weight[d] × modifier[d]` (P9, per subject-weighting spec) | Why the dashboard prioritizes some dimensions over others in this chapter |

All panels stamp the `chapter_analysis_id` and render only analyses with `qa_status = "passed"`.


### 5.3 V3 — Student Chapter Review (core view)

The per-student, per-chapter review that delivers the teacher-support MVP surface (§4 of that
spec). Six panels.

**3a — Exploration path.** Ordered reconstruction of the student's movement through the chapter:
nodes visited, threads followed, phrase selections, and what was offered versus what was selected
(option texts and selection order; never propensities or policy internals). Insight: *how* the
student moved, not how well. Action: open a conversation from the student's own path — "I saw you
spent time on internal resistance; what pulled you there?"

**3b — Engagement profile.** The 8-dimension cumulative state (normalized running sum of
selection vectors, per `docs/framework-design-philosophy.md` path-capture spec), display-ordered
by effective weight for this chapter, with a trajectory sparkline showing how the profile evolved
across the session(s). Insight: where attention has tended to go. This panel is context only — it
carries no flags and no value judgments.

**3c — Attention-gap panel (the centerpiece).** The cross-reference that makes a gap meaningful.
A (concept, dimension) cell is flagged only when **all three** hold:

1. coverage is low for that concept × dimension (`coverage_by_concept`, threshold in config),
2. the P6 audit marks the dimension AVAILABLE or PARTIALLY_AVAILABLE for that concept, and
3. the effective weight for the dimension passes the display threshold.

Each flagged cell ships with its P6 cited passages and `gap_note` — the teacher gets the gap *and*
the textbook material to address it in one card. Insight: "the pattern so far suggests this is
worth a follow-up question." Action: ask one in class; the card includes a suggested phrasing (3f).

**3d — Gap persistence.** Distinguishes flagged gaps by recency dynamics (philosophy doc,
path-capture item 5): low cumulative + low recent velocity = **persistent** (the student keeps not
engaging it despite opportunities — the offer-set log confirms opportunities existed); low
cumulative + recent non-zero velocity = **catching up** (no action needed). Persistent gaps sort
first in 3c; catching-up gaps render muted. This prevents teachers from spending attention on gaps
that are already closing.

**3e — Checkpoint signals (separate panel, never merged into coverage).** Sensemaking Pause
responses rendered exactly per the interpretation table in `docs/teacher-support-mvp-specification.md`
§7: Try Now response quality as cautious evidence, Not Sure Yet as metacognitive uncertainty,
repeated opt-out patterns only above the repetition threshold and only in low-certainty language.
A single Skip or Snooze is never shown. Checkpoint evidence may qualify a 3c card ("a recent
reflection near this concept was partial") but never changes a coverage value.

**3f — Suggested follow-ups.** For each flagged 3c cell, 1–3 teacher-use question phrasings
derived in code from the P6 evidence (template + passage reference; no LLM call in the request
path). Framed for the teacher's voice, category-visible ("a boundary-conditions question on X"),
and explicitly optional. These are prompts for the teacher to adapt, not scripts.

**3g — Connections not yet explored (topology layer, phased).** The relational complement to 3c:
where 3c asks *how* the student engaged each concept (dimensions), 3g asks *whether the chapter's
argument structure was traversed* (edges). Defined in `docs/chapter-topology-specification.md` §6.1;
summarized here for view completeness:

- **Phase 1 (no graph rendering)**: a ranked list of intended edges with no traversal evidence,
  from `coverage_by_pair`. Each row carries the edge label, the P4 `passage_support` citation, the
  status split — `never_surfaced` (the system's miss) vs `offered_not_selected` (the student's
  choice) vs `engaged_separately` (both concepts touched, link never crossed) — and a 3f-style
  suggested phrasing. The status split is the load-bearing distinction: it tells the teacher
  whether to prompt the student or to expect the system to surface it.
- **Phase 2**: the full chapter map (intended graph with realized-subgraph overlay, conceptual
  islands, outcome-subgraph shortfall), per topology spec §6.1.

3g rows obey the same availability-before-gap discipline as 3c: an edge is listed only if it
exists in the accepted P4 graph (with P10-adjudicated additions), ranked by P12 criticality once
Phase 2 lands; Phase 1 ranks by `passage_support` count.

### 5.4 V4 — Class Chapter Aggregate (bounded B2B extension)

V4 is part of the B2B dashboard direction but may be staged after the first Walking Skeleton if
pilot scope requires only V1 plus selected V3 panels. Any V4 endpoint must apply small-cohort
suppression and tenant/class authorization before returning values.

This view extends the teacher-support MVP boundary (which excluded "full class-level analytics
dashboards and ranked severity views"). The extension is deliberately bounded: **distribution
shapes only, never rankings.**

| Parameter | Content |
|-----------|---------|
| Engagement distribution | Per dimension: median and spread (IQR) of student cumulative scores across the class |
| Coverage spread | Per concept: share of students with low/medium/high explored breadth (suppressed below K) |
| Checkpoint response mix | Class-level counts of Try Now / Not Sure Yet / opt-out patterns |
| Participation | Active students, sessions, selections over the period |
| Common attention gaps | (concept, dimension) cells flagged per the 3c rule for ≥ a configurable share of the class |
| Common unexplored connections | Intended edges with no traversal evidence for ≥ a configurable share of the class (topology spec §6.2 class edge overlay; Phase 2) |

Built from `analytic_rm.class_aggregates` with as-of-event-time roster joins (backend §7.4), K = 5
suppression on every cell. **Excluded**: ranked student lists, severity leaderboards, any
per-student value visible in this view, cross-class comparisons.

**Insight**: whether a gap is individual or collective. Action: a gap common to most of the class
("half the class shows thin engagement with failure conditions on Ohm's law") suggests whole-class
treatment in the next lesson; an individual gap suggests a targeted follow-up via V3.

### 5.5 School-admin surface (reference only)

School admins consume `institution_aggregates` via `/v1/admin` (backend §11): class-level rollups
per grade band × subject, same K-suppression, no individual drill-down, no exploration paths. That
surface is part of the admin web app, not this dashboard, and is listed here only to fix the
boundary.

---

## 6. Data Contracts per View

All teacher endpoints read from `analytic_rm` (the `teacher_support_views` materializations,
backend §7.2) and Section C storage. Every response envelope carries:
`projection_version`, `chapter_analysis_id` (where chapter-dependent), `generated_at`,
`window` (period covered), and `suppressed_cells` (for aggregate views). Rows derived from
classifications carry the classification `prompt_version` and `model_id` lineage.

| View / panel | Projections & events | Section C inputs | Notes |
|--------------|---------------------|------------------|-------|
| V1 roster & participation | Participation projection over `session/node_visited/offer_set_choice` events; `class_memberships`, `consent_records` state | — | Operational counts only |
| V2 landscape | — | P6 audit, P9 availability vector / richness / modifiers / `low_material`, P11 backlog | `qa_status = "passed"` analyses only |
| V3a path | Path projection over `node_visited`, `node_created`, `offer_set_created/impression/choice`, `phrase_selected` | P1–P3 concept labels (for naming nodes) | Option propensities and `is_probe` stripped before serialization |
| V3b profile | `student_engagement_profiles` (← `question_classified` events) | P9 effective weights (ordering only) | Cumulative + trajectory + velocity |
| V3c gaps | `coverage_by_concept` × profile | P6 verdicts + passages + `gap_note`, P9 effective weights | Three-condition flag rule; thresholds in config |
| V3d persistence | `student_engagement_profiles` (velocity over recent selections) + offer-set log (opportunity check) | — | Persistent vs. catching-up |
| V3e checkpoints | `checkpoint_offered` / `checkpoint_response` events (incl. `trigger_type`, response-quality signal) | — | Rendered per teacher-support MVP §7; repetition threshold in config |
| V3f follow-ups | Derived in code from V3c output | P6 passages | No LLM call in the request path |
| V3g connections | `coverage_by_pair` (Phase 1) / `realized_subgraph` + `graph_diff` (Phase 2) × offer-set log (status split) | P4 edges + `passage_support`, P12 criticality, P13 outcome map (Phase 2) | Availability-before-gap applies to edges; statuses: `never_surfaced` / `offered_not_selected` / `engaged_separately` |
| V4 aggregates | `class_aggregates` (as-of-event-time membership joins) | P6/P9 (gap rule) | K = 5 suppression on every cell |

**Endpoint sketch** (`/v1/teacher`, full contract belongs to the API specification):

- `GET /classes` · `GET /classes/{class_id}/students` (V1)
- `GET /chapters/{chapter_id}/landscape` (V2)
- `GET /students/{student_id}/chapters/{chapter_id}/review` (V3, panel-parameterized)
- `GET /classes/{class_id}/chapters/{chapter_id}/aggregate` (V4)
- `POST /feedback` (§8)


---

## 7. Insight and Phrasing Catalog

All teacher-facing copy follows `docs/framework-design-philosophy.md` §7: probabilistic and
actionable, never definitive. Checkpoint phrasings reproduce the teacher-support MVP §7 table
verbatim and are not restated below.

### 7.1 Vocabulary rules (enforced in UI copy review)

**Banned anywhere on the dashboard**: "understands", "doesn't understand", "mastered", "weak in",
"failed", "avoided", "refused", "diagnosed", "deficient", "behind", "at risk".

**Required hedging register**: "has tended to", "the pattern so far suggests", "may", "worth a
follow-up question", "consider", "so far".

### 7.2 Catalog

| Parameter | Interpretation | Classroom action | Example phrasing | Prohibited phrasing |
|-----------|----------------|------------------|------------------|---------------------|
| Engagement profile (3b) | Where the student's attention has tended to go in this chapter | Context for conversation; no action by itself | "Selections so far have leaned toward how concepts connect and what follows from them." | "Strong in connect, weak in delimit." |
| Attention-gap cell (3c) | A pattern worth a follow-up — material exists, weight is meaningful, engagement is thin so far | Ask one targeted question; the card supplies the passage and a suggested phrasing | "The chapter offers material on when Ohm's law stops applying (p. 214), and the path so far hasn't gone there. May be worth a follow-up question." | "Student doesn't understand boundary conditions." |
| Persistent gap (3d) | The gap has had opportunities (offer-set log) and hasn't moved | Prioritize over catching-up gaps; a direct prompt may help | "This area has stayed thin across several sessions, even when related questions were available." | "Student keeps avoiding this topic." |
| Catching-up gap (3d) | Recent selections are already moving into the area | None — rendered muted | "Recent activity has started moving into this area." | "Gap closing — no concern." (verdict framing) |
| Checkpoint signals (3e) | Per teacher-support MVP §7 table, verbatim | Probe gently or note uncertainty; never grade | "Student gave a coherent reflection when prompted." | "Passed/failed the checkpoint." |
| Repeated opt-outs (3e) | Timing/comfort pattern, surfaced only above threshold | Optional, low-stakes check-in | "The student often chose not to pause for reflection when the path shifted into prediction-style prompts." | "Student refused reflections." |
| Suggested follow-up (3f) | A starting phrasing grounded in cited chapter material | Adapt to your own voice; optional | "You might ask: 'What happens to this circuit if the temperature rises sharply?' (draws on p. 198)." | Anything framed as a required remediation step |
| Unexplored connection (3g) | A relationship the chapter builds that the path hasn't crossed yet — with whether it was ever offered | If never surfaced, expect the system to offer it; if offered and not selected, a bridging question in class may help | "The chapter links resistance to Ohm's law (p. 210), and the path so far has explored both separately but hasn't crossed between them." | "Student can't connect resistance to Ohm's law." |
| Chapter availability (V2) | What this chapter's material can support | Plan supplementary depth for low-availability dimensions | "This chapter offers little material on boundary conditions; gaps there reflect the text, not the student." | "Chapter is deficient." |
| Prior-conceptions backlog (V2) | Research-grounded candidates to listen for; unvalidated | Listen during discussion; do not pre-attribute | "Students often arrive thinking current is 'used up' in a bulb — worth listening for. (UNVALIDATED)" | "Your students have this misconception." |
| Common class gap (V4) | A thin area shared widely enough to suggest whole-class treatment | Address in the next lesson rather than individually | "A sizable share of the class shows thin engagement with failure conditions on Ohm's law so far." | "Most of the class is weak in delimit." |
| Class engagement distribution (V4) | Shape of attention across the class | Adjust emphasis in upcoming lessons | "Class selections have clustered around definitions and components; consequence-style questions have been picked less often so far." | Any per-student naming or ranking |

### 7.3 Display conventions

- Every insight card pairs the signal with its evidence (passage reference, counts, window) — the
  teacher always sees *why* the card exists.
- Dimension names render in teacher-friendly long form ("when a concept stops applying" for
  *delimit*), with the internal key shown secondarily for consistency across views.
- Time qualifiers are mandatory: every claim is scoped ("so far", "over the last two weeks") —
  no card ever reads as a stable trait of the student.

---

## 8. Feedback Capture

The dashboard is itself an instrument: per `docs/measurement-and-experimentation.md`, the primary
outcome measure for teacher support is whether teachers find the signals useful.

### 8.1 Mechanism

- Every insight-bearing card (3c gap cards, 3d persistence markers, 3e checkpoint summaries,
  3f suggestions, 3g connection rows, V4 common-gap rows, V2 backlog entries) carries a one-tap
  **"Was this useful?" → Useful / Not useful** control.
- "Not useful" optionally opens reason chips: *not relevant* · *already knew this* · *unclear* ·
  *wrong for this student*. Free text optional. Never required — a bare tap is a valid response.
- V1 and plain-context panels (3a path, 3b profile) carry a single per-view control rather than
  per-row controls, to avoid prompt fatigue.

### 8.2 Event contract

Each response emits a `teacher_feedback` event (registry family per backend §6.2) carrying:

| Field | Content |
|-------|---------|
| `view_id`, `panel_id` | Which view and panel (e.g., `v3`, `3c`) |
| `card_ref` | Target refs: `student_id` (pseudonymous), `chapter_id`, `concept_id`, dimension key — whichever apply |
| `verdict` | `useful` / `not_useful` + optional `reason` chip + optional free text |
| Stamps | All stamps from the rendered payload: `projection_version`, `chapter_analysis_id`, classification `prompt_version`/`model_id`, config threshold versions |

The stamps make feedback joinable to the exact interpretation pipeline that produced the card —
"teachers marked 3c cards not useful 40% of the time under flag-threshold config v2" is a
queryable statement.

### 8.3 What feedback does and does not do

- **Does**: serve as the teacher-support layer's outcome instrument; drive threshold/phrasing
  revisions between versions (config bumps, replayed projections).
- **Does not** (Phases 1–3): feed back into runtime behavior, generation, classification, or any
  per-student model. No adaptive loop keys off `teacher_feedback`.

---

## 9. What the Dashboard Does NOT Show, and Why

| Omission | Why |
|----------|-----|
| Per-question dimensional vectors | A single classification is noisy by design (median-of-3 reduces, doesn't eliminate); per-question display invites over-reading. Only cumulative aggregates render. |
| Mastery scores, grades, certifications, pass/fail | Outside the framework's claim boundary (`framework-design-philosophy.md`): exploration signals are not assessment authority. |
| Ranked student lists, severity leaderboards | Ranking converts probabilistic signals into verdicts and invites comparison harm; V1 rosters are alphabetical, V4 shows distribution shapes only. |
| Individual Skip/Snooze events | Opt-out is agency, not data for surveillance (teacher-support MVP §7); only repeated patterns above the config threshold surface, in low-certainty language. |
| Student-matched prior-conception detections | P11 `trigger_spec` is a heuristic research aid; no runtime behavior may key off it in Phases 1–3 (chapter-analysis spec P11). Backlog renders chapter-level only, badged UNVALIDATED. |
| Propensities, `is_probe`, policy internals | Measurement instrumentation (measurement spec §4.2), not pedagogy; exposing them invites gaming and misreading of the offer policy. |
| Per-question entropy / classification confidence | Internal QA quantities; consumed by the pipeline (hedging, review queues), not by teachers. |
| Exports and reports | Deferred per teacher-support MVP §8. The access-control spec's Tier 1 "export reports" capability is superseded for now (§2); revisit with the B2B pilot. |
| Intervention tooling (question injection, content authoring) | Tier 2, later phase (access-control spec); the dashboard is read-only. |
| Anything rendered into student surfaces | One-way visibility (§3.7): no dashboard artifact, label, or score ever appears on a student-facing surface — enforced structurally by the separate read models and routers (backend §7, §11). |
| Cross-class / cross-school comparisons | Outside the job-to-be-done; comparison views drive ranking culture and add no per-class action. |

---

## 10. Open Items

1. **Visual encodings** — radar vs. horizontal bars for the engagement profile; cell grid vs.
   list for 3c. UX prototyping decision; this spec constrains content, not form.
2. **Config thresholds** (all config, not constants): low-coverage threshold (3c condition 1),
   persistence window and velocity definition (3d), opt-out repetition threshold (3e — open in
   teacher-support MVP §9), common-gap class share (V4), K suppression value.
3. **Export timing** — deferred; decide with the first B2B pilot contract requirements.
4. **Language** — Hindi/regional-language phrasings for the §7 catalog; phrasing review must
   re-apply the vocabulary rules per language.
5. **V4 timing** — whether the class aggregate view ships with the first B2B pilot or follows
   one iteration after V1–V3 feedback.
6. **Entry point** — teacher-support MVP §9 open item 1 is resolved here as V1 (class overview
   → drill-down); confirm with pilot teachers that this matches their pre-class workflow.

---

*Document Version 1.0 (draft) | Teacher Dashboard Specification*
*Platform: Path-Based Conceptual Exploration and Teacher-Support System*
