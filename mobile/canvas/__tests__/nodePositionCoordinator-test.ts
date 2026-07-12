import { createNodePositionCoordinator } from '../nodePositionCoordinator';

function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason?: unknown) => void;
  const promise = new Promise<T>((res, rej) => { resolve = res; reject = rej; });
  return { promise, resolve, reject };
}

describe('node position coordinator', () => {
  it('serializes writes FIFO per node while allowing different nodes concurrently', async () => {
    const first = deferred<any>();
    const write = jest.fn()
      .mockReturnValueOnce(first.promise)
      .mockResolvedValueOnce({ nodeId: 'node-1', position: { x: 2, y: 2 } })
      .mockResolvedValueOnce({ nodeId: 'node-2', position: { x: 8, y: 8 } });
    const coordinator = createNodePositionCoordinator({ write });

    coordinator.enqueue('node-1', { x: 1, y: 1 });
    coordinator.enqueue('node-1', { x: 2, y: 2 });
    coordinator.enqueue('node-2', { x: 8, y: 8 });

    expect(write).toHaveBeenCalledTimes(2);
    expect(coordinator.getSnapshot().visiblePositions['node-1']).toEqual({ x: 2, y: 2 });
    first.resolve({ nodeId: 'node-1', position: { x: 1, y: 1 } });
    await Promise.resolve();
    await Promise.resolve();
    expect(write.mock.calls.map(([nodeId, point]) => [nodeId, point])).toEqual([
      ['node-1', { x: 1, y: 1 }],
      ['node-2', { x: 8, y: 8 }],
      ['node-1', { x: 2, y: 2 }],
    ]);
  });

  it('keeps the latest intent visible and retryable when the head fails', async () => {
    const failed = new Error('offline');
    const write = jest.fn()
      .mockRejectedValueOnce(failed)
      .mockResolvedValueOnce({ nodeId: 'node-1', position: { x: 10, y: 10 } });
    const coordinator = createNodePositionCoordinator({ write });
    coordinator.setHydratedBaseline('node-1', { x: 0, y: 0 });

    coordinator.enqueue('node-1', { x: 10, y: 10 });
    await Promise.resolve();
    await Promise.resolve();

    expect(coordinator.getNodeState('node-1')).toMatchObject({
      visible: { x: 10, y: 10 }, status: 'failed', error: failed,
    });
    expect(coordinator.retry('node-1')).toBe(true);
    await Promise.resolve();
    expect(write).toHaveBeenCalledTimes(2);
  });

  it('rejects invalid intent and acknowledgement coordinates', async () => {
    const coordinator = createNodePositionCoordinator({
      write: jest.fn().mockResolvedValue({
        nodeId: 'node-1', position: { x: Number.POSITIVE_INFINITY, y: 1 },
      }),
    });

    expect(() => coordinator.enqueue('node-1', { x: Number.NaN, y: 1 })).toThrow(/finite/i);
    coordinator.enqueue('node-1', { x: 1, y: 1 });
    await Promise.resolve();
    await Promise.resolve();
    expect(coordinator.getNodeState('node-1').status).toBe('failed');
  });

  it('invalidates queued and in-flight writes when a node is removed', async () => {
    const pending = deferred<any>();
    const write = jest.fn().mockReturnValue(pending.promise);
    const coordinator = createNodePositionCoordinator({ write });
    coordinator.enqueue('node-1', { x: 1, y: 1 });
    coordinator.enqueue('node-1', { x: 2, y: 2 });

    coordinator.removeNode('node-1');
    pending.resolve({ nodeId: 'node-1', position: { x: 1, y: 1 } });
    await Promise.resolve();
    await Promise.resolve();

    expect(coordinator.getSnapshot().visiblePositions['node-1']).toBeUndefined();
    expect(coordinator.retry('node-1')).toBe(false);
    expect(write).toHaveBeenCalledTimes(1);
  });
});
