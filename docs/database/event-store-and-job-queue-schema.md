# Event Store and Job Queue Schema

**Document Version**: 1.0 (draft)  
**Status**: Current MVP schema baseline  
**Scope**: Append-only events and Postgres `SKIP LOCKED` jobs

---

## 1. Purpose

This document defines the durable event store and MVP async worker queue. It is grounded in `docs/planning/session-path-data-contract.md`, `docs/architecture/backend-architecture.md`, ADR-0002, ADR-0003, and ADR-0004.

## 2. Append-Only Event Store

The event store is the source of truth for session/path reconstruction, offer-set history, deletion evidence, checkpoint signals, teacher access, feedback, tenancy operations, and replay.

Table: `events`

| Column | Type | Required | Notes |
|---|---|---|---|
| `event_id` | UUID | yes | globally unique event identifier |
| `event_type` | text / enum | yes | registry-validated exact event name |
| `event_version` | integer | yes | payload schema version |
| `tenant_id` | UUID | yes | tenant isolation key |
| `actor_user_id` | UUID | conditional | authenticated actor when applicable |
| `student_id` | UUID | conditional | learner subject of event |
| `teacher_id` | UUID | conditional | teacher subject/actor for teacher events |
| `session_id` | UUID | conditional | required for session/path events |
| `exam_id` | UUID | conditional | session/curriculum context |
| `subject_id` | UUID | conditional | session/curriculum context |
| `chapter_id` | UUID | conditional | chapter-scoped sessions and projections |
| `chapter_analysis_id` | UUID | conditional | pinned chapter-analysis version when relevant |
| `concept_entry_id` | UUID | conditional | starting concept entry for session events |
| `node_id` | UUID | conditional | source/primary node where relevant |
| `edge_id` | UUID | conditional | edge events |
| `offer_set_id` | UUID | conditional | offer-set events and choices |
| `occurred_at` | timestamptz | yes | client/server occurrence time |
| `recorded_at` | timestamptz | yes | server append time |
| `idempotency_key` | text | conditional | mutation retry safety; unique per producer scope |
| `producer` | text | yes | `client`, `server`, `worker`, `admin`, `internal` |
| `payload` | JSONB | yes | registry-validated payload |
| `policy_name` | text | conditional | offer/checkpoint policy name |
| `policy_version` | text | conditional | offer/checkpoint policy version |
| `prompt_version` | text | conditional | generation/classification prompt version |
| `model_id` | text | conditional | LLM model identifier for model-derived artifacts |
| `projection_version` | text | conditional | projection/replay version for derived outputs |
| `replay_id` | UUID | conditional | replay batch identifier where applicable |

## 3. Append Rules

- Events are inserted only; no update/delete of historical rows.
- Event names and payloads are validated by an in-code registry before append.
- Client-submitted batches are whitelisted; clients cannot submit worker-only events such as `question_classified`.
- Student APIs must not expose raw event history.
- PII is prohibited in event payloads; use pseudonymous IDs and tenancy tables.

## 4. Event Families and Exact Names

| Family | Event Types |
|---|---|
| Session lifecycle | `session_started`, `session_resumed`, `app_backgrounded`, `app_foregrounded` |
| Canvas/node | `node_created`, `node_visited`, `node_deleted`, `viewport_changed` |
| Edges | `edge_created`, `edge_deleted` |
| Offer sets | `offer_set_created`, `offer_set_impression`, `offer_set_choice` |
| Phrase flow | `phrase_selected`, `phrase_offer_set_created`, `phrase_offer_set_choice` |
| Content | `node_content_generated`, `node_summary_compressed` |
| Classification | `question_classified` |
| Checkpoints | `checkpoint_offered`, `checkpoint_response` |
| Podcast | `podcast_requested`, `podcast_generated` |
| Teacher | `teacher_view_accessed`, `teacher_feedback` |
| B2B/admin | `roster_uploaded`, `membership_changed`, `consent_recorded`, `tenant_migration` |

## 5. JSONB Payload Requirements

Payloads must match the session/path contract fields where applicable:

| Event Area | Required Payload Concepts |
|---|---|
| Session | session identifier, learner identifier, exam/subject/chapter identifiers, concept entry identifier |
| Node | node identifier, node type, parent node identifier, creation source marker, content payload, position |
| Edge | edge identifier, source node identifier, target node identifier, edge type, creation label/trigger text |
| Offer choice | offer-set identifier, selected option identifier/text, dismissed/no-selection outcome, thread-context reference |
| Phrase | selected phrase, source excerpt, source node, thread-context reference |
| Deletion | root deleted node, cascade result, removed node IDs, removed edge IDs |
| Checkpoint | prompt identifier/text, action, optional response, trigger type, policy version |
| Podcast | phase, requested length, session/path snapshot reference, script/audio status |
| Teacher | view ID, panel/card references, projection version, feedback rating/reason |

## 6. Indexing Guidance

Required access patterns:

- tenant + session + recorded time
- tenant + student + chapter + recorded time
- tenant + event type + recorded time
- offer-set lookup by `offer_set_id`
- idempotency lookup by producer scope
- replay scans by recorded time and event type

Partitioning by recorded month may be introduced when measured event volume requires it.

## 7. Postgres Job Queue

Table: `jobs`

| Column | Type | Required | Notes |
|---|---|---|---|
| `job_id` | UUID | yes | primary identifier |
| `job_type` | text / enum | yes | `classify`, `compress`, `project`, `replay`, `podcast`, `chapter_analysis` |
| `tenant_id` | UUID | yes | tenant-scoped work item |
| `payload` | JSONB | yes | handler-specific validated payload |
| `status` | text / enum | yes | `queued`, `running`, `done`, `failed`, `dead` |
| `attempts` | integer | yes | incremented on claim/failure |
| `run_after` | timestamptz | yes | retry/backoff scheduling |
| `locked_at` | timestamptz | optional | set when claimed |
| `locked_by` | text | optional | worker identifier |
| `last_error` | text | optional | sanitized failure summary |
| `created_at` | timestamptz | yes | enqueue time |
| `updated_at` | timestamptz | yes | last state change |
| `idempotency_key` | text | conditional | prevents duplicate work for same trigger |

## 8. Job Types

| Job | Trigger | Writes Events | Writes Tables |
|---|---|---|---|
| `classify` | `offer_set_choice` | `question_classified` | `analytic_rm.question_classifications` |
| `compress` | `node_created` for AI/content nodes | `node_summary_compressed` | `student_rm.node_summaries` |
| `project` | new events past watermark | usually no | `analytic_rm.*`, selected student-safe projections |
| `replay` | internal/operator request | replayed derived events where needed | `analytic_rm.*` |
| `podcast` | `podcast_requested` | `podcast_generated` | `student_rm.podcasts` |
| `chapter_analysis` | content/ops trigger | pipeline/version events if used | chapter-analysis tables/projections |

## 9. Queue Rules

- Workers claim queued jobs with Postgres `SELECT ... FOR UPDATE SKIP LOCKED`.
- Event append and job enqueue should be transactional when one directly triggers the other.
- Handlers must be idempotent.
- Retry uses exponential backoff.
- Dead-letter after configured attempts, default 5 per ADR-0002.
- Redis/Celery are deferred; handlers must not depend on those transports.