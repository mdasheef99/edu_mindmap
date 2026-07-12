/**
 * Edge rendering helpers — geometry + edge_kind styling for the §9 Skia layer.
 *
 * Skia draws edges as cubic Béziers between the boardToCanvas-mapped endpoints (§4, §9).
 * The path command string and the style descriptor are produced here as plain data so the
 * geometry/branch logic is deterministic and CI-testable; the Skia renderer consumes them
 * (Path from SVG string + dash path effect). Styling is keyed by edge_kind: ai_path renders
 * solid (the ordered exploration structure), manual_reference renders dashed/distinct so a
 * learner-created reference is never misread as path progression (session-path-data-contract §7).
 *
 * Traceability: phase-3-m3-canvas-sdd.md §9, §4; session-path-data-contract.md §7.
 */

import { Point } from './coordinateSystem';

export type EdgeKind = 'ai_path' | 'manual_reference';

export interface EdgeStyle {
  dashed: boolean;
  dashIntervals: number[];
}

/**
 * Cubic Bézier path command between two screen-space points, biased to a vertical S-curve
 * (control points on the midline). Endpoints map a parent→child edge in the tidy-tree layout.
 */
export function cubicBezierPath(p0: Point, p1: Point): string {
  const midY = (p0.y + p1.y) / 2;
  return `M ${p0.x} ${p0.y} C ${p0.x} ${midY} ${p1.x} ${midY} ${p1.x} ${p1.y}`;
}

/** Style descriptor keyed by edge_kind: ai_path solid, manual_reference dashed. */
export function edgeStyleForKind(kind?: string): EdgeStyle {
  if (kind === 'manual_reference') {
    return { dashed: true, dashIntervals: [8, 6] };
  }
  return { dashed: false, dashIntervals: [] };
}
