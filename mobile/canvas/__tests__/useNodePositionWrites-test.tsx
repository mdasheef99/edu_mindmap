import { act, renderHook, waitFor } from '@testing-library/react-native';

import { useNodePositionWrites } from '../useNodePositionWrites';

function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason?: unknown) => void;
  const promise = new Promise<T>((res, rej) => {
    resolve = res;
    reject = rej;
  });
  return { promise, resolve, reject };
}

const originalFetch = globalThis.fetch;
const nodes = [{ node_id: 'node-1', position: { x: 0, y: 0 } }];

describe('useNodePositionWrites', () => {
  afterEach(() => {
    globalThis.fetch = originalFetch;
    jest.restoreAllMocks();
  });

  it('uses refreshed credentials for later queued writes without rebuilding visible authority', async () => {
    const first = deferred<any>();
    const second = deferred<any>();
    globalThis.fetch = jest.fn().mockReturnValueOnce(first.promise).mockReturnValueOnce(second.promise);
    const { result, rerender } = await renderHook(
      (props: { token: string }) => useNodePositionWrites({
        nodes,
        apiBaseUrl: 'http://localhost:8000',
        authorizationToken: props.token,
        sessionId: 'session-1',
      }),
      { initialProps: { token: 'token-1' } },
    );

    await act(async () => {
      result.current.enqueuePosition('node-1', { x: 10, y: 10 });
      result.current.enqueuePosition('node-1', { x: 20, y: 20 });
    });
    expect((globalThis.fetch as jest.Mock).mock.calls[0][1].headers.Authorization).toBe('Bearer token-1');
    expect(result.current.visiblePositions['node-1']).toEqual({ x: 20, y: 20 });

    await rerender({ token: 'token-2' });
    first.resolve({
      ok: true,
      json: async () => ({ node_id: 'node-1', position_x: 10, position_y: 10 }),
    });
    await waitFor(() => expect(globalThis.fetch).toHaveBeenCalledTimes(2));
    expect((globalThis.fetch as jest.Mock).mock.calls[1][1].headers.Authorization).toBe('Bearer token-2');
  });

  it('keeps queued and acknowledged mounted-session positions above hydration', async () => {
    const pending = deferred<any>();
    globalThis.fetch = jest.fn().mockReturnValue(pending.promise);
    const { result, rerender } = await renderHook(
      (props: { x: number }) => useNodePositionWrites({
        nodes: [{ node_id: 'node-1', position: { x: props.x, y: props.x } }],
        apiBaseUrl: 'http://localhost:8000',
        authorizationToken: 'token-1',
        sessionId: 'session-1',
      }),
      { initialProps: { x: 0 } },
    );

    await act(async () => result.current.enqueuePosition('node-1', { x: 10, y: 10 }));
    await rerender({ x: -5 });
    expect(result.current.visiblePositions['node-1']).toEqual({ x: 10, y: 10 });

    pending.resolve({
      ok: true,
      json: async () => ({ node_id: 'node-1', position_x: 10, position_y: 10 }),
    });
    await waitFor(() => expect(result.current.failedNodeCount).toBe(0));
    await rerender({ x: -10 });
    expect(result.current.visiblePositions['node-1']).toEqual({ x: 10, y: 10 });
  });

  it('aggregates failed nodes and Retry retries each failed head once', async () => {
    globalThis.fetch = jest
      .fn()
      .mockResolvedValueOnce({ ok: false, status: 503 })
      .mockResolvedValueOnce({ ok: false, status: 503 })
      .mockImplementation(() => new Promise(() => undefined));
    const { result } = await renderHook(() => useNodePositionWrites({
      nodes: [
        { node_id: 'node-1', position: { x: 0, y: 0 } },
        { node_id: 'node-2', position: { x: 0, y: 0 } },
      ],
      apiBaseUrl: 'http://localhost:8000',
      authorizationToken: 'token-1',
      sessionId: 'session-1',
    }));

    await act(async () => {
      result.current.enqueuePosition('node-1', { x: 1, y: 1 });
      result.current.enqueuePosition('node-2', { x: 2, y: 2 });
    });
    await waitFor(() => expect(result.current.failedNodeCount).toBe(2));

    await act(async () => expect(result.current.retryFailed()).toBe(2));
    await act(async () => expect(result.current.retryFailed()).toBe(0));
    expect(globalThis.fetch).toHaveBeenCalledTimes(4);
  });
});
