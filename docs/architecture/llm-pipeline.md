# LLM Pipeline Architecture

**Purpose**: Specification of the two-stage LLM pipeline for organic question generation and post-hoc classification  
**Parent Document**: `docs/system-architecture.md`  
**Version**: 1.0  
**Last Updated**: February 2025

---

## Design Philosophy

The LLM pipeline uses **direct API calls** with custom async orchestration rather than heavyweight frameworks. This approach provides:

- **Full transparency**: No hidden abstractions obscuring prompt behavior
- **Maximum control**: Direct access to prompts and response handling
- **Simpler debugging**: Clear stack traces and observable API calls
- **Framework independence**: Easy to swap LLM providers (Anthropic ↔ OpenAI ↔ local models)
- **Alignment with organic-first**: Nothing hidden from understanding

---

## Pipeline Structure

### Two-Stage Architecture

**Stage 1: Organic Question Generation**
- Model: Claude Sonnet 4 (`claude-sonnet-4-20250514`)
- Purpose: Generate 4-6 natural, context-driven questions
- No categorical structure imposed
- Student-facing output

**Stage 2: Post-Hoc Classification**
- Model: Claude Haiku 4 (`claude-haiku-4-20250514`)
- Purpose: Score each question across all 8 diagnostic dimensions as an independent engagement vector (0.0–1.0 per dimension)
- Invisible to students (teacher/admin analytics only)
- 10x cheaper than Sonnet (see `docs/scalability-analysis.md` §4.5)
- **Entropy-based quality gate**: `MAX_CLASSIFICATION_ENTROPY = 2.8`
  - Classifications with Shannon entropy above this threshold are flagged as `needs_review` — the classifier is hedging across too many dimensions
  - `MIN_CLASSIFICATION_ENTROPY = 0.5` — classifications below this threshold are flagged as suspiciously confident ("snapping" to a single dimension)
  - Rationale: Entropy replaces a single confidence score because dimensional vectors have 8 degrees of freedom; a scalar confidence cannot capture whether the classifier is hedging vs. confident across a multi-dimensional output

---

## Implementation

### Core Pipeline Class

```python
import anthropic
from dataclasses import dataclass
from typing import Optional
import asyncio

@dataclass
class GeneratedQuestion:
    text: str
    context: dict
    classification: Optional[dict] = None

class OrganicQuestionPipeline:
    """
    Transparent, framework-free LLM pipeline.
    Direct API calls with custom orchestration.
    """

    MAX_CLASSIFICATION_ENTROPY = 2.8   # Above = hedging (too uniform)
    MIN_CLASSIFICATION_ENTROPY = 0.5   # Below = snapping (suspiciously peaked)

    def __init__(self, client: anthropic.Anthropic):
        self.client = client

    async def generate_organic_questions(
        self,
        chapter_topic: str,
        current_node: str,
        connected_nodes: list[str],
        content_consumed: str
    ) -> list[GeneratedQuestion]:
        """
        Stage 1: Pure organic generation.
        No categorical structure imposed.
        """
        prompt = f"""
        You are helping a curious student explore {chapter_topic}.

        They are currently looking at: {current_node}
        They have connected it to: {', '.join(connected_nodes)}
        They have read: {content_consumed[:500]}...

        Generate 4-6 questions a genuinely curious student might ask next.
        Questions should feel natural and emerge from the context.

        Do NOT:
        - Use formulaic question patterns
        - Force artificial variety
        - Reference any educational framework

        Return as JSON array: [{{"text": "question text"}}]
        """

        response = await self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )

        questions = self._parse_questions(response.content[0].text)
        return [GeneratedQuestion(text=q["text"], context={
            "chapter": chapter_topic,
            "node": current_node,
            "connections": connected_nodes
        }) for q in questions]

    async def classify_question(
        self,
        question: GeneratedQuestion,
        subject: str
    ) -> GeneratedQuestion:
        """
        Stage 2: Post-hoc classification.
        Applied AFTER generation, invisible to students.
        Uses Claude Haiku (not Sonnet) — classification is a constrained
        structured-output task that doesn't require Sonnet's capabilities.
        See docs/scalability-analysis.md §4.5 for cost rationale (10x cheaper).
        """
        prompt = f"""
        Score this question's engagement with each diagnostic dimension.

        Question: "{question.text}"
        Subject: {subject}
        Context: Generated while exploring {question.context['node']}

        For each dimension, assign an independent score from 0.0 to 1.0:
        - 0.0 = dimension not present in this question
        - 0.3 = tangentially engaged
        - 0.6 = meaningfully engaged
        - 0.9 = centrally engaged

        Dimensions:
        1. define - What is X?
        2. distinguish - How is X different from Y?
        3. decompose - What are the parts of X?
        4. connect - How does X relate to Y?
        5. delimit - What are the limits/boundaries of X?
        6. predict - What happens if X?
        7. contextualize - Why does X matter historically/socially?
        8. vary - What are alternatives to X?

        Scores are independent — they do NOT need to sum to 1.
        A question can score high on multiple dimensions simultaneously.

        Return JSON: {{
          "dimensions": {{"define": float, "distinguish": float, "decompose": float,
                         "connect": float, "delimit": float, "predict": float,
                         "contextualize": float, "vary": float}},
          "classification_entropy": float
        }}

        classification_entropy = Shannon entropy of the normalised score vector.
        Low entropy (<1.5) = confident, peaked classification.
        High entropy (>2.8) = hedging across many dimensions.
        """

        response = await self.client.messages.create(
            model="claude-haiku-4-20250514",
            max_tokens=300,
            messages=[{{"role": "user", "content": prompt}}]
        )

        classification = self._parse_classification(response.content[0].text)

        # Entropy-based quality gate
        entropy = classification.get('classification_entropy', 0.0)
        if entropy > self.MAX_CLASSIFICATION_ENTROPY:
            # Hedging: classifier spread scores too uniformly
            classification['is_classified'] = False
            classification['needs_review'] = True
        elif entropy < self.MIN_CLASSIFICATION_ENTROPY:
            # Snapping: suspiciously peaked on one dimension
            classification['is_classified'] = True
            classification['needs_review'] = True  # Flag for spot-check
        else:
            classification['is_classified'] = True
            classification['needs_review'] = False

        question.classification = classification
        return question

    async def process_batch(
        self,
        chapter_topic: str,
        current_node: str,
        connected_nodes: list[str],
        content_consumed: str,
        subject: str
    ) -> list[GeneratedQuestion]:
        """
        Full pipeline: generate → classify (invisibly) → store.
        Parallel classification for efficiency.
        """
        # Stage 1: Organic generation
        questions = await self.generate_organic_questions(
            chapter_topic, current_node, connected_nodes, content_consumed
        )

        # Stage 2: Invisible classification (parallel execution)
        classified = await asyncio.gather(*[
            self.classify_question(q, subject) for q in questions
        ])

        # Stage 3: Store in question bank
        await self.store_questions(classified)

        # Stage 4: Apply conditional enhancements if needed
        enhanced = await self.apply_conditional_enhancements(classified)

        return enhanced
```

---

## Optional: Structured Output Validation

For complex classification outputs, the **Instructor** library can provide type-safe validation:

```python
# Optional: Using Instructor for structured outputs
import instructor
from pydantic import BaseModel, Field
from anthropic import Anthropic

class DimensionalScores(BaseModel):
    define: float = Field(ge=0.0, le=1.0)
    distinguish: float = Field(ge=0.0, le=1.0)
    decompose: float = Field(ge=0.0, le=1.0)
    connect: float = Field(ge=0.0, le=1.0)
    delimit: float = Field(ge=0.0, le=1.0)
    predict: float = Field(ge=0.0, le=1.0)
    contextualize: float = Field(ge=0.0, le=1.0)
    vary: float = Field(ge=0.0, le=1.0)

class QuestionClassification(BaseModel):
    dimensions: DimensionalScores = Field(description="Independent engagement scores per dimension")
    classification_entropy: float = Field(ge=0.0, description="Shannon entropy of normalised score vector")

client = instructor.from_anthropic(Anthropic())

# Classification uses Haiku (structured output task, 10x cheaper than Sonnet)
classification = client.messages.create(
    model="claude-haiku-4-20250514",
    response_model=QuestionClassification,
    messages=[{"role": "user", "content": classification_prompt}]
)
# Returns validated Pydantic model, not raw JSON
```

---

## Why Not LangChain?

| Consideration | Direct API | LangChain |
|---------------|------------|-----------|
| **Transparency** | Full visibility into prompts | Abstraction layers obscure behavior |
| **Complexity** | Minimal dependencies | Heavy framework with frequent breaking changes |
| **Control** | Direct prompt engineering | Framework patterns may not fit organic-first |
| **Debugging** | Simple stack traces | Multi-layer abstraction complicates debugging |
| **Use case fit** | Our pipeline is linear (generate → classify) | Designed for complex agent workflows |

---

## Related Documents

- **[System Architecture](../system-architecture.md)** - Parent document with full system design
- **[Scalability Analysis](../scalability-analysis.md)** - Cost analysis for Sonnet vs Haiku (§4.5)
- **[Mobile Feature Specification](../mobile-feature-specification.md)** - AI Node features (§2.3)
- **[Framework Design Philosophy](../framework-design-philosophy.md)** - Organic-first principles


