import { useCallback, useEffect, useMemo, useRef, useSyncExternalStore } from 'react';

import { patchNodePosition } from './apiClient';
import type { Point } from './coordinateSystem';
import { createNodePositionCoordinator } from './nodePositionCoordinator';
import { useMindMapStore } from './store';

interface PositionedNode {
  node_id: string;
  position: Point;
  positionOverridden?: boolean;
}

export interface UseNodePositionWritesArgs {
  nodes: PositionedNode[];
  apiBaseUrl?: string;
  authorizationToken?: string;
  sessionId?: string;
}

export interface UseNodePositionWritesResult {
  visiblePositions: Readonly<Record<string, Point>>;
  failedNodeCount: number;
  enqueuePosition(nodeId: string, position: Point): void;
  retryFailed(): number;
  removeNodes(nodeIds: readonly string[]): void;
}

export function useNodePositionWrites({
  nodes, apiBaseUrl, authorizationToken, sessionId,
}: UseNodePositionWritesArgs): UseNodePositionWritesResult {
  const sessionKey = sessionId ?? '__local_canvas__';
  const credentialsRef = useRef({ apiBaseUrl, authorizationToken });
  credentialsRef.current = { apiBaseUrl, authorizationToken };
  const positionAuthorityByNode = useMindMapStore((state) => state.positionAuthorityByNode);
  const visiblePositions = useMemo(() => {
    const positions: Record<string, Point> = {};
    for (const [nodeId, authority] of Object.entries(positionAuthorityByNode)) {
      positions[nodeId] = authority.position;
    }
    return positions;
  }, [positionAuthorityByNode]);

  const coordinator = useMemo(() => createNodePositionCoordinator({
    write: (nodeId, position) => {
      const credentials = credentialsRef.current;
      if (!credentials.apiBaseUrl || !sessionId) return Promise.resolve({ nodeId, position });
      return patchNodePosition(
        credentials.apiBaseUrl, sessionId, nodeId, credentials.authorizationToken, position,
      );
    },
  }), [sessionId]);

  const snapshot = useSyncExternalStore(
    coordinator.subscribe, coordinator.getSnapshot, coordinator.getSnapshot,
  );

  const positionHydrationKey = nodes.map((node) => [
    node.node_id, node.position.x, node.position.y, node.positionOverridden ?? false,
  ].join(':')).join('|');

  useEffect(() => {
    const store = useMindMapStore.getState();
    store.beginPositionSession(sessionKey);
    for (const node of nodes) {
      coordinator.setHydratedBaseline(node.node_id, node.position);
      useMindMapStore.getState().hydrateNodePosition(
        node.node_id, node.position, node.positionOverridden ?? false,
      );
    }
  }, [coordinator, positionHydrationKey, sessionKey]);

  useEffect(() => () => {
    coordinator.dispose();
    if (useMindMapStore.getState().positionSessionId === sessionKey) {
      useMindMapStore.getState().resetPositionSession();
    }
  }, [coordinator, sessionKey]);

  const enqueuePosition = useCallback((nodeId: string, position: Point) => {
    useMindMapStore.getState().commitNodePosition(nodeId, position);
    coordinator.enqueue(nodeId, position);
  }, [coordinator]);

  const removeNodes = useCallback((nodeIds: readonly string[]) => {
    for (const nodeId of nodeIds) coordinator.removeNode(nodeId);
    useMindMapStore.getState().removeNodePositions(nodeIds);
  }, [coordinator]);

  const currentIds = useMemo(() => new Set(nodes.map((node) => node.node_id)), [nodes]);
  const failedNodeIds = snapshot.failedNodeIds.filter((nodeId) => currentIds.has(nodeId));
  const retryFailed = useCallback(() => {
    let count = 0;
    for (const nodeId of failedNodeIds) if (coordinator.retry(nodeId)) count += 1;
    return count;
  }, [coordinator, failedNodeIds]);

  return {
    visiblePositions, failedNodeCount: failedNodeIds.length,
    enqueuePosition, retryFailed, removeNodes,
  };
}
