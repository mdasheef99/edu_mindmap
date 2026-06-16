# Teacher API Specification

**Document Version**: 1.0 (draft)  
**Router**: `/v1/teacher`  
**Read Model**: `analytic_rm` projections

---

## 1. Purpose

The teacher API powers the B2B teacher dashboard. It returns protected, probabilistic, evidence-linked support views derived from `analytic_rm` projections.

The teacher API is not an intervention, grading, diagnostic, ranking, or mastery-scoring API.

## 2. Access and Consent Rules

Every endpoint requires:

- authenticated teacher user
- resolved tenant context
- active tenant membership
- active teaching assignment for class-scoped data
- active student class membership for student-scoped data
- active behavioral-analytics consent for analytic panels

If consent is pending or withdrawn, roster context may render consent state, but analytic panels are withheld.

## 3. Upstream B2B/Admin Prerequisites

This spec assumes upstream admin/internal operations already provisioned:

- tenant and institution
- classes
- roster memberships
- student activation
- consent records
- teacher verification
- teaching assignments

Those operations belong to future `docs/api/admin-api-spec.md` and `docs/api/internal-api-spec.md`. This document fixes the boundary but defers those contracts.

Teacher APIs assume institutional context and behavioral-analytics consent have already been resolved by upstream onboarding operations. They do not redeem activation codes, upload rosters, record consent, or mutate memberships. Teacher visibility never implies learner-facing category visibility.

Teacher-assigned checkpoints are explicitly rejected for the MVP. Checkpoints remain system-generated, optional, category-neutral, and post-hoc to protect the Organic-First exploration model.

## 4. Common Response Metadata

Teacher projection responses should include:

| Field | Meaning |
|---|---|
| `projection_version` | Projection code/data version |
| `generated_at` | When the projection/view was generated |
| `source_event_recorded_at_max` | Latest event included |
| `is_stale` | Whether configured freshness threshold is exceeded |
| `consent_state` | `active`, `pending`, or `withdrawn` |
| `small_cohort_suppressed` | True when K suppression hides aggregate values |

## 5. V1 Class Overview

| Method | Path | Purpose | Events | Read Model |
|---|---|---|---|---|
| `GET` | `/v1/teacher/classes` | List active assigned classes | none | tenancy/class tables |
| `GET` | `/v1/teacher/classes/{class_id}/students` | Roster overview with activity, chapters touched, participation, consent state | none | tenancy + `analytic_rm` participation projections |

Roster output is alphabetical, never ranked by severity or inferred need.

## 6. V2 Chapter Landscape

| Method | Path | Purpose | Events | Read Model |
|---|---|---|---|---|
| `GET` | `/v1/teacher/chapters/{chapter_id}/landscape` | Chapter availability, concept richness, low-material flags, evidence, prior-conceptions backlog, effective weights | `teacher_view_accessed` | `analytic_rm` + chapter analysis outputs |

Rules:

- chapter-level only
- prior conceptions remain UNVALIDATED unless explicitly validated elsewhere
- no student ranking or diagnostic language

## 7. V3 Student Chapter Review

| Method | Path | Purpose | Events | Read Model |
|---|---|---|---|---|
| `GET` | `/v1/teacher/students/{student_id}/chapters/{chapter_id}/review` | Panelized student/chapter support view | `teacher_view_accessed` | `analytic_rm` |

Optional query parameters: `class_id`, `panels`, `as_of`.

Supported panels:

| Panel | Description | Source |
|---|---|---|
| `path` | Ordered exploration path and offer-set exposure/choice history | event-derived projection |
| `profile` | Cumulative engagement profile, trajectory, velocity | `student_engagement_profiles` |
| `attention_gaps` | Flagged concept/dimension cells with evidence | `coverage_by_concept` + chapter availability |
| `gap_persistence` | Persistent vs catching-up gaps | velocity/projection logic |
| `checkpoints` | Try Now / Not Sure Yet / Snooze / Skip interpretation | `checkpoint_offered`, `checkpoint_response` |
| `followups` | Teacher-use suggested prompts | derived from P6 evidence |
| `unexplored_connections` | Connection statuses | topology projections + offer-set log |

Request path must not make LLM calls. Suggested follow-ups are derived from projected evidence.

## 8. V4 Class Chapter Aggregate

| Method | Path | Purpose | Events | Read Model |
|---|---|---|---|---|
| `GET` | `/v1/teacher/classes/{class_id}/chapters/{chapter_id}/aggregate` | Distribution shapes, coverage spread, checkpoint mix, common gaps/connections | `teacher_view_accessed` | `analytic_rm.class_aggregates` |

V4 is a bounded B2B extension and may be staged after the first Walking Skeleton. Every aggregate cell applies K=5 small-cohort suppression. No endpoint may return ranked student lists.

## 9. Feedback

| Method | Path | Purpose | Events | Read Model |
|---|---|---|---|---|
| `POST` | `/v1/teacher/feedback` | Capture usefulness feedback on teacher insight cards | `teacher_feedback` | feedback/audit tables + event store |

Allowed ratings: `useful`, `not_useful`.

Allowed not-useful reasons: `not_relevant`, `already_knew_this`, `unclear`, `wrong_for_this_student`.

Feedback payloads should reference `view_id`, `panel_id`, `card_ref`, `chapter_id`, optional `student_id`, `projection_version`, and optional free text.

## 10. Claim Boundaries

Teacher responses may say patterns are worth attention. They must not assert:

- mastery or lack of mastery
- grades or pass/fail outcomes
- diagnoses
- ranked severity
- individual opt-out surveillance
- per-question dimensional truth

Checkpoint signals stay separate from coverage and are interpreted cautiously.