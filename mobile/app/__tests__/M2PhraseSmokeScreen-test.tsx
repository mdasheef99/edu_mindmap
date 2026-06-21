/**
 * Unit tests for M2PhraseSmokeScreen.
 *
 * Invariants exercised:
 *  - SDD §12 security: authToken field uses secureTextEntry; keyboard-mangling workaround via "Fill dev defaults" button.
 *  - SDD §12 / development-approach.md §7.6: Jest + RNTL is the prescribed mobile
 *    test path; the pytest static smoke was an interim stopgap.
 *
 * Notes on RNTL v14 + React 19:
 *  - render() is async → always await it.
 *  - fireEvent does NOT wrap in act() → wrap changeText calls in act() so state
 *    updates are flushed before subsequent events read them.
 *  - Use screen queries (always bound to latest render tree).
 *  - Use testID for inputs — more reliable than placeholder in RN host tree.
 *
 * Traceability: development-approach.md §7.6; SDD §12; backend-architecture.md §6.2
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react-native';
import { M2PhraseSmokeScreen } from '../M2PhraseSmokeScreen';

// Isolate the smoke screen from the real sheet — sheet has its own test file.
jest.mock('../../PhraseSelectionReaderSheet', () => ({
  PhraseSelectionReaderSheet: () => null,
}));

const API_BASE = 'http://localhost:8000';

function mockFetchOk(body: object) {
  return jest.fn().mockResolvedValue({ ok: true, json: async () => body });
}

function mockFetchFail(body: object) {
  return jest.fn().mockResolvedValue({ ok: false, json: async () => body });
}

/** Enter text into a controlled TextInput and flush the state update. */
async function fillInput(testId: string, text: string) {
  await act(async () => {
    fireEvent.changeText(screen.getByTestId(testId), text);
  });
}

describe('M2PhraseSmokeScreen', () => {
  afterEach(() => jest.clearAllMocks());

  it('renders heading, field labels, and start button', async () => {
    await render(<M2PhraseSmokeScreen />);
    screen.getByText('M2 Phrase Selection Smoke');
    screen.getByText('API Base URL');
    screen.getByText('Auth Token');
    screen.getByText('Start test session');
  });

  it('shows idle status initially', async () => {
    await render(<M2PhraseSmokeScreen />);
    screen.getByText('Status: idle');
  });

  /**
   * Security invariant — SDD §12:
   * The token field must have secureTextEntry to mask the JWT on screen.
   * Keyboard-mangling workaround: "Fill dev defaults" writes the token
   * programmatically, bypassing the secure keyboard (no paste = no 0x141 bug).
   * Belt-and-suspenders: autocorrect/spellcheck still disabled.
   */
  it('auth token input has secureTextEntry and disables autocorrect/spellcheck', async () => {
    await render(<M2PhraseSmokeScreen />);
    const tokenInput = screen.getByTestId('auth-token-input');
    expect(tokenInput.props.secureTextEntry).toBe(true);
    expect(tokenInput.props.autoCorrect).toBe(false);
    expect(tokenInput.props.autoCapitalize).toBe('none');
    expect(tokenInput.props.spellCheck).toBe(false);
  });

  it('Fill dev defaults button pre-fills URL and token', async () => {
    await render(<M2PhraseSmokeScreen />);
    await act(async () => {
      fireEvent.press(screen.getByText('Fill dev defaults'));
    });
    const urlInput = screen.getByTestId('api-base-url-input');
    expect(urlInput.props.value).toMatch(/^http:\/\//);
    const tokenInput = screen.getByTestId('auth-token-input');
    expect(tokenInput.props.value).toMatch(/^eyJ/);
  });

  it('"Open phrase reader" is not rendered before session starts', async () => {
    await render(<M2PhraseSmokeScreen />);
    expect(screen.queryByText('Open phrase reader')).toBeNull();
  });

  it('calls POST /v1/student/sessions with bearer token on start', async () => {
    global.fetch = mockFetchOk({ session_id: 'sess-001' });

    await render(<M2PhraseSmokeScreen />);
    await fillInput('api-base-url-input', API_BASE);
    await fillInput('auth-token-input', 'tok');
    fireEvent.press(screen.getByText('Start test session'));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        `${API_BASE}/v1/student/sessions`,
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({ Authorization: 'Bearer tok' }),
        }),
      );
    });
  });

  it('shows session id in status after successful start', async () => {
    global.fetch = mockFetchOk({ session_id: 'sess-002' });

    await render(<M2PhraseSmokeScreen />);
    await fillInput('api-base-url-input', API_BASE);
    fireEvent.press(screen.getByText('Start test session'));

    await waitFor(() => screen.getByText('Status: session started: sess-002'));
  });

  it('shows "Open phrase reader" button after session starts', async () => {
    global.fetch = mockFetchOk({ session_id: 'sess-003' });

    await render(<M2PhraseSmokeScreen />);
    await fillInput('api-base-url-input', API_BASE);
    fireEvent.press(screen.getByText('Start test session'));

    await waitFor(() => screen.getByText('Open phrase reader'));
  });

  it('shows failure status when session call returns non-ok', async () => {
    global.fetch = mockFetchFail({ detail: 'unauthorized' });

    await render(<M2PhraseSmokeScreen />);
    await fillInput('api-base-url-input', API_BASE);
    fireEvent.press(screen.getByText('Start test session'));

    await waitFor(() => expect(screen.getByText(/Status: failed/)).toBeTruthy());
  });
});
