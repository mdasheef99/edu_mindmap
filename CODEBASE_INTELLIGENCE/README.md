# Codebase Intelligence Pack

This folder contains a durable semantic map of the Mindmap Learning Project. It is designed to provide high-value architectural and operational knowledge to developers and AI agents.

## Purpose
The primary goal is to ensure that any session—human or AI—starts with a clear understanding of the project's invariants, boundaries, and critical flows, reducing the risk of architectural drift or security violations.

## When to Read
- **Before starting work** on a new feature or refactor.
- **When Augment/codebase-retrieval is available**, use these maps to focus your queries.
- **After major architectural changes**, update the relevant map files.

## Contents
1. **01-system-map.md**: High-level architecture, entry points, and runtime patterns.
2. **02-critical-flows.md**: Key user and business workflows.
3. **03-backend-data-map.md**: API, DB, Auth, and Storage integration.
4. **04-feature-inventory.md**: Ownership map of major modules.
5. **05-security-risk-map.md**: Security boundaries, invariants, and risks.
6. **06-testing-verification-map.md**: Testing setup and verification guidance.
7. **07-deployment-ops-map.md**: Env vars, CI/CD, and operational caveats.
8. **08-future-work-readiness.md**: Recommended reading and next steps.
9. **09-augment-query-log.md**: Log of Augment queries used to build this pack.

## How to Update
- Use `Augment/codebase-retrieval` to verify the current state.
- Keep descriptions concise and link to exact file paths.
- Clearly mark assumptions or stale information.
- Follow the "Mindmap Canon" in `.augment/rules/00-canon.md`.
