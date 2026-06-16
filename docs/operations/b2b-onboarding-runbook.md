# B2B Onboarding and Operations Runbook

**Document Version**: 1.0 (draft)
**Status**: Proposed
**Audience**: Platform operations, customer success, and support staff
**Related Documents**: `docs/architecture/backend-architecture.md` (§5 tenancy, §12 DPDP),
`docs/teacher-access-control-specification.md`, `docs/teacher-support-mvp-specification.md`,
`docs/teacher-dashboard-specification.md`

---

## 1. Purpose

This runbook operationalizes the tenancy and consent model of
`docs/architecture/backend-architecture.md` §5 and §12 into step-by-step procedures for
onboarding a school, running it through the academic year, and offboarding it at contract end.

| Relationship | Document | Detail |
|--------------|----------|--------|
| **Operationalizes** | Backend architecture §5.1–§5.5 | Tenant/institution/class entities, roster flows, interval memberships, B2C↔B2B migration |
| **Operationalizes** | Backend architecture §12 | Consent records, consent-pending state, withdrawal, erasure |
| **Depends on** | `docs/teacher-access-control-specification.md` | Teacher credential verification remains a platform-level step (§7 below) |
| **Depends on** | Backend §11 `/v1/admin` and `/v1/internal` routers | All operations below are performed through these surfaces; nothing in this runbook is a direct database edit |

**Standing rules** (apply to every procedure in this document):

1. **No direct database edits.** Every change goes through `/v1/admin` (school admin) or
   `/v1/internal` (platform ops, MFA + audit logging). Tenancy and membership changes emit
   `roster_uploaded` / `membership_changed` / `consent_recorded` / `tenant_migration` events.
2. **History is never deleted.** Roster changes close and open membership intervals
   (`active_from` / `active_to`); nothing is removed (backend §5.2.4).
3. **Consent gates analytics, not service.** A student without recorded behavioral-analytics
   consent can still explore; no dimensional profile is built and no teacher view renders them
   (backend §12.3).
4. **PII lives in tenancy tables only** — never in event payloads (backend §6.3.2).

---

## 2. Onboarding Overview

```
Stage 0  Contract signed → tenant + institution provisioned     (platform ops)
Stage 1  School admin account created and verified              (platform ops)
Stage 2  Classes created                                        (school admin)
Stage 3  Roster CSV uploaded and validated                      (school admin)
Stage 4  Provisional accounts + activation codes distributed    (school admin / school)
Stage 5  Parental consent collected; accounts activate          (parents / students)
Stage 6  Teachers invited and verified                          (school admin / platform)
```

Stages 2–6 can overlap. A school is "live" when ≥ 1 class has activated students with recorded
consent and ≥ 1 verified teacher holds an active teaching assignment.

---

## 3. Stage 0 — Tenant Provisioning (platform ops)

**Trigger**: signed contract with billing reference.

1. Create the tenant: `kind = institutional`, school name. One tenant per school — never share
   a tenant across schools, never create a second tenant for the same school (backend §5.1).
2. Create the `institutions` row: name, board (CBSE / state code), `billing_ref`, admin
   contact(s). Leave `verified = false`.
3. **Verification**: confirm the school's identity (registration documents or board affiliation
   number, per the sales checklist) → set `verified = true`. Unverified institutions must not
   proceed to Stage 3 (no minor PII enters an unverified tenant).
4. **Data residency check**: confirm the deployment serving this tenant runs in an Indian
   region, including backups (backend §12.6). This is a per-deployment invariant; the
   onboarding checklist records that it was checked, not a per-tenant toggle.
5. Record the contract's **data-handling terms**: retention on contract end, whether the school
   acts as consent-collection conduit (§5), agreed offboarding window (§10). These drive Stage
   5 and offboarding behavior.

**Output**: tenant_id; institution profile; checklist record.

---

## 4. Stages 1–2 — School Admin and Class Setup

### 4.1 School admin account (platform ops)

1. Invite the named admin contact by email; accepting creates a `memberships(role =
   school_admin)` row in the school's tenant.
2. `school_admin` capabilities (backend §5.3, §11): institution profile, class management,
   roster upload, activation-code lifecycle, teacher invitations, consent-record views,
   school-level aggregates. **No individual-student analytic drill-down** — that stays with
   the teaching relationship.
3. If the admin also teaches, they additionally need a teacher membership and verification
   (§7); the roles are separate memberships, not a merged super-role.

### 4.2 Class setup (school admin)

1. Create classes: name ("Class 10-B", "NEET Batch A"), subject, grade band, academic year.
2. Convention: one class per teaching group per subject. A physical classroom taught two
   subjects by two teachers = two classes. This keeps teaching assignments and teacher
   dashboard scoping correct.
3. Classes are created before rosters; the roster CSV references classes by exact name.

---

## 5. Stage 3 — Roster CSV Upload and Validation

### 5.1 CSV contract

One row per student per class. Required columns:

| Column | Rule |
|--------|------|
| `student_name` | Non-empty; stored in tenancy tables only |
| `class_name` | Must exactly match an existing class in this tenant |
| `parent_contact` | Phone (for OTP consent flow) or email; validated for format |
| `roll_no` (optional) | School-local identifier, helps the school reconcile |
| `date_of_birth` (optional) | Used only to determine minor status where provided |

Encoding UTF-8; header row mandatory.

### 5.2 Validation (automatic, on upload via `/v1/admin`)

| Check | On failure |
|-------|-----------|
| Header/format/encoding valid | Reject file with line-level errors |
| `class_name` resolves | Reject **row**, report unresolved names |
| `parent_contact` format valid | Reject row |
| Duplicate row within file (same name + class) | Reject duplicate rows, keep first |
| Probable existing student (same name + parent contact already in tenant) | Hold row for admin review — **never auto-create a second account** |

Validation is **row-level with a report**: valid rows proceed, invalid rows return in a
downloadable error report for correction and re-upload. Re-uploading corrected rows is safe:
the duplicate check makes the operation idempotent.

The upload emits one `roster_uploaded` event (file hash, counts, admin id) and
`membership_changed` events per created membership.

### 5.3 What upload creates

Per accepted row (backend §5.2): a `users` row, a `memberships(role = student)` row, and a
`class_memberships` interval — all **provisional**: no login credential exists yet, no consent
is recorded, and the consent-pending rule (§6.4) applies.

---

## 6. Stages 4–5 — Activation, Consent, and the Consent-Pending State

### 6.1 Activation code distribution

1. After roster acceptance, the school admin generates **activation codes** (one per student)
   or **parent-OTP links** (sent to `parent_contact`) from the admin console.
2. Codes are distributed by the school (printed slips, school communication app — the school's
   choice). Codes are single-use, expire after a configurable window (default 30 days), and are
   reissuable (§9).
3. The admin console shows per-class activation status: *provisional → code issued → activated →
   consent recorded*. This funnel is the primary onboarding health view.

### 6.2 First login (student/parent device)

First login with an activation code binds the credential (Supabase Auth identity) to the
provisional account and starts the consent flow.

### 6.3 DPDP consent collection

Per backend §12 — DPDP Act 2023 requires verifiable parental/guardian consent for minors:

1. The consent flow addresses the **parent/guardian**, not the student: plain-language notice
   (data collected, purpose, teacher visibility, withdrawal rights), then consent capture.
2. **Method** (records the grantor, never the school as proxy by default):
   - **Parent-OTP**: OTP to `parent_contact`; completion creates the consent record with
     `method = otp_link`.
   - **Signed school form**: where the contract designates the school as collection conduit
     (Stage 0.5, pending counsel review per backend §12.2), the school collects signed forms;
     the admin records consent with `method = signed_form_reference` + form reference. The
     record still names the guardian.
3. **Two consent kinds** are captured distinctly (backend §12.1): *data processing* (service
   operation) and *behavioral analytics for teacher support*. A parent may grant the first and
   decline the second.
4. Each grant emits `consent_recorded`; the `consent_records` row stores student, kind, grantor,
   method, timestamp.

### 6.4 The consent-pending state

Between activation and consent (or where analytics consent is declined/withdrawn), backend
§12.3 applies — operationally:

| Works | Does not happen |
|-------|-----------------|
| Exploration, canvas, AI nodes, PYQs, podcasts — full student product | `classify` / `project` workers skip the student: no dimensional profile, no coverage |
| Raw events still captured (service operation + later consent) | Student does not appear in teacher views ("consent pending" placeholder in roster) |
| Roster/membership management | Inclusion in class aggregates |

**Support note**: "teacher can't see student X" is most often this state, not a bug. Check the
consent funnel first (§9, F6).

---

## 7. Stage 6 — Teacher Invitation and Verification

1. School admin invites teachers by email from the admin console.
2. Accepting creates `memberships(role = teacher)` in the school's tenant.
3. **Platform credential verification** (per `docs/teacher-access-control-specification.md`)
   remains mandatory — an institutional membership does not bypass it (backend §5.2). Until
   verified, the teacher has no analytic access.
4. The admin assigns verified teachers to classes → `teaching_assignments` intervals.
5. Teacher dashboard scope follows automatically (backend §5.3): students with an *active*
   class membership in classes where the teacher holds an *active* assignment. No extra
   permission setup exists or is needed.

---

## 8. Ongoing Operations — Mid-Year Roster Changes

All changes are interval edits; history is never deleted (standing rule 2). As-of-event-time
joins (backend §7.4) keep historical aggregates correct automatically.

| Change | Procedure |
|--------|-----------|
| Student joins a class | New `class_memberships` interval (`active_from = now`). If new to the school: single-row roster addition → Stages 4–5 for that student |
| Student leaves a class | Set `active_to = now` on the interval. Account and history remain |
| Student changes class | Close old interval, open new one (same account) |
| Student leaves the school | Close all class memberships + the tenant membership. Data handling per §10.3 |
| Teacher leaves / reassigned | Close `teaching_assignments` interval(s); dashboard access ends immediately with them |
| New academic year | Create new classes for the new year; close old class memberships; bulk-assign via a roster CSV referencing the new classes. Old classes stay queryable as history |
| B2C student joins the school plan | `tenant_migration` (backend §5.5): new membership in school tenant, close individual-tenant membership. Historical-event transfer is a **consent decision** — requires fresh parental consent naming the transfer; default is no transfer |

---

## 9. Failure Modes and Remediation

| # | Failure | Remediation |
|---|---------|-------------|
| F1 | CSV rejected wholesale (encoding/header) | Return template + error report; support can supply a pre-validated template. Never hand-edit data into the database |
| F2 | Rows held as probable duplicates | Admin reviews: same child → discard row (or add class membership to existing account); different child with same name → confirm via roll_no/DOB, then force-create with an audit note |
| F3 | Activation code lost / expired | Admin reissues from console; old code is invalidated. Reissue is logged |
| F4 | OTP goes to a wrong/stale parent number | Admin corrects `parent_contact` (logged change), reissues. If consent was already recorded against the wrong contact, escalate to L3 (§9.1) — consent integrity issue, the record must be voided and recollected |
| F5 | Student activated but consent stalled | Funnel view identifies these; school nudges parents. Product remains usable (§6.4) — no emergency |
| F6 | "Teacher can't see student" | Checklist: (1) consent recorded for *analytics* kind? (2) class membership active? (3) teaching assignment active? (4) teacher verified? (5) cohort below K-suppression in aggregate views? In that order |
| F7 | Roster uploaded to wrong class | Close the wrong intervals, open correct ones. Events already emitted are unaffected (they carry student ids, and as-of joins use the corrected intervals going forward; a projection rebuild corrects historical aggregates if needed) |
| F8 | Consent withdrawal mid-year | Record withdrawal timestamp → workers stop including the student immediately; projection rebuild without the student (backend §12.4 — a replay, not surgery). Confirm teacher views no longer render them |
| F9 | Erasure request (parent) | L3 only: delete tenancy-table PII, tombstone the pseudonymous id (backend §12.4). Raw-event purge vs. de-identification follows the counsel position (backend §14.2); track each request in a register with statutory deadlines |
| F10 | School demands a student's "scores" | Not a data operation — the product has none (no grades/mastery; `docs/teacher-support-mvp-specification.md` §8). Customer-success conversation, escalate to L2 with the claim-boundary talking points |

### 9.1 Support escalation paths

| Level | Who | Handles |
|-------|-----|---------|
| L1 | Support | Funnel checks (F3, F5, F6), CSV help (F1), how-to |
| L2 | Customer success + ops | F2, F7, expectation management (F10), contract-term questions |
| L3 | Platform engineering + DPO/legal | Consent integrity (F4), withdrawal/erasure (F8, F9), `tenant_migration`, anything touching `/v1/internal` |

L3 actions require platform `admin` role + MFA and are audit-logged (backend §5.3). Erasure and
consent-integrity incidents are additionally tracked in the compliance register.

---

## 10. Offboarding and Contract End

### 10.1 Sequence

1. **Close access**: at contract end date, close all `teaching_assignments` and `school_admin`
   memberships. Teacher/admin dashboards go dark immediately; nothing is deleted.
2. **Student decision window** (length per contract, default 60 days): each family chooses —
   - **Continue B2C**: `tenant_migration` to the shared `individual` tenant with fresh consent
     (the parent now contracts directly). Event-history transfer follows the same consent
     decision as §8's migration row.
   - **Lapse**: account deactivates at window end (membership closed, credential disabled).
3. **Data handling at window end**, per contract terms recorded at Stage 0.5:
   - PII in tenancy tables for lapsed accounts: deleted or retained per contract + DPDP
     retention position (counsel item, backend §14.2).
   - Pseudonymous events: retained de-identified for research unless erasure was requested
     (the §6.3.2 pseudonymization boundary exists to make this defensible).
4. **Tenant closure**: institution marked inactive; tenant row retained (audit anchor for
   events that carry its `tenant_id`). Tenants are never reused.

### 10.2 School-requested data export at exit

Aggregate-level exports only, consistent with the product's claim boundaries; no per-student
dimensional data leaves the platform (it is interpretation, not a record of attainment).
Per-student raw data requests route to L3 as data-subject requests (parents, not the school,
are the data principals).

### 10.3 Individual student exit (mid-contract)

Same as 10.1 steps 2–3 scoped to one student — the decision belongs to the family, not the
school.

---

## 11. Open Items

1. Counsel review (backend §14.2) of: school as consent-collection agent, erasure scope for raw
   events, retention defaults — §6.3 and §10 carry the schema for either outcome.
2. Activation-code expiry and decision-window defaults are config; confirm with first pilot.
3. Hindi/regional-language consent notices and parent-facing flows.
4. Whether the admin console funnel view needs export (CSV of activation status) for school
   follow-up — likely yes, scope with first pilot.
5. SLA definitions per support level (response/resolution times) — set with the first contract.

---

*Document Version 1.0 (draft) | B2B Onboarding and Operations Runbook*
*Platform: Path-Based Conceptual Exploration and Teacher-Support System*
