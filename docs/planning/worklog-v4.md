# Worklog v4 — Phase 3 Core Loop Deepening

Continuation of `docs/planning/worklog-v3.md` after rotation beyond the 350-line guideline.

---

### 2026-06-18 — Phase 3 kickoff: student session resume slice green

**Phase / milestone**: Phase 3 — Core Loop Deepening (M1 session persistence + resume)

**Spec sections used**:
- `docs/planning/development-approach.md` §5 M1 (session persistence + resume) and §8
  (small traceable increments).
- `docs/architecture/backend-architecture.md` §2.2, §5.3–§5.5, §6.2, §7.1, §11
  (student-safe read model, tenant/ownership isolation, `session_resumed`, `/v1/student`).
- `docs/planning/session-path-data-contract.md` §5, §8, §11, §14 (resume context,
  session opened/resumed events, narrow offline/reopen boundary, acceptance checks).
- `docs/prd/master-prd.md` §6 and `docs/mvp-features-specification.md` Feature Groups 2 and 7
  (dashboard re-entry, recent sessions, session persistence/basic offline reopen).
- `docs/mobile-features-core-ui.md` §1.3 and `docs/mobile-features-system.md` §7.3
  (Continue Learning, Recent Sessions, narrow basic offline access).
- Active SDD: `docs/planning/sdd/phase-3-session-resume-sdd.md` §3–§9.

**Work completed**:
- Created the active Phase 3 SDD: `docs/planning/sdd/phase-3-session-resume-sdd.md`.
- Updated `.augment/rules/00-canon.md` to mark Phase 3 as active, Phase 2 locally closed, and this
  worklog as the live tracker.
- Added red tests in `tests/integration/test_session_resume.py` for:
  - recent sessions returning at most five authenticated-student-owned rows with no analytic fields,
  - resume appending `session_resumed` and updating `last_active_at`,
  - cross-tenant resume denial through the pooled tenant path.
- Registered `session_resumed` v1 in `app.events.registry`.
- Extended `student_rm.sessions` in-memory projection helpers with tenant + student ownership reads,
  recent ordering, and resume projection updates.
- Extended the in-memory pooled tenant helper with student-owned fetch/list operations.
- Added `/v1/student/sessions/recent` and `/v1/student/sessions/{session_id}/resume` using only
  student-safe domain response models.

**Validation run**:
- Red baseline observed first after test-helper correction:
  `python -m pytest tests/integration/test_session_resume.py -q` → 2 failed, 1 passed
  (missing Phase 3 endpoints returned 404).
- `python -m pytest tests/integration/test_session_resume.py -q` → 3 passed.
- `python -m pytest tests/integration/test_session_start.py tests/integration/test_offer_choice.py tests/integration/test_tenant_isolation.py tests/architecture/test_import_linter_contracts.py -q`
  → 17 passed.
- Initial `python -m ruff format --check backend tests` found one formatting change in the new test;
  formatted with `python -m ruff format tests/integration/test_session_resume.py`.
- `python -m ruff format --check backend tests` → passed.
- `python -m ruff check backend tests` → passed.
- `python -m mypy backend/app` → passed.
- `python -m pytest tests -q` → 73 passed.

**Gate status**:
- Phase 3 is now active with the first M1 session-resume slice **GREEN** locally.
- Remaining M1 scope is still open: offer-set impression/propensity logging completion,
  edge-`+` branching, deletion cascade with confirmation, and stronger full-session path
  reconstruction from events alone.
- Deferred operational gates remain: Render backend+worker live verification and physical-device
  Expo smoke against the deployed backend.

---

### 2026-06-18 — Phase 3 M1: edge offer-set logging slice green

**Phase / milestone**: Phase 3 — Core Loop Deepening (M1 offer-set logging completion)

**Spec sections used**:
- `docs/planning/development-approach.md` §5 M1 and §8 (offer-set logging completion before deeper
  path interpretation; small traceable increment).
- `docs/architecture/backend-architecture.md` §6.2, §7.1, §11 (offer-set event spine,
  student-safe `/v1/student`, category invisibility).
- `docs/planning/session-path-data-contract.md` §8–§9 and §14 (offer-set exposure + choice must be
  reconstructable from events).
- `docs/measurement-and-experimentation.md` §4.1–§4.4 (separate created/impression/choice events,
  propensities, probe flags, randomization metadata, visibility logging).
- `docs/mvp-features-specification.md` Feature 4.4 and `docs/mobile-features-ai-integration.md`
  §6.5.1 (edge `+` question discovery requires student-safe offer sets while backend owns logging).
- Active SDD: `docs/planning/sdd/phase-3-offer-set-logging-sdd.md` §3–§9.

**Work completed**:
- Created the active Phase 3 offer-set logging SDD and pointed `.augment/rules/00-canon.md` to it.
- Marked `docs/planning/sdd/phase-3-session-resume-sdd.md` as completed locally so the first slice
  no longer appears active.
- Added red tests in `tests/integration/test_offer_set_logging.py` for:
  - `POST /v1/student/offer-sets/edge` appending `offer_set_created` and `offer_set_impression`,
  - created-event payloads including rank/order, `propensity`, `is_probe`, and `randomization_id`,
  - student response hiding measurement fields,
  - no classify enqueue on impression, while existing selected `offer_set_choice` still enqueues.
- Added `app.domain.student.offer_sets` with deterministic fixture-backed edge offer-set request /
  response models and pure event builders.
- Added `app.api.student.offer_sets` exposing `POST /v1/student/offer-sets/edge`.
- Registered `offer_set_created` v1 and `offer_set_impression` v1 in `app.events.registry`.
- Extended `SessionRuntime` to validate session ownership through the pooled tenant path, append the
  created + impression events atomically, and return only student-safe response fields.

**Validation run**:
- Red baseline: `python -m pytest tests/integration/test_offer_set_logging.py -q` → 3 failed
  (`POST /v1/student/offer-sets/edge` returned 404 before implementation).
- `python -m pytest tests/integration/test_offer_set_logging.py -q` → 3 passed.
- `python -m pytest tests/integration/test_offer_choice.py tests/integration/test_session_start.py -q`
  → 12 passed.
- Initial `python -m ruff format --check backend tests` requested formatting in 4 files; formatted with
  `python -m ruff format backend/app/api/student/offer_sets.py backend/app/domain/student/offer_sets.py backend/app/main.py tests/integration/test_offer_set_logging.py`.
- `python -m ruff format --check backend tests` → passed.
- `python -m ruff check backend tests` → passed.
- `python -m mypy backend/app` → passed.
- `python -m pytest tests/integration/test_offer_set_logging.py tests/integration/test_offer_choice.py tests/integration/test_session_start.py -q`
  → 15 passed.
- `python -m pytest tests -q` → 76 passed.

**Gate status**:
- Offer-set logging completion slice is **GREEN** locally with no live LLM/provider calls and no
  student-visible measurement leakage.
- Remaining M1 scope is now narrower: edge-`+` child-node branching, deletion cascade with
  confirmation, and stronger full-session path reconstruction from events alone.
- Deferred operational gates remain unchanged: Render backend+worker live verification and
  physical-device Expo smoke against the deployed backend.

---

### 2026-06-18 — Phase 3 M1: edge `+` branching slice green

**Phase / milestone**: Phase 3 — Core Loop Deepening (M1 edge `+` child-node branching)

**Spec sections used**:
- `docs/planning/development-approach.md` §5 M1 and §8 (edge-`+` branching; one small traceable
  increment toward event-only path reconstruction).
- `docs/architecture/backend-architecture.md` §6.2, §7.1, §8.2, §11 (canvas/offer events,
  student-safe response types, async worker independence).
- `docs/planning/session-path-data-contract.md` §8–§9 and §14 (selected follow-up question,
  source/target node identifiers, thread context, reconstructable AI-path progression).
- `docs/api/student-api-spec.md` §8 (selected `offer_set_choice` creates `node_created` and
  `edge_created`; dismissed outcomes do not branch).
- `docs/mobile-features-ai-integration.md` §6.5.1 (edge `+` follow-up question flow).
- Active SDD: `docs/planning/sdd/phase-3-edge-branching-sdd.md` §3–§9.

**Work completed**:
- Created the active edge branching SDD and pointed `.augment/rules/00-canon.md` to it.
- Marked `docs/planning/sdd/phase-3-offer-set-logging-sdd.md` as completed locally.
- Added red tests in `tests/integration/test_edge_branching.py` for:
  - selected edge offer choice appending `offer_set_choice`, `node_created`, and `edge_created`,
  - child AI node event retaining source offer set, selected option, and thread context,
  - `edge_created` using `edge_kind: ai_path` with source/target node IDs,
  - dismissed choice remaining non-branching and non-classifying,
  - student response staying category-invisible.
- Extended `app.domain.student.offer_choices` with deterministic child path event builders and
  student-safe selected-choice response fields.
- Added `app.runtime.offer_workflow` so offer orchestration moved out of `backend/app/main.py`; this
  reduced `main.py` from ~330 lines to 292 lines and kept new workflow logic cohesive.
- Registered `edge_created` v1 and tightened `node_created` v1 payload requirements in the event
  registry.
- Updated older offer-choice and classify-worker tests so they no longer assume selected choice is a
  terminal event; classify lineage now explicitly points to the `offer_set_choice` event.

**Validation run**:
- Red baseline: `python -m pytest tests/integration/test_edge_branching.py -q` → 2 failed, 1 passed
  (selected choice did not yet append `node_created` / `edge_created`, and response lacked child fields).
- `python -m pytest tests/integration/test_edge_branching.py -q` → 3 passed.
- `python -m pytest tests/integration/test_edge_branching.py tests/integration/test_offer_choice.py tests/integration/test_offer_set_logging.py -q`
  → 13 passed.
- Initial `python -m ruff format --check backend tests` requested formatting in 2 files; formatted with
  `python -m ruff format backend/app/runtime/offer_workflow.py tests/integration/test_edge_branching.py`.
- `python -m ruff format --check backend tests` → passed.
- `python -m ruff check backend tests` → passed.
- `python -m mypy backend/app` → passed.
- First `python -m pytest tests -q` surfaced one classify lineage test assumption; fixed it to select
  `offer_set_choice` by event type instead of using the last event.
- `python -m pytest tests/integration/test_classify_worker.py::test_question_classified_row_carries_version_stamps -q`
  → 1 passed.
- Final `python -m pytest tests -q` → 79 passed.

**Gate status**:
- Edge `+` branching slice is **GREEN** locally with deterministic fixture content and no live
  LLM/provider calls.
- Phase 3 M1 now has session resume, offer-set logging, and edge branching green locally.
- Remaining M1 scope: deletion cascade with confirmation and stronger full-session path
  reconstruction from events alone.
- Deferred operational gates remain unchanged: Render backend+worker live verification and
  physical-device Expo smoke against the deployed backend.

---

### 2026-06-18 — Phase 3 M1: deletion cascade with confirmation slice green

**Phase / milestone**: Phase 3 — Core Loop Deepening (M1 deletion cascade with confirmation)

**Spec sections used**:
- `docs/planning/development-approach.md` §5 M1 and §8 (deletion cascade with confirmation; small
  traceable increment toward event-only path reconstruction).
- `docs/architecture/backend-architecture.md` §2.1, §6.2, §6.3, §7.1, §11 (append-only events,
  `node_deleted` / `edge_deleted`, student-safe `/v1/student`).
- `docs/planning/session-path-data-contract.md` §3, §8, §10, §12, §14–§15 (confirmed deletion,
  descendant AI-path cascade, deletion-aware consumers, append-only historical record).
- `docs/api/student-api-spec.md` §6 (confirmed node deletion emits `node_deleted` and related
  `edge_deleted` events with cascade cause).
- Active SDD: `docs/planning/sdd/phase-3-deletion-cascade-sdd.md` §3–§9.

**Work completed**:
- Created the active deletion cascade SDD and pointed `.augment/rules/00-canon.md` to it.
- Marked `docs/planning/sdd/phase-3-edge-branching-sdd.md` as completed locally.
- Added red tests in `tests/integration/test_deletion_cascade.py` for:
  - rejection without explicit confirmation,
  - cascading deletion across descendant AI-path nodes,
  - `edge_deleted` events using `deletion_cause: node_cascade`,
  - `node_deleted` recording root node and cascade result,
  - student-safe deletion response.
- Added `app.domain.student.deletions` for student-safe response models and delete event builders.
- Added `app.runtime.canvas_deletion` to reconstruct the active canvas from the event log and append
  cascade events without mutating prior events.
- Added `app.api.student.nodes` with
  `DELETE /v1/student/sessions/{session_id}/nodes/{node_id}?confirmed=true`.
- Registered `edge_deleted` v1 and `node_deleted` v1 in the event registry.
- Kept `backend/app/main.py` within the source-size guideline at 314 lines after adding router/runtime
  delegation.

**Validation run**:
- Red baseline: `python -m pytest tests/integration/test_deletion_cascade.py -q` → 3 failed
  (`DELETE /v1/student/sessions/{session_id}/nodes/{node_id}` returned 404 before implementation).
- `python -m pytest tests/integration/test_deletion_cascade.py -q` → 3 passed.
- `python -m pytest tests/integration/test_edge_branching.py tests/integration/test_offer_choice.py tests/integration/test_offer_set_logging.py -q`
  → 13 passed.
- Initial `python -m ruff format --check backend tests` requested formatting in 4 files; formatted with
  `python -m ruff format backend/app/api/student/nodes.py backend/app/domain/student/deletions.py backend/app/runtime/canvas_deletion.py tests/integration/test_deletion_cascade.py`.
- `python -m ruff format --check backend tests` → passed.
- `python -m ruff check backend tests` → passed.
- `python -m mypy backend/app` → passed.
- `python -m pytest tests/integration/test_deletion_cascade.py tests/integration/test_edge_branching.py tests/integration/test_offer_choice.py tests/integration/test_offer_set_logging.py -q`
  → 16 passed.
- `python -m pytest tests -q` → 82 passed.

**Gate status**:
- Deletion cascade slice is **GREEN** locally with append-only delete events and no live LLM/provider
  calls.
- Phase 3 M1 now has session resume, offer-set logging, edge branching, and deletion cascade green
  locally.
- Remaining M1 scope: stronger full-session path reconstruction from events alone.
- Deferred operational gates remain unchanged: Render backend+worker live verification and
  physical-device Expo smoke against the deployed backend.

---

### 2026-06-18 — Phase 3 M1: full-session path reconstruction slice green

**Phase / milestone**: Phase 3 — Core Loop Deepening (M1 full-session path reconstruction)

**Spec sections used**:
- `docs/planning/development-approach.md` §5 M1 (the M1 gate is one full session path
  reconstructable from events alone, without the board snapshot).
- `docs/architecture/backend-architecture.md` §2.1, §6.2, §6.3, §7.1, §7.3, §11 (append-only
  event store, deterministic/idempotent projections, student-safe seams).
- `docs/planning/session-path-data-contract.md` §5–§10 and §12–§15 (session context, ordered
  interaction history, deletion-aware structure, and shared downstream inputs).
- `docs/api/student-api-spec.md` §5 (student-safe session-state seam; no raw event endpoint).
- Active SDD: `docs/planning/sdd/phase-3-session-path-reconstruction-sdd.md` §3–§9.

**Work completed**:
- Added the final Phase 3 M1 SDD and pointed `.augment/rules/00-canon.md` to it.
- Marked `docs/planning/sdd/phase-3-deletion-cascade-sdd.md` completed locally.
- Added deterministic projection tests in `tests/projections/test_session_path_projection.py`.
- Added `app.projections.session_path` to replay one session path from append-only events alone.
- Reconstructed, from events only:
  - session context from `session_started` / `session_resumed`,
  - offer-set exposure and selected/dismissed choice history,
  - created AI-path nodes,
  - active AI-path edges/nodes after deletion events.
- Kept the slice projection-only: no raw `/v1/student/.../events` endpoint, no event-schema change,
  and no Supabase migration.

**Validation run**:
- Red baseline: `python -m pytest tests/projections/test_session_path_projection.py -q` → 2 failed
  (`ModuleNotFoundError: No module named 'app.projections.session_path'`).
- `python -m pytest tests/projections/test_session_path_projection.py -q` → 2 passed.
- `python -m pytest tests/projections/test_session_projection_replay.py tests/projections/test_session_path_projection.py tests/integration/test_session_resume.py tests/integration/test_offer_set_logging.py tests/integration/test_edge_branching.py tests/integration/test_deletion_cascade.py -q`
  → 16 passed.
- Initial `python -m ruff format --check backend tests docs` requested formatting in 2 files;
  formatted with `python -m ruff format backend/app/projections/session_path.py tests/projections/test_session_path_projection.py`.
- Initial `python -m ruff check backend tests` requested import sorting in
  `backend/app/projections/session_path.py`; fixed with
  `python -m ruff check backend/app/projections/session_path.py --fix`.
- `python -m ruff format --check backend tests docs` → passed.
- `python -m ruff check backend tests` → passed.
- `python -m mypy backend/app` → passed.
- `python -m pytest tests -q` → 84 passed.

**Gate status**:
- Full-session path reconstruction slice is **GREEN** locally.
- Phase 3 M1 is now complete locally: session resume, offer-set logging, edge branching,
  deletion cascade, and event-only path reconstruction are all green.
- No Supabase migration was required for the final M1 slice.
- Phase 3 M1 status is **Locally Complete / Operationally Pending**.
- Explicitly deferred operational gates: Render backend+worker live verification and
  physical-device Expo smoke against the deployed backend. These are not prerequisites for starting
  Phase 3 M2 in the current local-development track, but they remain open until a deployed backend,
  deployed worker, and physical-device connection are available and recorded.

---

### 2026-06-18 — Phase 3 M1 operational gates deferred for M2 handoff

**Phase / milestone**: Phase 3 — Core Loop Deepening (M1 operational gate handoff)

**Spec sections used**:
- `docs/planning/development-approach.md` §4.2 and §5 (deployed backend/worker and physical-device
  gates; M2 phrase-selection milestone follows M1 once the event-reconstruction gate is locally green).
- `docs/operations/delivery-and-operations.md` §2, §6, §10–§11 (Render backend/worker deployment,
  worker operations, Sentry, and Expo physical-device proof).
- `docs/mobile-features-system.md` §7.7 (physical Android reference-device expectations).

**Decision / status**:
- Phase 3 M1 remains **Locally Complete**: all deterministic M1 code/test/doc gates are green locally.
- Phase 3 M1 remains **Operationally Pending**: Render backend+worker live verification and
  physical-device Expo smoke are explicitly deferred.
- M2 may start in a new session with operational verification skipped for now by explicit instruction.
- Final operational closure still requires recording:
  - deployed Render backend health/API evidence,
  - deployed Render worker evidence that it can claim/process a Postgres `SKIP LOCKED` job,
  - physical-device Expo evidence against the deployed backend,
  - mobile Sentry smoke evidence if enabled for that device build.

**Reason for deferral**:
- The local M1 gate was satisfied through event-sourced replay and full regression validation.
- Live Render/device verification requires deployment/device access and should not be claimed from local
  checks alone.
- The project can proceed to Phase 3 M2 while carrying this operational gate as an explicit pending item.
