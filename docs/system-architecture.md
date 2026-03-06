# System Architecture: Categorical Exploration Learning Platform

## Design Principles

### Core Philosophy

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     FUNDAMENTAL DESIGN PRINCIPLES                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. ORGANIC-FIRST GENERATION                                           │
│     Questions emerge naturally from context, never from categorical    │
│     templates. The LLM generates what a curious learner would ask.     │
│                                                                         │
│  2. POST-HOC CLASSIFICATION                                            │
│     Categories are applied AFTER generation for diagnosis, because     │
│     they represent principled diagnostic dimensions for engaging       │
│     concepts. Classification reveals which diagnostic dimensions of    │
│     the concept the student has engaged with through question-based    │
│     exploration. Diagnostic significance of any gap depends on how     │
│     structurally available that dimension is in the concept—as         │
│     encoded by subject weights. Categories are invisible to students   │
│     throughout the experience.                                         │
│                                                                         │
│  3. CHAPTER-BOUNDED SCOPE                                              │
│     Learning sessions focus on single chapters. All concepts, nodes,   │
│     and questions relate to the current chapter's learning objectives. │
│                                                                         │
│  4. SUBJECT-WEIGHTED DIAGNOSIS                                         │
│     Different subjects systematically produce concepts with different  │
│     structural profiles. Weights encode which dimensions are more      │
│     prominently and meaningfully available in a subject's              │
│     characteristic concept types, not merely which dimensions          │
│     teachers prefer to assess. Diagnostic analysis applies these      │
│     discipline-specific weights.                                       │
│                                                                         │
│  5. TEACHER AS MKO                                                     │
│     System surfaces gaps; teachers provide scaffolding as the          │
│     "More Knowledgeable Other" per Vygotsky's ZPD framework.          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## System Components

### Component Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        SYSTEM ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                   STUDENT EXPERIENCE LAYER                       │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │   │
│  │  │ Mind Map │  │ Question │  │ Content  │  │  Quiz    │        │   │
│  │  │Navigation│  │ Selection│  │ Display  │  │Checkpoint│        │   │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │   │
│  └───────┼─────────────┼─────────────┼─────────────┼───────────────┘   │
│          │             │             │             │                    │
│          ▼             ▼             ▼             ▼                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                   DATA COLLECTION LAYER                          │   │
│  │  Mind Map Behavior │ Question Selection │ Engagement │ Quiz     │   │
│  └──────────────────────────────┬──────────────────────────────────┘   │
│                                 │                                       │
│                                 ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                   LLM PROCESSING LAYER (Direct API)              │   │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐     │   │
│  │  │    Organic     │  │   Post-Hoc     │  │   Secondary    │     │   │
│  │  │   Question     │→ │  Categorical   │→ │  Enhancement   │     │   │
│  │  │  Generation    │  │ Classification │  │    Layers      │     │   │
│  │  └────────────────┘  └────────────────┘  └────────────────┘     │   │
│  └──────────────────────────────┬──────────────────────────────────┘   │
│                                 │                                       │
│                                 ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                   ANALYSIS LAYER                                 │   │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐     │   │
│  │  │  Question      │  │   Coverage     │  │  Subject       │     │   │
│  │  │    Bank        │  │    Engine      │  │  Weighting     │     │   │
│  │  └────────────────┘  └────────────────┘  └────────────────┘     │   │
│  └──────────────────────────────┬──────────────────────────────────┘   │
│                                 │                                       │
│                                 ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                   OUTPUT LAYER                                   │   │
│  │  ┌──────────────────────┐  ┌──────────────────────────────┐     │   │
│  │  │  Student Feedback    │  │  Teacher Dashboard           │     │   │
│  │  │  • Assessment results│  │  • Individual profiles       │     │   │
│  │  │  • Suggested Qs      │  │  • Class-level concerns      │     │   │
│  │  │    (category-neutral)│  │  • Avoided questions         │     │   │
│  │  └──────────────────────┘  └──────────────────────────────┘     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Processing Pipeline

### Stage 1: Organic Question Generation

**Principle**: Questions must feel natural, not formulaic. No categorical structure imposed.

**Input Context**:
- Current chapter content and learning objectives
- Content consumed so far in session
- Mind map nodes currently connected
- Specific node from which student is exploring
- Student's exploration history within chapter
- (Optional) **Phrase anchor** selected by the learner (selected phrase + local excerpt)

**LLM Prompt Strategy**:
```
Generate questions that a curious student would naturally ask at this 
point in their exploration of [chapter topic].

Context:
- Student is currently exploring: [current node]
- Previously explored: [connected nodes]
- Content consumed: [summary of consumed content]
- (Optional) Phrase anchor: [selected phrase] in excerpt: [local excerpt]

Generate 4-6 questions that:
- Emerge organically from the current context
- Reflect genuine curiosity about the topic
- Vary in focus and approach naturally
- Feel like questions a thoughtful student would ask

Do NOT:
- Use formulaic question patterns
- Force artificial variety
- Reference any categorical framework
- Optimize for diagnostic category coverage (no "cover all 8" / "hit each dimension" objectives)
```

**Output**: Natural, contextually-relevant questions with no categorical tagging.

#### Stage 1A (MVP entry point): Phrase-anchored exploration

Phrase selection is treated as a **learner-chosen anchor** that conditions both:
1) a direct elaboration/explanation response, and
2) a small offer set of recommended follow-up questions.

**Thread context packet (conceptual, bounded)**:
- `selected_phrase`
- `source_node_id`
- `source_excerpt` (local window around phrase)
- `parent_node_summary` (short, stored summary)
- `neighborhood_summaries` (recent/connected nodes, capped)
- `chapter_context` (subject/chapter/grade/exam)

This packet (or a hash/reference to it) must be persisted on the resulting child node so subsequent generation stays **thread-aware**, not only chapter-aware.

---

### Stage 2: Post-Hoc Categorical Classification

**Principle**: Classification happens invisibly, after generation, for diagnostic purposes only.

**Classification Process**:
```
Generated Question → Classification Model → Category Assignment → Question Bank
```

**Classification Prompt**:
```
Score this question on how strongly it engages each diagnostic dimension of conceptual engagement.

Question: "[generated question]"
Concept: [chapter concept]
Subject: [academic subject]

Dimensions:
1. Define - Explores what the concept IS (essence, definition)
2. Distinguish - Explores what the concept is NOT (boundaries, differences)
3. Decompose - Explores constituent parts (structure, components)
4. Connect - Explores relationships to other concepts
5. Delimit - Explores constraints, limitations, failure conditions
6. Predict - Explores effects, consequences, causation
7. Contextualize - Explores placement in larger frameworks
8. Vary - Explores alternatives, possibilities, variations

Score each dimension independently from 0.0 to 1.0:
  0.0 = dimension not present in this question
  0.3 = tangentially engaged
  0.6 = meaningfully engaged
  0.9 = centrally engaged

Scores are INDEPENDENT — they do not need to sum to 1.
A question can score high on multiple dimensions simultaneously.

Output format:
{
  "scores": {
    "define": 0.0,
    "distinguish": 0.0,
    "decompose": 0.0,
    "connect": 0.0,
    "delimit": 0.0,
    "predict": 0.0,
    "contextualize": 0.0,
    "vary": 0.0
  }
}
```

**Classification Quality Signal: Dimensional Entropy**

After classification, compute the Shannon entropy of the score vector to detect suspicious outputs:

```
H = -Σ (p_d * log2(p_d))  where p_d = score_d / Σ scores
```

- **Low entropy** (H < 1.5): scores are concentrated — one or two dimensions dominate. This is the expected case for most questions and indicates a confident classification.
- **High entropy** (H > 2.8): scores are spread nearly uniformly — the classifier is "hedging" and hasn't committed to a meaningful profile. Flag for review.
- **Near-zero entropy** (H < 0.3): only one dimension has a non-zero score. Expected for simple definitional questions; suspicious if the question text appears multi-dimensional.

Entropy is computed automatically and stored alongside scores. It requires no additional LLM call.

---

### Stage 3: Secondary Enhancement (Conditional)

**Principle**: Applied only when demonstrably beneficial, not as default processing.

**Enhancement Types**:

| Enhancement | When Applied | Purpose |
|-------------|--------------|---------|
| Semantic Tracking | Always (passive) | Analyze conceptual relationships |
| Contextual Framing | When understanding level detected | Adjust complexity to student |
| Linguistic Framing | When clarity issues detected | Improve question phrasing |

**Decision Logic**:
```python
def should_enhance(question, student_context):
    enhancements = []
    
    # Semantic tracking always runs (passive analysis)
    enhancements.append("semantic")
    
    # Contextual framing if understanding level mismatch detected
    if student_context.understanding_level != question.complexity_level:
        enhancements.append("contextual")
    
    # Linguistic framing if clarity score below threshold
    if question.clarity_score < CLARITY_THRESHOLD:
        enhancements.append("linguistic")
    
    return enhancements
```

---

## Data Collection & Pattern Analysis

**See `docs/architecture/data-collection.md` for complete specification** of:
- Mind map behavioral data collection
- Question selection data
- Phrase selection data
- Quiz performance data
- Learning path capture requirements
- Statistical pattern analysis implementation

---


---


## Multimedia content integration (image/video nodes)

Multimedia must be represented in a way that supports:
1) rendering in the mind map, and
2) safe, text-based **LLM context** (since most LLM prompts remain text-first).

### Media asset model (conceptual)
- `media_asset_id`
- `media_type`: `video` | `image`
- `source`: `youtube` | `web` | `user_upload`
- `source_ref`: e.g., YouTube video ID / URL
- `storage_url` (for uploaded images) + optional `cdn_url`
- `title`, `author/channel`, `duration_seconds` (video)
- `created_at`, `added_by_user_id`

### Derived text for LLM context (adapters)
To include multimedia in question generation (Stage 1) without passing raw pixels, create a compact **media context packet**:
- **Video**: transcript/captions (if available) — excerpt + summary + key terms
- **Image**: caption + OCR-extracted text (if available) + short description

If a vision-capable model is used later, these derived fields still act as the **default safe fallback** and as searchable metadata.

These derived fields are what get injected into prompts as:
`content_consumed` / `media_context` (with length limits and redaction).

### Storage and delivery requirements
- **Images**: object storage (S3/Supabase Storage/etc.) + CDN; store original + optional resized variants.
- **Videos**: store references (YouTube ID/URL) and derived transcript/summary; stream via platform player.
- **Offline mode**: cache media metadata and derived text; optionally cache downloaded audio/video where permitted.

---

## Handwritten answer submission & analysis (pipeline)

This pipeline turns a photographed handwritten solution into actionable feedback and diagnostic signals.

### End-to-end flow
1. **Capture/upload**: student photographs handwritten work and attaches it to a `question_attempt_id` (and optionally `node_id`).
2. **Pre-processing**: crop/deskew/contrast; optionally detect regions (question vs working vs final answer).
3. **Handwriting OCR**: call a handwriting/STEM-capable OCR provider (e.g., Mathpix, MyScript, Google Document AI, or Datalab's Chandra OCR: https://www.datalab.to/blog/introducing-chandra) to extract:
   - plain text,
   - math as LaTeX/MathML (when relevant),
   - structured steps/lines (when possible),
   - confidence scores per region.
4. **Student verification step (recommended)**: show the extracted result and allow quick edits when OCR confidence is low.
5. **AI analysis**: compare extracted work to the expected solution/rubric (or model solution) and generate:
   - correctness (final answer + key steps),
   - misconception tags / error type (conceptual vs algebraic vs unit error),
   - next-step hint(s) and targeted follow-up prompts.
6. **Feedback delivery**: present concise feedback to student; optionally generate a "worked example".
7. **Diagnostic integration**: write back signals for teacher/admin analytics and longitudinal profiling.

### Contextual OCR hints
OCR requests should include contextual hints to improve accuracy:
- subject/grade, question type (numerical/proof/diagram), expected units/symbols,
- allowed notation (e.g., calculus, vectors), and language.

### Logging & safety
- Store the original image securely; treat it as sensitive user data.
- Persist OCR outputs + confidence; if confidence is low, downstream diagnostics must down-weight these signals.
- Emit events for: upload, OCR completed, student-edited OCR, analysis completed, feedback shown.

## Question Bank Architecture

### Schema

```json
{
  "question_id": "q_uuid",
  "text": "What happens when photosynthesis cannot occur?",
  "chapter_id": "ch_biology_101_photosynthesis",
  "concept_id": "photosynthesis",
  "subject": "biology",
  "note_on_subject_field": "Subject must be one of: mathematics, physics, chemistry, biology, history, literature, economics, psychology, sociology. Use specific sciences (physics/chemistry/biology) not generic 'sciences'.",
  "classification": {
    "dimensional_scores": {
      "define": 0.0,
      "distinguish": 0.1,
      "decompose": 0.0,
      "connect": 0.0,
      "delimit": 0.9,
      "predict": 0.6,
      "contextualize": 0.0,
      "vary": 0.0
    },
    "entropy": 1.22,
    "is_classified": true,
    "needs_review": false,
    "classified_at": "2025-01-15T10:30:00Z",
    "note": "dimensional_scores is the 8-dimensional engagement vector (0.0–1.0 per dimension, independent scores). entropy is the Shannon entropy of the normalised score vector — low entropy (<1.5) indicates confident classification; high entropy (>2.8) flags hedging and triggers review."
  },
  "generation_context": {
    "current_node": "limiting_factors",
    "connected_nodes": ["chloroplast", "light_reactions"],
    "content_consumed": ["intro_photosynthesis", "light_dependent_reactions"],
    "session_id": "session_uuid"
  },
  "selection_metrics": {
    "times_presented": 47,
    "times_selected": 4,
    "selection_rate": 0.085,
    "avg_selection_position": 2.3
  },
  "outcome_metrics": {
    "led_to_quiz_success": 3,
    "led_to_quiz_failure": 1,
    "success_rate": 0.75
  },
  "created_at": "2025-01-15T10:30:00Z"
}
```

### Cumulative Intelligence

The question bank enables:

1. **Avoided Question Detection**: Questions with low selection rates across class
2. **Effective Question Identification**: Questions leading to quiz success
3. **Dimensional Balance Analysis**: Which dimensions are over/under-represented in cumulative profiles
4. **Cross-Concept Patterns**: Systematic avoidance patterns across chapters

---

## Diagnostic Engine

Weighted coverage gaps are treated as diagnostically significant indicators of possible gaps in conceptual understanding—specifically, in dimensions that are meaningfully available and significant in the concept being studied. The framework hypothesizes that breadth of engagement matters for understanding: a student who has engaged with multiple diagnostically relevant dimensions of a concept may hold a more robust understanding than one who has gone deep in only one. This is a hypothesis under empirical validation, not a settled assumption.

### Individual Student Coverage Calculation

```python
DIMENSIONS = ["define", "distinguish", "decompose", "connect",
              "delimit", "predict", "contextualize", "vary"]

def calculate_student_coverage(student_id, chapter_id, subject):
    """
    Calculate weighted dimensional coverage for a student's chapter exploration.
    Each selected question contributes its full 8-dimensional engagement vector.
    Coverage is the normalised cumulative score: Σ scores[d] / N per dimension.
    """
    # Get all questions selected by student for this chapter
    selected_questions = get_selected_questions(student_id, chapter_id)

    # Get subject-specific weights
    weights = get_subject_weights(subject)

    # Cumulative state: running sum of dimensional vectors
    cumulative = {d: 0.0 for d in DIMENSIONS}
    n_classified = 0

    for question in selected_questions:
        if not question.classification.is_classified:
            continue
        # Skip hedged classifications (high entropy = classifier unsure)
        if question.classification.entropy > 2.8:
            continue

        scores = question.classification.dimensional_scores
        for d in DIMENSIONS:
            cumulative[d] += scores[d]
        n_classified += 1

    # Normalised cumulative score (0.0–1.0 range per dimension)
    if n_classified > 0:
        normalised = {d: cumulative[d] / n_classified for d in DIMENSIONS}
    else:
        normalised = {d: 0.0 for d in DIMENSIONS}

    # Apply subject weights (see docs/subject-weighting-specification.md)
    weighted_coverage = apply_weights(normalised, weights)

    # Identify gaps using normalised scores and weights
    gaps = identify_gaps(normalised, weights)

    return {
        "raw_coverage": normalised,
        "weighted_coverage": weighted_coverage,
        "cumulative_state": cumulative,
        "questions_counted": n_classified,
        "critical_gaps": gaps["critical"],
        "moderate_gaps": gaps["moderate"],
        "strengths": gaps["strengths"]
    }
```

### Class-Level Concern Analysis

```python
def analyze_class_gaps(class_id, chapter_id, subject):
    """
    Identify questions generated but consistently avoided across class.
    """
    # Get all questions generated for this chapter
    all_questions = get_chapter_questions(chapter_id)

    # Filter to questions presented to multiple students
    widely_presented = [q for q in all_questions if q.times_presented >= 10]

    # Identify low-selection questions
    avoided_questions = [
        q for q in widely_presented
        if q.selection_rate < AVOIDANCE_THRESHOLD  # e.g., 0.15
    ]

    # Group by category
    avoided_by_dimension = group_by_dominant_dimension(avoided_questions)

    # Generate teacher recommendations
    recommendations = generate_mko_recommendations(avoided_by_dimension, subject)

    return {
        "avoided_questions": avoided_questions,
        "category_gaps": avoided_by_category,
        "recommendations": recommendations
    }
```

---

## Teacher Dashboard Specification

### Individual Student View

```
┌─────────────────────────────────────────────────────────────────────────┐
│  STUDENT: Alex Chen  │  CHAPTER: Photosynthesis  │  SUBJECT: Biology   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  CATEGORICAL COVERAGE (Biology-weighted)                               │
│  ────────────────────────────────────────                              │
│  Define        [████████████████░░░░] 80%                              │
│  Distinguish   [████████░░░░░░░░░░░░] 40%                              │
│  Decompose     [████████████████░░░░] 80%  ★ HIGH PRIORITY             │
│  Connect       [████████████████░░░░] 80%  ★ HIGH PRIORITY             │
│  Delimit       [████░░░░░░░░░░░░░░░░] 20%  ★ HIGH PRIORITY  ⚠ SIGNIFICANT    │
│  Predict       [████████░░░░░░░░░░░░] 40%  ★ HIGH PRIORITY  ⚠ FOLLOW-UP│
│  Contextualize [████████░░░░░░░░░░░░] 40%                              │
│  Vary          [████░░░░░░░░░░░░░░░░] 20%                              │
│                                                                         │
│  WEIGHTED SCORE: 58%                                                   │
│                                                                         │
│  RECOMMENDED FOLLOW-UPS                                                │
│  ──────────────────────                                                │
│  1. Predict: Limited exploration detected in causal                    │
│     consequences                                                       │
│     → "What would happen to a plant if chlorophyll stopped working?"   │
│                                                                         │
│  2. Delimit: Significant gap detected in failure                       │
│     conditions                                                         │
│     → "Under what conditions does photosynthesis fail or slow down?"   │
│                                                                         │
│  EXPLORATION PATTERNS                                                  │
│  ───────────────────                                                   │
│  Entry point: Define (typical for this student)                        │
│  Time on chapter: 34 minutes                                           │
│  Questions selected: 12 of 28 presented                                │
│  Quiz performance: 7/10 correct                                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Class Overview View

```
┌─────────────────────────────────────────────────────────────────────────┐
│  CLASS: Biology 101  │  CHAPTER: Photosynthesis  │  28 Students        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  CLASS DIMENSIONAL COVERAGE (normalised cumulative scores)             │
│  ──────────────────────────                                            │
│  Define        [████████████████████] 92%  ✓ Strong                    │
│  Distinguish   [████████████░░░░░░░░] 61%                              │
│  Decompose     [████████████████░░░░] 78%  ✓ Strong                    │
│  Connect       [████████████████░░░░] 81%  ✓ Strong                    │
│  Delimit       [████░░░░░░░░░░░░░░░░] 23%  ⚠ CLASS-LEVEL CONCERN       │
│  Predict       [████████░░░░░░░░░░░░] 45%  ⚠ CLASS-LEVEL CONCERN       │
│  Contextualize [████████████░░░░░░░░] 58%                              │
│  Vary          [██████░░░░░░░░░░░░░░] 31%  ⚠ CLASS-LEVEL CONCERN       │
│                                                                         │
│  COMMONLY AVOIDED QUESTIONS (for whole-class instruction)             │
│  ─────────────────────────────────────────────────────────             │
│  Dimension: Delimit (8% selection rate)                                │
│  • "What happens when a plant can't get enough CO2?"                   │
│  • "Under what conditions does photosynthesis completely stop?"        │
│                                                                         │
│  Dimension: Vary (12% selection rate)                                  │
│  • "Could plants evolve to use a different energy source?"             │
│  • "Why don't all organisms use photosynthesis?"                       │
│                                                                         │
│  RECOMMENDED CLASS INTERVENTION                                        │
│  ─────────────────────────────                                         │
│  Focus next lesson on: Limiting factors and alternatives               │
│  Discussion prompts:                                                   │
│  → "What are the breaking points for photosynthesis?"                  │
│  → "Why did evolution produce photosynthesis instead of alternatives?" │
│                                                                         │
│  STUDENT DISTRIBUTION                                                  │
│  ────────────────────                                                  │
│  Strong coverage (>70%): 8 students                                    │
│  Moderate coverage (40-70%): 14 students                               │
│  Needs support (<40%): 6 students  [View list]                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```


## Quiz System

Trigger mechanisms and adaptive logic are **yet to be designed/specified** and will be defined in a future document.

**Category invisibility**: if/when quizzes exist, student-facing quiz UX and results remain category-neutral (no category names, axis labels, or “X/8 dimensions” language). Category-level diagnostics remain teacher/admin-facing.

---

## LLM Pipeline Architecture

**See `docs/architecture/llm-pipeline.md` for complete specification** of:
- Two-stage pipeline design (Sonnet for generation, Haiku for classification)
- Direct API implementation (no LangChain)
- Organic question generation prompts
- Post-hoc classification system
- Optional structured output validation

---


## Collective Intelligence Layer

### Overview

The system learns from aggregate student behavior to improve experiences for future students while preserving organic exploration.

**Key Technical Principle**: The Collective Intelligence Layer uses **statistical pattern recognition**, not machine learning. All pattern detection is accomplished through:
- Database aggregation queries (frequency counting, sequence analysis)
- Statistical correlation methods (Pearson/Spearman coefficients)
- Rule-based thresholds with configurable parameters

No ML model training is required for Phases 1-3.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    COLLECTIVE INTELLIGENCE FLOW                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Many Students Explore Chapter                                         │
│           │                                                             │
│           ▼                                                             │
│  Question Selection Patterns Accumulate                                │
│           │                                                             │
│           ▼                                                             │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │              PATTERN ANALYSIS ENGINE (Statistical)               │   │
│  │  • Question paths: Sequence frequency counting (SQL/NoSQL)      │   │
│  │  • Success correlation: Pearson/Spearman coefficients           │   │
│  │  • Avoidance patterns: Selection rate aggregation               │   │
│  │  • Bridge questions: Category transition analysis               │   │
│  │  • NO ML model training required                                │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│           │                                                             │
│           ▼                                                             │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐                   │
│  │  STUDENT   │    │  TEACHER   │    │  CONTENT   │                   │
│  │ SUGGESTIONS│    │  INSIGHTS  │    │   CACHE    │                   │
│  └────────────┘    └────────────┘    └────────────┘                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Feature 1: Question Path Pattern Analysis

**Purpose**: Learn from collective exploration to improve suggestions for new students.

**Implementation**: Database aggregation queries—no ML training required.

**Pattern Data Structure**:
```json
{
  "question_path_patterns": {
    "chapter_id": "ch_biology_photosynthesis",
    "patterns": [
      {
        "path_id": "path_001",
        "sequence": ["q_define_basic", "q_decompose_chloroplast", "q_connect_energy"],
        "frequency": 847,
        "avg_quiz_score": 0.82,
        "cumulative_profile_at_end": {
          "define": 0.75, "distinguish": 0.1, "decompose": 0.7, "connect": 0.65,
          "delimit": 0.05, "predict": 0.2, "contextualize": 0.15, "vary": 0.0
        },
        "success_rating": "high_engagement_partial_coverage"
      }
    ],
    "bridge_questions": [
      {
        "question_id": "q_delimit_conditions",
        "dimensional_profile": {
          "define": 0.1, "distinguish": 0.2, "decompose": 0.0, "connect": 0.0,
          "delimit": 0.9, "predict": 0.6, "contextualize": 0.0, "vary": 0.1
        },
        "effective_when_cumulative_state": {
          "high_dimensions": ["define", "decompose"],
          "low_dimensions": ["delimit", "predict"]
        },
        "success_rate_when_bridging": 0.76,
        "note": "Bridge effectiveness is computed from aggregate data: given students whose cumulative state has high scores in high_dimensions and low scores in low_dimensions, how often does selecting this question lead to subsequent engagement with the low dimensions? This is a transition probability computed via database aggregation."
      }
    ]
  }
}
```

**Application Logic**:
```python
def suggest_questions_for_new_student(student_session, chapter_id):
    # Generate organic questions (always primary)
    organic_questions = generate_organic_questions(student_session)

    if has_sufficient_pattern_data(chapter_id):
        # Find successful path continuations
        continuations = find_path_continuations(current_path, chapter_id)

        # Find bridge questions whose dimensional profile fills gaps
        # in the student's current cumulative state
        bridges = find_bridge_questions(student_session.cumulative_state, chapter_id)

        # Blend: organic 70%, collective 30%
        return blend_suggestions(organic_questions, continuations, bridges)

    return organic_questions
```

### Feature 2: Teacher Insights from Selection Patterns

**Purpose**: Transform aggregate selection data into actionable teaching intelligence.

**Implementation**: Selection rate aggregation and category accessibility ranking—pure database queries.

**Analytics Structure**:
```json
{
  "chapter_selection_analytics": {
    "high_appeal_questions": [...],
    "systematic_avoidance": [...],
    "entry_point_analysis": {...},
    "category_accessibility_ranking": [...],
    "teaching_recommendations": {
      "let_students_explore_independently": ["define", "connect"],
      "provide_light_scaffolding": ["predict", "contextualize"],
      "requires_direct_teaching": ["delimit", "vary"]
    }
  }
}
```

### Feature 3: Content Caching Strategy

**Purpose**: Optimize performance by pre-generating content for common paths.

**Important clarification (terminology)**:
- **Content Library** = persistent, promoted, versioned pre-generated content derived from statistically significant aggregate usage.
- **Cache** = fast serving layer (e.g., Redis) for recently-used library items and hot results.

See: `docs/content-library-specification.md` for the full serving + write-time lifecycle (exact match → prefix match → hybrid → LLM fallback), maturity phases, and promotion rules.

**Implementation**: Threshold-based caching rules—no ML prediction models.

**Caching Policy**:
```python
class ContentCacheManager:
    MIN_SEQUENCE_FREQUENCY = 50      # Reliable pattern threshold
    MIN_PROBABILITY_THRESHOLD = 0.40  # Likely followup threshold
    CACHE_TTL_DAYS = 30              # Freshness window
    ORGANIC_GENERATION_FLOOR = 0.30   # Always 30% fresh
    VARIATION_INJECTION_RATE = 0.15   # 15% get variations
```

**Safeguards Against Rigidity**:
- Organic generation floor (30% always fresh)
- Variation injection into cached content (15%)
- Cache only high-frequency, high-success sequences
- Regular cache refresh to incorporate new patterns
- Minimum path diversity requirement before caching

---

## Data Thresholds

| Metric | Threshold | Rationale |
|--------|-----------|-----------|
| Minimum students for pattern analysis | 50 | Statistical significance |
| Minimum sequence frequency for caching | 50 | Reliable pattern |
| Minimum probability for followup caching | 0.40 | Likely enough to justify cache |
| Minimum quiz success rate for "successful path" | 0.70 | Indicates understanding |
| Cache TTL | 30 days | Balance freshness vs. efficiency |
| Organic generation floor | 30% | Preserve diversity |

---

---


## Technical Stack

### Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         TECHNICAL STACK                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  LLM LAYER                                                              │
│  ─────────                                                              │
│  • Direct API calls (Anthropic Claude / OpenAI GPT-4)                  │
│  • Custom async pipeline orchestration                                  │
│  • Optional: Instructor library for structured output validation       │
│  • NO LangChain or heavyweight frameworks                              │
│                                                                         │
│  PATTERN ANALYSIS LAYER                                                │
│  ─────────────────────                                                 │
│  • Database aggregation queries (PostgreSQL window functions)          │
│  • Statistical analysis (scipy for correlations)                       │
│  • Rule-based thresholds (configurable parameters)                     │
│  • LLM-assisted analysis (inference, not training)                     │
│  • NO ML model training required for Phases 1-3                        │
│                                                                         │
│  DATA LAYER                                                            │
│  ──────────                                                            │
│  • PostgreSQL (Supabase): Question bank, student sessions, analytics  │
│  • Redis: Content caching, session state, real-time data              │
│  • Time-series storage: Exploration patterns, behavioral sequences    │
│                                                                         │
│  APPLICATION LAYER                                                     │
│  ─────────────────                                                     │
│  • Python backend (FastAPI)                                            │
│  • React Native frontend (Hybrid Views + Skia Edges + Zustand)        │
│  • Supabase Realtime: Mind map sync                                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Layer Specifications

#### LLM Layer

| Component | Specification |
|-----------|--------------|
| Provider | Anthropic Claude (primary) / OpenAI GPT-4 (fallback) |
| Integration | Direct API calls with async/await |
| Orchestration | Custom Python pipeline (no framework) |
| Structured outputs | Optional Instructor library for Pydantic validation |
| Rate limiting | Custom implementation with exponential backoff |
| Cost management | Token counting, caching, request batching |

#### Pattern Analysis Layer

| Component | Specification |
|-----------|--------------|
| Path analysis | PostgreSQL window functions |
| Correlation | scipy.stats (Pearson, Spearman) |
| Thresholds | Configurable via environment/database |
| Success factors | LLM inference (not ML training) |
| ML (optional) | Only Phase 4+ if statistical approaches insufficient |

#### Data Layer

| Store | Purpose | Technology |
|-------|---------|------------|
| Primary database | Question bank, sessions, user data | PostgreSQL (Supabase) |
| Cache | Content cache, session state | Redis |
| Analytics | Aggregated patterns, dashboards | PostgreSQL (same Supabase instance, dedicated schema) |
| Time-series | Behavioral sequences | TimescaleDB extension on Supabase |

### Key Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| LLM integration | Direct API, no framework | Transparency, control, organic-first alignment |
| Pattern detection | Statistical, not ML | Sufficient for needs, simpler, interpretable |
| Database | PostgreSQL (Supabase) | Managed hosting, Auth integration, Realtime, Row Level Security |
| Caching | Redis | Performance, TTL support, session management |
| Frontend | React Native (Hybrid Animated Views + Skia Edges + Zustand + Reanimated) | Mobile-first for Indian student market; native Views for nodes (free text/touch/accessibility), Skia for edge rendering (Bézier curves) |

---

## Implementation Phases

| Phase | Focus | Deliverables |
|-------|-------|--------------|
| 1 | Core Infrastructure | Mind map UI, basic question generation, data collection |
| 2 | Classification Pipeline | Post-hoc categorization, question bank storage |
| 2 | Teacher Insights | Selection pattern analytics, accessibility rankings |
| 3 | Diagnostic Engine | Coverage calculation, gap detection, subject weighting |
| 3 | Pattern Analysis | Question path identification, bridge question detection |
| 4 | Student Feedback | Quiz system, self-awareness prompts |
| 4 | Path Suggestions | Apply patterns to improve question suggestions |
| 5 | Teacher Dashboard | Individual profiles, class analytics, recommendations |
| 5 | Content Caching | Pre-generate content for common paths |
| 6 | Refinement | Enhancement layers, adaptive quiz timing, cross-concept transfer |

---

*Document Version 1.2 | System Architecture Specification*
*Aligned with: Organic-First Generation, Post-Hoc Classification, Chapter-Bounded Scope*

**Version History**:
- v1.0: Initial architecture specification
- v1.1: Added Collective Intelligence Layer (Question Paths, Teacher Insights, Content Caching)
- v1.2: Replaced LangChain with Direct API architecture; Added Pattern Analysis Implementation section (no ML required); Added Technical Stack specification


