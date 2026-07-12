# 06 Testing and Verification Map

**2026-07-13 update**: canvas lifecycle coverage now includes checked PATCH, FIFO/concurrency,
session/deletion disposal, finite validation, UI-thread drag geometry, placement recovery, and
edge-plus single-flight behavior.

**Snapshot**: 2026-07-10. Current automated M4 remediation gates are green; human gates remain.

## Test Systems and Locations

- Backend: `pytest` under `tests/{architecture,chapter_analysis,database,integration,projections}`.
- Mobile/canvas: Jest tests under `mobile/app/__tests__/` and `mobile/canvas/__tests__/`.
- Boundaries: four import-linter contracts in `pyproject.toml`, with subprocess assertions in
  `tests/architecture/`.
- Type safety: TypeScript for the Expo app/canvas and the CI mypy gate over `backend/app`.
- Deterministic AI: recorded fixtures/contract checks under `LLM_CI_MODE`; no live LLM in CI.
- Live Postgres tests: opt-in via non-bypass `TEST_DATABASE_URL`; they must not silently fall back
  to a bypass production credential.

## Commands

From the repository root in PowerShell:

```powershell
$env:PYTHONPATH='backend'
python -m pytest --basetemp=.pytest-tmp
ruff format --check backend tests
ruff check backend tests
mypy backend/app
lint-imports --config pyproject.toml --no-cache
```

The workspace-local `--basetemp` is required on this Windows environment. In the Codex sandbox,
the four import-linter subprocess tests can fail only because the user-level `lint-imports.exe`
path under AppData is not accessible; run those isolated tests with approved escalation or verify
the contracts directly with `lint-imports`. After Python tests, delete generated `*.pyc` and
verify the count is zero.

From `mobile/app`:

```powershell
npm test -- --runInBand
npx tsc --noEmit
npx expo export --platform web
```

## Latest Branch-Local Evidence

- Backend: 164 passed / 3 skipped; focused PATCH/replay/hydration/deletion/resume 22 passed;
  import-linter 4 kept / 0 broken; Ruff format/lint and mypy green.
- Mobile: 35 suites / 159 tests passed; App and Canvas TypeScript green.
- Source/test Python bytecode count: zero; `git diff --check`: green.
- Web export: green and contains `dist/canvaskit.wasm`.
- Native bundling: Expo Go Android Hermes bundle succeeded with 1,822 modules and 11,243,312 bytes.
- Live durable smoke: signup/bootstrap → consent-aware session/root → branch → runtime recreation →
  dashboard/resume/hydrate; the Postgres worker completed classification and projection.
- Live schema readback: all 15 audited tables contain `tenant_id` and have RLS enabled.

## Remaining Human/Operational Gates

1. Owner review and approval before pushing the local canvas stabilization branch.
2. Canvas 40+ node performance rerun and 65-node physical-device smoke remain unverified here.
3. Interactive browser rendering remains a separately documented non-blocking follow-up.

Jest/export/bundle success does not substitute for these gates. Likewise, schema metadata alone is
not the non-bypass RLS behavior test.
