# Agent Instructions

Welcome to the Mindmap Learning Project. To ensure a productive and safe session, please follow these instructions.

## 1. Context First
- **Read this folder first**: Start by reading `CODEBASE_INTELLIGENCE/README.md` and the relevant map files.
- **Verify live state**: Codebases change. Always verify the current state of the code using `view` or `Augment/codebase-retrieval` before proposing changes.
- **Consult the Canon**: Refer to `.augment/rules/00-canon.md` for non-negotiable invariants (e.g., Category Invisibility, Tenant Isolation).

## 2. Tool Usage
- **Primary Tool**: Use `Augment/codebase-retrieval` for semantic search and high-level mapping.
- **Precision**: When editing, use `str-replace-editor` with exact line numbers and string matches.
- **Safety**: Do not run destructive commands or expose secrets.

## 3. Architecture Awareness
- **Modular Monolith**: Respect the boundaries between `app/domain`, `app/api`, `app/events`, and `app/projections`.
- **Hybrid Mobile Rendering**: Understand the split between Skia (edges) and Native Views (nodes).
- **Event Sourcing**: Remember that the `events` table is the source of truth. Do not `UPDATE` or `DELETE` events.

## 4. Documentation & Maintenance
- **Keep it fresh**: If you make architectural changes, update the corresponding file in `CODEBASE_INTELLIGENCE/`.
- **Log your queries**: Add significant discovery queries to `09-augment-query-log.md` to help future sessions.

## 5. Security & Invariants
- **Category Invisibility**: Never expose `analytic_rm` fields to the student API.
- **Tenant Isolation**: Always ensure `tenant_id` is applied and verified server-side.
- **No Mobile Secrets**: Never place API keys or provider credentials in the mobile app.
