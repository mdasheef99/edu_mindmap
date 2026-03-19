# Student Reflective Guidance and Self-Review System

## Document Purpose

This document defines a planned future-facing product capability for **student-facing reflective guidance, self-review support, and next-step support**.

For a shorter internal summary, see `docs/student-reflective-guidance-brief.md`.

The platform remains primarily a **path-based conceptual exploration and teacher-support system**. This capability is intended to extend learner value on the student-facing side without repositioning the platform as a strong standalone diagnostic engine.

The purpose of this system is to help learners:
- reflect on what they have explored
- identify useful next steps
- revisit areas that may need reinforcement
- engage in low-stakes review
- build better self-directed study habits

This document is intentionally product-oriented and future-facing. It describes a capability we may develop seriously in a later phase, while keeping claims cautious and evidence-aligned.

---

## Strategic Role in the Product

This capability should be positioned as a **meaningful learner-facing layer** on top of the core exploration system, not as a replacement for that system.

### Primary product role

- For **direct-to-learner use**, it can become a major value driver by making exploration more actionable, reflective, and sticky.
- For **school/institutional use**, it can strengthen independent study, homework follow-through, and student reflection between teacher interactions.
- For the broader product, it can improve the usefulness of the learner experience without collapsing the distinction between learner support and teacher interpretation.

### Positioning summary

The product should still be described primarily as:
- a **path-based conceptual exploration system**
- with **teacher-support interpretation**

This capability should be described as:
- a **student-facing reflective guidance and self-review system**
- a **category-neutral learner guidance layer**
- a **next-step support capability**

---

## Learner Value Hypothesis

The learner-facing value hypothesis is not that the system can definitively determine what a student understands. The hypothesis is that students may learn more effectively when the platform helps them interpret their own exploration path and choose reasonable follow-up actions.

### Working learner value hypothesis

If students receive timely, category-neutral prompts that help them review what they explored, revisit weakly reinforced material, and choose useful next questions, they may:
- retain more of what they studied
- continue exploration more productively
- notice incomplete or fragile understanding earlier
- develop stronger self-regulation and reflection habits

These are product hypotheses to be validated, not settled claims.

---

## Non-Goals and Claim Boundaries

This capability must remain explicitly bounded.

### Non-goals

The student-facing system is **not** intended to be:
- a formal diagnostic engine
- a mastery-judgment engine
- a substitute for teacher judgment
- a grading or certification mechanism
- a category-visible explanation layer
- a claim that the platform knows exactly what the learner "does not understand"

### Claim boundaries

Allowed claims should be framed in terms such as:
- reflective guidance
- self-review support
- next-step support
- possible reinforcement opportunities
- low-stakes review

Avoid or tightly qualify claims such as:
- diagnosis
- gap detection
- misconception diagnosis
- AI assessment engine
- mastery engine

Where stronger language is unavoidable, it should be clearly qualified as:
- a research hypothesis
- a limited signal
- a low-confidence or probabilistic interpretation

---

## Relationship to the Teacher-Support System

The learner-facing system and the teacher-support system should be treated as related but distinct layers.

### Teacher-support layer

- uses internal analytic interpretation
- supports teacher judgment and scaffolding
- may expose dimension/category-visible analytics to authorized teacher/admin surfaces

### Student-facing reflective guidance layer

- remains fully category-neutral
- converts exploration patterns into learner-appropriate support
- helps learners reflect, review, and choose next actions
- must not expose hidden analytic dimensions or teacher-facing interpretations directly

### Core separation rule

The same underlying exploration signals may inform both layers, but the student-facing layer must translate those signals into **supportive, non-diagnostic, learner-appropriate guidance**.

---

## Student-Facing UX Principles

### 1. Category-neutral by default

Students should never see hidden analytic dimensions, internal category labels, or teacher-facing interpretive schemas.

### 2. Reflective, not judgmental

The system should help the learner think about what they explored and what they might do next. It should not speak as if it can authoritatively judge understanding.

### 3. Low-stakes and supportive

Outputs should feel like coaching, review support, and study guidance rather than testing, grading, or correction from an authority.

### 4. Actionable over abstract

Guidance should lead to clear next actions, such as revisiting a node, trying a new question, attempting a short review check, or comparing two related ideas.

### 5. Grounded in actual learner activity

Guidance should be anchored in the learner's recent path, revisits, selections, low-stakes checks, and study history rather than generic encouragement.

### 6. Honest about uncertainty

Where the platform is inferring a likely reinforcement opportunity, the wording should remain cautious and non-final.

---

## Category Invisibility Requirements

The learner-facing system must preserve strict category invisibility.

### Required rules

- No display of analytic dimensions or hidden category names
- No student-facing charts or meters that reveal the internal framework indirectly
- No wording that teaches students to optimize for hidden dimensions
- No learner copy that implies the system is reading hidden cognitive states with confidence

### Allowed translation strategy

Internal signals may be translated into learner-facing wording such as:
- "You may want to revisit how this idea changes under different conditions."
- "You explored the core idea well; a useful next step may be to compare it with a related concept."
- "Try a quick review check before moving on."

---

## Learner-Facing Output Types

The student-facing system may eventually include the following output types.

| Output Type | Purpose | Example Framing |
|------------|---------|-----------------|
| **Exploration recap** | Help the learner remember what they covered | "Here's a short recap of the main ideas you explored." |
| **Reflection prompts** | Encourage metacognition and consolidation | "Which part of this topic still feels least clear to you?" |
| **Next-question suggestions** | Support productive continued exploration | "A useful next question could be: What changes when the conditions change?" |
| **Review suggestions** | Prompt reinforcement of lightly consolidated material | "Before moving on, revisit this comparison once more." |
| **Low-stakes checks** | Help learners test recall or reasoning informally | "Try a quick check: explain this idea in one sentence." |
| **Re-entry prompts** | Help learners resume a prior path productively | "Last time you explored the mechanism; a good next step may be to test the limits." |
| **Study planning nudges** | Encourage better self-directed learning habits | "You may benefit from a short review session on this topic tomorrow." |

These outputs should remain clearly supportive rather than authoritative.

---

## High-Level Product and Architecture Boundaries

This document does not define detailed implementation, but it does define the intended boundary conditions.

### Inputs the learner-facing system may use

- path history and exploration sequence
- question selections and revisits
- node interactions and content consumption
- low-stakes quiz/check performance
- session continuity and return behavior
- internally generated exploration signals

### Outputs it may produce

- recaps
- reflective prompts
- next-step suggestions
- reinforcement suggestions
- low-stakes review prompts

### Outputs it must not produce

- student-visible category scores
- strong claims of misunderstanding or mastery
- teacher-style intervention language
- authoritative statements about what the learner definitively knows or does not know

### Architecture relationship

At a high level, the capability should sit between:
- the **student exploration experience**, where learning behavior is observed
- and the **teacher-support interpretation layer**, where richer internal analysis may exist

The learner-facing layer should consume filtered, translated, category-neutral signals rather than raw teacher-facing analytic outputs.

---

## Measurement and Validation Considerations

Because this capability is learner-facing, helpfulness matters more than theoretical elegance.

### Primary validation questions

- Do students actually use the reflective guidance features?
- Do next-step prompts lead to more productive follow-up exploration?
- Do review suggestions increase return-to-topic behavior or reinforcement activity?
- Do low-stakes checks improve retention or transfer on later performance checks?

### Secondary validation questions

- Do learners report that the guidance feels helpful, clear, and non-judgmental?
- Does the feature improve session continuity for independent learners?
- Does it improve between-class reinforcement in school settings?

### Guardrail questions

- Does the system create false confidence?
- Does it overstate certainty about learner understanding?
- Do learners misread guidance as formal evaluation?
- Does any UI element accidentally expose the hidden analytic framework?

### Evidence standard

The feature should earn stronger product claims only if experiments show that it improves useful learner outcomes such as follow-up exploration, review completion, retention, or transfer without increasing confusion or false certainty.

---

## Phased Product Intent

This capability is best treated as a **later-phase serious product capability**, not as a cosmetic add-on.

### Likely sequencing

1. Establish the core exploration loop and teacher-support interpretation
2. Add bounded learner-facing recap and next-step support
3. Expand into low-stakes self-review and re-entry guidance
4. Validate which guidance types genuinely improve learner outcomes
5. Only then consider broader positioning as a major learner-facing differentiator

This sequencing protects the product from making claims before the supporting evidence and UX quality are strong enough.

---

## Recommended Positioning Language

Preferred wording for this capability:

- **student-facing reflective guidance**
- **self-review support**
- **next-step support**
- **category-neutral learner guidance**
- **low-stakes review**

Recommended summary sentence:

> A future learner-facing capability that helps students reflect on what they have explored, revisit ideas that may need reinforcement, and choose useful next steps through category-neutral guidance and low-stakes self-review support.

---

## Related Documents

This page should remain aligned with:

- `docs/student-reflective-guidance-brief.md`
- `docs/theory-of-change.md`
- `docs/system-architecture.md`
- `docs/measurement-and-experimentation.md`
- `docs/mobile-features-index.md`

Future cross-references may be added from those documents once this capability moves from planned future state into active design.

---

*Document Version 1.0 | Student Reflective Guidance and Self-Review System*
*Status: Future-facing planned capability; evidence and UX claims remain subject to validation*