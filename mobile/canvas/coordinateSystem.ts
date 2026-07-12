/**
 * Coordinate system seam — the single bridge between the three hybrid-canvas spaces.
 *
 * ADR-0013 names the Skia<->Native coordinate seam as the highest engineering risk: node
 * positions are shared state read by both the Skia edge renderer and the Native node mapper.
 * This module is the SOLE location for seam math. No component may contain inline coordinate
 * calculations; every conversion calls boardToCanvas / canvasToBoard from here.
 *
 * Seam formula (phase-3-m3-canvas-sdd.md §4):
 *   screenX = boardX * scale + translateX
 *   screenY = boardY * scale + translateY
 *
 * Traceability: phase-3-m3-canvas-sdd.md §4; adr-log-02.md ADR-0013.
 */

export interface CanvasTransform {
  scale: number;
  translateX: number;
  translateY: number;
}

export interface Point {
  x: number;
  y: number;
}

/** Board space -> screen space. Used by the Skia edge renderer and Native node mapper. */
export function boardToCanvas(boardX: number, boardY: number, transform: CanvasTransform): Point {
  'worklet';
  return {
    x: boardX * transform.scale + transform.translateX,
    y: boardY * transform.scale + transform.translateY,
  };
}

/** Screen space -> board space. Used by tap-to-node hit testing and pinch focal math. */
export function canvasToBoard(screenX: number, screenY: number, transform: CanvasTransform): Point {
  'worklet';
  return {
    x: (screenX - transform.translateX) / transform.scale,
    y: (screenY - transform.translateY) / transform.scale,
  };
}
