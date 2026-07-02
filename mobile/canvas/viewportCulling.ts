/**
 * Viewport culling (M3 SDD §9, §10).
 *
 * Before each Skia render pass, edges whose BOTH endpoints fall outside the board-space
 * viewport box are dropped; only visible edges are drawn. The visible node_id list produced
 * by the same filter populates the viewport_changed payload's visible_node_ids (§10).
 *
 * Board-space viewport box (§9) — the inverse of the §4 seam
 * (boardX = (screenX - translateX) / scale), evaluated at the screen corners so the
 * box stays consistent with rendering under pan/zoom:
 *   minX = -translateX / scale,            maxX = (screenW - translateX) / scale
 *   minY = -translateY / scale,            maxY = (screenH - translateY) / scale
 *
 * Traceability: phase-3-m3-canvas-sdd.md §4, §9, §10.
 */

import { CanvasTransform, Point } from './coordinateSystem';

export interface ScreenSize {
  width: number;
  height: number;
}

export interface BoardViewport {
  minX: number;
  minY: number;
  maxX: number;
  maxY: number;
}

export interface BoardEdge {
  edge_id: string;
  source_node_id: string;
  target_node_id: string;
  edge_kind?: string;
}

/** Board-space rectangle currently visible, per the §9 seam-inverse formula. */
export function computeBoardViewport(
  transform: CanvasTransform,
  screen: ScreenSize,
): BoardViewport {
  return {
    minX: -transform.translateX / transform.scale,
    minY: -transform.translateY / transform.scale,
    maxX: (screen.width - transform.translateX) / transform.scale,
    maxY: (screen.height - transform.translateY) / transform.scale,
  };
}

export function isPointInViewport(point: Point, viewport: BoardViewport): boolean {
  return (
    point.x >= viewport.minX &&
    point.x <= viewport.maxX &&
    point.y >= viewport.minY &&
    point.y <= viewport.maxY
  );
}

/** Keep an edge only if at least one endpoint is inside the viewport box. */
export function cullEdges<T extends BoardEdge>(
  edges: T[],
  nodePositions: Record<string, Point>,
  viewport: BoardViewport,
): T[] {
  return edges.filter((edge) => {
    const source = nodePositions[edge.source_node_id];
    const target = nodePositions[edge.target_node_id];
    const sourceVisible = source !== undefined && isPointInViewport(source, viewport);
    const targetVisible = target !== undefined && isPointInViewport(target, viewport);
    return sourceVisible || targetVisible;
  });
}

/** Node ids whose board position falls inside the viewport box (viewport_changed payload). */
export function visibleNodeIds(
  nodePositions: Record<string, Point>,
  viewport: BoardViewport,
): string[] {
  return Object.entries(nodePositions)
    .filter(([, position]) => isPointInViewport(position, viewport))
    .map(([nodeId]) => nodeId);
}
