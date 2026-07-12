# 03 Backend & Data Map

## API Integration
- **Framework**: FastAPI.
- **Client**: Mobile uses `fetch` via `mobile/canvas/apiClient.ts` and `mobile/canvas/useSessionHydration.ts`.
- **Base URL**: Environment-dependent (LAN IP for dev, Render URL for production).

## Database Access (PostgreSQL)
- **Platform**: Supabase.
- **Invariants**:
    - Every row must have `tenant_id`.
    - `events` table is append-only (no `UPDATE`/`DELETE`).
- **Read Models**:
    - `student_rm`: Student-safe data (nodes, edges, sessions).
    - `analytic_rm`: Teacher/Admin data (vectors, classifications, PII-sensitive).

## Auth & Session Handling
- **Identity**: Supabase Auth (JWT).
- **Resolution**: `backend/app/tenancy/auth.py` resolves `user_id` -> `tenant_id` and `role`.
- **JWT Secret**: Managed via environment variables.

## Job Queue
- **Pattern**: Postgres `SKIP LOCKED` (`backend/app/workers/`).
- **Jobs**:
    - `classify`: Post-hoc AI classification of student responses.
    - `project`: Rebuilding read models from event stream.
    - `chapter_analysis`: Pipeline for processing curriculum content.

## AI & LLM Gateway
- **Module**: `backend/app/llm_gateway/`.
- **Chokepoint**: Single point of entry for all Anthropic/OpenAI calls.
- **Accounting**: `InMemoryLLMUsageStore` (and Postgres equivalent) tracks costs.

## Storage
- **Platform**: Supabase Storage.
- **Usage**: Podcast audio files, student-uploaded media.

## Stale/Uncertain Areas
- **Live Auth**: Migration to real Supabase Auth is planned but may need verification of JWT hook behavior in production.
- **Mocks**: `InMemoryEventStore` and `InMemoryStudentSessionProjectionStore` are heavily used in tests but must be mirrored by real Postgres implementations.
