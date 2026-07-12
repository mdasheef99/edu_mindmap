# Codebase Intelligence Pack

**2026-07-12 update**: M4 is closed. The bounded pre-M5 canvas stabilization record is complete:
position lifecycle, dragged-edge synchronization, and edge-plus feedback/single-flight behavior
are automated-green and Android-reviewed. M5 remains frozen.

**2026-07-12 update**: M4 is closed. The bounded pre-M5 canvas stabilization record is complete:
position lifecycle, dragged-edge synchronization, and edge-plus feedback/single-flight behavior
are automated-green and Android-reviewed. M5 remains frozen.

This folder is a durable orientation map for the Mindmap Learning Project. It reduces rediscovery
cost, but it does not override canon or the source-of-truth hierarchy.

**Current snapshot**: 2026-07-12 — read `canvas-position-write-lifecycle-sdd.md` v0.6 and
`worklog-v10.md` for the completed bounded record and remaining gates. It is not a formal M4.5
milestone.

## Required Reading Order

1. `.augment/rules/00-canon.md`
2. Active SDD and worklog named by canon
3. Source hierarchy named by canon
4. `AGENT_INSTRUCTIONS.md`
5. Relevant maps below
6. Current code, tests, migrations, and live read-only evidence

## Contents

1. `01-system-map.md` — current production/test composition, mobile structure, and runtime paths.
2. `02-critical-flows.md` — auth/bootstrap, dashboard/catalog, consent/session/root, branching,
   worker, resume/hydration, ordered position writes/recovery, and deletion flows.
3. `03-backend-data-map.md` — Postgres adapters, auth/consent, schemas, jobs, and remaining RLS gate.
4. `04-feature-inventory.md` — milestone ownership/status and reuse boundaries.
5. `05-security-risk-map.md` — Category Invisibility, tenancy, event sourcing, secrets, and risks.
6. `06-testing-verification-map.md` — commands, latest evidence, and human/operational gates.
7. `07-deployment-ops-map.md` — Render/Expo/Supabase services, env names, migrations, and health.
8. `08-future-work-readiness.md` — device review, explicit deferred slices, honest gaps, and likely
   touchpoints.
9. `09-augment-query-log.md` — Augment queries and clearly labeled direct-verification refreshes.

## Maintenance Rules

- Verify live state before relying on a map; dates and remaining gates matter.
- When Augment is available, use it to focus semantic retrieval. When it is not, use direct evidence
  and label that evidence honestly.
- Keep exact paths concise, update affected maps after architectural changes, and record significant
  discovery in the log.
- Never place secrets, bearer tokens, database credentials, or private Supabase keys in this pack.
- Requirements must trace upward to canon's source hierarchy; maps may describe but never invent
  behavior.
