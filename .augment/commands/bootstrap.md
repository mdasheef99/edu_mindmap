# /bootstrap - re-establish M4 context

Re-ground yourself in the Context Continuity Framework before doing anything else.
Read the following, in order, then state the current M4 status back to the user before proposing
or editing anything:

1. `.augment/rules/00-canon.md` - the canon, hierarchy, invariants, and blacklist.
2. `docs/planning/development-approach.md` - active milestone order and execution discipline.
3. `docs/architecture/backend-architecture.md` - backend invariants, tenancy, auth, event store,
   read models, and API boundaries.
4. `docs/architecture/adr-log.md`
5. `docs/architecture/adr-log-02.md`
6. `docs/planning/session-path-data-contract.md`
7. `docs/prd/master-prd.md`
8. `docs/mvp-features-specification.md`
9. `docs/api/student-api-spec.md`
10. `docs/database/core-operational-schema.md`
11. `docs/database/schema-traceability-and-validation.md`
12. `docs/configuration-reference.md`
13. `docs/planning/testing-strategy.md`
14. `docs/planning/sdd/phase-3-m4-curriculum-auth-sdd.md` - the active blueprint.
15. `docs/planning/worklog-v9.md` - the live tracker.

Report:

- M4 scope and status.
- Supabase project warning: MCP currently exposes `ahntbtktjjmvfosgkmgn`
  (`Bookconnect_reactexpo`), while local Mindmap `.env` points at `jbmqyxhrmcbdgardamrp`.
- The active SDD and tracker paths.
- Any implementation gate that must happen before code changes, including red tests first.

## Rules for this re-grounding

- Resolve ambiguity using the Source-of-Truth hierarchy in `00-canon.md`; higher-ranked documents
  win on conflict.
- Every requirement or edit you propose must cite a specific source-of-truth section. Do not
  originate requirements.
- Honor Category Invisibility, Organic-First, Tenant Isolation, Event Sourcing, and no mobile-side
  AI/TTS credentials.
- Do not propose or edit until you have stated the current status back to the user.
