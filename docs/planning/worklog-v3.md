# Worklog v3 — Phase 2 Curriculum Ingestion

Continuation of `docs/planning/worklog-v2.md` after rotation at the Phase 2 line cap.

---

### 2026-06-18 — Phase 2 sprint 1: curriculum Postgres persistence adapter slice green

**Phase / milestone**: Phase 2 — Curriculum Ingestion (priority 3 persistence slice)

**Spec sections used**:
- `docs/planning/sdd/phase-2-curriculum-ingestion-sdd.md` §6, §8–§10 (curriculum schema,
  L2 persistence determinism/idempotency, row stamps, DoD)
- `docs/architecture/backend-architecture.md` §5.3 (tenant-scoped RLS), §7.5 (`curriculum`
  content schema), §10 (version stamping)
- `docs/planning/development-approach.md` §6 and §8 (red-test-first, small reviewable slices)

**Work completed**:
- Added red adapter contract tests in `tests/database/test_curriculum_postgres_adapter.py`:
  - `test_postgres_curriculum_store_upserts_all_tables_under_tenant_context`,
  - `test_postgres_curriculum_store_finds_chapter_for_launch_under_tenant_context`.
- Implemented `backend/app/projections/curriculum_postgres.py`:
  - `PostgresCurriculumStore.ingest()` upserts `curriculum.chapters`, `segments`, `concepts`,
    and `concept_edges`,
  - uses one transaction per ingest and sets transaction-local `app.tenant_id`,
  - JSON-serializes JSONB fields before writing,
  - supports `find_chapter()` for tenant-scoped session launch lookup.
- Re-exported `PostgresCurriculumStore` from `backend/app/projections/curriculum.py` while keeping
  implementation in a separate module to keep source files under the size guideline.
- Cleaned generated `.pyc` files after validation; final `.pyc` count is 0.

**Validation run**:
- Red baseline observed first: new adapter tests failed on missing `PostgresCurriculumStore`.
- `python -m pytest tests/database/test_curriculum_postgres_adapter.py -q` → 2 passed.
- `python -m ruff format --check backend tests` → passed.
- `python -m ruff check backend tests` → passed.
- `python -m mypy backend/app` → passed.
- `python -m pytest tests -q` → 55 passed, 2 skipped.

**Gate status**:
- Priority 3 remains **IN PROGRESS**.
- The code now has a Postgres adapter contract for `curriculum`, but the live DB/Supabase path still
  needs an opt-in integration proof with `TEST_DATABASE_URL` or equivalent non-bypass app role.
- Remaining Phase 2 work estimate:
  - Priority 3: ~3 slices left — real PDF-backed P0 extraction (`pypdf` approval required),
    P1/P2/P4 fixture-backed LLM contracts through `llm_gateway`, and one real NCERT chapter
    end-to-end ingest into Postgres/Supabase.
  - Priority 5: ~2 slices — Teacher V1 auth/read endpoint and payload/forbidden-field tests.
  - Priority 1/6 deferred ops: ~2 verification slices — Render backend+worker verification and
    physical-device Expo smoke or explicit re-deferral.
- Roughly, Phase 2 is around halfway done by proof items, but the remaining work includes the
  highest-integration pieces: real document parsing, fixture-backed LLM contracts, live persistence,
  teacher render, and deployment/device verification.

---

### 2026-06-18 — Phase 2 new-session handoff prepared

**Decision**: start the remaining Phase 2 work in a new session.

**Why**:
- The remaining work has the highest integration risk: real PDF parsing, fixture-backed LLM contracts,
  live Postgres/Supabase persistence/RLS, Teacher V1 auth/read surface, and deployment/device smoke.
- A new session should reduce context drift and force a fresh read of the active SDD + worklog before
  any edits.

**New-session first action**:
- Read `.augment/rules/00-canon.md`, `docs/planning/development-approach.md`,
  `docs/architecture/backend-architecture.md`, `docs/planning/sdd/phase-2-curriculum-ingestion-sdd.md`,
  and this `docs/planning/worklog-v3.md` before proposing or editing.
- State back that Phase 2 is active and that priority 3 is partly green but still open.
- Do not reopen Phase 1 and do not design Phase 3+ features.

**Recommended next slice**:
- Start with real PDF-backed P0 extraction because it is the next priority-3 integration risk and is a
  prerequisite for a real NCERT chapter ingest.
- Ask for explicit approval before installing or adding `pypdf`.
- Follow red→green: write failing tests for PDF bytes/text extraction into deterministic P0 segments,
  then implement the smallest parser wrapper in `backend/app/chapter_analysis/`.

**Current validation baseline before handoff**:
- `python -m ruff format --check backend tests` → passed.
- `python -m ruff check backend tests` → passed.
- `python -m mypy backend/app` → passed.
- `python -m pytest tests -q` → 55 passed, 2 skipped.
- Generated `.pyc` count after cleanup → 0.

---

### 2026-06-18 — Phase 2 sprint 1: real PDF-backed P0 extraction slice green

**Phase / milestone**: Phase 2 — Curriculum Ingestion (priority 3 PDF-backed P0 slice)

**Spec sections used**:
- `docs/planning/sdd/phase-2-curriculum-ingestion-sdd.md` §8–§10 (L1/L2 pipeline proof,
  deterministic/idempotent ingestion behavior, DoD)
- `docs/chapter-analysis-pipeline-specification.md` P0 (extract text per page using `pypdf`,
  deterministic segment IDs, required segment index fields)
- `docs/planning/development-approach.md` §7.7 (`pypdf`, not deprecated `PyPDF2`)
- `docs/architecture/backend-architecture.md` §7.5 and §10 (curriculum content/versioned rows)

**Work completed**:
- Added red PDF-backed P0 tests in `tests/chapter_analysis/test_pipeline.py` for:
  - deterministic PDF page extraction from the same bytes,
  - deterministic segment IDs from the same PDF bytes,
  - required PDF-backed segment index fields.
- Added `pypdf` to `requirements.txt` and installed with `python -m pip install -r requirements.txt`.
- Implemented the smallest wrapper in `backend/app/chapter_analysis/segments.py`:
  - `extract_pdf_pages(pdf_bytes)` reads source PDF bytes with `pypdf.PdfReader`,
  - `segment_chapter_pdf_bytes(chapter_id, pdf_bytes)` feeds extracted page text into the existing
    deterministic `segment_chapter_text()` implementation.
- Replaced the `PyPDF2` seed-script dependency direction with the governed `pypdf` package in runtime
  code while keeping the implementation inside `app.chapter_analysis`.
- Cleaned generated `.pyc` files after validation; final `.pyc` count is 0.

**Validation run**:
- Red baseline observed first: new PDF tests failed on missing `extract_pdf_pages` and
  `segment_chapter_pdf_bytes`.
- `python -m pytest tests/chapter_analysis/test_pipeline.py -q` → 8 passed.
- `python -m ruff format --check backend tests` → passed.
- `python -m ruff check backend tests` → passed.
- `python -m mypy backend/app` → passed.
- `python -m pytest tests -q` → 58 passed, 2 skipped.
- Generated `.pyc` count after cleanup → 0.

**Gate status**:
- Priority 3 remains **IN PROGRESS**, but the real PDF-backed P0 extraction risk is now green.
- Remaining Priority 3 slices are now primarily:
  - P1/P2/P4 fixture-backed LLM contracts through `llm_gateway`,
  - one real NCERT chapter end-to-end ingest into Postgres/Supabase with the non-bypass app role.

---

### 2026-06-18 — Phase 2 stabilization before LLM integration

**Phase / milestone**: Phase 2 — Curriculum Ingestion (priority 3 baseline stabilization)

**Spec sections used**:
- `docs/planning/sdd/phase-2-curriculum-ingestion-sdd.md` §8–§10 (P0–P4 proof, deterministic
  segment IDs, DoD)
- `docs/chapter-analysis-pipeline-specification.md` P0 and P3 (segment index contract and merge/dedup)
- `docs/planning/development-approach.md` §3.1 and §7.7 (Electricity asset and `pypdf` direction)

**Work completed**:
- Renamed `docs/research/electiricity.pdf` to `docs/research/electricity.pdf` and updated source/test/doc
  references.
- Updated `extract_pdf.py` to use `pypdf.PdfReader` and the corrected PDF path.
- Ensured `backend/app/chapter_analysis/segments.py` starts with the exact module docstring
  `"""Deterministic P0 segmentation helpers."""`.
- Confirmed `backend/app/domain/student/sessions.py` already carries the requested student-safe session
  module docstring.
- Tightened PDF-backed P0 tests so `char_span` is consistently asserted as a tuple of two integers.
- Fixed P3 label normalization so non-plural trailing-`s` labels such as `process` are not normalized to
  false stems such as `proce`; added a regression test.
- Added a curriculum ingest test asserting every segment ID follows `[chapter_id]_[segment_type]_[NNN]`.
- Verified the renamed Electricity PDF appears to be the full NCERT chapter candidate: 24 pages, ~45k
  extracted characters, includes `What you have learnt`, `EXERCISES`, and end-of-chapter questions.
- Cleaned generated `.pyc` files after validation; final `.pyc` count is 0.

**Validation run**:
- `python -m pytest tests/chapter_analysis/test_pipeline.py tests/projections/test_curriculum_ingest.py -q`
  → 13 passed.
- `python -m ruff format --check backend tests extract_pdf.py` → passed.
- `python -m ruff check backend tests extract_pdf.py` → passed.
- `python -m mypy backend/app` → passed.
- `python -m pytest tests -q` → 60 passed, 2 skipped.
- Generated `.pyc` count after cleanup → 0.

**Gate status**:
- Priority 3 remains **IN PROGRESS**.
- Baseline is stable for the next red-to-green slice: P1/P2/P4 fixture-backed LLM contracts through
  `llm_gateway`.

---

### 2026-06-18 — Phase 2 sprint 1: P1/P2/P4 fixture-backed LLM contracts green

**Phase / milestone**: Phase 2 — Curriculum Ingestion (priority 3 fixture-backed LLM slice)

**Spec sections used**:
- `docs/planning/sdd/phase-2-curriculum-ingestion-sdd.md` §5 and §8 (chapter_analysis may call models
  only through `llm_gateway`; L5 recorded fixtures in CI)
- `docs/chapter-analysis-pipeline-specification.md` P1, P2, P4 (named concepts, embedded concepts,
  typed relationship graph contracts)
- `docs/configuration-reference.md` §9–§10 (`LLM_CI_MODE` recorded fixtures,
  `CHAPTER_ANALYSIS_FIXTURE_DIR` intent)
- `docs/architecture/backend-architecture.md` §4.4 and §9 (single model-call gateway boundary)

**Work completed**:
- Added red fixture-backed contract test `tests/chapter_analysis/test_llm_fixture_contracts.py` proving
  P1/P2/P4 calls:
  - go through `app.chapter_analysis.passes` and `app.llm_gateway`,
  - return schema-shaped concept/edge envelopes with prompt/model stamps,
  - cite only known P0 segment IDs,
  - record one `analysis` usage record per pass with `fixture=True`.
- Implemented `backend/app/chapter_analysis/passes.py` as the chapter-analysis pass wrapper surface.
- Implemented `backend/app/llm_gateway/chapter_analysis_fixture.py` with recorded fixture envelopes for:
  - `chapter-analysis-p1-fixture-v1`,
  - `chapter-analysis-p2-fixture-v1`,
  - `chapter-analysis-p4-fixture-v1`.
- Added opt-in real chapter integration test `tests/integration/test_real_chapter_ingest.py` that, when
  `TEST_DATABASE_URL` is set to a non-bypass app role, runs real `docs/research/electricity.pdf` through
  P0 + P1/P2/P4 fixtures, builds curriculum rows, ingests through `PostgresCurriculumStore`, and rolls
  the transaction back.
- Initial DB prerequisite check looked only at process environment: `TEST_DATABASE_URL` was present in
  `.env` but was not loaded into pytest; `DATABASE_URL` was present in the process and bypassed RLS, so
  it was not used for the required non-bypass ingest proof.
- Cleaned generated `.pyc` files after validation; final `.pyc` count is 0.

**Validation run**:
- Red baseline observed first: new fixture contract failed on missing `app.chapter_analysis.passes`.
- `python -m pytest tests/chapter_analysis/test_llm_fixture_contracts.py -q` → 1 passed.
- `python -m pytest tests/integration/test_real_chapter_ingest.py -q` → 1 skipped
  (`TEST_DATABASE_URL` not set).
- `python -m ruff format --check backend tests extract_pdf.py` → passed.
- `python -m ruff check backend tests extract_pdf.py` → passed.
- `python -m mypy backend/app` → passed.
- `python -m pytest tests -q` → 61 passed, 3 skipped.
- Generated `.pyc` count after cleanup → 0.

**Gate status**:
- Priority 3 remains **IN PROGRESS**.
- P1/P2/P4 fixture-backed contracts are green.
- Live NCERT ingest into Postgres/Supabase is blocked until the `TEST_DATABASE_URL` target DB has the
  Phase 2 curriculum schema migration applied; the existing optional live RLS/SKIP LOCKED tests pass
  once pytest loads `TEST_DATABASE_URL` from `.env`.

---

### 2026-06-18 — Phase 2 env loading clarification for live DB tests

**Phase / milestone**: Phase 2 — Curriculum Ingestion (priority 3 live DB readiness)

**Spec sections used**:
- `docs/planning/sdd/phase-2-curriculum-ingestion-sdd.md` §8–§10 (live persistence proof, DoD)
- `docs/architecture/backend-architecture.md` §5.3 and §7.5 (tenant RLS and curriculum schema)
- `docs/configuration-reference.md` §10 (`TEST_DATABASE_URL` ownership and local loading behavior)

**Work completed**:
- Added `tests/conftest.py` to load only `TEST_DATABASE_URL` from local `.env` when it is not already
  exported, without printing secret values.
- Confirmed `.env` contains `TEST_DATABASE_URL`, while the previous Python process environment did not.
- Re-ran opt-in live DB tests through the loaded `TEST_DATABASE_URL`:
  - existing real RLS isolation test passed,
  - existing real SKIP LOCKED test passed,
  - new real Electricity ingest test reached the DB but skipped because `curriculum.chapters` is absent.
- Updated the new real ingest test to skip with a precise migration-0004 reason when the target database
  has not applied the Phase 2 curriculum schema.

**Validation run**:
- `python -m pytest tests/database/test_optional_postgres_rls_contract.py tests/integration/test_real_chapter_ingest.py -q`
  → 2 passed, 1 skipped.

**Gate status**:
- Priority 3 remains **IN PROGRESS**.
- The env-loading confusion is resolved. The remaining blocker is applying migration
  `0004_curriculum_schema` to the non-bypass `TEST_DATABASE_URL` target before running the real chapter
  ingest proof end-to-end.

---

### 2026-06-18 — Phase 2 live curriculum ingest proof green via Supabase MCP

**Phase / milestone**: Phase 2 — Curriculum Ingestion (priority 3 live persistence proof)

**Spec sections used**:
- `docs/planning/sdd/phase-2-curriculum-ingestion-sdd.md` §8–§10 (live persistence proof, deterministic
  ingest, DoD)
- `docs/architecture/backend-architecture.md` §5.3 and §7.5 (tenant RLS and curriculum schema)
- `docs/chapter-analysis-pipeline-specification.md` P0–P4 (real PDF extraction, fixture-backed concept
  and edge outputs)
- `docs/configuration-reference.md` §10 (`TEST_DATABASE_URL` and Phase 2 curriculum migrations)

**Work completed**:
- Restored local `backend/migrations/versions/0004_curriculum_schema.py` after detecting it was
  accidentally truncated on disk.
- Applied `0004_curriculum_schema` through Supabase MCP to the connected project.
- Supabase performance advisor then flagged unindexed foreign keys on `curriculum.*`; added and applied
  `0005_curriculum_privileges_and_indexes` through Supabase MCP to:
  - grant the non-bypass app/test role `phase1_rls_tester` schema/table access for `curriculum`,
  - add covering indexes for the new curriculum foreign keys.
- Fixed live-ingest row shape by ensuring curriculum segment rows always include nullable `location` for
  the Postgres adapter.
- Added static migration coverage for `0005` grants and indexes and projection coverage for nullable
  segment `location`.
- Verified the real Electricity chapter ingest proof now runs end-to-end through `TEST_DATABASE_URL`:
  real PDF P0 extraction, P1/P2/P4 recorded fixtures, curriculum row building, tenant-scoped Postgres
  upsert, lookup, and rollback cleanup.

**Validation run**:
- `python -m pytest tests/projections/test_curriculum_ingest.py -q` → 5 passed.
- `python -m pytest tests/integration/test_real_chapter_ingest.py -q` → 1 passed.
- `python -m pytest tests/database/test_curriculum_schema_migration.py tests/integration/test_real_chapter_ingest.py -q`
  → 4 passed.
- `python -m pytest tests -q` → 66 passed.
- Supabase security advisor → no lints.
- Supabase performance advisor → unindexed curriculum FK findings resolved; remaining INFO items are
  unused-index notices in an empty/low-traffic database. Remediation reference:
  https://supabase.com/docs/guides/database/database-linter?lint=0005_unused_index

**Gate status**:
- Priority 3 live NCERT curriculum ingest proof is now **GREEN** for the current fixture-backed P0–P4
  path.
- Priority 3 can move from integration-risk proof toward hardening/fixture quality review, unless a
  stricter real LLM-output artifact review is opened as the next Phase 2 slice.

---

### 2026-06-18 — Phase 2 fixture-quality audit and status sync

**Phase / milestone**: Phase 2 — Curriculum Ingestion (post-priority-3 hardening review)

**Spec sections used**:
- `docs/planning/sdd/phase-2-curriculum-ingestion-sdd.md` §1.2, §3.1, §8, §10 (current checkpoint,
  implementation priority, L5 contract shape, DoD)
- `docs/chapter-analysis-pipeline-specification.md` P1, P2, P4, §5 (pass contracts + verification
  gate)
- `docs/planning/testing-strategy.md` §2, §3.1, §4 (fixture-backed contract testing expectations)
- `docs/architecture/backend-architecture.md` §4.4, §5.3, §7.5, §9 (gateway boundary, RLS,
  curriculum schema, version stamping)

**Work completed**:
- Audited the recorded `chapter_analysis` P1/P2/P4 fixtures against the active pipeline spec.
- Hardened the fixture module so the recorded envelopes now self-check key contract guarantees before
  returning:
  - P1 concepts must carry exactly one definitional citation and bounded explanatory/application refs,
  - P2 concepts must not duplicate normalized labels already supplied by P1,
  - P4 edges must reference known merged concept ids, use allowed edge enums, and carry 1–2 support
    segment ids with a non-empty rationale.
- Updated the active Phase 2 SDD status sections so they no longer say PDF-backed P0, P1/P2/P4
  fixture-backed extraction, and live Supabase ingest are still pending.
- Reconfirmed the migration plan/status by inspection:
  - `0004_curriculum_schema` owns the schema/RLS tables required by the plan,
  - `0005_curriculum_privileges_and_indexes` is the follow-up remediation needed for non-bypass
    app-role access and advisor/index hygiene on the live database.
- Reviewed repository hygiene without rerunning tests: `.pyc` file count remains 0.

**Review findings / remaining gap**:
- The current recorded fixtures are still intentionally **minimal contract fixtures**, not a full
  canonical exported chapter-analysis artifact set.
- This is acceptable for the current L5 CI contract (schema + gateway + citation/use-stamp checks),
  but a later hardening slice may still externalize them into prompt-versioned repo assets if stricter
  fixture-asset parity is required.

**Validation note**:
- Per explicit user instruction in the current session, no tests were re-run in this audit slice.
- Static review only: migrations, fixture code, and active docs were inspected and synchronized.

**Gate status**:
- Priority 3 remains **GREEN** for the fixture-backed curriculum-ingestion spine.
- Phase 2 as a whole remains **IN PROGRESS** because the SDD DoD still requires:
  - Teacher Dashboard V1 render endpoint + no-per-student-field proof,
  - Render backend/worker live verification,
  - physical-device Expo smoke or explicit re-deferral.
