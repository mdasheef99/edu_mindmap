/**
 * T4 — Viewport culling (M3 SDD §12 / §9).
 *
 * Before each Skia render pass, edges whose BOTH endpoints fall outside the board-space
 * viewport box are dropped; only visible edges are drawn. The visible node_id list produced
 * by the same filter is what populates the viewport_changed payload's visible_node_ids.
 *
 * Board-space viewport box (§9) — derived from the §4 seam inverse
 * (boardX = (screenX - translateX) / scale):
 *   minX = -translateX / scale,            maxX = (screenW - translateX) / scale
 *   minY = -translateY / scale,            maxY = (screenH - translateY) / scale
 *
 * Traceability: phase-3-m3-canvas-sdd.md §4, §9, §10, §12 T4.
 */

import {
  computeBoardViewport,
  cullEdges,
  visibleNodeIds,
} from '../../canvas/viewportCulling';

const TRANSFORM = { scale: 1, translateX: 0, translateY: 0 };
const SCREEN = { width: 100, height: 100 };

// A non-zero pan/zoom transform exercises the seam-inverse box (regression for the
// §4/§9 convention conflict that culled on-screen nodes during panning).
const TRANSFORM_PANNED = { scale: 2, translateX: 100, translateY: 50 };
const SCREEN_PANNED = { width: 400, height: 300 };

// A,B inside the [0,0,100,100] box; C,D outside.
const NODE_POSITIONS = {
  A: { x: 10, y: 10 },
  B: { x: 50, y: 50 },
  C: { x: 500, y: 500 },
  D: { x: -50, y: -50 },
};

describe('T4 — viewport culling', () => {
  it('test_viewport_culling_excludes_offscreen_edges', () => {
    const viewport = computeBoardViewport(TRANSFORM, SCREEN);
    const edges = [
      { edge_id: 'e1', source_node_id: 'A', target_node_id: 'B' }, // both inside
      { edge_id: 'e2', source_node_id: 'C', target_node_id: 'D' }, // both outside
      { edge_id: 'e3', source_node_id: 'A', target_node_id: 'C' }, // straddles
    ];

    const visible = cullEdges(edges, NODE_POSITIONS, viewport);
    const visibleIds = visible.map((edge) => edge.edge_id);

    expect(visibleIds).toContain('e1');
    expect(visibleIds).toContain('e3');
    expect(visibleIds).not.toContain('e2');
  });

  it('test_visible_node_ids_matches_culled_set', () => {
    const viewport = computeBoardViewport(TRANSFORM, SCREEN);

    const ids = visibleNodeIds(NODE_POSITIONS, viewport);

    expect(new Set(ids)).toEqual(new Set(['A', 'B']));
  });

  it('test_compute_board_viewport_box_matches_seam_inverse', () => {
    // §4 seam inverse: boardX = (screenX - translateX) / scale, evaluated at the
    // screen corners [0,0] and [width,height].
    const viewport = computeBoardViewport(TRANSFORM_PANNED, SCREEN_PANNED);

    expect(viewport.minX).toBeCloseTo(-100 / 2); // -50
    expect(viewport.minY).toBeCloseTo(-50 / 2); // -25
    expect(viewport.maxX).toBeCloseTo((400 - 100) / 2); // 150
    expect(viewport.maxY).toBeCloseTo((300 - 50) / 2); // 125
  });

  it('test_panned_viewport_keeps_onscreen_node_visible', () => {
    // A board point at the origin maps on-screen under this pan (screenX = translateX),
    // so it must survive culling — the bug previously dropped it.
    const viewport = computeBoardViewport(TRANSFORM_PANNED, SCREEN_PANNED);

    const ids = visibleNodeIds({ origin: { x: 0, y: 0 } }, viewport);

    expect(ids).toContain('origin');
  });
});
