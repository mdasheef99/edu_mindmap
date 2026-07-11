# 06 Testing and Verification Map

**2026-07-11 update**: physical-device remediation coverage added cached JWKS reuse, bootstrap
consent mapping, consent prompt suppression, remote Supabase logout, and progressive dashboard
rendering before curriculum completion.

**Snapshot**: 2026-07-10. Current automated M4 remediation gates are green; human gates remain.

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
- Mobile: 27/27 suites and 136/136 tests green; TypeScript green.
- Web export: green and contains `dist/canvaskit.wasm`.
- Native bundling: Expo Go Android Hermes bundle succeeded with 1,822 modules and 11,243,312 bytes.
- Live durable smoke: signup/bootstrap → consent-aware session/root → branch → runtime recreation →
  dashboard/resume/hydrate; the Postgres worker completed classification and projection.
- Live schema readback: all 15 audited tables contain `tenant_id` and have RLS enabled.

## Remaining Human/Operational Gates

1. Physical Android: stranger signup → dashboard → Electricity → canvas and resume.
2. Interactive browser: render the web canvas without `PictureRecorder`/CanvasKit errors.
3. Pooled non-bypass app-role: prove cross-tenant denial through RLS.

Jest/export/bundle success does not substitute for these gates. Likewise, schema metadata alone is
not the non-bypass RLS behavior test.
