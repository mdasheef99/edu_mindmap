# Read Models Schema

**Document Version**: 1.0 (draft)  
**Status**: Current MVP schema baseline  
**Scope**: `student_rm` and `analytic_rm`

---

## 1. Purpose

This document defines the physically separate student and analytic read models. This separation is the database-level enforcement of Category Invisibility from ADR-0003.

## 2. Ownership Rules

| Schema | Owner | Written By | Read By |
|---|---|---|---|
| `student_rm` | student domain | student router, student-safe projections, workers for summaries/podcasts | `/v1/student` |
| `analytic_rm` | analytic/projection domain | projection/classification workers | `/v1/teacher`, internal/replay tools |

`/v1/student` must never read from `analytic_rm`.

## 3. `student_rm` Allowed Scope

`student_rm` stores only render/resume state and student-safe artifacts.

Allowed concepts:

- sessions
- nodes
- edges
- node summaries
- current offer sets
- student-safe checkpoint offers
- podcasts
- local-resume state references

Forbidden concepts:

- dimensions, scores, coverage, classifications
- entropy, dispersion, confidence, vectors
- gap labels, teacher suggestions, teacher support cards
- effective weights, propensities, probe flags
- projection reasons or analytic status

## 4. `student_rm` Tables

### `student_rm.sessions`

| Column | Notes |
|---|---|
| `session_id` | UUID |
| `tenant_id` | tenant scope |
| `student_user_id` | learner |
| `exam_id`, `subject_id`, `chapter_id` | curriculum context |
| `concept_entry_id` | starting concept |
| `chapter_analysis_id` | pinned analysis version |
| `status` | `active`, `inactive`, `closed` |
| `last_active_node_id` | resume pointer |
| `started_at`, `last_active_at`, `closed_at` | lifecycle timestamps |

### `student_rm.nodes`

| Column | Notes |
|---|---|
| `node_id` | UUID |
| `tenant_id`, `session_id`, `student_user_id` | scope |
| `node_type` | `ai`, `text`, `image`, `video` |
| `parent_node_id` | nullable parent for AI-path children |
| `creation_source` | initial prompt, phrase, edge_plus, manual, pyq |
| `content_payload` | student-visible content only |
| `position_x`, `position_y` | canvas position |
| `width`, `height` | optional layout metadata |
| `media_id`, `video_link_id`, `pyq_question_id` | nullable references |
| `deleted_at` | nullable student-visible deletion marker |
| `created_at`, `updated_at` | timestamps |

### `student_rm.edges`

| Column | Notes |
|---|---|
| `edge_id` | UUID |
| `tenant_id`, `session_id` | scope |
| `source_node_id`, `target_node_id` | endpoints |
| `edge_type` | `ai_path` or `manual_reference` |
| `creation_label` | student-safe label/trigger text |
| `deleted_at` | nullable |
| `created_at`, `updated_at` | timestamps |

### `student_rm.node_summaries`

| Column | Notes |
|---|---|
| `summary_id` | UUID |
| `tenant_id`, `session_id`, `node_id` | scope |
| `summary_text` | student-safe summary |
| `prompt_version`, `model_id` | generation stamps, not analytic classification |
| `created_at` | timestamp |

### `student_rm.current_offer_sets`

| Column | Notes |
|---|---|
| `offer_set_id` | UUID |
| `tenant_id`, `session_id`, `source_node_id` | scope |
| `launch_method` | `phrase` or `edge_plus` |
| `options_payload` | student-safe option IDs/text only |
| `status` | `active`, `chosen`, `dismissed`, `expired` |
| `expires_at`, `created_at` | timestamps |

### `student_rm.checkpoint_offers`

Optional student-safe table if persisted checkpoint delivery state is required.

| Column | Notes |
|---|---|
| `checkpoint_offer_id` | UUID |
| `tenant_id`, `session_id`, `student_user_id` | scope |
| `prompt_text` | category-neutral text |
| `status` | `available`, `delivered`, `responded`, `snoozed`, `expired` |
| `created_at`, `expires_at` | timestamps |

This table must not store trigger vectors or category names.

### `student_rm.podcasts`

| Column | Notes |
|---|---|
| `podcast_id` | UUID |
| `tenant_id`, `session_id`, `student_user_id` | scope |
| `status` | `script_generating`, `script_ready`, `audio_generating`, `audio_ready`, `failed`, `cancelled` |
| `requested_length` | selected duration preset |
| `script_text` | student-visible script preview |
| `audio_media_id` | Supabase Storage metadata reference |
| `failure_reason` | sanitized message |
| `created_at`, `updated_at` | timestamps |

## 5. `student_rm` Forbidden Columns Checklist

Any column with these terms in `student_rm` requires rejection or architecture review:

| Pattern | Reason |
|---|---|
| `dimension`, `dimensional` | leaks analytic framework |
| `classification`, `classified` | post-hoc analytic artifact |
| `coverage`, `gap` | teacher-support interpretation |
| `score`, `confidence`, `entropy`, `dispersion` | analytic reliability/score vocabulary |
| `vector`, `profile`, `weight` | engagement/analytic model data |
| `propensity`, `probe`, `steer_reason` | offer policy internals |
| `teacher_followup`, `teacher_suggestion` | teacher-only output |

## 6. `analytic_rm` Scope

`analytic_rm` contains rebuildable classification, coverage, topology, checkpoint, and teacher-support projections. It is never the source of truth and is not readable by `/v1/student`.

## 7. `analytic_rm` Tables

| Table | Purpose | Key Fields |
|---|---|---|
| `analytic_rm.question_classifications` | post-hoc selected-question classification | `tenant_id`, `student_user_id`, `session_id`, `chapter_id`, `offer_set_id`, `event_id`, dimension scores, entropy, dispersion, flags, `prompt_version`, `model_id` |
| `analytic_rm.student_engagement_profiles` | cumulative/trajectory profile | `tenant_id`, `student_user_id`, `chapter_id`, cumulative vector, velocity, `projection_version`, freshness fields |
| `analytic_rm.coverage_by_concept` | concept coverage/gap input | `tenant_id`, `student_user_id`, `chapter_id`, `concept_id`, dimension, coverage value, evidence refs |
| `analytic_rm.coverage_by_pair` | concept-pair traversal evidence | `tenant_id`, `student_user_id`, `chapter_id`, source/target concept IDs, traversal status |
| `analytic_rm.dimensional_shift_log` | checkpoint trigger history | `tenant_id`, `student_user_id`, `session_id`, prior/recent summaries, trigger type, policy version |
| `analytic_rm.checkpoint_signals` | checkpoint teacher-support signal | `tenant_id`, `student_user_id`, `chapter_id`, action counts, response-quality signal, projection stamps |
| `analytic_rm.teacher_support_views` | pre-materialized V3 panels | `tenant_id`, `teacher_user_id`, `student_user_id`, `chapter_id`, panel payload, freshness metadata |
| `analytic_rm.class_aggregates` | V4 class/chapter aggregates | `tenant_id`, `class_id`, `chapter_id`, distribution payload, K-suppression metadata |
| `analytic_rm.institution_aggregates` | institution-level rollups | `tenant_id`, grade/subject/chapter keys, aggregate payload, suppression metadata |
| `analytic_rm.realized_subgraph` | realized topology projection | `tenant_id`, `student_user_id`, `chapter_id`, graph payload, projection stamps |
| `analytic_rm.graph_diff` | intended vs realized topology | `tenant_id`, `student_user_id`, `chapter_id`, missing/partial edge payload, projection stamps |

## 8. Analytic Freshness Fields

Projection tables should include:

- `projection_version`
- `generated_at`
- `source_event_recorded_at_max`
- `chapter_analysis_id`
- `policy_version` where policy-driven
- `prompt_version` / `model_id` where model-derived
- `replay_id` when replayed

## 9. Consent and Teacher Access

`analytic_rm` rows are generated only when consent and tenancy rules allow. On withdrawal, teacher panels must hide immediately where possible and projections must be rebuilt or replayed without the withdrawn student according to the operational policy.

Aggregates must apply small-cohort suppression before display.