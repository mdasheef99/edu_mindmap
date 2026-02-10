# Measurement and Experimentation Specification

## Purpose
This document formalizes the platform’s **data collection and experimentation strategy** needed to preserve measurement quality while the system personalizes question offers.

It operationalizes Section 4 (“offer sets + discovery vs exploitation”) in `docs/framework-design-philosophy.md`.

## Non-goals / guardrails
- Not a UX spec (student UI remains **category-neutral**).
- Not an adaptive intervention spec (teacher interventions may be logged, but design is separate).
- Not a guarantee of causality; this defines the **instrumentation + traffic policy** required to estimate effects.

## Core principles
1. **Offer-set logging is mandatory**: log what was offered, what was shown, and what was chosen.
2. **Discovery is protected**: maintain a tunable discovery budget + stratification.
3. **Probes exist inside exploitation**: periodic randomized probes detect steering + preference drift.
4. **Off-policy evaluation requires propensities**: log selection probabilities (or randomization mechanism) per option.

## Definitions
- **Offer set**: the concrete menu of options presented for a decision.
- **Discovery mode**: measurement-first traffic (more organic, limited personalization, controlled randomness).
- **Exploitation mode**: experience-optimized traffic (ranking, caching, interventions), still logged.
- **Diagnostic probe**: a small, randomized perturbation embedded in exploitation to preserve identifiability.

---

## 1) Discovery stratification rules
### 1.1 Segment definition
A **segment key** is a stable tuple used to stratify discovery allocation. Recommended primary axes:
- grade_band (e.g., 3–5 / 6–8 / 9–10 / 11–12)
- proficiency_band (e.g., low / mid / high; derived, versioned)
- language (UI language)
- subject (math/science/history/etc.)
- device_tier (optional; e.g., low/mid/high capability)

**Rule**: segment definitions must be versioned (`segment_schema_version`).

### 1.2 Allocation policy (how discovery budget is assigned)
Let `B_total` be the global discovery budget (starting point: 30%; tunable).

Requirements:
- **Per-segment minimum**: every segment receives at least `B_min` discovery (e.g., 10%) so measurement is not concentrated.
- **Stratified remainder**: the remaining discovery budget is allocated by a weighted function of:
  - segment traffic volume
  - model uncertainty / drift indicators
  - fairness/coverage priorities (explicitly configured)

Operational guideline (practical default):
- `B_total = clamp(0.30, 0.15, 0.60)` initially; adjust upward when personalization intensity increases.
- `B_seg = max(B_min, f(seg))` where `f(seg)` is proportional to uncertainty × importance.

### 1.3 Avoiding “cell explosion”
If the Cartesian product of axes yields too many tiny segments:
- Use **hierarchical backoff**: allocate by (subject, grade_band) first; then refine by language/proficiency when volume allows.
- Merge rare segments into “other” buckets while preserving `segment_schema_version`.

### 1.4 Monitoring and triggers to raise discovery
Discovery budget MUST increase (globally or for specific segments) when any condition holds:
- strong personalization (large ranking score spread; high repeat-rate of similar options)
- detected preference drift (probe outcomes change materially)
- sparse overlap (propensity mass near 0/1 for most options)
- large unexplained outcome variance across segments

---

## 2) Diagnostic probe design (inside exploitation)
### 2.1 Frequency and placement
Probes occur in exploitation mode with probability `p_probe` per offer set.

Baseline defaults (tunable per subject/grade):
- `p_probe = 0.05` (≈ 1 probe per 20 offer sets), OR
- at least **1 probe per session** if session length is short.

### 2.2 Probe construction
A probe offer set is a **controlled mixture** that preserves UX but introduces overlap:
- Keep total options constant (e.g., 4–6).
- Reserve `k_probe` slots (e.g., 1–2) for randomized candidates.
- Candidate sources for probe slots:
  - organic generation (fresh)
  - long-tail cached items (low exposure)
  - safely-randomized re-ranking among top-N candidates

**Hard constraints**:
- No category labels in student-visible text.
- No forced “cover all dimensions” objectives.
- Respect safety/age filters and content policies.

### 2.3 Randomization method (must be loggable)
Supported probe randomization mechanisms:
- **Epsilon-greedy**: with probability ε, pick uniformly from a candidate pool; else use ranker.
- **Top-N shuffle**: shuffle the top-N candidates with a logged seed.
- **Uniform slot injection**: fill designated probe slots uniformly at random.

**Rule**: deterministic personalization without probes is not acceptable for measurement.

---

## 3) Minimum per-segment sample targets
### 3.1 What “sample” means
Primary unit: **offer sets** (and their impressions + selections). Secondary: downstream outcomes (assessments, retention).

### 3.2 Practical minimums (starting guidance)
For each segment × policy_version (per evaluation window, e.g., weekly):
- `N_offer_sets >= 1,000` (target) and `>= 300` (minimum) in discovery+probe traffic.
- `N_choices >= 300` (minimum) to estimate choice proportions with reasonable error.

If volume is low:
- widen the window (biweekly/monthly), or
- merge segments using hierarchical backoff.

### 3.3 Statistical note (for proportion estimates)
To estimate a selection rate `p` with margin `e` at 95% confidence:
- worst-case `n >= 0.25 * (1.96/e)^2` (since p(1-p) ≤ 0.25).
Example: `e=0.05` ⇒ `n≈384` selections.

For outcome experiments (A/B or policy comparisons): define desired effect size + power; compute per-segment targets accordingly.

---

## 4) Required logging fields for off-policy evaluation
### 4.1 Event model (recommended)
Log **separate events** so exposure vs choice is distinguishable:
1. `offer_set_created`
2. `offer_set_impression` (what was actually shown/visible)
3. `offer_set_choice`
4. `learning_outcome` (later joins)

All events MUST include join keys:
- `offer_set_id`, `student_id_pseudo`, `session_id`, `node_id`, `timestamp`
- `mode` (discovery|exploitation), `policy_name`, `policy_version`
- `experiment_id` (optional), `variant_id` (optional)
- `feature_flags` (optional snapshot), `app_version`, `client_platform`
- `segment_key`, `segment_schema_version`

### 4.2 `offer_set_created` (counterfactual menu)
- `options[]`: per option
  - `option_id` (stable), `question_id` (if applicable), `text_hash`, `rendered_text` (or `text_ref`)
  - `rank_position`
  - `source` (organic_llm|cache|teacher_variant|probe)
  - `candidate_pool_id` / `cache_key` (if relevant)
  - `model_id` + `prompt_version` (if LLM-generated)
  - `policy_params` (e.g., epsilon value, top-N used, probe settings)
  - `scores` (ranker scores/features snapshot, if used)
  - `propensity` (probability this option appears in this slot under the policy)
  - `is_probe` (bool), `random_seed` / `randomization_id`
- latency: `gen_ms`, `rank_ms`, `total_ms`

### 4.3 `offer_set_impression` (what the learner could actually see)
- `visible_option_ids[]` (subset of offered options)
- `ui_positioning` (order as rendered)
- optional: `scroll_depth`, `time_visible_ms`

### 4.4 `offer_set_choice` (decision)
- `selected_option_id`
- `time_to_select_ms`
- optional: `dismissed` / `no_selection`

### 4.5 `learning_outcome` (downstream signals)
- `outcome_type` (assessment|retention|transfer|time_on_task|teacher_rating|etc.)
- `value` (typed) + `instrument_version`
- join keys: `student_id_pseudo`, `session_id` (or timeframe window)

### 4.6 Privacy and integrity
- Do not store raw PII in events.
- Version every policy and schema.
- Maintain an audit trail for policy changes that affect propensities or candidate pools.

