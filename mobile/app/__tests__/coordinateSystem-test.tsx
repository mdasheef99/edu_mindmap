/**
 * T1 — Coordinate seam (M3 SDD §12 / §4).
 *
 * The hybrid canvas (ADR-0013) has three coordinate spaces; the seam contract is the
 * single shared formula bridging board <-> screen. These tests are the enforcement
 * mechanism for the rule that all conversions go through one shared module
 * (mobile/canvas/coordinateSystem.ts) — no inline coordinate math anywhere.
 *
 * Traceability: phase-3-m3-canvas-sdd.md §4, §12 T1; adr-log-02.md ADR-0013.
 */

import { boardToCanvas, canvasToBoard } from '../../canvas/coordinateSystem';

describe('T1 — coordinate seam', () => {
  it('test_board_to_canvas_at_zoom_and_pan', () => {
    const transform = { scale: 0.5, translateX: 100, translateY: -50 };

    // Root node at board (0, 0) maps to screen (100, -50).
    expect(boardToCanvas(0, 0, transform)).toEqual({ x: 100, y: -50 });

    // Child at board (200, 100) maps to screen (200, 0).
    expect(boardToCanvas(200, 100, transform)).toEqual({ x: 200, y: 0 });
  });

  it('test_canvas_to_board_round_trip', () => {
    const transform = { scale: 1.37, translateX: -42.5, translateY: 318.25 };
    const samples = [
      { x: 0, y: 0 },
      { x: 123.75, y: -987.5 },
      { x: -456.25, y: 654.125 },
    ];

    for (const point of samples) {
      const screen = boardToCanvas(point.x, point.y, transform);
      const board = canvasToBoard(screen.x, screen.y, transform);
      expect(board.x).toBeCloseTo(point.x, 10);
      expect(board.y).toBeCloseTo(point.y, 10);
    }
  });
});
