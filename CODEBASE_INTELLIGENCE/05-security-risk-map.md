# 05 Security and Operational Risk Map

**2026-07-11 update**: Supabase ES256/JWKS verification now reuses a cached JWKS client; bootstrap
reports persisted consent state; sign-out calls Supabase remote logout before local clearing.

**Snapshot**: 2026-07-10. Security authority is the canon plus
`docs/architecture/backend-architecture.md` §§5-8 and ADR-0003/0007/0010/0014/0017.

## Merge-Blocking Boundaries

### Category Invisibility

- `/v1/student` may read student-safe operational data and `student_rm`; it must never import/read
  `analytic_rm` or expose dimensions, classification, coverage, gap, score, confidence, entropy,
  vectors, profiles, propensities, probes, or teacher fields.
- `pyproject.toml` defines four import-linter contracts covering student API, generation, and
  chapter-analysis seams. Physical schema separation is the second control.
- There is no student raw-event endpoint.

### Tenant Isolation

- Supabase JWT establishes user identity; the backend membership store resolves `tenant_id` and
  role. Mobile-supplied tenant or role values are never authoritative.
- Pooled Postgres operations must run inside a transaction with
  `SET LOCAL app.tenant_id`; RLS is the database-level backstop.
- Migration `0007_m4_runtime_remediation.sql` adds/backfills tenant keys and replaces permissive
  M4 catalog read policies with tenant-isolation policies.
- Remaining risk: the final cross-tenant smoke must use a non-bypass app role. Schema/RLS metadata
  being present is necessary but does not prove policy behavior through a bypass-RLS credential.

### Event Sourcing and Organic-First

- Never update or delete `events`; all client events pass the in-code type/version registry.
- Worker-only events such as `question_classified` are rejected from clients.
- Only a selected offer-set choice enqueues classification. Dismissal does not, and student
  responses never wait on the worker.
- Analytic projection requires active behavioral-analytics consent.

## Auth, Secrets, and Privacy

- Live Supabase tokens use ES256/JWKS via `SUPABASE_URL` or `SUPABASE_JWT_JWKS_URL`. The backend
  caches the JWKS client/key path across authenticated requests. HS256 is available only through
  an explicitly injected deterministic test-fixture verifier.
- Never log bearer/refresh tokens, database URLs, service-role keys, or provider credentials.
- Mobile may contain only Expo-public Supabase URL/anon key, backend base URL, and a public Sentry
  DSN. AI/TTS keys, `DATABASE_URL`, service-role keys, and JWT fixture secrets are backend-only.
- Identity PII belongs in Supabase Auth/tenancy tables, not event payloads or analytic exports.
- The M4 session-start consent input is only an acknowledgement; backend identity/tenant/grantor
  fields are resolved server-side.
- Bootstrap reports whether an active behavioral-analytics consent grant already exists so the
  client can avoid repeatedly asking for the same acknowledgement.

## Operational Risks

- `canvas_snapshot_from_events` replays the session log. Monitor latency and add versioned snapshots
  only when the source hierarchy schedules that optimization.
- Monitor `jobs.status = 'dead'`; `JOB_MAX_ATTEMPTS=5` is merge-blocking.
- Changing projection logic requires projection-version/replay consideration.
- Production configuration fails closed. Never restore an in-memory fallback to normal
  `create_app()` startup.
- The normal M4 path must not hardcode a LAN IP. Supply `EXPO_PUBLIC_API_BASE_URL` to the Expo
  process/build; closed milestone smoke fixtures should not be copied into production paths.
- Sign-out should call Supabase remote logout before local session clearing; local clearing remains
  the fallback if the logout request fails.
