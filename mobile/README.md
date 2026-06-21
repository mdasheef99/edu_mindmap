# Mobile Components & Scaffold

This directory holds standalone React Native components plus the planned runnable Expo app. Every
component calls the backend `/v1/student` API only and stores **no** provider/AI/TTS credentials.

## Components

- `Phase1WalkingSkeletonScreen.tsx` — Phase 1 Walking Skeleton screen
  (`docs/planning/development-approach.md` §4.2).
- `PhraseSelectionReaderSheet.tsx` — Phase 3 M2 Reader bottom-sheet phrase-selection flow
  (active SDD `docs/planning/sdd/phase-3-phrase-selection-sdd.md`). It opens a `Modal`, captures a
  selected phrase from a read-only `TextInput`, calls `POST /v1/student/offer-sets/phrase`, and
  submits selected/dismissed outcomes to the existing offer-choice endpoint. The caller supplies a
  `ReaderNode` (`sessionId`, `nodeId`, `threadContextId`, `content`).

## Runnable Expo app (assembled — see SDD §12)

The Expo SDK 56 (blank-typescript) project is scaffolded under `mobile/app/` (not `create-expo-app .`
into this non-empty directory), with `node_modules/` excluded via `mobile/.gitignore`. Assembled
pieces:

- `mobile/app/metro.config.js` adds the parent `mobile/` dir to `watchFolders` so
  `../PhraseSelectionReaderSheet` resolves from inside `mobile/app/`.
- `mobile/app/M2PhraseSmokeScreen.tsx` — apiBaseUrl input, `secureTextEntry` token field, "Start test
  session" (`POST /v1/student/sessions`), then opens `PhraseSelectionReaderSheet`.
- `mobile/app/App.tsx` renders `M2PhraseSmokeScreen`.

To run the smoke locally:

1. Backend — `python backend/scripts/dev_smoke_bootstrap.py --dev-smoke`; copy the printed
   `apiBaseUrl` and token.
2. Expo — `cd mobile/app` then `npx expo start`; scan the QR code with Expo Go.
3. Enter `apiBaseUrl` + token, tap **Start test session**, open the reader, select a phrase, branch.

Status: **COMPLETE — M2 user/device gate CLOSED** (physical Android device verified 2026-06-20;
see `docs/planning/worklog-v5.md` "Phase 3 M2 Student Gate: CLOSED"). iOS confirmation is an
optional follow-up, not a gate blocker. M3 Canvas maturation is now the active milestone.

Local dev notes:

- The phone cannot reach `localhost` on the host machine. Point `apiBaseUrl` at the host LAN IP
  (e.g. `http://192.168.x.x:8000`) and bind the backend to `0.0.0.0`.
- `0.0.0.0` binding is **local-trusted-network only**; never expose it on shared/public Wi-Fi or
  against a deployed backend.
- Provide the dev auth token at runtime via a `secureTextEntry` field; do not persist it to
  AsyncStorage in committed code, do not log it, and never place it in a shell command/argv.
- Expo Go (native phone, QR scan) needs no CORS. Expo Web (browser) requires dev-guarded CORS on the
  backend.

## Phase 1 gate proof (record in the live worklog)

1. Expo dev build installed on one physical mid-range Android device.
2. `apiBaseUrl` points at the deployed Render backend.
3. Tapping **Start test session** receives `201` from `/v1/student/sessions`.
4. A selected offer choice is submitted through the backend and classified by the deployed worker.
5. Sentry receives one deliberate mobile error.