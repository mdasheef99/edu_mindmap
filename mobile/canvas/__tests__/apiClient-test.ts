import { patchNodePosition } from '../apiClient';

describe('canvas api client', () => {
  const originalFetch = globalThis.fetch;

  afterEach(() => {
    globalThis.fetch = originalFetch;
    jest.clearAllMocks();
  });

  it('PATCHes committed node positions to the student node endpoint', () => {
    const mockFetch = jest.fn().mockResolvedValue({ ok: true });
    globalThis.fetch = mockFetch as unknown as typeof fetch;

    patchNodePosition('http://localhost:8000', 'session-1', 'node-1', 'token-1', { x: 23, y: 38 });

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
});
