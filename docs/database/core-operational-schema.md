# Core Operational Schema

**Document Version**: 1.1 (M4 runtime alignment)
**Status**: Current MVP schema baseline  
**Scope**: Tenancy, membership, consent, curriculum, PYQ, and media metadata

---

## 1. Purpose

This document defines the operational tables needed by the FastAPI modular monolith before read-model projection. It aligns with `docs/operations/b2b-onboarding-runbook.md`, the API suite, and the v1.3+ tenant-first architecture.

## 2. Tenancy Tables

### `tenants`

| Column | Notes |
|---|---|
| `tenant_id` | UUID primary identifier |
| `kind` | `individual` or `institutional` |
| `name` | display/admin name |
| `status` | `active`, `suspended`, `offboarding`, `closed` |
| `region` | deployment/data residency region marker |
| `created_at`, `updated_at` | audit timestamps |

### `institutions`

| Column | Notes |
|---|---|
| `institution_id` | UUID primary identifier |
| `tenant_id` | institutional tenant |
| `name` | school/institution name |
| `board` | CBSE, ICSE, state code, or other supported board |
| `billing_ref` | external contract/billing reference |
| `verified` | institution identity verification flag |
| `admin_contact_ref` | pointer to approved admin contact record |
| `created_at`, `updated_at` | audit timestamps |

### `tenant_migrations`

Tracks B2C to B2B or tenant-transfer operations. Endpoint contracts are deferred to admin/internal specs.

| Column | Notes |
|---|---|
| `migration_id` | UUID |
| `from_tenant_id`, `to_tenant_id` | source/target tenant |
| `user_id` | affected user |
| `reason` | migration reason |
| `status` | `requested`, `approved`, `completed`, `failed`, `cancelled` |
| `event_id` | associated `tenant_migration` event |
| `created_at`, `completed_at` | lifecycle timestamps |

## 3. Identity and Membership Tables

Supabase Auth owns credential identity. FastAPI resolves product context from operational tables.

### `user_profiles`

| Column | Notes |
|---|---|
| `user_id` | Supabase Auth user identifier |
| `display_name` | safe display name |
| `date_of_birth` | optional; used for minor/guardian rules |
| `guardian_contact_ref` | pointer to guardian contact where required |
| `created_at`, `updated_at` | audit timestamps |

### `memberships`

| Column | Notes |
|---|---|
| `membership_id` | UUID |
| `tenant_id` | tenant scope |
| `user_id` | member user |
| `role` | `student`, `teacher`, `approved_teacher`, `school_admin`, `admin` |
| `status` | `provisional`, `active`, `suspended`, `ended` |
| `active_from`, `active_to` | interval model; close intervals, never delete history |
| `created_at`, `updated_at` | audit timestamps |

### `classes`

| Column | Notes |
|---|---|
| `class_id` | UUID |
| `tenant_id` | school/institution tenant |
| `name` | school-facing class/batch name |
| `grade_level` | class/syllabus level |
| `subject_id` | optional subject-scoped class |
| `academic_year` | year/term label |
| `status` | `active`, `archived` |

### `class_memberships`

| Column | Notes |
|---|---|
| `class_membership_id` | UUID |
| `tenant_id` | tenant scope |
| `class_id` | class/batch |
| `student_user_id` | student |
| `active_from`, `active_to` | membership interval |
| `source` | roster, migration, admin correction |

### `teaching_assignments`

| Column | Notes |
|---|---|
| `teaching_assignment_id` | UUID |
| `tenant_id` | tenant scope |
| `class_id` | assigned class |
| `teacher_user_id` | teacher |
| `active_from`, `active_to` | assignment interval |
| `status` | `active`, `ended`, `suspended` |

## 4. B2B Onboarding Support Tables

These tables support the runbook, but endpoint contracts are deferred to `admin-api-spec.md`.

### `roster_batches`

| Column | Notes |
|---|---|
| `roster_batch_id` | UUID |
| `tenant_id` | institution tenant |
| `uploaded_by_user_id` | school admin/platform actor |
| `status` | `uploaded`, `validated`, `applied`, `failed` |
| `row_count` | input count |
| `error_summary` | sanitized validation summary |
| `event_id` | `roster_uploaded` event |

### `provisional_accounts`

| Column | Notes |
|---|---|
| `provisional_account_id` | UUID |
| `tenant_id` | institution tenant |
| `roster_batch_id` | source batch |
| `student_user_id` | nullable until credential binding |
| `external_student_ref` | school-provided pseudonymous ref |
| `status` | `provisional`, `code_issued`, `activated`, `consent_pending`, `active` |

### `activation_codes`

| Column | Notes |
|---|---|
| `activation_code_id` | UUID |
| `tenant_id` | institution tenant |
| `provisional_account_id` | target provisional account |
| `code_hash` | hashed code only |
| `expires_at` | expiry timestamp |
| `redeemed_at` | nullable |
| `invalidated_at` | nullable |
| `attempt_count` | rate-limit/audit support |

## 5. Consent Tables

### `consent_records`

| Column | Notes |
|---|---|
| `consent_id` | UUID |
| `tenant_id` | tenant scope |
| `student_user_id` | student subject |
| `consent_kind` | `data_processing`, `behavioral_analytics`, other configured kinds |
| `state` | `granted`, `withdrawn`, `pending` |
| `grantor_user_id` | parent/guardian/student as allowed |
| `method` | `otp_link`, `signed_form_reference`, `admin_recorded` |
| `granted_at` | nullable |
| `withdrawn_at` | nullable |
| `source_ref` | form/checklist reference |
| `event_id` | associated `consent_recorded` event |

Behavioral analytics consent gates classification/projection inclusion and teacher panels. Student service access may continue while analytic panels are withheld.

## 6. Curriculum Tables

| Table | Purpose | Key Fields |
|---|---|---|
| `curriculum_classes` | class/syllabus levels | `class_level_id`, `tenant_id`, `label`, `sort_order` |
| `exams` | CBSE, ICSE, state boards, NEET, JEE, etc. | `exam_id`, `tenant_id`, `class_level_id`, `name`, `status` |
| `subjects` | exam/class subjects | `subject_id`, `tenant_id`, `exam_id`, `name`, `status` |
| `chapters` | launchable chapter catalog | `chapter_id`, `tenant_id`, `subject_id`, `title`, `status`, `chapter_analysis_id` |
| `concept_entries` | supported session entry points | `concept_entry_id`, `tenant_id`, `chapter_id`, `title`, `status` |
| `chapter_analysis_versions` | analysis version registry | `chapter_analysis_id`, `tenant_id`, `chapter_id`, `qa_status`, `version`, `generated_at` |

Only chapters with approved launch status and required analysis references may be used to start sessions.

Migration `0007_m4_runtime_remediation.sql` is the forward-only correction for the already-applied
M4 seed: it adds/backfills missing `tenant_id` on `curriculum_classes`, `exams`, `subjects`,
`chapter_analysis_versions`, and `concept_entries`; makes the columns non-null; adds tenant foreign
keys and indexes; and replaces permissive catalog policies with tenant-isolation RLS policies.
`chapters` already carried `tenant_id` before this remediation.

## 7. PYQ Tables

| Table | Purpose | Key Fields |
|---|---|---|
| `pyq_questions` | previous year question records | `question_id`, `exam_id`, `subject_id`, `chapter_id`, `year`, `question_text`, `difficulty`, `status` |
| `pyq_solutions` | solution/explanation records | `solution_id`, `question_id`, `solution_text`, `source_ref`, `status` |
| `pyq_topic_links` | optional concept mapping | `question_id`, `concept_entry_id`, `chapter_id` |

PYQ records are backend-curated, not generated placeholders in the student API.

## 8. Media Metadata Tables

| Table | Purpose | Key Fields |
|---|---|---|
| `media_assets` | uploaded image/audio metadata | `media_id`, `tenant_id`, `owner_user_id`, `storage_key`, `media_type`, `status` |
| `video_links` | validated video URL metadata | `video_link_id`, `tenant_id`, `url`, `provider`, `title`, `thumbnail_url`, `status` |

Supabase Storage holds bytes. Database rows hold metadata and authorization context.
