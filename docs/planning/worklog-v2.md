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

- **Current phase**: Phase 1 — Walking Skeleton. Local CI gates are green; live Supabase RLS and
  `SKIP LOCKED` verification now run with a non-bypass role and pass.
- **Next phase gate**: Phase 1 exit gate per SDD §10. Remaining proof items: remote GitHub Actions
  rerun on the latest pushed commit, Render deployment, and physical-device mobile verification.
- **Open decisions**: none for Phase 1; consent gate resolved in `worklog.md` and ADR-0014.

## Phase 1 Live Tracker

### Definition of Done (SDD §10) — current status

- [x] Supabase migrations `0001`–`0003` applied; security advisor lints resolved
- [x] local CI-equivalent gates pass: Ruff format, Ruff lint, mypy, import-linter, pytest
- [x] live `TEST_DATABASE_URL` uses non-bypass role; RLS / `SKIP LOCKED` tests pass actively
- [x] backend Sentry smoke received
- [ ] GitHub Actions CI green on latest pushed commit
- [ ] Render backend + worker deployment verified
- [ ] physical-device Expo verification recorded

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

**Gate status**:
- Phase 1 backend and database proof is green locally and against live Supabase RLS. Remote CI rerun
  still needs verification after this commit is pushed.

**Next step**:
- Push the CI/doc fixes and verify the GitHub Actions run for the new `main` commit.