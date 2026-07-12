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
| ADR-0015 | Supabase Auth JWT validation strategy | Superseded for live runtime by ADR-0017 |
| ADR-0016 | M3 canvas layout engine: deterministic `d3-hierarchy` | Accepted |
| ADR-0017 | Supabase Auth ES256/JWKS live validation | Accepted |

---

## ADR-0015 — Supabase Auth JWT validation strategy

**Status**: Accepted
**Date**: 2026-06-18
**Phase**: Phase 2 — Curriculum Ingestion
**Source-of-truth refs**: `development-approach.md` §7.1 (Auth = Supabase Auth, JWT `user_id`;
role/tenant resolved server-side); `backend-architecture.md` §5.4 (identity + tenant resolution),
§11 (per-router auth requirements); `docs/planning/sdd/phase-2-curriculum-ingestion-sdd.md` §3, §7.3.

### Context

Phase 2 enforces authentication on `/v1/student` and `/v1/teacher`. Supabase Auth issues JWTs that
identify the **user only** — never the tenant. The backend must verify the JWT and then resolve
`user_id → memberships → tenant/role` server-side, because **mobile-supplied tenant is never
authoritative** (Tenant Isolation invariant, `00-canon.md`). Two verification mechanisms were
available:

1. **Shared HS256 secret** (`SUPABASE_JWT_SECRET`) — simplest; secret lives only in backend env.
2. **Asymmetric / JWKS** (`SUPABASE_JWT_JWKS_URL`) — rotatable keys, no shared secret distribution.

### Decision

**Selected mechanism: HS256 shared secret (`SUPABASE_JWT_SECRET`).**

JWKS placeholder remains in `configuration-reference.md` §10.1 for future rotation without a schema
change. The binding rules are fixed:

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
- The unchosen env-var placeholder (`SUPABASE_JWT_JWKS_URL`) remains documented
  (`configuration-reference.md` §10.1) so the mechanism can be revised without a schema change.
- HS256 is sufficient for MVP; key rotation is a later operational concern tracked in the worklog.

---

## ADR-0016 — M3 canvas layout engine: deterministic `d3-hierarchy`

**Status**: Accepted
**Date**: 2026-06-21
**Phase**: Phase 3 — M3 Canvas maturation
**Source-of-truth refs**: `development-approach.md` §5 M3 (node visualization, 65-node limits, 60fps at
40+ nodes on the reference mid-range Android device), §7.3 (mobile stack: Skia + Reanimated +
Gesture Handler + Zustand); `adr-log.md` ADR-0013 (Hybrid Architecture: Skia for edges/board, native
Views for node content; positions held as shared state); `00-canon.md` (Organic-First invariant).

### Context

M3 must place up to 65 nodes on a pan/zoom canvas and hold 60fps at 40+ nodes on the reference
mid-range Android device. The session board is a **tree**: every node is created via edge-`+`
branching from a single parent (`session_path` projection stores `parent_node_id` from
`payload["source_node_id"]`), so the structure is strictly hierarchical with optional manual
reference links drawn as overlays. The §7.3 stack is locked, but the layout *engine* was the one
open slot. Two candidates were considered:

1. **`d3-force`** — continuous physics simulation; organic but non-deterministic, runs the
   simulation loop on the JS thread every tick until cool-down, and produces different coordinates
   across runs for the same input.
2. **`d3-hierarchy`** — deterministic tidy-tree / radial placement; computes coordinates once per
   structural change, pure function of the tree.

### Decision

**Adopt `d3-hierarchy` (deterministic tidy-tree / radial layout) for the M3 canvas.** `d3-force` is
explicitly **not** adopted for MVP.

Binding rules:

- Layout is computed **once when the tree structure changes** (node added/deleted), not per frame.
  Output coordinates are written to the canonical Zustand store and mirrored to Reanimated
  SharedValues for gesture-driven pan/zoom, per ADR-0013's "positions as shared state".
- Manual reference links are drawn as Skia overlay curves **outside** the layout engine; they do not
  feed back into node placement.
- A user drag overrides the computed position for that node and persists locally; re-running layout is
  a deliberate, user- or structure-triggered action, never a background loop.
- `d3-hierarchy` is a pure-JS dependency with no native module footprint, so it adds no Skia↔native
  coordinate-seam risk beyond the existing hybrid boundary.

### Consequences

- **Serves Organic-First**: the tree is grown organically by selection-driven branching; deterministic
  *placement* of that organic structure does not reintroduce any pre-classification or central
  planning of content — classification remains post-hoc and async, untouched by layout.
- **Protects the 60fps gate**: eliminating the continuous physics loop removes per-frame JS-thread work,
  leaving the frame budget to Skia rendering and Reanimated gesture handling. This is the primary
  reason for choosing determinism over physics at this node scale.
- **Replay-friendly**: deterministic coordinates make board screenshots and tests reproducible.
- **Escalation path**: if future measurement shows `d3-hierarchy` placement is visually inadequate for
  dense reference-link graphs, `d3-force` may be revisited via a superseding ADR — deferred until
  measured, consistent with the project's defer-until-evidence posture.
- Red tests for layout determinism precede M3 layout code (`00-canon.md` behavioral rules; active SDD §9).

---

## ADR-0017 — Supabase Auth ES256/JWKS live validation

**Status**: Accepted
**Date**: 2026-07-10
**Phase**: Phase 3 — M4 runtime/closure remediation
**Supersedes**: ADR-0015 for the live Supabase runtime; HS256 remains test-fixture compatibility
**Source-of-truth refs**: `development-approach.md` §7.1; `backend-architecture.md` §§5.4, 5.5,
9.6, and 11; `phase-3-m4-runtime-closure-remediation-sdd.md` §§2-5.

### Context

ADR-0015 selected a shared HS256 secret before the target Supabase project was exercised. The live
project `jbmqyxhrmcbdgardamrp` issues ES256 access tokens with a JWKS `kid`. The M4 browser smoke
therefore failed until an uncommitted JWKS compatibility path was added. Leaving the accepted ADR
on HS256 while silently deploying ES256 would make auth behavior and configuration unauditable.

### Decision

The live backend validates Supabase access tokens with the project's ES256 JWKS endpoint.

Binding rules:

- Validate the signature using the key selected by `kid` from the configured/derived JWKS URL.
- Accept only the configured asymmetric algorithm for the live path.
- Validate `iss`, `aud=authenticated`, expiration, and required UUID-shaped `sub`.
- Apply a fixed 30-second clock-skew tolerance to ES256 `iat`, `nbf`, and expiration validation;
  do not disable temporal-claim validation. Tokens outside that bounded tolerance fail closed.
- Resolve tenant and role only from backend-owned memberships after token verification.
- Cache signing keys through the JWT/JWKS client and fail closed when keys/configuration cannot be
  resolved.
- `SUPABASE_URL` or explicit issuer/JWKS variables are backend runtime configuration. They are not
  mobile secrets.
- HS256 tokens are permitted only in deterministic local/test fixtures unless a future Supabase
  project explicitly requires a new accepted decision.
- The client uses only the project URL and active publishable/anon key; it never receives signing
  secrets, service-role keys, database credentials, or provider credentials.

### Consequences

- The implementation now matches the real Supabase signing configuration and supports key rotation
  without distributing a shared signing secret.
- Render/local production startup must supply and validate the Supabase issuer/JWKS configuration.
- Auth tests require both deterministic mocked-JWKS coverage and a separately gated live token
  smoke; CI never depends on the network.
- Boundary tests prove a token 20 seconds ahead is accepted while a token 120 seconds ahead is
  rejected, preserving a bounded distributed-clock allowance.
- ADR-0015 remains historical context for the earlier HS256 decision but no longer governs the
  live runtime.

---

*Document Version 1.3 | Architecture Decision Record Log — 02*
