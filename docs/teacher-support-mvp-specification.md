# Teacher Support MVP Specification

**Document Version**: 1.0  
**Status**: Current MVP Scope  
**Last Updated**: March 2026  
**Related Documents**: `docs/prd/master-prd.md`, `docs/mvp-features-specification.md`, `docs/framework-design-philosophy.md`, `docs/measurement-and-experimentation.md`, `docs/teacher-access-control-specification.md`

---

## 1. Purpose

This document defines the smallest teacher-facing surface and access boundary included in the current MVP. It exists to make the teacher-support layer concrete without expanding the product into a full teacher dashboard, intervention system, or admin operations suite.

---

## 2. Role in the Documentation Set

- `docs/prd/master-prd.md` remains the master product-definition and scope anchor.
- `docs/mvp-features-specification.md` remains the learner/mobile MVP feature reference and the source for shared data-capture requirements.
- `docs/teacher-support-mvp-specification.md` defines the current teacher-facing MVP surface and minimum access boundary.
- `docs/teacher-access-control-specification.md` should be treated as a broader, later-phase privilege/intervention reference rather than the current MVP source of truth.
- `docs/analytics-dashboard-inventory.md` remains a broader dashboard inventory reference and is not, by itself, a commitment to current MVP scope.

---

## 3. MVP Teacher Job to Be Done

Before the next class, a teacher should be able to review a student's chapter exploration quickly enough to decide what to ask next, which concept to revisit, or where targeted scaffolding may help.

Current MVP teacher support is:

- chapter-level
- per-student
- action-oriented
- category-visible only on teacher-facing surfaces
- probabilistic rather than diagnostic

Current MVP teacher support is not:

- a full class analytics suite
- a content intervention workflow
- a replacement for teacher judgment

---

## 4. Minimum MVP Teacher Surface

| Capability | MVP expectation |
|------------|-----------------|
| Open teacher-only review surface | Teacher opens a protected teacher-facing view for an authorized student and chapter |
| Review chapter exploration path | See the student's chapter path as recorded through node visits, selections, and thread progression |
| Review explored vs relatively thin areas | See which chapter concepts or areas appear explored versus comparatively under-examined |
| Review weighted follow-up areas | See teacher-facing prioritization shaped by internal interpretation and subject weighting |
| Review checkpoint metacognitive signals | See optional Sensemaking Pause response quality and repeated opt-out patterns as cautious teacher-support evidence |
| Review suggested follow-up prompts | See prompts framed for teacher use before class or student follow-up |
| Preserve learner-facing invisibility | Category-visible interpretation remains hidden from student-facing surfaces |

---

## 5. Minimum Access Model

- A protected teacher account is required to access teacher-support views.
- The product may use the same underlying authentication system for students and teachers, but teacher/admin roles and authorization rules are required.
- A teacher should only be able to view students they are explicitly authorized to review through a school, class, or roster relationship.
- If no authorized teacher-student relationship exists, the teacher-facing student view should not be accessible.
- Teacher-support interpretation must remain separate from learner-facing surfaces, even when both are backed by the same underlying session data.

---

## 6. Required Shared Inputs from the MVP Learner Flow

| Shared input | Why it is required for teacher support |
|--------------|----------------------------------------|
| Ordered node visits and thread context | Reconstructs how the learner moved through the chapter |
| Offer-set logging and question selections | Shows what was offered versus what the learner actually selected |
| Chapter and concept structure | Anchors interpretation to the current syllabus chapter |
| Subject weighting logic | Helps prioritize which relatively thin areas matter more for follow-up |
| Session timestamps and persistence state | Helps teachers review the latest chapter activity and continuity |
| Reflective Checkpoint events | Adds optional active-probing signals such as Try Now response quality, Not Sure Yet, Snooze, and Skip patterns |

These inputs are already implied by `docs/mvp-features-specification.md`, `docs/system-architecture.md`, `docs/measurement-and-experimentation.md`, and `docs/subject-weighting-specification.md`.

---

## 7. Reflective Checkpoint Interpretation in MVP

Reflective Checkpoints, student-facing as Sensemaking Pauses, are optional low-stakes active probes. Teacher surfaces may use them to add context to exploration-path interpretation, but they must not be shown as quiz grades, mastery scores, pass/fail outcomes, or definitive diagnoses.

| Checkpoint signal | MVP teacher interpretation | Surface guidance |
|-------------------|----------------------------|------------------|
| Try Now + strong response | Evidence of current sensemaking when invited to reflect | “Student gave a coherent reflection when prompted.” |
| Try Now + partial response | Possible follow-up area around the prompt focus | “Reflection was partial; consider probing gently.” |
| Try Now + likely misconception | Stronger but still probabilistic follow-up signal | “Prompted response suggested a possible misconception.” |
| Not Sure Yet | Metacognitive uncertainty, not failure | “Student marked uncertainty during reflection.” |
| Snooze | Temporary deferral / timing preference | Usually hidden unless repeated; never punitive |
| Skip | Agency/opt-out event | Do not surface individually; only repeated similar skips may be summarized cautiously |

Repeated opt-out patterns may be shown only with low-certainty language, for example: “The student often chose not to pause for reflection when the path shifted into prediction-style prompts.” Avoid language such as “refused,” “failed,” “avoided,” or “does not understand.”

Checkpoint evidence should be displayed separately from exploration coverage. It may qualify a suggested follow-up, but it should not reduce or overwrite the learner's dimensional coverage score.

---

## 8. Out of Scope for the Current MVP Teacher Surface

- full class-level analytics dashboards and ranked severity views
- teacher-authored question injection, intervention tooling, or content-library contribution workflows
- privilege tiers, approval workflows, trust scoring, and quality-monitoring systems
- exports, reporting workflows, or admin moderation operations
- learner-facing exposure of category-visible interpretation
- treating checkpoint responses or opt-outs as grades, mastery scores, or formal remediation triggers

---

## 9. Open Follow-Up Items

- the exact first teacher entry point: dedicated teacher dashboard versus a lighter chapter review surface
- the first version of teacher-student authorization linkage: roster import, school-managed assignment, or another constrained model
- the minimum teacher overview needed before drilling into a single student chapter view
- the minimum repetition threshold before opt-out patterns become visible enough to mention without overstating certainty

This document intentionally defines the current MVP boundary only. It does not settle the broader later-phase teacher dashboard, intervention, or admin-control architecture.

---

*Document Version 1.0 | Teacher Support MVP Specification*
*Platform: Path-Based Conceptual Exploration and Teacher-Support System*