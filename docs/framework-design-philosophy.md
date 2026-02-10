# Framework Design Philosophy

## Purpose
This document defines the **design philosophy** for the Categorical Exploration Learning Platform: how we think the framework works, what we are (and are not) claiming, and how those claims translate into product + data decisions.

## Non-goals / Guardrails
- **Not a metaphysical claim** that the 8 categories are universal necessities of thought.
- **Not a student-facing taxonomy**: students must never see category labels, axis names, or “you explored 6/8 dimensions”.
- **Not a quiz-trigger spec**: adaptive trigger logic is intentionally out of scope and will be designed later.

---

## 1) Pragmatic epistemological position
We treat the 8-category framework as:
- a **pedagogical checklist** for teachers/designers (coverage lens), and
- a **diagnostic measurement model** (behavioral signals), and
- an **empirical hypothesis** to be validated and refined with data.

### What we believe is practically useful
- Learners’ *question-selection behavior* (from a presented offer set) contains **probabilistic signals** about what they are attending to.
- Post-hoc classification of questions into a small set of diagnostic dimensions yields a usable “learning fingerprint” for instructional support.

### Learning path capture is a first-class product goal
We treat each learner’s exploration as a **sequential trajectory** through nodes and offered questions (not just aggregate counts).

Concretely, the product must be able to reconstruct:
- the **ordered path** of node visits and question selections (with timestamps),
- the **offer sets** that were shown at each step (counterfactual menu), and
- the resulting **transitions** (what the learner did next).

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
Categories are applied **after** question generation.

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

Subjects differ in **relative diagnostic importance**, implemented via weights (see `docs/subject-weighting-specification.md`).

**Rule**: adapt interpretation and prioritization via weights; do not delete dimensions.

---

## 3.5) How weights flow through the pipeline (diagnostic lens, not a generation constraint)
Subject weights are a **diagnostic lens** used downstream; they must not be used to "steer" Stage 1 generation.

- **Generation (Stage 1)**: organic, context-driven question generation. **No weights applied.** Only mild, non-categorical diversity instructions are allowed (e.g., avoid duplicates; vary angles naturally) to prevent degenerate repetition.
- **Classification (Stage 2)**: post-hoc mapping of each question to a diagnostic dimension. **Weights not applied.**
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

**Policy requirement**: always tag mode + policy version, and preserve an **organic discovery budget** (e.g., 30% as a starting point) to keep discovery data available.

To avoid personalization feedback loops corrupting measurement:
- **Stratify discovery** across student segments (grade level, proficiency bands, language, subject, etc.) so discovery data is not concentrated in a single subgroup.
- **Periodic re-randomization / diagnostic probes**: even for exploitation-mode students, periodically include small amounts of safely-randomized or organic content to detect preference drift and evaluate whether personalization is steering behavior.
- Treat the floor as **tunable**: if exploitation becomes highly personalized (or model uncertainty is high), increase discovery share or widen probe frequency.

---

## 5) Structural completeness (subject-weighted, empirical)
We define “structural completeness” operationally:
- a **weighted coverage score** over the 8 categories for a concept/session, and
- a set of **gap severities** derived from subject weights.

**Working hypothesis**: higher weighted coverage (especially in high-weight dimensions for that subject) correlates with better downstream learning outcomes. This must be tested and recalibrated.

---

## 6) Key design principles
1. **Organic-first generation**: questions are generated from context as a curious learner would ask—no categorical templates (and no attempt to optimize for category coverage at generation time).
2. **Post-hoc classification**: categories are applied after generation for diagnosis.
3. **Category-neutral student language**: any student prompts are phrased as natural suggestions (e.g., “Try comparing…”, “What happens if…”) without naming dimensions.
4. **Teacher-visible diagnostics**: teachers see category-weighted coverage, gaps, and suggested interventions.
5. **Multiple outcome measures**: validate signals using more than one outcome (e.g., retention, transfer tasks, time-to-mastery, confidence calibration, optional assessments).
6. **Subject-specific interpretation**: weights change what counts as a critical gap.

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

