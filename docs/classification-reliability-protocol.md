# Classification Reliability and Validation Protocol

**Document Version**: 1.0 (draft)
**Status**: Proposed
**Related Documents**: `docs/architecture/llm-pipeline.md`,
`docs/chapter-analysis-pipeline-specification.md`, `docs/architecture/backend-architecture.md`,
`docs/measurement-and-experimentation.md`, `docs/framework-design-philosophy.md`

---

## 1. Purpose

This document defines how the reliability and validity of the Stage 2 post-hoc classifier are
measured, what thresholds a classifier version must meet, and how those measurements gate the
deployment of any new classification `prompt_version` or `model_id`.

Everything downstream of classification — engagement profiles, coverage, dimensional-shift
detection, teacher-support views — inherits the classifier's error. This protocol is what makes
the suite's probabilistic claims honest: we state the instrument's measured precision and
validity instead of assuming them.

**Scope**: the runtime Stage 2 classifier (Haiku `claude-haiku-4-20250514`) that scores selected
questions on the 8 engagement dimensions (define, distinguish, decompose, connect, delimit,
predict, contextualize, vary). Chapter-analysis pipeline passes (P1–P11) have their own
verification gates and human QA and are out of scope here.

---

## 2. Position in the Documentation Suite

| Relationship | Document | Detail |
|--------------|----------|--------|
| **Supersedes (partially)** | `docs/architecture/llm-pipeline.md` | The classifier prompt there asks the model to return `classification_entropy`, and the `QuestionClassification` Pydantic model carries that field. This is superseded: **the model returns dimension scores only**; entropy, medians, dispersion, and flags are computed in code (§5). The prompt prose "Low entropy (<1.5) = confident" is likewise superseded. The entropy thresholds themselves (0.5 / 2.8) are retained. |
| **Extends** | `docs/chapter-analysis-pipeline-specification.md` §6.2 | That section states the runtime contract (reduced anchor scope, discrete scale, median-of-3, code-side entropy). This document supplies the measurement protocol, thresholds, and deployment gate around it. |
| **Depends on** | `docs/chapter-analysis-pipeline-specification.md` P8, P10 | Golden-set items are P8 seed questions; labels are assigned by the human analyst at the P10 QA gate (checklist item 5) and stored in Section C / golden set only. |
| **Depends on** | `docs/architecture/backend-architecture.md` §8.3 | Regression on prompt/model change is a replay operation: new outputs stamped with the new version and a `replay_id`, written alongside old rows, compared side-by-side. |
| **Consistent with** | `docs/measurement-and-experimentation.md` §4 | All classification artifacts carry the standard instrument stamps (`prompt_version`, `model_id`, `chapter_analysis_id`). |

---

## 3. The Instrument Under Test

- **Model**: `claude-haiku-4-20250514` via the `llm_gateway` module (backend §9), structured
  output mandatory (Instructor / tool-use JSON schema).
- **Output**: 8 per-dimension scores on the discrete ordinal scale **{0.0, 0.3, 0.6, 0.9}**.
  Nothing else — no entropy, no confidence, no flags (those are code's job).
- **Anchors**: per chapter-analysis spec §6.2 — the source concept's 8 P6 audit rows plus ≤ 2
  directly connected concepts' rows, with the calibration-only caution.
- **Why the discrete scale**: continuous scores produce false-precision jitter (0.62 vs 0.65 is
  noise that registers as disagreement in every statistic). Four anchored levels make any
  disagreement a real category step, make agreement statistics interpretable, and let human
  raters label on exactly the scale the model uses.

---

## 4. The Golden Set

### 4.1 Source and labeling

- Items are **P8 seed questions**: organically written (no deliberate dimension targeting),
  grounded in chapter passages, generated for every concept with ≥ 4 non-ABSENT audit dimensions.
- Labels are assigned by human analysts at the **P10 QA gate** (checklist item 5), on the
  0.0/0.3/0.6/0.9 anchors, after the calibration procedure in §7. Labels live in **Section C /
  golden set storage only** — never Section A (chapter-analysis storage-split rule).

### 4.2 Size and composition targets

| Property | Target |
|----------|--------|
| Total size | ~200 questions (grows as chapters pass P10) |
| Chapter spread | ≥ 8 chapters across ≥ 2 subjects |
| Dimension balance | Each of the 8 dimensions dominant in ≥ 15 items |
| Ambiguous items | ~10% genuinely multi-dimensional (no single dominant) — the classifier must not be tested only on easy cases |
| Edge items | ~5% near-unclassifiable (e.g., pure recall phrasing); expected `unclassifiable` flag recorded as part of the label |

Composition is reviewed quarterly (§10); imbalances are corrected by directing the next P10
labeling sessions, not by deleting items.

### 4.3 Item record

Each golden-set item stores: `question_text`, `concept_id`, `chapter_analysis_id`, grounding
segments, per-dimension consensus label, expected flags, `analyst_ids`, label date,
adjudication notes (if any), and `golden_set_version` at entry.

### 4.4 Versioning

- `golden_set_version` increments when items are added or a label is corrected.
- Items are never edited in place; a label correction supersedes the old record and is logged.
- Every reliability result reports the `golden_set_version` it ran against. Comparisons across
  classifier versions use the same golden-set version.

---

## 5. Runtime Aggregation Contract (median-of-3 + code-side arithmetic)

This is the production protocol for **every** classification, golden-set or live. The reliability
metrics in §6 are measured over this full protocol, not over single calls.

1. **Three runs** per question, temperature 0, identical prompt. (Temperature 0 does not
   guarantee determinism across API calls; the protocol absorbs residual nondeterminism.)
2. **Code takes the per-dimension median** of the three runs. The median vector is the stored
   classification.
3. **Code logs per-dimension dispersion** (max − min across the three runs). Dispersion > 0.3 on
   any dimension → `needs_review = true`. Dispersion is stored per dimension, per question —
   downstream consumers may filter on it.
4. **Code computes Shannon entropy** over the normalized median vector:
   - entropy > **2.8** → hedging: `is_classified = false`, `needs_review = true`
   - entropy < **0.5** → snapping: `is_classified = true`, `needs_review = true` (spot-check)
5. **All-zero vector** → `unclassifiable = true` (flagged, never silently stored).
6. Stored row (event `question_classified` + `analytic_rm.question_classifications`): median
   scores, dispersions, entropy, flags, `prompt_version`, `model_id`, `chapter_analysis_id`,
   and `replay_id` when produced by replay.

**The LLM performs no arithmetic.** No entropy, no medians, no averages, no flags. This is a
hard rule (backend §9.3); any prompt requesting computed quantities fails review.

---

## 6. Metrics and Thresholds

All metrics are computed in code by the reliability harness (`api/internal` golden-set runs,
backend §11). "Run" below means one full §5 protocol execution over the golden set.

### 6.1 Precision (run-to-run stability)

| Metric | Definition | Threshold |
|--------|------------|-----------|
| Vector stability | Mean cosine similarity between median vectors of two independent runs, per item, averaged over the set | **> 0.95** mean; additionally < 2% of items below 0.80 |
| Dominant-dimension agreement | Share of items whose top-scoring dimension matches across the two runs (ties resolved identically by deterministic code) | **> 90%** |

Why both: cosine can stay high while the dominant dimension flips on near-ties — and the dominant
dimension is the coarse signal teacher-support interpretation consumes, so it gets its own gate.
Precision is necessary, not sufficient: a consistently wrong classifier passes it.

### 6.2 Validity (agreement with human labels)

| Metric | Definition | Threshold |
|--------|------------|-----------|
| Human↔human Krippendorff's α (ordinal) | Agreement between the two analysts on the overlap set (§7), before adjudication | **≥ 0.67** — a *precondition*: below this, golden labels do not count and the remedy is rater calibration (§7), not prompt work |
| Model↔human Krippendorff's α (ordinal) | Classifier median vectors vs. adjudicated consensus labels, all items × dimensions | **≥ 0.67** ships *provisional*; **≥ 0.80** ships *reliable*; below 0.67 = no-ship |
| ICC(2,1) | Two-way random effects, single rater, absolute agreement, model vs. consensus per dimension | Reported, no hard gate — diagnostic (see below) |

- **Why α (ordinal)**: it penalizes a 0.3-vs-0.6 disagreement less than 0.0-vs-0.9 (correct for
  an anchored ordinal scale), handles multiple raters and missing data, and the 0.67/0.80
  cut-points are Krippendorff's published conventions.
- **Why ICC(2,1) alongside α**: a classifier that consistently scores 0.3 where humans say 0.6 is
  perfectly *ordered* but systematically deflated. ICC(2,1)'s absolute-agreement form catches the
  offset. Triage: low α + low ICC → noisy classifier (remedy: prompt clarity, better anchors);
  acceptable α + low ICC → biased classifier (remedy: recalibrate few-shot anchor examples).

### 6.3 Calibration (flag behavior)

| Metric | Definition | Band / threshold |
|--------|------------|------------------|
| Hedging flag rate | Share of golden-set items with entropy > 2.8 | Within ±5 percentage points of the incumbent version's rate, unless the change is intended |
| Snapping flag rate | Share with entropy < 0.5 | Same band rule |
| Dispersion distribution | Median and p90 of per-dimension dispersion | No more than 50% increase vs. incumbent |
| Unclassifiable detection | Known near-unclassifiable items (§4.2) flagged | ≥ 90% flagged; false `unclassifiable` on normal items < 2% |

### 6.4 Drift vs. incumbent

| Metric | Definition | Threshold |
|--------|------------|-----------|
| Per-dimension mean shift | Mean score per dimension, new vs. incumbent version, same golden-set version | Absolute shift ≤ 0.1 per dimension, or explicitly documented as intended |
| Production replay review | §8 replay comparison on a recent production sample | No unexplained mass migration of dominant dimensions; reviewed and signed off |

---

## 7. Human Inter-Rater Calibration Procedure

Golden-set labels are only as good as the humans producing them. Before any analyst's labels
enter the golden set:

1. **Anchor training**: the analyst studies the dimension definitions and the 0.0/0.3/0.6/0.9
   anchor descriptions, plus 10 worked examples with rationale.
2. **Calibration round**: two analysts independently label the same 20 questions, then discuss
   every disagreement against the anchors. Anchor-definition ambiguities discovered here are
   fixed in the definitions document (versioned), not resolved ad hoc.
3. **Qualification**: the analysts independently label a fresh overlap set of ≥ 30 questions.
   **Krippendorff's α (ordinal) ≥ 0.67** on this set qualifies the pair. Below 0.67: repeat
   from step 2; persistent failure means the anchor definitions are defective — revise and
   relabel rather than forcing agreement.
4. **Production labeling**: each golden-set item is labeled independently by two analysts.
   Disagreements of ≥ 2 scale steps on any dimension are adjudicated to consensus (logged);
   1-step disagreements resolve to the lower score (conservative default, logged).
5. **Refresh**: recalibration (steps 2–3) runs whenever a new analyst joins, anchor definitions
   change, or the quarterly review (§10) shows human α decaying below 0.67.

---

## 8. Regression Procedure on Prompt or Model Change

Replay-based, per backend architecture §8.3. Applies to any change to the classification prompt
(`prompt_version` bump) or model (`model_id` change). Version values are code constants bumped
in the same commit as the change (backend §10 rule 2).

1. **Golden-set run**: execute the full §5 protocol over the current golden-set version under
   the candidate version, twice (for §6.1 stability). Outputs are stamped with the candidate
   `prompt_version`/`model_id` and stored alongside incumbent results.
2. **Production replay**: replay classification over a recent production sample — last 14 days
   or ≥ 500 questions, whichever is larger — with a `replay_id`. Outputs are written alongside
   the incumbent rows, never overwriting (backend §8.3.2).
3. **Comparison**: the harness computes the full §6 metric table for the candidate, side-by-side
   with the incumbent, plus the per-dimension shift analysis and flag-rate deltas on both the
   golden set and the replayed production sample.
4. **Decision**: apply the §9 gate. For a **model change** (new `model_id`), two additions:
   the *reliable* threshold (α ≥ 0.80) is required rather than provisional, and a human
   spot-check of 30 replayed production classifications is mandatory before cutover.
5. **Cutover / rollback**: cutover = consumers (projections, teacher-support views) re-pin to
   the new version; rollback = re-pin back. No rows are deleted in either direction.

---

## 9. Deployment Gate for a New `prompt_version`

All of the following must hold, on the same `golden_set_version`, before a candidate version
serves production traffic:

| # | Gate | Source |
|---|------|--------|
| 1 | Human↔human α ≥ 0.67 on the labels in play (standing precondition) | §6.2 |
| 2 | Model↔human α (ordinal) ≥ 0.67 (provisional) or ≥ 0.80 (reliable) | §6.2 |
| 3 | Vector stability mean cosine > 0.95; < 2% of items below 0.80 | §6.1 |
| 4 | Dominant-dimension agreement > 90% | §6.1 |
| 5 | Flag rates and dispersion within §6.3 bands (or intended + documented) | §6.3 |
| 6 | Per-dimension drift within §6.4 tolerance (or intended + documented) | §6.4 |
| 7 | Production replay comparison reviewed and signed off | §8 |
| 8 | ICC(2,1) reviewed; any systematic bias triaged and accepted or fixed | §6.2 |

**Provisional status** (α in [0.67, 0.80)): deployment is allowed, with mandatory weekly drift
checks (§10) and a recorded review-by date (≤ 8 weeks) by which the version must either reach
reliable status (after golden-set growth or prompt iteration) or be revisited.

**Reliable status** (α ≥ 0.80): standard cadence applies.

The gate result — metric values, golden-set version, decision, sign-off — is recorded against
the candidate version. A version with no recorded gate result must not serve production traffic.

---

## 10. Cadence of Reliability Checks

| Check | Frequency | Content |
|-------|-----------|---------|
| Full deployment gate (§9) | Every prompt or model change | Complete §6 metric table + replay |
| Drift sample | Weekly | Re-run a fixed 25-item drift subset of the golden set under the live version; compare against that version's gate-time results. Alert on any §6 threshold breach |
| Flag-rate monitoring | Weekly (same job) | Hedging/snapping/dispersion rates over live production classifications vs. gate-time bands |
| Golden-set growth | Per chapter at P10 | New labeled seed questions enter; `golden_set_version` bump |
| Validity refresh | Monthly | Human analyst labels 20 sampled *production* classifications blind; model↔human α computed on the sample — guards against golden-set unrepresentativeness |
| Composition review | Quarterly | §4.2 balance check; human α decay check; anchor-definition review |

---

## 11. Arithmetic-in-Code Rule (consolidated)

For avoidance of doubt, the following quantities are computed **only in code** (`classification`
module / `llm_gateway`, backend §9.3), never requested from or trusted from the model:

Shannon entropy, per-dimension medians, per-dimension dispersion, all flags (`needs_review`,
`is_classified`, `unclassifiable`), cosine similarity, dominant-dimension determination and
tie-breaking, Krippendorff's α, ICC, all rates and shift statistics.

This supersedes the `classification_entropy` field and prompt instruction in
`docs/architecture/llm-pipeline.md` (§2 of this document). That document should be annotated
accordingly when next revised.

---

## 12. Open Items

1. **Drift-subset selection** — the fixed 25-item weekly subset should be stratified by
   dimension and difficulty; selection procedure to be defined when the harness is built.
2. **Per-subject golden sets** — whether physics/biology/chemistry need separate threshold
   tracking once multiple subjects are live (composition targets in §4.2 are a start).
3. **Anchor-definitions document** — the rater-facing dimension/anchor definitions with worked
   examples (§7.1) is referenced but not yet written; it is a prerequisite for the first
   calibration round.
4. **Tie-breaking rule** — deterministic dominant-dimension tie-break (e.g., fixed dimension
   order) must be specified in code before §6.1 agreement is measurable.

---

*Document Version 1.0 (draft) | Classification Reliability and Validation Protocol*
*Platform: Path-Based Conceptual Exploration and Teacher-Support System*
