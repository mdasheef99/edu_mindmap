import {
  clearStoredSupabaseSession,
  loadStoredSupabaseSession,
  saveStoredSupabaseSession,
} from '../../m4/sessionStore';
import {
  refreshSupabaseSession,
  signInWithEmailPassword,
} from '../../m4/supabaseAuth';
import { loadStudentDashboard, resumeStudentSession } from '../../m4/studentApi';

const mockSecureValues = new Map<string, string>();

jest.mock('expo-secure-store', () => ({
  getItemAsync: jest.fn(async (key: string) => mockSecureValues.get(key) ?? null),
  setItemAsync: jest.fn(async (key: string, value: string) => {
    mockSecureValues.set(key, value);
  }),
  deleteItemAsync: jest.fn(async (key: string) => {
    mockSecureValues.delete(key);
  }),
}));

describe('M4 persisted auth and dashboard lifecycle', () => {
  const originalFetch = global.fetch;

  beforeEach(() => {
    mockSecureValues.clear();
    jest.clearAllMocks();
  });

  afterEach(() => {
    global.fetch = originalFetch;
  });

  it('persists and restores the access/refresh session', async () => {
    const session = {
      accessToken: 'access-token',
      refreshToken: 'refresh-token',
      expiresAt: 2_000_000_000,
      userId: 'user-1',
    };

    await saveStoredSupabaseSession(session);
    await expect(loadStoredSupabaseSession()).resolves.toEqual(session);
    await clearStoredSupabaseSession();
    await expect(loadStoredSupabaseSession()).resolves.toBeNull();
  });

  it('retains refresh metadata from sign-in and refreshes through Supabase', async () => {
    global.fetch = jest
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          access_token: 'access-1',
          refresh_token: 'refresh-1',
          expires_at: 2_000_000_000,
          user: { id: 'user-1' },
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          access_token: 'access-2',
          refresh_token: 'refresh-2',
          expires_at: 2_000_000_100,
          user: { id: 'user-1' },
        }),
      });

    const signedIn = await signInWithEmailPassword({
      supabaseUrl: 'https://project.supabase.co',
      anonKey: 'anon',
      email: 'student@example.com',
      password: 'strong-password',
    });
    const refreshed = await refreshSupabaseSession({
      supabaseUrl: 'https://project.supabase.co',
      anonKey: 'anon',
      refreshToken: signedIn.refreshToken,
    });

    expect(signedIn.refreshToken).toBe('refresh-1');
    expect(refreshed.accessToken).toBe('access-2');
    expect((global.fetch as jest.Mock).mock.calls[1][0]).toBe(
      'https://project.supabase.co/auth/v1/token?grant_type=refresh_token',
    );
  });

  it('loads dashboard and resumes an existing session with bearer auth', async () => {
    global.fetch = jest
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          continue_learning: {
            session_id: 'session-1',
            chapter_id: 'chapter-1',
            chapter_title: 'Electricity',
            last_active_at: '2026-07-10T00:00:00Z',
            status: 'active',
          },
          recent_sessions: [],
          launch_suggestions: [],
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ session_id: 'session-1' }),
      });

    const dashboard = await loadStudentDashboard({
      apiBaseUrl: 'https://api.example.com',
      accessToken: 'access-token',
    });
    const resumed = await resumeStudentSession({
      apiBaseUrl: 'https://api.example.com',
      accessToken: 'access-token',
      sessionId: dashboard.continueLearning!.sessionId,
    });

    expect(dashboard.continueLearning?.chapterTitle).toBe('Electricity');
    expect(resumed.sessionId).toBe('session-1');
    expect((global.fetch as jest.Mock).mock.calls[1][1].headers.Authorization).toBe(
      'Bearer access-token',
    );
  });
});
