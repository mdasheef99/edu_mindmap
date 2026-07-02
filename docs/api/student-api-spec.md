# Student API Specification

**Document Version**: 1.0 (draft)  
**Router**: `/v1/student`  
**Read Model**: `student_rm` only

---

## 1. Purpose

The student API supports curriculum navigation, chapter-scoped sessions, bounded canvas state, AI branching, checkpoint polling, podcast generation, PYQ access, and student-safe resume/offline reopening.

The student API must preserve Category Invisibility. It never returns analytic dimensions, scores, coverage, classifications, teacher labels, or raw event history.

## 2. Authorization and Context

Every endpoint requires an authenticated user and resolved tenant context. A session is always scoped to one tenant, one learner, one chapter, and one pinned `chapter_analysis_id`.

## 3. B2C/B2B Active Context Assumption

The `/v1/student` router starts after the backend has resolved the learner's active context. The learning endpoints remain identical for individual and institutional learners.

| Context | Backend-provided state | Student API behavior |
|---|---|---|
| B2C / individual | individual tenant context, active student membership, manually selected curriculum preferences | learner chooses class/exam/subject/chapter through curriculum endpoints |
| B2B / institutional | institutional `tenant_id`, class membership, consent state, roster-linked curriculum defaults | class/curriculum may be pre-filled or locked by school assignment |

The mobile client must not decide the authoritative `tenant_id`, role, class membership, or consent state. FastAPI resolves those from server-side identity, membership, roster, and consent records.

`/v1/student` does not define or handle:

- activation code redemption
- roster upload or roster binding
- class membership changes
- consent-recording workflows
- teacher invitation or assignment
- B2C to B2B tenant migration

Those contracts belong to future admin/auth/internal API specs. B2B context never changes Category Invisibility: student endpoints still return only student-safe data from `student_rm`.

## 4. Curriculum Endpoints

| Method | Path | Purpose | Source |
|---|---|---|---|
| `GET` | `/v1/student/curriculum/classes` | List supported class/syllabus levels | curriculum tables |
| `GET` | `/v1/student/curriculum/exams` | List exams filtered by class | curriculum tables |
| `GET` | `/v1/student/curriculum/subjects` | List subjects filtered by class/exam | curriculum tables |
| `GET` | `/v1/student/curriculum/chapters` | List launchable chapters | curriculum + chapter analysis status |
| `GET` | `/v1/student/chapters/{chapter_id}` | Student-safe chapter metadata | curriculum tables |
| `GET` | `/v1/student/chapters/{chapter_id}/concept-entries` | Supported concept entry points | student-safe chapter projection |

Student chapter responses must not include dimensional availability, richness profiles, gap notes, or teacher evidence.

## 5. Session Endpoints

| Method | Path | Purpose | Events | Jobs |
|---|---|---|---|---|
| `GET` | `/v1/student/dashboard` | Continue Learning and recent sessions | none | none |
| `POST` | `/v1/student/sessions` | Start chapter-scoped session | `session_started`, optional `node_created` | optional `project` |
| `GET` | `/v1/student/sessions/{session_id}` | Fetch student-safe session state | none | none |
| `POST` | `/v1/student/sessions/{session_id}/resume` | Resume session | `session_resumed` | none |
| `POST` | `/v1/student/sessions/{session_id}/events` | Batch ingest whitelisted client events | whitelisted only | `project` as needed |
| `POST` | `/v1/student/sessions/{session_id}/close` | Close or mark inactive | lifecycle event | optional `project` |

Session state may include sessions, nodes, edges, summaries, current offer sets, and podcast status. It must not embed checkpoint eligibility; checkpoints are polled separately.

### `GET /sessions/{session_id}` — Canvas Payload Shape

Returns a `StudentSession` envelope extended with a `canvas` field reconstructed from the
event log via `active_canvas_from_events`. Canvas fields are student-safe (`student_rm` only):

```
{
  "session_id": uuid,
  "status": "active" | "inactive" | "closed",
  "last_active_node_id": uuid | null,
  "started_at": timestamp,
  "last_active_at": timestamp,
  "canvas": {
    "nodes": [{ "node_id": uuid, "node_type": str, "content": str,
                "position_x": float | null, "position_y": float | null,
                "thread_context_id": uuid | null }],
    "edges": [{ "edge_id": uuid, "source_node_id": uuid, "target_node_id": uuid,
                "edge_kind": "ai_path" | "manual_reference", "label": str | null }],
    "viewport": { "scale": float, "translate_x": float, "translate_y": float }
  }
}
```

Canvas fields must never include analytic dimensions, classification labels, coverage scores,
propensities, or any `analytic_rm` data. If no canvas events exist yet, `canvas.nodes` and
`canvas.edges` are empty arrays and `canvas.viewport` holds the default transform.

### `POST /sessions/{session_id}/events` — Client Event Whitelist

Only the following event types may be submitted by the `client` producer. All others are
rejected with `400 Bad Request`.

| Event type | Required payload fields | `visit_source` allowed values |
|---|---|---|
| `node_visited` | `node_id`, `session_id`, `visit_source` | `"tap"`, `"edge_plus"`, `"session_resume"` |
| `viewport_changed` | `session_id`, `scale`, `translate_x`, `translate_y`, `visible_node_ids` | n/a |

Validation rules applied at the endpoint boundary (beyond `validate_event` presence checks):
- `visit_source` must be one of the three allowed string literals.
- `scale` must be a float in `[CANVAS_MIN_ZOOM, CANVAS_MAX_ZOOM]`.
- `visible_node_ids` must be an array of UUID strings.
- Extra payload fields not in the whitelist spec are stripped (not stored).
- Worker-only event types (`question_classified`) submitted by `client` → `403 Forbidden`.

Response: `202 Accepted` with `{ "accepted": N, "rejected": [...] }` where N is the count of events successfully
appended. Individual validation failures within a batch are rejected; successfully validated
events in the same batch are still appended (partial acceptance).

## 6. Node Endpoints

| Method | Path | Purpose | Events | Jobs |
|---|---|---|---|---|
| `POST` | `/v1/student/sessions/{session_id}/nodes` | Create `ai`, `text`, `image`, or `video` node | `node_created` | `compress`, `project` as needed |
| `GET` | `/v1/student/sessions/{session_id}/nodes/{node_id}` | Fetch node | none | none |
| `PATCH` | `/v1/student/sessions/{session_id}/nodes/{node_id}` | Update position/title/media metadata | canvas/content event where applicable | optional `project` |
| `DELETE` | `/v1/student/sessions/{session_id}/nodes/{node_id}` | Confirmed deletion and AI-path descendant cascade | `node_deleted`, related `edge_deleted` | `project` |
| `POST` | `/v1/student/sessions/{session_id}/nodes/{node_id}/summary` | Request student-safe summary | content/summary event | `compress` |

Deletion is destructive in `student_rm` but append-only historically. `node_deleted` records the root deleted node and cascade result. Cascade edge removals use `edge_deleted` with `deletion_cause: node_cascade`.

## 7. Edge Endpoints

| Method | Path | Purpose | Events |
|---|---|---|---|
| `POST` | `/v1/student/sessions/{session_id}/edges` | Create manual reference link | `edge_created` |
| `DELETE` | `/v1/student/sessions/{session_id}/edges/{edge_id}` | Remove manual reference link | `edge_deleted` with `deletion_cause: user_action` |

Allowed edge types are `ai_path` and `manual_reference`. Student-created manual links are not path progression.

## 8. AI Offer-Set Workflow Endpoints

Workflow endpoints are allowed here because they represent generation acts owned by the backend LLM Gateway.

| Method | Path | Purpose | Events | Jobs |
|---|---|---|---|---|
| `POST` | `/v1/student/offer-sets/phrase` | Generate phrase-conditioned options | `phrase_selected`, `phrase_offer_set_created`, `offer_set_impression` | none |
| `POST` | `/v1/student/offer-sets/edge` | Generate edge `+` follow-up options | `offer_set_created`, `offer_set_impression` | none |
| `POST` | `/v1/student/offer-sets/{offer_set_id}/choices` | Record selected/dismissed outcome and create child path if selected | `offer_set_choice`, optional `phrase_offer_set_choice`, `node_created`, `edge_created` | `classify`, `compress`, `project` |

Offer-set responses contain only `offer_set_id`, student-safe option IDs/text, source node reference, launch method, and expiry/status. They never contain analytic labels, propensities, probe flags, or coverage hints.

Classification is post-hoc: `classify` is enqueued only after `offer_set_choice` and never blocks the student response.

## 9. Reflective Checkpoint Endpoints

Checkpoints are dedicated, polled endpoints. They are not embedded in synchronous session-state responses.

| Method | Path | Purpose | Events | Jobs |
|---|---|---|---|---|
| `GET` | `/v1/student/sessions/{session_id}/checkpoint` | Poll for student-safe checkpoint availability | `checkpoint_offered` only when delivered | upstream `classify`, `project` |
| `POST` | `/v1/student/sessions/{session_id}/checkpoint/responses` | Submit action/response | `checkpoint_response` | `project` |

Allowed actions: `try_now`, `not_sure_yet`, `snooze`, `skip`.

Checkpoint prompts are optional, category-neutral, non-blocking, and never framed as grades, mastery, pass/fail, or remediation.

Teacher-assigned checkpoints are explicitly out of MVP scope. Checkpoints remain system-generated, post-hoc, optional, and Organic-First compatible; `/v1/teacher` cannot assign checkpoint prompts to individual learners.

## 10. Podcast Endpoints

Podcast generation is a two-phase async lifecycle: `script_ready` → user confirmation → `audio_ready`.

| Method | Path | Purpose | Events | Jobs |
|---|---|---|---|---|
| `POST` | `/v1/student/sessions/{session_id}/podcasts` | Request script from session/path snapshot | `podcast_requested` with phase `script` | `podcast` |
| `GET` | `/v1/student/podcasts/{podcast_id}` | Get status and script preview/audio status | none | none |
| `POST` | `/v1/student/podcasts/{podcast_id}/audio` | Confirm script and request audio | `podcast_requested` with phase `audio` | `podcast` |
| `GET` | `/v1/student/podcasts/{podcast_id}/audio` | Retrieve playable audio when ready | none | none |

Statuses: `script_generating`, `script_ready`, `audio_generating`, `audio_ready`, `failed`, `cancelled`.

The worker appends `podcast_generated` when audio is ready. Offline podcast playback/download is out of MVP scope.

## 11. PYQ Endpoints

| Method | Path | Purpose | Events |
|---|---|---|---|
| `GET` | `/v1/student/chapters/{chapter_id}/pyq` | List previous year questions | none |
| `GET` | `/v1/student/pyq/{question_id}` | Get PYQ detail | none |
| `POST` | `/v1/student/sessions/{session_id}/pyq/{question_id}/nodes` | Add PYQ as node | `node_created` |

## 12. Offline Boundary

The API supports fetching student-safe session state for local persistence and reopen. MVP excludes offline AI generation, queued sync, conflict resolution, offline video behavior, and offline podcast playback. Offline dwell/revisit events are not buffered in MVP.