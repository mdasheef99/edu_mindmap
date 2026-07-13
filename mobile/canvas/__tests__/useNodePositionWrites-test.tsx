import { act, renderHook, waitFor } from '@testing-library/react-native';

import { useMindMapStore } from '../store';
import { useNodePositionWrites } from '../useNodePositionWrites';

function deferred<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((res) => { resolve = res; });
  return { promise, resolve };
}

const originalFetch = globalThis.fetch;

describe('useNodePositionWrites', () => {
  beforeEach(() => useMindMapStore.getState().resetPositionSession());
  afterEach(() => {
    globalThis.fetch = originalFetch;
    jest.restoreAllMocks();
  });

  it('keeps a failed local commit visible and exposes one retry action', async () => {
    globalThis.fetch = jest.fn()
      .mockResolvedValueOnce({ ok: false, status: 503 })
      .mockImplementation(() => new Promise(() => undefined)) as unknown as typeof fetch;
    const { result } = await renderHook(() => useNodePositionWrites({
      nodes: [{ node_id: 'node-1', position: { x: 0, y: 0 }, positionOverridden: false }],
      apiBaseUrl: 'http://localhost:8000', sessionId: 'session-1',
    }));

    await act(async () => result.current.enqueuePosition('node-1', { x: 10, y: 10 }));
    await waitFor(() => expect(result.current.failedNodeCount).toBe(1));
    expect(result.current.visiblePositions['node-1']).toEqual({ x: 10, y: 10 });
    await act(async () => expect(result.current.retryFailed()).toBe(1));
  });

  it('discards stale completion when the session changes', async () => {
    const pending = deferred<any>();
    globalThis.fetch = jest.fn().mockReturnValue(pending.promise) as unknown as typeof fetch;
    const { result, rerender } = await renderHook(
      ({ sessionId }) => useNodePositionWrites({
        nodes: [{ node_id: 'node-1', position: { x: 0, y: 0 }, positionOverridden: false }],
        apiBaseUrl: 'http://localhost:8000', sessionId,
      }),
      { initialProps: { sessionId: 'session-1' } },
    );
    await act(async () => result.current.enqueuePosition('node-1', { x: 10, y: 10 }));

    await rerender({ sessionId: 'session-2' });
    pending.resolve({ ok: true, json: async () => ({ node_id: 'node-1', position_x: 10, position_y: 10 }) });
    await act(async () => { await Promise.resolve(); });

    expect(useMindMapStore.getState().positionSessionId).toBe('session-2');
    expect(result.current.visiblePositions['node-1']).toEqual({ x: 0, y: 0 });
  });

  it('removes deleted positions and prevents retrying their failed writes', async () => {
    globalThis.fetch = jest.fn().mockResolvedValue({ ok: false, status: 503 }) as unknown as typeof fetch;
    const { result } = await renderHook(() => useNodePositionWrites({
      nodes: [{ node_id: 'node-1', position: { x: 0, y: 0 }, positionOverridden: false }],
      apiBaseUrl: 'http://localhost:8000', sessionId: 'session-1',
    }));
    await act(async () => result.current.enqueuePosition('node-1', { x: 10, y: 10 }));
    await waitFor(() => expect(result.current.failedNodeCount).toBe(1));

    await act(async () => result.current.removeNodes(['node-1']));
    expect(result.current.failedNodeCount).toBe(0);
    expect(result.current.visiblePositions['node-1']).toBeUndefined();
    expect(result.current.retryFailed()).toBe(0);
  });
});
