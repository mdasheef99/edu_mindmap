# Phase 3 Offer-Set Logging — Software Design Document (SDD)

**Document Version**: 1.0 (active draft)  
**Status**: Completed locally — green Phase 3 M1 instrumentation slice  
**Phase / milestone**: Phase 3 — Core Loop Deepening, M1 offer-set logging completion  
**Live tracker**: `docs/planning/worklog-v4.md`

---

## 1. Increment Identity

| Field | Value |
|---|---|
| Increment name | Edge offer-set created/impression logging spine |
| Phase / milestone | Phase 3 — Core Loop Deepening, M1 |
| Owner | (developer) |
| Status | Active |

Goal: add the smallest deterministic backend slice that logs what was offered and what was shown before
the existing `offer_set_choice` endpoint records selected/dismissed outcomes. This prepares edge-`+`
branching without spending LLM credits or exposing measurement internals to students.

## 2. Source-of-Truth References

- `development-approach.md` §5 M1: offer-set logging must be complete before the core path can be
  interpreted; the M1 gate is event-only path reconstruction.
- `backend-architecture.md` §6.2: offer-set events are `offer_set_created`, `offer_set_impression`,
  and `offer_set_choice`; §6.2 points payload details to measurement §4.2–§4.6.
- `backend-architecture.md` §7.1 and §11: student API responses are from student-safe types only and
  must not expose analytic/measurement internals.
- `session-path-data-contract.md` §8–§9 and §14: offer-set exposure and selection history must be
  reconstructable from events.
- `measurement-and-experimentation.md` §4.1–§4.4: created/impression/choice are separate events with
  option metadata, propensities, probe flags, randomization metadata, and latency fields.
- `mvp-features-specification.md` Feature 4.4 and Success Criteria: offered question sets and
  selection/dismissal must be logged for exploration flows.
- `mobile-features-ai-integration.md` §6.5.1: edge `+` opens 3–6 student-safe generated questions;
  generation must remain organic-first and backend-owned.

## 3. Scope of Increment

**In scope:**
- `POST /v1/student/offer-sets/edge` returns a deterministic student-safe offer set for tests.
- The endpoint appends `offer_set_created` and `offer_set_impression` in one synchronous path.
- Event payloads include option IDs/text/order plus measurement-only fields: `propensity`, `is_probe`,
  and `randomization_id`.
- Student response hides propensities, probe flags, scores, and other measurement/analytic fields.
- No classify job is enqueued until the existing `offer_set_choice` selected path.

**Out of scope:**
- Live LLM generation, prompt assembly, and model-provider calls.
- Phrase-selection offer sets, child node creation, AI-path edge creation, and node response generation.
- Adaptive ranking, personalization, discovery-budget tuning, checkpoints, teacher dashboards, podcast.
- Persistence of `student_rm.current_offer_sets` beyond the event log in this slice.

## 4. Traceability Rows

| Feature | Endpoint | Events | Read Model | Worker Job | Table(s) |
|---|---|---|---|---|---|
| Edge offer-set logging | `POST /v1/student/offer-sets/edge` | `offer_set_created`, `offer_set_impression` | none in this slice | none | `events` |
| Existing choice logging | `POST /v1/student/offer-sets/{offer_set_id}/choices` | `offer_set_choice` | none in this slice | `classify` only when selected | `events`, `jobs` |

## 5. Module Placement & Import Rules

| Concern | Module | Rule |
|---|---|---|
| Student-safe request/response + event builders | `app.domain.student.offer_sets` | no analytic/category fields in response |
| API router | `app.api.student.offer_sets` | student domain + auth only; no projections/analytic imports |
| Runtime orchestration | `app.main.SessionRuntime` | append created + impression; no job enqueue |
| Event registry | `app.events.registry` | registered known event types only |

Existing import-linter contracts remain merge-blocking: `api/student` must not import `analytic`,
`classification`, or `projections`.

## 6. Event / Schema Deltas

- Register `offer_set_created` v1 and `offer_set_impression` v1.
- Required envelope fields include `actor_user_id`, `student_id`, `session_id`, `node_id`, and
  `offer_set_id`.
- Required payload fields:
  - `offer_set_id`, `session_id`, `source_node_id`, `launch_method`, `options`, `policy_name`,
    `policy_version`, `mode` for `offer_set_created`.
  - `offer_set_id`, `session_id`, `source_node_id`, `visible_option_ids`, `ui_positioning` for
    `offer_set_impression`.
- No database migration is required for this in-memory/event-registry slice.

## 7. API Contract

### `POST /v1/student/offer-sets/edge`

Request: `session_id`, `source_node_id`, optional `thread_context_id`.  
Response: `offer_set_id`, `session_id`, `source_node_id`, `launch_method`, and 3 student-safe options
with `option_id`, `text`, and `rank_position` only.

## 8. Test Plan

First red tests:
- T1: edge offer-set endpoint appends `offer_set_created` and `offer_set_impression` with propensities,
  rank/order, probe flags, randomization id, policy stamps, and latency fields.
- T2: student response hides `propensity`, `is_probe`, `randomization_id`, scores, and analytic words.
- T3: edge offer-set impression does not enqueue `classify`; existing selected `offer_set_choice` still
  enqueues exactly one classify job.

Validation gates:
- Focused integration tests for offer-set logging.
- Existing offer-choice/classify regression tests.
- Ruff format/check, MyPy, and full pytest after focused green.

## 9. Definition of Done

- Active SDD and canon point to this slice.
- Red tests fail before implementation and pass after implementation.
- Created/impression/choice are distinguishable event types.
- Measurement fields are present in event payloads but absent from student responses.
- No LLM/provider call is introduced.
- `docs/planning/worklog-v4.md` records the slice, validations, and remaining M1 work.