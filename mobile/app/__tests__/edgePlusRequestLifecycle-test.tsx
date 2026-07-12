jest.mock('react-native-reanimated', () => {
  const { View } = require('react-native');
  return {
    __esModule: true,
    default: { View, createAnimatedComponent: (component: any) => component },
    useAnimatedStyle: jest.fn((worklet: () => any) => worklet()),
  };
});

import React from 'react';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react-native';
import { EdgePlusButtons } from '../../canvas/EdgePlusButtons';

function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason?: unknown) => void;
  const promise = new Promise<T>((res, rej) => { resolve = res; reject = rej; });
  return { promise, resolve, reject };
}

const shared = (value: number) => ({ value } as any);
const BASE_PROPS = {
  node: { node_id: 'n1', position: { x: 50, y: 60 } },
  nodeIdx: 0,
  scaleShared: shared(1),
  translateXShared: shared(0),
  translateYShared: shared(0),
  dragNodeIdxShared: shared(-1),
  dragCurrBXShared: shared(0),
  dragCurrBYShared: shared(0),
  apiBaseUrl: 'http://localhost:8000',
  authorizationToken: 'token',
  sessionId: 'session-1',
  threadContextId: 'thread-1',
};

const successResponse = (payload: unknown) => ({
  ok: true,
  status: 200,
  statusText: 'OK',
  json: async () => payload,
} as Response);

describe('EdgePlusButtons request lifecycle', () => {
  const originalFetch = global.fetch;

  afterEach(() => {
    global.fetch = originalFetch;
    jest.restoreAllMocks();
  });

  it('shows immediate busy feedback and shares one in-flight request across both sides', async () => {
    const request = deferred<Response>();
    global.fetch = jest.fn(() => request.promise);
    const onOfferSet = jest.fn();
    await render(<EdgePlusButtons {...BASE_PROPS} onOfferSet={onOfferSet} />);

    await fireEvent.press(screen.getByRole('button', { name: 'Explore from left edge' }));
    await waitFor(() => expect(screen.getByText('Loading questions…')).toBeTruthy());
    expect(global.fetch).toHaveBeenCalledTimes(1);

    await fireEvent.press(screen.getByRole('button', { name: 'Loading questions' }));
    await fireEvent.press(screen.getByRole('button', { name: 'Explore from right edge' }));
    expect(global.fetch).toHaveBeenCalledTimes(1);

    await act(async () => { request.resolve(successResponse({ offer_set_id: 'os-1', options: [] })); });
    await waitFor(() => expect(onOfferSet).toHaveBeenCalledTimes(1));
    expect(onOfferSet.mock.calls[0][0]).toEqual({ offer_set_id: 'os-1', options: [] });
    expect(screen.queryByText('Loading questions…')).toBeNull();
  });

  it.each([
    ['HTTP failure', async (request: ReturnType<typeof deferred<Response>>) => request.resolve({ ok: false, status: 503, statusText: 'Unavailable' } as Response)],
    ['network rejection', async (request: ReturnType<typeof deferred<Response>>) => request.reject(new Error('offline'))],
  ])('clears busy after %s, exposes neutral retry feedback, and keeps retry single-flight', async (_label, completeFailure) => {
    const first = deferred<Response>();
    const retry = deferred<Response>();
    global.fetch = jest.fn()
      .mockImplementationOnce(() => first.promise)
      .mockImplementationOnce(() => retry.promise);
    const onError = jest.fn();
    const onOfferSet = jest.fn();
    await render(<EdgePlusButtons {...BASE_PROPS} onError={onError} onOfferSet={onOfferSet} />);

    await fireEvent.press(screen.getByRole('button', { name: 'Explore from right edge' }));
    await act(async () => { await completeFailure(first); });
    await waitFor(() => expect(screen.getByText('Questions could not load. Tap to retry.')).toBeTruthy());
    expect(onError).toHaveBeenCalledTimes(1);

    await fireEvent.press(screen.getByRole('button', { name: 'Retry loading questions from right edge' }));
    await waitFor(() => expect(screen.getByText('Loading questions…')).toBeTruthy());
    await fireEvent.press(screen.getByRole('button', { name: 'Loading questions' }));
    await fireEvent.press(screen.getByRole('button', { name: 'Explore from left edge' }));
    expect(global.fetch).toHaveBeenCalledTimes(2);

    await act(async () => { retry.resolve(successResponse({ offer_set_id: 'os-retry' })); });
    await waitFor(() => expect(onOfferSet).toHaveBeenCalledTimes(1));
  });

  it('ignores late success and failure after unmount', async () => {
    const success = deferred<Response>();
    const onOfferSet = jest.fn();
    global.fetch = jest.fn(() => success.promise);
    const first = await render(<EdgePlusButtons {...BASE_PROPS} onOfferSet={onOfferSet} />);
    await fireEvent.press(screen.getByRole('button', { name: 'Explore from left edge' }));
    await first.unmount();
    await act(async () => { success.resolve(successResponse({ offer_set_id: 'late' })); });
    expect(onOfferSet).not.toHaveBeenCalled();

    const failure = deferred<Response>();
    const onError = jest.fn();
    global.fetch = jest.fn(() => failure.promise);
    const second = await render(<EdgePlusButtons {...BASE_PROPS} onError={onError} />);
    await fireEvent.press(screen.getByRole('button', { name: 'Explore from left edge' }));
    await second.unmount();
    await act(async () => { failure.reject(new Error('late failure')); });
    expect(onError).not.toHaveBeenCalled();
  });

  it('keeps different node controls independent while each node remains single-flight', async () => {
    const first = deferred<Response>();
    const second = deferred<Response>();
    global.fetch = jest.fn()
      .mockImplementationOnce(() => first.promise)
      .mockImplementationOnce(() => second.promise);
    await render(
      <>
        <EdgePlusButtons {...BASE_PROPS} />
        <EdgePlusButtons {...BASE_PROPS} node={{ node_id: 'n2', position: { x: 100, y: 100 } }} nodeIdx={1} />
      </>,
    );

    const leftButtons = screen.getAllByRole('button', { name: 'Explore from left edge' });
    await fireEvent.press(leftButtons[0]);
    await fireEvent.press(leftButtons[1]);
    await fireEvent.press(leftButtons[0]);
    expect(global.fetch).toHaveBeenCalledTimes(2);
    await act(async () => {
      first.resolve(successResponse({ offer_set_id: 'os-1' }));
      second.resolve(successResponse({ offer_set_id: 'os-2' }));
    });
  });
});
