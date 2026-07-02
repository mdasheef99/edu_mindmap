# Phase 3 M4 Curriculum Auth Plan Index

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement these plans task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the M4 B2C learner entry loop: Supabase email/password auth, Class 10 -> CBSE -> Science -> Electricity curriculum navigation, dashboard re-entry, consent capture, and fixture-backed Electricity canvas start/resume.

**Architecture:** Keep the M4 SDD as the governing milestone design. Execute M4 as four small, red-test-first slices so each change remains reviewable and traceable to the source-of-truth hierarchy.

**Tech Stack:** FastAPI, Pydantic, PyJWT, Postgres/Supabase SQL, pytest, Expo React Native, Supabase JS, Jest, React Native Testing Library, Zustand/canvas modules already in place.

---

## Current Status

- Branch: `codex/phase-3-m4-curriculum-auth`
- M4 SDD: `docs/planning/sdd/phase-3-m4-curriculum-auth-sdd.md`
- Worklog: `docs/planning/worklog-v9.md`
- M4 implementation status: not started when this index was created.
- Supabase warning: MCP is connected to the wrong project (`ahntbtktjjmvfosgkmgn` / Bookconnect). Generate SQL locally and have the owner apply it manually to Mindmap project ref `jbmqyxhrmcbdgardamrp`.

## Execution Slices

1. [Backend Auth + B2C Bootstrap](./2026-07-02-m4-backend-auth-bootstrap.md)
2. [Curriculum Catalog + Dashboard + Manual SQL](./2026-07-02-m4-curriculum-dashboard-sql.md)
3. [Fixture Electricity Session + Generation Flow](./2026-07-02-m4-fixture-electricity-flow.md)
4. [Mobile Auth + Curriculum + Canvas Handoff](./2026-07-02-m4-mobile-auth-canvas-handoff.md)

Execute in order. Do not start slice 2 until slice 1 tests are green, and so on.

## Shared Canon

Every slice must trace to:

- `docs/planning/development-approach.md` Section 5 M4 and Sections 6-8.
- `docs/architecture/backend-architecture.md` Sections 5.3-5.5, 6, 7.1, 9-12.
- `docs/architecture/adr-log.md` ADR-0001, ADR-0002, ADR-0003, ADR-0004, ADR-0007, ADR-0008, ADR-0014.
- `docs/architecture/adr-log-02.md` ADR-0015.
- `docs/planning/session-path-data-contract.md` Sections 5-11.
- `docs/prd/master-prd.md` Sections 4-7.
- `docs/mvp-features-specification.md` Feature Groups 1-4 and 7.1.
- `docs/api/student-api-spec.md` Sections 2-5 and 8.
- `docs/database/core-operational-schema.md` Sections 2, 3, 5, 6.
- `docs/database/schema-traceability-and-validation.md` Sections 2-7.
- `docs/configuration-reference.md` Sections 9-10.
- `docs/planning/testing-strategy.md` Sections 1-6.
- `docs/planning/sdd/phase-3-m4-curriculum-auth-sdd.md` Sections 4-14.

## Non-Negotiable Execution Rules

- Red tests before production code.
- Student APIs must stay category-invisible.
- Backend-resolved tenant and membership only; ignore mobile-supplied tenant IDs.
- Use fixture-backed Electricity generation only; no live LLM calls.
- Do not apply migrations through MCP.
- After Python tests, delete `*.pyc` and verify remaining `.pyc` count is zero.
- Update the M4 SDD parity table and `worklog-v9.md` only after verified implementation work.
