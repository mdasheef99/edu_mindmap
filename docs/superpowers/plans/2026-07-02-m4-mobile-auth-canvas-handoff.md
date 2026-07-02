# M4 Mobile Auth + Curriculum + Canvas Handoff Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the dev mobile shell with Supabase email/password auth, dashboard, curriculum picker, chapter start/resume, and real session/token handoff into the existing canvas.

**Architecture:** Keep `SkiaCanvas` internals stable. Add a simple M4 app state machine around auth, dashboard, curriculum selection, chapter detail/start, and canvas handoff. Mobile sends Supabase access tokens to the backend and never holds AI/TTS credentials.

**Traceability:** M4 SDD Sections 5, 6.1, 10, 12.5; `mvp-features-specification.md` Feature Groups 1-4 and 7.1; `configuration-reference.md` Sections 9-10.

---

## Files

- Modify: `mobile/app/package.json`
- Modify: `mobile/app/package-lock.json`
- Create: `mobile/app/auth/supabaseClient.ts`
- Create: `mobile/app/auth/useAuthSession.ts`
- Create: `mobile/app/api/studentClient.ts`
- Create: `mobile/app/screens/AuthScreen.tsx`
- Create: `mobile/app/screens/ConsentScreen.tsx`
- Create: `mobile/app/screens/DashboardScreen.tsx`
- Create: `mobile/app/screens/CurriculumPickerScreen.tsx`
- Create: `mobile/app/screens/ChapterDetailScreen.tsx`
- Modify: `mobile/app/App.tsx`
- Modify: `mobile/canvas/useSessionHydration.ts` only if needed
- Test: `mobile/app/__tests__/m4AuthScreen-test.tsx`
- Test: `mobile/app/__tests__/m4DashboardFlow-test.tsx`
- Test: `mobile/app/__tests__/m4CurriculumFlow-test.tsx`
- Test: `mobile/app/__tests__/m4CanvasHandoff-test.tsx`

## Task 1: Supabase Dependency And Auth Red Tests

- [ ] Add dependency with `npm.cmd install @supabase/supabase-js` from `mobile/app`.
- [ ] Test missing config shows a safe setup error.
- [ ] Test sign-up calls Supabase email/password.
- [ ] Test sign-in calls Supabase email/password.
- [ ] Test access token is exposed to backend client code.
- [ ] Test loading and error states.

Run:

```powershell
npm.cmd test -- --runInBand __tests__/m4AuthScreen-test.tsx
```

Expected: fail until auth files/screens exist.

## Task 2: Implement Auth Client And Screen

- [ ] Use `EXPO_PUBLIC_SUPABASE_URL`.
- [ ] Use `EXPO_PUBLIC_SUPABASE_ANON_KEY`.
- [ ] Do not add mobile-side LLM/TTS credentials.
- [ ] Keep phone/OTP deferred.

## Task 3: Backend Client Red Tests

- [ ] Test dashboard request includes `Authorization: Bearer <token>`.
- [ ] Test curriculum requests hit documented endpoint paths.
- [ ] Test session start posts selected curriculum IDs.
- [ ] Test resume/fetch session use real session ID.

Run:

```powershell
npm.cmd test -- --runInBand __tests__/m4DashboardFlow-test.tsx __tests__/m4CurriculumFlow-test.tsx
```

Expected: fail until `studentClient.ts` exists.

## Task 4: Implement Backend Client

- [ ] Read `EXPO_PUBLIC_API_BASE_URL`.
- [ ] Implement `getDashboard`.
- [ ] Implement `listClasses`, `listExams`, `listSubjects`, `listChapters`.
- [ ] Implement `getChapter`, `listConceptEntries`.
- [ ] Implement `startSession`, `resumeSession`, `getSession`.
- [ ] Keep error handling typed enough for screens to render safe errors.

## Task 5: Screen Flow Red Tests

- [ ] Test authenticated app loads dashboard.
- [ ] Test dashboard Continue Learning resumes a session.
- [ ] Test no-session dashboard can navigate to Class 10 -> CBSE -> Science -> Electricity.
- [ ] Test chapter detail starts session.
- [ ] Test consent acknowledgement appears before first learning entry if required by state.

Run:

```powershell
npm.cmd test -- --runInBand __tests__/m4DashboardFlow-test.tsx __tests__/m4CurriculumFlow-test.tsx
```

Expected: fail until screens/state machine are implemented.

## Task 6: Implement Screens And App State

- [ ] Replace normal dev shell path in `App.tsx`.
- [ ] Keep UI compact and operational; no landing page.
- [ ] Authenticated default route is dashboard.
- [ ] Curriculum flow is Class 10 -> CBSE -> Science -> Electricity.
- [ ] Chapter start stores active `sessionId`, `accessToken`, and `apiBaseUrl`.

## Task 7: Canvas Handoff Red Tests

- [ ] Mock `SkiaCanvas`.
- [ ] Test it receives backend session ID from `POST /sessions`.
- [ ] Test it receives the Supabase access token.
- [ ] Test normal M4 path does not pass hardcoded `DEV_SESSION_ID` or `DEV_AUTH_TOKEN`.

Run:

```powershell
npm.cmd test -- --runInBand __tests__/m4CanvasHandoff-test.tsx
```

Expected: fail until handoff is implemented.

## Task 8: Implement Canvas Handoff

- [ ] Pass real `apiBaseUrl`, `authorizationToken`, and `sessionId` into `useSessionHydration`.
- [ ] Pass the same real values into `SkiaCanvas`.
- [ ] Preserve existing canvas gesture/layout/toolbar behavior.
- [ ] Keep a dev escape hatch only outside the normal M4 path if still needed.

## Task 9: Green

Run:

```powershell
npm.cmd test -- --runInBand __tests__/m4AuthScreen-test.tsx __tests__/m4DashboardFlow-test.tsx __tests__/m4CurriculumFlow-test.tsx __tests__/m4CanvasHandoff-test.tsx
npm.cmd test -- --runInBand
npx.cmd tsc --noEmit
```

Expected: M4 mobile tests, full mobile Jest, and TypeScript gate pass.
