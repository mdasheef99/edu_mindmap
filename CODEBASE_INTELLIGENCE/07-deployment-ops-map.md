# 07 Deployment & Ops Map

## Hosting
- **Backend + Worker**: Render (`render.yaml`).
- **Mobile**: Expo Application Services (EAS) or standard native builds.
- **Database**: Supabase (PostgreSQL).

## Environment Variables
- `DATABASE_URL`: Postgres connection string.
- `JWT_SECRET`: For auth token signing/verification.
- `LLM_API_KEY`: Anthropic/OpenAI key for LLM Gateway.
- `SENTRY_DSN`: Error tracking.
- `RENDER_EXTERNAL_URL`: Public backend URL.

## CI/CD
- **Pipeline**: GitHub Actions (assumed).
- **Checks**:
    - Backend Pytest + Coverage.
    - Mobile Jest.
    - Import Linter (Boundary enforcement).
    - MyPy / TypeScript type checks.

## Monitoring & Observability
- **Sentry**: Crash reporting and error tracking (`backend/app/observability/sentry.py`).
- **Postgres Logs**: For slow queries or `SKIP LOCKED` deadlocks.
- **LLM Usage**: Tracked via `InMemoryLLMUsageStore` (or DB equivalent) to monitor costs.

## Operational Caveats
- **Tenant Isolation**: Connection pool must be handled carefully to avoid leaking `SET LOCAL app.tenant_id` across requests (see ADR-0010/Canon).
- **Worker Scaling**: The current `SKIP LOCKED` queue is designed for the MVP modular monolith. Scaling to multiple worker instances is supported by the Postgres lock mechanism.
- **Stale Snapshots**: Ensure that `projection_version` is incremented when snapshot logic changes, triggering a rebuild.
