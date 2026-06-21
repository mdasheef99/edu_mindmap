/**
 * T2 — Layout engine (M3 SDD §12 / §6).
 *
 * ADR-0016 adopts deterministic d3-hierarchy (tidy-tree) over d3-force. Layout runs once
 * per structural change as a pure function of the tree, producing byte-identical board-space
 * coordinates for the same input shape. Drag overrides persist: a node flagged
 * positionOverridden keeps its position when siblings are re-laid-out.
 *
 * Traceability: phase-3-m3-canvas-sdd.md §6, §12 T2; adr-log-02.md ADR-0016.
 */

import { computeLayout, LayoutInputNode } from '../../canvas/layout';

function tree(nodes: LayoutInputNode[]): Record<string, LayoutInputNode> {
  return Object.fromEntries(nodes.map((node) => [node.node_id, node]));
}

describe('T2 — d3-hierarchy layout engine', () => {
  it('test_hierarchy_layout_root_only', () => {
    const nodes = tree([{ node_id: 'root', parent_node_id: null }]);

    const positions = computeLayout(nodes);

    expect(positions.root).toEqual({ x: 0, y: 0 });
  });

  it('test_hierarchy_layout_two_nodes', () => {
    const nodes = tree([
      { node_id: 'root', parent_node_id: null },
      { node_id: 'child', parent_node_id: 'root' },
    ]);

    const positions = computeLayout(nodes);

    // Root anchored at origin; child offset by positive Y (one generation below root).
    expect(positions.root).toEqual({ x: 0, y: 0 });
    expect(positions.child.y).toBeGreaterThan(positions.root.y);
  });

  it('test_hierarchy_layout_determinism', () => {
    const nodes = tree([
      { node_id: 'root', parent_node_id: null },
      { node_id: 'a', parent_node_id: 'root' },
      { node_id: 'b', parent_node_id: 'root' },
      { node_id: 'a1', parent_node_id: 'a' },
    ]);

    const first = computeLayout(nodes);
    const second = computeLayout(nodes);

    expect(JSON.stringify(second)).toBe(JSON.stringify(first));
  });

  it('test_hierarchy_layout_respects_drag_override', () => {
    const dragged = { x: 999, y: -777 };
    const nodes = tree([
      { node_id: 'root', parent_node_id: null },
      {
        node_id: 'a',
        parent_node_id: 'root',
        position: dragged,
        positionOverridden: true,
      },
      { node_id: 'b', parent_node_id: 'root' },
    ]);

    const positions = computeLayout(nodes);

    // The dragged node keeps its overridden position after re-layout of siblings.
    expect(positions.a).toEqual(dragged);
  });
});
