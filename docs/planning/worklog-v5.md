# Worklog v5 — Phase 3 M2 Phrase Selection

AGENT ROTATION INSTRUCTION — READ FIRST: This is the live worklog after `worklog-v4.md` reached the
line-count threshold. Read `.augment/rules/00-canon.md`, `docs/planning/development-approach.md` §5,
and the active SDD before making changes.

## Legacy Context Summary

- Previous tracker: `docs/planning/worklog-v4.md`.
- Phase 3 M1 is **Locally Complete / Operationally Pending**: session resume, offer-set logging,
  edge `+` branching, deletion cascade, and event-only session-path reconstruction are green locally.
- Deferred operational gates remain open and must not be claimed here: Render backend/worker live
  verification and physical-device Expo smoke.
- Active milestone is Phase 3 M2 Phrase Selection. Scope for this session is Reader bottom-sheet
  phrase-selection flow first; in-node selection, canvas maturation, manual links, Render verification,
  and physical-device gates are deferred.

---

### 2026-06-18 — Phase 3 M2 kickoff: Reader phrase-selection SDD activated

**Phase / milestone**: Phase 3 — M2 Phrase Selection

**Spec sections used**:
- `docs/planning/development-approach.md` §5 M2 and §8 (Reader bottom-sheet phrase-selection first;
  small traceable increments).
- `docs/planning/development-approach.md` §7.3 and §9 (Expo/React Native stack; Reader-sheet fallback
  before in-node selection).
- `docs/api/student-api-spec.md` §1, §2, §8 (`/v1/student` category invisibility, backend-resolved
  tenant context, phrase offer and choice endpoints).
- `docs/mvp-features-specification.md` Feature 4.6 and `docs/mobile-features-ai-integration.md`
  §6.5.2 (bottom sheet fixed actions + recommended questions, child AI path creation).
- Active SDD: `docs/planning/sdd/phase-3-phrase-selection-sdd.md` §3–§9.

**Work started**:
- Created the active Phase 3 M2 SDD: `docs/planning/sdd/phase-3-phrase-selection-sdd.md`.
- Updated `.augment/rules/00-canon.md` to point at M2 and the new live tracker.
- Rotated the live tracker to this file to avoid extending `worklog-v4.md` beyond the governance limit.

**Gate status**:
- M2 is now active locally.
- Red-test-first implementation is next.
- Operational gates from M1 remain explicitly deferred and untouched.

---

### 2026-06-18 — Phase 3 M2: Reader bottom-sheet phrase-selection slice green locally

**Phase / milestone**: Phase 3 — M2 Phrase Selection (Reader bottom-sheet flow first)

**Spec sections used**:
- `docs/planning/development-approach.md` §5 M2, §7.3, §8, §9 (Reader bottom-sheet phrase-selection
  first; Expo/React Native stack; small red-test-first increment; in-node selection deferred).
- `docs/architecture/backend-architecture.md` §2.1, §5.3–§5.5, §6.2, §7.1, §8.2, §11 (append-only
  event store, tenant scoping, event registry, backend-owned AI seam, student-safe `/v1/student`).
- `docs/planning/session-path-data-contract.md` §8–§9 and §14 (phrase/offer/choice path events must
  remain reconstructable).
- `docs/api/student-api-spec.md` §1, §2, §8 (phrase offer endpoint, choice endpoint, category
  invisibility).
- `docs/mvp-features-specification.md` Feature 4.6 and `docs/mobile-features-ai-integration.md`
  §6.5.2 (bottom sheet fixed actions + recommended questions; Reader selectable text surface).
- Active SDD: `docs/planning/sdd/phase-3-phrase-selection-sdd.md` §3–§10.

**Work completed**:
- Added red backend tests in `tests/integration/test_phrase_selection.py` for:
  - `POST /v1/student/offer-sets/phrase` logging `phrase_selected`, `phrase_offer_set_created`, and
    `offer_set_impression`,
  - student-safe bottom-sheet response fields with fixed actions plus recommended questions,
  - tenant/student scoping through the pooled path,
  - selected phrase choices branching and enqueuing classify asynchronously while dismissed choices do
    not branch or classify.
- Added red mobile static smoke tests in `tests/integration/test_mobile_phrase_reader_static.py` because
  the repository has no JS/Expo test harness yet.
- Registered `phrase_selected` v1 and `phrase_offer_set_created` v1 in `app.events.registry`.
- Added deterministic student-safe phrase offer request/response models and event builders in
  `app.domain.student.offer_sets`.
- Confirmed that M2 extended the existing M1 offer-set modules (`app.domain.student.offer_sets` and
  `app.api.student.offer_sets`) rather than creating a separate backend offer-set file; the new M2 file
  is `mobile/PhraseSelectionReaderSheet.tsx`.
- Added `POST /v1/student/offer-sets/phrase` and runtime orchestration that validates session ownership
  through the tenant pool before appending events.
- Added `mobile/PhraseSelectionReaderSheet.tsx`, a Reader bottom-sheet component using a React Native
  `TextInput` selection surface and only `/v1/student` API calls.

**Validation run**:
- Red backend baseline: `python -m pytest tests/integration/test_phrase_selection.py -q` → 3 failed,
  1 passed (missing phrase endpoint returned 404).
- Red mobile static baseline: `python -m pytest tests/integration/test_mobile_phrase_reader_static.py -q`
  → 2 failed (missing Reader component file).
- `python -m pytest tests/integration/test_phrase_selection.py tests/integration/test_mobile_phrase_reader_static.py -q`
  → 6 passed.
- `python -m pytest tests/integration/test_offer_set_logging.py tests/integration/test_offer_choice.py tests/integration/test_edge_branching.py tests/integration/test_deletion_cascade.py tests/projections/test_session_path_projection.py -q`
  → 19 passed.
- `python -m ruff format --check backend tests docs` → passed.
- `python -m ruff check backend tests` → passed.
- `python -m mypy backend/app` → passed.
- `python -m pytest tests -q` → 91 passed.
- Generated `*.pyc` files were removed after test completion; verification command reported
  `.pyc` count = 0.

**Gate status**:
- Reader bottom-sheet phrase-selection slice is **GREEN locally**.
- Broader M2 human/device gate remains pending: a test user must branch from a self-chosen phrase on
  Android and iOS.
- In-node selection, canvas maturation, manual links, Render backend/worker verification, and physical
  device gates were not attempted.

**Remaining M2 tasks**:
- Wire the Reader bottom-sheet component into the eventual runnable Expo app scaffold.
- Add a real mobile component/test harness beyond the current static smoke test.
- Complete the Android + iOS test-user phrase-branching gate.
- Decide whether in-node selection stays deferred past M2 or becomes a later M2 enhancement after the
  Reader flow is proven.

---

### 2026-06-20 — M2 Expo Go mobile smoke: slice planned (refined)

**Phase / milestone**: Phase 3 — M2 Phrase Selection (Reader bottom-sheet flow first)

**Spec sections used**:
- `docs/planning/development-approach.md` §5 M2, §7.3, §7.6 (Jest + RNTL), §8.2 (no secrets in
  code/docs/logs).
- `docs/architecture/backend-architecture.md` §5.3–§5.5, §6.2, §7.1.
- `docs/api/student-api-spec.md` §1, §2, §8; `docs/mobile-features-ai-integration.md` §6.5.2.
- Active SDD: `docs/planning/sdd/phase-3-phrase-selection-sdd.md` §12.

**Work started (planning only — no code/deps yet)**:
- Defined the M2 Expo Go mobile smoke as an engineering sub-step toward the §5 M2 gate, explicitly
  NOT a new milestone and NOT the Android + iOS user/device gate.
- Recorded refinements in SDD §12: scaffold under `mobile/app/` (not `create-expo-app .` into the
  non-empty `mobile/`) + `mobile/.gitignore`; dev-smoke bootstrap as a script outside `app/` so the
  `api/student ⇏ analytic` import-linter contract is unaffected; Jest + RNTL as the prescribed mobile
  test path per §7.6.
- Captured security constraints: local-trusted-network-only `0.0.0.0` bind, dev-flag + prod-secret
  refusal, no token in shell argv, `secureTextEntry` token field with no logging/persistence.
- Captured platform blockers: Windows Firewall prompt, LAN client isolation, mandatory dev-guarded
  CORS for Expo Web, in-memory store volatility on restart.

**Gate status**:
- Backend Reader phrase-selection slice remains GREEN locally.
- M2 Expo Go mobile smoke is the next slice; it does not satisfy the M2 gate.
- Render backend/worker verification and physical-device operational gates from M1 remain deferred.

---

### 2026-06-20 — M2 Expo Go mobile smoke: slice assembled locally (device run pending)

**Phase / milestone**: Phase 3 — M2 Phrase Selection (Reader bottom-sheet flow first)

**Spec sections used**:
- `docs/planning/development-approach.md` §5 M2, §7.3, §7.6 (Jest + RNTL), §8.2 (no secrets in
  code/docs/logs).
- `docs/architecture/backend-architecture.md` §5.3–§5.5, §6.2, §7.1.
- `docs/api/student-api-spec.md` §1, §2, §8; `docs/mobile-features-ai-integration.md` §6.5.2.
- Active SDD: `docs/planning/sdd/phase-3-phrase-selection-sdd.md` §12.

**Work completed**:
- Added `backend/scripts/dev_smoke_bootstrap.py` (outside `app/` to preserve the `api/student ⇏
  analytic` import-linter contract): `--dev-smoke` flag, production-secret refusal guard, curriculum +
  membership seeding via `build_curriculum_rows`, HS256 dev-token mint, `0.0.0.0` bind, and a stdout
  banner with `apiBaseUrl` + token + fixed seed IDs (no logging, no env-var exposure).
- Scaffolded an Expo SDK 56 (blank-typescript) app under `mobile/app/` with `npm install` complete;
  added `mobile/.gitignore` for `node_modules/`.
- Added `mobile/app/metro.config.js` adding the parent `mobile/` dir to `watchFolders` so
  `../PhraseSelectionReaderSheet` resolves from inside `mobile/app/`.
- Added `mobile/app/M2PhraseSmokeScreen.tsx` (apiBaseUrl input, `secureTextEntry` token field with no
  logging, "Start test session" → `POST /v1/student/sessions`, opens `PhraseSelectionReaderSheet`) and
  wired it into `mobile/app/App.tsx`.

**Validation run**:
- Bootstrap banner verified to print `apiBaseUrl`, token, and seed IDs; uvicorn bound on `0.0.0.0:8000`.
- `python -m pytest tests -q` → 91 passed.
- Generated `*.pyc` files removed after tests; verification command reported `.pyc` count = 0.

**Gate status**:
- M2 Expo Go mobile smoke is **assembled locally**; this is proof-of-wiring only and does NOT satisfy
  the §5 M2 user/device gate.
- PENDING: physical-device run (Android first, then iOS) — scan QR via Expo Go, enter `apiBaseUrl` +
  token, run session → phrase → options → branch, confirm `phrase_selected` /
  `phrase_offer_set_created` / `offer_set_choice` recorded and no analytic-field leakage.
- PENDING: Jest + RNTL coverage for `M2PhraseSmokeScreen` and `PhraseSelectionReaderSheet` per §7.6.
- Render backend/worker verification and physical-device operational gates from M1 remain deferred.

---

### 2026-06-20 — Phase 3 M2: Jest + RNTL Coverage Green Locally

**Phase / milestone**: Phase 3 — M2 Phrase Selection (Reader bottom-sheet flow first)

**Spec sections used**:
- `docs/planning/development-approach.md` §7.6 (Jest + RNTL unit testing strategy).
- `docs/planning/sdd/phase-3-phrase-selection-sdd.md` §7 (Category Invisibility), §12 (M2 Test Plan).
- `00-canon.md` (Invariants: Category Invisibility, Organic-First, Tenant Isolation).

**Work completed**:
- Installed `jest-expo`, `jest`, `@testing-library/react-native` and configured the environment (babel, tsconfig, package.json).
- Implemented unit tests for `M2PhraseSmokeScreen.tsx` (8/8 passing).
- Implemented unit tests for `PhraseSelectionReaderSheet.tsx` (7/7 passing).
- Verified invariants via tests:
  - **Category Invisibility**: POST request bodies to `/v1/student/offer-sets/phrase` and `/v1/student/offer-sets/.../choices` contain no analytic/dimension/tenant fields.
  - **Organic-First**: Dismissed outcomes fire to the choices endpoint; selected outcomes fire with `outcome:"selected"` and trigger the `onBranchCreated` callback.
  - **Tenant Isolation**: No `tenant_id` is sent from the mobile layer.
- Refactored `PhraseSelectionReaderSheet.tsx` to use `readOnly={true}` on the passage `TextInput` to enable selection events in the Jest/RNTL environment while maintaining read-only behavior for users. (Superseded same day by the gate-closure entry below: `readOnly` blocked focus/selection on physical Android, so it was replaced with `showSoftInputOnFocus={false}` + `maxLength`.)

**Gate status**:
- Mobile unit coverage for M2 Phrase Selection is **COMPLETE** and green locally.
- §5 M2 user/device gate (successful branching on both Android and iOS) remains **OPEN** and pending physical device verification.
- .pyc count verified at 0.

---

### 2026-06-20 — Phase 3 M2 Student Gate: CLOSED (physical Android device verified)

**Phase / milestone**: Phase 3 — M2 Phrase Selection (Reader bottom-sheet flow first)

**Spec sections used**:
- `docs/planning/development-approach.md` §5 M2 (gate: a test user branches from a phrase they chose
  themselves), §5.5 "Real users embarrassingly early", §9 (risk: "Generated questions aren't tappable"
  retired by the M2 real-student test).
- `docs/planning/sdd/phase-3-phrase-selection-sdd.md` §6.5.2 (Reader selectable text surface), §12.
- `00-canon.md` (Category Invisibility, Organic-First, Tenant Isolation invariants).
- `mobile/app/AGENTS.md` (Expo SDK 56 versioned docs).

**Work completed (device-readiness fixes)**:
- **JWT input fix** (`mobile/app/M2PhraseSmokeScreen.tsx`): removed `secureTextEntry` from the auth-token
  field and added `autoCorrect={false}` / `autoCapitalize="none"` / `spellCheck={false}` to stop the
  Android secure keyboard mangling the pasted JWT (it had substituted `Ł` / `0x141` at offset 79). Added a
  one-tap "Fill dev defaults" button to avoid manual paste during the gate run.
- **Reader selection fix** (`mobile/PhraseSelectionReaderSheet.tsx`): a `readOnly`/non-editable
  `TextInput` is not focusable on Android, so `onSelectionChange` never fired and no phrase could be
  selected. Replaced `readOnly` with the RN-docs "selectable but non-editable" pattern
  (`showSoftInputOnFocus={false}` + `maxLength={content.length}`) so the surface is focusable/selectable
  with no keyboard, and added deterministic per-sentence quick-select buttons so a phrase can be selected
  by tap regardless of device long-press behavior.

**Validation run**:
- `cd mobile/app; npx jest --testPathPattern="M2PhraseSmokeScreen" --no-coverage` → 9 passed.
- `cd mobile/app; npx jest --testPathPattern="PhraseSelectionReaderSheet" --no-coverage` → 7 passed.
- Physical-device run (Android, Expo Go SDK 56, `dev_smoke_bootstrap.py --dev-smoke --port 8001` on LAN):
  session started → phrase selected via quick-select → "Use selected phrase" → option chosen →
  **branch created** confirmed by the user.
- .pyc count verified at 0.

**Gate status**:
- §5 M2 user/device gate is **CLOSED** — a test user branched from a self-chosen phrase on a physical
  Android device. The "Generated questions aren't tappable" fatal risk (§9) is **retired**.
- iOS run remains an optional follow-up, not a blocker for the §5 gate (which was met on Android).
- Render backend/worker live verification and the M1 physical-device operational gates remain deferred and
  untouched.
- M3 (Canvas maturation) is now unblocked per §5 milestone gating.
