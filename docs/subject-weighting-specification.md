# Subject-Specific Category Weighting Specification

## Overview

This document specifies how the 8-dimensional diagnostic framework adapts to different academic subjects through calibrated weighting, maintaining theoretical coherence while accommodating disciplinary epistemological differences.

**Core Principle**: All 8 categories apply to all subjects. Weights determine *relative diagnostic significance*, not applicability.

---

## Theoretical Framing

The 8 categories used in this framework are grounded in a principled derivation from a philosophical tradition asking the right foundational question: *what are the fundamental ways a mind engages with a concept?* This makes them a stronger starting point than dimensions selected by committee or intuition. The weight matrices encode the typical structural availability and diagnostic significance of each categorical dimension across a subject's characteristic concept types. The 8 categories are not claimed to be logically complete—logical completeness requires an independent argument that is not provided here. Instead, **provisional sufficiency** is claimed: these categories are adequate for diagnostic purposes given current evidence. Sufficiency is tested through **independent open-coding probes** in which raters generate dimensional labels without prior knowledge of the framework, not through classification residual analysis, which is circular (a classifier trained on these categories will force questions into them by construction).

Subject weights reflect the uneven ways in which different subjects make some dimensions more diagnostically central and others less central. The weights are the system's principled encoding of that unevenness, grounded in expert judgment about conceptual engagement and refined by empirical validation.

---

## Category Reference

| ID | Category | Cognitive Function |
|----|----------|-------------------|
| C1 | Define | Establish what the concept IS (essence) |
| C2 | Distinguish | Establish what the concept is NOT (boundaries) |
| C3 | Decompose | Analyze constituent parts (structure) |
| C4 | Connect | Map relationships to other concepts |
| C5 | Delimit | Identify constraints and failure conditions |
| C6 | Predict | Trace effects and consequences |
| C7 | Contextualize | Situate within larger frameworks |
| C8 | Vary | Explore alternatives and contingencies |

---

## Subject Weight Matrices

### Weight Scale
- **1.0** = Standard importance (baseline)
- **1.3** = Elevated importance (discipline-critical)
- **0.7** = Reduced importance (less central to discipline)
- **1.5** = High importance (essential for disciplinary understanding)
- **0.5** = Low importance (peripheral to core understanding)

A low weight (0.5) does not mean a category is unimportant in general—it means the concept types characteristic of that subject tend to engage that dimension less centrally, making gaps there less diagnostically significant. Weights encode diagnostic significance and typical structural availability, not pedagogical preference.

Weights sum-normalized per subject to enable cross-subject comparison.

### Mathematics

| Category | Weight | Rationale |
|----------|--------|-----------|
| C1 Define | 1.5 | Mathematical concepts are structurally rich in definitional precision; most concept types require exact boundary-setting |
| C2 Distinguish | 1.3 | Boundary and applicability conditions are consistently instantiated (e.g., when theorems apply vs. fail) |
| C3 Decompose | 1.0 | Structural decomposition is present but not distinctively rich across mathematical concept types |
| C4 Connect | 1.0 | Relational structure is present but less pervasively instantiated than in humanities |
| C5 Delimit | 1.3 | Counterexamples and edge cases are richly and consistently present in mathematical concepts |
| C6 Predict | 0.7 | Causal/consequential structure tends to be less central in most mathematical concept types |
| C7 Contextualize | 0.5 | Historical/applied framing tends to be less central to most mathematical concept types |
| C8 Vary | 1.3 | Alternative approaches and generalizations are richly instantiated across mathematical concepts |

### Physics

| Category | Weight | Rationale |
|----------|--------|-----------|
| C1 Define | 1.3 | Physical concepts require precise operational definitions (force, energy, field); definitional structure is richly instantiated |
| C2 Distinguish | 1.0 | Boundary distinctions are present at standard levels (e.g., elastic vs. inelastic collisions) |
| C3 Decompose | 1.3 | Force diagrams, vector decomposition, and system analysis are richly instantiated in physics concepts |
| C4 Connect | 1.3 | Conservation laws and cross-domain unification (mechanics ↔ thermodynamics ↔ E&M) are richly present |
| C5 Delimit | 1.5 | Applicability conditions and model breakdown (classical → relativistic, deterministic → quantum) are pervasively instantiated |
| C6 Predict | 1.5 | Predictive structure is the core epistemic mode of physics; richly instantiated across all concept types |
| C7 Contextualize | 0.5 | Historical/applied framing tends to be less central to most physics concept types |
| C8 Vary | 1.0 | Alternative formulations (Lagrangian vs. Newtonian) are present at standard levels |

### Chemistry

| Category | Weight | Rationale |
|----------|--------|-----------|
| C1 Define | 1.0 | Definitional structure is present at standard levels (compound, reaction, bond) |
| C2 Distinguish | 1.3 | Distinguishing similar species (isomers, isotopes, oxidation states) is richly instantiated in chemistry |
| C3 Decompose | 1.5 | Structural decomposition (molecular structure, reaction mechanisms, electron configurations) is pervasively instantiated |
| C4 Connect | 1.3 | Reaction networks, periodic trends, and structure-property relationships are richly present |
| C5 Delimit | 1.0 | Reaction conditions and equilibrium limits are present at standard levels |
| C6 Predict | 1.3 | Predicting products, properties, and reactivity is richly instantiated in chemistry concepts |
| C7 Contextualize | 0.7 | Applied/industrial framing tends to be less central relative to mechanistic structure |
| C8 Vary | 1.0 | Alternative synthesis routes and reaction pathways are present at standard levels |

### Biology

| Category | Weight | Rationale |
|----------|--------|-----------|
| C1 Define | 0.7 | Biological definitions are often fuzzy and contested (species, gene, life); definitional precision tends to be less central |
| C2 Distinguish | 1.0 | Taxonomic and functional distinctions are present at standard levels |
| C3 Decompose | 1.3 | Hierarchical decomposition (organism → organ → tissue → cell → molecule) is richly instantiated |
| C4 Connect | 1.5 | Ecological networks, metabolic pathways, and evolutionary relationships are pervasively and richly instantiated |
| C5 Delimit | 1.3 | Environmental limits, homeostatic ranges, and niche boundaries are richly present in biological concepts |
| C6 Predict | 1.3 | Predicting outcomes (inheritance, population dynamics, physiological responses) is richly instantiated |
| C7 Contextualize | 1.0 | Evolutionary and ecological framing is present at standard levels across biological concepts |
| C8 Vary | 1.0 | Genetic variation and alternative strategies are present at standard levels |

### History

| Category | Weight | Rationale |
|----------|--------|-----------|
| C1 Define | 0.7 | Definitional precision is less central in historical concepts; definitions are typically contested and fluid |
| C2 Distinguish | 1.0 | Period/movement distinctions are present at standard levels across historical concept types |
| C3 Decompose | 0.7 | Structural decomposition tends to be less central in historical concepts, which are more interpretive than compositional |
| C4 Connect | 1.5 | Relational structure across time, place, and causation is pervasively and richly instantiated |
| C5 Delimit | 1.0 | Evidential limitations are present at standard levels in historical concept types |
| C6 Predict | 1.3 | Causal-consequential structure is richly present in historical concepts |
| C7 Contextualize | 1.5 | Broader framing is pervasively and richly instantiated; historical concepts are structurally saturated with context |
| C8 Vary | 1.3 | Counterfactual and alternative-interpretation structure is richly present in historical concepts |

### Literature & Language Arts

| Category | Weight | Rationale |
|----------|--------|-----------|
| C1 Define | 0.7 | Definitional precision is less central in literary concepts; meaning is fluid and interpretive |
| C2 Distinguish | 1.3 | Genre, style, and register distinctions are richly instantiated across literary concept types |
| C3 Decompose | 1.3 | Compositional and structural analysis is richly present in literary concepts (close reading) |
| C4 Connect | 1.5 | Intertextual and thematic relational structure is pervasively instantiated across literary concepts |
| C5 Delimit | 0.7 | Failure-condition analysis tends to be less central in most literary concept types |
| C6 Predict | 0.7 | Causal/consequential analysis tends to be less central in most literary concept types |
| C7 Contextualize | 1.5 | Historical/cultural framing is pervasively and richly instantiated in literary concepts |
| C8 Vary | 1.3 | Alternative-interpretation structure is richly present across literary concept types |

### Social Sciences (Economics, Psychology, Sociology)

| Category | Weight | Rationale |
|----------|--------|-----------|
| C1 Define | 1.0 | Operational definitional structure is present at standard levels across social science concept types |
| C2 Distinguish | 1.0 | Boundary distinctions are present at standard levels across social science concepts |
| C3 Decompose | 1.0 | Variable decomposition is present at standard levels across social science concept types |
| C4 Connect | 1.3 | Systems-level relational structure is richly instantiated across social science concepts |
| C5 Delimit | 1.3 | Model-limitation structure is richly and consistently present in social science concept types |
| C6 Predict | 1.3 | Predictive/causal structure is richly instantiated across social science concepts |
| C7 Contextualize | 1.3 | Social/cultural framing is richly present across social science concept types |
| C8 Vary | 1.0 | Alternative-variation structure is present at standard levels across social science concepts |

---

## Input: Exploration Data Aggregation

Before applying subject weights, exploration data must be aggregated from raw question selections. This aggregation step is defined in `docs/system-architecture.md` and must be applied upstream of the weighting calculation.

### Dimensional Vector Aggregation

Each selected question is classified as an **8-dimensional engagement vector** — independent scores (0.0–1.0) across all 8 dimensions. The aggregation step accumulates these vectors into a normalised cumulative score per dimension.

### Aggregation Pseudocode

```python
DIMENSIONS = ["define", "distinguish", "decompose", "connect",
              "delimit", "predict", "contextualize", "vary"]

def aggregate_exploration_data(selected_questions: list[Question]) -> dict[str, float]:
    """
    Aggregate raw question selections into normalised cumulative scores.

    Args:
        selected_questions: List of questions selected by student, each with
                          classification.scores: dict[str, float] (0.0-1.0 per dimension),
                          classification.classification_entropy: float

    Returns:
        normalised_cumulative: dict mapping dimension to normalised cumulative score
    """
    cumulative = {d: 0.0 for d in DIMENSIONS}
    count = 0

    for question in selected_questions:
        # Skip high-entropy classifications (entropy > 2.8 — hedging)
        if question.classification.classification_entropy > 2.8:
            continue

        for d in DIMENSIONS:
            cumulative[d] += question.classification.scores[d]
        count += 1

    # Normalise: cumulative[d] / N
    if count > 0:
        normalised = {d: cumulative[d] / count for d in DIMENSIONS}
    else:
        normalised = {d: 0.0 for d in DIMENSIONS}

    return normalised
```

**Important**: The `normalised_cumulative` dict passed to `calculate_weighted_coverage()` must be the output of this aggregation step, not raw question counts.

---

## Weight Application Algorithm

### Weighted Coverage Calculation

```python
DIMENSIONS = ["define", "distinguish", "decompose", "connect",
              "delimit", "predict", "contextualize", "vary"]

def calculate_weighted_coverage(normalised_cumulative, subject):
    """
    Calculate weighted coverage score for a student's exploration.

    Args:
        normalised_cumulative: dict mapping dimension to normalised cumulative score (0.0–1.0).
                               Computed as: Σ scores[d] / N  for each dimension d,
                               where scores come from the 8-dimensional engagement vectors
                               of all classified selected questions.
        subject: string identifying academic subject

    Returns:
        weighted_coverage: float (0.0-1.0)
        gap_report: dict with gap analysis
    """
    weights = get_subject_weights(subject)
    normalized_weights = normalize_weights(weights)

    weighted_sum = 0.0
    gap_report = {"critical_gaps": [], "minor_gaps": [], "strengths": []}

    for dimension, weight in normalized_weights.items():
        score = normalised_cumulative.get(dimension, 0.0)
        weighted_sum += score * weight

        # Gap detection with weight-adjusted thresholds
        if score < 0.3 and weight >= 1.3:
            gap_report["critical_gaps"].append(dimension)
        elif score < 0.3 and weight < 1.3:
            gap_report["minor_gaps"].append(dimension)
        elif score >= 0.7:
            gap_report["strengths"].append(dimension)

    return weighted_sum, gap_report
```

### Gap Severity Classification

Gap severity uses the **normalised cumulative score** per dimension (`Σ scores[d] / N`), not raw counts or primary/secondary assignments.

| Normalised Cumulative Score | Dimension Weight | Gap Classification |
|-----------------------------|-----------------|-------------------|
| < 0.3 | ≥ 1.3 (elevated) | **Significant Gap Detected** — follow-up recommended |
| < 0.3 | 1.0 (standard) | **Moderate Gap Detected** — support recommended |
| < 0.3 | ≤ 0.7 (reduced) | **Lower-Priority Gap Detected** — note for follow-up |
| 0.3 – 0.7 | any | **Partial Coverage Detected** — monitor |
| ≥ 0.7 | any | **Adequate Coverage** — relative strength |

---

## Teacher Dashboard Integration

### Subject-Aware Diagnostic Display

```
Student: Alex Chen | Subject: Mathematics | Concept: Limits
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Category Coverage (weighted for Mathematics):

  Define     [████████████████░░░░] 80%  ★ HIGH PRIORITY
  Distinguish[████████░░░░░░░░░░░░] 40%  ★ HIGH PRIORITY  ⚠ FOLLOW-UP
  Decompose  [████████████░░░░░░░░] 60%    
  Connect    [██████░░░░░░░░░░░░░░] 30%    
  Delimit    [████░░░░░░░░░░░░░░░░] 20%  ★ HIGH PRIORITY  ⚠ SIGNIFICANT GAP
  Predict    [████████░░░░░░░░░░░░] 40%    
  Context    [░░░░░░░░░░░░░░░░░░░░]  0%    (lower priority for math)
  Vary       [██░░░░░░░░░░░░░░░░░░] 10%  ★ HIGH PRIORITY  ⚠ SIGNIFICANT GAP

Weighted Coverage Score: 47%

PRIORITY FOLLOW-UPS (Mathematics-weighted):
1. Delimit: Significant gap detected in boundary cases where limits fail or do not exist
   → Suggest: "What happens when we try to find the limit of 1/x as x→0?"

2. Vary: Significant gap detected in alternative approaches to limits
   → Suggest: "Could we define limits differently? Why epsilon-delta?"

3. Distinguish: Limited exploration detected in boundary conditions
   → Suggest: "When is something NOT a limit? What disqualifies a value?"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Cross-Subject Comparison

Weighted scores enable meaningful comparison across subjects:

```
Student: Alex Chen | Cross-Subject Profile
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Subject-Weighted Diagnostic Coverage Scores:

  Mathematics  [████████████░░░░░░░░] 58%
  Physics      [████████████████░░░░] 78%
  History      [██████████░░░░░░░░░░] 52%
  Literature   [████████░░░░░░░░░░░░] 42%

Cross-Subject Pattern:
- Strongest in empirical/predictive subjects (Physics)
- Weaker in interpretive/contextual subjects (Literature, History)
- Mathematics gap in boundary/variation categories

Recommended Focus: Contextualization and interpretation skills
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Weight Calibration Process

### Initial Weight Determination

1. **Expert Panel Review**: Subject matter experts rate the typical diagnostic centrality of each dimension—how richly and consistently a given dimension is engaged across the concept types of that subject (1-5 scale). The calibration process elicits judgments about structural availability and diagnostic significance, not preference rankings.
2. **Literature Alignment**: Cross-reference with disciplinary epistemology research
3. **Consensus Building**: Resolve disagreements through structured discussion
4. **Normalization**: Convert to weight scale (0.5-1.5 range)

### Empirical Validation

Once system is operational, validate weights through:

1. **Predictive Validity**: Do weighted diagnostic gaps predict understanding failures?
   - Students with significant gaps (high-weight categories weakly explored) should be more likely to show poorer understanding
   - Students with lower-priority gaps (low-weight categories weakly explored) should be less likely to show meaningful understanding failures

2. **Teacher Validation**: Do teachers agree with priority rankings?
   - Present weighted vs. unweighted gap reports
   - Measure agreement with teacher intuition

3. **Outcome Correlation**: Do weighted diagnostic coverage scores predict learning outcomes?
   - Correlate weighted diagnostic scores with assessment performance
   - Compare predictive power of weighted vs. unweighted scores

4. **Independent Sufficiency Probe**: Human raters open-code a sample of student-generated questions without prior knowledge of the 8 categories. Emergent dimensional labels are compared against the framework. Consistent convergence is evidence of sufficiency; consistent emergence of uncaptured dimensions is a finding requiring framework revision. This probe must be conducted periodically as a standing validation requirement, not only at initial calibration. Classifier residual analysis alone is not a valid sufficiency test because a classifier trained on these categories will force questions into them by construction.

5. **Breadth vs. Depth Tradeoff**: Does broader engagement across multiple weighted dimensions predict better learning outcomes than equivalent depth in a subset of dimensions? The weighting system is directly implicated in this test: if breadth across high-weight dimensions predicts better outcomes than depth in one or two, that validates both the breadth hypothesis and the weight calibration. This is one of the framework's core empirical questions and must be tested, not assumed.

### Weight Adjustment Protocol

```
IF empirical_validation shows weight_i is miscalibrated:
    - Collect prediction errors for category_i
    - Analyze whether gaps in category_i predicted understanding failures
    - IF over-weighted: reduce weight by 0.1-0.2
    - IF under-weighted: increase weight by 0.1-0.2
    - Re-validate after adjustment
```

---

## Data Schema

### Subject Weight Configuration

```json
{
  "subject_weights": {
    "mathematics": {
      "define": 1.5,
      "distinguish": 1.3,
      "decompose": 1.0,
      "connect": 1.0,
      "delimit": 1.3,
      "predict": 0.7,
      "contextualize": 0.5,
      "vary": 1.3
    },
    "physics": {
      "define": 1.3,
      "distinguish": 1.0,
      "decompose": 1.3,
      "connect": 1.3,
      "delimit": 1.5,
      "predict": 1.5,
      "contextualize": 0.5,
      "vary": 1.0
    },
    "chemistry": {
      "define": 1.0,
      "distinguish": 1.3,
      "decompose": 1.5,
      "connect": 1.3,
      "delimit": 1.0,
      "predict": 1.3,
      "contextualize": 0.7,
      "vary": 1.0
    },
    "biology": {
      "define": 0.7,
      "distinguish": 1.0,
      "decompose": 1.3,
      "connect": 1.5,
      "delimit": 1.3,
      "predict": 1.3,
      "contextualize": 1.0,
      "vary": 1.0
    }
  },
  "version": "1.0",
  "last_calibration": "2025-01-15"
}
```

### Student Exploration Record

```json
{
  "student_id": "student_123",
  "concept_id": "limits_calculus",
  "subject": "mathematics",
  "exploration_data": {
    "define": 0.8,
    "distinguish": 0.4,
    "decompose": 0.6,
    "connect": 0.3,
    "delimit": 0.2,
    "predict": 0.4,
    "contextualize": 0.0,
    "vary": 0.1
  },
  "weighted_coverage": 0.47,
  "critical_gaps": ["delimit", "vary"],
  "minor_gaps": ["contextualize"],
  "timestamp": "2025-01-15T10:30:00Z"
}
```

---

## Implementation Checklist

- [ ] Define weight matrices for all target subjects
- [ ] Implement weighted coverage calculation algorithm
- [ ] Build gap severity classification logic
- [ ] Design teacher dashboard with subject-aware display
- [ ] Create cross-subject comparison views
- [ ] Establish expert panel for initial weight calibration
- [ ] Design validation study protocol
- [ ] Build weight adjustment pipeline for empirical refinement

---

*Document Version 1.0 | Subject-Specific Weighting Specification*


