/**
 * Node overlay placement — screen-space anchors for Native View canvas chrome (M3-B SDD §5.2,
 * §5.3). Edge-`+` buttons (F2) sit on the node's left/right vertical-edge midpoints; the action
 * toolbar (F3) anchors above the node's top edge. All conversions go through boardToCanvas
 * (ADR-0013 — no inline seam math in any component); these pure helpers are CI-testable.
 *
 * Node footprint is nodeSize = [width, height] board units, centered on the stored position
 * (default NODE_SIZE = [200, 160], matching hitTestNode and the M3 layout §6).
 *
 * Traceability: phase-3-m3b-canvas-feature-parity-sdd.md §5.2, §5.3; adr-log-02.md ADR-0013;
 * phase-3-m3-canvas-sdd.md §4, §6.
 */

import { boardToCanvas, CanvasTransform, Point } from './coordinateSystem';
import { CHIP_H, CHIP_W } from './chipConstants';

/** Default node footprint in board units (width, height) — shared with hitTestNode. */
export const NODE_SIZE: [number, number] = [CHIP_W, CHIP_H];

export interface OverlayNode {
  node_id: string;
  position: Point;
}

export interface EdgePlusPositions {
  left: Point;
  right: Point;
}

/** Screen-space anchors for the left/right edge-`+` buttons (F2). */
export function edgePlusButtonPositions(
  node: OverlayNode,
  transform: CanvasTransform,
  nodeSize: [number, number] = NODE_SIZE,
): EdgePlusPositions {
  const halfWidth = nodeSize[0] / 2;
  return {
    left: boardToCanvas(node.position.x - halfWidth, node.position.y, transform),
    right: boardToCanvas(node.position.x + halfWidth, node.position.y, transform),
  };
}

/** Screen-space anchor above the node's top edge for the action toolbar (F3). */
export function toolbarPosition(
  node: OverlayNode,
  transform: CanvasTransform,
  nodeSize: [number, number] = NODE_SIZE,
): Point {
  const halfHeight = nodeSize[1] / 2;
  return boardToCanvas(node.position.x, node.position.y - halfHeight, transform);
}
