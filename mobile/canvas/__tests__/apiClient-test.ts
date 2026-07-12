import { patchNodePosition } from '../apiClient';

describe('canvas position API client', () => {
  const originalFetch = globalThis.fetch;

  afterEach(() => {
    globalThis.fetch = originalFetch;
    jest.clearAllMocks();
  });

  it('returns a checked acknowledgement for a successful PATCH', async () => {
    globalThis.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ node_id: 'node-1', position_x: 23, position_y: 38 }),
    }) as unknown as typeof fetch;

    await expect(patchNodePosition(
      'http://localhost:8000',
      'session-1',
      'node-1',
      'token-1',
      { x: 23, y: 38 },
    )).resolves.toEqual({ nodeId: 'node-1', position: { x: 23, y: 38 } });

    expect(globalThis.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/v1/student/sessions/session-1/nodes/node-1',
      expect.objectContaining({
        method: 'PATCH',
        body: JSON.stringify({ position_x: 23, position_y: 38 }),
      }),
    );
  });

  it('rejects network, HTTP, and malformed acknowledgements', async () => {
    globalThis.fetch = jest.fn()
      .mockRejectedValueOnce(new Error('offline'))
      .mockResolvedValueOnce({ ok: false, status: 503 })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ node_id: 'wrong-node', position_x: 1, position_y: 2 }),
      }) as unknown as typeof fetch;

    await expect(patchNodePosition('x', 's', 'n', undefined, { x: 1, y: 2 }))
      .rejects.toThrow('offline');
    await expect(patchNodePosition('x', 's', 'n', undefined, { x: 1, y: 2 }))
      .rejects.toThrow('503');
    await expect(patchNodePosition('x', 's', 'n', undefined, { x: 1, y: 2 }))
      .rejects.toThrow(/acknowledgement/i);
  });

  it('rejects non-finite coordinates before issuing a request', async () => {
    globalThis.fetch = jest.fn() as unknown as typeof fetch;

    await expect(patchNodePosition('x', 's', 'n', undefined, { x: Number.NaN, y: 2 }))
      .rejects.toThrow(/finite/i);
    expect(globalThis.fetch).not.toHaveBeenCalled();
  });
});
