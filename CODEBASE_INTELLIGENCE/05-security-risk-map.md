# 05 Security & Operational Risk Map

## Security Boundaries
- **Category Invisibility**:
    - **Rule**: Student API (`/v1/student`) MUST NOT read from `analytic_rm` or expose dimensional/classification fields.
    - **Enforcement**: `import-linter` (see `pyproject.toml`) and physical schema separation.
- **Tenant Isolation**:
    - **Rule**: Every data request must be filtered by `tenant_id` resolved from the actor's JWT.
    - **Enforcement**: Server-side resolution in `backend/app/tenancy/auth.py` and Postgres RLS.

## Authorization
- **Roles**: `student`, `teacher`, `approved_teacher`, `admin`.
- **Boundaries**: Teachers cannot see other classes; Students cannot see other students' analytic profiles.

## Secret Handling
- **No Mobile Secrets**: AI/TTS provider keys must stay on the backend.
- **JWT Secrets**: Must be rotated and managed via environment variables (e.g., `JWT_SECRET`).

## PII & Privacy
- **Student Data**: Names and emails are stored in Supabase Auth/Tenancy tables.
- **Anonymization**: Analytic exports should use anonymized IDs where possible.

## Risky Patterns (Forbidden)
- **Direct Event Update**: Never `UPDATE` the `events` table. Append only.
- **Mobile Auth Token Logging**: Never log the `Authorization` header or tokens.
- **Hardcoded IPs**: `DEV_API_BASE_URL` in `App.tsx` must be updated for your LAN IP but never committed as a production value.

## Operational Risks
- **Durable Snapshot Reconstruction**: If the event log grows too large, `canvas_snapshot_from_events` may become slow. Snapshotting (checkpointing) read models is the planned mitigation.
- **Job Queue Dead-letter**: Jobs failing more than 5 times (`JOB_MAX_ATTEMPTS`) move to a dead-letter state. Monitor `jobs` table for `status = 'dead'`.
