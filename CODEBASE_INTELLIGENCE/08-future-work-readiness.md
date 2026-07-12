# 08 Future Work Readiness

**2026-07-12 update**: M4 is closed. Bounded pre-M5 canvas stabilization is complete and
Android-reviewed. M5 remains frozen.

**Snapshot**: 2026-07-11. The current active bounded design record is
`docs/planning/sdd/canvas-position-write-lifecycle-sdd.md`; it is not a formal M4.5 milestone.

## Read Before Changing Code

1. `.augment/rules/00-canon.md`.
2. Source hierarchy in order: `development-approach.md`, `backend-architecture.md`, ADR logs,
   `session-path-data-contract.md`, master PRD, MVP feature specification.
3. `docs/planning/sdd/canvas-position-write-lifecycle-sdd.md`.
4. `docs/planning/worklog-v10.md`.
5. The relevant maps in this folder, then verify the actual code and tests.

Every new requirement/edit must trace to a source-of-truth section. Do not use superseded docs or
introduce Redis Streams, Celery, TimescaleDB, legacy event tables, or client-side AI credentials.

## Immediate Next Actions

1. Complete the bounded physical Android canvas review and record only observed behavior.
2. Decide whether the bounded stabilization increment can close; do not formalize M4.5 without an
   explicit owner decision supported by the audit/evidence.
3. Keep deterministic layout, `{0,0}` fallback correction, `manual_reference` hierarchy changes,
   persistent/offline writes, and backend branch atomicity in later separately approved slices.
4. Keep interactive web CanvasKit rendering and deferred M3 performance checks as explicit
   follow-ups rather than silently folding them into the position lifecycle.
5. Do not start M5 merely because automated tests are green.

## Honest Product Gaps Within M4

- The current mobile curriculum surface derives the accepted Electricity launch path from the API,
  but it does not yet let the learner choose arbitrary classes/exams/subjects/chapters.
- M4 deliberately uses deterministic fixture generation, not a live LLM.
- Phone/OTP auth, B2B roster/invite activation, institutional consent administration, admin/content
  panels, and general catalog UX are deferred by the M4 SDD.

## Known Canvas Position-Lifecycle Limits

- No causal snapshot revision/event watermark exists, so cross-device freshness is undefined.
- In-memory queued delivery is not guaranteed across unmount, application termination, or restart.
- Branch creation and initial child positioning remain separate, non-atomic backend operations.
- An unpositioned child may still hydrate at the existing `{0,0}` fallback.
- Device interaction and performance evidence is not replaced by unit tests or LAN readiness.

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

## 2026-07-12 Next Boundary

The bounded position/interaction stabilization record is complete and must not silently grow. The
next work requires a separately approved SDD: either M5 checkpoints, or a later canvas layout and
position-quality slice. Keep deterministic layout, `{0,0}` fallback, `manual_reference` hierarchy,
persistent delivery, backend branch atomicity, performance gates, and interactive web review as
explicit decisions rather than incidental follow-ons.
