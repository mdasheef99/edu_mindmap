# Data Collection & Pattern Analysis

**Purpose**: Specification of behavioral data collection and statistical pattern analysis  
**Parent Document**: `docs/system-architecture.md`  
**Version**: 1.0  
**Last Updated**: February 2025

---

## Data Collection Specification

### Mind Map Behavioral Data

| Data Point | Collection Method | Diagnostic Value |
|------------|-------------------|------------------|
| Node dwell time | Timer on node focus | Engagement depth / confusion |
| Selection hesitation | Time between options and click | Decision confidence |
| Node placement | Coordinates when student arranges | Conceptual organization |
| Connection creation | Link events between nodes | Relationship recognition |
| Revisitation count | Return visits to same node | Reinforcement need |
| Navigation sequence | Ordered list of node visits | Exploration strategy |
| Zoom/pan patterns | Viewport changes | Focus vs. overview behavior |

### Question Selection Data

| Data Point | Collection Method | Diagnostic Value |
|------------|-------------------|------------------|
| Question selected | Click event with question ID | Category engagement |
| Questions presented | Full list shown to student | Opportunity set |
| Questions NOT selected | Presented minus selected | Avoidance patterns |
| Selection order | Timestamp sequence | Priority/interest |
| Time to select | Duration viewing options | Decision process |

### Phrase Selection Data (phrase/word selection feature)

**Cross-reference**: See `docs/measurement-and-experimentation.md` §4.6 for detailed offer set logging requirements.

| Data Point | Collection Method | Diagnostic / Product Value |
|------------|-------------------|----------------------------|
| Phrase selected | Selection event with `selected_text` | What learners notice / latch onto |
| Source node | `source_node_id` | Provenance for branching |
| Source excerpt / anchor | Excerpt window + optional offsets/hash | Robustness across formatting/regeneration |
| Phrase offer set shown | `phrase_offer_set_id` with ranked options | Counterfactual measurement ("what was offered") |
| Offer set mode | `mode` (discovery\|exploitation) | Traffic policy tracking |
| Propensities | Per-option selection probability | Off-policy evaluation |
| Action chosen | `elaborate` / `custom_question` / `recommended_question` | Preference signal |
| Recommended question chosen | Selected question text/id | Downstream learning intent |
| Resulting transition | `parent_node_id → child_node_id` edge created | Path reconstruction |
| Thread context reference | `thread_context_id`/hash stored on child | Ensures thread-aware future generation |

### Quiz Performance Data

| Data Point | Collection Method | Diagnostic Value |
|------------|-------------------|------------------|
| Correct/incorrect | Answer evaluation | Understanding verification |
| Dimensional profile of question | From question classification (8D vector) | Dimension-specific understanding |
| Confidence rating | Student self-report (optional) | Metacognitive calibration |
| Time to answer | Response duration | Fluency vs. struggle |
| Answer changes | Edit tracking | Uncertainty signals |

---

## Learning Path Capture (First-Class Product Artifact)

The platform must treat a learner's exploration as a **reconstructable path**, not just summary stats.

**Path =** ordered events over time:
- node focus/visit events,
- offer-set impressions (what was shown),
- question selections (what was chosen), and
- resulting transitions (what happened next).

**Minimum requirements**:
- Every event is tied to `student_id`, `chapter_id`, and a durable `session_id`.
- Offer sets and choices are joinable (e.g., `offer_set_id`, `phrase_offer_set_id`).
- A path can be reconstructed as both:
  - a **sequence** (chronological replay), and
  - a **graph** (clusters, revisits, branching).

**Why this matters (architecturally)**:
- Teacher insights are based on patterns like revisitation, avoidance, and cluster transitions.
- The Content Library promotes high-frequency/high-success **path fragments**.
- Reinforcement artifacts (e.g., podcasts) should be **path-optimized**, not simple narration.

---

## Pattern Analysis Implementation

### Overview

Pattern analysis in the Collective Intelligence Layer uses **statistical methods and database queries**, not machine learning model training. This approach is:
- Simpler to implement and maintain
- Sufficient for the pattern types we need to detect
- Interpretable and debuggable
- Does not require training data or model infrastructure

### Analysis Methods by Feature

| Feature | Analysis Method | ML Required? |
|---------|-----------------|--------------|
| Question path patterns | Sequence frequency counting | ❌ No |
| Bridge question identification | Dimensional transition analysis | ❌ No |
| Success-correlated questions | Pearson/Spearman correlation | ❌ No |
| Dimensional accessibility ranking | Selection rate aggregation by dominant dimension | ❌ No |
| Content caching decisions | Threshold-based rules | ❌ No |
| Three-dimensional success analysis | LLM-assisted extraction | ⚠️ LLM inference (not training) |
| Personalized path prediction | Collaborative filtering | ⚠️ Optional (later) |

### Implementation Examples

**Question Path Pattern Detection** (Pure Database Aggregation):

```python
class QuestionPathAnalyzer:
    """
    Statistical pattern analysis - no ML training required.
    """

    def find_common_paths(self, chapter_id: str, min_frequency: int = 50):
        """
        Find frequently-followed question sequences.
        Implementation: SQL GROUP BY with COUNT aggregation.
        """
        # MongoDB aggregation pipeline example
        return self.db.aggregate([
            {"$match": {"chapter_id": chapter_id}},
            {"$group": {
                "_id": "$question_sequence",
                "frequency": {"$sum": 1},
                "avg_quiz_score": {"$avg": "$final_quiz_score"},
                "students": {"$addToSet": "$student_id"}
            }},
            {"$match": {"frequency": {"$gte": min_frequency}}},
            {"$sort": {"frequency": -1}}
        ])

    def identify_bridge_questions(self, chapter_id: str):
        """
        Find questions whose dimensional profiles effectively transition
        students from one region of the dimensional space to another.
        Implementation: Dimensional transition analysis using cumulative state.
        """
        transitions = []

        for session in self.get_sessions(chapter_id):
            cumulative = {d: 0.0 for d in DIMENSIONS}
            n = 0
            for i, question in enumerate(session.questions[:-1]):
                # Update cumulative state
                scores = question.classification.dimensional_scores
                for d in DIMENSIONS:
                    cumulative[d] += scores[d]
                n += 1
                normalised = {d: cumulative[d] / n for d in DIMENSIONS}

                next_question = session.questions[i + 1]
                next_scores = next_question.classification.dimensional_scores

                # Identify which dimensions were low before and engaged after
                high_dims = [d for d in DIMENSIONS if normalised[d] >= 0.5]
                low_dims = [d for d in DIMENSIONS if normalised[d] < 0.3]
                engaged_dims = [d for d in DIMENSIONS if next_scores[d] >= 0.6]

                transitions.append({
                    "cumulative_high": high_dims,
                    "cumulative_low": low_dims,
                    "bridge_question": next_question.id,
                    "bridge_profile": next_scores,
                    "dimensions_bridged": [d for d in engaged_dims if d in low_dims],
                    "session_continued": len(session.questions) > i + 2
                })

        # Aggregate: which questions most often bridge dimensional gaps?
        return self.aggregate_bridge_effectiveness(transitions)
```

**Success Correlation Analysis** (Basic Statistics):

```python
from scipy.stats import pearsonr, spearmanr

class SuccessCorrelationAnalyzer:
    """
    Statistical correlation - scipy, not ML.
    """

    def calculate_question_success_correlation(self, chapter_id: str):
        """
        Correlate question selection with quiz performance.
        Implementation: Pearson correlation coefficient.
        """
        questions = self.get_all_questions(chapter_id)
        correlations = {}

        for question in questions:
            all_sessions = self.get_all_sessions(chapter_id)

            # Binary: did student select this question?
            selection_vector = [
                1 if question.id in s.selected_questions else 0
                for s in all_sessions
            ]

            # Continuous: student's quiz score
            score_vector = [s.quiz_score for s in all_sessions]

            # Calculate correlation
            correlation, p_value = pearsonr(selection_vector, score_vector)

            correlations[question.id] = {
                "correlation": correlation,
                "p_value": p_value,
                "significant": p_value < 0.05,
                "direction": "positive" if correlation > 0 else "negative"
            }

        return correlations
```

**LLM-Assisted Success Factor Analysis** (Inference, Not Training):

```python
class SuccessFactorAnalyzer:
    """
    Uses LLM for analysis - but this is INFERENCE, not model training.
    The LLM extracts patterns from successful questions.
    """

    async def extract_success_factors(self, question: Question, metrics: dict):
        """
        LLM extracts WHY a question succeeded.
        This is prompt-based analysis, not ML training.
        """
        prompt = f"""
        Analyze why this question was successful with students:

        Question: "{question.text}"
        Concept: {question.concept}
        Selection Rate: {metrics['selection_rate']:.0%}
        Quiz Score Correlation: {metrics['correlation']:.2f}

        Extract:
        1. SEMANTIC BRIDGE: What conceptual connection made this compelling?
        2. LINGUISTIC FRAMING: What language pattern felt natural?
        3. CONTEXTUAL SETUP: What situational framing created relevance?

        Return as JSON.
        """

        # LLM inference call - no model training
        response = await self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        return self._parse_factors(response.content[0].text)
```

### When ML might be considered (optional, later)

Machine learning models are **optional enhancements** that could be considered only after simpler approaches have been validated:

| ML Approach | Use Case | Prerequisite |
|-------------|----------|--------------|
| Collaborative filtering | Personalized question recommendations | Large user base (1000+ students) |
| Embedding similarity | Cross-concept pattern transfer | Proven patterns in source concepts |
| Sequence prediction | Next-question prediction | Validated path patterns |

**Decision Criteria**: Only implement ML if statistical approaches demonstrate clear limitations after simpler approaches have been validated.

---

## Related Documents

- **[System Architecture](../system-architecture.md)** - Parent document with full system design
- **[LLM Pipeline](llm-pipeline.md)** - Question generation and classification
- **[Analytics Dashboard Inventory](../analytics-dashboard-inventory.md)** - Teacher-facing pattern visualizations
- **[Content Library Specification](../content-library-specification.md)** - Pattern-based content caching


