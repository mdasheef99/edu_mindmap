# Chapter Analysis Pipeline Specification

**Document Version**: 1.0 (draft)
**Status**: Proposed — implements Layer 2 chapter analysis from `docs/prd/master-prd.md` §4
**Related Documents**: `docs/prd/master-prd.md`, `docs/system-architecture.md`, `docs/framework-design-philosophy.md`, `docs/architecture/llm-pipeline.md`, `docs/subject-weighting-specification.md`, `docs/measurement-and-experimentation.md`, `docs/chapter-topology-specification.md`

---

## 1. Purpose

This pipeline pre-analyzes each launch chapter before students arrive. Its outputs:

1. ground runtime Stage 1 generation in chapter structure (Section A),
2. anchor runtime Stage 2 classification in chapter-specific language (Section B),
3. establish the dimensional availability landscape against which exploration is interpreted for teacher support (Section C), and
4. provide the structural substrate — concept graph, emphasis weights, outcome map — for the chapter-topology layer (`docs/chapter-topology-specification.md`, Section C).

Per `docs/prd/master-prd.md` §6, a chapter must not ship without a completed and QA-passed analysis.

---

## 2. Pipeline Overview (execution order)

Steps are numbered in execution order. P-numbers are the only identifiers used in code and storage.

| Step | Name | Type | Model |
|------|------|------|-------|
| P0 | Segmentation & Ingestion | Code | — |
| P1 | Named Concept Extraction | LLM | Sonnet (`claude-sonnet-4-20250514`) |
| P2 | Embedded Concept Extraction | LLM | Sonnet |
| P3 | Merge & Deduplication | Code + LLM adjudication | Haiku (`claude-haiku-4-20250514`) |
| P4 | Typed Relationship Graph | LLM | Sonnet |
| P5 | Evidence Store | Code | — |
| P6 | Dimension Audit | LLM (one call per concept) | Sonnet |
| P7 | Cross-Concept Productive Pairs | LLM | Sonnet |
| P8 | Seed Questions | LLM | Sonnet |
| P9 | Richness Profiles & Chapter Weight Modifiers | Code | — |
| P10 | Human QA Gate | Human analyst | — |
| P11 | Prior Conceptions Backlog | LLM | Sonnet |
| P12 | Structural Metrics & Emphasis Weights | Code | — |
| P13 | Outcome-to-Subgraph Mapping | LLM | Sonnet |

P12 and P13 are specified in `docs/chapter-topology-specification.md`. Dependency order: P13 runs
after P4; P12 runs after P5, and its outcome-dependent term (composite edge criticality) is
recomputed after P13.

**Cross-cutting rules (apply to every LLM pass):**

- **Structured output is mandatory** (Anthropic tool-use JSON schema or Instructor/Pydantic). No free-text JSON parsing.
- **All arithmetic is computed in code, never by the model.** This includes richness profiles, entropy, confidence bands, counts, and weight modifiers.
- Every LLM pass is followed by the verification gate defined in §5.
- Every LLM pass output records its `prompt_version` and `model_id`.

---

## 3. Output Versioning (mandatory)

Every chapter analysis is wrapped in a versioned envelope:

```json
{
  "chapter_analysis_id": "ca_uuid",
  "chapter_id": "ch_phys10_electricity",
  "subject": "physics",
  "source_doc_hash": "sha256 of source PDF/text bytes",
  "segment_index_version": "1",
  "pipeline_version": "1.0.0",
  "pass_versions": {"P1": {"prompt_version": "1", "model_id": "claude-sonnet-4-20250514"}},
  "created_at": "ISO-8601",
  "qa_status": "pending | passed | failed"
}
```

Rules:

- Runtime layers may only consume analyses with `qa_status = "passed"`.
- All runtime events that depend on chapter analysis (offer sets, classifications, teacher-support
  interpretation) must record the `chapter_analysis_id` they ran against, consistent with the
  version-stamping requirements in `docs/measurement-and-experimentation.md` §4.

---

## 4. Data Boundary Sections

| Section | Contents | Consumers |
|---------|----------|-----------|
| **A — Generation context** | P1–P5 outputs, P7 pairs, P8 seed question text | Runtime Stage 1 prompt assembler |
| **B — Classification anchors** | P6 dimension audit | Runtime Stage 2 classifier |
| **C — Teacher support & research** | P6 audit, P9 profiles/modifiers, P11 backlog, P10 QA labels, P12 structural metrics, P13 outcome map | Teacher-support interpretation, graph-diff projections, validation studies |

**Enforcement**: the runtime Stage 1 prompt assembler has no file path, key, or variable referencing
Sections B or C. Enforced in code (separate storage keys and separate read APIs), not by convention.
No dimension labels may appear anywhere inside Section A content.

---

## 5. Verification Gate (code, runs after every LLM pass)

| # | Check | On failure |
|---|-------|------------|
| 1 | Output validates against the pass's JSON schema | Hard fail → retry pass |
| 2 | Every cited segment ID exists in the P0 segment index | Hard fail → retry pass |
| 3 | Each cited segment fuzzy-contains the concept label or a close variant | Warn → `qa_review_queue` |
| 4 | All relationship/pair endpoints exist in the merged concept list | Hard fail → retry pass |
| 5 | Counts within parameterized density bounds (§ per pass) | Warn → `qa_review_queue` |
| 6 | All enum fields contain allowed values only | Hard fail → retry pass |

Hard failures abort and retry the pass (max 2 retries, then halt for human attention).
Warn-level items accumulate in `qa_review_queue` and must be resolved at P10.

---

## P0 — Segmentation & Ingestion (Code)

**Purpose**: produce the stable segment IDs that every later citation resolves against. Without this
pass, LLM-cited passage references are unverifiable.

**Input**: source chapter PDF or text.

**Process**:

1. Extract text per page using `pypdf` (successor to the deprecated PyPDF2; the existing
   `extract_pdf.py` script is the seed of this step and should be restructured into it).
2. Split into typed segments: `para`, `example`, `activity`, `figure_caption`, `table`,
   `summary_point`, `question`. `question` segments additionally record
   `location: in_text | end_of_chapter` — end-of-chapter exercises are the authority's outcome
   specification (consumed by P13); in-text questions are scaffolding checks.
3. Assign deterministic IDs: `[<chapter_id>_<segment_type>_<NNN>]`,
   e.g. `[ch_phys10_electricity_para_014]`. Same input bytes → same IDs.
4. Store the segment index: `segment_id`, `segment_type`, `text`, `page`, `char_span`
   (+ `location` for `question` segments). `char_span` must cover the stripped `text` only,
   not any surrounding whitespace from the raw block.
5. Render the **segmented chapter text**: full chapter text with segment ID markers inline.
   This rendered form — never the raw text — is what all LLM passes receive.

**Output**: segment index + segmented chapter text + `segment_index_version`.


---

## P1 — Named Concept Extraction (LLM, Sonnet)

**Input**: segmented chapter text. One call per chapter.

**SYSTEM PROMPT:**

> You are analyzing a chapter from a [SUBJECT] textbook for [CLASS_LEVEL] ([CURRICULUM]). Your task is to extract every concept the chapter explicitly names and treats as an object of instruction — terms it defines, states, or builds explanation around.
>
> For each concept produce:
> - `concept_id`: snake_case identifier, stable within this chapter
> - `label`: the concept's name exactly as the chapter uses it
> - `definition`: one to two sentences stating what the concept is, **using only what this chapter says** — do not import outside knowledge
> - `category_tag`: one value from the provided tag list
> - `passage_refs`: segment IDs where the chapter engages this concept:
>   - `definitional`: exactly 1 segment ID — where the chapter defines or first states it
>   - `explanatory`: 0–2 segment IDs — where the chapter explains how/why it works
>   - `application`: 0–2 segment IDs — where the chapter applies it (examples, activities, devices)
>
> Allowed `category_tag` values: [SUBJECT_TAG_ENUM]
>
> Cite only segment IDs that appear in the provided text. Every concept must have a definitional citation.

**USER PROMPT:**

> Here is the segmented chapter text:
>
> [SEGMENTED CHAPTER TEXT]
>
> Extract all named concepts. Produce output as a JSON object with a `concepts` array. Set `extraction_pass` to `"P1"` on each record.

**DO NOT:**
- Invent concepts the chapter does not name
- Write definitions from general knowledge rather than the chapter's own treatment
- Cite a segment ID not present in the provided text
- Include skills ("solving numericals") or chapter-navigation items ("summary") as concepts

**Parameters**: `[SUBJECT_TAG_ENUM]` is a per-subject configuration list (e.g., physics: `quantity`, `law`, `device`, `phenomenon`, `material_property`). It is config, not prompt text to be edited per chapter.

**Verification**: gate checks 1–3, 6. Density bound (check 5): warn if concept count < 10 or > 60 for a standard NCERT chapter.

---

## P2 — Embedded Concept Extraction (LLM, Sonnet)

**Purpose**: capture mechanisms, causal accounts, and explanatory principles the chapter *uses* but never names as headline terms (e.g., "electron drift under an applied field" inside the current section).

**Input**: segmented chapter text + the P1 concept list (labels only, to avoid duplication).

**SYSTEM PROMPT:**

> You are analyzing the same chapter a second time. The first pass extracted the concepts the chapter explicitly names — that list is provided. Your task now is to extract **embedded concepts**: mechanisms, causal accounts, and explanatory principles the chapter relies on in its explanations without naming them as formal terms.
>
> Inclusion test: *could the student follow the chapter's explanation without this idea?* If no, it is an embedded concept. If the idea is merely mentioned in passing and the explanation survives without it, exclude it.
>
> For each embedded concept produce the same record structure as the named pass, with these differences:
> - `label`: a short descriptive phrase you compose (the chapter has no name for it)
> - `definition`: grounded strictly in how the chapter uses the idea
> - `passage_refs.definitional`: may be `null` — embedded concepts often have no defining segment; cite the explanatory segment(s) where the idea does its work
>
> Do not re-extract any concept already in the provided named-concept list.

**USER PROMPT:**

> Named concepts already extracted:
>
> [P1 CONCEPT LABELS]
>
> Here is the segmented chapter text:
>
> [SEGMENTED CHAPTER TEXT]
>
> Extract embedded concepts. Produce output as a JSON object with a `concepts` array. Set `extraction_pass` to `"P2"` on each record.

**DO NOT:**
- Duplicate named concepts under a paraphrased label
- Extract pedagogical devices (analogies, mnemonics) as concepts
- Exceed roughly one embedded concept per chapter section unless the text clearly warrants more

**Verification**: gate checks 1–3, 6. Density bound: warn if embedded count > 0.5 × named count.

---

## P3 — Merge & Deduplication (Code + LLM adjudication, Haiku)

**Purpose**: produce the single merged concept inventory all later passes reference. Pure-code dedup cannot reliably match a P2 composed label to a P1 name, so ambiguous cases get one cheap adjudication call.

**Process**:

1. **Code**: exact and normalized label match (case, whitespace, plural/singular). Auto-merge.
2. **Code**: embed all definitions; flag candidate pairs with cosine similarity > 0.80.
3. **LLM (Haiku)**: for each candidate pair, one adjudication call:

   > Two concept records extracted from the same chapter are shown below. Decide whether they describe the same concept. Answer with `same` or `different` and one sentence of reasoning. Records: [RECORD_A] [RECORD_B]

4. **Code**: on merge — keep the P1 record (named label wins), union the `passage_refs`, record the absorbed `concept_id` in `merged_from`.
5. **Code**: log every merge decision (auto and adjudicated, with reasoning) to `merge_log` for P10 review.

**Output**: merged concept inventory. `N` = its size; later density bounds are expressed in terms of `N`.

**Verification**: gate checks 1, 6 on adjudication outputs. All adjudicated merges appear in `qa_review_queue` as warn-level items.


---

## P4 — Typed Relationship Graph (LLM, Sonnet)

**Input**: segmented chapter text + merged concept inventory (labels + definitions).

**SYSTEM PROMPT:**

> You are mapping the relationships this chapter establishes between its concepts. The concept inventory is provided. Use only relationships the chapter itself states or directly demonstrates — not relationships you know from the subject in general.
>
> Three relationship types:
>
> **PREREQUISITE_OF** (directional): understanding A is logically required before B can be understood *as this chapter presents it*. Test: does the chapter's explanation of B use A? Order of appearance in the chapter is evidence, not proof.
>
> **CONNECTS** (non-directional): the chapter establishes a substantive link between A and B. Apply all three tests before emitting:
> 1. The chapter states or demonstrates the link in identifiable passages.
> 2. Reasoning about A and B together yields something reasoning about each alone does not.
> 3. The link is specific to these two concepts — not "everything in a circuit relates to everything else."
>
> **CONTRASTS_WITH** (non-directional): the chapter explicitly differentiates A from B (series vs parallel, conductor vs insulator).
>
> Every edge requires `passage_support`: 1–2 segment IDs where the chapter establishes the relationship.

**USER PROMPT:**

> Concept inventory:
>
> [MERGED CONCEPT LIST — concept_id, label, definition]
>
> Here is the segmented chapter text:
>
> [SEGMENTED CHAPTER TEXT]
>
> Map the relationship graph. Produce output as a JSON object with an `edges` array. Each edge: `from_concept`, `to_concept`, `type`, `passage_support`, `rationale` (one sentence).

**DO NOT:**
- Emit edges supported only by general subject knowledge
- Emit a CONNECTS edge that fails any of the three tests
- Connect a concept to more than 6 others — that is a sign of over-connection, not richness

**Density bounds (parameterized in N, not hardcoded per chapter)**:
- CONNECTS edges: target 0.4–0.6 × N; warn (check 5) above 0.75 × N
- Isolated concepts (no edges at all): warn — usually an extraction or merge problem
- PREREQUISITE_OF cycles: hard fail (check 4 extension) — prerequisite graphs must be acyclic

**Edge IDs (code, post-pass)**: code assigns each edge a deterministic ID,
`edge_<type>_<from_concept>_<to_concept>`, with endpoints in lexicographic order for the
non-directional types (CONNECTS, CONTRASTS_WITH). Same inputs → same IDs. The model never
produces edge IDs. All downstream references — P13 `required_edges`, runtime edge attribution
(§6.2), and coverage projections — resolve against these IDs.

**Verification**: gate checks 1, 2, 4, 5, 6 + acyclicity.

---

## P5 — Evidence Store (Code)

**Purpose**: resolve every citation in P1–P4 outputs into stored text so the runtime never re-parses the source document.

**Process**:

1. For every `passage_refs` entry and `passage_support` entry, resolve the segment ID against the P0 segment index and store the full segment text keyed by `(concept_id | edge_id, segment_id)`.
2. Cap stored passages at 3 per type per concept; if more were cited, keep those the verification gate scored highest on fuzzy containment (check 3).
3. Build the reverse index `segment_id → concepts/edges citing it` (used by the runtime phrase-trigger flow to find which concept a selected phrase belongs to).

**Output**: evidence store + reverse index. This is the only passage source the runtime Stage 1 assembler reads.


---

## P6 — Dimension Audit (LLM, Sonnet — one call per concept)

**Change from draft**: the draft audited all concepts in one call (~40 concepts × 8 dimensions × 4-step
protocol = 320 evaluations in a single response — quality collapses well before that). This spec runs
**one call per concept**: 8 dimension evaluations per call, chapter cost ≈ N calls.

**Input per call**: one concept record (with resolved passages from P5) + the segmented chapter text + the 8 dimension definitions.

**SYSTEM PROMPT:**

> You are auditing what a chapter makes available for one concept across eight dimensions of conceptual engagement. You are measuring the **chapter's text**, not the concept's importance and not what a student could ask — only what the chapter itself provides material for.
>
> The eight dimensions:
>
> - **define**: material stating what the concept is — its essence, boundary, or formal statement
> - **distinguish**: material contrasting it with other concepts, or marking where it ends and another begins
> - **decompose**: material breaking it into components, factors, or structural parts
> - **connect**: material relating it to other concepts in the chapter
> - **delimit**: material on boundary conditions — where it fails, what constrains it, what it does not apply to
> - **predict**: material supporting derivation of consequences — what happens in a scenario
> - **contextualize**: material placing it in a broader system — applications, devices, larger frameworks
> - **vary**: material supporting counterfactual reasoning — what changes if values, conditions, or concepts change
>
> For each dimension, follow this protocol:
>
> 1. **Search**: locate every segment where the chapter provides material for this dimension of this concept.
> 2. **Cite**: list the segment IDs found (empty list if none).
> 3. **Assess**: one sentence describing what the material actually supports.
> 4. **Verdict**: `AVAILABLE` (chapter provides substantive material), `PARTIALLY_AVAILABLE` (material exists but is thin, implicit, or incomplete), or `ABSENT` (no material). If `PARTIALLY_AVAILABLE`, add a `gap_note`: one sentence on what is missing.
>
> Do not compute any scores, counts, or profiles — verdicts and citations only.

**USER PROMPT:**

> Concept under audit:
>
> [CONCEPT RECORD — label, definition, resolved passages]
>
> Here is the segmented chapter text:
>
> [SEGMENTED CHAPTER TEXT]
>
> Audit all eight dimensions. Produce output as a JSON object with an `audit` key: one entry per dimension, each containing `verdict`, `passages` (array of segment IDs), `assessment` (one sentence), and `gap_note` (required if verdict is PARTIALLY_AVAILABLE, otherwise null).

**DO NOT:**
- Judge by what a knowledgeable teacher could supply — only what this chapter contains
- Return AVAILABLE without at least one cited segment
- Let the concept's importance inflate verdicts — a central concept can still have ABSENT dimensions

**Verification**: gate checks 1, 2, 6; plus code rule — `verdict = AVAILABLE` with empty `passages` is a hard fail.

**Storage**: Sections B and C only. Never enters Section A.

---

## P7 — Cross-Concept Productive Pairs (LLM, Sonnet)

**Input**: merged concept inventory + P4 edge list + P6 audit verdicts. Runs after P6.

**SYSTEM PROMPT:**

> You are identifying pairs of concepts in this chapter whose joint consideration is unusually productive for understanding. Most concept pairs are not productive pairs. Emit a pair only if all conditions hold:
>
> 1. The chapter provides material engaging both concepts (verify against the relationship graph and audit provided).
> 2. The pair's connection is non-obvious — not already a single direct edge a student would naturally traverse.
> 3. **Joint inference test**: there is at least one inference that requires reasoning about both concepts *simultaneously* — not decomposable into "first understand A, then understand B."
>
> For each pair produce: `concept_a`, `concept_b`, `relation_chain` (the edges or passages linking them), `relevance_statement` (one sentence, plain language, no framework terminology — this text may reach the student-facing generation context), and `joint_inference_rationale` (one sentence stating the non-decomposable inference).
>
> Do not write questions. Pairs are context for a downstream generator, not test items.

**USER PROMPT:**

> Concept inventory: [MERGED CONCEPT LIST]
>
> Relationship graph: [P4 EDGES]
>
> Dimension audit summary: [P6 VERDICTS — verdicts and citations only, no assessments]
>
> Identify productive pairs. Produce output as a JSON object with a `productive_pairs` array.

**DO NOT:**
- Exceed ceil(N/4) pairs — scarcity is the point
- Use dimension labels or framework terminology in `relevance_statement` (it enters Section A)
- Pair concepts whose only link is co-occurrence in the same section

**Verification**: gate checks 1, 4, 6; density bound (check 5): hard cap at ceil(N/4) pairs — excess pairs are dropped lowest-confidence-first and logged. Code scans `relevance_statement` for the 8 dimension keys and framework terms (`dimension`, `category`, `framework`, `coverage`) — any hit is a hard fail, since this field crosses into Section A.


---

## P8 — Seed Questions (LLM, Sonnet) — NEW, required by PRD Layer 2

**Purpose**: cold-start offer sets for first-visit nodes, and (after human labeling at P10) golden-set
entries for classifier regression testing. The draft pipeline omitted this PRD launch requirement.

**Input**: concepts whose P6 audit shows ≥ 4 non-ABSENT dimensions (richness is computed at P9; this
pass uses the raw verdict counts) + their resolved passages.

**SYSTEM PROMPT:**

> You are writing questions a genuinely curious student might ask while reading this chapter. For the concept provided, write 2–4 questions grounded strictly in the cited passages.
>
> Requirements:
> - Each question must be answerable from the chapter content alone.
> - Questions must feel like natural curiosity, not test items — no "state", "list", "enumerate" phrasing.
> - Vary the angle naturally; do not work through analytical angles in a visible sequence.
> - Cite for each question the segment ID(s) it is grounded in.

**USER PROMPT:**

> Concept: [CONCEPT RECORD — label, definition, resolved passages]
>
> Write 2–4 seed questions. Produce output as a JSON object with a `seed_questions` array: `question_text`, `grounding_segments`.

**DO NOT:**
- Use dimension labels or framework terminology in question text
- Write questions requiring knowledge beyond this chapter
- Target dimensions deliberately — these questions are organic, like runtime generation

**Storage split (critical)**:
- `question_text` + `grounding_segments` → **Section A** (cold-start offer material).
- Dimensional labels are **not produced by this pass**. They are assigned by the human analyst at P10
  and stored in the **golden set / Section C only**. No dimensional label ever attaches to the
  Section A copy.

**Verification**: gate checks 1, 2, 6; same Section A terminology scan as P7.

---

## P9 — Richness Profiles & Chapter Weight Modifiers (Code)

**Purpose**: all derived numbers from the P6 audit. Nothing here involves an LLM.

**Computations**:

1. **Per-concept richness profile**:
   `richness = count(AVAILABLE) + 0.5 × count(PARTIALLY_AVAILABLE)` — range 0.0–8.0.
2. **Chapter availability vector**: for each of the 8 dimensions,
   `availability[d] = (count of concepts with AVAILABLE on d + 0.5 × count PARTIALLY_AVAILABLE) / N`.
3. **Chapter weight modifiers** (consumed per `docs/subject-weighting-specification.md`):
   `modifier[d] = clamp(0.5 + availability[d], 0.5, 1.2)` — initial formula, tunable; the formula and
   its constants are versioned in `pass_versions.P9`.
   `effective_weight[d] = subject_weight[d] × modifier[d]`.
4. **Audit dispersion flags**: concepts with richness < 1.5 are flagged `low_material` for P10
   attention (they will generate poorly and should be candidates for de-emphasis or merge).

**Storage**: Section C. Modifiers are an interpretive lens only — they never enter Section A and never
constrain generation, consistent with `docs/subject-weighting-specification.md`.

---

## P10 — Human QA Gate (Human analyst)

**Purpose**: the draft named "Pass 6 — human analyst framework validation record" without specifying
it. This is that specification. A chapter ships only when this gate records `qa_status = "passed"`.

**Checklist** (all items recorded against the `chapter_analysis_id`):

1. **Concept inventory review**: read the full merged inventory against the chapter. Add missing
   concepts, delete spurious ones, fix definitions. Target: < 10% of records need correction; above
   that, the extraction prompts are re-tuned and the chapter re-run rather than hand-patched.
2. **Merge log review**: confirm or reverse every adjudicated merge from P3.
3. **Dimension audit spot-check**: review ≥ 20% of concept×dimension cells, sampled randomly, **plus
   every item in `qa_review_queue`**. Correct verdicts and citations in place.
4. **Relationship sample**: verify a random sample of ≥ 15 edges against their cited passages.
5. **Seed question labeling**: assign dimensional labels (scores on the 0.0/0.3/0.6/0.9 anchors) to
   every P8 seed question. These labels go to the golden set (`docs/architecture/llm-pipeline.md`
   regression harness) and Section C — never Section A.
6. **Warn resolution**: every warn-level item from the verification gates is resolved or explicitly
   accepted with a note.
7. **Outcome-mapping review**: verify ≥ 5 P13 outcome mappings against the actual item text;
   confirm or reject every `missing_edge_candidate` (accepted candidates become P4 edges and
   trigger the P12 recompute).

**Record**: `analyst_id`, `started_at`, `completed_at`, per-item corrections (old value → new value),
and final `qa_status`. Corrections are applied to the analysis output directly; the pre-correction
output is retained for prompt-tuning analysis.

**Recompute rule**: any correction touching P6 verdicts triggers a P9 recompute (code, cheap).

---

## P11 — Prior Conceptions Backlog (LLM, Sonnet)

**Input**: concepts with P9 richness ≥ 3.0 + segmented chapter text. Runs after P9.

**SYSTEM PROMPT:**

> You are compiling a research backlog of prior conceptions — ideas students commonly hold before instruction that interact with this chapter's concepts. Ground every entry in published education research traditions (e.g., physics education research on current consumption models) or widely documented classroom observation. For each entry produce: `conception` (the idea as a student would hold it), `affected_concepts`, `research_basis` (one sentence), `trigger_spec` ({`match_phrases`, `match_questions`, `negation_suppressors`}), and `status: "UNVALIDATED"`.

**USER PROMPT:**

> Concepts with high material richness: [CONCEPT LIST]
>
> Here is the segmented chapter text: [SEGMENTED CHAPTER TEXT]
>
> Produce the research backlog as a JSON object with a `prior_conceptions` array.

**DO NOT:**
- Mark anything validated — every record is `UNVALIDATED` until a human researcher reviews it
- Invent misconceptions without a research or classroom-observation basis
- Use these records in any generation prompt — Section C only

**Status caveat**: `trigger_spec` is a heuristic research aid for human analysts, not a
production-grade detector. No runtime behavior may key off it in Phases 1–3.

**Verification**: gate checks 1, 4, 6.


---

## 6. Runtime Consumption Contracts

How the runtime layers consume this pipeline's outputs. Full runtime behavior lives in
`docs/architecture/llm-pipeline.md`; this section specifies only the contract with chapter analysis.

### 6.1 Node Summary Compression (Haiku, runs at node-save time)

Draft prompt retained as-is (compress node content to 2–3 sentences, ≤ 80 tokens, third person, no
dimension labels, no added interpretation). Additional requirements:

- Stored summary records `prompt_version` and `model_id`.
- Code scans the summary for the 8 dimension keys and framework terms; a hit discards the summary and
  retries once, then stores a code-side truncation of the node text instead.

### 6.2 Stage 2 Classification (Haiku, async post-selection)

**Changes from draft** (see `docs/architecture/llm-pipeline.md` for the full classifier spec):

1. **Anchor scope reduced.** The draft passed the whole Section B audit. That inflates every call's
   cost and biases scores toward dimensions the chapter happens to make available. Instead pass only:
   the source concept's 8 audit rows + the audit rows of ≤ 2 directly connected concepts (when the
   question references them). With this caution appended to the anchor block:

   > These audit rows show how the dimensions appear in this chapter's language. They are calibration
   > examples only — a question may score on any dimension regardless of what the chapter makes
   > available.

2. **Model outputs scores only.** Discrete scale per dimension: {0.0, 0.3, 0.6, 0.9}. The model does
   **not** compute entropy, confidence, or review flags. Code computes Shannon entropy over the
   normalized score vector and applies thresholds (snap < 0.5, review > 2.8).
3. **Median-of-3.** Three classification runs per question (temperature 0); code takes the
   per-dimension median and logs per-dimension dispersion. Max-dispersion > 0.3 on any dimension →
   `needs_review`.
4. **Structured output mandatory**; `unclassifiable` flag retained from the draft (all-zero vectors
   must be flagged, never silently stored).
5. Classification records carry `chapter_analysis_id` and classifier `prompt_version`.
6. **Concept attribution (topology layer).** The same call additionally outputs
   `engaged_concepts` (0–2 secondary concept IDs from the merged inventory) and
   `relation_engaged` (boolean: does the question reason about the relationship itself, or merely
   mention both concepts?). Code — never the model — resolves (source, secondary) pairs against
   the P4 edge IDs; attribution is taken by majority vote across the 3 runs, and disagreement on
   `relation_engaged` resolves to `false`. Unselected offer-set options are classified in a
   nightly batch queue (lowest priority — they gate nothing in-session). Quiz-generated questions
   ("Quiz Me") pass through the same attribution contract — this is what makes the topology layer
   falsifiable: it enables the validation query *do students who traversed edge E outperform those
   who didn't, on quiz items whose attribution requires E?* Full contract:
   `docs/chapter-topology-specification.md` §4.1.

The draft's "classify by intent, not by keyword" instruction is retained verbatim — it is correct and
important.

### 6.3 Stage 1 Generation (Sonnet, student-facing)

**Retained from draft (good engineering, unchanged)**:

- Token budget 1,500 with explicit truncation order: (1) drop productive pairs → (2) reduce connected
  concepts to 3 → (3) truncate session history to 1 node summary → (4) never drop current concept
  definition or direct relationships.
- Assembler reads Section A only — no file path, key, or variable referencing Sections B/C.
- Positive-only, category-invisible exploration summary (max 3 sentences).
- Pairs are context, not instructions; no engineered bridge questions; no visible analytical-angle
  templates.

**Changed: the banned-word list.** The draft banned the words "define, distinguish, decompose,
connect, delimit, predict, contextualize, vary, dimension, framework, category, coverage" outright.
Banning ordinary verbs harms generation — "What would you predict happens if…" is natural student
English, not framework leakage. The philosophy documents prohibit exposing *labels, axes, and
counts*, not vocabulary. Replacement DO-NOT block:

> **DO NOT:**
> - Reference the analytic framework in any form: never mention dimensions, categories, engagement
>   axes, coverage, or that questions are being classified or tracked
> - Enumerate analytical angles ("let's look at this from the definition side… now the prediction
>   side…") or follow a visible template where each question targets a different angle in sequence
> - Generate questions requiring knowledge beyond this chapter
> - Engineer bridge questions as a deliberate category
>
> Ordinary conversational use of words like "predict", "compare", "connect", or "define" is allowed —
> these are normal English, and stilted avoidance of them is itself a detectable template.

**Logging**: every offer set records `chapter_analysis_id`, generation `prompt_version`, and the
policy fields required by `docs/measurement-and-experimentation.md` (offer-set contents,
propensities, policy version).

---

## Appendix A — Changes from the draft prompt pipeline

| Draft | This spec | Change and reason |
|-------|-----------|-------------------|
| — | P0 | **Added.** Draft cited `[chapter_id_segment_type_number]` IDs with no pass producing them; citations were unverifiable. |
| Pass 1A | P1 | Subject/curriculum parameterized; `category_tag` enum moved to per-subject config (draft hardcoded `circuit_concept` etc.); citation-existence rule added. |
| Pass 1B | P2 | Inclusion test retained; P1 labels passed in to prevent duplicates; density bound added. |
| Merge step | P3 | Draft was pure code; semantic dedup of unnamed P2 concepts needs embedding candidates + Haiku adjudication; merge log added for QA. |
| Pass 2 | P4 | Density parameterized in N (draft hardcoded "15–25 edges for 35–45 concepts"); acyclicity check on PREREQUISITE_OF added. |
| Pass 3 | P5 | Unchanged in substance; reverse index added for phrase-trigger resolution. |
| Pass 5 | P6 | **Split to one call per concept** (draft: ~320 evaluations in one call). Explicit per-dimension output contract; richness arithmetic removed from the model. |
| Pass 4 | P7 | Joint inference test retained; cap parameterized at ceil(N/4); Section A terminology scan added on `relevance_statement`. |
| — | P8 | **Added.** Seed questions are a PRD Layer 2 launch requirement the draft omitted; doubles as golden-set source. |
| — | P9 | **Added.** Richness and weight-modifier arithmetic moved out of LLM passes into code; modifier formula versioned. |
| Pass 6 | P10 | Draft named the human gate but never specified it; concrete checklist, correction recording, and recompute rule added. |
| Pass 7 | P11 | Retained; input now defined precisely (P9 richness ≥ 3.0); `trigger_spec` explicitly demoted to heuristic research aid. |
| Stage 2 runtime | §6.2 | Entropy/confidence moved to code; anchor scope cut from whole Section B to source-concept rows; discrete scale + median-of-3 added. |
| Stage 1 runtime | §6.3 | Banned-word list replaced with meta-language prohibition; version logging added. Token budget and truncation order kept verbatim. |
| P0 | `location` field | **Added** (topology spec): `question` segments record `in_text` vs `end_of_chapter` so P13 can treat outcome items as the authority's specification. |
| P4 | Edge IDs | **Added** (topology spec): deterministic code-assigned edge IDs; P13, runtime attribution, and coverage projections need durable edge references. |
| — | P12 | **Added** (topology spec): exposition order, emphasis weights, edge criticality — code only, Section C. |
| — | P13 | **Added** (topology spec): outcome-to-subgraph mapping; `missing_edge_candidates` doubles as a P4 recall check. |
| P10 | Checklist item 7 | **Added** (topology spec): outcome-mapping verification and missing-edge adjudication. |
| Stage 2 runtime | §6.2 item 6 | **Added** (topology spec): `engaged_concepts` + `relation_engaged` attribution; nightly batch classification of unselected offers. |
