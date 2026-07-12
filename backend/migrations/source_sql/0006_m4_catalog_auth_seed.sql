-- M4 catalog/auth seed SQL for Mindmap project ref jbmqyxhrmcbdgardamrp.
-- DO NOT run this against MCP-visible project ahntbtktjjmvfosgkmgn / Bookconnect_reactexpo.
-- Applied through Supabase migration tooling only after verifying the project ref.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS public.curriculum_classes (
    class_level_id UUID PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    label TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.exams (
    exam_id UUID PRIMARY KEY,
    class_level_id UUID NOT NULL REFERENCES public.curriculum_classes(class_level_id),
    slug TEXT NOT NULL,
    name TEXT NOT NULL,
    status TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (class_level_id, slug)
);

CREATE TABLE IF NOT EXISTS public.subjects (
    subject_id UUID PRIMARY KEY,
    class_level_id UUID NOT NULL REFERENCES public.curriculum_classes(class_level_id),
    exam_id UUID NOT NULL REFERENCES public.exams(exam_id),
    slug TEXT NOT NULL,
    name TEXT NOT NULL,
    status TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (exam_id, slug)
);

CREATE TABLE IF NOT EXISTS public.chapter_analysis_versions (
    chapter_analysis_id UUID PRIMARY KEY,
    version TEXT NOT NULL,
    qa_status TEXT NOT NULL,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.chapters (
    chapter_id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES public.tenants(tenant_id),
    class_level_id UUID NOT NULL REFERENCES public.curriculum_classes(class_level_id),
    exam_id UUID NOT NULL REFERENCES public.exams(exam_id),
    subject_id UUID NOT NULL REFERENCES public.subjects(subject_id),
    chapter_analysis_id UUID NOT NULL REFERENCES public.chapter_analysis_versions(chapter_analysis_id),
    slug TEXT NOT NULL,
    title TEXT NOT NULL,
    status TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, subject_id, slug)
);

CREATE TABLE IF NOT EXISTS public.concept_entries (
    concept_entry_id UUID PRIMARY KEY,
    chapter_id UUID NOT NULL REFERENCES public.chapters(chapter_id),
    slug TEXT NOT NULL,
    title TEXT NOT NULL,
    status TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (chapter_id, slug)
);

CREATE INDEX IF NOT EXISTS exams_class_level_id_idx ON public.exams (class_level_id);
CREATE INDEX IF NOT EXISTS subjects_exam_id_idx ON public.subjects (exam_id);
CREATE INDEX IF NOT EXISTS chapters_tenant_subject_status_idx
    ON public.chapters (tenant_id, subject_id, status);
CREATE INDEX IF NOT EXISTS concept_entries_chapter_status_idx
    ON public.concept_entries (chapter_id, status);

ALTER TABLE public.curriculum_classes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.exams ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subjects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chapter_analysis_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chapters ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.concept_entries ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS curriculum_classes_read_all ON public.curriculum_classes;
CREATE POLICY curriculum_classes_read_all ON public.curriculum_classes
    FOR SELECT USING (true);

DROP POLICY IF EXISTS exams_read_all ON public.exams;
CREATE POLICY exams_read_all ON public.exams
    FOR SELECT USING (true);

DROP POLICY IF EXISTS subjects_read_all ON public.subjects;
CREATE POLICY subjects_read_all ON public.subjects
    FOR SELECT USING (true);

DROP POLICY IF EXISTS chapter_analysis_versions_read_all ON public.chapter_analysis_versions;
CREATE POLICY chapter_analysis_versions_read_all ON public.chapter_analysis_versions
    FOR SELECT USING (true);

DROP POLICY IF EXISTS chapters_tenant_isolation ON public.chapters;
CREATE POLICY chapters_tenant_isolation ON public.chapters
    FOR SELECT USING (tenant_id = (SELECT public.current_app_tenant_id()));

DROP POLICY IF EXISTS concept_entries_launch_chapter_read ON public.concept_entries;
CREATE POLICY concept_entries_launch_chapter_read ON public.concept_entries
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.chapters c
            WHERE c.chapter_id = concept_entries.chapter_id
              AND c.tenant_id = (SELECT public.current_app_tenant_id())
        )
    );

INSERT INTO public.curriculum_classes (class_level_id, slug, label, sort_order)
VALUES ('10000000-0000-4000-8000-000000000010', 'class-10', 'Class 10', 10)
ON CONFLICT (class_level_id) DO UPDATE SET
    slug = EXCLUDED.slug,
    label = EXCLUDED.label,
    sort_order = EXCLUDED.sort_order;

INSERT INTO public.exams (exam_id, class_level_id, slug, name, status, sort_order)
VALUES (
    '10000000-0000-4000-8000-000000000020',
    '10000000-0000-4000-8000-000000000010',
    'cbse',
    'CBSE',
    'active',
    10
)
ON CONFLICT (exam_id) DO UPDATE SET
    name = EXCLUDED.name,
    status = EXCLUDED.status,
    sort_order = EXCLUDED.sort_order;

INSERT INTO public.subjects (subject_id, class_level_id, exam_id, slug, name, status, sort_order)
VALUES (
    '10000000-0000-4000-8000-000000000030',
    '10000000-0000-4000-8000-000000000010',
    '10000000-0000-4000-8000-000000000020',
    'science',
    'Science',
    'active',
    10
)
ON CONFLICT (subject_id) DO UPDATE SET
    name = EXCLUDED.name,
    status = EXCLUDED.status,
    sort_order = EXCLUDED.sort_order;

INSERT INTO public.chapter_analysis_versions (chapter_analysis_id, version, qa_status)
VALUES ('10000000-0000-4000-8000-000000000050', 'fixture-electricity-v1', 'approved')
ON CONFLICT (chapter_analysis_id) DO UPDATE SET
    version = EXCLUDED.version,
    qa_status = EXCLUDED.qa_status;

INSERT INTO public.tenants (tenant_id, kind, name, status)
VALUES (
    '00000000-0000-4000-8000-000000000010',
    'individual',
    'M4 Individual Launch Tenant',
    'active'
)
ON CONFLICT (tenant_id) DO UPDATE SET
    kind = EXCLUDED.kind,
    name = EXCLUDED.name,
    status = EXCLUDED.status,
    updated_at = now();

INSERT INTO public.chapters (
    chapter_id, tenant_id, class_level_id, exam_id, subject_id, chapter_analysis_id,
    slug, title, status, sort_order
)
VALUES (
    '10000000-0000-4000-8000-000000000040',
    '00000000-0000-4000-8000-000000000010',
    '10000000-0000-4000-8000-000000000010',
    '10000000-0000-4000-8000-000000000020',
    '10000000-0000-4000-8000-000000000030',
    '10000000-0000-4000-8000-000000000050',
    'electricity',
    'Electricity',
    'launchable',
    10
)
ON CONFLICT (chapter_id) DO UPDATE SET
    status = EXCLUDED.status,
    sort_order = EXCLUDED.sort_order,
    chapter_analysis_id = EXCLUDED.chapter_analysis_id;

INSERT INTO public.concept_entries (concept_entry_id, chapter_id, slug, title, status, sort_order)
VALUES (
    '10000000-0000-4000-8000-000000000060',
    '10000000-0000-4000-8000-000000000040',
    'electricity-overview',
    'Electricity overview',
    'active',
    10
)
ON CONFLICT (concept_entry_id) DO UPDATE SET
    title = EXCLUDED.title,
    status = EXCLUDED.status,
    sort_order = EXCLUDED.sort_order;
