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

- **Phase 1 — Walking Skeleton** is in progress. The main remaining proof items are remote CI,
  deployment, and physical-device mobile verification per the active SDD.

---

## ADR Numbering

Continue numbering from ADR-0015. Do not renumber or move earlier decisions from the previous file.

## Index

| ADR | Title | Status |
|-----|-------|--------|

---

*Document Version 1.0 | Architecture Decision Record Log — 02*