# AGENT ROTATION INSTRUCTION — READ FIRST

This is the live tracker for the local post-PR-6 reconstruction of the historically closed M4
implementation. Keep it below 350 lines and rotate before exceeding that threshold.

## Legacy Context Summary

- `worklog-v9.md` and `worklog-v10.md` are immutable historical M4 evidence.
- Phase 3 M4 remains historically closed as of 2026-07-11; M5 has not started.
- The reconstruction base is the PR #6 merge on `main`.
- This work restores M4 without redesigning product behavior, API contracts, membership
  semantics, tenant isolation, database behavior, mobile flow, or closure evidence.
- Live Supabase migration application and physical-device testing are excluded from this local
  reconstruction stage.

## 2026-07-13 — Local M4 reconstruction opened

**Source sections**:

- `development-approach.md` §§5–8.
- `backend-architecture.md` §§5.3–5.5, 6–8, and 11–12.
- ADR-0017.
- `session-path-data-contract.md` §§5–11.
- Closed M4 parent SDD §§6, 8.4, 10, and 12–14.
- Closed M4 remediation SDD R1, R4, R5, PR-1, PR-2, and DB-1.

**Approved boundaries**:

- Reconstruct from the final M4 snapshot; do not cherry-pick the historical range.
- Preserve PR #6 CORS and fail-closed development configuration.
- Production authentication is ES256/JWKS only.
- HS256 exists only as an explicitly injected deterministic test-fixture verifier.
- `M4_INDIVIDUAL_TENANT_ID` is required production configuration.
- Preserve the applied M4 SQL artifacts unchanged; clarify their order with a manifest.
- Defer event-registry extraction and preserve current 401 handling for JWKS failures.

**Red-first evidence**:

- Added configuration, production-HS256 rejection, fixture-isolation, and migration-manifest
  tests before implementing the cleanup.
- Initial focused run: 18 failed / 7 passed for the intended missing M4/configuration boundaries.
- After implementation: 29/29 focused tests green.

**Implemented so far**:

- Typed fail-closed production configuration with explicit database, Supabase issuer/JWKS,
  individual tenant, and CORS inputs.
- Explicit ES256/JWKS production verifier and separate HS256 fixture verifier.
- Durable production composition contains no fallback secret or implicit tenant.
- Migration-source manifest distinguishes Alembic and applied Supabase histories without changing
  either applied SQL artifact.
- Historical M4 app shell is manually reconciled with PR #6 development Canvas configuration;
  no embedded credential or machine-specific URL is used.

**Local verification evidence**:

- Ruff format: 145 files already formatted; Ruff lint: all checks passed.
- Mypy: 94 application source files green.
- Import-linter: four contracts kept, zero broken.
- Full Python suite: 164 passed / 3 skipped.
- Focused configuration, authentication, tenant-isolation, runtime, migration-order, and session
  suite: 30 passed.
- Full mobile Jest suite: 28 suites / 139 tests passed.
- App and Canvas TypeScript checks: green.
- `git diff --check`: reconstructed code is clean; two trailing-space findings remain in the
  byte-for-byte preserved, closed remediation SDD at lines 5-6. The immutable closure evidence was
  not edited to conceal that historical formatting issue.
- Sensitive-value scan found no JWT-shaped tokens or private-key material. URL/credential-pattern
  hits are confined to immutable historical evidence, explicit example/test fixtures, and typed
  credential parameters; production configuration contains no embedded value.
- Only `.env.example` is present in the reconstruction worktree. Generated-file count is zero;
  Python bytecode count is zero.

**Remaining operational gates**:

- Live Supabase ES256/JWKS, key rotation, membership bootstrap, and applied-migration verification
  require explicit project configuration and credentials.
- The closed physical-device flow remains operational evidence and was not rerun in this local
  reconstruction stage.
- Create local commits only; do not push or open a PR without separate approval.
