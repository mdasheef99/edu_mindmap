import { useCallback, useEffect, useMemo, useRef, useSyncExternalStore } from 'react';

import { patchNodePosition } from './apiClient';
import type { Point } from './coordinateSystem';
import { createNodePositionCoordinator } from './nodePositionCoordinator';

interface PositionedNode {
  node_id: string;
  position: Point;
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
}

export function useNodePositionWrites({
  nodes,
  apiBaseUrl,
  authorizationToken,
  sessionId,
}: UseNodePositionWritesArgs): UseNodePositionWritesResult {
  const credentialsRef = useRef({ apiBaseUrl, authorizationToken });
  credentialsRef.current = { apiBaseUrl, authorizationToken };

  const coordinator = useMemo(
    () => createNodePositionCoordinator({
      write: (nodeId, position) => {
        const current = credentialsRef.current;
        if (!current.apiBaseUrl || !sessionId) {
          return Promise.resolve({ nodeId, position });
        }
        return patchNodePosition(
          current.apiBaseUrl,
          sessionId,
          nodeId,
          current.authorizationToken,
          position,
        );
      },
    }),
    [sessionId],
  );

  const snapshot = useSyncExternalStore(
    coordinator.subscribe,
    coordinator.getSnapshot,
    coordinator.getSnapshot,
  );

  useEffect(() => {
    for (const node of nodes) {
      coordinator.setHydratedBaseline(node.node_id, node.position);
    }
  }, [coordinator, nodes]);

  useEffect(() => () => coordinator.dispose(), [coordinator]);

  const currentNodeIds = useMemo(() => new Set(nodes.map((node) => node.node_id)), [nodes]);
  const failedNodeIds = useMemo(
    () => snapshot.failedNodeIds.filter((nodeId) => currentNodeIds.has(nodeId)),
    [snapshot.failedNodeIds, currentNodeIds],
  );

  const enqueuePosition = useCallback(
    (nodeId: string, position: Point) => coordinator.enqueue(nodeId, position),
    [coordinator],
  );
  const retryFailed = useCallback(() => {
    let retried = 0;
    for (const nodeId of failedNodeIds) {
      if (coordinator.retry(nodeId)) retried += 1;
    }
    return retried;
  }, [coordinator, failedNodeIds]);

  return {
    visiblePositions: snapshot.visiblePositions,
    failedNodeCount: failedNodeIds.length,
    enqueuePosition,
    retryFailed,
  };
}
