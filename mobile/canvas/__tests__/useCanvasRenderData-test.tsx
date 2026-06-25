/**
 * useCanvasRenderData — unit tests (red-first).
 *
 * Verifies the consolidated culling memo: node positions, viewport, visible node ids,
 * and visible edges (M3 SDD §9, §10).
 */

import { renderHook } from '@testing-library/react-native';
import { useCanvasRenderData } from '../useCanvasRenderData';
import type { CanvasNode, CanvasEdge } from '../SkiaCanvas';
import type { LiveDragOverride } from '../useLiveDragOverride';

const SCREEN = { width: 375, height: 812 };
const IDENTITY = { scale: 1, translateX: 0, translateY: 0 };

const NODES: CanvasNode[] = [
  { node_id: 'n1', parent_node_id: null, position: { x: 0, y: 0 } },
  { node_id: 'n2', parent_node_id: 'n1', position: { x: 0, y: 1000 } },
];

const EDGES: CanvasEdge[] = [
  { edge_id: 'e1', source_node_id: 'n1', target_node_id: 'n2', edge_kind: 'ai_path' },
];

describe('useCanvasRenderData', () => {
  it('returns node positions from live nodes', async () => {
    const { result } = await renderHook(() => useCanvasRenderData(NODES, EDGES, null, IDENTITY, SCREEN));
    expect(result.current.nodePositions).toEqual({ n1: { x: 0, y: 0 }, n2: { x: 0, y: 1000 } });
  });

  it('overrides the dragged node position', async () => {
    const override: LiveDragOverride = { nodeId: 'n1', x: 42, y: 43 };
    const { result } = await renderHook(() => useCanvasRenderData(NODES, EDGES, override, IDENTITY, SCREEN));
    expect(result.current.nodePositions.n1).toEqual({ x: 42, y: 43 });
    expect(result.current.nodePositions.n2).toEqual({ x: 0, y: 1000 });
  });

  it('computes visible node ids for the current viewport', async () => {
    const { result } = await renderHook(() => useCanvasRenderData(NODES, EDGES, null, IDENTITY, SCREEN));
    expect(result.current.visIds.has('n1')).toBe(true);
    expect(result.current.visIds.has('n2')).toBe(false);
  });

  it('culls edges with both endpoints off-screen', async () => {
    const { result } = await renderHook(() => useCanvasRenderData(NODES, EDGES, null, IDENTITY, SCREEN));
    expect(result.current.visibleEdges).toHaveLength(1);
    expect(result.current.visibleEdges[0].edge_id).toBe('e1');
  });
});
