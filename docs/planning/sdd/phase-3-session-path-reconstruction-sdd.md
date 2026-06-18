# Phase 3 Session-Path Reconstruction — Software Design Document (SDD)

**Document Version**: 1.0 (active draft)  
**Status**: Completed locally — green  
**Phase / milestone**: Phase 3 — Core Loop Deepening, M1 full-session path reconstruction  
**Live tracker**: `docs/planning/worklog-v4.md`

---

## 1. Increment Identity

| Field | Value |
|---|---|
| Increment name | Full-session path reconstruction from events alone |
| Phase / milestone | Phase 3 — Core Loop Deepening, M1 |
| Owner | (developer) |
| Status | Completed locally |

Goal: add the smallest deterministic projection slice proving one full learner session path is
reconstructable from the append-only event log alone, without depending on a mutable board
snapshot.

## 2. Source-of-Truth References

- `development-approach.md` §5 M1: the M1 gate is one full session path reconstructable from events
  alone, without the board snapshot.
- `backend-architecture.md` §2.1, §6.2, §6.3, §7.1, §7.3, §11: events are append-only;
  projections are deterministic/idempotent; student-facing seams stay category-invisible.
- `session-path-data-contract.md` §5–§10 and §12–§15: session context, ordered interaction history,
  thread progression, deletion-aware current structure, and shared teacher/podcast inputs must all
  be reconstructable from the path contract.
- `docs/api/student-api-spec.md` §5: session state is student-safe and must not expose raw event
  history; `GET /v1/student/sessions/{session_id}` is a future consumer seam, not a raw event
  surface.

## 3. Scope of Increment

**In scope:**
- Add a deterministic projection module that rebuilds one session path from append-only events.
- Reconstruct session context from `session_started` / `session_resumed`.
- Reconstruct offer-set exposure and selected/dismissed choice history from
  `offer_set_created`, `offer_set_impression`, and `offer_set_choice`.
- Reconstruct active AI-path nodes/edges from `node_created`, `edge_created`, `edge_deleted`, and
  `node_deleted`.
- Derive an ordered explored-path view suitable for later student-safe session-state, teacher, or
  podcast consumers.
- Preserve tenant/student scoping while replaying events.
- Prove byte-identical rebuild and idempotent replay via tests.

**Out of scope:**
- A broad `GET /v1/student/sessions/{session_id}` API response contract.
- Writing `student_rm.nodes` / `student_rm.edges` rows in this slice.
- Manual-reference edge workflows beyond ignoring non-`ai_path` structure when ordering the path.
- A new root `node_created` event at session start.
- Any analytic projection or worker change.

## 4. Traceability Rows

| Feature | Endpoint | Events | Read Model | Worker Job | Table(s) |
|---|---|---|---|---|---|
| Full-session event replay proof | none in this slice | `session_started`, `session_resumed`, `offer_set_created`, `offer_set_impression`, `offer_set_choice`, `node_created`, `edge_created`, `edge_deleted`, `node_deleted` | in-memory session-path projection only | none | `events` |

## 5. Module Placement & Import Rules

| Concern | Module | Rule |
|---|---|---|
| Deterministic session-path replay/projection | `app.projections.session_path` | projection code only; no analytic imports |
| Student-safe session context types reused from prior slices | `app.domain.student.sessions` | no analytic/category fields |
| Validation tests | `tests/projections/test_session_path_projection.py` and focused integration tests if needed | deterministic fixtures only |

This slice must not add a raw event-history endpoint under `/v1/student`.

## 6. Event / Schema Deltas

- No new event types.
- No payload schema changes.
- No database migration for this projection-only slice.

## 7. Projection Contract

The projection must be able to answer, for one `(tenant_id, student_id, session_id)`:

- session context (`exam_id`, `subject_id`, `chapter_id`, `concept_entry_id`,
  `chapter_analysis_id`, timestamps)
- ordered offer-set history, including dismissed outcomes
- ordered selected child-node creation history
- active AI-path nodes and active AI-path edges after deletions
- deletion-aware current session structure suitable for downstream consumers

The initial session root may be represented by the session's starting-context reference
(`concept_entry_id`) rather than a synthetic raw-event endpoint or mutable board snapshot.

## 8. Test Plan

First red tests:
- T1: replay reconstructs session context plus ordered offer/choice history from events alone.
- T2: replay reconstructs ordered AI-path child nodes and parent/edge lineage from selected choices.
- T3: replay is deletion-aware; `node_deleted` / `edge_deleted` remove inactive path artifacts.
- T4: rebuild is byte-identical and replay application is idempotent.
- T5: no raw `/v1/student/.../events` endpoint is introduced while adding this slice.

Validation gates:
- Focused projection tests for the new session-path module.
- Adjacent session/offer/edge/deletion regressions.
- Ruff format/check, MyPy, and full pytest after focused green.

## 9. Definition of Done

- Active SDD and canon point to this slice.
- Red tests fail before implementation and pass after implementation.
- One full session path is reconstructable from events alone without a board snapshot.
- Reconstruction is tenant-scoped, deletion-aware, byte-identical on rebuild, and idempotent on
  replay.
- No raw event endpoint is added to `/v1/student`.
- No LLM/provider call or Supabase migration is introduced.
- `docs/planning/worklog-v4.md` records validation and Phase 3 M1 completion status.