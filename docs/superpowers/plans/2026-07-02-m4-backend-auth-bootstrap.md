# M4 Backend Auth + B2C Bootstrap Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Verify Supabase JWTs and create an idempotent B2C student membership without letting the mobile client choose tenant, role, or membership state.

**Architecture:** Keep identity in Supabase Auth and product context in backend-owned membership rows. `Authorization: Bearer <token>` yields only a Supabase `user_id`; backend resolves or bootstraps the active B2C `student` context.

**Traceability:** M4 SDD Sections 6 and 12.1; `development-approach.md` Sections 5 and 7.1; `backend-architecture.md` Sections 5.3-5.5 and 11; ADR-0015.

---

## Files

- Modify: `backend/app/tenancy/memberships.py`
- Modify: `backend/app/tenancy/membership_auth.py`
- Modify: `backend/app/tenancy/auth.py`
- Modify: `backend/app/runtime/session.py`
- Test: `tests/integration/test_m4_auth_bootstrap.py`

## Task 1: Red Tests

- [ ] Add `tests/integration/test_m4_auth_bootstrap.py`.
- [ ] Cover valid JWT with existing membership -> resolved tenant/role.
- [ ] Cover mobile-supplied tenant mismatch -> backend ignores mobile tenant.
- [ ] Cover first B2C user without membership on bootstrap path -> one `student` membership in configured individual tenant.
- [ ] Cover repeated bootstrap -> no duplicate membership.
- [ ] Cover invalid/expired JWT -> 401.
- [ ] Cover valid JWT without membership on non-bootstrap endpoint -> 403 membership-specific error.

Run:

```powershell
pytest tests/integration/test_m4_auth_bootstrap.py -q
```

Expected: fail because bootstrap support is missing or incomplete.

## Task 2: Minimal Implementation

- [ ] Add `ensure_student_membership(user_id, individual_tenant_id)` to the in-memory membership store.
- [ ] Keep tenant choice server-side only.
- [ ] Keep non-bootstrap endpoints strict: valid JWT without active membership returns 403.
- [ ] Add a narrow runtime bootstrap method used by the M4 app entry/session bootstrap flow.
- [ ] Do not add B2B activation, roster, invite, or phone/OTP behavior.

## Task 3: Green And Cleanup

Run:

```powershell
pytest tests/integration/test_m4_auth_bootstrap.py -q
```

After Python tests:

```powershell
Get-ChildItem -Path . -Recurse -Filter *.pyc | Remove-Item -Force
$pycCount = (Get-ChildItem -Path . -Recurse -Filter *.pyc | Measure-Object).Count
if ($pycCount -ne 0) { throw "Remaining .pyc count: $pycCount" }
```

Expected: auth/bootstrap tests pass and `.pyc` count is zero.
