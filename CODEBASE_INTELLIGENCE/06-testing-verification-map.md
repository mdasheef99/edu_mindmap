# 06 Testing and Verification Map

**2026-07-12 update**: bounded canvas stabilization verification and Android review are complete:
checked position lifecycle, dragged-edge synchronization, and edge-plus single-flight/recovery.

**Snapshot**: 2026-07-12. M4 is closed; the bounded canvas stabilization record is complete and
M5 remains frozen.

## Test Systems and Locations

- Backend: `pytest` under `tests/{architecture,chapter_analysis,database,integration,projections}`.
- Mobile/canvas: Jest tests under `mobile/app/__tests__/` and `mobile/canvas/__tests__/`.
- Boundaries: four import-linter contracts in `pyproject.toml`, with subprocess assertions in
  `tests/architecture/`.
- Type safety: TypeScript for the Expo app/canvas. There is no current merge-blocking mypy gate.
- Deterministic AI: recorded fixtures/contract checks under `LLM_CI_MODE`; no live LLM in CI.
- Live Postgres tests: opt-in via non-bypass `TEST_DATABASE_URL`; they must not silently fall back
  to a bypass production credential.

## Commands

From the repository root in PowerShell:

```powershell
$env:PYTHONPATH='backend'
python -m pytest --basetemp=.pytest-tmp
lint-imports
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

## Latest Evidence

- Backend: 147 regular tests plus 4/4 isolated import-linter tests green (151 combined); direct
  import-linter reports 4 kept, 0 broken.
- Mobile: 32/32 suites and 170/170 tests green; TypeScript green.
- Canvas position lifecycle: focused B2 12/12 green; nearest branch/discovery/API/coordinator/hook/
  canvas regressions 8 suites and 53/53 green. The new B2 file is clean in isolation.
- Web export: green and contains `dist/canvaskit.wasm`.
- Native bundling: Expo Go Android Hermes bundle succeeded with 1,822 modules and 11,243,312 bytes.
- Live durable smoke: signup/bootstrap → consent-aware session/root → branch → runtime recreation →
  dashboard/resume/hydrate; the Postgres worker completed classification and projection.
- Live schema readback: all 15 audited tables contain `tenant_id` and have RLS enabled.

## Remaining Human/Operational Evidence

1. Physical Android canvas review: rapid completed drags, save-failure feedback/retry where a
   controlled failure can be produced safely, branch placement/reload recovery, and resume.
2. Deferred M3 performance checks: 40+ node 60fps rerun and 65-node smoke.
3. Interactive browser: render the web canvas without `PictureRecorder`/CanvasKit errors
   (non-blocking follow-up).

Jest, TypeScript, LAN reachability, export, and bundle success do not substitute for direct device
behavior or performance evidence.

## 2026-07-12 Stabilization Evidence

- Edge-plus lifecycle: 5/5 independently and 16/16 with nearest discovery tests.
- Focused edge/gesture/position regressions: 13 suites, 68/68.
- TypeScript and `git diff --check`: green; final relevant runs had no new warnings, open handles,
  or unhandled rejections.
- Direct Android review confirmed the dragged-edge and edge-plus corrections. Deferred 40+ node
  60fps and 65-node smoke measurement still require separate evidence.
