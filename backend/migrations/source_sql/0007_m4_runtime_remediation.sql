-- M4 forward-only catalog tenancy/index remediation.
-- Traceability: phase-3-m4-runtime-closure-remediation-sdd.md R5 / DB-1..DB-2;
-- backend-architecture.md §5.3; development-approach.md §6.6.
-- Applied migration 20260702173751 is intentionally not rewritten.

BEGIN;

ALTER TABLE public.curriculum_classes
    ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE public.exams
    ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE public.subjects
    ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE public.chapter_analysis_versions
    ADD COLUMN IF NOT EXISTS tenant_id UUID,
    ADD COLUMN IF NOT EXISTS chapter_id UUID;
ALTER TABLE public.concept_entries
    ADD COLUMN IF NOT EXISTS tenant_id UUID;

-- Existing M4 rows are owned by the accepted shared individual tenant (ADR-0007).
UPDATE public.curriculum_classes
SET tenant_id = '00000000-0000-4000-8000-000000000010'
WHERE tenant_id IS NULL;

UPDATE public.exams e
SET tenant_id = cc.tenant_id
FROM public.curriculum_classes cc
WHERE e.class_level_id = cc.class_level_id
  AND e.tenant_id IS NULL;

UPDATE public.subjects s
SET tenant_id = e.tenant_id
FROM public.exams e
WHERE s.exam_id = e.exam_id
  AND s.tenant_id IS NULL;

UPDATE public.chapter_analysis_versions cav
SET tenant_id = c.tenant_id,
    chapter_id = c.chapter_id
FROM public.chapters c
WHERE c.chapter_analysis_id = cav.chapter_analysis_id
  AND (cav.tenant_id IS NULL OR cav.chapter_id IS NULL);

UPDATE public.concept_entries ce
SET tenant_id = c.tenant_id
FROM public.chapters c
WHERE ce.chapter_id = c.chapter_id
  AND ce.tenant_id IS NULL;

ALTER TABLE public.curriculum_classes ALTER COLUMN tenant_id SET NOT NULL;
ALTER TABLE public.exams ALTER COLUMN tenant_id SET NOT NULL;
ALTER TABLE public.subjects ALTER COLUMN tenant_id SET NOT NULL;
ALTER TABLE public.chapter_analysis_versions ALTER COLUMN tenant_id SET NOT NULL;
ALTER TABLE public.chapter_analysis_versions ALTER COLUMN chapter_id SET NOT NULL;
ALTER TABLE public.concept_entries ALTER COLUMN tenant_id SET NOT NULL;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'curriculum_classes_tenant_id_fkey') THEN
        ALTER TABLE public.curriculum_classes
            ADD CONSTRAINT curriculum_classes_tenant_id_fkey
            FOREIGN KEY (tenant_id) REFERENCES public.tenants(tenant_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'exams_tenant_id_fkey') THEN
        ALTER TABLE public.exams
            ADD CONSTRAINT exams_tenant_id_fkey
            FOREIGN KEY (tenant_id) REFERENCES public.tenants(tenant_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'subjects_tenant_id_fkey') THEN
        ALTER TABLE public.subjects
            ADD CONSTRAINT subjects_tenant_id_fkey
            FOREIGN KEY (tenant_id) REFERENCES public.tenants(tenant_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chapter_analysis_versions_tenant_id_fkey') THEN
        ALTER TABLE public.chapter_analysis_versions
            ADD CONSTRAINT chapter_analysis_versions_tenant_id_fkey
            FOREIGN KEY (tenant_id) REFERENCES public.tenants(tenant_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chapter_analysis_versions_chapter_id_fkey') THEN
        ALTER TABLE public.chapter_analysis_versions
            ADD CONSTRAINT chapter_analysis_versions_chapter_id_fkey
            FOREIGN KEY (chapter_id) REFERENCES public.chapters(chapter_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'concept_entries_tenant_id_fkey') THEN
        ALTER TABLE public.concept_entries
            ADD CONSTRAINT concept_entries_tenant_id_fkey
            FOREIGN KEY (tenant_id) REFERENCES public.tenants(tenant_id);
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS curriculum_classes_tenant_id_idx
    ON public.curriculum_classes (tenant_id);
CREATE INDEX IF NOT EXISTS exams_tenant_id_idx ON public.exams (tenant_id);
CREATE INDEX IF NOT EXISTS subjects_tenant_id_idx ON public.subjects (tenant_id);
CREATE INDEX IF NOT EXISTS chapter_analysis_versions_tenant_id_idx
    ON public.chapter_analysis_versions (tenant_id);
CREATE UNIQUE INDEX IF NOT EXISTS chapter_analysis_versions_chapter_id_idx
    ON public.chapter_analysis_versions (chapter_id);
CREATE INDEX IF NOT EXISTS concept_entries_tenant_id_idx
    ON public.concept_entries (tenant_id);

CREATE INDEX IF NOT EXISTS chapters_class_level_id_idx
    ON public.chapters (class_level_id);
CREATE INDEX IF NOT EXISTS chapters_exam_id_idx ON public.chapters (exam_id);
CREATE INDEX IF NOT EXISTS chapters_subject_id_idx ON public.chapters (subject_id);
CREATE INDEX IF NOT EXISTS chapters_chapter_analysis_id_idx
    ON public.chapters (chapter_analysis_id);
CREATE INDEX IF NOT EXISTS subjects_class_level_id_idx
    ON public.subjects (class_level_id);

CREATE UNIQUE INDEX IF NOT EXISTS memberships_one_active_role_idx
    ON public.memberships (tenant_id, user_id, role)
    WHERE status = 'active' AND active_to IS NULL;
CREATE UNIQUE INDEX IF NOT EXISTS consent_records_one_active_kind_idx
    ON public.consent_records (tenant_id, student_user_id, consent_kind)
    WHERE state = 'granted' AND withdrawn_at IS NULL;

-- The app-facing launch row must resolve to the Phase 2 content schema used by session start.
INSERT INTO curriculum.chapters (
    chapter_id, tenant_id, exam_id, subject_id, title, chapter_analysis_id,
    source_doc_hash, segment_index_version, pipeline_version
) VALUES (
    '10000000-0000-4000-8000-000000000040',
    '00000000-0000-4000-8000-000000000010',
    '10000000-0000-4000-8000-000000000020',
    '10000000-0000-4000-8000-000000000030',
    'Electricity',
    '10000000-0000-4000-8000-000000000050',
    'm4-fixture-electricity-v1',
    'm4-fixture-v1',
    'm4-fixture-v1'
)
ON CONFLICT (chapter_id) DO UPDATE SET
    chapter_analysis_id = EXCLUDED.chapter_analysis_id,
    segment_index_version = EXCLUDED.segment_index_version,
    pipeline_version = EXCLUDED.pipeline_version;

INSERT INTO curriculum.segments (
    segment_id, chapter_id, tenant_id, chapter_analysis_id, segment_type,
    text, page, char_span, location, pipeline_version
) VALUES (
    'm4_electricity_para_001',
    '10000000-0000-4000-8000-000000000040',
    '00000000-0000-4000-8000-000000000010',
    '10000000-0000-4000-8000-000000000050',
    'paragraph',
    'Electric current flows through a closed circuit.',
    1,
    '{"start": 0, "end": 48}'::jsonb,
    'M4 fixture launch segment',
    'm4-fixture-v1'
)
ON CONFLICT (segment_id) DO UPDATE SET text = EXCLUDED.text;

INSERT INTO curriculum.concepts (
    concept_id, chapter_id, tenant_id, chapter_analysis_id, label, definition,
    category_tag, passage_refs, merged_from, pipeline_version, prompt_version, model_id
) VALUES (
    '10000000-0000-4000-8000-000000000060',
    '10000000-0000-4000-8000-000000000040',
    '00000000-0000-4000-8000-000000000010',
    '10000000-0000-4000-8000-000000000050',
    'Electricity overview',
    'A chapter-level entry point for the M4 fixture-backed launch path.',
    'overview',
    '{"definitional": ["m4_electricity_para_001"], "explanatory": [], "application": []}'::jsonb,
    '[]'::jsonb,
    'm4-fixture-v1',
    'fixture-electricity-v1',
    'fixture'
)
ON CONFLICT (concept_id) DO UPDATE SET definition = EXCLUDED.definition;

DROP POLICY IF EXISTS curriculum_classes_read_all ON public.curriculum_classes;
DROP POLICY IF EXISTS curriculum_classes_tenant_isolation ON public.curriculum_classes;
CREATE POLICY curriculum_classes_tenant_isolation ON public.curriculum_classes
    USING (tenant_id = (SELECT public.current_app_tenant_id()));

DROP POLICY IF EXISTS exams_read_all ON public.exams;
DROP POLICY IF EXISTS exams_tenant_isolation ON public.exams;
CREATE POLICY exams_tenant_isolation ON public.exams
    USING (tenant_id = (SELECT public.current_app_tenant_id()));

DROP POLICY IF EXISTS subjects_read_all ON public.subjects;
DROP POLICY IF EXISTS subjects_tenant_isolation ON public.subjects;
CREATE POLICY subjects_tenant_isolation ON public.subjects
    USING (tenant_id = (SELECT public.current_app_tenant_id()));

DROP POLICY IF EXISTS chapter_analysis_versions_read_all ON public.chapter_analysis_versions;
DROP POLICY IF EXISTS chapter_analysis_versions_tenant_isolation
    ON public.chapter_analysis_versions;
CREATE POLICY chapter_analysis_versions_tenant_isolation
    ON public.chapter_analysis_versions
    USING (tenant_id = (SELECT public.current_app_tenant_id()));

DROP POLICY IF EXISTS concept_entries_launch_chapter_read ON public.concept_entries;
DROP POLICY IF EXISTS concept_entries_tenant_isolation ON public.concept_entries;
CREATE POLICY concept_entries_tenant_isolation ON public.concept_entries
    USING (tenant_id = (SELECT public.current_app_tenant_id()));

COMMIT;
