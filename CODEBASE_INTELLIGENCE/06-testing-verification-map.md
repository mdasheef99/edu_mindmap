# 06 Testing & Verification Map

## Test Frameworks
- **Backend**: `pytest`
- **Mobile**: `Jest`
- **Boundary Checks**: `import-linter`

## Key Test Locations
- **Backend Unit/Integration**: `tests/` (mirrors `backend/app/` structure).
- **Mobile Logic**: `mobile/app/__tests__/`.
- **Worker Jobs**: `tests/workers/`.

## Setup & Fixtures
- **SessionRuntime.for_testing**: Creates an in-memory runtime for fast, isolated backend tests.
- **InMemoryEventStore**: Mocked event log.
- **LLM Fixtures**: LLM responses are recorded in `LLM_CI_MODE` to avoid external costs and non-determinism in CI.

## Critical Test Commands
- **Backend Tests**: `pytest`
- **Mobile Tests**: `npm test` (inside `mobile/app/`)
- **Import Linter**: `lint-imports`
- **Type Check**: `tsc --noEmit` (mobile) or `mypy` (backend).

## Verification Risks
- **60fps Mobile Performance**: Cannot be verified in Jest; requires manual verification on physical devices (Stage 2 gate).
- **Concurrent Job Claims**: `SKIP LOCKED` behavior should be tested under load to ensure no duplicate job execution.
- **Snapshot Determinism**: Replaying the same event log must always produce a byte-identical read model.

## Smoke Testing
- **Script**: `backend/scripts/dev_smoke_bootstrap.py --dev-smoke`
- **Purpose**: Bootstraps a local backend with a seeded canvas and prints a token for Expo Go.
- **Workflow**:
    1. Run bootstrap script.
    2. Open Expo Go on physical device.
    3. Paste `apiBaseUrl` and token into `M2PhraseSmokeScreen`.
    4. Verify branching and canvas hydration.
