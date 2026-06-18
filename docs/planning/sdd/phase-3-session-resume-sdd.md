# Phase 3 Session Resume — Software Design Document (SDD)

**Document Version**: 1.0 (active draft)  
**Status**: Completed locally — green first Phase 3 slice  
**Phase / milestone**: Phase 3 — Core Loop Deepening, M1 session persistence + resume  
**Live tracker**: `docs/planning/worklog-v4.md`

---

## 1. Increment Identity

| Field | Value |
|---|---|
| Increment name | Student session resume and recent-session API |
| Phase / milestone | Phase 3 — Core Loop Deepening, M1 |
| Owner | (developer) |
| Status | Active |

Goal: add the smallest backend slice needed for mobile dashboard re-entry: authenticated students can
list their most recent sessions and resume one previously started session. The slice uses the existing
`student_rm.sessions` projection and remains category-invisible.

## 2. Source-of-Truth References

- `development-approach.md` §5 M1: Core loop deepening includes session persistence + resume;
  §8 requires one small traceable increment with tests.
- `backend-architecture.md` §2.2, §7.1, §11: `/v1/student` reads from student-safe domain/read-model
  types only; `student_rm` contains render/resume state and no dimensional fields.
- `backend-architecture.md` §5.3–§5.5: tenant is backend-resolved, RLS is the DB backstop, and B2C
  student ownership remains scoped within the tenant.
- `backend-architecture.md` §6.2: session lifecycle events include `session_resumed`.
- `session-path-data-contract.md` §5, §8, §11, §14: sessions carry resume context; session
  opened/resumed events are part of path reconstruction; local/offline reopen remains narrow.
- `master-prd.md` §6: MVP includes dashboard re-entry, recent-session access, session persistence,
  and basic offline access to previously stored content.
- `mvp-features-specification.md` Feature Group 2 and Feature 7.1: Continue Learning, Recent
  Sessions, and session persistence support learning continuity.
- `mobile-features-core-ui.md` §1.3: Continue learning card and recent sessions list.
- `mobile-features-system.md` §7.3: basic offline access is limited to reopening previously stored
  online content; no offline editing, sync queue, or offline AI.

## 3. Scope of Increment

**In scope:**
- `GET /v1/student/sessions/recent` returns up to the five most recent sessions owned by the
  authenticated student in the backend-resolved tenant.
- `POST /v1/student/sessions/{session_id}/resume` returns the requested student-safe session and
  appends a `session_resumed` event for path reconstruction.
- Both endpoints use `domain/student` response models and contain no analytic/category fields.
- Tenant and ownership checks run through the existing tenant-scoped pool helper in tests.

**Out of scope:**
- Mobile AsyncStorage implementation and physical-device Expo smoke.
- Node/edge persistence, edge-`+` branching, phrase selection, deletion cascade, and canvas gestures.
- Offer-set impression completion beyond the existing selected/dismissed choice capture.
- Checkpoints, teacher V3, class dashboards, podcast generation, broader offline editing/sync.

## 4. Traceability Rows

| Feature | Endpoint | Event | Read Model | Worker Job | Table(s) |
|---|---|---|---|---|---|
| Recent sessions | `GET /v1/student/sessions/recent` | none | `student_rm.sessions` | none | `student_rm.sessions` |
| Resume session | `POST /v1/student/sessions/{session_id}/resume` | `session_resumed` | `student_rm.sessions` | none | `events`, `student_rm.sessions` |

## 5. Module Placement & Import Rules

| Concern | Module | Rule |
|---|---|---|
| Student-safe session types | `app.domain.student.sessions` | no analytic/category fields |
| Session projection reads | `app.projections.student_sessions` | tenant + student ownership filters |
| API router | `app.api.student.sessions` | may import student domain and auth only |
| Runtime orchestration | `app.main.SessionRuntime` | append event, project, and return student model |
| Tenant backstop | `app.tenancy.pool` | transaction-scoped tenant context per read |

Existing import-linter contracts remain merge-blocking: `api/student` must not import `analytic`,
`classification`, or dimensional projections.

## 6. Event / Schema Deltas

- Register `session_resumed` v1 with server/client producer allowance and required fields:
  `actor_user_id`, `student_id`, and `session_id`.
- No migration is required for this in-memory slice; the existing Phase 1 event table already accepts
  registered event envelopes.
- No `analytic_rm` table is read or written.

## 7. API Contracts

### `GET /v1/student/sessions/recent`

Returns `200` with a JSON list of up to five `StudentSession` objects ordered by `last_active_at`
descending. It returns only sessions for `auth.tenant_id` and `auth.user_id`.

### `POST /v1/student/sessions/{session_id}/resume`

Returns `200` with a `StudentSession` when the session exists for `auth.tenant_id` and `auth.user_id`.
Returns `404` otherwise. A successful resume appends `session_resumed` and updates the student read
model's `last_active_at` from that event.

## 8. Test Plan

First red tests:
- T1: recent endpoint returns at most five owned sessions, newest first, with no analytic fields.
- T2: resume endpoint appends `session_resumed`, updates `last_active_at`, and returns a student-safe
  payload.
- T3: another tenant cannot resume a session through the pooled path.

Validation gates:
- Focused integration tests for this slice.
- Existing student session and tenant-isolation tests.
- Ruff format/check, MyPy, and full pytest if time permits.

## 9. Definition of Done

- Active SDD is present and canon points to it.
- Red tests fail before production code and pass after implementation.
- `/v1/student` remains category-invisible and exposes no raw event endpoint.
- Tenant and ownership isolation are covered by tests.
- `docs/planning/worklog-v4.md` records the slice, validations, and remaining Phase 3 work.