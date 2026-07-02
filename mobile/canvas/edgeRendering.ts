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
export function edgeStyleForKind(kind: string): EdgeStyle {
  if (kind === 'manual_reference') {
    return { dashed: true, dashIntervals: [8, 6] };
  }
  return { dashed: false, dashIntervals: [] };
}

/** Default single-line character budget for an ai_path edge label (M3-B SDD §5.1). */
export const EDGE_LABEL_MAX_CHARS = 28;

export interface EdgeLabelLayout {
  position: Point;
  displayText: string;
}

/** Cubic Bézier point at parameter t for control points (p0, c1, c2, p1). */
function cubicBezierPoint(p0: Point, c1: Point, c2: Point, p1: Point, t: number): Point {
  const u = 1 - t;
  const w0 = u * u * u;
  const w1 = 3 * u * u * t;
  const w2 = 3 * u * t * t;
  const w3 = t * t * t;
  return {
    x: w0 * p0.x + w1 * c1.x + w2 * c2.x + w3 * p1.x,
    y: w0 * p0.y + w1 * c1.y + w2 * c2.y + w3 * p1.y,
  };
}

/**
 * Placement + display text for an ai_path edge label (M3-B SDD §5.1). The anchor is the
 * point on the edge's cubic Bézier at t=0.5, using the same midline control points as
 * cubicBezierPath so the label sits on the rendered curve. Display text is single-line and
 * truncated to opts.maxChars (default EDGE_LABEL_MAX_CHARS) with a trailing ellipsis.
 */
export function edgeLabelLayout(
  p0: Point,
  p1: Point,
  text: string,
  opts: { maxChars?: number } = {},
): EdgeLabelLayout {
  const midY = (p0.y + p1.y) / 2;
  const position = cubicBezierPoint(p0, { x: p0.x, y: midY }, { x: p1.x, y: midY }, p1, 0.5);
  const maxChars = opts.maxChars ?? EDGE_LABEL_MAX_CHARS;
  const displayText = text.length > maxChars ? `${text.slice(0, maxChars - 1)}…` : text;
  return { position, displayText };
}
