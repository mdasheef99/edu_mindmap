# Configuration Reference

**Document Version**: 1.0 (draft)  
**Status**: Current MVP configuration baseline  
**Related Documents**: `docs/planning/development-approach.md`, `docs/api/README.md`, `docs/database/README.md`, `docs/mvp-features-specification.md`

---

## 1. Purpose

This document centralizes constants, thresholds, feature flags, and operational defaults that must not be scattered through implementation code. Values are conservative MVP defaults and may be revised through the worklog when implementation or pilot evidence warrants it.

## 2. Scope Rules

- Configuration must preserve Category Invisibility.
- Student-facing config must not expose analytic dimensions, classifier thresholds, or teacher-support logic.
- Secrets are never documented here; only variable names and ownership are listed.
- Redis, Celery, and TimescaleDB are not MVP configuration targets.

## 3. Canvas and Mobile Limits

| Setting | Value | Notes |
|---|---:|---|
| `CANVAS_NODE_WARNING_COUNT` | 50 | show warning as board approaches complexity limit |
| `CANVAS_NODE_HARD_LIMIT` | 65 | prevent unbounded canvas growth |
| `CANVAS_MIN_ZOOM` | 0.25 | 25% |
| `CANVAS_MAX_ZOOM` | 4.0 | 400% |
| `CANVAS_GRID_SIZE_PX` | 15 | snap-to-grid size |
| `CANVAS_PERFORMANCE_GATE_NODES` | 40 | 60fps gate on reference Android device |

## 4. Event and API Limits

| Setting | Value | Notes |
|---|---:|---|
| `EVENT_BATCH_MAX_SIZE` | 100 | upper bound for client event batch ingestion |
| `IDEMPOTENCY_KEY_TTL_HOURS` | 24 | retry safety window |
| `VIEWPORT_EVENT_THROTTLE_MS` | 1000 | required to prevent noisy pan/zoom event volume |
| `NODE_POSITION_PERSIST_MODE` | `drag_end` | persist final drag position; sampled intermediates only if later justified |

## 5. Worker Queue Defaults

| Setting | Value | Notes |
|---|---:|---|
| `JOB_MAX_ATTEMPTS` | 5 | dead-letter after repeated failure |
| `JOB_CLAIM_BATCH_SIZE` | 10 | small MVP batch to keep locks short and behavior easy to inspect |
| `JOB_RETRY_BACKOFF` | `1m,5m,15m,1h,6h` | exponential-ish schedule across 5 attempts |
| `JOB_QUEUE_BACKEND` | `postgres_skip_locked` | Redis/Celery deferred |

## 6. Teacher and Privacy Thresholds

| Setting | Value | Notes |
|---|---:|---|
| `SMALL_COHORT_SUPPRESSION_K` | 5 | suppress aggregate cells below K |
| `PROJECTION_STALENESS_WARNING_MINUTES` | 15 | teacher responses include freshness metadata |
| `CHECKPOINT_OPT_OUT_VISIBILITY_THRESHOLD` | 3 | repeated opt-out patterns require at least 3 relevant events |

## 7. Checkpoint Policy Defaults

| Setting | Value | Notes |
|---|---:|---|
| `CHECKPOINT_COSINE_DISTANCE_THRESHOLD` | 0.35 | current MVP planning value for meaningful shift |
| `CHECKPOINT_MIN_PRIOR_CONTEXT_EVENTS` | 5 | minimum classified learner choices before offering checkpoint |
| `CHECKPOINT_COOLDOWN_MINUTES` | 15 | prevent repeated interruption |
| `CHECKPOINT_DELIVERY_MODE` | `poll_only` | `GET /v1/student/sessions/{session_id}/checkpoint` |

## 8. Podcast Defaults

| Setting | Value | Notes |
|---|---:|---|
| `PODCAST_LIFECYCLE` | `script_then_audio` | `script_ready` requires user confirmation before audio |
| `PODCAST_LENGTH_PRESETS` | `3m,5m,8m` | short MVP lengths for cost and UX control |
| `PODCAST_AUDIO_URL_TTL_MINUTES` | 60 | signed URL/access window default |
| `PODCAST_RETRY_POLICY` | worker default | uses `JOB_MAX_ATTEMPTS` unless overridden |

## 9. LLM Gateway Defaults

| Setting | Value | Notes |
|---|---|---|
| `LLM_PROVIDER` | configurable provider key | backend-only provider access; no mobile-side credentials |
| `LLM_STAGE1_MODEL_ID` | Stage 1 Generation Model id | environment-specific model id used for organic generation |
| `LLM_STAGE2_MODEL_ID` | Stage 2 Classification Model id | environment-specific model id used for post-hoc classification |
| `LLM_CI_MODE` | recorded fixtures | no live LLM calls in CI |
| `LLM_DAILY_TENANT_BUDGET_USD` | 10 | conservative pilot tenant guard; raise only with worklog entry |
| `LLM_DAILY_GLOBAL_BUDGET_USD` | 50 | conservative global MVP guard; raise only with worklog entry |

## 10. Environment Variable Names

Values are not documented here.

| Variable | Owner | Purpose |
|---|---|---|
| `DATABASE_URL` | backend/worker | Postgres connection |
| `TEST_DATABASE_URL` | tests only | opt-in live Postgres / pooled-RLS verification connection |
| `SUPABASE_URL` | backend/mobile/web | Supabase project URL |
| `SUPABASE_ANON_KEY` | mobile/web | client-safe Supabase key |
| `EXPO_PUBLIC_SUPABASE_URL` | mobile | Expo-exposed Supabase project URL for B2C email/password auth |
| `EXPO_PUBLIC_SUPABASE_ANON_KEY` | mobile | Expo-exposed client-safe Supabase anon key |
| `EXPO_PUBLIC_API_BASE_URL` | mobile | backend API base URL used by the M4 Expo app |
| `EXPO_PUBLIC_SHOW_CANVAS` | mobile local/dev | optional M3 canvas smoke override |
| `EXPO_PUBLIC_SHOW_M2_SMOKE` | mobile local/dev | optional M2 phrase smoke override |
| `EXPO_PUBLIC_DEV_API_BASE_URL` | mobile dev only | explicit backend URL for the development Canvas path |
| `EXPO_PUBLIC_DEV_SESSION_ID` | mobile dev only | explicit seeded development session |
| `EXPO_PUBLIC_DEV_AUTH_TOKEN` | mobile dev only | explicit disposable development bearer token |
| `M4_INDIVIDUAL_TENANT_ID` | backend | required configured B2C individual tenant; production startup fails if absent or malformed |
| `CORS_ALLOWED_ORIGINS` | backend | comma-separated browser origins; empty disables browser cross-origin access |
| `SUPABASE_SERVICE_ROLE_KEY` | backend only | privileged server operations |
| `LLM_PROVIDER_API_KEY` | backend only | LLM Gateway provider credential |
| `SENTRY_DSN_BACKEND` | backend | error tracking |
| `EXPO_PUBLIC_SENTRY_DSN_MOBILE` | mobile | Expo-exposed mobile error-tracking DSN |
| `SENTRY_DSN_WEB` | teacher web | error tracking |

Expo-exposed variables are bundled into client builds. Do not put `DATABASE_URL`,
`TEST_DATABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, or `SUPABASE_JWT_SECRET` into any
`EXPO_PUBLIC_*` variable. M4 client auth uses only the Supabase project URL and anon key. Backend
token verification follows ADR-0017: ES256/JWKS for the live Supabase runtime. Production
configuration never reads `SUPABASE_JWT_SECRET`; deterministic tests inject an HS256 fixture
verifier explicitly. Live
ES256 verification applies a fixed 30-second clock-skew tolerance while continuing to validate
the signature, issuer, audience, issued-at, not-before, and expiry claims.

### 10.1 Phase 2 placeholders — Supabase Auth + curriculum ingestion

Names only; values are never documented here. Auth rows back `backend-architecture.md` §5.4 (JWT →
backend-resolved tenant/role) and ADR-0015 (`adr-log-02.md`); ingestion rows back
`chapter-analysis-pipeline-specification.md` P0–P4 and
`docs/planning/sdd/phase-2-curriculum-ingestion-sdd.md` §3, §6. ADR-0017 supersedes ADR-0015 for
the live runtime and selects asymmetric ES256/JWKS validation.

| Variable | Owner | Purpose |
|---|---|---|
| `SUPABASE_JWT_SECRET` | test harness only | optional fixture input passed explicitly to tests; ignored by production configuration |
| `SUPABASE_JWT_JWKS_URL` | backend only | optional explicit JWKS endpoint for ADR-0017 ES256 verification; otherwise derived from `SUPABASE_URL` |
| `SUPABASE_AUTH_URL` | backend/mobile/web | Supabase Auth issuer/base URL |
| `TEST_DATABASE_URL` | tests/CI/local | non-bypass app-role Postgres URL for opt-in live RLS and curriculum ingest tests; local pytest loads this key from `.env` if it is not exported |
| `CURRICULUM_SOURCE_DIR` | ingestion operator | path to source chapter PDF/text inputs for P0 |
| `CHAPTER_ANALYSIS_FIXTURE_DIR` | tests/CI | recorded P1–P4 LLM fixtures keyed by `prompt_version` (CI never calls live LLM) |
| `CHAPTER_ANALYSIS_OUTPUT_DIR` | ingestion operator | versioned P0–P4 JSON artifacts before/with DB persistence |

Live Phase 2 curriculum ingest tests also require the target `TEST_DATABASE_URL` database to have the
Phase 2 curriculum migrations applied (`backend/migrations/versions/0004_curriculum_schema.py` and
`backend/migrations/versions/0005_curriculum_privileges_and_indexes.py`). Tests must skip rather than
fall back to `DATABASE_URL` when `TEST_DATABASE_URL` is absent, points at a bypass-RLS role, or lacks the
required schema/access grants.

## 11. Change Control

Any config change affecting teacher interpretation, checkpoint triggering, classification, consent, or Category Invisibility requires a worklog entry and, where persistent outputs change, a projection/replay plan.
