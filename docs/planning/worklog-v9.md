# AGENT ROTATION INSTRUCTION - READ FIRST

This is the active worklog as of 2026-07-02. Read this file after the source-of-truth hierarchy
and before making M4 code or schema changes.

Legacy context:

- `docs/planning/worklog-v8.md` is now a closed archive. It covers post-M3-C housekeeping,
  M3.5 frontend readiness verification, M3.6 canvas controls, the canvas TypeScript/Jest config
  blocker resolution, and the M4 SDD draft.
- M3-C, M3.5, and M3.6 are locally complete. Do not reopen them unless explicitly requested.
- M4 is the active milestone: curriculum entry, Supabase Auth, dashboard re-entry, consent
  capture, and fixture-backed Electricity canvas flow.
- Active SDD: `docs/planning/sdd/phase-3-m4-curriculum-auth-sdd.md`.
- Supabase MCP currently exposes the wrong project: `ahntbtktjjmvfosgkmgn`
  (`Bookconnect_reactexpo`). The local Mindmap `.env` points at project ref
  `jbmqyxhrmcbdgardamrp`. Do not apply migrations through MCP in this session unless the MCP
  account/project access changes and is re-verified.
- The owner intends to run the generated SQL manually against the correct Supabase database.

Required reading order for M4 implementation sessions:

1. `.augment/rules/00-canon.md`
2. `docs/planning/development-approach.md`
3. `docs/architecture/backend-architecture.md`
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
14. `docs/planning/sdd/phase-3-m4-curriculum-auth-sdd.md`
15. `docs/planning/worklog-v9.md`

Current implementation status:

- M4 SDD is drafted, not implemented.
- B2C individual signup is first. School/B2B roster or invite activation is deferred.
- Auth path is Supabase email/password for M4. Phone/OTP is deferred behind the same Supabase
  identity model.
- Real LLM generation is deferred. M4 uses a deterministic fixture-backed Electricity generation
  provider that mimics real node creation through the backend/event/canvas boundaries.
- Launch curriculum path is Class 10 -> CBSE -> Science -> Electricity, with about 10
  fixture-backed Electricity nodes.

---

### 2026-07-02 - Worklog v9 opened for M4 implementation planning

**Milestone context**: M4 is active planning/implementation-next. M3-C, M3.5, and M3.6 are locally
complete.

**Spec sections used**:
- `development-approach.md` Section 5 M4 and Section 8.1 worklog rotation guidance.
- `.augment/rules/00-canon.md` active milestone and source-of-truth hierarchy.
- `phase-3-m4-curriculum-auth-sdd.md` Sections 3, 7, 13, and 14.

**Work completed**:
- Rotated `docs/planning/worklog-v8.md` to closed archive status.
- Created this `docs/planning/worklog-v9.md` as the active tracker for M4.
- Recorded required M4 reading order for a fresh implementation session.
- Preserved the Supabase project warning: MCP-visible project is not the Mindmap project.
- Updated `.augment/rules/00-canon.md`, `docs/planning/development-approach.md`,
  `docs/planning/session-bootstrap.md`, `.augment/hooks/session-context.sh`, and
  `.augment/commands/bootstrap.md` so new sessions point at M4, the M4 SDD, and this worklog.

**Gate status**: Ready for M4 implementation planning after user approval of the SDD.
