import type { Point } from './coordinateSystem';

export interface PositionAcknowledgement { nodeId: string; position: Point }
export type PositionWrite = (nodeId: string, position: Point) => Promise<PositionAcknowledgement>;
export type PositionWriteStatus = 'idle' | 'writing' | 'failed';

export interface NodePositionState {
  baseline: Point | null;
  acknowledged: Point | null;
  visible: Point | null;
  status: PositionWriteStatus;
  queuedCount: number;
  error: unknown | null;
}

export interface NodePositionSnapshot {
  visiblePositions: Readonly<Record<string, Point>>;
  failedNodeIds: readonly string[];
}

interface Intent { id: number; position: Point }
interface InternalState {
  baseline: Point | null;
  acknowledged: Point | null;
  visible: Point | null;
  status: PositionWriteStatus;
  queue: Intent[];
  error: unknown | null;
}

export interface NodePositionCoordinator {
  setHydratedBaseline(nodeId: string, position: Point): void;
  enqueue(nodeId: string, position: Point): void;
  retry(nodeId: string): boolean;
  retryFailed(): number;
  removeNode(nodeId: string): void;
  getNodeState(nodeId: string): NodePositionState;
  getSnapshot(): NodePositionSnapshot;
  subscribe(listener: () => void): () => void;
  dispose(): void;
}

export function createNodePositionCoordinator({ write }: { write: PositionWrite }): NodePositionCoordinator {
  const nodes = new Map<string, InternalState>();
  const listeners = new Set<() => void>();
  let nextIntentId = 1;
  let active = true;
  let snapshot: NodePositionSnapshot = { visiblePositions: {}, failedNodeIds: [] };

  const publish = () => {
    if (!active) return;
    const visiblePositions: Record<string, Point> = {};
    const failedNodeIds: string[] = [];
    for (const [nodeId, state] of nodes) {
      if (state.visible) visiblePositions[nodeId] = { ...state.visible };
      if (state.status === 'failed') failedNodeIds.push(nodeId);
    }
    snapshot = { visiblePositions, failedNodeIds };
    for (const listener of listeners) listener();
  };

  const stateFor = (nodeId: string): InternalState => {
    const existing = nodes.get(nodeId);
    if (existing) return existing;
    const created: InternalState = {
      baseline: null, acknowledged: null, visible: null,
      status: 'idle', queue: [], error: null,
    };
    nodes.set(nodeId, created);
    return created;
  };

  const fail = (nodeId: string, intentId: number, error: unknown) => {
    const state = nodes.get(nodeId);
    if (!active || state?.status !== 'writing' || state.queue[0]?.id !== intentId) return;
    state.status = 'failed';
    state.error = error;
    state.visible = copy(state.queue[state.queue.length - 1]?.position ?? state.visible);
    publish();
  };

  const dispatch = (nodeId: string, state: InternalState) => {
    if (!active || state.status !== 'idle' || state.queue.length === 0) return;
    const intent = state.queue[0];
    state.status = 'writing';
    state.error = null;
    let request: Promise<PositionAcknowledgement>;
    try {
      request = write(nodeId, { ...intent.position });
    } catch (error) {
      fail(nodeId, intent.id, error);
      return;
    }
    request.then((ack) => {
      const current = nodes.get(nodeId);
      if (!active || current?.status !== 'writing' || current.queue[0]?.id !== intent.id) return;
      try {
        assertFinitePoint(ack.position);
        if (ack.nodeId !== nodeId) throw new Error('Invalid node position acknowledgement');
      } catch (error) {
        fail(nodeId, intent.id, error);
        return;
      }
      current.queue.shift();
      current.acknowledged = { ...ack.position };
      current.visible = copy(current.queue.at(-1)?.position ?? ack.position);
      current.status = 'idle';
      dispatch(nodeId, current);
      publish();
    }, (error) => fail(nodeId, intent.id, error));
  };

  const retry = (nodeId: string): boolean => {
    const state = nodes.get(nodeId);
    if (!active || state?.status !== 'failed' || state.queue.length === 0) return false;
    state.status = 'idle';
    state.error = null;
    dispatch(nodeId, state);
    publish();
    return true;
  };

  return {
    setHydratedBaseline(nodeId, position) {
      assertFinitePoint(position);
      if (!active) return;
      const state = stateFor(nodeId);
      state.baseline = { ...position };
      if (!state.acknowledged && state.queue.length === 0) state.visible = { ...position };
      publish();
    },
    enqueue(nodeId, position) {
      assertFinitePoint(position);
      if (!active) return;
      const state = stateFor(nodeId);
      state.queue.push({ id: nextIntentId++, position: { ...position } });
      state.visible = { ...position };
      dispatch(nodeId, state);
      publish();
    },
    retry,
    retryFailed() {
      let count = 0;
      for (const nodeId of snapshot.failedNodeIds) if (retry(nodeId)) count += 1;
      return count;
    },
    removeNode(nodeId) {
      if (nodes.delete(nodeId)) publish();
    },
    getNodeState(nodeId) {
      const state = nodes.get(nodeId);
      return state ? {
        baseline: copy(state.baseline), acknowledged: copy(state.acknowledged),
        visible: copy(state.visible), status: state.status,
        queuedCount: state.queue.length, error: state.error,
      } : {
        baseline: null, acknowledged: null, visible: null,
        status: 'idle', queuedCount: 0, error: null,
      };
    },
    getSnapshot: () => snapshot,
    subscribe(listener) { listeners.add(listener); return () => listeners.delete(listener); },
    dispose() { active = false; listeners.clear(); nodes.clear(); },
  };
}

function copy(point: Point | null): Point | null {
  return point ? { ...point } : null;
}

function assertFinitePoint(point: Point): void {
  if (!Number.isFinite(point.x) || !Number.isFinite(point.y)) {
    throw new TypeError('Node position coordinates must be finite');
  }
}
