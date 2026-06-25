/**
 * useDeletionReconciliation — unit tests (red-first).
 *
 * Verifies the hook soft-filters nodes and edges after a full NodeDeletionResponse
 * is received, preserving the M3-C cascade-reconcile behavior (SDD §6, §9.4).
 */

import { renderHook, act } from '@testing-library/react-native';
import { useDeletionReconciliation } from '../useDeletionReconciliation';
import type { CanvasNode, CanvasEdge } from '../SkiaCanvas';
import type { NodeDeletionResponse } from '../NodeToolbar';

function makeNodes(): CanvasNode[] {
  return [
    { node_id: 'n1', parent_node_id: null, position: { x: 0, y: 0 } },
    { node_id: 'n2', parent_node_id: 'n1', position: { x: 0, y: 160 } },
    { node_id: 'n3', parent_node_id: 'n1', position: { x: 160, y: 0 } },
  ];
}

function makeEdges(): CanvasEdge[] {
  return [
    { edge_id: 'e1', source_node_id: 'n1', target_node_id: 'n2', edge_kind: 'ai_path' },
    { edge_id: 'e2', source_node_id: 'n1', target_node_id: 'n3', edge_kind: 'ai_path' },
  ];
}

describe('useDeletionReconciliation', () => {
  it('returns all nodes and edges before any deletion', async () => {
    const { result } = await renderHook(() => useDeletionReconciliation(makeNodes(), makeEdges()));
    expect(result.current.liveNodes.map((n) => n.node_id)).toEqual(['n1', 'n2', 'n3']);
    expect(result.current.liveEdges.map((e) => e.edge_id)).toEqual(['e1', 'e2']);
  });

  it('removes deleted nodes and edges incident to them', async () => {
    const { result } = await renderHook(() => useDeletionReconciliation(makeNodes(), makeEdges()));
    const response: NodeDeletionResponse = {
      session_id: 's1', root_node_id: 'n1', deleted_node_ids: ['n1'], deleted_edge_ids: [], confirmed: true,
    };
    await act(async () => { result.current.handleDeleted(response); });
    expect(result.current.liveNodes.map((n) => n.node_id)).toEqual(['n2', 'n3']);
    expect(result.current.liveEdges.map((e) => e.edge_id)).toEqual([]);
  });

  it('merges deletion results across multiple calls', async () => {
    const { result } = await renderHook(() => useDeletionReconciliation(makeNodes(), makeEdges()));
    await act(async () => { result.current.handleDeleted({
      session_id: 's1', root_node_id: 'n2', deleted_node_ids: ['n2'], deleted_edge_ids: ['e1'], confirmed: true,
    }); });
    await act(async () => { result.current.handleDeleted({
      session_id: 's1', root_node_id: 'n3', deleted_node_ids: ['n3'], deleted_edge_ids: ['e2'], confirmed: true,
    }); });
    expect(result.current.liveNodes.map((n) => n.node_id)).toEqual(['n1']);
    expect(result.current.liveEdges.map((e) => e.edge_id)).toEqual([]);
  });

  it('invokes onAfterDelete callback', async () => {
    const onAfterDelete = jest.fn();
    const { result } = await renderHook(() => useDeletionReconciliation(makeNodes(), makeEdges(), onAfterDelete));
    await act(async () => { result.current.handleDeleted({
      session_id: 's1', root_node_id: 'n1', deleted_node_ids: ['n1'], deleted_edge_ids: [], confirmed: true,
    }); });
    expect(onAfterDelete).toHaveBeenCalledTimes(1);
  });
});
