> **AGENT ROTATION INSTRUCTION — READ FIRST**
>
> This is the **active ADR continuation file**. Keep this file at or below 350 lines. When adding a
> new ADR would exceed 350 lines, create `docs/architecture/adr-log-03.md`, add a `Legacy Context
> Summary` linking back to this file, and mark this file as rotated/closed.

# Architecture Decision Record (ADR) Log — 02

**Document Version**: 1.0  
**Status**: Active continuation — append new ADRs here  
**Previous File**: `docs/architecture/adr-log.md`

---

## Legacy Context Summary

This file continues the ADR sequence after `docs/architecture/adr-log.md`, which is closed at
ADR-0014.

Final state inherited from the previous ADR file:

- ADR-0001 through ADR-0014 define the accepted v1.3+ backend architecture and Phase 1 guardrails.
- The backend is a FastAPI modular monolith with a worker process sharing one codebase and one
  Supabase PostgreSQL database.
- MVP async work uses the Postgres `SKIP LOCKED` jobs table; Redis/Celery are deferred.
- `student_rm` and `analytic_rm` are physically separate read models for Category Invisibility.
- Generation remains Organic-First; classification is post-hoc and async after selected
  `offer_set_choice` events.
- Tenant isolation uses backend-resolved tenant context plus RLS as a database backstop.
- LLM access is backend-only through the LLM Gateway; no mobile-side provider credentials.
- Phase 1 includes the behavioral-analytics consent gate: migration 0001 includes
  `consent_records` and `consent_recorded`, and the `classify` worker skips `analytic_rm` writes
  without valid `behavioral_analytics` consent.

Active milestone inherited from the worklog:

- **Phase 1 — Walking Skeleton is CLOSED (2026-06-18).** Backend, database, CI, live non-bypass RLS,
  and Sentry smoke are verified. Render deployment and physical-device Expo verification were
  deferred (non-blocking) to Phase 2 sprint 1.
- **Phase 2 — Curriculum Ingestion** is now the active milestone
  (`docs/planning/sdd/phase-2-curriculum-ingestion-sdd.md`): productionize P0–P4 into
  `chapter_analysis`, land a real chapter in the `curriculum` schema, add Supabase Auth, and render a
  Teacher Dashboard V1. ADR-0015 (below) is the first decision this phase requires.

---

## ADR Numbering

Continue numbering from ADR-0015. Do not renumber or move earlier decisions from the previous file.

## Index

| ADR | Title | Status |
|-----|-------|--------|
| ADR-0015 | Supabase Auth JWT validation strategy | Proposed |

---

## ADR-0015 — Supabase Auth JWT validation strategy

**Status**: Proposed (to be Accepted at Phase 2 kickoff)
**Date**: 2026-06-18
**Phase**: Phase 2 — Curriculum Ingestion
**Source-of-truth refs**: `development-approach.md` §7.1 (Auth = Supabase Auth, JWT `user_id`;
role/tenant resolved server-side); `backend-architecture.md` §5.4 (identity + tenant resolution),
§11 (per-router auth requirements); `docs/planning/sdd/phase-2-curriculum-ingestion-sdd.md` §3, §7.3.

### Context

Phase 2 enforces authentication on `/v1/student` and `/v1/teacher`. Supabase Auth issues JWTs that
identify the **user only** — never the tenant. The backend must verify the JWT and then resolve
`user_id → memberships → tenant/role` server-side, because **mobile-supplied tenant is never
authoritative** (Tenant Isolation invariant, `00-canon.md`). Two verification mechanisms are
available and the choice must be recorded, not left implicit:

1. **Shared HS256 secret** (`SUPABASE_JWT_SECRET`) — simplest; secret lives only in backend env.
2. **Asymmetric / JWKS** (`SUPABASE_JWT_JWKS_URL`) — rotatable keys, no shared secret distribution.

### Decision (to confirm)

Record the selected mechanism here when accepted. Either way, the binding rules are fixed:

- The JWT is verified in `tenancy`/`api` middleware before any handler runs; an invalid/expired
  token is rejected with a uniform error that leaks no analytic vocabulary
  (`backend-architecture.md` §11).
- Tenant and role are resolved from `memberships` server-side; any client-supplied `tenant_id` is
  ignored (`backend-architecture.md` §5.4; SDD §9 `test_authenticated_request_ignores_mobile_supplied_tenant_id`).
- First successful sign-in appends a `consent_recorded` event (Phase 1 registry; ADR-0014;
  `backend-architecture.md` §12.1).

### Consequences

- No mobile-side provider credentials; key custody stays backend-only (`backend-architecture.md` §9.6).
- A red test (`test_jwt_resolves_backend_tenant_and_role`) must exist before implementation
  (`00-canon.md` behavioral rules; SDD §9).
- The unchosen env-var placeholder remains documented (`configuration-reference.md` §10.1) so the
  mechanism can be revised without a schema change.

---

*Document Version 1.0 | Architecture Decision Record Log — 02*