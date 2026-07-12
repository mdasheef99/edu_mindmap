import {
  createNodePositionCoordinator,
  type PositionAcknowledgement,
} from '../nodePositionCoordinator';

type Point = { x: number; y: number };

function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason?: unknown) => void;
  const promise = new Promise<T>((res, rej) => {
    resolve = res;
    reject = rej;
  });
  return { promise, resolve, reject };
}

function acknowledgement(nodeId: string, position: Point): PositionAcknowledgement {
  return { nodeId, position };
}

async function flushPromises() {
  await Promise.resolve();
  await Promise.resolve();
}

describe('node position coordinator', () => {
  it('keeps snapshot identity stable until a meaningful transition', () => {
    const coordinator = createNodePositionCoordinator({ write: jest.fn() });
    const listener = jest.fn();
    const unsubscribe = coordinator.subscribe(listener);
    const initial = coordinator.getSnapshot();

    expect(coordinator.getSnapshot()).toBe(initial);
    coordinator.setHydratedBaseline('node-1', { x: 0, y: 0 });
    const hydrated = coordinator.getSnapshot();
    expect(hydrated).not.toBe(initial);
    expect(listener).toHaveBeenCalledTimes(1);

    coordinator.setHydratedBaseline('node-1', { x: 0, y: 0 });
    expect(coordinator.getSnapshot()).toBe(hydrated);
    expect(listener).toHaveBeenCalledTimes(1);

    unsubscribe();
    coordinator.setHydratedBaseline('node-2', { x: 2, y: 2 });
    expect(listener).toHaveBeenCalledTimes(1);
  });

  it('dispatches every completed drag FIFO with one write per node in flight', async () => {
    const first = deferred<PositionAcknowledgement>();
    const second = deferred<PositionAcknowledgement>();
    const third = deferred<PositionAcknowledgement>();
    const write = jest
      .fn()
      .mockReturnValueOnce(first.promise)
      .mockReturnValueOnce(second.promise)
      .mockReturnValueOnce(third.promise);
    const coordinator = createNodePositionCoordinator({ write });
    coordinator.setHydratedBaseline('node-1', { x: 0, y: 0 });

    coordinator.enqueue('node-1', { x: 10, y: 10 });
    coordinator.enqueue('node-1', { x: 20, y: 20 });
    coordinator.enqueue('node-1', { x: 30, y: 30 });

    expect(write).toHaveBeenCalledTimes(1);
    expect(coordinator.getNodeState('node-1')).toMatchObject({
      visible: { x: 30, y: 30 }, status: 'writing', queuedCount: 3,
    });

    first.resolve(acknowledgement('node-1', { x: 10, y: 10 }));
    await flushPromises();
    expect(write).toHaveBeenCalledTimes(2);
    expect(write.mock.calls[1]).toEqual(['node-1', { x: 20, y: 20 }]);

    second.resolve(acknowledgement('node-1', { x: 20, y: 20 }));
    await flushPromises();
    expect(write).toHaveBeenCalledTimes(3);
    expect(write.mock.calls[2]).toEqual(['node-1', { x: 30, y: 30 }]);

    third.resolve(acknowledgement('node-1', { x: 30, y: 30 }));
    await flushPromises();
    expect(coordinator.getNodeState('node-1')).toMatchObject({
      acknowledged: { x: 30, y: 30 }, visible: { x: 30, y: 30 }, status: 'idle', queuedCount: 0,
    });
  });

  it('allows different nodes to persist independently', () => {
    const writes = new Map<string, ReturnType<typeof deferred<PositionAcknowledgement>>>();
    const write = jest.fn((nodeId: string) => {
      const pending = deferred<PositionAcknowledgement>();
      writes.set(nodeId, pending);
      return pending.promise;
    });
    const coordinator = createNodePositionCoordinator({ write });

    coordinator.enqueue('node-1', { x: 10, y: 10 });
    coordinator.enqueue('node-2', { x: 20, y: 20 });

    expect(write).toHaveBeenCalledTimes(2);
    expect(writes.size).toBe(2);
  });

  it('keeps newer intent visible when an older queue head fails', async () => {
    const first = deferred<PositionAcknowledgement>();
    const write = jest.fn().mockReturnValue(first.promise);
    const coordinator = createNodePositionCoordinator({ write });
    coordinator.setHydratedBaseline('node-1', { x: 0, y: 0 });
    coordinator.enqueue('node-1', { x: 10, y: 10 });
    coordinator.enqueue('node-1', { x: 20, y: 20 });

    first.reject(new Error('offline'));
    await flushPromises();

    expect(coordinator.getNodeState('node-1')).toMatchObject({
      visible: { x: 20, y: 20 }, status: 'failed', queuedCount: 2,
    });
    expect(write).toHaveBeenCalledTimes(1);
  });

  it('rolls back a failed latest intent to acknowledgement or hydrated baseline', async () => {
    const first = deferred<PositionAcknowledgement>();
    const second = deferred<PositionAcknowledgement>();
    const write = jest.fn().mockReturnValueOnce(first.promise).mockReturnValueOnce(second.promise);
    const coordinator = createNodePositionCoordinator({ write });
    coordinator.setHydratedBaseline('node-1', { x: 0, y: 0 });
    coordinator.enqueue('node-1', { x: 10, y: 10 });
    first.resolve(acknowledgement('node-1', { x: 10, y: 10 }));
    await flushPromises();

    coordinator.enqueue('node-1', { x: 20, y: 20 });
    second.reject(new Error('offline'));
    await flushPromises();
    expect(coordinator.getNodeState('node-1')).toMatchObject({
      visible: { x: 10, y: 10 }, acknowledged: { x: 10, y: 10 }, status: 'failed',
    });

    const baselineFailure = deferred<PositionAcknowledgement>();
    const baselineCoordinator = createNodePositionCoordinator({
      write: jest.fn().mockReturnValue(baselineFailure.promise),
    });
    baselineCoordinator.setHydratedBaseline('node-2', { x: 5, y: 5 });
    baselineCoordinator.enqueue('node-2', { x: 15, y: 15 });
    baselineFailure.reject(new Error('offline'));
    await flushPromises();
    expect(baselineCoordinator.getNodeState('node-2')).toMatchObject({
      visible: { x: 5, y: 5 }, acknowledged: null, status: 'failed',
    });
  });

  it('retries the failed head once and resumes FIFO without duplicating later writes', async () => {
    const failed = deferred<PositionAcknowledgement>();
    const retry = deferred<PositionAcknowledgement>();
    const later = deferred<PositionAcknowledgement>();
    const write = jest
      .fn()
      .mockReturnValueOnce(failed.promise)
      .mockReturnValueOnce(retry.promise)
      .mockReturnValueOnce(later.promise);
    const coordinator = createNodePositionCoordinator({ write });
    coordinator.enqueue('node-1', { x: 10, y: 10 });
    coordinator.enqueue('node-1', { x: 20, y: 20 });
    failed.reject(new Error('offline'));
    await flushPromises();

    expect(coordinator.retry('node-1')).toBe(true);
    expect(coordinator.retry('node-1')).toBe(false);
    expect(write).toHaveBeenCalledTimes(2);
    retry.resolve(acknowledgement('node-1', { x: 10, y: 10 }));
    await flushPromises();
    expect(write).toHaveBeenCalledTimes(3);
    expect(write.mock.calls[2]).toEqual(['node-1', { x: 20, y: 20 }]);
  });

  it('does not let hydration replace mounted-session acknowledged or queued authority', async () => {
    const pending = deferred<PositionAcknowledgement>();
    const coordinator = createNodePositionCoordinator({ write: jest.fn().mockReturnValue(pending.promise) });
    coordinator.setHydratedBaseline('node-1', { x: 0, y: 0 });
    coordinator.enqueue('node-1', { x: 10, y: 10 });
    pending.resolve(acknowledgement('node-1', { x: 10, y: 10 }));
    await flushPromises();

    coordinator.setHydratedBaseline('node-1', { x: 0, y: 0 });
    expect(coordinator.getNodeState('node-1').visible).toEqual({ x: 10, y: 10 });

    const queued = deferred<PositionAcknowledgement>();
    const queuedCoordinator = createNodePositionCoordinator({ write: jest.fn().mockReturnValue(queued.promise) });
    queuedCoordinator.setHydratedBaseline('node-2', { x: 1, y: 1 });
    queuedCoordinator.enqueue('node-2', { x: 2, y: 2 });
    queuedCoordinator.setHydratedBaseline('node-2', { x: 1, y: 1 });
    expect(queuedCoordinator.getNodeState('node-2').visible).toEqual({ x: 2, y: 2 });
  });

  it('ignores late completions after disposal', async () => {
    const pending = deferred<PositionAcknowledgement>();
    const coordinator = createNodePositionCoordinator({ write: jest.fn().mockReturnValue(pending.promise) });
    coordinator.setHydratedBaseline('node-1', { x: 0, y: 0 });
    coordinator.enqueue('node-1', { x: 10, y: 10 });
    coordinator.dispose();

    pending.resolve(acknowledgement('node-1', { x: 10, y: 10 }));
    await flushPromises();

    expect(coordinator.getNodeState('node-1')).toMatchObject({
      acknowledged: null, visible: { x: 10, y: 10 }, status: 'writing',
    });
  });

  it('aggregates failed nodes and retries each failed head once', async () => {
    const firstA = deferred<PositionAcknowledgement>();
    const firstB = deferred<PositionAcknowledgement>();
    const retryA = deferred<PositionAcknowledgement>();
    const retryB = deferred<PositionAcknowledgement>();
    const pendingByNode: Record<string, Array<ReturnType<typeof deferred<PositionAcknowledgement>>>> = {
      'node-1': [firstA, retryA],
      'node-2': [firstB, retryB],
    };
    const write = jest.fn((nodeId: string) => pendingByNode[nodeId].shift()!.promise);
    const coordinator = createNodePositionCoordinator({ write });
    coordinator.enqueue('node-1', { x: 1, y: 1 });
    coordinator.enqueue('node-2', { x: 2, y: 2 });
    firstA.reject(new Error('offline'));
    firstB.reject(new Error('offline'));
    await flushPromises();

    expect(coordinator.getSnapshot().failedNodeIds).toEqual(['node-1', 'node-2']);
    expect(coordinator.retryFailed()).toBe(2);
    expect(coordinator.retryFailed()).toBe(0);
    expect(write).toHaveBeenCalledTimes(4);
  });
});
