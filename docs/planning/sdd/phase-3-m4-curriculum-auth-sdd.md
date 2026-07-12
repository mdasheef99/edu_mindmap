# Phase 3 M4 Curriculum Entry + Supabase Auth - Software Design Document (SDD)

**Document Version**: 0.1
**Status**: Draft - user review required
**Phase / milestone**: Phase 3 - M4
**Owner**: (developer)
**Live tracker**: `docs/planning/worklog-v9.md`

---

## 1. Increment Summary

| Item | Value |
|---|---|
| Increment name | B2C auth, curriculum entry, dashboard re-entry, and fixture-backed Electricity canvas flow |
| Phase / milestone | Phase 3 - M4 |
| Status | Draft - not implemented |

**Goal**: complete the first learner-visible app loop after M3 canvas maturation: a stranger can
sign up with Supabase Auth, reach a realistic curriculum path, start or resume Class 10 CBSE
Science - Electricity, and see content flow through the existing mind map canvas without dev-only
session/token constants.

M4 intentionally uses a deterministic fixture-backed generation simulator for the first launch
chapter. It must behave like real generation at the API/event/canvas boundary, but it does not call
a live LLM in this increment. Live generation remains a later provider swap behind the same
backend interface.

---

## 2. Source-of-Truth References

- `docs/planning/development-approach.md` Section 5 M4: Supabase Auth, exam/subject/chapter entry,
  dashboard re-entry, consent capture; gate is a stranger reaching a chapter unaided.
- `docs/planning/development-approach.md` Section 7.1: Supabase Auth; JWT `user_id`; role and
  tenant resolved server-side.
- `docs/architecture/backend-architecture.md` Sections 5.3-5.5: tenant isolation, Supabase Auth
  identity resolution, B2C/B2B coexistence.
- `docs/architecture/backend-architecture.md` Sections 6, 7.1, 9, 10, 11: append-only events,
  student read model, LLM gateway boundary, version stamping, API organization.
- `docs/architecture/adr-log-02.md` ADR-0015: accepted Supabase Auth JWT validation strategy
  using backend-side HS256 validation for MVP.
- `docs/api/student-api-spec.md` Sections 2-5: authenticated student API, curriculum endpoints,
  dashboard, session start/resume, and canvas hydration.
- `docs/database/core-operational-schema.md` Sections 2 and 6: Supabase Auth identity ownership,
  curriculum catalog tables, launchable chapter status, and chapter analysis references.
- `docs/database/schema-traceability-and-validation.md`: endpoint-to-table/event traceability for
  curriculum navigation, chapter metadata, session start, resume, and canvas state.
- `docs/prd/master-prd.md` Sections "Core product concept", "MVP scope", "Primary user journey",
  and "Minimum viable chapter coverage for launch": exam/subject/chapter/concept entry,
  chapter-bounded mind map exploration, and launch chapter readiness.
- `docs/mvp-features-specification.md` Feature Groups 1-4: curriculum navigation, dashboard,
  mind map canvas, and AI exploration nodes.
- `docs/configuration-reference.md` Sections 9-10: Supabase environment variables, JWT validation
  placeholders, and curriculum source configuration.
- `docs/planning/sdd/phase-3-m3c-infrastructure-remediation-sdd.md`: existing event ingest,
  canvas hydration, node position persistence, node delete reconciliation, and mobile event
  emission seams that M4 must reuse rather than rebuild.

---

## 3. Current Context and Constraints

M3-C, M3.5, and M3.6 are locally complete. The mobile canvas can hydrate a real session, emit
client events, persist node positions, reconcile deletion cascades, use edge-plus branching, use
phrase selection, and expose zoom/fit/reset/grid controls. M4 must replace the dev shell around
that canvas with real learner entry.

The current repository has these M4-relevant gaps:

1. The app still uses dev API/session/token wiring in the mobile shell.
2. The backend composition path still needs a production Postgres/Supabase runtime path equivalent
   to the worker's Postgres-backed adapters.
3. There are no student curriculum navigation or dashboard routers yet.
4. Existing `curriculum` ingestion tables store analyzed content, but the app-facing catalog
   described in `core-operational-schema.md` is not fully represented by current migrations.
5. Existing offer/node creation uses deterministic fixture text. M4 will formalize that as a
   fixture generation provider so behavior is intentional and later swappable.
6. Supabase MCP currently exposes a different project (`ahntbtktjjmvfosgkmgn`,
   `Bookconnect_reactexpo`) than the local Mindmap `.env` project ref
   (`jbmqyxhrmcbdgardamrp`). M4 migration SQL must therefore be committed locally for manual
   execution against the correct Supabase project, not applied through MCP in this session.

---

## 4. Scope

### In Scope

| Ref | Description |
|---|---|
| M4-A1 | Supabase email/password signup and login in the mobile app. |
| M4-A2 | Backend JWT verification against Supabase Auth tokens, resolving `user_id` to tenant and role from server-side memberships. |
| M4-A3 | B2C first-run membership bootstrap for an authenticated individual learner. |
| M4-C1 | Curriculum catalog migration/source SQL for class, exam, subject, chapter, concept entry, and analysis version metadata. |
| M4-C2 | Seed realistic launch catalog: Class 10 -> CBSE -> Science -> Electricity. |
| M4-C3 | Student curriculum endpoints for classes, exams, subjects, launchable chapters, chapter metadata, and concept entries. |
| M4-D1 | Student dashboard endpoint with Continue Learning and recent sessions. |
| M4-S1 | Start/resume Electricity session from curriculum selection, with no mobile-supplied authoritative tenant. |
| M4-G1 | Fixture generation provider with about 10 Electricity nodes that mimics real generation at the backend interface. |
| M4-G2 | Initial session start creates or ensures a root explanation node so the canvas is not empty. |
| M4-M1 | Mobile app shell: auth screens, dashboard, curriculum picker, chapter launch, and canvas handoff. |
| M4-T1 | Red-first backend and mobile tests for auth, curriculum, dashboard, fixture node creation, and canvas entry. |

### Out of Scope

- Live LLM generation, live model API keys, prompt tuning, and production cost accounting beyond
  preserving the provider boundary.
- Phone/OTP auth. The UI and auth client should be structured so phone OTP can be added later,
  but email/password is the M4 path.
- B2B school roster upload, invite activation, school admin panels, and teacher analytics.
- Checkpoints, podcast, PYQ node creation, broader offline sync, and admin/content-ops UI.
- Applying Supabase migrations through MCP. The correct database is not available to the MCP
  account in this session.

---

## 5. Product Flow

M4 ships one realistic learner path:

1. Learner opens the app and signs up or logs in with email/password.
2. Mobile stores the Supabase session token securely enough for the current Expo MVP surface.
3. Mobile calls the backend with the Supabase access token.
4. Backend verifies the JWT and resolves or bootstraps an active B2C `student` membership.
5. Learner lands on the dashboard.
6. If there is an active/recent session, Continue Learning can resume it.
7. Otherwise learner selects Class 10, CBSE, Science, Electricity.
8. Learner starts the chapter from the approved Electricity launch metadata.
9. Backend appends `session_started` and creates a root fixture-backed `node_created` event if the
   session has no root node.
10. Mobile opens the existing `SkiaCanvas` with the real session id and bearer token.
11. Edge-plus or phrase selection extends the canvas with fixture-backed child nodes.
12. Reload/resume hydrates the same student-safe canvas state through `GET /v1/student/sessions/{id}`.

---

## 6. Auth and Tenant Design

### 6.1 Mobile Auth

The mobile app uses Supabase Auth email/password for M4:

- `signUp(email, password)` creates the Supabase identity.
- `signInWithPassword(email, password)` returns the access token.
- The token is sent to the backend as `Authorization: Bearer <access_token>`.
- Phone/OTP is deferred. Adding it later must not change backend membership resolution because the
  backend depends only on Supabase `user_id`.

### 6.2 Backend Auth

Backend auth follows ADR-0015:

1. Verify the Supabase JWT using `SUPABASE_JWT_SECRET` in the backend environment.
2. Extract only the user id from token claims.
3. Resolve tenant and role from backend-owned memberships.
4. Ignore any mobile-supplied `tenant_id`, role, or membership claim.
5. Reject valid JWTs without a resolvable membership unless the request is the M4 B2C bootstrap
   path.

### 6.3 B2C Membership Bootstrap

M4 needs a narrow bootstrap path because individual signup precedes school/B2B onboarding:

- A configured shared individual tenant must exist.
- On first authenticated app entry, if the Supabase user has no active membership, backend creates
  one `memberships` row with role `student` in the individual tenant.
- The bootstrap path must be idempotent.
- The bootstrap path must not allow the mobile client to pick a tenant.
- B2B invite/roster activation remains out of scope.

### 6.4 Consent Capture

M4 captures the minimal consent state required by the current milestone gate:

- Record a B2C app consent acknowledgement before or during first session start.
- Append `consent_recorded` once per user/consent kind.
- Keep the current worker rule: classification/projection gates must honor consent state.
- Minor/guardian-grade consent UX and school-managed consent are deferred to B2B onboarding, but
  the data model must remain compatible with `backend-architecture.md` Section 12.

---

## 7. Curriculum Catalog and Seed Data

### 7.1 Required Catalog Shape

M4 needs the app-facing catalog from `core-operational-schema.md` Section 6:

- `curriculum_classes`
- `exams`
- `subjects`
- `chapters`
- `concept_entries`
- `chapter_analysis_versions`

Current Phase 2 `curriculum` tables (`curriculum.chapters`, `segments`, `concepts`,
`concept_edges`) remain the content-analysis store. M4 catalog rows should reference the approved
chapter analysis rather than duplicate analysis content.

### 7.2 Launch Seed

Initial seed path:

| Level | Value |
|---|---|
| Class | Class 10 |
| Exam/board | CBSE |
| Subject | Science |
| Chapter | Electricity |
| Launch status | approved/launchable |
| Concept entries | Root chapter entry plus selected Electricity concepts |
| Content source | Fixture-backed M4 node catalog, linked to the Electricity chapter analysis id |

The schema must support adding other classes, boards, exams, subjects, and chapters later without
changing the mobile navigation model.

### 7.3 Manual Supabase SQL

Because MCP is connected to the wrong project, M4 implementation must produce migration/source SQL
that the owner can manually run against the correct Supabase database. The SQL must be idempotent
where practical and must not hardcode generated production ids into schema DDL. Seed data may use
stable natural keys/slugs plus deterministic UUIDs only if documented.

---

## 8. Backend API Design

### 8.1 New Student Curriculum Router

Add `backend/app/api/student/curriculum.py` and register it in `main.py`.

| Endpoint | Purpose |
|---|---|
| `GET /v1/student/curriculum/classes` | List supported class/syllabus levels. |
| `GET /v1/student/curriculum/exams?class_id=...` | List exams/boards for a class. |
| `GET /v1/student/curriculum/subjects?class_id=...&exam_id=...` | List subjects. |
| `GET /v1/student/curriculum/chapters?class_id=...&exam_id=...&subject_id=...` | List launchable chapters only. |
| `GET /v1/student/chapters/{chapter_id}` | Student-safe chapter metadata. |
| `GET /v1/student/chapters/{chapter_id}/concept-entries` | Supported concept entry points. |

Responses must contain only curriculum/student-safe metadata. They must not include dimensional
availability, coverage, classification, confidence, gap, teacher, or analytic fields.

### 8.2 Dashboard Router

Add `GET /v1/student/dashboard` returning:

- authenticated learner display metadata if safe and available;
- Continue Learning candidate from recent active sessions;
- last five sessions;
- launchable curriculum suggestions, initially Electricity.

Dashboard data reads student-safe session state and curriculum catalog only.

### 8.3 Session Start Changes

`POST /v1/student/sessions` must:

1. Require authenticated `student` context.
2. Resolve chapter launchability from catalog/chapter analysis status.
3. Reject unapproved chapters.
4. Resolve `chapter_analysis_id` server-side.
5. Append `session_started`.
6. Ensure the root fixture node exists for a new session.
7. Return session id plus enough chapter metadata for mobile to open the canvas.

### 8.4 Production Runtime Wiring

M4 must add or finalize a Supabase/Postgres-backed API runtime path:

- Event store: Postgres adapter.
- Student sessions/nodes/canvas state: Postgres-backed or event-replay-backed adapter consistent
  with M3-C.
- Curriculum catalog: Postgres adapter.
- Memberships/consent: Postgres-backed adapter.
- Job queue remains Postgres `SKIP LOCKED`.

The in-memory runtime remains for tests, but the mobile M4 flow must not depend on dev-only
constants or local in-memory state.

---

## 9. Fixture Generation Simulator

### 9.1 Purpose

The fixture provider gives the learner the first sight of the real app while keeping M4 focused:
content appears in response to chapter start, edge-plus, and phrase-selection actions, but no live
LLM is called.

### 9.2 Provider Boundary

Introduce a generation boundary with two providers:

| Provider | M4 status | Behavior |
|---|---|---|
| `fixture_electricity_v1` | active | Deterministically returns seeded Electricity nodes and offer options. |
| `llm_stage1` | deferred | Later live provider using the same request/response contract. |

The backend should call the provider through a typed interface, not by embedding fixture text in
routers. Provider responses include:

- node title;
- node body/content;
- edge label;
- source node id or fixture parent key;
- `prompt_version` such as `fixture-electricity-v1`;
- `model_id` such as `fixture`;
- lineage metadata sufficient for later replay/projection compatibility.

### 9.3 Electricity Node Fixture Set

M4 fixture content should include about 10 nodes covering a realistic first path:

1. Electricity - chapter overview.
2. Electric current.
3. Potential difference.
4. Ohm's law.
5. Resistance.
6. Factors affecting resistance.
7. Series combination.
8. Parallel combination.
9. Heating effect of electric current.
10. Electric power.

The exact educational wording can be improved during implementation, but tests must assert shape,
lineage, and student-safe fields rather than exact prose.

### 9.4 Event Behavior

Fixture-backed node creation must still use the same event-sourced behavior expected by the real
provider:

- `node_created` for each created node.
- `edge_created` for each branch.
- existing `offer_set_created`, `offer_set_impression`, and `offer_set_choice` behavior remains.
- SELECTED choices continue to enqueue classification only according to the Organic-First rule.
- DISMISSED choices enqueue nothing.

---

## 10. Mobile Design

### 10.1 App Shell

Replace the dev shell with these screens/states:

1. Auth loading.
2. Login/signup.
3. Consent/first-run acknowledgement if needed.
4. Dashboard.
5. Curriculum picker.
6. Chapter detail/start.
7. Canvas.

This can be implemented as a simple state-machine in the current app shell for M4; a full routing
framework migration is not required unless it is already locally preferred by the repo.

### 10.2 Canvas Handoff

When a session is started or resumed, mobile passes the real values into existing canvas code:

- `apiBaseUrl`
- Supabase bearer token
- `sessionId`
- hydrated `nodes` and `edges`

`SkiaCanvas` internals should remain mostly unchanged. M4 should not rework gesture, layout,
edge-plus, phrase selection, toolbar, culling, or node-limit behavior unless required for auth
handoff.

### 10.3 Configuration

Mobile needs:

- `EXPO_PUBLIC_SUPABASE_URL`
- `EXPO_PUBLIC_SUPABASE_ANON_KEY`
- `EXPO_PUBLIC_API_BASE_URL`

Backend needs:

- `DATABASE_URL`
- `SUPABASE_JWT_SECRET`
- existing Sentry/LLM/test variables as applicable

No mobile-side LLM credentials are allowed.

---

## 11. Data Safety and Invariants

M4 remains bound by the merge-blocking canon:

- Category Invisibility: student APIs return no analytic fields.
- Organic-First: generation/fixture creation does not imply classification; selected choices
  enqueue classification asynchronously; dismissed choices do not.
- Tenant Isolation: backend-resolved tenant only; RLS remains a DB-level backstop.
- Event Sourcing: append-only event behavior and registry validation remain mandatory.
- No mobile-side AI/TTS credentials.
- Constants remain K=5 small-cohort suppression and 0.35 checkpoint cosine threshold, though
  checkpoint delivery is out of scope for M4.

---

## 12. TDD Test Plan

All tests must be written red before production code.

### 12.1 Backend Auth and Membership

| ID | Scenario | Expected |
|---|---|---|
| BA-1 | Valid Supabase-style JWT with existing membership | Resolves server-side tenant/role. |
| BA-2 | Mobile-supplied tenant differs from membership tenant | Backend ignores mobile tenant. |
| BA-3 | First B2C user without membership hits bootstrap path | Creates one student membership idempotently. |
| BA-4 | Invalid/expired JWT | 401. |
| BA-5 | Valid JWT without membership on non-bootstrap endpoint | 403 or membership-specific error. |

### 12.2 Backend Curriculum and Dashboard

| ID | Scenario | Expected |
|---|---|---|
| BC-1 | List classes | Includes Class 10. |
| BC-2 | List exams for Class 10 | Includes CBSE. |
| BC-3 | List subjects for Class 10 + CBSE | Includes Science. |
| BC-4 | List chapters for Class 10 + CBSE + Science | Includes only launchable Electricity. |
| BC-5 | Get Electricity chapter metadata | Student-safe response; no analytic fields. |
| BC-6 | Get concept entries | Returns approved fixture-backed entries. |
| BD-1 | Dashboard with no sessions | Shows launchable Electricity and no Continue Learning. |
| BD-2 | Dashboard after session start | Shows Continue Learning and recent session. |

### 12.3 Backend Fixture Generation and Sessions

| ID | Scenario | Expected |
|---|---|---|
| BG-1 | Start Electricity session | Appends `session_started` and root `node_created`. |
| BG-2 | Fetch session after start | Canvas contains root node. |
| BG-3 | Edge-plus choice | Creates fixture child node and edge through existing response shape. |
| BG-4 | Phrase-selection choice | Creates fixture child node and edge through existing response shape. |
| BG-5 | Attempt unlaunchable chapter | Rejects session start. |
| BG-6 | Fixture provider exhaustion or unknown path | Returns typed fallback/error without breaking canvas hydration. |

### 12.4 Database and RLS

| ID | Scenario | Expected |
|---|---|---|
| DB-1 | Migration creates catalog tables | Tables, keys, indexes, and RLS exist. |
| DB-2 | Seed SQL is idempotent | Re-run does not duplicate launch catalog rows. |
| DB-3 | Cross-tenant curriculum/session read through app role | Denied or filtered by tenant. |
| DB-4 | Student forbidden-column scan | `student_rm` remains free of analytic columns. |

### 12.5 Mobile

| ID | Scenario | Expected |
|---|---|---|
| MA-1 | Login/signup screen validates email/password basics | Calls Supabase client; handles loading/error states. |
| MA-2 | Authenticated app loads dashboard | Calls backend with bearer token. |
| MA-3 | Curriculum picker selects Class 10 -> CBSE -> Science -> Electricity | Calls documented curriculum endpoints. |
| MA-4 | Start chapter | Calls `POST /sessions` and opens canvas. |
| MA-5 | Resume session | Opens existing canvas from dashboard. |
| MA-6 | Canvas receives real token/session id | No dev session/token constants in the normal M4 path. |
| MA-7 | Existing canvas tests remain green | M3-C/M3.6 behavior not regressed. |

---

## 13. API Parity Check Required Before Closure

Per `development-approach.md` Section 6 discipline #10, M4 cannot close until every endpoint used
by the mobile M4 flow has a router and `main.py` registration.

| Endpoint | Router | M4 status before implementation |
|---|---|---|
| `GET /v1/student/dashboard` | `student/dashboard.py` | new |
| `GET /v1/student/curriculum/classes` | `student/curriculum.py` | new |
| `GET /v1/student/curriculum/exams` | `student/curriculum.py` | new |
| `GET /v1/student/curriculum/subjects` | `student/curriculum.py` | new |
| `GET /v1/student/curriculum/chapters` | `student/curriculum.py` | new |
| `GET /v1/student/chapters/{chapter_id}` | `student/curriculum.py` | new |
| `GET /v1/student/chapters/{chapter_id}/concept-entries` | `student/curriculum.py` | new |
| `POST /v1/student/sessions` | `student/sessions.py` | existing, needs M4 launch/root-node behavior |
| `GET /v1/student/sessions/{session_id}` | `student/sessions.py` | existing from M3-C |
| `POST /v1/student/sessions/{session_id}/resume` | `student/sessions.py` | existing |
| `POST /v1/student/sessions/{session_id}/events` | `student/events.py` | existing from M3-C |
| `PATCH /v1/student/sessions/{session_id}/nodes/{node_id}` | `student/nodes.py` | existing from M3-C |
| `DELETE /v1/student/sessions/{session_id}/nodes/{node_id}` | `student/nodes.py` | existing |
| `POST /v1/student/offer-sets/phrase` | `student/offer_sets.py` | existing |
| `POST /v1/student/offer-sets/edge` | `student/offer_sets.py` | existing |
| `POST /v1/student/offer-sets/{offer_set_id}/choices` | `student/offer_choices.py` | existing, needs fixture provider integration |

---

## 14. Definition of Done

M4 is locally complete when:

1. New M4 tests are written red-first and pass.
2. Backend pytest passes for affected suites, followed by required `.pyc` cleanup and verification
   that zero `.pyc` files remain.
3. Mobile Jest passes for affected suites and then full mobile suite.
4. Canvas TypeScript gate passes from `mobile/app` using the known compiler path.
5. Student API parity table in Section 13 is updated with implemented/registered status.
6. Migration/source SQL exists locally for manual Supabase execution against the correct project.
7. Manual SQL execution instructions identify the expected Mindmap project ref and warn against
   applying to the MCP-visible Bookconnect project.
8. App can sign up/login with email/password, load dashboard, select Electricity, start session,
   and open the canvas with at least the root fixture node.
9. Edge-plus or phrase selection can create additional fixture-backed nodes up to the seeded
   Electricity fixture set.
10. Existing Category Invisibility, Organic-First, Tenant Isolation, Event Sourcing, and no
    mobile-side AI credential invariants remain intact.

---

## 15. Open Decisions

| ID | Decision | Proposed M4 answer |
|---|---|---|
| OD-1 | Exact Supabase project used for manual SQL | Owner will run SQL against project ref `jbmqyxhrmcbdgardamrp`; MCP currently cannot access it. |
| OD-2 | Email/password vs phone OTP | Email/password for M4; phone OTP later. |
| OD-3 | Real generation vs fixture simulation | Fixture simulation for M4; real generation later behind same provider interface. |
| OD-4 | Admin/content panel for adding future exams | Deferred; M4 uses migration/seed/operator-ingested catalog. |
| OD-5 | B2C vs B2B first | B2C individual signup first; B2B roster/invite activation later. |
