# Schema Traceability and Validation

**Document Version**: 1.0 (draft)  
**Status**: Current MVP validation baseline  
**Trace Chain**: Feature → Endpoint → Event → Read Model → Worker Job → Table(s)

---

## 1. Purpose

This document extends `docs/api/feature-endpoint-traceability.md` into the database layer and defines validation gates for Category Invisibility, session-path contract alignment, tenancy, consent, and async jobs.

## 2. Database Traceability Matrix

| Feature | Endpoint | Event | Read Model | Worker Job | Table(s) |
|---|---|---|---|---|---|
| Curriculum navigation | `GET /v1/student/curriculum/*` | none | curriculum | none | `curriculum_classes`, `exams`, `subjects`, `chapters` |
| Launchable chapter metadata | `GET /v1/student/chapters/{chapter_id}` | none | student-safe curriculum | none | `chapters`, `chapter_analysis_versions`, `concept_entries` |
| Start session | `POST /v1/student/sessions` | `session_started` | `student_rm` | optional `project` | `events`, `student_rm.sessions` |
| Resume session | `POST /v1/student/sessions/{session_id}/resume` | `session_resumed` | `student_rm` | none | `events`, `student_rm.sessions` |
| Fetch session state | `GET /v1/student/sessions/{session_id}` | none | `student_rm` | none | `student_rm.sessions`, `student_rm.nodes`, `student_rm.edges`, `student_rm.podcasts` |
| Batch client events | `POST /v1/student/sessions/{session_id}/events` | whitelisted events | event store | `project` | `events`, `jobs` |
| Create node | `POST /v1/student/sessions/{session_id}/nodes` | `node_created` | `student_rm` | optional `compress`, `project` | `events`, `student_rm.nodes`, `jobs` |
| Delete node cascade | `DELETE /v1/student/sessions/{session_id}/nodes/{node_id}` | `node_deleted`, `edge_deleted` | `student_rm` | `project` | `events`, `student_rm.nodes`, `student_rm.edges`, `jobs` |
| Manual reference create | `POST /v1/student/sessions/{session_id}/edges` | `edge_created` | `student_rm` | `project` | `events`, `student_rm.edges`, `jobs` |
| Manual reference remove | `DELETE /v1/student/sessions/{session_id}/edges/{edge_id}` | `edge_deleted` | `student_rm` | `project` | `events`, `student_rm.edges`, `jobs` |
| Phrase offer set | `POST /v1/student/offer-sets/phrase` | `phrase_selected`, `phrase_offer_set_created`, `offer_set_impression` | `student_rm` | none | `events`, `student_rm.current_offer_sets` |
| Edge `+` offer set | `POST /v1/student/offer-sets/edge` | `offer_set_created`, `offer_set_impression` | `student_rm` | none | `events`, `student_rm.current_offer_sets` |
| Offer choice | `POST /v1/student/offer-sets/{offer_set_id}/choices` | `offer_set_choice`, `node_created`, `edge_created` | `student_rm`, later `analytic_rm` | `classify`, `compress`, `project` | `events`, `student_rm.nodes`, `student_rm.edges`, `jobs` |
| Post-hoc classification | no student endpoint | `question_classified` | `analytic_rm` | `classify` | `events`, `analytic_rm.question_classifications` |
| Checkpoint poll | `GET /v1/student/sessions/{session_id}/checkpoint` | `checkpoint_offered` when delivered | student-safe checkpoint state | upstream `classify`, `project` | `events`, optional `student_rm.checkpoint_offers` |
| Checkpoint response | `POST /v1/student/sessions/{session_id}/checkpoint/responses` | `checkpoint_response` | checkpoint projections | `project` | `events`, `analytic_rm.checkpoint_signals`, `jobs` |
| Podcast script | `POST /v1/student/sessions/{session_id}/podcasts` | `podcast_requested` phase `script` | `student_rm` | `podcast` | `events`, `student_rm.podcasts`, `jobs` |
| Podcast audio | `POST /v1/student/podcasts/{podcast_id}/audio` | `podcast_requested` phase `audio`, `podcast_generated` | `student_rm` | `podcast` | `events`, `student_rm.podcasts`, `media_assets`, `jobs` |
| PYQ list/detail | PYQ GET endpoints | none | curriculum/PYQ | none | `pyq_questions`, `pyq_solutions`, `pyq_topic_links` |
| Add PYQ to board | `POST /v1/student/sessions/{session_id}/pyq/{question_id}/nodes` | `node_created` | `student_rm` | optional `project` | `events`, `student_rm.nodes`, `pyq_questions` |
| Teacher classes | `GET /v1/teacher/classes` | none | operational | none | `classes`, `teaching_assignments`, `memberships` |
| Teacher roster overview | `GET /v1/teacher/classes/{class_id}/students` | none | `analytic_rm` + operational | none | `class_memberships`, `consent_records`, `analytic_rm.student_engagement_profiles` |
| Chapter landscape | `GET /v1/teacher/chapters/{chapter_id}/landscape` | `teacher_view_accessed` | `analytic_rm` | none | `events`, chapter-analysis tables, `analytic_rm.teacher_support_views` |
| Student chapter review | teacher review endpoint | `teacher_view_accessed` | `analytic_rm` | none | `events`, `analytic_rm.teacher_support_views`, `analytic_rm.coverage_by_concept` |
| Class aggregate | teacher aggregate endpoint | `teacher_view_accessed` | `analytic_rm` | `project` | `events`, `analytic_rm.class_aggregates` |
| Teacher feedback | `POST /v1/teacher/feedback` | `teacher_feedback` | audit/analytic | optional `project` | `events`, feedback/audit table |
| Institutional activation | future admin/auth endpoint | `membership_changed` if state changes | operational | optional `project` | `activation_codes`, `provisional_accounts`, `memberships`, `events` |
| Consent recording | future admin/auth endpoint | `consent_recorded` | operational/projection gates | `project`, `replay` on withdrawal | `consent_records`, `events`, `jobs` |
| B2C to B2B migration | future admin/internal endpoint | `tenant_migration`, `membership_changed` | operational | `replay` if history inclusion changes | `tenant_migrations`, `memberships`, `events`, `jobs` |

## 3. Category Invisibility Validation

Validation gate: no table in `student_rm` may contain analytic columns.

Forbidden terms in `student_rm` column names by default:

- `dimension`, `score`, `coverage`, `classification`, `entropy`, `dispersion`, `confidence`
- `gap`, `profile`, `vector`, `weight`, `propensity`, `probe`
- `teacher`, `analytic`, `projection_reason`

Required checks:

- `/v1/student` response DTOs map only to `student_rm`, curriculum/PYQ, or student-safe generated artifacts.
- `/v1/student` has no raw event-history endpoint.
- `student_rm.checkpoint_offers`, if used, stores only prompt text/status and no trigger vectors.
- Teacher follow-ups and gap cards exist only in `analytic_rm`.

## 4. Session-Path Contract Alignment

| Contract Field | DB Location | Event |
|---|---|---|
| session identifier | `events.session_id`, `student_rm.sessions.session_id` | `session_started`, `session_resumed` |
| learner identifier | `events.student_id`, `student_rm.sessions.student_user_id` | session/path events |
| chapter identifier | `events.chapter_id`, `student_rm.sessions.chapter_id` | session/path events |
| concept entry identifier | `student_rm.sessions.concept_entry_id` | `session_started` |
| node identifier | `events.node_id`, `student_rm.nodes.node_id` | `node_created`, `node_visited`, `node_deleted` |
| node type | `student_rm.nodes.node_type`, event payload | `node_created` |
| edge type | `student_rm.edges.edge_type`, event payload | `edge_created`, `edge_deleted` |
| offer-set identifier | `events.offer_set_id`, `student_rm.current_offer_sets.offer_set_id` | offer-set events |
| selected option | event payload | `offer_set_choice`, `phrase_offer_set_choice` |
| thread-context reference | event payload | `phrase_selected`, offer-set choice events |
| deletion cascade result | event payload | `node_deleted`, `edge_deleted` |

## 5. Tenant and RLS Validation

Checklist:

- every tenant-scoped table includes `tenant_id`
- every job includes `tenant_id`
- every event includes `tenant_id`
- teacher queries require active teaching assignment and class membership check
- student queries require resolved active student context
- consent-gated analytic projections exclude withdrawn/pending students
- application-level tenancy is the mechanism; RLS is the backstop
- mobile-supplied `tenant_id` is never authoritative

## 6. Job Validation

Each job definition must specify:

- trigger event or operator action
- payload schema and idempotency key
- writes-events behavior
- target tables
- retry/dead-letter policy
- consent gate if analytic

`classify`, `project`, and `replay` must check behavioral-analytics consent before writing or preserving teacher-visible analytic outputs.

## 7. Legacy Exclusion Validation

Schema review must reject designs that require Redis, Celery, TimescaleDB, shared student/analytic tables, client-side AI credentials, or broad offline queued sync for MVP.