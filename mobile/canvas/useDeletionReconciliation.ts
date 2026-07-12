/**
 * useDeletionReconciliation — soft-deletion filter for the canvas (M3-C SDD §6).
 *
 * Receives the full NodeDeletionResponse and atomically filters the deleted node/edge ids
 * from the render set so the canvas matches the server snapshot after a cascade delete.
 */

import { useCallback, useMemo, useState } from 'react';
import type { CanvasNode, CanvasEdge } from './SkiaCanvas';
import type { NodeDeletionResponse } from './NodeToolbar';

export function useDeletionReconciliation(
  nodes: CanvasNode[],
  edges: CanvasEdge[],
  onAfterDelete?: () => void,
) {
  const [deletedNodeIds, setDeletedNodeIds] = useState<Set<string>>(() => new Set());
  const [deletedEdgeIds, setDeletedEdgeIds] = useState<Set<string>>(() => new Set());

  const handleDeleted = useCallback(
    (result: NodeDeletionResponse) => {
      setDeletedNodeIds((prev) => new Set([...prev, ...result.deleted_node_ids]));
      setDeletedEdgeIds((prev) => new Set([...prev, ...result.deleted_edge_ids]));
      onAfterDelete?.();
    },
    [onAfterDelete],
  );

  const liveNodes = useMemo(
    () => nodes.filter((n) => !deletedNodeIds.has(n.node_id)),
    [nodes, deletedNodeIds],
  );

  const liveEdges = useMemo(
    () =>
      edges.filter(
        (e) =>
          !deletedEdgeIds.has(e.edge_id) &&
          !deletedNodeIds.has(e.source_node_id) &&
          !deletedNodeIds.has(e.target_node_id),
      ),
    [edges, deletedEdgeIds, deletedNodeIds],
  );

  return { liveNodes, liveEdges, handleDeleted };
}
