# M4 Supabase migration-source manifest

These SQL files preserve the exact source supplied to Supabase for the closed M4 milestone. They
are not Alembic revisions and their numeric filename prefixes do not extend the Python revision
chain in `backend/migrations/versions/`.

## Ordered histories

The Python/Alembic baseline currently ends at `0006_m3_schema_alignment`.

The separate M4 Supabase source history must be interpreted in this order:

1. `0006_m4_catalog_auth_seed.sql` — applied as `20260702173751 / m4_catalog_auth_seed`.
2. `0007_m4_runtime_remediation.sql` — applied as
   `20260710075416 / m4_runtime_remediation`.

The remediation depends on the catalog/auth seed. It forward-corrects the already-applied catalog
schema; it is not an alternative initial migration.

Do not rename or rewrite either applied SQL artifact. Do not infer that the source-SQL `0006` is
the Alembic successor of `0006_m3_schema_alignment`. Any future schema correction requires a new,
reviewed forward migration after verifying the target Supabase project.
