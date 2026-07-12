import type { Point } from './coordinateSystem';

export interface PositionAcknowledgement {
  nodeId: string;
  position: Point;
}

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

interface PositionIntent {
  intentId: number;
  position: Point;
}

interface InternalNodeState {
  baseline: Point | null;
  acknowledged: Point | null;
  visible: Point | null;
  status: PositionWriteStatus;
  queue: PositionIntent[];
  error: unknown | null;
}

export interface NodePositionCoordinator {
  setHydratedBaseline(nodeId: string, position: Point): void;
  enqueue(nodeId: string, position: Point): void;
  retry(nodeId: string): boolean;
  retryFailed(): number;
  getNodeState(nodeId: string): NodePositionState;
  getSnapshot(): NodePositionSnapshot;
  subscribe(listener: () => void): () => void;
  dispose(): void;
}

export function createNodePositionCoordinator({ write }: { write: PositionWrite }): NodePositionCoordinator {
  const nodes = new Map<string, InternalNodeState>();
  let nextIntentId = 1;
  let generation = 1;
  let active = true;
  const listeners = new Set<() => void>();
  let snapshot: NodePositionSnapshot = Object.freeze({
    visiblePositions: Object.freeze({}),
    failedNodeIds: Object.freeze([]),
  });

  function publish() {
    if (!active) return;
    const visiblePositions: Record<string, Point> = {};
    const failedNodeIds: string[] = [];
    for (const [nodeId, state] of nodes) {
      if (state.visible) visiblePositions[nodeId] = { ...state.visible };
      if (state.status === 'failed') failedNodeIds.push(nodeId);
    }
    snapshot = Object.freeze({
      visiblePositions: Object.freeze(visiblePositions),
      failedNodeIds: Object.freeze(failedNodeIds),
    });
    for (const listener of listeners) listener();
  }

  function stateFor(nodeId: string): InternalNodeState {
    let state = nodes.get(nodeId);
    if (!state) {
      state = {
        baseline: null,
        acknowledged: null,
        visible: null,
        status: 'idle',
        queue: [],
        error: null,
      };
      nodes.set(nodeId, state);
    }
    return state;
  }

  function dispatchHead(nodeId: string, state: InternalNodeState) {
    if (!active || state.status !== 'idle' || state.queue.length === 0) return;
    const intent = state.queue[0];
    const dispatchGeneration = generation;
    state.status = 'writing';
    state.error = null;

    let request: Promise<PositionAcknowledgement>;
    try {
      request = write(nodeId, intent.position);
    } catch (error) {
      failHead(nodeId, intent.intentId, dispatchGeneration, error);
      return;
    }
    request.then(
      (acknowledgement) => acknowledgeHead(nodeId, intent.intentId, dispatchGeneration, acknowledgement),
      (error) => failHead(nodeId, intent.intentId, dispatchGeneration, error),
    );
  }

  function acknowledgeHead(
    nodeId: string,
    intentId: number,
    dispatchGeneration: number,
    acknowledgement: PositionAcknowledgement,
  ) {
    if (!active || dispatchGeneration !== generation) return;
    const state = nodes.get(nodeId);
    if (!state || state.status !== 'writing' || state.queue[0]?.intentId !== intentId) return;

    state.queue.shift();
    state.acknowledged = { ...acknowledgement.position };
    state.status = 'idle';
    state.error = null;
    state.visible = state.queue.length > 0
      ? { ...state.queue[state.queue.length - 1].position }
      : { ...acknowledgement.position };
    dispatchHead(nodeId, state);
    publish();
  }

  function failHead(nodeId: string, intentId: number, dispatchGeneration: number, error: unknown) {
    if (!active || dispatchGeneration !== generation) return;
    const state = nodes.get(nodeId);
    if (!state || state.status !== 'writing' || state.queue[0]?.intentId !== intentId) return;

    state.status = 'failed';
    state.error = error;
    state.visible = state.queue.length > 1
      ? { ...state.queue[state.queue.length - 1].position }
      : copyPoint(state.acknowledged ?? state.baseline ?? state.visible);
    publish();
  }

  function retryNode(nodeId: string): boolean {
    if (!active) return false;
    const state = nodes.get(nodeId);
    if (!state || state.status !== 'failed' || state.queue.length === 0) return false;
    state.status = 'idle';
    state.error = null;
    state.visible = { ...state.queue[state.queue.length - 1].position };
    dispatchHead(nodeId, state);
    publish();
    return true;
  }

  return {
    setHydratedBaseline(nodeId, position) {
      if (!active) return;
      const state = stateFor(nodeId);
      if (pointsEqual(state.baseline, position)) return;
      state.baseline = { ...position };
      if (state.acknowledged === null && state.queue.length === 0) {
        state.visible = { ...position };
      }
      publish();
    },

    enqueue(nodeId, position) {
      if (!active) return;
      const state = stateFor(nodeId);
      state.queue.push({ intentId: nextIntentId++, position: { ...position } });
      state.visible = { ...position };
      dispatchHead(nodeId, state);
      publish();
    },

    retry(nodeId) {
      return retryNode(nodeId);
    },

    retryFailed() {
      let retried = 0;
      for (const nodeId of snapshot.failedNodeIds) {
        if (retryNode(nodeId)) retried += 1;
      }
      return retried;
    },

    getNodeState(nodeId) {
      const state = nodes.get(nodeId);
      if (!state) {
        return { baseline: null, acknowledged: null, visible: null, status: 'idle', queuedCount: 0, error: null };
      }
      return {
        baseline: copyPoint(state.baseline),
        acknowledged: copyPoint(state.acknowledged),
        visible: copyPoint(state.visible),
        status: state.status,
        queuedCount: state.queue.length,
        error: state.error,
      };
    },

    getSnapshot() {
      return snapshot;
    },

    subscribe(listener) {
      if (!active) return () => undefined;
      listeners.add(listener);
      return () => listeners.delete(listener);
    },

    dispose() {
      active = false;
      generation += 1;
      listeners.clear();
    },
  };
}

function copyPoint(point: Point | null): Point | null {
  return point ? { ...point } : null;
}

function pointsEqual(left: Point | null, right: Point): boolean {
  return left?.x === right.x && left?.y === right.y;
}
