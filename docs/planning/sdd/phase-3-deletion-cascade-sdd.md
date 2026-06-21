# Phase 3 Deletion Cascade — Software Design Document (SDD)

**Document Version**: 1.0 (active draft)  
**Status**: Completed locally — green  
**Phase / milestone**: Phase 3 — Core Loop Deepening, M1 deletion cascade with confirmation  
**Live tracker**: `docs/planning/worklog-v4.md`

---

## 1. Increment Identity

| Field | Value |
|---|---|
| Increment name | Confirmed AI-path node deletion cascade |
| Phase / milestone | Phase 3 — Core Loop Deepening, M1 |
| Owner | (developer) |
| Status | Completed locally |

Goal: add the smallest student-safe backend slice for confirmed AI-path node deletion. Deleting an
AI-path node must cascade to descendant AI-path nodes and related edges while preserving append-only
history through `edge_deleted` and `node_deleted` events.

## 2. Source-of-Truth References

- `development-approach.md` §5 M1: Core Loop Deepening includes deletion cascade with confirmation;
  the M1 gate is a full session path reconstructable from events alone.
- `backend-architecture.md` §2.1, §6.2, §6.3, §7.1, §11: event store is append-only; canvas events
  include `node_deleted` and `edge_deleted`; `/v1/student` stays student-safe.
- `session-path-data-contract.md` §3, §8, §10, §12, §14–§15: deleting an AI-generated path node
  removes descendants after confirmation; deletion must be evented and deletion-aware for consumers.
- `docs/api/student-api-spec.md` §6: `DELETE /v1/student/sessions/{session_id}/nodes/{node_id}` is a
  confirmed deletion that emits `node_deleted` and related `edge_deleted` with `node_cascade` cause.

## 3. Scope of Increment

**In scope:**
- Add `DELETE /v1/student/sessions/{session_id}/nodes/{node_id}?confirmed=true`.
- Reject deletion without explicit confirmation.
- Verify session ownership through backend-resolved tenant/student context.
- Reconstruct active nodes/edges for the session from append-only events.
- Cascade through active `ai_path` descendant edges.
- Append `edge_deleted` events for cascade-related edges.
- Append one `node_deleted` event recording the root node and cascade result.
- Return a student-safe deletion summary.

**Out of scope:**
- Live projection tables for `student_rm.nodes` / `student_rm.edges`.
- Manual reference link creation/deletion endpoint behavior beyond cleaning attached edges if present.
- Worker `project` job implementation, teacher/podcast consumers, UI confirmation modal.
- Hard deletion or mutation of existing events/read-model rows.

## 4. Traceability Rows

| Feature | Endpoint | Events | Read Model | Worker Job | Table(s) |
|---|---|---|---|---|---|
| Confirmed node cascade | `DELETE /v1/student/sessions/{session_id}/nodes/{node_id}?confirmed=true` | `edge_deleted`, `node_deleted` | none in this slice | none in this slice | `events` |

## 5. Module Placement & Import Rules

| Concern | Module | Rule |
|---|---|---|
| Student-safe deletion request/response + event builders | `app.domain.student.deletions` | no analytic/category fields |
| API router | `app.api.student.nodes` | student domain + auth only |
| Runtime orchestration | `app.runtime.canvas_deletion` delegated by `SessionRuntime` | event-log reconstruction + append |
| Event registry | `app.events.registry` | registered known event types only |

The student API must not import projections, analytic modules, or classification modules.

## 6. Event / Schema Deltas

- Register `edge_deleted` v1.
  - Required payload: `edge_id`, `session_id`, `edge_kind`, `deletion_cause`.
  - For this slice, cascade deletions use `deletion_cause: node_cascade`.
- Register `node_deleted` v1.
  - Required payload: `root_node_id`, `session_id`, `deleted_node_ids`, `deleted_edge_ids`,
    `confirmed`, `deletion_cause`.
  - For this slice, node deletion uses `deletion_cause: user_confirmed_node_delete`.

No database migration is required for this in-memory/event-registry slice.

## 7. API Contract

### `DELETE /v1/student/sessions/{session_id}/nodes/{node_id}?confirmed=true`

Response fields:
- `session_id`
- `root_node_id`
- `deleted_node_ids`
- `deleted_edge_ids`
- `confirmed`

Without `confirmed=true`, the endpoint returns a conflict/error and appends no events.

## 8. Test Plan

First red tests:
- T1: deletion without confirmation is rejected and appends no delete events.
- T2: deleting an AI-path node cascades to descendant AI-path nodes and related edges.
- T3: appended `edge_deleted` events use `deletion_cause: node_cascade`.
- T4: appended `node_deleted` records root node and cascade result.
- T5: response is student-safe and contains no analytic/measurement fields.

Validation gates:
- Focused deletion cascade integration tests.
- Existing edge branching / offer workflow regressions.
- Ruff format/check, MyPy, and full pytest after focused green.

## 9. Definition of Done

- Active SDD and canon point to this slice.
- Red tests fail before implementation and pass after implementation.
- Delete endpoint requires confirmation.
- Cascade is derived from events and records delete events without mutating prior events.
- Student response stays category-invisible.
- No LLM/provider call is introduced.
- `docs/planning/worklog-v4.md` records validation and remaining M1 work.