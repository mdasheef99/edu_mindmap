import React from 'react';
import { fireEvent, render, screen, waitFor, act } from '@testing-library/react-native';
import { M4CurriculumAuthScreen } from '../../M4CurriculumAuthScreen';

jest.mock('../../m4/sessionStore', () => ({
  loadStoredSupabaseSession: jest.fn(async () => null),
  saveStoredSupabaseSession: jest.fn(async () => undefined),
  clearStoredSupabaseSession: jest.fn(async () => undefined),
}));

const originalFetch = global.fetch;

jest.setTimeout(15_000);

async function fillInput(testId: string, text: string) {
  await act(async () => {
    fireEvent.changeText(screen.getByTestId(testId), text);
  });
}

describe('M4CurriculumAuthScreen', () => {
  afterEach(() => {
    jest.clearAllMocks();
    global.fetch = originalFetch;
  });

  it('masks password input and renders B2C auth actions', async () => {
    await render(
      <M4CurriculumAuthScreen
        apiBaseUrl="http://127.0.0.1:8000"
        supabaseUrl="https://project.supabase.co"
        supabaseAnonKey="anon"
      />,
    );

    expect(screen.getByText('Mindmap')).toBeTruthy();
    expect(screen.getByText('Create account')).toBeTruthy();
    expect(screen.getByText('Sign in')).toBeTruthy();
    expect(screen.getByTestId('m4-password-input').props.secureTextEntry).toBe(true);
  });

  it('signs in, loads the M4 launch path, and starts Electricity', async () => {
    const onSessionStarted = jest.fn();
    global.fetch = jest
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          access_token: 'student-token',
          refresh_token: 'refresh-token',
          expires_at: 2_000_000_000,
          user: { id: 'user-1' },
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          user_id: 'user-1',
          tenant_id: 'tenant-1',
          role: 'student',
          behavioral_analytics_consent_granted: false,
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ continue_learning: null, recent_sessions: [] }),
      })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ classes: [{ class_id: 'class-10', label: 'Class 10' }] }) })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ exams: [{ exam_id: 'cbse', label: 'CBSE' }] }) })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ subjects: [{ subject_id: 'science', label: 'Science' }] }) })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ chapters: [{ chapter_id: 'electricity', title: 'Electricity' }] }) })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ concept_entries: [{ concept_entry_id: 'concept-root', label: 'Electricity overview' }] }),
      })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ session_id: 'session-1' }) });

    await render(
      <M4CurriculumAuthScreen
        apiBaseUrl="http://127.0.0.1:8000"
        supabaseUrl="https://project.supabase.co"
        supabaseAnonKey="anon"
        onSessionStarted={onSessionStarted}
      />,
    );

    await fillInput('m4-email-input', 'student@example.com');
    await fillInput('m4-password-input', 'secret-123');
    await act(async () => {
      fireEvent.press(screen.getByText('Sign in'));
    });

    await waitFor(() => screen.getByText('Electricity ready'));
    expect(screen.getByText('Class 10')).toBeTruthy();
    expect(screen.getByText('CBSE')).toBeTruthy();
    expect(screen.getByText('Science')).toBeTruthy();
    await act(async () => {
      fireEvent(screen.getByTestId('m4-consent-switch'), 'valueChange', true);
    });
    await act(async () => {
      fireEvent.press(screen.getByText('Start Electricity'));
    });

    await waitFor(() => screen.getByText('Session: session-1'));
    expect(onSessionStarted).toHaveBeenCalledWith({
      sessionId: 'session-1',
      accessToken: 'student-token',
    });
    expect((global.fetch as jest.Mock).mock.calls[0][0]).toBe(
      'https://project.supabase.co/auth/v1/token?grant_type=password',
    );
    expect((global.fetch as jest.Mock).mock.calls[1][0]).toBe(
      'http://127.0.0.1:8000/v1/student/auth/bootstrap',
    );
    expect((global.fetch as jest.Mock).mock.calls[8][1].headers.Authorization).toBe(
      'Bearer student-token',
    );
  });

  it('shows the dashboard before curriculum loading finishes', async () => {
    let releaseClasses: ((value: unknown) => void) | undefined;
    const classesResponse = new Promise((resolve) => {
      releaseClasses = resolve;
    });
    global.fetch = jest.fn(async (input: unknown) => {
      const url = String(input);
      if (url.includes('/auth/v1/token')) {
        return {
          ok: true,
          json: async () => ({
            access_token: 'student-token', refresh_token: 'refresh-token',
            expires_at: 2_000_000_000, user: { id: 'user-1' },
          }),
        };
      }
      if (url.endsWith('/v1/student/auth/bootstrap')) {
        return {
          ok: true,
          json: async () => ({
            user_id: 'user-1', tenant_id: 'tenant-1', role: 'student',
            behavioral_analytics_consent_granted: true,
          }),
        };
      }
      if (url.endsWith('/v1/student/dashboard')) {
        return {
          ok: true,
          json: async () => ({
            continue_learning: {
              session_id: 'session-1', chapter_id: 'electricity', chapter_title: 'Electricity',
              last_active_at: '2026-07-10T00:00:00Z', status: 'active',
            },
            recent_sessions: [],
          }),
        };
      }
      if (url.endsWith('/v1/student/curriculum/classes')) return classesResponse;
      if (url.includes('/curriculum/exams')) {
        return { ok: true, json: async () => ({ exams: [{ exam_id: 'cbse', label: 'CBSE' }] }) };
      }
      if (url.includes('/curriculum/subjects')) {
        return { ok: true, json: async () => ({ subjects: [{ subject_id: 'science', label: 'Science' }] }) };
      }
      if (url.includes('/curriculum/chapters')) {
        return { ok: true, json: async () => ({ chapters: [{ chapter_id: 'electricity', title: 'Electricity' }] }) };
      }
      return {
        ok: true,
        json: async () => ({
          concept_entries: [{ concept_entry_id: 'concept-root', label: 'Electricity overview' }],
        }),
      };
    }) as unknown as typeof fetch;

    await render(
      <M4CurriculumAuthScreen
        apiBaseUrl="http://127.0.0.1:8000"
        supabaseUrl="https://project.supabase.co"
        supabaseAnonKey="anon"
      />,
    );
    await fillInput('m4-email-input', 'student@example.com');
    await fillInput('m4-password-input', 'secret-123');
    await act(async () => {
      fireEvent.press(screen.getByText('Sign in'));
      await Promise.resolve();
    });

    await waitFor(() => expect(screen.getByText('Resume Electricity')).toBeTruthy());
    expect(screen.getByText('Loading curriculum')).toBeTruthy();

    await act(async () => {
      releaseClasses?.({
        ok: true,
        json: async () => ({ classes: [{ class_id: 'class-10', label: 'Class 10' }] }),
      });
    });
    await waitFor(() => expect(screen.getByText('Electricity ready')).toBeTruthy());
  });

  it('does not request learning-data acknowledgement after consent is already granted', async () => {
    global.fetch = jest
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          access_token: 'student-token', refresh_token: 'refresh-token',
          expires_at: 2_000_000_000, user: { id: 'user-1' },
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          user_id: 'user-1', tenant_id: 'tenant-1', role: 'student',
          behavioral_analytics_consent_granted: true,
        }),
      })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ continue_learning: null, recent_sessions: [] }) })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ classes: [{ class_id: 'class-10', label: 'Class 10' }] }) })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ exams: [{ exam_id: 'cbse', label: 'CBSE' }] }) })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ subjects: [{ subject_id: 'science', label: 'Science' }] }) })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ chapters: [{ chapter_id: 'electricity', title: 'Electricity' }] }) })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ concept_entries: [{ concept_entry_id: 'concept-root', label: 'Electricity overview' }] }),
      });

    await render(
      <M4CurriculumAuthScreen
        apiBaseUrl="http://127.0.0.1:8000"
        supabaseUrl="https://project.supabase.co"
        supabaseAnonKey="anon"
      />,
    );
    await fillInput('m4-email-input', 'student@example.com');
    await fillInput('m4-password-input', 'secret-123');
    await act(async () => fireEvent.press(screen.getByText('Sign in')));

    await waitFor(() => expect(screen.getByText('Electricity ready')).toBeTruthy());
    expect(screen.queryByTestId('m4-consent-switch')).toBeNull();
    expect(screen.queryByText('Learning-data acknowledgement')).toBeNull();
    expect(screen.getByText('Consent already recorded')).toBeTruthy();
  });
});
