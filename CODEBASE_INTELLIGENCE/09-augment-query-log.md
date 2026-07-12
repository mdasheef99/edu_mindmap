# 09 Intelligence Discovery Log

## 2026-07-11 -- Physical-device remediation direct evidence

- Supabase MCP was available and used against the correct project `jbmqyxhrmcbdgardamrp`.
- Supabase auth logs showed successful password sign-in responses while the app surfaced backend
  `401 Invalid Supabase token`, pointing to backend token verification/session handling.
- Live consent readback showed an active behavioral-analytics grant, so repeated acknowledgement
  was a bootstrap/mobile state propagation defect.
- Direct repository evidence found per-request `PyJWKClient` construction, dashboard rendering
  blocked behind sequential curriculum fetches, and local-only sign-out.
- Augment semantic retrieval was not used for this refresh; direct code, test, log, and Supabase
  MCP evidence was used instead.

This file records significant semantic retrieval and direct verification used to maintain the pack.
Entries explicitly distinguish Augment queries from repository/Supabase evidence.

## 2026-06-24 — Initial Augment Pack Generation

### High-level architecture

**Augment prompt**: Map architecture layers, entry points, routing, state, backend/data integration,
tests, configuration, deployment, and documentation with exact paths.

**Findings**: event-sourced FastAPI modular monolith, hybrid Skia/native mobile canvas,
`backend/app/main.py` and `mobile/app/index.ts` entry points.

### Critical flows and data integration

**Augment prompt**: Map important workflows, screens, services, APIs, tables, jobs, auth, migrations,
storage, mocks, and security caveats.

**Findings**: session start, offer choice, node generation, hydration, Supabase stack, Category
Invisibility, and Tenant Isolation.

### Features, testing, security, and readiness

**Augment prompt**: Map feature ownership, tests, smoke/e2e/type/lint commands, security-sensitive
areas, risky patterns, future touchpoints, stale docs, and live-verification assumptions.

**Findings**: pytest/Jest/import-linter gates, device performance and replay risks, and the then-next
M4 auth/curriculum milestone.

## 2026-07-10 — M4 Canonical Refresh (Direct Evidence)

Augment/codebase-retrieval was not available as a callable tool in this session. The refresh used
complete direct reads and `rg` searches; it must not be represented as an Augment query.

**Read completely**:

- `.augment/rules/00-canon.md`
- active M4 remediation SDD and `docs/planning/worklog-v10.md`
- the full source hierarchy: development approach, backend architecture, both ADR logs,
  session-path contract, master PRD, and MVP feature specification
- every file in `CODEBASE_INTELLIGENCE/`

**Code/config evidence reviewed**:

- production/test runtime composition, Postgres ports/adapters, auth/JWKS, consent, session/root,
  dashboard/catalog, mobile auth restore, canvas handoff, tests, package scripts, Render, and env docs
- `backend/migrations/source_sql/0007_m4_runtime_remediation.sql`
- import-linter configuration and latest recorded automated/device bundle evidence

**External state already verified during the M4 remediation**:

- Correct Supabase project: `jbmqyxhrmcbdgardamrp`
- Applied migrations: `20260702173751` and `20260710075416`
- All 15 audited operational/catalog/read-model tables expose `tenant_id` and have RLS enabled

**Refresh decisions**:

- Replaced stale M2/in-memory flow descriptions with durable M4 production-runtime flows.
- Corrected “Supabase Auth planned” to automated implementation complete, human gates pending.
- Documented the five-table catalog tenant remediation and the remaining non-bypass RLS gate.
- Corrected Expo env names to match `mobile/app/App.tsx`.
- Recorded the honest UX scope: API-derived fixed Electricity path, not a general catalog picker.
