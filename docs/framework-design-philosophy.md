# Framework Design Philosophy

## Purpose
This document defines the **design philosophy** for the Categorical Exploration Learning Platform: how we think the framework works, what we are (and are not) claiming, and how those claims translate into product + data decisions.

## Non-goals / Guardrails
- **Not a metaphysical claim** that the 8 categories are universal necessities of thought.
- **Not a student-facing taxonomy**: students must never see category labels, axis names, or “you explored 6/8 dimensions”.
- **Not a quiz-trigger spec**: adaptive trigger logic is intentionally out of scope and will be designed later.

---

## 1) Pragmatic epistemological position
The 8 categories are grounded in a **principled derivation** from a philosophical tradition asking the right foundational question: *what are the fundamental ways a mind engages with a concept?* This makes them a stronger starting point than dimensions selected by committee or intuition. We treat the 8-category framework as:
- a **diagnostic measurement model** for teachers/designers (coverage lens and behavioral signals), and
- a claim of **provisional sufficiency**: these categories are adequate for diagnostic purposes given current evidence, with sufficiency treated as an open empirical question under ongoing test.

Logical completeness is not claimed—stripping Kant's transcendental scaffolding removes the original justification for completeness without replacing it. The validation pipeline is designed to test sufficiency through **independent open-coding probes** (human raters generating dimensional labels without prior knowledge of the framework), alongside the **depth/breadth tradeoff** (whether breadth of coverage predicts better outcomes than equivalent depth in fewer dimensions).

### What we believe is practically useful
- Learners’ *question-selection behavior* (from a presented offer set) contains **probabilistic signals** about what they are attending to.
- Post-hoc classification of questions as **multi-dimensional engagement vectors**—independent scores (0.0–1.0) across all 8 diagnostic dimensions—yields a richer “learning fingerprint” than single-category assignment, because a single question can genuinely engage multiple dimensions simultaneously.

### Learning path capture is a first-class product goal
We treat each learner’s exploration as a **sequential trajectory** through nodes and offered questions (not just aggregate counts). Because each selected question carries an 8-dimensional engagement vector, the path is a sequence of vectors—not a sequence of single-category labels.

Concretely, the product must be able to reconstruct:
- the **ordered path** of node visits and question selections (with timestamps),
- the **offer sets** that were shown at each step (counterfactual menu),
- the resulting **transitions** (what the learner did next), and
- the **dimensional engagement vector** for each selected question.

From the captured path, the system computes five statistical analyses (all computable via database aggregation—no ML training required):

1. **Cumulative State** — running sum of dimensional vectors across all selected questions, normalised by question count. This is the primary input for gap detection: `normalised_cumulative[d] = Σ scores[d] / N`.
2. **Trajectory Shape** — how the cumulative profile evolves over the session. Early exploration may cluster in one region of the dimensional space; later exploration may diversify. The shape (not just the endpoint) is diagnostically informative.
3. **Velocity** — the dimensional engagement vector of a single selection event, interpreted as the rate of change per step. A question with high Delimit and low everything else contributes a velocity vector that “pushes” the cumulative state toward Delimit.
4. **Transition Probabilities** — P(next_vector | current_cumulative_state). Computed from aggregate data across students: given a cumulative profile similar to the current one, what dimensional engagement tends to come next? Used for bridge question recommendations.
5. **Gap Persistence** — distinguishes dimensions that are merely unexplored-so-far from dimensions that are being actively avoided. A dimension with low cumulative score *and* low velocity across recent selections (the learner keeps not engaging it despite opportunities) is a persistent gap. A dimension with low cumulative score but recent non-zero velocity is catching up.

This “path capture” goal is foundational because it powers (and constrains):
- teacher diagnostics (patterns, clusters, avoidance, revisitation),
- content-library/caching promotion (what converges at scale),
- non-linear reinforcement artifacts (e.g., path-optimized podcasts), and
- any later personalization (must be measurable; see Section 4).

### What we explicitly do NOT assume
- That category coverage is a guaranteed necessary/sufficient condition for “understanding”.
- That observed patterns are causal without measurement safeguards.

---

## 2) Canonical category set (diagnostic only)
These categories are diagnostic because they provide principled dimensions for analyzing conceptual engagement, derived from a serious philosophical tradition. Any given concept engages these dimensions unevenly; subject-specific weights encode which dimensions are structurally available and diagnostically significant. Gaps in high-weight dimensions are treated as diagnostically significant indicators of likely gaps in conceptual understanding; gaps in low-weight dimensions are less diagnostically significant.

Categories are applied **after** question generation. Each question receives an independent score (0.0–1.0) on every dimension simultaneously, producing an 8-dimensional engagement vector rather than a single primary/secondary category assignment. Scores use the following anchors: 0.0 (dimension not present), 0.3 (tangentially engaged), 0.6 (meaningfully engaged), 0.9 (centrally engaged). Scores are independent—they do not form a probability distribution and need not sum to 1.

| ID | Key | Label | Diagnostic intent |
|---:|---|---|---|
| C1 | define | Define | What is X? |
| C2 | distinguish | Distinguish | X vs Y / boundaries |
| C3 | decompose | Decompose | Parts / structure |
| C4 | connect | Connect | Relations / links |
| C5 | delimit | Delimit | Limits / failure conditions |
| C6 | predict | Predict | Consequences / mechanisms |
| C7 | contextualize | Contextualize | Broader frames / systems |
| C8 | vary | Vary | Alternatives / counterfactuals |

**Policy**: category names/IDs are allowed in teacher/admin tools and internal logs, but are **never displayed to students**.

---

## 3) Subject-specific weighting (weighting, not filtering)
All 8 categories remain:
- present in the generator’s organic output space,
- present in post-hoc classification, and
- present in analytics.

Subjects differ because different subjects systematically produce concepts with different structural profiles. Weights encode the typical structural availability and diagnostic significance of each dimension across the concept types characteristic of a given subject. A high weight means the dimension tends to be prominently and meaningfully available in that subject's concepts. A low weight means the dimension tends to be thinner or less diagnostically central—present in the categorical space but not meaningfully instantiated in most of that subject's concept types. Weights are implemented via the weight matrices defined in `docs/subject-weighting-specification.md`.

**Rule**: adapt interpretation and prioritization via weights; do not delete dimensions.

---

## 3.5) How weights flow through the pipeline (diagnostic lens, not a generation constraint)
Subject weights are a **diagnostic lens** used downstream; they must not be used to "steer" Stage 1 generation.

- **Generation (Stage 1)**: organic, context-driven question generation. **No weights applied.** Only mild, non-categorical diversity instructions are allowed (e.g., avoid duplicates; vary angles naturally) to prevent degenerate repetition.
- **Classification (Stage 2)**: post-hoc scoring of each question across all 8 dimensions as an independent engagement vector (0.0–1.0 per dimension). **Weights not applied.**
- **Scoring / analytics**: compute **weighted coverage** and **gap severity** using subject weights.
- **Presentation**:
  - **Student**: category-neutral language only (no labels, no axis names, no dimension counts).
  - **Teacher/Admin**: may see weighted gaps and category-level breakdown.
- **Intervention**: teacher recommendations prioritize **high-weight gaps** (subject-specific), while student-facing prompts remain category-neutral.

---

## 4) Data collection strategy: offer sets + causal leverage
### Why offer sets are mandatory
To interpret selection behavior, we must log not only what the learner chose, but **what was offered** (the counterfactual menu).

### Minimum “offer set” event fields (conceptual)
- `offer_set_id`, `student_id`, `session_id`, `node_id`, `timestamp`
- `options[]`: stable IDs/hashes + rendered text + rank/order
- per option: `source` (organic_llm/cache/teacher_variant/etc.)
- policy metadata: `policy_name`, `policy_version`, `mode` (discovery|exploitation)
- outcome: `selected_option_id`, `time_to_select`, optional scroll/visibility signals

### Discovery vs exploitation separation
- **Discovery traffic**: preserves measurement quality (diverse, more organic, limited personalization, occasional safe randomization).
- **Exploitation traffic**: applies optimizations (ranking, caching, interventions) to improve experience.

**Policy requirement**: always tag mode + policy version, and preserve an **organic discovery budget** with a hard floor of 30% minimum to keep discovery data available.

To avoid personalization feedback loops corrupting measurement:
- **Stratify discovery** across student segments (grade level, proficiency bands, language, subject, etc.) so discovery data is not concentrated in a single subgroup.
- **Periodic re-randomization / diagnostic probes**: even for exploitation-mode students, periodically include small amounts of safely-randomized or organic content to detect preference drift and evaluate whether personalization is steering behavior.
- **Hard floor at 30%**: The organic discovery floor is fixed at 30% minimum system-wide and cannot be reduced below 30% by any actor including administrators. It may be increased above 30% (e.g., if exploitation becomes highly personalized or model uncertainty is high) but never lowered.

---

## 5) Structural coverage (subject-weighted, empirical)
We define “diagnostic coverage of conceptual engagement” operationally:
- a **weighted coverage score** over the 8 categories for a concept/session, and
- a set of **gap severities** derived from subject weights.

**Working hypothesis**: higher weighted coverage (especially in high-weight dimensions for that subject) is expected to correlate with better downstream learning outcomes. This must be tested and recalibrated.

---

## 6) Key design principles
1. **Organic-first generation**: questions are generated from context as a curious learner would ask—no categorical templates (and no attempt to optimize for category coverage at generation time).
2. **Post-hoc classification**: categories are applied after generation for diagnosis.
3. **Category-neutral student language**: any student prompts are phrased as natural suggestions (e.g., “Try comparing…”, “What happens if…”) without naming dimensions.
4. **Teacher-visible diagnostics**: teachers see category-weighted coverage, priority concerns, and suggested follow-ups.
5. **Multiple outcome measures**: validate signals using more than one outcome (e.g., retention, transfer tasks, time-to-mastery, confidence calibration, optional assessments).
6. **Subject-specific interpretation**: weights change which low-coverage dimensions count as more diagnostically significant concerns.

---

## 7) Implementation guidance (how this philosophy constrains decisions)
### Question suggestion blending
- Blend sources (organic, cached, teacher variants) while enforcing organic floor.
- Ranking/personalization must be logged as policy decisions (for later evaluation).

### Dashboards
- **Student**: progress is expressed in category-neutral terms (e.g., “exploration depth”, “breadth”, “new connections made”).
- **Teacher/Admin**: may show full 8-dimension breakdown with subject weights and gap severities.

### Diagnostics + reporting
- Treat diagnostics as **probabilistic** and **actionable**, not as definitive proofs of understanding.
- Prefer recommendations like “next best prompts” (category-neutral for students) and “intervention themes” (category-visible for teachers).

### Quiz / assessment
Assessments may exist as one outcome signal, but **trigger mechanisms and adaptive logic are not yet specified** and must be defined in a future document.

