# 08 Future Work Readiness

**2026-07-13 update**: M4 is closed; the bounded canvas position-lifecycle reconstruction is
locally complete and awaits owner approval. M5 has not started.

**Snapshot**: 2026-07-13. Do not reopen M4 or broaden the canvas stabilization into M5.

## Read Before Changing Code

1. `.augment/rules/00-canon.md`.
2. Source hierarchy in order: `development-approach.md`, `backend-architecture.md`, ADR logs,
   `session-path-data-contract.md`, master PRD, MVP feature specification.
3. `docs/planning/sdd/canvas-position-write-lifecycle-sdd.md` for this local integration, then the
   closed M4 SDDs for M4 behavior.
4. `docs/planning/worklog-v11.md`.
5. The relevant maps in this folder, then verify the actual code and tests.

Every new requirement/edit must trace to a source-of-truth section. Do not use superseded docs or
introduce Redis Streams, Celery, TimescaleDB, legacy event tables, or client-side AI credentials.

## Immediate Next Actions

1. Review the local canvas stabilization diff; push or open a draft PR only with owner approval.
2. If explicitly scheduled, rerun the 40+ node performance and 65-node physical-device smoke.
3. Keep interactive web rendering as a separately scoped non-blocking follow-up.
4. Do not start M5 merely because this bounded integration is green.

## Honest Product Gaps Within M4

- The current mobile curriculum surface derives the accepted Electricity launch path from the API,
  but it does not yet let the learner choose arbitrary classes/exams/subjects/chapters.
- M4 deliberately uses deterministic fixture generation, not a live LLM.
- Phone/OTP auth, B2B roster/invite activation, institutional consent administration, admin/content
  panels, and general catalog UX are deferred by the M4 SDD.

## Likely Touchpoints

- Auth/session lifecycle: `mobile/m4/`, `backend/app/api/student/auth.py`, tenancy adapters.
- Curriculum UI/API: `mobile/M4CurriculumAuthScreen.tsx`, `mobile/m4/studentApi.ts`, catalog adapters.
- Canvas interactions: `mobile/canvas/`.
- Events: registry + domain builder + projection + replay tests.
- New Postgres behavior: runtime port, concrete adapter, forward migration, pooled isolation test.
- AI: `backend/app/llm_gateway/` with fixture/schema tests and usage accounting.

## Later Optimization Candidates

- Versioned session snapshots if measured event replay latency becomes material.
- General curriculum picker only when scheduled by a higher-ranked requirement/SDD.
- Broader device/platform performance gates as scheduled by `development-approach.md`.
