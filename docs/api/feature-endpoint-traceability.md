# Feature Endpoint Traceability

**Document Version**: 1.0 (draft)  
**Trace Chain**: Feature → Endpoint → Event → Read Model → Worker Job

---

## 1. Purpose

This document proves that the API surface preserves Category Invisibility and Organic-First post-hoc classification while covering the current MVP feature hierarchy.

## 2. Boundary Summary

| Surface | Endpoint Family | Read Model | Analytic Visibility |
|---|---|---|---|
| Student | `/v1/student` | `student_rm` | none |
| Teacher | `/v1/teacher` | `analytic_rm` | consent-gated |
| Admin | future `/v1/admin` | tenancy/admin tables | operational only |
| Internal | future `/v1/internal` | events/jobs/projections | platform ops only |

## 3. Traceability Matrix

| Feature | Endpoint | Event | Read Model | Worker Job |
|---|---|---|---|---|
| Class/exam/subject/chapter navigation | `GET /v1/student/curriculum/*` | none | curriculum tables | none |
| Launchable chapter metadata | `GET /v1/student/chapters/{chapter_id}` | none | student-safe curriculum/chapter projection | none |
| Concept entry selection | `GET /v1/student/chapters/{chapter_id}/concept-entries` | none | student-safe chapter projection | none |
| Start session | `POST /v1/student/sessions` | `session_started` | `student_rm.sessions` | optional `project` |
| Resume session | `POST /v1/student/sessions/{session_id}/resume` | `session_resumed` | `student_rm.sessions` | none |
| Fetch session state | `GET /v1/student/sessions/{session_id}` | none | `student_rm` only | none |
| Batch client events | `POST /v1/student/sessions/{session_id}/events` | whitelisted client events | event store | `project` as needed |
| Create node | `POST /v1/student/sessions/{session_id}/nodes` | `node_created` | `student_rm.nodes` | optional `compress`, `project` |
| Visit node | batch events endpoint | `node_visited` | event store | `project` |
| Update node | `PATCH /v1/student/sessions/{session_id}/nodes/{node_id}` | canvas/content event | `student_rm.nodes` | optional `project` |
| Delete AI-path node | `DELETE /v1/student/sessions/{session_id}/nodes/{node_id}` | `node_deleted`, `edge_deleted` | `student_rm.nodes`, `student_rm.edges` | `project` |
| Create manual reference | `POST /v1/student/sessions/{session_id}/edges` | `edge_created` | `student_rm.edges` | `project` |
| Remove manual reference | `DELETE /v1/student/sessions/{session_id}/edges/{edge_id}` | `edge_deleted` | `student_rm.edges` | `project` |
| Phrase offer set | `POST /v1/student/offer-sets/phrase` | `phrase_selected`, `phrase_offer_set_created`, `offer_set_impression` | `student_rm.current_offer_sets` | none |
| Edge `+` offer set | `POST /v1/student/offer-sets/edge` | `offer_set_created`, `offer_set_impression` | `student_rm.current_offer_sets` | none |
| Select offer-set option | `POST /v1/student/offer-sets/{offer_set_id}/choices` | `offer_set_choice`, `phrase_offer_set_choice` when phrase-launched, `node_created`, `edge_created` | `student_rm.nodes`, `student_rm.edges` | `classify`, `compress`, `project` |
| Dismiss offer set | same choice endpoint | `offer_set_choice`, `phrase_offer_set_choice` when phrase-launched, with no-selection outcome | `student_rm.current_offer_sets` | `project` only; no `classify`/`compress` |
| Post-hoc classification | no student endpoint | `question_classified` | `analytic_rm.question_classifications` | `classify` |
| Analytic projection update | no student endpoint | derived from event stream | `analytic_rm` | `project` |
| Poll checkpoint | `GET /v1/student/sessions/{session_id}/checkpoint` | `checkpoint_offered` when delivered | student-safe checkpoint state | upstream `classify`, `project` |
| Submit checkpoint response | `POST /v1/student/sessions/{session_id}/checkpoint/responses` | `checkpoint_response` | event store/checkpoint projection | `project` |
| Request podcast script | `POST /v1/student/sessions/{session_id}/podcasts` | `podcast_requested` phase `script` | `student_rm.podcasts` | `podcast` |
| Confirm podcast audio | `POST /v1/student/podcasts/{podcast_id}/audio` | `podcast_requested` phase `audio` | `student_rm.podcasts` | `podcast` |
| Audio ready | worker completion | `podcast_generated` | `student_rm.podcasts` | `podcast` |
| PYQ list/detail | `GET /v1/student/chapters/{chapter_id}/pyq`, `GET /v1/student/pyq/{question_id}` | none | PYQ/curriculum tables | none |
| Add PYQ to board | `POST /v1/student/sessions/{session_id}/pyq/{question_id}/nodes` | `node_created` | `student_rm.nodes` | optional `project` |
| Teacher classes | `GET /v1/teacher/classes` | none | tenancy/class tables | none |
| Teacher roster overview | `GET /v1/teacher/classes/{class_id}/students` | none | tenancy + `analytic_rm` participation projections | none |
| Chapter landscape | `GET /v1/teacher/chapters/{chapter_id}/landscape` | `teacher_view_accessed` | `analytic_rm` + chapter analysis | none |
| Student chapter review | `GET /v1/teacher/students/{student_id}/chapters/{chapter_id}/review` | `teacher_view_accessed` | `analytic_rm` | none |
| Checkpoint interpretation | review panel | `checkpoint_offered`, `checkpoint_response` | `analytic_rm` checkpoint projection | `project` |
| Suggested follow-ups | review panel | `teacher_view_accessed` | derived from `analytic_rm` + P6 evidence | none in request path |
| Class aggregate | `GET /v1/teacher/classes/{class_id}/chapters/{chapter_id}/aggregate` | `teacher_view_accessed` | `analytic_rm.class_aggregates` | `project` |
| Teacher feedback | `POST /v1/teacher/feedback` | `teacher_feedback` | feedback/audit tables + event store | optional `project` |
| Institutional Activation | Future/Deferred admin/auth endpoint | `membership_changed` if activation changes membership state | tenancy/membership tables | optional `project` |
| Consent Recording | Future/Deferred admin/auth endpoint | `consent_recorded` | consent tables + projection gates | `project`, `replay` on withdrawal |
| B2C to B2B Migration | Future/Deferred admin/internal endpoint | `tenant_migration`, `membership_changed` | tenancy/membership tables | `replay` if historical inclusion changes |
| Roster upload prerequisite | future `/v1/admin` | `roster_uploaded` | tenancy/class membership tables | `project` |
| Membership change prerequisite | future `/v1/admin` | `membership_changed` | tenancy/class membership tables | `project` |

## 4. Organic-First Proof

The student sees only organic, category-neutral options. After the learner selects an option, the backend appends `offer_set_choice` and, for phrase-launched flows, `phrase_offer_set_choice`; only selected choices enqueue `classify`. Dismissed/no-selection outcomes are projected for exposure history but are not classified.

Classification never blocks the student response and never returns through `/v1/student`.

## 5. Checkpoint Post-Hoc Proof

Checkpoints are polled with `GET /v1/student/sessions/{session_id}/checkpoint`. They are not embedded in normal session-state responses. Eligibility depends on prior async classification/projection, and delivered prompts remain category-neutral and optional.

## 6. B2B Boundary Proof

Teacher endpoints require tenant, roster, assignment, membership, and consent state. Exact roster upload, activation code, teacher invitation, consent recording, tenant provisioning, and internal replay contracts are deferred to future admin/internal API specs.

The student learning API assumes active context has already been resolved by the backend. It does not trust mobile-supplied tenant/role/membership claims and does not define activation-code or roster-management contracts.

Teacher-assigned checkpoints are not part of the MVP API surface. Checkpoints are system-generated, post-hoc, optional, and category-neutral.

## 7. Legacy Rejection Proof

No endpoint in these specs requires client-side AI provider calls, client provider credentials, Redis/Celery for MVP, TimescaleDB for MVP, student raw-event export, teacher grading/ranking/mastery, or offline queued sync.