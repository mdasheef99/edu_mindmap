/**
 * Node hit-testing — board-space tap resolution for canvas selection (M3-B SDD §5.3).
 *
 * The caller converts a screen tap to board space via coordinateSystem.canvasToBoard first,
 * then asks which node the board-space point falls inside. Each node occupies an
 * axis-aligned bounding box of nodeSize ([width, height] board units) centered on its stored
 * position (§6). On overlap the topmost node wins: later entries in the array render on top,
 * so the last matching node is returned. The math is pure so it is deterministic and
 * CI-testable without a device.
 *
 * Traceability: phase-3-m3b-canvas-feature-parity-sdd.md §5.3; phase-3-m3-canvas-sdd.md §4;
 * adr-log-02.md ADR-0013.
 */

import { Point } from './coordinateSystem';

export interface HitTestNode {
  node_id: string;
  position: Point;
}

/**
 * Returns the node_id whose centered AABB contains boardPoint, or null if none. Topmost
 * (last in array) wins on overlap.
 */
export function hitTestNode(
  boardPoint: Point,
  nodes: HitTestNode[],
  nodeSize: [number, number],
): string | null {
  const halfWidth = nodeSize[0] / 2;
  const halfHeight = nodeSize[1] / 2;
  let hit: string | null = null;
  for (const node of nodes) {
    const insideX = Math.abs(boardPoint.x - node.position.x) <= halfWidth;
    const insideY = Math.abs(boardPoint.y - node.position.y) <= halfHeight;
    if (insideX && insideY) {
      hit = node.node_id;
    }
  }
  return hit;
}
