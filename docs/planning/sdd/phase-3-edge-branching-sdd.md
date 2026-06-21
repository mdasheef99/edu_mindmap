# Phase 3 Edge Branching — Software Design Document (SDD)

**Document Version**: 1.0 (active draft)  
**Status**: Completed locally — green Phase 3 M1 edge `+` branching slice  
**Phase / milestone**: Phase 3 — Core Loop Deepening, M1 edge `+` branching  
**Live tracker**: `docs/planning/worklog-v4.md`

---

## 1. Increment Identity

| Field | Value |
|---|---|
| Increment name | Selected edge offer creates deterministic child path |
| Phase / milestone | Phase 3 — Core Loop Deepening, M1 |
| Owner | (developer) |
| Status | Active |

Goal: extend the already-green edge offer-set logging and choice spine so a selected edge `+` option
creates a deterministic child AI node and an `ai_path` edge, while dismissed choices remain logging-only.
The slice proves event-only path reconstruction can distinguish offer exposure, selection, and child path
creation without calling a live LLM.

## 2. Source-of-Truth References

- `development-approach.md` §5 M1: Core Loop Deepening includes edge-`+` branching; the gate is one
  full session path reconstructable from events alone.
- `backend-architecture.md` §6.2: canvas events include `node_created` and `edge_created`; offer-set
  events include `offer_set_choice`; §8.2 keeps synchronous student flow independent of workers.
- `backend-architecture.md` §7.1 and §11: `/v1/student` uses student-safe domain types only and must
  never expose analytic/category fields.
- `session-path-data-contract.md` §8–§9 and §14: follow-up question selections, source/target node
  identifiers, thread context, and AI-path progression must be reconstructable from events.
- `docs/api/student-api-spec.md` §8: selected `offer_set_choice` creates child path with
  `node_created` and `edge_created`; dismissed outcomes do not branch.
- `docs/mobile-features-ai-integration.md` §6.5.1: edge `+` generates student-safe follow-up
  questions; this slice keeps generation deterministic and backend-owned.

## 3. Scope of Increment

**In scope:**
- Extend `POST /v1/student/offer-sets/{offer_set_id}/choices` selected path.
- Append `offer_set_choice`, `node_created`, and `edge_created` atomically for selected outcomes.
- Include source node, child node, selected option, thread context, and `edge_kind: ai_path` in events.
- Return a student-safe response that may include child node/edge IDs and fixture child content.
- Preserve classify enqueue for selected choices after events are appended.
- Preserve dismissed behavior: `offer_set_choice` only, no child path, no classify job.

**Out of scope:**
- Live LLM generation, prompt assembly, model/provider calls, and token usage.
- Rich student board projection for nodes/edges beyond the event log.
- Phrase-selection branching, manual reference links, deletion cascade, podcast/checkpoint behavior.
- Teacher/analytic projections and classification completion.

## 4. Traceability Rows

| Feature | Endpoint | Events | Read Model | Worker Job | Table(s) |
|---|---|---|---|---|---|
| Selected edge child path | `POST /v1/student/offer-sets/{offer_set_id}/choices` | `offer_set_choice`, `node_created`, `edge_created` | none in this slice | `classify` queued | `events`, `jobs` |
| Dismissed edge offer | same | `offer_set_choice` | none | none | `events` |

## 5. Module Placement & Import Rules

| Concern | Module | Rule |
|---|---|---|
| Student-safe choice request/response + event builders | `app.domain.student.offer_choices` | no analytic/category fields |
| API router | `app.api.student.offer_choices` | student domain + auth only |
| Runtime orchestration | `app.main.SessionRuntime` | verify session ownership, append events, enqueue selected classify |
| Event registry | `app.events.registry` | known event types only |

`backend/app/main.py` is near the 300–350 line guideline, so this slice must keep runtime additions
minimal and place deterministic event construction in the student domain module.

## 6. Event / Schema Deltas

- Tighten `node_created` v1 required payload fields for this slice:
  - `node_id`, `session_id`, `node_type`, `content`, `source_node_id`, `source_offer_set_id`,
    `source_option_id`, `source_option_text`, `thread_context_id`.
- Register `edge_created` v1 with required payload fields:
  - `edge_id`, `session_id`, `source_node_id`, `target_node_id`, `edge_kind`, `created_by`.
- `edge_kind` for this slice is `ai_path` only.

No database migration is required for this in-memory event-registry slice.

## 7. API Contract Delta

`OfferChoiceResponse` remains student-safe. For selected outcomes it adds:
- `child_node_id`
- `edge_id`
- `child_node_type: "ai"`
- `child_content`

For dismissed outcomes those fields are `null` or absent, and no child path events are appended.

## 8. Test Plan

First red tests:
- T1: selected edge offer choice appends `offer_set_choice`, `node_created`, and `edge_created` in order.
- T2: `node_created` links selected option, offer set, parent/source node, and thread context.
- T3: `edge_created` uses `edge_kind: ai_path`, source node, and target child node.
- T4: dismissed choice appends no `node_created`/`edge_created` and enqueues no classify job.
- T5: response contains no analytic/measurement fields.

Validation gates:
- Focused integration tests for edge branching.
- Existing offer-set logging and offer-choice regressions.
- Ruff format/check, MyPy, and full pytest after focused green.

## 9. Definition of Done

- Active SDD and canon point to this slice.
- Red tests fail before implementation and pass after implementation.
- Selected edge choices create a reconstructable child path from events alone.
- Dismissed choices remain non-branching and non-classifying.
- No LLM/provider call is introduced.
- `docs/planning/worklog-v4.md` records validation and remaining M1 work.