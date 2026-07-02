import React from 'react';
import { fireEvent, render, screen, waitFor, act } from '@testing-library/react-native';
import { M4CurriculumAuthScreen } from '../../M4CurriculumAuthScreen';

const originalFetch = global.fetch;

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
    global.fetch = jest
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ access_token: 'student-token', user: { id: 'user-1' } }),
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
      />,
    );

    await fillInput('m4-email-input', 'student@example.com');
    await fillInput('m4-password-input', 'secret-123');
    await act(async () => {
      fireEvent.press(screen.getByText('Sign in'));
    });

    await waitFor(() => screen.getByText('Electricity ready'));
    await act(async () => {
      fireEvent.press(screen.getByText('Start Electricity'));
    });

    await waitFor(() => screen.getByText('Session: session-1'));
    expect((global.fetch as jest.Mock).mock.calls[0][0]).toBe(
      'https://project.supabase.co/auth/v1/token?grant_type=password',
    );
    expect((global.fetch as jest.Mock).mock.calls[6][1].headers.Authorization).toBe(
      'Bearer student-token',
    );
  });
});
