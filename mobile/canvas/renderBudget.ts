/**
 * Render-budget harness — Stage 1 of the §13 performance gate (merge-blocking, device-free).
 *
 * The canvas render path is the set of draw primitives per frame: the visible Native node
 * overlays plus the culled-visible Skia edges (§9). Counting them deterministically (no device,
 * no timing) lets CI assert the render path stays bounded for a CANVAS_PERFORMANCE_GATE_NODES
 * board and that viewport culling collapses cost to on-screen content. Stage 2 (physical-device
 * 60fps profiling) verifies the actual frame budget.
 *
 * Traceability: phase-3-m3-canvas-sdd.md §13, §9; configuration-reference.md §3.
 */

import { CanvasTransform } from './coordinateSystem';
import { LayoutResult } from './layout';
import {
  BoardEdge,
  ScreenSize,
  computeBoardViewport,
  cullEdges,
  visibleNodeIds,
} from './viewportCulling';

/** 60fps gate node count on the reference Android device (configuration-reference.md §3). */
export const CANVAS_PERFORMANCE_GATE_NODES = 40;

export interface RenderPrimitiveCount {
  nodes: number;
  edges: number;
  total: number;
}

/**
 * Count the draw primitives the canvas would emit for the current viewport: visible node
 * overlays + culled-visible edges. Reuses the §9 culling helpers so the count tracks the real
 * render path exactly.
 */
export function countRenderPrimitives(
  positions: LayoutResult,
  edges: BoardEdge[],
  transform: CanvasTransform,
  screen: ScreenSize,
): RenderPrimitiveCount {
  const viewport = computeBoardViewport(transform, screen);
  const nodes = visibleNodeIds(positions, viewport).length;
  const edgeCount = cullEdges(edges, positions, viewport).length;
  return { nodes, edges: edgeCount, total: nodes + edgeCount };
}
