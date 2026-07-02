/**
 * Stage 1 CI render-count gate (M3 SDD §13, §14) — merge-blocking, device-free.
 *
 * §13 Stage 1: a deterministic render-count harness asserts the canvas render path stays
 * bounded for a CANVAS_PERFORMANCE_GATE_NODES (40) board. The render path is the set of draw
 * primitives = visible nodes + culled-visible edges (§9). Two invariants protect the 16 ms
 * frame budget without a device: (1) at the 40-node budget the render path is bounded by the
 * node budget; (2) viewport culling collapses the render path to *visible* content when zoomed,
 * so cost scales with what is on screen, not with total board size.
 *
 * Traceability: phase-3-m3-canvas-sdd.md §13, §9, §14; configuration-reference.md §3.
 */

import { computeLayout, LayoutInputNode } from '../../canvas/layout';
import {
  CANVAS_PERFORMANCE_GATE_NODES,
  countRenderPrimitives,
} from '../../canvas/renderBudget';
import { BoardEdge } from '../../canvas/viewportCulling';

// Ternary tree of n nodes (n0 root) with parent→child edges.
function buildTree(n: number): Record<string, LayoutInputNode> {
  const nodes: Record<string, LayoutInputNode> = {};
  for (let i = 0; i < n; i += 1) {
    nodes[`n${i}`] = {
      node_id: `n${i}`,
      parent_node_id: i === 0 ? null : `n${Math.floor((i - 1) / 3)}`,
    };
  }
  return nodes;
}

function buildEdges(n: number): BoardEdge[] {
  const edges: BoardEdge[] = [];
  for (let i = 1; i < n; i += 1) {
    edges.push({
      edge_id: `e${i}`,
      source_node_id: `n${Math.floor((i - 1) / 3)}`,
      target_node_id: `n${i}`,
    });
  }
  return edges;
}

describe('Stage 1 render-count gate (M3 SDD §13)', () => {
  const N = CANVAS_PERFORMANCE_GATE_NODES;
  const positions = computeLayout(buildTree(N));
  const edges = buildEdges(N);

  const xs = Object.values(positions).map((p) => p.x);
  const ys = Object.values(positions).map((p) => p.y);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);

  it('test_render_path_bounded_by_node_budget_for_40_nodes', () => {
    // §4 seam: screenX = boardX*scale + translateX. To map the board's [minX..maxX] box
    // onto [0..width] at scale 1, translate by -min (board min → screen 0).
    const fullViewportTransform = { scale: 1, translateX: -minX, translateY: -minY };
    const screen = { width: maxX - minX + 1, height: maxY - minY + 1 };

    const counts = countRenderPrimitives(positions, edges, fullViewportTransform, screen);

    expect(CANVAS_PERFORMANCE_GATE_NODES).toBe(40);
    expect(counts.nodes).toBe(N);
    expect(counts.edges).toBe(N - 1);
    // The 40-node render path is bounded by the node budget (nodes + tree edges).
    expect(counts.nodes).toBeLessThanOrEqual(CANVAS_PERFORMANCE_GATE_NODES);
    expect(counts.total).toBe(N + (N - 1));
  });

  it('test_culling_collapses_render_path_to_visible_content', () => {
    const fullTotal = countRenderPrimitives(
      positions,
      edges,
      { scale: 1, translateX: -minX, translateY: -minY },
      { width: maxX - minX + 1, height: maxY - minY + 1 },
    ).total;

    // Small viewport centered on the root at board (0,0): translate = width/2 places the
    // box at [-50,50] (§4 seam inverse), so most nodes are off-screen.
    const zoomed = countRenderPrimitives(
      positions,
      edges,
      { scale: 1, translateX: 50, translateY: 50 },
      { width: 100, height: 100 },
    );

    expect(zoomed.nodes).toBeGreaterThanOrEqual(1);
    expect(zoomed.total).toBeLessThan(fullTotal);
  });
});
