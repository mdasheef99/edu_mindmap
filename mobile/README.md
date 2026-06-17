# Phase 1 Mobile Scaffold

This directory intentionally contains only the minimal screen contract needed for the Phase 1
Walking Skeleton gate (`docs/planning/development-approach.md` §4.2).

To create the runnable Expo app, use `npx create-expo-app` and import
`Phase1WalkingSkeletonScreen.tsx`. Do not add provider credentials to the mobile app; it calls the
backend `/v1/student` API only.

Gate proof to record in `docs/planning/worklog.md`:

1. Expo dev build installed on one physical mid-range Android device.
2. `apiBaseUrl` points at the deployed Render backend.
3. Tapping **Start test session** receives `201` from `/v1/student/sessions`.
4. A selected offer choice is submitted through the backend and classified by the deployed worker.
5. Sentry receives one deliberate mobile error.