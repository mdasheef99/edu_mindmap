# Outcome Instrumentation Specification

**Document Version**: 1.0 (draft)
**Status**: Proposed
**Related Documents**: `docs/measurement-and-experimentation.md`,
`docs/mvp-features-specification.md`, `docs/teacher-support-mvp-specification.md`,
`docs/architecture/backend-architecture.md`, `docs/framework-design-philosophy.md`,
`docs/student-reflective-guidance-and-self-review.md`

---

## 1. Purpose

The platform's claims — that path-based exploration supports sensemaking, and that dimensional
coverage relates to exam readiness — are testable only if outcomes are instrumented. This
document specifies the two outcome instruments of Phases 1–3:

1. **PYQ (previous year question) attempt tracking** — the primary *external* outcome
   instrument: performance on questions written by exam boards, independent of our own
   generation pipeline.
2. **Reflective Checkpoints (Sensemaking Pauses)** — the *intermediate, in-product* probe:
   close in time to exploration, weaker in external validity. The two triangulate.

Both produce evidence for **research and measurement**, and bounded signals for **teacher
support**. Neither produces grades, mastery scores, or pass/fail verdicts — see §3.

## 2. Position in the Documentation Suite

| Relationship | Document | Detail |
|--------------|----------|--------|
| **Extends** | `docs/measurement-and-experimentation.md` §4.5 | That section defines the `learning_outcome` event shape (`outcome_type`, typed `value`, `instrument_version`, join keys). This document instantiates it for PYQ attempts and adds the supporting PYQ event family. |
| **Extends** | `docs/architecture/backend-architecture.md` §6.2 | Adds a **PYQ event family** (`pyq_viewed`, `pyq_added_to_map`) to the event type registry; uses the existing Reflection (`checkpoint_offered`, `checkpoint_response`) and Outcomes (`learning_outcome`) families. |
| **Depends on** | `docs/mvp-features-specification.md` Feature Groups 5 & 6 | Checkpoint trigger and soft-participation UI (5.1–5.2); PYQ panel and add-to-map (6.1–6.2). This document does not change those features; it specifies their instrumentation. |
| **Bounded by** | `docs/teacher-support-mvp-specification.md` §7–8 | Checkpoint interpretation phrasings and the no-quizzes/no-grades boundary are normative; §5.4 reproduces the rules by reference, not restatement. |
| **Bounded by** | `docs/framework-design-philosophy.md` | All claims derived from these instruments are probabilistic and condition-scoped. |
| **Consistent with** | `docs/student-reflective-guidance-and-self-review.md` | Any future learner-facing use of these signals stays category-neutral and non-diagnostic. |

---

## 3. Terminology Resolution: "Intermediate Quiz" → Reflective Checkpoint

The phrase "intermediate quiz" appeared in planning discussion. It is **resolved in favor of the
Reflective Checkpoint model** and the term "quiz" is not used anywhere in this layer:

- The MVP explicitly excludes quizzes, tests, grades, and progression gates
  (`docs/mvp-features-specification.md` Scope Boundary Notes; `docs/teacher-support-mvp-specification.md` §8).
- Checkpoints are **non-mandatory, low-stakes sensemaking invitations**. Every response option
  — including declining — is a valid, non-punitive outcome. Nothing is scored, passed, or failed.
- What the platform gains from a quiz (an intermediate signal between exploration and exam
  performance) is obtained instead from checkpoint participation patterns and reflection
  presence/coherence — framed as **probabilistic evidence of sensemaking**, never measurement
  of understanding.

PYQ attempts are also not quizzes: they are a student-initiated study resource with a
reveal-answer flow (§4.2). The instrumentation observes; it does not examine.

---

## 4. Instrument 1 — PYQ Attempt Tracking (primary external outcome)

### 4.1 Why PYQs

PYQs are the only outcome source in Phases 1–3 that is (a) external to our generation pipeline
(written by exam boards, immune to our prompt drift), (b) aligned with the user's actual goal
(NEET/JEE/CBSE performance), and (c) already in-product as a study resource (Feature Group 6).
They carry official answer keys, so correctness is determinable without grading authority.

### 4.2 Student-facing framing constraints

The PYQ surface remains exactly what Feature Group 6 specifies — a study resource. Instrumenting
it must not change its character:

- Attempting is student-initiated; no PYQ is pushed as an assessment.
- The flow is attempt → reveal answer (with explanation where available). For MCQ-format
  questions the selected option is captured; for non-MCQ formats the student may optionally
  self-mark after reveal (*Got it / Not yet / Not sure*).
- **No score displays, streaks, percentages, leaderboards, or aggregate performance views** in
  Phases 1–3. The student sees the answer to the question they tried, nothing cumulative.
- Skipping the reveal, abandoning, or browsing without attempting are all unremarkable actions —
  logged, never discouraged.

### 4.3 Events captured

| Event | Family | When | Key payload fields |
|-------|--------|------|--------------------|
| `pyq_viewed` | PYQ (new) | Question opened in panel or detail | `pyq_id`, `exam`, `year`, `chapter_id`, surface (`panel` / `map_node`) |
| `pyq_added_to_map` | PYQ (new) | Feature 6.2 add-to-map | `pyq_id`, `node_id`, `session_id` |
| `learning_outcome` | Outcomes (existing) | Attempt resolves (answer selected / self-marked / revealed without attempt) | §4.4 |

### 4.4 The `learning_outcome` event for a PYQ attempt

Per measurement spec §4.5, with PYQ-specific payload:

| Field | Content |
|-------|---------|
| `outcome_type` | `performance_check` |
| `instrument` | `pyq_attempt` |
| `instrument_version` | Version of this capture contract (§7) |
| `value` | `{ result: correct \| incorrect \| self_marked_got_it \| self_marked_not_yet \| self_marked_not_sure \| revealed_without_attempt, response_format: mcq \| numeric \| open, selected_option?, time_to_resolve_ms, attempt_index }` |
| PYQ identity | `pyq_id`, `exam` (NEET/JEE/CBSE...), `year`, `pyq_mapping_version` (§4.5) |
| Context | `chapter_id`, mapped `concept_ids`, surface (`panel` / `map_node`), `node_id` if attempted from a map node |
| Join keys | `student_id_pseudo`, `session_id`, `tenant_id`, `timestamp`, `app_version`, `client_platform`, `segment_key`, `segment_schema_version` — the standard set from measurement spec §4.1 |

`attempt_index` distinguishes first attempts from repeats; analyses default to first attempts.
`revealed_without_attempt` is captured because reveal-first study is a legitimate strategy, not
a missing data point — but it is excluded from performance analyses.

### 4.5 PYQ → concept mapping

Joining outcomes to exploration requires knowing which concepts a PYQ touches. Mapping is
produced at PYQ ingestion time (chapter and concept assignment against the chapter-analysis
concept inventory), stamped `pyq_mapping_version`, and stored with the PYQ record. The mapping
pipeline itself is an open item (§8.1); until it exists, joins operate at `chapter_id`
granularity only.

### 4.6 Joining outcomes back to exploration paths

Standard join keys (measurement spec §4.1) make these analyses queryable without new mechanisms:

- **Within-session**: `session_id` links an attempt to the exploration that preceded it,
  including offer-set lineage (`offer_set_id` chains) when the PYQ was reached from a map node.
- **Cross-session**: `student_id_pseudo` + `chapter_id` + timeframe windows — e.g., dimensional
  coverage accumulated in a chapter *as of attempt time* (event-time join, same discipline as
  backend §7.4 interval joins) vs. first-attempt results.
- **Condition-scoped**: every joined row carries the instrument stamps (`policy_version`,
  `chapter_analysis_id`, classification `prompt_version`), so relationships are always stated
  per-condition, per `docs/measurement-and-experimentation.md`.

### 4.7 Analysis uses and constraints

- Primary research question: does dimensional coverage breadth/shape predict first-attempt PYQ
  performance, within segment and condition?
- **Correlational first**; causal claims require the experiment designs in the measurement spec.
- Sample minimums per measurement spec §3.2 apply; segment-level results only.
- **Never per-student verdicts**: PYQ results do not render as student-level performance
  summaries on any surface (student or teacher) in Phases 1–3 (§6).

---

## 5. Instrument 2 — Reflective Checkpoints (intermediate in-product probe)

### 5.1 Role

Checkpoints sit between raw exploration behavior and external outcomes: they probe whether the
student can articulate something about the conceptual move their path just made, at the moment
it happens. They are nearer in time than PYQs (better attribution) but weaker in external
validity (self-expression, not exam performance). Analyses use both.

### 5.2 Trigger (by reference)

Per `docs/mvp-features-specification.md` Feature 5.1: eligibility requires cosine distance
≥ **0.35** between prior and recent rolling-window classified vectors, a dominant-dimension
change, sufficient prior context, and cooldown clearance. This document does not modify the
trigger; it specifies what is recorded around it.

### 5.3 Capture contract

Two events (existing Reflection family, backend §6.2):

**`checkpoint_offered`** — emitted whenever an eligible checkpoint is shown:

| Field | Content |
|-------|---------|
| `checkpoint_id` | Unique per offer; joins the response |
| `trigger_type` | `dimensional_shift` (only type in MVP) |
| `prior_vector`, `recent_vector` | The rolling-window vectors that triggered eligibility |
| `cosine_distance`, `entropy_delta` | Computed in code |
| `prompt_ref` / `prompt_text` | The reflection prompt shown, with generation `prompt_version`/`model_id` if AI-generated |
| `reappearance` | `first` / `post_snooze` |
| `policy_version` | Trigger policy version (thresholds, cooldown) |
| Join keys | Standard set (`student_id_pseudo`, `session_id`, `node_id`, `chapter_id`, `tenant_id`, timestamps, stamps) |

Eligibility evaluations that do *not* result in an offer (cooldown, context insufficient) are
logged in the analytic lane per Feature 5.1's analytics requirements, not as offers.

**`checkpoint_response`** — emitted on the student's action:

| Field | Content |
|-------|---------|
| `checkpoint_id` | Joins the offer |
| `action` | `try_now` / `not_sure_yet` / `snooze` / `skip` (also `dismissed` if the sheet is closed without choosing) |
| `response_text` | Only for `try_now`; optional even then |
| `latency_ms` | Offer-to-action time |

### 5.4 Interpretation rules

Interpretation is normatively defined by `docs/teacher-support-mvp-specification.md` §7 (exact
teacher-facing phrasings) and the soft-participation rules in
`docs/mvp-features-specification.md` Feature 5.2. Summary of what each action *is evidence of*:

| Action | Evidence of | Never read as |
|--------|-------------|---------------|
| Try Now + response | Willingness to articulate; the response's presence and coherence are a sensemaking signal | Correctness, mastery, a graded answer |
| Not Sure Yet | Metacognitive self-awareness — the student noticed uncertainty | Failure, weakness |
| Snooze | Timing preference; may reappear once after cooldown | Avoidance |
| Skip | Agency; a single skip is an opt-out event | Avoidance, misunderstanding, refusal |

**Response-text handling**: any automated read of `try_now` text is limited to presence and
coherence (did the student engage with the prompt at all), is stamped with its
`prompt_version`/`model_id` if LLM-assisted, lives in `analytic_rm` only, and surfaces solely
through the hedged phrasings of teacher-support §7. It is never scored for correctness.

### 5.5 Storage separation

Checkpoint signals are stored **separately from exploration coverage** and are never merged
into coverage, any mastery-like scalar, or any composite "understanding" metric
(`docs/mvp-features-specification.md` Feature 5.2 analytics requirements). They may sit
*alongside* coverage in teacher-support views, clearly distinct.

### 5.6 Relationship to `learning_outcome`

Checkpoint responses are **not** `learning_outcome` events — they keep their own family. They
participate in outcome *analyses* (e.g., does checkpoint participation correlate with later PYQ
performance?) through the shared join keys, but the event taxonomy keeps the probe distinct
from the outcome.

---

## 6. What These Instruments Must Never Do

Binding on all surfaces and all phases through Phase 3:

1. No grades, marks, percentages, mastery scores, or pass/fail derived from either instrument.
2. No student-visible cumulative performance views (PYQ or checkpoint).
3. No teacher-facing verdict language; only the hedged register of teacher-support §7 and the
   dashboard phrasing catalog (`docs/teacher-dashboard-specification.md` §7).
4. No use of checkpoint opt-outs as negative evidence about understanding; repeated-pattern
   surfacing follows teacher-support §7's threshold and low-certainty language only.
5. No gating of product features on outcomes (no "score X to unlock Y").
6. No per-student PYQ performance reporting to teachers or admins in Phases 1–3; aggregates, if
   ever introduced, go through the K-suppression and claim-boundary review (open item §8.3).
7. No runtime adaptation keyed off outcomes in Phases 1–3 (consistent with no-ML-training and
   the teacher-feedback rule in `docs/teacher-dashboard-specification.md` §8.3).

---

## 7. Versioning

| Stamp | Bumped when |
|-------|-------------|
| `instrument_version` (on `learning_outcome`) | The capture flow changes meaning — e.g., self-mark options change, reveal flow changes, `value` schema changes |
| `pyq_mapping_version` | The PYQ → concept mapping method or data changes |
| `policy_version` (on checkpoint events) | Trigger thresholds, cooldown, or reappearance rules change |
| `prompt_version` / `model_id` | Reflection-prompt generation or response-text reading changes |
| `event_version` | Payload schema changes, per backend §6.2 registry rules |

Analyses never pool across `instrument_version` values without an explicit bridging note.

---

## 8. Open Items

1. **PYQ → concept mapping pipeline** (§4.5): ingestion-time mapping procedure, human QA
   sampling, and storage contract need their own short spec before concept-level joins ship.
2. **Self-mark UI** for non-MCQ formats: wording and placement of *Got it / Not yet / Not sure*
   need UX design that keeps the non-evaluative register.
3. **Aggregate PYQ visibility**: whether any chapter-level PYQ aggregate ever reaches the
   teacher dashboard — deferred; requires claim-boundary review + K-suppression design.
4. **Retention/transfer instruments**: `outcome_type` values beyond `performance_check`
   (retention, transfer) have no instrument in Phases 1–3; revisit with the validation study
   design.
5. **Checkpoint prompt quality**: a review loop for AI-generated reflection prompts
   (category-neutrality scan, per Stage 1 meta-language rules) — currently assumed, not specified.

---

*Document Version 1.0 (draft) | Outcome Instrumentation Specification*
*Platform: Path-Based Conceptual Exploration and Teacher-Support System*
