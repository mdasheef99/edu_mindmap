# 04 Feature Inventory

**2026-07-12 update**: M4 is closed. Bounded pre-M5 canvas stabilization is complete and
Android-reviewed; M5 is frozen.

**Snapshot**: 2026-07-10.

## M4 Curriculum Entry and Supabase Auth

- **Status**: closed 2026-07-11. Interactive web remains a non-blocking follow-up.
- **Mobile**: `mobile/M4CurriculumAuthScreen.tsx`, `mobile/m4/useM4AppFlow.ts`,
  `mobile/m4/supabaseAuth.ts`, `mobile/m4/sessionStore.ts`, `mobile/m4/studentApi.ts`.
- **Backend**: `backend/app/api/student/{auth,curriculum,dashboard,sessions}.py`,
  `backend/app/runtime/{postgres_runtime,curriculum_workflow,session_workflow}.py`, and concrete
  Postgres adapters under `events/`, `tenancy/`, and `projections/`.
- **Behavior**: email/password auth, refresh restore/remote sign-out, idempotent B2C membership
  bootstrap with persisted consent state, tenant-scoped progressive dashboard/resume, API-derived
  Electricity launch, explicit consent, deterministic root/branch generation, durable worker
  classification.
- **Scope limit**: the current curriculum surface is the accepted Class 10 → CBSE → Science →
  Electricity path, not a general multi-choice catalog picker. Phone/OTP, B2B activation, admin
  panels, and live LLM generation are deferred by the M4 SDD.

## M3/M3-B/M3.5/M3.6 Canvas

- **Status**: closed locally; physical performance gates recorded separately in canon/worklogs.
- **Ownership**: `mobile/canvas/`.
- **Core**: `SkiaCanvas.tsx`, `CanvasEdges.tsx`, `NodeChip.tsx`, `CanvasToolbar.tsx`, `store.ts`,
  `useCanvasGestures.ts`, `useSessionHydration.ts`, viewport culling, render budgets, discovery,
  deletion reconciliation, zoom/fit/reset/snap controls.
- **Pattern**: Skia edges + native node overlays, Zustand transient state, Reanimated/Gesture
  Handler transforms, hierarchy layout.

## Bounded Pre-M5 Canvas Position Lifecycle

- **Status**: completed bounded stabilization record; Android review accepted 2026-07-12.
  This is not a formal M4.5 milestone and does not authorize M5.
- **Ownership**: `mobile/canvas/apiClient.ts`, `nodePositionCoordinator.ts`,
  `useNodePositionWrites.ts`, `SkiaCanvas.tsx`, and `EdgeOfferSetSheet.tsx`.
- **Behavior**: checked position PATCHes; independent per-node FIFO; newest-intent visibility;
  acknowledged/baseline reconciliation; stale-hydration protection for mounted-session authority;
  neutral retry aggregation; session/disposal isolation; branch-child placement retry without
  branch recreation; idempotent Close and reload.
- **Explicit exclusions**: deterministic layout, `{0,0}` fallback replacement,
  `manual_reference` hierarchy correction, offline/persistent delivery, backend branch atomicity,
  optimistic insertion, navigation, and checkpoints.

## M2 Phrase Selection

- **Status**: closed on physical Android.
- **Files**: `mobile/PhraseSelectionReaderSheet.tsx`, the optional
  `mobile/app/M2PhraseSmokeScreen.tsx`, phrase offer-set routers/workflows, and their tests.
- The smoke screen is retained for closed-milestone diagnostics; it is not the M4 entry point.

## M1 Session/Event Infrastructure and M3-C

- **Status**: locally complete, with older operational gates documented in canon.
- **Ownership**: append-only events, session-path projections, offer-set logging, resume/hydration,
  deletion cascade, event registry, Postgres queue, and async classification wiring.

## Phase 2 Curriculum Analysis

- **Status**: closed.
- **Files**: `backend/app/chapter_analysis/`, `backend/app/projections/curriculum*.py`,
  `backend/app/llm_gateway/chapter_analysis_fixture.py`, and `curriculum` schema migrations/tests.

## Reuse Rules

- `InMemory*` stores and `SessionRuntime.for_testing()` are for tests and explicit smoke fixtures,
  never normal production composition.
- Files directly under `mobile/` are not automatically legacy: M4 and shared reader components live
  there. Determine status from `App.tsx`, canon, and the active SDD before reusing or deleting them.
- New generation/classification behavior must preserve the import-linter seams and Organic-First
  async boundary.

## 2026-07-12 Stabilization Completion

The bounded pre-M5 canvas record is Android-reviewed and complete. In addition to the position
lifecycle and branch-placement recovery, it includes active-drag edge SharedValue synchronization
and edge-plus local busy/single-flight/retry behavior. It is not a formal M4.5 milestone; M5
remains frozen.
