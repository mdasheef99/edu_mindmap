# 08 Future Work Readiness

**2026-07-11 update**: physical-device remediation has landed for dashboard latency, persisted
consent, and sign-out/re-login handling. Retest this exact native path before closing M4.

**Snapshot**: 2026-07-10. M4 implementation is not “still planned”: automated remediation is
complete. M4 is not closed until its three remaining human/operational gates pass.

## Read Before Changing Code

1. `.augment/rules/00-canon.md`.
2. Source hierarchy in order: `development-approach.md`, `backend-architecture.md`, ADR logs,
   `session-path-data-contract.md`, master PRD, MVP feature specification.
3. `docs/planning/sdd/phase-3-m4-runtime-closure-remediation-sdd.md`.
4. `docs/planning/worklog-v10.md`.
5. The relevant maps in this folder, then verify the actual code and tests.

Every new requirement/edit must trace to a source-of-truth section. Do not use superseded docs or
introduce Redis Streams, Celery, TimescaleDB, legacy event tables, or client-side AI credentials.

## Immediate Next Actions

0. Retest the fixed native Android path on the physical device, including sign out and sign in again
   on the same account.

1. Complete the native Android stranger signup → dashboard → Electricity → canvas/resume gate.
2. Complete the interactive web CanvasKit render gate.
3. Complete pooled non-bypass app-role cross-tenant RLS verification.
4. Record evidence in the active SDD/worklog and close M4 only if all acceptance criteria pass.
5. Do not start M5 merely because automated tests are green.

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
