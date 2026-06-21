/**
 * Gesture transform math — pinch/pan reducers for the §8 gesture layer.
 *
 * Pure functions only: pinch and pan are driven on the UI thread (Reanimated worklets),
 * but the transform arithmetic lives here so it is deterministic and CI-testable without a
 * device. Scale is clamped to [CANVAS_MIN_ZOOM, CANVAS_MAX_ZOOM] (configuration-reference.md
 * §3). Pinch is focal-preserving: the board point under the focal stays under the focal,
 * computed through the §4 coordinate seam.
 *
 * Traceability: phase-3-m3-canvas-sdd.md §8, §4; configuration-reference.md §3.
 */

import { CanvasTransform, canvasToBoard } from './coordinateSystem';

export const CANVAS_MIN_ZOOM = 0.25;
export const CANVAS_MAX_ZOOM = 4.0;

/** Clamp a scale to the configured zoom bounds. */
export function clampScale(scale: number): number {
  'worklet';
  if (scale < CANVAS_MIN_ZOOM) {
    return CANVAS_MIN_ZOOM;
  }
  if (scale > CANVAS_MAX_ZOOM) {
    return CANVAS_MAX_ZOOM;
  }
  return scale;
}

/**
 * Apply a pinch about a screen-space focal point, preserving the board point under it.
 *
 * newScale = clamp(base.scale * gestureScale); translate is then solved so that
 * boardToCanvas(boardUnderFocal, result) === focal.
 */
export function applyPinch(
  base: CanvasTransform,
  gestureScale: number,
  focal: { x: number; y: number },
): CanvasTransform {
  'worklet';
  const newScale = clampScale(base.scale * gestureScale);
  const board = canvasToBoard(focal.x, focal.y, base);
  return {
    scale: newScale,
    translateX: focal.x - board.x * newScale,
    translateY: focal.y - board.y * newScale,
  };
}

/** Apply a pan by a screen-space delta; scale is unchanged. */
export function applyPan(base: CanvasTransform, dx: number, dy: number): CanvasTransform {
  'worklet';
  return {
    scale: base.scale,
    translateX: base.translateX + dx,
    translateY: base.translateY + dy,
  };
}
