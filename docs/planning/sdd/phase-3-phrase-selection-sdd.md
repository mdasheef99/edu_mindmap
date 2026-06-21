# Phase 3 Phrase Selection — Software Design Document (SDD)

**Document Version**: 1.1
**Status**: Completed — M2 user/device gate CLOSED (physical Android device verified 2026-06-20)
**Phase / milestone**: Phase 3 — M2 Phrase Selection
**Live tracker**: `docs/planning/worklog-v5.md`

---

## 1. Increment Identity

| Field | Value |
|---|---|
| Increment name | Reader bottom-sheet phrase-selection flow |
| Phase / milestone | Phase 3 — M2 |
| Owner | (developer) |
| Status | Completed — M2 user/device gate CLOSED (physical Android device, 2026-06-20) |

Goal: implement the smallest student-safe phrase-selection path where a learner opens a Reader
bottom sheet for an AI node, selects a phrase, receives fixed phrase actions plus recommended
follow-up questions, and can branch from that phrase through existing event-sourced child-node
creation.

## 2. Source-of-Truth References

- `development-approach.md` §5 M2: phrase selection follows M1; Reader bottom-sheet flow is first,
  while in-node selection is deferred; M2 retires the fiddliest mobile interaction risk.
- `development-approach.md` §7.3 and §9: Expo/React Native mobile stack; Reader-sheet fallback
  precedes in-node selection and reduces canvas/selection risk.
- `development-approach.md` §8: work in small traceable increments with red tests first.
- `backend-architecture.md` §2.1, §5.3–§5.5, §6.2, §7.1, §8.2, §11: append-only events,
  backend-resolved tenancy, student-safe APIs, backend-owned AI gateway, and category invisibility.
- `session-path-data-contract.md` §8–§9 and §14: phrase/offer/choice/thread context must be
  reconstructable from session path events.
- `docs/api/student-api-spec.md` §1, §2, §8: `/v1/student` must remain category-invisible;
  phrase offer creation uses `POST /v1/student/offer-sets/phrase`; selected choices create child
  path events while dismissed choices do not branch.
- `docs/mvp-features-specification.md` Feature 4.6: selected words/phrases open a bottom sheet with
  fixed top actions and 3–5 recommended questions; phrase selection creates a child AI node and
  parent→child AI path edge.
- `docs/mobile-features-ai-integration.md` §6.5.2: Basic tier uses a Reader bottom sheet and a
  selectable React Native text surface; in-node selection is possible but not required for the first
  implementation.

## 3. Scope of Increment

**In scope:**
- Reader bottom-sheet entry point from an AI node response.
- Capturing a selected phrase from the Reader surface, not in-node selection.
- Backend phrase offer-set creation with fixed actions and 3–5 deterministic recommended questions.
- Append-only phrase-selection/offer/impression logging under backend-resolved tenant/student scope.
- Student-safe phrase offer response with no analytic fields, propensities, scores, or category labels.
- Existing offer-choice endpoint continues to append selected/dismissed outcomes; selected choices may
  create child `node_created` and `edge_created` events and enqueue `classify` asynchronously;
  dismissed choices do not classify.

**Out of scope:**
- In-node text selection and exact-selection handles inside canvas nodes.
- Canvas maturation, pan/zoom performance work, manual/reference links, Render verification,
  physical-device Expo gates, checkpoints, teacher surfaces, podcast, and live LLM/provider calls.
- New raw student event endpoints or analytic read-model exposure.

## 4. Traceability Rows

| Feature | Endpoint | Events | Read Model | Worker Job | Table(s) |
|---|---|---|---|---|---|
| Reader phrase offer set | `POST /v1/student/offer-sets/phrase` | `phrase_selected`, `phrase_offer_set_created`, `offer_set_impression` | none in this slice | none | `events` |
| Phrase branch selected | existing `POST /v1/student/offer-sets/{offer_set_id}/choices` | `offer_set_choice`, optional `phrase_offer_set_choice`, `node_created`, `edge_created` | none in this slice | `classify` queued only when selected | `events`, `jobs` |
| Phrase offer dismissed | existing choice endpoint | `offer_set_choice`, optional `phrase_offer_set_choice` with dismissed outcome | none | none | `events` |

## 5. Module Placement & Import Rules

| Concern | Module | Rule |
|---|---|---|
| Student-safe phrase offer request/response + event builders | `app.domain.student.offer_sets` or cohesive sibling module if size requires | no analytic/category fields |
| Student API route | `app.api.student.offer_sets` | student domain + auth only |
| Runtime orchestration | `app.runtime.offer_workflow` and thin `SessionRuntime` delegator | validate session ownership through tenant pool before appending |
| Event validation | `app.events.registry` | register exact payload schemas; reject ad-hoc event payloads |
| Mobile Reader UI | `mobile/` Reader bottom-sheet component/screen helper | no provider credentials; calls `/v1/student` only |

Module note: the M2 backend did **not** create a separate new offer-set module. It extended the
existing M1 offer-set files (`app.domain.student.offer_sets` and `app.api.student.offer_sets`) because
phrase offers and edge-`+` offers share the same student-safe `/v1/student/offer-sets/*` seam and
reuse the same selected/dismissed choice endpoint. The new file for M2 is the mobile Reader component:
`mobile/PhraseSelectionReaderSheet.tsx`.

## 6. Event / Schema Deltas

- Add/validate `phrase_selected` v1 for the learner-selected phrase anchor.
- Add/validate `phrase_offer_set_created` v1 for phrase-conditioned fixed actions + recommended
  questions, including measurement-only fields in the event payload.
- Reuse `offer_set_impression` v1 for visibility logging.
- Reuse existing `offer_set_choice`, `node_created`, and `edge_created` selected/dismissed behavior.
- No database migration in this deterministic in-memory/test slice unless existing Postgres event
  validation requires mirrored constants only.

## 7. Student-Safety Contract

- `/v1/student` responses must contain only `offer_set_id`, session/source identifiers,
  `launch_method: "phrase_selection"`, selected phrase display text, and student-visible options.
- Measurement fields such as `propensity`, `is_probe`, `randomization_id`, classifications, scores,
  dimensions, coverage, confidence, entropy, vectors, profile/weight/propensity internals, and
  teacher fields must never appear in student responses.
- Mobile-supplied `tenant_id` is ignored; tenant and student ownership are resolved server-side.
- Generation and phrase-offer creation do not enqueue classification. Selected choices may enqueue
  classification after append; dismissed choices enqueue nothing.

## 8. Test Plan

First red tests:
- T1: `POST /v1/student/offer-sets/phrase` returns 404 before implementation, then creates
  `phrase_selected`, `phrase_offer_set_created`, and `offer_set_impression` events for a valid
  student-owned session.
- T2: phrase offer response exposes fixed actions plus 3–5 recommended questions and hides all
  measurement/analytic fields.
- T3: cross-tenant/student session access is denied through the pooled tenant path.
- T4: selected phrase offer choice creates a child AI path via existing choice flow and enqueues
  classify asynchronously; dismissed phrase offer choice does not create a child path or job.
- T5: mobile Reader bottom-sheet logic can capture a selected phrase and build the phrase offer request
  without adding provider credentials or in-node selection behavior.

Validation gates:
- Focused backend integration tests for phrase offer creation and choice behavior.
- Focused mobile deterministic tests if the existing scaffold supports them; otherwise a typed/mobile
  helper smoke via the available toolchain.
- Adjacent offer-set/offer-choice/edge/deletion/session-path regressions.
- Ruff format/check, MyPy, and full pytest after focused green.

## 9. Definition of Done

- Active SDD and Canon point to this M2 slice; worklog records the start and validation.
- Red tests fail before implementation and pass after implementation.
- Reader bottom-sheet phrase-selection path is implemented before in-node selection.
- Phrase-offer creation and choice handling are tenant-scoped, event-sourced, deterministic, and
  category-invisible.
- No raw student event endpoint, analytic leakage, live LLM/provider call, manual links, canvas
  maturation, Render verification, or physical-device gate is introduced in this session.

## 10. Local Validation Record

- Red backend baseline: `python -m pytest tests/integration/test_phrase_selection.py -q` → 3 failed,
  1 passed (`POST /v1/student/offer-sets/phrase` returned 404 before implementation).
- Red mobile static baseline: `python -m pytest tests/integration/test_mobile_phrase_reader_static.py -q`
  → 2 failed (Reader component file missing).
- Focused green: `python -m pytest tests/integration/test_phrase_selection.py tests/integration/test_mobile_phrase_reader_static.py -q`
  → 6 passed.
- Adjacent regressions: offer-set logging, offer choice, edge branching, deletion cascade, and
  session-path projection tests → 19 passed.
- Static gates: `python -m ruff format --check backend tests docs`, `python -m ruff check backend tests`,
  and `python -m mypy backend/app` → passed.
- Full suite: `python -m pytest tests -q` → 91 passed.
- Generated Python cache cleanup: all `*.pyc` files were removed after test completion and verified with
  `.pyc` count = 0.

The broader M2 gate — a test user branching from a self-chosen phrase — was CLOSED on 2026-06-20 on a
physical Android device (worklog-v5.md entry "Phase 3 M2 Student Gate: CLOSED").

## 11. M2 Tasks — Completion Record

- DONE: Wired `PhraseSelectionReaderSheet` into the runnable Expo app via `mobile/app/M2PhraseSmokeScreen.tsx`.
- DONE: Added a real Jest + RNTL test path (`mobile/app/__tests__/`) for the smoke screen and Reader sheet,
  superseding the interim static smoke tests.
- DONE: Ran the M2 human/device gate — a test user branched from a self-chosen phrase on a physical
  Android device. The two device-readiness fixes are recorded in the worklog: the JWT input fix
  (disabled autocorrect/secure keyboard) and the Reader selection fix (focusable non-editable surface
  plus per-sentence quick-select buttons).
- Open enhancement (not a gate blocker): optional iOS confirmation run; in-node text selection remains a
  deferred enhancement after the proven Reader flow.

Still deferred: canvas maturation, manual links, Render backend/worker verification, physical-device
operational gates from M1, checkpoints, teacher surfaces, podcast, and live LLM/provider calls.

## 12. M2 Expo Go Mobile Integration Smoke Plan

Slice name: "M2 Expo Go mobile smoke — wire the Reader phrase-selection sheet into a runnable Expo
app against a local dev-smoke backend."

**Position (governance):** This is an engineering sub-step toward the `development-approach.md`
§5 M2 gate ("A test user branches from a phrase they chose themselves, on Android and iOS"). It is
**not** a new milestone and it does **not** satisfy the M2 gate. "Expo Go smoke" and "Expo Web" are
not source-of-truth increments; they are local proof-of-wiring only. Passing this smoke leaves the
Android + iOS user/device gate open.

**Source-of-truth references:** `development-approach.md` §5 M2, §7.3 (Expo/React Native, Reader-
sheet primary), §7.6 (Jest + React Native Testing Library for mobile unit tests), §8.2 (reviewable
diffs, no secrets in code/docs/logs); `backend-architecture.md` §5.3–§5.5, §6.2, §7.1;
`docs/api/student-api-spec.md` §1, §2, §8; `docs/mobile-features-ai-integration.md` §6.5.2.

**In scope:**
- Create a runnable Expo scaffold under `mobile/app/` (NOT `create-expo-app .` into the non-empty
  `mobile/` dir); add `mobile/.gitignore` for `node_modules/`.
- Wire `mobile/PhraseSelectionReaderSheet.tsx` into a simple `M2PhraseSmokeScreen`.
- A local dev-only backend smoke bootstrap (separate script outside `app/`) seeding curriculum +
  membership + a local test token.
- Expo Go QR-scan run from a phone on the same trusted LAN; optional Expo Web secondary check.
- Jest + React Native Testing Library coverage per §7.6 once the scaffold exists (the existing
  pytest static smoke is an interim stopgap, not the prescribed mobile test path).

**Out of scope:** in-node selection, canvas maturation, Render deployment, real production auth,
the Android + iOS user/device M2 gate itself.

**Invariant guards:**
- Category Invisibility — the dev-smoke script adds NO routes and exposes no analytic fields; no raw
  student event endpoint is introduced. The script lives outside `app/` so the `api/student ⇏
  analytic` import-linter contract is unaffected.
- Organic-First — phrase-offer creation does not classify; only a selected choice enqueues
  `classify`. The in-memory queue is not drained during the smoke, which positively demonstrates the
  student never waits on a job (branch is created synchronously; classification stays async/pending).
- Tenant Isolation — mobile-supplied `tenant_id` stays non-authoritative; tenant resolves from the
  seeded membership server-side.

**Security / secret-handling constraints (§8.2):**
- The dev-smoke bootstrap is local-trusted-network ONLY. Binding `0.0.0.0` plus a printed bearer
  token plus the default weak HS256 secret must never run against a shared/public network or any
  deployed/prod backend; the script must require an explicit dev flag and refuse a production secret.
- No token is ever placed in a shell command/argv (no token-bearing `curl`); reachability is checked
  without secrets, or via the app itself.
- The mobile token field uses `secureTextEntry`, is not persisted to AsyncStorage in committed code,
  and is never logged to console or Sentry.

**Known platform blockers to expect:**
- Windows Firewall will prompt/may block inbound connections to Python on the first `0.0.0.0` bind.
- LAN client isolation (common on guest Wi-Fi) blocks phone↔laptop traffic on the same SSID.
- Expo Web requires dev-guarded CORS on the backend (mandatory for the browser path; Expo Go native
  does not need CORS).
- `InMemoryEventStore` loses all state on restart; a backend restart invalidates an in-flight session.

**Local validation sequence:**
1. Backend: focused phrase tests + adjacent regressions + ruff/mypy/full pytest; delete all `*.pyc`
   and verify count = 0.
2. Start the backend via the dev-smoke bootstrap bound to `0.0.0.0`.
3. Scaffold/run Expo (`mobile/app/`); confirm with the user before any dependency install.
4. Expo Go: scan QR from a phone on the same LAN; complete session → phrase → options → branch.
5. Expo Web: optional secondary UI check (requires dev CORS).
6. Record the result in `worklog-v5.md`; confirm no analytic leakage and that the Android + iOS gate
   remains open.

**Implementation status (COMPLETE — M2 user/device gate CLOSED 2026-06-20):**
- `backend/scripts/dev_smoke_bootstrap.py`: `--dev-smoke` flag, prod-secret refusal guard,
  curriculum/membership seeding via `build_curriculum_rows`, HS256 dev token mint, `0.0.0.0` bind,
  prints `apiBaseUrl` + token + seed IDs to stdout (no logging).
- Expo SDK 56 scaffold under `mobile/app/` (blank-typescript); `mobile/.gitignore` excludes
  `node_modules/`; `metro.config.js` adds parent `mobile/` to `watchFolders`.
- `mobile/app/M2PhraseSmokeScreen.tsx`: apiBaseUrl input, `secureTextEntry` token field
  (keyboard-mangling workaround: one-tap "Fill dev defaults" button pre-fills credentials
  programmatically, bypassing secure-keyboard paste), "Start test session", opens Reader sheet.
  Wired into `mobile/app/App.tsx`.
- `mobile/app/__tests__/M2PhraseSmokeScreen-test.tsx` + `PhraseSelectionReaderSheet-test.tsx`:
  Jest + RNTL coverage (16 tests, all green).
- Physical-device gate (Android, Expo Go SDK 56, LAN backend): session started → phrase selected
  via quick-select → "Use selected phrase" → option chosen → branch created. Gate confirmed by
  test user 2026-06-20.
- Full pytest suite: 91 passed; `.pyc` count = 0.
  Passing the local smoke does NOT satisfy the §5 M2 user/device gate.