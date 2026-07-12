/**
 * useCanvasRenderData — consolidated render-pipeline memo (M3 SDD §9).
 *
 * Builds node positions, the board-space viewport, the visible-node id set, and the
 * visible-edge subset in one place so the SkiaCanvas orchestrator only consumes the
 * resulting render data.
 */

import { useMemo } from 'react';
import { computeBoardViewport, cullEdges, visibleNodeIds, ScreenSize } from './viewportCulling';
import type { CanvasNode, CanvasEdge } from './SkiaCanvas';
import type { CanvasTransform, Point } from './coordinateSystem';
import type { LiveDragOverride } from './useLiveDragOverride';

export interface CanvasRenderData {
  nodePositions: Record<string, Point>;
  viewport: ReturnType<typeof computeBoardViewport>;
  visIds: Set<string>;
  visibleEdges: CanvasEdge[];
}

export function useCanvasRenderData(
  liveNodes: CanvasNode[],
  liveEdges: CanvasEdge[],
  liveDragOverride: LiveDragOverride | null,
  transform: CanvasTransform,
  screen: ScreenSize,
): CanvasRenderData {
  const nodePositions = useMemo<Record<string, Point>>(() => {
    const base = Object.fromEntries(liveNodes.map((n) => [n.node_id, n.position]));
    if (liveDragOverride) {
      base[liveDragOverride.nodeId] = { x: liveDragOverride.x, y: liveDragOverride.y };
    }
    return base;
  }, [liveNodes, liveDragOverride]);

  const viewport = useMemo(() => computeBoardViewport(transform, screen), [transform, screen]);

  const visIds = useMemo(
    () => new Set(visibleNodeIds(nodePositions, viewport)),
    [nodePositions, viewport],
  );

  const visibleEdges = useMemo(
    () => cullEdges(liveEdges, nodePositions, viewport),
    [liveEdges, nodePositions, viewport],
  );

  return { nodePositions, viewport, visIds, visibleEdges };
}
