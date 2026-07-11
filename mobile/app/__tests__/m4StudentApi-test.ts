import {
  signInWithEmailPassword,
  signOutSupabaseSession,
  signUpWithEmailPassword,
} from '../../m4/supabaseAuth';
import {
  bootstrapStudentAuth,
  loadElectricityLaunchPath,
  startElectricitySession,
} from '../../m4/studentApi';

const originalFetch = global.fetch;

describe('M4 Supabase auth service', () => {
  afterEach(() => {
    jest.clearAllMocks();
    global.fetch = originalFetch;
  });

  it('signs up with Supabase email/password using anon key headers', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        access_token: 'supabase-token',
        refresh_token: 'refresh-token',
        expires_at: 2_000_000_000,
        user: { id: 'user-1' },
      }),
    });

    const result = await signUpWithEmailPassword({
      supabaseUrl: 'https://project.supabase.co',
      anonKey: 'anon',
      email: 'student@example.com',
      password: 'secret-123',
    });

    expect(result.accessToken).toBe('supabase-token');
    expect(global.fetch).toHaveBeenCalledWith(
      'https://project.supabase.co/auth/v1/signup',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({ apikey: 'anon', Authorization: 'Bearer anon' }),
      }),
    );
  });

  it('rejects placeholder Supabase anon key before calling auth API', async () => {
    global.fetch = jest.fn();

    await expect(
      signUpWithEmailPassword({
        supabaseUrl: 'https://project.supabase.co',
        anonKey: '<anon key>',
        email: 'student@gmail.com',
        password: 'secret-123',
      }),
    ).rejects.toThrow('Supabase anon key is not configured');
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('signs in with Supabase password grant', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        access_token: 'login-token',
        refresh_token: 'refresh-token',
        expires_at: 2_000_000_000,
        user: { id: 'user-1' },
      }),
    });

    const result = await signInWithEmailPassword({
      supabaseUrl: 'https://project.supabase.co/',
      anonKey: 'anon',
      email: 'student@example.com',
      password: 'secret-123',
    });

    expect(result.accessToken).toBe('login-token');
    expect(global.fetch).toHaveBeenCalledWith(
      'https://project.supabase.co/auth/v1/token?grant_type=password',
      expect.objectContaining({ method: 'POST' }),
    );
  });

  it('revokes the Supabase session during sign-out', async () => {
    global.fetch = jest.fn().mockResolvedValue({ ok: true, status: 204 });

    await signOutSupabaseSession({
      supabaseUrl: 'https://project.supabase.co/',
      anonKey: 'anon',
      accessToken: 'access-token',
    });

    expect(global.fetch).toHaveBeenCalledWith(
      'https://project.supabase.co/auth/v1/logout',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          apikey: 'anon',
          Authorization: 'Bearer access-token',
        }),
      }),
    );
  });
});

describe('M4 student API launch path', () => {
  afterEach(() => {
    jest.clearAllMocks();
    global.fetch = originalFetch;
  });

  it('loads Class 10 -> CBSE -> Science -> Electricity IDs through student-safe endpoints', async () => {
    global.fetch = jest
      .fn()
      .mockResolvedValueOnce({ ok: true, json: async () => ({ classes: [{ class_id: 'class-10', label: 'Class 10' }] }) })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ exams: [{ exam_id: 'cbse', label: 'CBSE' }] }) })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ subjects: [{ subject_id: 'science', label: 'Science' }] }) })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ chapters: [{ chapter_id: 'electricity', title: 'Electricity' }] }) })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ concept_entries: [{ concept_entry_id: 'concept-root', label: 'Electricity overview' }] }),
      });

    const result = await loadElectricityLaunchPath({
      apiBaseUrl: 'http://127.0.0.1:8000',
      accessToken: 'student-token',
    });

    expect(result).toEqual({
      classId: 'class-10',
      classLabel: 'Class 10',
      examId: 'cbse',
      examName: 'CBSE',
      subjectId: 'science',
      subjectName: 'Science',
      chapterId: 'electricity',
      chapterTitle: 'Electricity',
      conceptEntryId: 'concept-root',
      conceptTitle: 'Electricity overview',
    });
    expect((global.fetch as jest.Mock).mock.calls.map(([url]) => url)).toEqual([
      'http://127.0.0.1:8000/v1/student/curriculum/classes',
      'http://127.0.0.1:8000/v1/student/curriculum/exams?class_id=class-10',
      'http://127.0.0.1:8000/v1/student/curriculum/subjects?class_id=class-10&exam_id=cbse',
      'http://127.0.0.1:8000/v1/student/curriculum/chapters?class_id=class-10&exam_id=cbse&subject_id=science',
      'http://127.0.0.1:8000/v1/student/chapters/electricity/concept-entries',
    ]);
  });

  it('loads launch path from backend items response shape', async () => {
    global.fetch = jest
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          items: [{ class_level_id: 'class-10', slug: 'class-10', label: 'Class 10' }],
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ items: [{ exam_id: 'cbse', slug: 'cbse', name: 'CBSE' }] }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          items: [{ subject_id: 'science', slug: 'science', name: 'Science' }],
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          items: [{ chapter_id: 'electricity', slug: 'electricity', title: 'Electricity' }],
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          items: [{ concept_entry_id: 'concept-root', title: 'Electricity overview' }],
        }),
      });

    const result = await loadElectricityLaunchPath({
      apiBaseUrl: 'http://127.0.0.1:8000',
      accessToken: 'student-token',
    });

    expect(result.classId).toBe('class-10');
    expect((global.fetch as jest.Mock).mock.calls[1][0]).toBe(
      'http://127.0.0.1:8000/v1/student/curriculum/exams?class_id=class-10',
    );
  });

  it('bootstraps backend B2C membership before student API calls', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        user_id: 'user-1',
        tenant_id: 'tenant-1',
        role: 'student',
        behavioral_analytics_consent_granted: true,
      }),
    });

    const result = await bootstrapStudentAuth({
      apiBaseUrl: 'http://127.0.0.1:8000',
      accessToken: 'student-token',
    });

    expect(result).toEqual({
      userId: 'user-1',
      tenantId: 'tenant-1',
      role: 'student',
      behavioralAnalyticsConsentGranted: true,
    });
    expect(global.fetch).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/v1/student/auth/bootstrap',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({ Authorization: 'Bearer student-token' }),
        signal: expect.any(Object),
        body: '{}',
      }),
    );
  });

  it('starts an Electricity session with launch path IDs', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ session_id: 'session-1' }),
    });

    const session = await startElectricitySession({
      apiBaseUrl: 'http://127.0.0.1:8000',
      accessToken: 'student-token',
      launchPath: {
        classId: 'class-10',
        classLabel: 'Class 10',
        examId: 'cbse',
        examName: 'CBSE',
        subjectId: 'science',
        subjectName: 'Science',
        chapterId: 'electricity',
        chapterTitle: 'Electricity',
        conceptEntryId: 'concept-root',
        conceptTitle: 'Electricity overview',
      },
      behavioralAnalyticsConsent: true,
    });

    expect(session.sessionId).toBe('session-1');
    expect(global.fetch).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/v1/student/sessions',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({ Authorization: 'Bearer student-token' }),
        signal: expect.any(Object),
        body: JSON.stringify({
          exam_id: 'cbse',
          subject_id: 'science',
          chapter_id: 'electricity',
          concept_entry_id: 'concept-root',
          behavioral_analytics_consent: true,
        }),
      }),
    );
  });

  it('preserves backend error detail in thrown messages', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: false,
      status: 404,
      json: async () => ({ detail: 'Chapter not found in curriculum' }),
    });

    await expect(
      startElectricitySession({
        apiBaseUrl: 'http://127.0.0.1:8000',
        accessToken: 'student-token',
        launchPath: {
          classId: 'class-10',
          classLabel: 'Class 10',
          examId: 'cbse',
          examName: 'CBSE',
          subjectId: 'science',
          subjectName: 'Science',
          chapterId: 'electricity',
          chapterTitle: 'Electricity',
          conceptEntryId: 'concept-root',
          conceptTitle: 'Electricity overview',
        },
        behavioralAnalyticsConsent: true,
      }),
    ).rejects.toThrow('Student API failed: 404: Chapter not found in curriculum');
  });

  it('maps aborted student API calls to timeout errors', async () => {
    const abortError = new Error('aborted');
    abortError.name = 'AbortError';
    global.fetch = jest.fn().mockRejectedValue(abortError);

    await expect(
      loadElectricityLaunchPath({
        apiBaseUrl: 'http://127.0.0.1:8000',
        accessToken: 'student-token',
        timeoutMs: 1,
      }),
    ).rejects.toThrow('Student API request timed out');
    expect((global.fetch as jest.Mock).mock.calls[0][1].signal).toBeTruthy();
  });
});
