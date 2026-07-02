# 01 System Map

## High-Level Architecture
The project follows an **event-sourced modular monolith** pattern for the backend and a **hybrid native/Skia rendering** pattern for the mobile app.

### Backend (Python/FastAPI)
- **Pattern**: Modular Monolith with CQRS-style read separation.
- **Composition Root**: `backend/app/main.py` (58 lines — pure composition root: app
  instantiation, CORS/Sentry middleware, router inclusion, and re-exports of `SessionRuntime`
  / `InMemoryMembershipStore` for backward compatibility. No domain logic here.)
- **Major Layers**:
    - `app/domain/`: Pure types and invariants (e.g., `app/domain/student/sessions.py`).
    - `app/api/`: FastAPI routers (e.g., `app/api/student/sessions.py`). Routers access the
      runtime via `request.app.state.session_runtime` (duck-typed; no direct import of
      `SessionRuntime` class to avoid circular dependencies).
    - `app/runtime/`: In-process DI container and orchestration.
        - `session.py` — `SessionRuntime` dataclass: the thin DI facade injected into
          `app.state`. All methods delegate to typed workflow functions; no inline orchestration.
          `for_testing` factory used by all integration tests.
        - `session_workflow.py` — `start_session_workflow`, `resume_student_session_workflow`,
          `get_student_session_with_canvas_workflow`.
        - `curriculum_workflow.py` — `resolve_session_request`, `render_teacher_chapter_graph`.
        - `node_position_workflow.py` — `update_node_position_workflow`.
        - `offer_workflow.py` — phrase/edge offer-set creation, offer-choice recording.
        - `canvas_deletion.py` — `delete_node_cascade_workflow`.
        - `canvas_state.py` — `canvas_snapshot_from_events` (event replay → student-safe snapshot).
    - `app/tenancy/`: Tenant identity and membership resolution.
        - `memberships.py` — `InMemoryMembershipStore`: in-process tenant role registry.
        - `membership_auth.py` — `resolve_membership_auth`: JWT decode + role lookup.
        - `auth.py` — FastAPI dependency `get_auth_context`; calls `runtime.resolve_auth`
          via duck-typing to stay decoupled from `app/runtime/`.
        - `pool.py` — `InMemoryTenantConnectionPool`: transactional session store access.
        - `consent.py` — `InMemoryConsentRecordStore`.
    - `app/events/`: Event store and registry (e.g., `app/events/store.py`).
    - `app/projections/`: Event-to-Read-Model builders.
    - `app/workers/`: Async job handlers (e.g., `app/workers/classify.py`).
    - `app/llm_gateway/`: Central chokepoint for AI calls.

### Mobile (React Native/Expo)
- **Pattern**: Hybrid rendering (React Native Animated Views for nodes + Skia for edges).
- **Entry Point**: `mobile/app/index.ts` -> `mobile/app/App.tsx`
- **State Management**: Zustand (`mobile/canvas/store.ts`).
- **Animation/Gestures**: Reanimated + Gesture Handler (`mobile/canvas/useCanvasGestures.ts`).
- **Physics**: D3-Force for node positioning.

### Data & Infrastructure
- **Database**: Supabase PostgreSQL (Event Store, Jobs, Read Models).
- **Auth**: Supabase Auth (JWT-based).
- **Storage**: Supabase Storage (Media/Podcasts).
- **Job Queue**: Postgres `SELECT ... FOR UPDATE SKIP LOCKED`.

### Runtime Patterns
- **Write Path**: API -> Command -> Event Append -> Sync Projection (Student RM).
- **Read Path**: API -> Read Model (Student RM).
- **Async Path**: Event Append -> Job Enqueue -> Worker Claim -> Async Projection (Analytic RM).
- **Category Invisibility**: Strict physical separation between student and analytic schemas.
