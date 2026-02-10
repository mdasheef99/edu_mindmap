# Subject-Specific Category Weighting Specification

## Overview

This document specifies how the 8-dimensional Kantian diagnostic framework adapts to different academic subjects through calibrated weighting, maintaining theoretical coherence while accommodating disciplinary epistemological differences.

**Core Principle**: All 8 categories apply to all subjects. Weights determine *relative diagnostic importance*, not applicability.

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

Weights sum-normalized per subject to enable cross-subject comparison.

### Mathematics

| Category | Weight | Rationale |
|----------|--------|-----------|
| C1 Define | 1.5 | Precise definition is foundational to mathematical reasoning |
| C2 Distinguish | 1.3 | Boundary conditions critical (e.g., when theorems apply) |
| C3 Decompose | 1.0 | Important but not distinctively mathematical |
| C4 Connect | 1.0 | Connections matter but less than in humanities |
| C5 Delimit | 1.3 | Counterexamples and edge cases essential |
| C6 Predict | 0.7 | Less central than in sciences |
| C7 Contextualize | 0.5 | Historical/applied context less critical |
| C8 Vary | 1.3 | Alternative approaches and generalizations important |

### Sciences (Physics, Chemistry, Biology)

| Category | Weight | Rationale |
|----------|--------|-----------|
| C1 Define | 1.0 | Important but not distinctively scientific |
| C2 Distinguish | 1.0 | Standard importance |
| C3 Decompose | 1.3 | Mechanism understanding requires structural analysis |
| C4 Connect | 1.3 | Systems thinking connects phenomena |
| C5 Delimit | 1.3 | Understanding when models/laws break down |
| C6 Predict | 1.5 | Prediction is core to scientific epistemology |
| C7 Contextualize | 0.7 | Less central than predictive power |
| C8 Vary | 1.0 | Experimental variations matter |

### History

| Category | Weight | Rationale |
|----------|--------|-----------|
| C1 Define | 0.7 | Definitions often contested in history |
| C2 Distinguish | 1.0 | Distinguishing periods/movements matters |
| C3 Decompose | 0.7 | Less structural than interpretive |
| C4 Connect | 1.5 | Connections across time/place essential |
| C5 Delimit | 1.0 | Understanding limitations of evidence |
| C6 Predict | 1.3 | Causal reasoning about consequences |
| C7 Contextualize | 1.5 | Context is everything in historical understanding |
| C8 Vary | 1.3 | Counterfactual reasoning develops insight |

### Literature & Language Arts

| Category | Weight | Rationale |
|----------|--------|-----------|
| C1 Define | 0.7 | Definitions fluid in interpretive disciplines |
| C2 Distinguish | 1.3 | Genre/style distinctions important |
| C3 Decompose | 1.3 | Close reading requires structural analysis |
| C4 Connect | 1.5 | Intertextual connections central |
| C5 Delimit | 0.7 | Less emphasis on failure conditions |
| C6 Predict | 0.7 | Not central to literary analysis |
| C7 Contextualize | 1.5 | Historical/cultural context essential |
| C8 Vary | 1.3 | Alternative interpretations valued |

### Social Sciences (Economics, Psychology, Sociology)

| Category | Weight | Rationale |
|----------|--------|-----------|
| C1 Define | 1.0 | Operational definitions matter |
| C2 Distinguish | 1.0 | Standard importance |
| C3 Decompose | 1.0 | Variable analysis important |
| C4 Connect | 1.3 | Systems and relationships central |
| C5 Delimit | 1.3 | Model limitations critical |
| C6 Predict | 1.3 | Predictive models central to social science |
| C7 Contextualize | 1.3 | Social/cultural context matters |
| C8 Vary | 1.0 | Standard importance |

---

## Weight Application Algorithm

### Weighted Coverage Calculation

```python
def calculate_weighted_coverage(exploration_data, subject):
    """
    Calculate weighted coverage score for a student's exploration.
    
    Args:
        exploration_data: dict mapping category_id to exploration_depth (0.0-1.0)
        subject: string identifying academic subject
    
    Returns:
        weighted_coverage: float (0.0-1.0)
        gap_report: dict with gap analysis
    """
    weights = get_subject_weights(subject)
    normalized_weights = normalize_weights(weights)
    
    weighted_sum = 0.0
    gap_report = {"critical_gaps": [], "minor_gaps": [], "strengths": []}
    
    for category_id, weight in normalized_weights.items():
        exploration = exploration_data.get(category_id, 0.0)
        weighted_sum += exploration * weight
        
        # Gap detection with weight-adjusted thresholds
        if exploration < 0.3 and weight >= 1.3:
            gap_report["critical_gaps"].append(category_id)
        elif exploration < 0.3 and weight < 1.3:
            gap_report["minor_gaps"].append(category_id)
        elif exploration >= 0.7:
            gap_report["strengths"].append(category_id)
    
    return weighted_sum, gap_report
```

### Gap Severity Classification

| Exploration Level | Category Weight | Gap Classification |
|-------------------|-----------------|-------------------|
| < 0.3 | ≥ 1.3 (elevated) | **Critical Gap** - requires immediate intervention |
| < 0.3 | 1.0 (standard) | **Moderate Gap** - should be addressed |
| < 0.3 | ≤ 0.7 (reduced) | **Minor Gap** - note but lower priority |
| 0.3 - 0.7 | any | **Partial Coverage** - monitor |
| ≥ 0.7 | any | **Adequate Coverage** - strength area |

---

## Teacher Dashboard Integration

### Subject-Aware Diagnostic Display

```
Student: Alex Chen | Subject: Mathematics | Concept: Limits
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Category Coverage (weighted for Mathematics):

  Define     [████████████████░░░░] 80%  ★ HIGH PRIORITY
  Distinguish[████████░░░░░░░░░░░░] 40%  ★ HIGH PRIORITY  ⚠ GAP
  Decompose  [████████████░░░░░░░░] 60%    
  Connect    [██████░░░░░░░░░░░░░░] 30%    
  Delimit    [████░░░░░░░░░░░░░░░░] 20%  ★ HIGH PRIORITY  ⚠ CRITICAL GAP
  Predict    [████████░░░░░░░░░░░░] 40%    
  Context    [░░░░░░░░░░░░░░░░░░░░]  0%    (lower priority for math)
  Vary       [██░░░░░░░░░░░░░░░░░░] 10%  ★ HIGH PRIORITY  ⚠ CRITICAL GAP

Weighted Coverage Score: 47%

PRIORITY INTERVENTIONS (Mathematics-weighted):
1. Delimit: Student hasn't explored when limits fail or don't exist
   → Suggest: "What happens when we try to find the limit of 1/x as x→0?"

2. Vary: Student hasn't explored alternative approaches
   → Suggest: "Could we define limits differently? Why epsilon-delta?"

3. Distinguish: Partial coverage of boundary conditions
   → Suggest: "When is something NOT a limit? What disqualifies a value?"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Cross-Subject Comparison

Weighted scores enable meaningful comparison across subjects:

```
Student: Alex Chen | Cross-Subject Profile
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Subject-Weighted Coverage Scores:

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

1. **Expert Panel Review**: Subject matter experts rate category importance (1-5 scale)
2. **Literature Alignment**: Cross-reference with disciplinary epistemology research
3. **Consensus Building**: Resolve disagreements through structured discussion
4. **Normalization**: Convert to weight scale (0.5-1.5 range)

### Empirical Validation

Once system is operational, validate weights through:

1. **Predictive Validity**: Do weighted gaps predict understanding failures?
   - Students with critical gaps (high-weight categories unexplored) should show poorer understanding
   - Students with minor gaps (low-weight categories unexplored) should show adequate understanding

2. **Teacher Validation**: Do teachers agree with priority rankings?
   - Present weighted vs. unweighted gap reports
   - Measure agreement with teacher intuition

3. **Outcome Correlation**: Do weighted coverage scores predict learning outcomes?
   - Correlate weighted scores with assessment performance
   - Compare predictive power of weighted vs. unweighted scores

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
    "sciences": {
      "define": 1.0,
      "distinguish": 1.0,
      "decompose": 1.3,
      "connect": 1.3,
      "delimit": 1.3,
      "predict": 1.5,
      "contextualize": 0.7,
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


