# M4 Fixture Electricity Session + Generation Flow Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Start and extend Electricity sessions with deterministic fixture-backed content that mimics real backend/event/canvas node creation without live LLM calls.

**Architecture:** Introduce a typed generation provider boundary with `fixture_electricity_v1` active for M4 and `llm_stage1` deferred. Session start creates a root fixture node; selected edge-plus/phrase choices create child fixture nodes and AI-path edges through existing event flows.

**Traceability:** M4 SDD Sections 8.3, 9, 12.3; `student-api-spec.md` Sections 5 and 8; `backend-architecture.md` Sections 6, 7.1, 9-11.

---

## Files

- Create: `backend/app/generation/provider.py`
- Create: `backend/app/generation/fixture_electricity.py`
- Modify: `backend/app/runtime/session.py`
- Modify: `backend/app/runtime/session_workflow.py`
- Modify: `backend/app/runtime/offer_workflow.py`
- Modify: `backend/app/domain/student/offer_choices.py`
- Modify: `backend/app/domain/student/sessions.py`
- Modify: `backend/app/events/registry.py` if payload schemas need fixture lineage fields
- Test: `tests/integration/test_m4_fixture_sessions.py`
- Regression tests: `tests/integration/test_offer_choice.py`, `tests/integration/test_phrase_selection.py`, `tests/integration/test_edge_branching.py`, `tests/integration/test_session_canvas_state.py`

## Task 1: Provider Red Tests

- [ ] Test provider exposes about 10 nodes.
- [ ] Test root node has `prompt_version = fixture-electricity-v1` and `model_id = fixture`.
- [ ] Test nodes include overview, current, potential difference, Ohm's law, resistance, factors affecting resistance, series, parallel, heating effect, power.
- [ ] Test unknown path returns a typed fallback/error.
- [ ] Test provider responses include lineage metadata and no analytic fields.

Run:

```powershell
pytest tests/integration/test_m4_fixture_sessions.py -q
```

Expected: fail because provider does not exist.

## Task 2: Implement Provider

- [ ] Add protocol and request/response types in `backend/app/generation/provider.py`.
- [ ] Add fixture content in `backend/app/generation/fixture_electricity.py`.
- [ ] Assert behavior by shape and lineage, not exact educational prose.
- [ ] Do not add live LLM generation.

## Task 3: Session Root Node Red Tests

- [ ] Test `POST /v1/student/sessions` appends `session_started` and root `node_created`.
- [ ] Test `GET /v1/student/sessions/{id}` after start returns a canvas with the root node.
- [ ] Test unlaunchable chapter is rejected.
- [ ] Test root node payload includes chapter analysis, prompt/model stamp, and lineage.

Run:

```powershell
pytest tests/integration/test_m4_fixture_sessions.py -q
```

Expected: root node assertions fail until session workflow is updated.

## Task 4: Implement Session Root Node

- [ ] Resolve chapter launchability and `chapter_analysis_id` server-side.
- [ ] Append `session_started`.
- [ ] Append root `node_created` for a new Electricity session.
- [ ] Keep event store append-only and registry-validated.
- [ ] Ensure canvas hydration reads the new root node.

## Task 5: Offer Choice Child Node Red Tests

- [ ] Test edge-plus selected choice creates fixture child node and `ai_path` edge.
- [ ] Test phrase selected choice creates fixture child node and `ai_path` edge.
- [ ] Test selected choice enqueues classification asynchronously.
- [ ] Test dismissed choice creates no child node and enqueues no classify job.
- [ ] Test provider exhaustion/unknown choice returns typed fallback without breaking canvas hydration.

Run:

```powershell
pytest tests/integration/test_m4_fixture_sessions.py -q
```

Expected: child fixture assertions fail until offer workflow is updated.

## Task 6: Implement Offer Choice Integration

- [ ] Keep existing `offer_set_choice`, `node_created`, and `edge_created` event types.
- [ ] Use provider output for selected child node content/title/edge label.
- [ ] Preserve Organic-First rule: selected choices enqueue classify; dismissed choices enqueue nothing.
- [ ] Preserve node hard-limit behavior.

## Task 7: Green And Cleanup

Run:

```powershell
pytest tests/integration/test_m4_fixture_sessions.py tests/integration/test_offer_choice.py tests/integration/test_phrase_selection.py tests/integration/test_edge_branching.py tests/integration/test_session_canvas_state.py -q
```

After Python tests:

```powershell
Get-ChildItem -Path . -Recurse -Filter *.pyc | Remove-Item -Force
$pycCount = (Get-ChildItem -Path . -Recurse -Filter *.pyc | Measure-Object).Count
if ($pycCount -ne 0) { throw "Remaining .pyc count: $pycCount" }
```

Expected: tests pass and `.pyc` count is zero.
