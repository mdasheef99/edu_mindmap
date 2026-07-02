# Phase 3 M3.5 Frontend Readiness SDD

**Status**: Verified / Complete for M3.5 bridge phase
**Date**: 2026-06-25
**Owner intent**: harden the already-built learner-facing M1-M3/M3-C surface before beginning M4.
**Closure evidence**: automated Jest tests green + successful physical device Expo Go verification.

---

## 1. Goal

M3-C is locally complete and M4 is the next canonical milestone. This M3.5 readiness pass is a
bounded bridge: make the existing canvas, phrase-selection, edge-branching, and session
rehydration surfaces credible enough to attach real M4 auth/curriculum entry to them.

The goal is not to build M4. The goal is to remove obvious dev-only roughness and close
frontend-visible gaps in the features already claimed complete by M2, M3, M3-B, and M3-C.

---

## 2. Source-of-Truth References

- `.augment/rules/00-canon.md`: current milestone status, source-of-truth hierarchy, red-tests-first,
  Category Invisibility, file-size constraints.
- `docs/planning/development-approach.md` §5: M2 phrase selection, M3 canvas maturation, M3-C
  infrastructure remediation, M4 next milestone.
- `docs/mvp-features-specification.md` Feature Group 3 (Mind Map Canvas), Feature Group 4
  (AI Exploration Nodes), Feature 7.1 (session persistence/basic offline reopen boundary).
- `docs/planning/sdd/phase-3-m3b-canvas-feature-parity-sdd.md` §1-§9: edge labels, edge `+`,
  node selection/toolbar, culling, node limits.
- `docs/planning/sdd/phase-3-m3c-infrastructure-remediation-sdd.md` §3-§11: event ingest,
  session hydration, node position persistence, delete/branch reconciliation.
- `docs/planning/session-path-data-contract.md` §6, §8, §9, §10: node contract, interaction
  events, offer-set/thread context, deletion cascade.
- `docs/api/student-api-spec.md` §5-§8: session, node, offer-set, and offer-choice endpoints.
- `docs/architecture/adr-log-02.md` ADR-0013 and ADR-0016: hybrid canvas seam and deterministic
  layout expectations.

---

## 3. Scope

### In Scope

| Ref | Readiness item | Why now |
|---|---|---|
| F1 | Canvas empty/loading/error states are learner-safe and visibly recoverable | M3-C hydration is real; failures should not look like a blank app |
| F2 | Node chip content prefers student-safe title/body fields over raw UUID labels where available | Browser-visible canvas currently reads as dev data |
| F3 | Edge `+` flow exposes offer-set loading/error/disabled states without silent failure | M3-B claims edge `+`; M4 users must be able to trust it |
| F4 | Edge offer-choice branch creation triggers a session reload and leaves visible canvas state consistent | M3-C rehydration must prove branch reconciliation from the UI |
| F5 | Phrase-selection smoke flow keeps full `node_created`/`edge_created` propagation visible enough for local QA | M2/M3-C contract should remain testable before M4 hides it behind auth |
| F6 | Node delete and node position persistence have focused UI-level tests covering reload/reconcile behavior | M3-C Seam C should stay protected |
| F7 | `SkiaCanvas.tsx` does not receive new behavior until `NodeChip`/overlay concerns remain extracted or the file stays within canon limits | Canon file-size constraint |

### Out of Scope

- Supabase Auth, signup, OTP, logout, account recovery.
- Curriculum onboarding, class/exam/subject/chapter browser, dashboard, real session selection.
- PYQ, podcast, checkpoints, teacher dashboard, admin surfaces.
- In-node text selection; Reader bottom-sheet remains the MVP phrase-selection path.
- New backend product endpoints unless a readiness test reveals a regression in already-scoped
  M1-M3/M3-C endpoints.
- Image/video enrichment tiers, advanced connectivity, topology/steering, or broader offline sync.

---

## 4. Current Frontend Baseline

- `mobile/app/App.tsx` still uses dev constants for `apiBaseUrl`, `sessionId`, and auth token.
  This is acceptable before M4 but must be visually explicit and non-confusing in dev mode.
- `mobile/canvas/useSessionHydration.ts` fetches `GET /v1/student/sessions/{id}` and maps
  `canvas.nodes`/`canvas.edges`.
- `mobile/canvas/SkiaCanvas.tsx` wires node selection, node deletion, edge `+`, node limits,
  node visit events, viewport events, and reload callback hooks.
- `mobile/PhraseSelectionReaderSheet.tsx` supports the Reader bottom-sheet flow and propagates
  branch payloads.
- The in-app browser can render the local web build, but web is an inspection surface; MVP
  platform remains React Native iOS/Android.

---

## 5. Design

### 5.1 Canvas Status Overlay

`App.tsx` may keep a dev-only canvas screen until M4 supplies real session selection, but its
status overlay must distinguish:

1. loading session state,
2. backend hydration failure,
3. successful empty canvas,
4. ready canvas.

The messages must remain category-neutral and must not expose event payload details, analytic
fields, or internal dimensions.

### 5.2 Node Presentation

`NodeChip` should render the most learner-meaningful student-safe text available from
`CanvasNode`:

1. title/header/question text if present,
2. short body/content text if present,
3. compact node id fallback only when no learner-safe content exists.

No node body editing is introduced. This is display-only.

### 5.3 Branching Surfaces

Edge `+` and phrase-selection flows should make these states observable in tests and local QA:

- request started,
- offer set displayed,
- choice accepted,
- branch created,
- session reload requested,
- failure shown without crashing.

### 5.4 Reconciliation

After branch creation, deletion, or node position update, the UI should rely on the canonical
server snapshot whenever possible. Local optimistic state is allowed only as a short-lived bridge.

---

## 6. API Parity Check

This SDD must not introduce new mobile `fetch` targets unless the matching FastAPI router is
present and registered in `backend/app/main.py`.

Expected existing targets:

| Mobile target | Router |
|---|---|
| `GET /v1/student/sessions/{id}` | `backend/app/api/student/sessions.py` |
| `POST /v1/student/sessions/{id}/events` | `backend/app/api/student/events.py` |
| `PATCH /v1/student/sessions/{id}/nodes/{node_id}` | `backend/app/api/student/nodes.py` |
| `DELETE /v1/student/sessions/{id}/nodes/{node_id}` | `backend/app/api/student/nodes.py` |
| `POST /v1/student/offer-sets/edge` | `backend/app/api/student/offer_sets.py` |
| `POST /v1/student/offer-sets/phrase` | `backend/app/api/student/offer_sets.py` |
| `POST /v1/student/offer-sets/{id}/choices` | `backend/app/api/student/offer_choices.py` |

M4 endpoints for auth/curriculum/dashboard are explicitly out of scope.

---

## 7. TDD Test Plan

All production changes must follow red-before-green.

### 7.1 Mobile Tests

Add or extend focused Jest tests before editing production code:

- `nodeChip-test.tsx`: verifies learner-safe title/body fallback and compact-id fallback.
- `useSessionHydration-test.tsx`: verifies mapped title/content fields if returned by session
  snapshot and confirms error/empty state behavior.
- `edgePlusButton-test.tsx` or `skiaCanvas-test.tsx`: verifies edge offer choice calls reload and
  handles failed offer-set request visibly.
- `PhraseSelectionReaderSheet-test.tsx`: verifies full branch payload remains passed to
  `onBranchCreated` and failure status is visible.
- `skiaCanvas-test.tsx`: protects delete reconciliation and position/reload callback behavior.

### 7.2 Backend Tests

Only add backend tests if a readiness test exposes an API regression in an already-scoped endpoint.
Do not add M4 backend endpoints in M3.5.

### 7.3 Verification Commands

Targeted first:

```powershell
npm.cmd test -- --runInBand nodeChip-test.tsx useSessionHydration-test.tsx edgePlusButton-test.tsx PhraseSelectionReaderSheet-test.tsx skiaCanvas-test.tsx
```

Then, if production code touched shared canvas behavior:

```powershell
npm.cmd test -- --runInBand
```

TypeScript:

```powershell
npx.cmd tsc --noEmit -p ..\canvas\tsconfig.json
```

Known caveat: current TypeScript check may fail on `TS2688` Jest type resolution. If unchanged,
record it as an existing config issue rather than a new M3.5 source failure.

If Python tests are run, delete generated `__pycache__` and verify none remain under `backend/`.

---

## 8. Definition of Done

- [x] SDD created before production edits.
- [x] Red tests written before implementation.
- [x] In-scope mobile readiness items green in focused Jest.
- [x] No new M4 auth/curriculum/dashboard behavior added.
- [x] No student-facing analytic/category fields introduced.
- [x] API parity check remains green for every mobile fetch target touched.
- [x] Worklog updated with files changed, tests run, residual risks, and M4 handoff note.
- [x] Local browser/dev server may be used for inspection, but native mobile remains the MVP target.

---

## 9. Implementation Notes

Completed readiness slice:

- `NodeChip` now prefers learner-facing `title` and `content`, and only falls back to a compact
  node id when no safe text is present. The previous dev-only mock node body was removed.
  Verified by `nodeChip-test.tsx` and confirmed on a physical device running Expo Go: node chips
  render the learner-safe title instead of raw UUIDs.
- `useSessionHydration` preserves optional `title` and `content` returned in the session canvas
  snapshot so backend-provided learner text can reach the canvas. Verified by
  `useSessionHydration-test.tsx` and confirmed on-device via the canvas hydration overlay.
- `SkiaCanvas` now exposes a visible, category-neutral failure banner when edge `+` offer-set
  loading fails, and clears that failure when a later offer set succeeds. Verified by
  `skiaCanvas-test.tsx` ("M3.5: failed edge-plus offer request shows a visible canvas error")
  and confirmed on-device by tapping an edge-`+` button with the backend unreachable.

This slice intentionally does not add M4 auth, curriculum entry, dashboard routing, or new backend
endpoints.

---

## 10. Verification Results

Red-before-green evidence:

- `nodeChip-test.tsx` and `useSessionHydration-test.tsx` failed first because node display used
  raw ids/mock body text and hydration dropped learner-facing fields.
- `skiaCanvas-test.tsx` failed first because edge `+` request failure had no visible canvas error.

Green verification:

```powershell
npm.cmd test -- --runInBand nodeChip-test.tsx useSessionHydration-test.tsx skiaCanvas-test.tsx PhraseSelectionReaderSheet-test.tsx edgePlusButton-test.tsx
```

Result: 5 suites, 35 tests passed.

```powershell
npm.cmd test -- --runInBand
```

Result: 18 suites, 97 tests passed. (This is an increase from the M3-C baseline of 92 tests,
reflecting the 5 new M3.5 frontend readiness tests across NodeChip, useSessionHydration,
edge-`+` error handling, and reconciliation coverage.)

```powershell
npx.cmd tsc --noEmit -p ..\canvas\tsconfig.json
```

Result: blocked by existing TypeScript configuration issue:

```text
error TS2688: Cannot find type definition file for 'jest'.
```

The TypeScript check stops at configured Jest type resolution before validating the changed source.
This is a known, pre-existing config blocker; it does not invalidate the M3.5 feature verification.
No Python tests were run in this slice, so no `.pyc` cleanup was required.

Physical device verification: the M3.5 canvas was launched via Expo Go on a physical device
with `EXPO_PUBLIC_SHOW_CANVAS=true`. Pan/zoom gestures, node-chip rendering, edge-`+` buttons,
node selection toolbar, and the neutral error banner were all inspected and behaved as expected.

---

## 11. Residual Risks

- The app may still feel like a dev build until M4 supplies real auth, curriculum entry, and
  dashboard shell.
- Web inspection can differ from native Skia/Gesture behavior; device validation remains the
  authoritative gate for canvas performance.
- Full offline reopen is not completed in M3.5; only the existing session-hydration surface is
  protected.
- Full mobile Jest passes, but existing React `act(...)` warnings and the current hook-order warning
  around the canvas gesture tests remain as housekeeping risks.
- TypeScript verification remains blocked by the existing `jest` type definition configuration.
