/**
 * Unit tests for PhraseSelectionReaderSheet.
 *
 * Invariants exercised:
 *  - Category Invisibility (canon / SDD §7): no analytic fields in the phrase-offer
 *    request body (propensity, score, dimension, classification, confidence, entropy,
 *    vector, profile, weight, teacher_*).
 *  - Organic-First (canon): dismissed outcome fires to the choices endpoint; selected
 *    outcome fires with outcome:"selected" and triggers onBranchCreated. No classify
 *    job is enqueued from the mobile layer — that is backend-only and async.
 *  - Tenant Isolation (canon): mobile layer does NOT send a tenant_id in any request.
 *
 * Notes on RNTL v14 + React 19:
 *  - render() is async → always await it.
 *  - UNSAFE_getAllByType removed in RNTL v14 → use testID="passage-input" instead.
 *  - Use screen queries for fresh bindings after each render.
 *
 * Traceability: development-approach.md §7.6; SDD §7, §12;
 *               backend-architecture.md §5.3–§5.5, §6.2
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react-native';
import { PhraseSelectionReaderSheet } from '../../PhraseSelectionReaderSheet';

const NODE = {
  sessionId: 'session-1',
  nodeId: 'node-1',
  threadContextId: 'thread-1',
  content: 'Electric current flows through a closed circuit.',
};

const OFFER_SET = {
  offer_set_id: 'offer-1',
  session_id: 'session-1',
  source_node_id: 'node-1',
  thread_context_id: 'thread-1',
  selected_phrase: 'Electric current',
  actions: [{ option_id: 'a1', text: 'Elaborate', rank_position: 1, action_type: 'elaborate' }],
  recommended_questions: [
    { option_id: 'r1', text: "What is Ohm's law?", rank_position: 2, action_type: 'recommended' },
  ],
};

const DEFAULT_PROPS = {
  visible: true,
  apiBaseUrl: 'http://localhost:8000',
  authorizationToken: 'test-token',
  node: NODE,
  onClose: jest.fn(),
  onBranchCreated: jest.fn(),
};

function makeProps(overrides = {}) {
  return { ...DEFAULT_PROPS, onClose: jest.fn(), onBranchCreated: jest.fn(), ...overrides };
}

/**
 * Simulate the user long-pressing to select characters [start, end) in the passage.
 * Wrapped in act() so setSelection state update is flushed before the caller reads
 * selectedPhrase (RNTL v14 does not auto-wrap fireEvent in act).
 */
async function selectPhrase(start: number, end: number) {
  await act(async () => {
    fireEvent(screen.getByTestId('passage-input'), 'selectionChange', {
      nativeEvent: { selection: { start, end } },
    });
  });
}

const originalFetch = global.fetch;

describe('PhraseSelectionReaderSheet', () => {
  afterEach(() => {
    jest.clearAllMocks();
    global.fetch = originalFetch;
  });

  it('renders Reader label, status, buttons when visible', async () => {
    await render(<PhraseSelectionReaderSheet {...makeProps()} />);
    screen.getByText('Reader');
    screen.getByText('Use selected phrase');
    screen.getByText('Close');
  });

  it('renders the node passage in the TextInput', async () => {
    await render(<PhraseSelectionReaderSheet {...makeProps()} />);
    screen.getByDisplayValue(NODE.content);
  });

  /**
   * Category Invisibility invariant — SDD §7 / canon:
   * The phrase-offer request must contain ONLY student-visible fields.
   */
  it('POST offer-sets/phrase body has no analytic fields (Category Invisibility)', async () => {
    global.fetch = jest.fn().mockResolvedValue({ ok: true, json: async () => OFFER_SET });
    const props = makeProps();
    await render(<PhraseSelectionReaderSheet {...props} />);

    await selectPhrase(0, 16); // "Electric current"
    fireEvent.press(screen.getByText('Use selected phrase'));

    await waitFor(() => expect(global.fetch).toHaveBeenCalled());

    const [url, opts] = (global.fetch as jest.Mock).mock.calls[0];
    expect(url).toContain('/v1/student/offer-sets/phrase');
    const body = JSON.parse(opts.body as string);

    // Confirm required student-safe fields
    expect(body.session_id).toBe('session-1');
    expect(body.source_node_id).toBe('node-1');
    expect(body.selected_phrase).toBe('Electric current');

    // Confirm analytic fields are absent
    for (const forbidden of [
      'propensity', 'score', 'dimension', 'classification', 'confidence',
      'entropy', 'vector', 'profile', 'weight', 'tenant_id',
    ]) {
      expect(body).not.toHaveProperty(forbidden);
    }

    // Confirm no teacher_* fields leak into the student request (Category Invisibility invariant)
    Object.keys(body).forEach(key => {
      expect(key).not.toMatch(/^teacher_/);
    });
  });

  it('shows actions and questions after offer set returns', async () => {
    global.fetch = jest.fn().mockResolvedValue({ ok: true, json: async () => OFFER_SET });
    await render(<PhraseSelectionReaderSheet {...makeProps()} />);

    await selectPhrase(0, 16);
    fireEvent.press(screen.getByText('Use selected phrase'));

    await waitFor(() => {
      screen.getByText('Elaborate');
      screen.getByText("What is Ohm's law?");
    });
  });

  /**
   * Organic-First invariant — canon:
   * Selected choice fires outcome:"selected" and triggers onBranchCreated.
   */
  it('selected option fires choices endpoint with outcome:selected and calls onBranchCreated', async () => {
    global.fetch = jest
      .fn()
      .mockResolvedValueOnce({ ok: true, json: async () => OFFER_SET })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ child_node_id: 'child-1' }) });

    const props = makeProps();
    await render(<PhraseSelectionReaderSheet {...props} />);

    await selectPhrase(0, 16);
    fireEvent.press(screen.getByText('Use selected phrase'));
    await waitFor(() => screen.getByText('Elaborate'));

    fireEvent.press(screen.getByText('Elaborate'));

    await waitFor(() => {
      const calls = (global.fetch as jest.Mock).mock.calls;
      expect(calls).toHaveLength(2);
      const [choiceUrl, choiceOpts] = calls[1];
      expect(choiceUrl).toContain('/v1/student/offer-sets/offer-1/choices');
      const body = JSON.parse(choiceOpts.body as string);
      expect(body.outcome).toBe('selected');
      expect(props.onBranchCreated).toHaveBeenCalledWith('child-1');
    });
  });

  /**
   * Organic-First invariant — canon:
   * Dismissed offer fires outcome:"dismissed"; does NOT create a branch.
   */
  it('Close with active offer fires choices endpoint with outcome:dismissed (Organic-First)', async () => {
    global.fetch = jest
      .fn()
      .mockResolvedValueOnce({ ok: true, json: async () => OFFER_SET })
      .mockResolvedValueOnce({ ok: true, json: async () => ({}) });

    const props = makeProps();
    await render(<PhraseSelectionReaderSheet {...props} />);

    await selectPhrase(0, 16);
    fireEvent.press(screen.getByText('Use selected phrase'));
    await waitFor(() => screen.getByText('Elaborate'));

    fireEvent.press(screen.getByText('Close'));

    await waitFor(() => {
      const calls = (global.fetch as jest.Mock).mock.calls;
      expect(calls).toHaveLength(2);
      const body = JSON.parse(calls[1][1].body as string);
      expect(body.outcome).toBe('dismissed');
      expect(props.onBranchCreated).not.toHaveBeenCalled();
      expect(props.onClose).toHaveBeenCalled();
    });
  });

  it('Close without active offer calls onClose only — no fetch (Organic-First)', async () => {
    global.fetch = jest.fn();
    const props = makeProps();
    await render(<PhraseSelectionReaderSheet {...props} />);

    fireEvent.press(screen.getByText('Close'));

    await waitFor(() => expect(props.onClose).toHaveBeenCalled());
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('handles a network failure while requesting phrase options', async () => {
    global.fetch = jest.fn().mockRejectedValue(new Error('Network error'));
    const props = makeProps();
    await render(<PhraseSelectionReaderSheet {...props} />);

    await selectPhrase(0, 16);
    fireEvent.press(screen.getByText('Use selected phrase'));

    await waitFor(() => screen.getByText(/phrase options failed/));
    expect(props.onBranchCreated).not.toHaveBeenCalled();
  });

  it('handles a network failure while creating a branch', async () => {
    global.fetch = jest
      .fn()
      .mockResolvedValueOnce({ ok: true, json: async () => OFFER_SET })
      .mockRejectedValueOnce(new Error('Network error'));

    const props = makeProps();
    await render(<PhraseSelectionReaderSheet {...props} />);

    await selectPhrase(0, 16);
    fireEvent.press(screen.getByText('Use selected phrase'));
    await waitFor(() => screen.getByText('Elaborate'));

    fireEvent.press(screen.getByText('Elaborate'));

    await waitFor(() => screen.getByText(/branch failed/));
    expect(props.onBranchCreated).not.toHaveBeenCalled();
  });

  it('closes the modal even if the dismiss request fails', async () => {
    global.fetch = jest
      .fn()
      .mockResolvedValueOnce({ ok: true, json: async () => OFFER_SET })
      .mockRejectedValueOnce(new Error('Network error'));

    const props = makeProps();
    await render(<PhraseSelectionReaderSheet {...props} />);

    await selectPhrase(0, 16);
    fireEvent.press(screen.getByText('Use selected phrase'));
    await waitFor(() => screen.getByText('Elaborate'));

    fireEvent.press(screen.getByText('Close'));

    await waitFor(() => expect(props.onClose).toHaveBeenCalled());
    expect(props.onBranchCreated).not.toHaveBeenCalled();
  });
});
