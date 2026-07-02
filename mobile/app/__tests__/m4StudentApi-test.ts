import { signInWithEmailPassword, signUpWithEmailPassword } from '../../m4/supabaseAuth';
import { loadElectricityLaunchPath, startElectricitySession } from '../../m4/studentApi';

const originalFetch = global.fetch;

describe('M4 Supabase auth service', () => {
  afterEach(() => {
    jest.clearAllMocks();
    global.fetch = originalFetch;
  });

  it('signs up with Supabase email/password using anon key headers', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ access_token: 'supabase-token', user: { id: 'user-1' } }),
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

  it('signs in with Supabase password grant', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ access_token: 'login-token', user: { id: 'user-1' } }),
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
      examId: 'cbse',
      subjectId: 'science',
      chapterId: 'electricity',
      conceptEntryId: 'concept-root',
    });
    expect((global.fetch as jest.Mock).mock.calls.map(([url]) => url)).toEqual([
      'http://127.0.0.1:8000/v1/student/curriculum/classes',
      'http://127.0.0.1:8000/v1/student/curriculum/exams?class_id=class-10',
      'http://127.0.0.1:8000/v1/student/curriculum/subjects?class_id=class-10&exam_id=cbse',
      'http://127.0.0.1:8000/v1/student/curriculum/chapters?class_id=class-10&exam_id=cbse&subject_id=science',
      'http://127.0.0.1:8000/v1/student/chapters/electricity/concept-entries',
    ]);
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
        examId: 'cbse',
        subjectId: 'science',
        chapterId: 'electricity',
        conceptEntryId: 'concept-root',
      },
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
          examId: 'cbse',
          subjectId: 'science',
          chapterId: 'electricity',
          conceptEntryId: 'concept-root',
        },
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
