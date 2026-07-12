# Phase 3 M4 Runtime + Closure Remediation — Software Design Document

**Document Version**: 0.3
**Status**: Closed (2026-07-11)
**Phase / milestone**: Phase 3 — M4  
**Parent SDD**: `phase-3-m4-curriculum-auth-sdd.md`  
**Live tracker**: `docs/planning/worklog-v10.md`

---

## 1. Purpose

This bounded remediation closes the difference between the M4 local smoke prototype and the
durable learner flow required by the parent SDD. It introduces no new product scope.

The remediation is required by:

- `development-approach.md` §5 M4: a stranger can sign up and reach a chapter unaided.
- `development-approach.md` §6 disciplines 2, 6, and 10: import boundaries, pooled tenant
  isolation, and API/mobile parity are merge-blocking.
- `backend-architecture.md` §§3, 5.3-5.5, 6-8, and 11: Postgres-backed runtime, backend-resolved
  membership, append-only events, student read model, and Postgres `SKIP LOCKED` jobs.
- `backend-architecture.md` §12 and ADR-0014: consent is a durable entity and gates analytic
  projection without blocking the learner.
- `session-path-data-contract.md` §§5-11: sessions, paths, and student-safe reopen state survive
  process restarts.
- Parent M4 SDD §§6, 8.4, 10, 12-14.

## 2. Evidence Requiring Remediation

1. `create_app()` constructs `SessionRuntime.for_testing()` when no runtime is injected.
2. Render starts that default application; `DATABASE_URL` is not used by the API composition root.
3. API events, sessions, memberships, consent, catalog, and jobs are therefore in memory, while
   the worker uses Postgres. The two processes do not share state.
4. Live Supabase migration `20260702173751 / m4_catalog_auth_seed` is applied, but live M4
   membership/event/job/session rows remain empty after the recorded browser smoke.
5. Mobile implements a fixed Electricity smoke path, not dashboard re-entry, curriculum choice,
   auth restoration, or resume.
6. Expo web enters the Skia canvas without loading CanvasKit first.
7. The accepted JWT ADR selects HS256, while the live Supabase project issues ES256/JWKS tokens.
8. Focused backend tests pass only with explicit in-memory runtimes; mobile Jest and TypeScript
   gates are currently red.

## 3. Remediation Scope

### R1 — Production Composition

- `create_app()` must build a production runtime when `DATABASE_URL` is configured.
- Test fixtures may use `SessionRuntime.for_testing()` only through explicit injection.
- Production startup must fail closed when required database/auth configuration is missing.
- API and worker must share the same Postgres event store, jobs table, session read model,
  memberships, consent records, and catalog.
- Runtime workflows depend on typed ports/protocols, not concrete `InMemory*` classes.

### R2 — Durable Student Flow

- Bootstrap creates or reuses the B2C membership in `public.memberships` idempotently.
- Session start atomically appends events and persists `student_rm.sessions` state.
- Canvas hydration reads durable session ownership and reconstructs active nodes/edges from the
  durable event stream.
- Selected offer choices enqueue Postgres `classify` jobs; dismissed choices enqueue none.
- Dashboard and resume work after an API process restart.

### R3 — Consent Integrity

- Mobile presents an explicit B2C acknowledgement before first session start.
- Backend records both the append-only `consent_recorded` event and durable consent entity.
- Repeating bootstrap/start does not duplicate an unchanged consent grant.
- Worker consent checks observe the same durable record.

### R4 — JWT Decision Alignment

- ADR-0017 supersedes ADR-0015 for the live path: ES256/JWKS with issuer and audience validation.
- HS256 remains test-fixture compatibility only unless a future Supabase project explicitly uses it.
- JWT verification configuration is backend-only and explicit in Render/local runtime config.

### R5 — Catalog Forward Migration

- Do not rewrite the applied M4 migration.
- Add a forward migration aligning catalog tenancy/relationships with the canon and
  `core-operational-schema.md` §6.
- Add missing foreign-key indexes reported by the Supabase advisor.
- Validate RLS through a non-bypass pooled app-role connection.

### R6 — Mobile Closure Flow

- Restore/refresh authenticated Supabase sessions and support sign-out.
- Render dashboard Continue Learning and recent sessions.
- Render curriculum class/exam/subject/chapter/concept selection from API data.
- Start or resume a real session and hand its token/id to the canvas.
- Normal M4 builds use `EXPO_PUBLIC_API_BASE_URL`; local-only constants remain behind explicit
  development flags.

### R7 — Platform Gate

- Native Android remains the M4 human gate per `development-approach.md` §5 and §7.3.
- If web remains a supported smoke surface, CanvasKit must load before any Skia import/render and
  a web rendering smoke must cover the canvas handoff.

## 4. Red-First Verification Matrix

| ID | Red test / gate | Expected closure evidence |
|---|---|---|
| PR-1 | Default app with `DATABASE_URL` | Production runtime; no `InMemory*` adapters |
| PR-2 | Missing required production config | Startup fails with actionable error |
| PR-3 | Bootstrap twice | One active B2C membership |
| PR-4 | Start, recreate app/runtime, fetch dashboard/session | Same session and root node survive |
| PR-5 | Selected vs dismissed choice | Postgres job only for selected choice |
| PR-6 | Consent acknowledgement twice | One active consent entity; auditable event behavior |
| DB-1 | Execute forward migration against Postgres | Columns, constraints, indexes, RLS present |
| DB-2 | Two tenants through pool | Cross-tenant membership/session/catalog reads denied |
| MA-1 | Restore Supabase session | Dashboard loads without re-entering credentials |
| MA-2 | Dashboard resume | Existing canvas opens with real token/session id |
| MA-3 | Curriculum picker | API response fields drive visible selections |
| MA-4 | Missing production API URL | Release-mode startup fails closed |
| WEB-1 | Web canvas handoff | CanvasKit loads before Skia; no `PictureRecorder` error |

Python tests run with bytecode cleanup and a verified final `.pyc` count of zero.

## 5. Definition of Done

M4 may close only when:

1. Production API composition uses Postgres and shares state with the worker.
2. A restart-durability smoke passes: signup/bootstrap → start → branch → restart → dashboard →
   resume/hydrate.
3. Live Supabase contains the expected membership, consent, events, session, node/path, and job
   records for the smoke user, with no cross-tenant visibility.
4. Mobile implements auth restoration, dashboard, curriculum choice, start/resume, and canvas
   handoff without normal-path dev constants.
5. Consent entity/event behavior is durable and worker-visible.
6. JWT implementation and accepted ADR agree.
7. Parent SDD API parity table includes auth bootstrap and records router plus mobile-call-site
   verification.
8. Backend pytest, database/RLS tests, import-linter, full mobile Jest, and TypeScript are green.
9. Native Android human gate passes. Web is either explicitly excluded or its CanvasKit smoke passes.

## 6. 2026-07-11 Physical-Device Gate Findings

The native Android gate is in progress, not closed. Device evidence confirmed that login, recent
sessions, resume, the Electricity launch path, and canvas handoff work. It also found three M4
runtime defects that required remediation:

1. Dashboard load was slower than needed because mobile waited for the sequential curriculum path
   fetches before rendering dashboard state.
2. Learning-data acknowledgement appeared every run even when an active behavioral-analytics
   consent grant already existed for the account.
3. Sign-out cleared only local Expo SecureStore state; a following sign-in could hit the backend
   with a token that failed backend verification and surfaced as `Student API failed: 401: Invalid
   Supabase token`.

Read-only Supabase evidence showed password sign-in returning HTTP 200 and an active consent grant
for the device account, so the 401 was isolated to backend token verification/session handling, not
bad credentials. Backend logs showed repeated JWKS requests during one app initialization. The fix
is:

- cache the Supabase `PyJWKClient` per JWKS URL/client type, matching ADR-0017's ES256/JWKS path;
- return `behavioral_analytics_consent_granted` from auth bootstrap and suppress the first-run
  acknowledgement when true;
- render the dashboard after bootstrap/dashboard fetch, then load curriculum progressively;
- call Supabase `/auth/v1/logout` before local session clearing, with local clearing retained as a
  fallback.

The current M4 UI intentionally exposes only the Class 10 -> CBSE -> Science -> Electricity path.
That is the accepted M4 launch scope, not a newly discovered defect. General arbitrary curriculum
selection remains out of this milestone unless a higher-ranked SDD schedules it.

### 6.1 Post-remediation partial retest

After the 30-second bounded ES256 clock-skew correction, the physical device restored its stored
Supabase session successfully. Backend evidence shows bootstrap, dashboard, the complete API-derived
Class 10 -> CBSE -> Science -> Electricity path, session resume/hydration, event ingest, branching,
and new-session creation succeeding. The earlier `ImmatureSignatureError` did not recur.

Final user validation confirms the remaining native flow works after the correction. Auth
restoration/sign-in, dashboard, curriculum-path loading, resume, canvas handoff, new-session
creation, branching, and active session writes are verified. DB-2 passed through the configured
non-bypass pooled app-role connection. Interactive web is explicitly excluded from the M4 closure
gate under R7/definition-of-done item 9; the production web export with CanvasKit remains green and
interactive browser rendering is retained as a non-blocking follow-up.

The single visible curriculum path is intentional for M4. The client fetches class, exam, subject,
chapter, and concept-entry data from the API, but the live catalog currently supplies only Class 10
-> CBSE -> Science -> Electricity. Arbitrary multi-option curriculum selection is not required by
this bounded launch milestone.

## 7. Closure Record

M4 closed on 2026-07-11. All production-runtime, durable auth/consent/session, mobile native-flow,
automated-test, and pooled-RLS gates are satisfied. The user confirmed the corrected physical-device
flow is working. Curriculum loading performs five dependent API lookups for the single bounded path,
so a short progressive-loading delay is expected and is not a closure blocker. WEB-1 is explicitly
excluded from this native-first milestone; interactive web smoke remains follow-up work.
