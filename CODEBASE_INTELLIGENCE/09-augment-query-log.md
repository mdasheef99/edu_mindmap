# 09 Augment Query Log

This log records the significant queries run via `Augment/codebase-retrieval` during the creation of this intelligence pack.

## 2026-06-24: Initial Pack Generation

### Query 1: High-level architecture
**Prompt**: “Map this codebase at a high level. Identify major architecture layers, entry points, routing/navigation, state management, backend/data integration, feature modules, tests, configuration, deployment, and documentation. Include exact file paths and concise notes.”
**Key Findings**:
- Confirmed Event-Sourced Modular Monolith for backend.
- Confirmed Hybrid Rendering (Skia + Native Views) for mobile.
- Identified `backend/app/main.py` and `mobile/app/index.ts` as entry points.

### Query 2: Critical flows & Data Integration
**Prompt**: “Identify the most important user and business workflows in this project. For each flow, list the screens/components/services/hooks/APIs/database tables/jobs involved, with exact file paths. Identify backend/data integration in this repo. Identify API clients, database access, migrations/schema, auth/session handling, storage, background jobs, server functions, generated types, mocks, and known security/privacy caveats.”
**Key Findings**:
- Mapped Session Start, Offer Choice, Node Generation, and Canvas Hydration.
- Confirmed Supabase stack (Postgres, Auth, Storage).
- Identified "Category Invisibility" and "Tenant Isolation" as core security invariants.

### Query 3: Feature Ownership, Testing, Security, & Readiness
**Prompt**: “Map all major feature modules. For each feature, identify what it owns, key screens/components/services/hooks/types/tests, reusable patterns, and areas that should not be reused without review. Map the testing system. Identify test framework, setup files, mocks, representative tests, useful focused test commands, e2e/smoke tests, typecheck/lint/build commands, and verification risks. Identify security-sensitive areas, authorization boundaries, secret handling, privacy/PII handling, payment/financial logic, admin/operator flows, data deletion/export behavior, and any risky patterns future agents must not copy. Given the current codebase, identify what future agents should read first, what files are likely touchpoints for new feature work, what docs may be stale, and what assumptions need live verification.”
**Key Findings**:
- Detailed the testing strategy (Pytest, Jest, Import Linter).
- Highlighted risks around 60fps performance and event replay latency.
- Identified next steps (Milestone M4: Supabase Auth + Curriculum).
