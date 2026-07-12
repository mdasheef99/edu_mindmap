# Agent Instructions

## 1. Canon and Source Hierarchy First

Before proposing or editing:

1. Read `.augment/rules/00-canon.md` completely and state the active milestone.
2. Read the active SDD and live worklog named by canon.
3. Resolve ambiguity using the full source hierarchy in canon, in order.
4. Read this pack for orientation, then verify relevant claims in the current code/tests.

Every requirement and code edit must cite a source-of-truth section. Do not originate product
requirements from this pack; it is a navigational snapshot, not higher authority.

## 2. Discovery and Editing Tools

- If Augment/codebase-retrieval is actually available, use it for semantic mapping and record
  significant queries in `09-augment-query-log.md`.
- If it is unavailable, say so and use repository-native evidence (`rg`, direct file reads, tests,
  migration inspection, and configured MCP/database readback). Do not pretend direct search was an
  Augment query.
- Use the editing mechanism available in the current environment (`apply_patch` for Codex). Do not
  require a tool such as `str-replace-editor` when it is not installed.
- Preserve unrelated dirty-worktree changes and never expose secrets in commands, logs, docs, or
  responses.

## 3. Architecture and Security

- Preserve the modular boundaries among API, domain, runtime ports/workflows, adapters, events,
  projections, workers, and observability.
- Student API must never import/read analytic internals or expose analytic fields.
- Backend-resolved membership owns `tenant_id`; mobile tenancy is never authoritative.
- Pooled Postgres work must use transaction-local tenant context; RLS is the backstop.
- Events are append-only and registry-validated. Worker-only events cannot come from clients.
- Generation stays independent of classification; only selected choices enqueue async classify.
- No AI/TTS/database/service-role credentials in mobile code.

## 4. Implementation Discipline

- Follow red tests before production code as required by the active SDD.
- Keep source files under the canon's 300–350-line limit; split cohesive concerns before adding more.
- Reuse shared infrastructure helpers rather than copying tenant/RLS/queue/accounting patterns.
- In-memory stores are test adapters, not normal production fallbacks.
- After Python tests, remove all generated `*.pyc` and verify the count is zero.

## 5. Documentation Maintenance

- Update the relevant pack files when runtime architecture, flows, gates, env names, or risk state
  materially changes.
- Update the active SDD/worklog for milestone evidence; this pack does not replace them.
- Mark assumptions and remaining human gates explicitly. Automated bundle/export success is not a
  physical-device or interactive-browser result.
