import { patchNodePosition } from '../apiClient';

describe('canvas api client', () => {
  const originalFetch = globalThis.fetch;

  afterEach(() => {
    globalThis.fetch = originalFetch;
    jest.restoreAllMocks();
  });

  it('PATCHes committed node positions to the student node endpoint', async () => {
    const mockFetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ node_id: 'node-1', position_x: 23, position_y: 38 }),
    });
    globalThis.fetch = mockFetch as unknown as typeof fetch;

    await patchNodePosition('http://localhost:8000', 'session-1', 'node-1', 'token-1', { x: 23, y: 38 });

    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/v1/student/sessions/session-1/nodes/node-1',
      {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Bearer token-1',
        },
        body: JSON.stringify({ position_x: 23, position_y: 38 }),
      },
    );
  });

  it('propagates a network failure to the caller', async () => {
    const failure = new Error('network unavailable');
    globalThis.fetch = jest.fn().mockRejectedValue(failure) as unknown as typeof fetch;

    const result = patchNodePosition(
      'http://localhost:8000',
      'session-1',
      'node-1',
      'token-1',
      { x: 23, y: 38 },
    ) as unknown as Promise<unknown>;

    await expect(result).rejects.toBe(failure);
  });

  it('rejects a non-2xx position response', async () => {
    globalThis.fetch = jest.fn().mockResolvedValue({ ok: false, status: 503 }) as unknown as typeof fetch;

    const result = patchNodePosition(
      'http://localhost:8000',
      'session-1',
      'node-1',
      'token-1',
      { x: 23, y: 38 },
    ) as unknown as Promise<unknown>;

    await expect(result).rejects.toBeDefined();
  });

  it('returns the accepted position acknowledgement', async () => {
    globalThis.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ node_id: 'node-1', position_x: 23, position_y: 38 }),
    }) as unknown as typeof fetch;

    const result = patchNodePosition(
      'http://localhost:8000',
      'session-1',
      'node-1',
      'token-1',
      { x: 23, y: 38 },
    ) as unknown as Promise<unknown>;

    await expect(result).resolves.toEqual({ nodeId: 'node-1', position: { x: 23, y: 38 } });
  });
});
