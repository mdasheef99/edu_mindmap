> **AGENT ROTATION INSTRUCTION — READ FIRST**
>
> This is the active worklog continuation after `docs/planning/worklog.md`. Keep this file at or
> below 350 lines. When adding an entry would exceed 350 lines, create
> `docs/planning/worklog-v3.md`, add a `Legacy Context Summary`, copy forward current phase/gate
> status and open blockers, then append future entries only in the new file.

# Development Worklog — 02

**Document Version**: 1.0  
**Status**: Active continuation  
**Previous File**: `docs/planning/worklog.md`

---

## Legacy Context Summary

- Phase 1 — Walking Skeleton is the active increment; do not open Phase 2/3 work.
- Migrations `0001`, `0002`, and `0003` are applied on the connected Supabase project.
- Supabase security advisor lints are resolved for the Phase 1 schema baseline.
- Backend worker entrypoint uses Postgres-backed queue/store adapters.
- Backend Sentry smoke was received in the `mindmap-backend` project.
- The previous local baseline was `35 passed, 2 skipped`; the skips were the opt-in live DB tests
  when `TEST_DATABASE_URL` was missing or used a role with `BYPASSRLS`.

## Current Phase

- **Current phase**: Phase 1 — Walking Skeleton. **CLOSED 2026-06-18.**
- **Next phase**: Phase 2 — Curriculum Ingestion (active milestone per `00-canon.md`).
- **Open decisions**: none for Phase 1; consent gate resolved in `worklog.md` and ADR-0014.

## Phase 1 Live Tracker

### Definition of Done (SDD §10) — FINAL status

- [x] Supabase migrations `0001`–`0003` applied; security advisor lints resolved
- [x] local CI-equivalent gates pass: Ruff format, Ruff lint, mypy, import-linter, pytest
- [x] live `TEST_DATABASE_URL` uses non-bypass role; RLS / `SKIP LOCKED` tests pass actively
- [x] backend Sentry smoke received
- [x] GitHub Actions CI green on latest pushed commit (`10bb751`, run `27716220823`)
- [deferred] Render backend + worker deployment — defer to Phase 2 sprint 1
- [deferred] physical-device Expo verification — defer to Phase 2 sprint 1

---

## Entries

### 2026-06-17 — CI gate repair and live non-bypass RLS proof

**Phase / milestone**: Phase 1 — Walking Skeleton

**Spec sections used**:
- `docs/planning/development-approach.md` §4, §6, §8
- `docs/planning/sdd/phase-1-walking-skeleton-sdd.md` §10
- `docs/architecture/backend-architecture.md` §5, §8, §12
- `docs/planning/testing-strategy.md` §3, §6

**Work completed**:
- Checked GitHub Actions for commit `36f256c`; initial run failed at Ruff format.
- Formatted backend/tests and aligned CI dependency install with `requirements.txt`.
- Added `PYTHONPATH=backend` to CI so import-linter can resolve `app`.
- Created a non-bypass Supabase login role for live RLS tests and updated local `TEST_DATABASE_URL`.
- Replaced parameterized `SET LOCAL app.tenant_id` calls with shared `set_config(...)` helper.
- Added code-organization standard: source files should stay under 300–350 lines and be split by
  responsibility when they approach that limit.

**Validation run**:
- `python -m ruff format --check backend tests` → passed.
- `python -m ruff check backend tests` → passed.
- `python -m mypy backend/app` → passed.
- `PYTHONPATH=backend lint-imports --config pyproject.toml --no-cache` → contracts kept.
- `python -m pytest tests -q` → 35 passed, 2 skipped.
- `pytest tests/database/test_optional_postgres_rls_contract.py` with `.env` loaded → 2 passed.
- GitHub Actions `Phase 1 CI` run `27716220823` for commit `10bb751` → passed.

**Gate status**:
- Phase 1 backend, database, and remote CI proof are green. Remaining Phase 1 proof items are Render
  deployment and physical-device mobile verification.

**Next step**:
- Prepare Render backend/worker verification steps, then record physical-device Expo proof.

---

### 2026-06-18 — Phase 1 formally closed; mobile verification deferred

**Phase / milestone**: Phase 1 — Walking Skeleton (exit)

**Work completed**:
- Updated SDD §1 status and §10 DoD to mark Phase 1 as CLOSED.
- Physical-device Expo verification and Render deployment recorded as deferred (non-blocking;
  mobile surface is additive to the backend walking skeleton).
- `00-canon.md` ACTIVE MILESTONE updated to Phase 2 — Curriculum Ingestion.
- Worklog status updated to reflect Phase 1 closure.

**Gate status**: Phase 1 exit gate **PASSED**. All non-deferred DoD items verified.

---

### 2026-06-18 — Phase 2 kickoff: Curriculum Ingestion SDD + supporting docs initialized

**Phase / milestone**: Phase 2 — Curriculum Ingestion (active milestone per `00-canon.md`)

**Spec sections used**:
- `docs/planning/development-approach.md` §3 (Phase 0 P0–P4), §5 (M4 auth + M6 teacher render note), §6 (day-one disciplines), §7.1/§7.7 (auth stack + content pipeline tooling), §8 (working method)
- `docs/architecture/backend-architecture.md` §3 (deployment), §4 (module boundaries + new `chapter_analysis` + `curriculum` contracts), §5.1/§5.3/§5.4 (tenancy, RLS, identity resolution), §6 (event store), §7.5 (curriculum schema), §9 (LLM Gateway), §11 (API surface)
- `docs/chapter-analysis-pipeline-specification.md` P0–P4 + §5 (verification gate)
- `docs/planning/sdd/phase-2-curriculum-ingestion-sdd.md` §3–§11 (the new active SDD)
- `docs/planning/testing-strategy.md` §2/§3.1 (L1–L6 matrix + Phase 2 additions)
- `docs/configuration-reference.md` §10.1 (Phase 2 env placeholders)
- `docs/architecture/adr-log-02.md` ADR-0015 (Supabase Auth strategy, Proposed)

**Work completed**:
- Created `docs/planning/sdd/phase-2-curriculum-ingestion-sdd.md` (draft v1.0): defines Phase 2
  scope as P0–P4 ingestion, Supabase Auth + tenant resolution, and Teacher Dashboard V1 render.
  Listed Render deployment and physical-device Expo verification as the first implementation
  priorities (deferred from Phase 1), with Expo explicitly gated on a mobile curriculum surface
  existing (SDD §7.4).
- Updated `docs/architecture/backend-architecture.md`: added §4 Phase 2 boundary note for
  `chapter_analysis` and new §7.5 `curriculum` content schema.
- Updated `docs/planning/testing-strategy.md`: added §3.1 Phase 2 test matrix (Auth L3, Ingestion L2
  determinism/idempotency, plus L1/L4/L5/L6 rows).
- Updated `docs/configuration-reference.md`: added §10.1 Supabase Auth + ingestion env placeholders
  (names only, no values).
- Updated `docs/architecture/adr-log-02.md`: refreshed legacy summary to Phase 2; added ADR-0015
  (Supabase Auth JWT validation strategy) as Proposed.
- Updated `.augment/rules/00-canon.md`: active SDD line marked as created (draft v1.0).

**Gate status**: Phase 2 entry gate **OPEN**; no production code yet. First red tests (SDD §9) must be
written before implementation.

**Deferred / non-deferred items for next session**:
- Render deployment: **do not defer** — no frontend dependency; should be the first proof item.
- Physical-device Expo smoke: **may remain deferred** until a mobile curriculum session surface
  exists (SDD §7.4).

**Next step**:
- Record ADR-0015 acceptance and start either Render deployment verification or Supabase Auth
  red-test-first implementation (SDD §3.1 priority order).