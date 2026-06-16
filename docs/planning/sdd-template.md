# Software Design Document (SDD) Template

**Document Version**: 1.0  
**Status**: Template — copy per increment into `docs/planning/sdd/`  
**Related Documents**: `docs/planning/development-approach.md` §8, `docs/planning/testing-strategy.md`, `docs/architecture/backend-architecture.md` §4, `docs/api/feature-endpoint-traceability.md`, `docs/database/schema-traceability-and-validation.md`

---

## How to use this template

- Copy this file to `docs/planning/sdd/<increment-name>-sdd.md`.
- **One SDD per increment** (one endpoint / one event type / one projection / one panel) per `development-approach.md` §8.2.
- **Every requirement MUST cite a source-of-truth section.** An SDD never *originates* a requirement; a discovered gap or conflict becomes an ADR or a deliberate spec edit plus a worklog entry (`development-approach.md` §8.1), never a silent SDD decision.
- **Write the "First Red Tests" before implementation.** TDD red-green-refactor applies to the deterministic core (L1/L2/L3). LLM-touching behavior is validated by fixtures / golden sets (L5) and is **never** asserted exactly per-push (`testing-strategy.md` §2).
- Do not build ahead of the current phase (`development-approach.md` §2.1); list deferred work explicitly in §3.

---

## 1. Increment Identity

| Field | Value |
|---|---|
| Increment name | ... |
| Phase / milestone | Phase 0 / Phase 1 / M1 ... |
| Owner | ... |
| Status | Draft / In progress / Done |

## 2. Source-of-Truth References (mandatory)

List the exact spec sections and ADRs this increment implements. No orphan requirements.

- `docs/...` §...
- `docs/architecture/adr-log.md` ADR-...

## 3. Scope of Increment

**In scope:**
- ...

**Out of scope (deferred — name the milestone/gate that owns it):**
- ...

## 4. Traceability Row(s)

Extend the existing chain from `docs/api/feature-endpoint-traceability.md` and `docs/database/schema-traceability-and-validation.md` down to this increment.

| Feature | Endpoint | Event | Read Model | Worker Job | Table(s) |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

## 5. Module Placement & Import Rules

Per `backend-architecture.md` §4. Name the owning `app/` module(s) and the enforced import contracts that apply to this increment.

| Concern | Module | Import rule enforced |
|---|---|---|
| ... | ... | ... |

## 6. Event / Payload / Schema Deltas

- New/changed event types (registry change in `events/registry.py`): ...
- Required stamps made non-nullable per type (`tenant_id`, `event_version`, and family stamps such as `prompt_version`, `model_id`, `policy_version`, `projection_version`): ...
- Migration impact — distinguish migration 0001 non-retrofittable primitives (`development-approach.md` §6) from later additive migrations: ...
- Config bindings consumed (`docs/configuration-reference.md`): ...

## 7. Invariant Enforcement

State, per invariant, how it is *structurally* enforced and which tests prove it (not prose assertions).

### 7.1 Category Invisibility
- Enforced by: ...
- Tests: ...

### 7.2 Organic-First
- Enforced by: ...
- Tests: ...

### 7.3 Tenant Isolation
- Enforced by: ...
- Tests: ...

## 8. Test Plan by Layer

| Layer | Tests Required |
|---|---|
| L1 | pure functions / registry validation / rules |
| L2 | projection replay + idempotency (if a projection is touched) |
| L3 | append-only grants; import-linter; student DTO forbidden-field; `student_rm` forbidden-column |
| L4 | API → events → worker → projection integration for the increment's flow |
| L5 | fixture / golden-set validation for any LLM-touching path (cadence, not per-push exact assert) |
| L6 | mobile unit / device smoke only if a mobile surface is part of this increment |

## 9. First Red Tests (write before implementation)

1. ...

## 10. Definition of Done

Per `testing-strategy.md` §6 and `development-approach.md` §8.2 — the increment is done only when:

- [ ] L1 tests exist and pass
- [ ] any new projection has L2 determinism + idempotency tests
- [ ] any new endpoint has its L4 flow covered or extended
- [ ] the standing guarantee suite (import-linter, invisibility serialization, append-only, tenant isolation) is green
- [ ] CI is green including import-linter and formatter
- [ ] any LLM prompt change followed its L5 cadence
- [ ] the worklog entry (§11) is added

## 11. Worklog Entry Required

After implementation, add one entry to `docs/planning/worklog.md` (using its template) recording: source sections used, events implemented, tables created, endpoints implemented, tests run, invariant-test status, open issues, and next-milestone recommendation.
