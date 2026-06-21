/**
 * Layout engine — tidy-tree via d3-hierarchy (ADR-0016).
 *
 * Runs once per structural change as a pure function of the tree. For the same input shape
 * it produces byte-identical board-space coordinates (deterministic). Nodes flagged with
 * `positionOverridden` (drag-pinned) keep their position unchanged after siblings are
 * re-laid-out.
 *
 * Traceability:
 * - docs/planning/sdd/phase-3-m3-canvas-sdd.md §6, §12 T2
 * - docs/architecture/adr-log-02.md ADR-0016
 */

import { hierarchy, tree } from 'd3-hierarchy';

export interface LayoutInputNode {
  node_id: string;
  parent_node_id: string | null;
  /** Existing board-space position (honoured when positionOverridden is true). */
  position?: { x: number; y: number };
  /** When true the node's position is a user drag-override and must not be recomputed. */
  positionOverridden?: boolean;
}

export interface LayoutPosition {
  x: number;
  y: number;
}

/** Board-space positions keyed by node_id. */
export type LayoutResult = Record<string, LayoutPosition>;

/** Horizontal and vertical spacing between nodes in board units. */
const NODE_X_SPACING = 200;
const NODE_Y_SPACING = 160;

/**
 * Compute board-space positions for every node in `nodes`.
 *
 * @param nodes - Map of node_id → LayoutInputNode. Must contain exactly one root
 *   (parent_node_id === null). Disconnected nodes (whose parent is absent) are silently
 *   omitted from the result.
 * @returns A record of node_id → { x, y } in board space (root at origin).
 */
export function computeLayout(nodes: Record<string, LayoutInputNode>): LayoutResult {
  // Find root.
  const rootNode = Object.values(nodes).find((n) => n.parent_node_id === null);
  if (!rootNode) return {};

  // Build adjacency list.
  const childrenMap: Record<string, string[]> = {};
  for (const n of Object.values(nodes)) {
    if (n.parent_node_id !== null) {
      if (!childrenMap[n.parent_node_id]) childrenMap[n.parent_node_id] = [];
      childrenMap[n.parent_node_id].push(n.node_id);
    }
  }

  // d3 hierarchy datum is just the node_id string.
  const root = hierarchy<string>(rootNode.node_id, (id) =>
    (childrenMap[id] ?? []).map((cid) => cid),
  );

  // Tidy-tree layout.
  const treeLayout = tree<string>().nodeSize([NODE_X_SPACING, NODE_Y_SPACING]);
  treeLayout(root);

  // Extract positions, offset so root is at (0, 0).
  const rootX = root.x ?? 0;
  const rootY = root.y ?? 0;

  const result: LayoutResult = {};
  root.each((d) => {
    const id = d.data;
    const input = nodes[id];
    if (!input) return;

    if (input.positionOverridden && input.position) {
      result[id] = { x: input.position.x, y: input.position.y };
    } else {
      result[id] = {
        x: Math.round((d.x - rootX) * 10) / 10,
        y: Math.round((d.y - rootY) * 10) / 10,
      };
    }
  });

  return result;
}
