/**
 * Gesture transform — zoom clamp + focal-preserving pinch (M3 SDD §8, §14).
 *
 * §8: pinch/pan run on the UI thread; scale is clamped to
 * [CANVAS_MIN_ZOOM=0.25, CANVAS_MAX_ZOOM=4.0] (configuration-reference.md §3).
 * Pinch must be focal-preserving: the board point under the pinch focal stays under
 * the focal after zooming (round-trip through the §4 coordinate seam).
 *
 * Traceability: phase-3-m3-canvas-sdd.md §8, §4, §14; configuration-reference.md §3.
 */

import { boardToCanvas, CanvasTransform } from '../../canvas/coordinateSystem';
import {
  CANVAS_MAX_ZOOM,
  CANVAS_MIN_ZOOM,
  applyPan,
  applyPinch,
  clampScale,
} from '../../canvas/gestureTransform';

const IDENTITY: CanvasTransform = { scale: 1, translateX: 0, translateY: 0 };

describe('gesture transform — zoom clamp (M3 SDD §8)', () => {
  it('test_clamp_scale_below_min', () => {
    expect(clampScale(0.05)).toBe(CANVAS_MIN_ZOOM);
    expect(CANVAS_MIN_ZOOM).toBe(0.25);
  });

  it('test_clamp_scale_above_max', () => {
    expect(clampScale(99)).toBe(CANVAS_MAX_ZOOM);
    expect(CANVAS_MAX_ZOOM).toBe(4.0);
  });

  it('test_clamp_scale_in_range_unchanged', () => {
    expect(clampScale(1.5)).toBe(1.5);
  });
});

describe('gesture transform — focal-preserving pinch (M3 SDD §8)', () => {
  it('test_pinch_keeps_board_point_under_focal', () => {
    const base: CanvasTransform = { scale: 1, translateX: 30, translateY: 40 };
    const focal = { x: 120, y: 90 };

    const next = applyPinch(base, 2, focal);

    expect(next.scale).toBe(2);
    // The board point that was under the focal must remain under the focal.
    const projected = boardToCanvas(
      (focal.x - base.translateX) / base.scale,
      (focal.y - base.translateY) / base.scale,
      next,
    );
    expect(projected.x).toBeCloseTo(focal.x, 6);
    expect(projected.y).toBeCloseTo(focal.y, 6);
  });

  it('test_pinch_respects_max_clamp', () => {
    const next = applyPinch(IDENTITY, 1000, { x: 50, y: 50 });
    expect(next.scale).toBe(CANVAS_MAX_ZOOM);
  });
});

describe('gesture transform — pan (M3 SDD §8)', () => {
  it('test_pan_translates_by_delta', () => {
    const next = applyPan({ scale: 2, translateX: 10, translateY: 20 }, 5, -7);
    expect(next).toEqual({ scale: 2, translateX: 15, translateY: 13 });
  });
});
