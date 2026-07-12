jest.mock('react-native-reanimated', () => {
  const { View } = require('react-native');
  return { __esModule: true, default: { View, createAnimatedComponent: (c: any) => c },
    useAnimatedStyle: (worklet: () => unknown) => worklet() };
});

import React from 'react';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react-native';
import { EdgePlusButtons } from '../../canvas/EdgePlusButtons';

function deferred<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((res) => { resolve = res; });
  return { promise, resolve };
}
const shared = (value: number) => ({ value } as any);
const props = { node: { node_id: 'n1', position: { x: 0, y: 0 } }, nodeIdx: 0,
  scaleShared: shared(1), translateXShared: shared(0), translateYShared: shared(0),
  dragNodeIdxShared: shared(-1), dragCurrBXShared: shared(0), dragCurrBYShared: shared(0),
  apiBaseUrl: 'http://localhost:8000', sessionId: 'session-1', threadContextId: 'thread-1' };
const originalFetch = globalThis.fetch;

describe('EdgePlusButtons request lifecycle', () => {
  afterEach(() => { globalThis.fetch = originalFetch; jest.restoreAllMocks(); });

  it('shares one in-flight request across both edge controls', async () => {
    const pending = deferred<any>();
    globalThis.fetch = jest.fn(() => pending.promise) as unknown as typeof fetch;
    const onOfferSet = jest.fn();
    await render(<EdgePlusButtons {...props} onOfferSet={onOfferSet} />);
    fireEvent.press(screen.getByRole('button', { name: 'Explore from left edge' }));
    await waitFor(() => expect(screen.getByText('Loading questions…')).toBeTruthy());
    fireEvent.press(screen.getByRole('button', { name: 'Explore from right edge' }));
    expect(globalThis.fetch).toHaveBeenCalledTimes(1);
    await act(async () => pending.resolve({ ok: true, json: async () => ({ offer_set_id: 'os-1' }) }));
    await waitFor(() => expect(onOfferSet).toHaveBeenCalledTimes(1));
  });

  it('shows neutral retry feedback and keeps retry single-flight', async () => {
    const retry = deferred<any>();
    globalThis.fetch = jest.fn()
      .mockResolvedValueOnce({ ok: false, status: 503, statusText: 'Unavailable' })
      .mockImplementationOnce(() => retry.promise) as unknown as typeof fetch;
    await render(<EdgePlusButtons {...props} />);
    await fireEvent.press(screen.getByRole('button', { name: 'Explore from right edge' }));
    await screen.findByText('Questions could not load. Tap to retry.');
    fireEvent.press(screen.getByRole('button', { name: 'Retry loading questions from right edge' }));
    fireEvent.press(screen.getByRole('button', { name: 'Loading questions' }));
    expect(globalThis.fetch).toHaveBeenCalledTimes(2);
  });
});
