/**
 * TB3 — Node selection (M3-B SDD §5.3, §6, §8).
 *
 * §5.3: `hitTestNode` is a pure helper — given a BOARD-space point (the caller converts the
 * screen tap via canvasToBoard first), the list of nodes, and the board-space node size, it
 * returns the node whose AABB (centered on the stored position) contains the point, or null.
 * On overlap the topmost node wins (last in array = rendered on top).
 *
 * §6/§7: selection is canonical Zustand state. `selectNode` obeys the write-once rule —
 * exactly one `set(...)` per call — so a tap commits a single store write.
 *
 * TB4 (§8, same file) covers the node-level action toolbar: Explore + Delete only (no
 * body-edit action — data-contract §3), and Delete → confirmation →
 * DELETE /v1/student/sessions/{session_id}/nodes/{node_id}?confirmed=true (data-contract §10).
 *
 * RED: mobile/canvas/hitTest.ts, store.ts, and NodeToolbar.tsx do not all exist yet.
 *
 * Traceability: phase-3-m3b-canvas-feature-parity-sdd.md §5.3, §6, §7, §8 TB3/TB4;
 * MVP §3.3, §4.3 L260; session-path-data-contract.md §3, §10.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { hitTestNode } from '../../canvas/hitTest';
import { useMindMapStore } from '../../canvas/store';
import { NodeToolbar } from '../../canvas/NodeToolbar';

const NODE_SIZE: [number, number] = [200, 160]; // half-width 100, half-height 80
const NODES = [
  { node_id: 'n1', position: { x: 0, y: 0 } },
  { node_id: 'n2', position: { x: 300, y: 0 } },
];

describe('TB3 — hitTestNode board-space AABB (SDD §5.3)', () => {
  it('test_hit_test_returns_node_under_point', () => {
    expect(hitTestNode({ x: 0, y: 0 }, NODES, NODE_SIZE)).toBe('n1');
    expect(hitTestNode({ x: 300, y: 0 }, NODES, NODE_SIZE)).toBe('n2');
  });

  it('test_hit_test_inside_aabb_corner', () => {
    // Just inside n1's half-extents (|dx|≤100, |dy|≤80).
    expect(hitTestNode({ x: 99, y: 79 }, NODES, NODE_SIZE)).toBe('n1');
  });

  it('test_hit_test_null_outside', () => {
    expect(hitTestNode({ x: 150, y: 0 }, NODES, NODE_SIZE)).toBeNull(); // gap between nodes
    expect(hitTestNode({ x: 1000, y: 1000 }, NODES, NODE_SIZE)).toBeNull();
  });

  it('test_hit_test_topmost_on_overlap', () => {
    // Overlapping nodes; the point falls inside both → topmost (last inserted) wins.
    const overlapping = [
      { node_id: 'under', position: { x: 0, y: 0 } },
      { node_id: 'over', position: { x: 50, y: 0 } },
    ];
    expect(hitTestNode({ x: 25, y: 0 }, overlapping, NODE_SIZE)).toBe('over');
  });
});

describe('TB3 — single-write selection in the canonical store (SDD §6/§7)', () => {
  beforeEach(() => {
    useMindMapStore.setState({ selectedNodeId: null });
  });

  it('test_select_node_sets_selected_node_id', () => {
    useMindMapStore.getState().selectNode('n1');
    expect(useMindMapStore.getState().selectedNodeId).toBe('n1');
  });

  it('test_tap_writes_selected_node_once', () => {
    // Write-once rule: one selectNode call → exactly one store mutation.
    let writes = 0;
    const unsubscribe = useMindMapStore.subscribe(() => {
      writes += 1;
    });
    useMindMapStore.getState().selectNode('n2');
    unsubscribe();
    expect(writes).toBe(1);
    expect(useMindMapStore.getState().selectedNodeId).toBe('n2');
  });

  it('test_clear_selection_resets_to_null', () => {
    useMindMapStore.getState().selectNode('n1');
    useMindMapStore.getState().clearSelection();
    expect(useMindMapStore.getState().selectedNodeId).toBeNull();
  });
});

describe('TB4 — node toolbar actions (SDD §5.3; data-contract §3/§10)', () => {
  const TOOLBAR_PROPS = {
    node: { node_id: 'n1', position: { x: 50, y: 60 } },
    transform: { scale: 1, translateX: 0, translateY: 0 },
    nodeSize: NODE_SIZE,
    apiBaseUrl: 'http://localhost:8000',
    authorizationToken: 'test-token',
    sessionId: 'session-1',
  };
  const originalFetch = global.fetch;

  afterEach(() => {
    jest.clearAllMocks();
    global.fetch = originalFetch;
  });

  it('test_toolbar_has_no_body_edit_action', async () => {
    // data-contract §3: learners never edit node body/content — the toolbar must expose
    // no edit-content affordance, only category-neutral navigation/delete actions.
    await render(<NodeToolbar {...TOOLBAR_PROPS} />);
    expect(screen.getByText('Explore')).toBeTruthy();
    expect(screen.getByText('Delete')).toBeTruthy();
    expect(screen.queryByText(/edit/i)).toBeNull();
  });

  it('test_delete_calls_endpoint_with_confirmed_true', async () => {
    global.fetch = jest.fn().mockResolvedValue({ ok: true, json: async () => ({}) });
    const onDeleted = jest.fn();
    await render(<NodeToolbar {...TOOLBAR_PROPS} onDeleted={onDeleted} />);

    // Delete requires explicit confirmation before the cascade endpoint is hit.
    fireEvent.press(screen.getByText('Delete'));
    fireEvent.press(await screen.findByText('Confirm'));

    await waitFor(() => expect(global.fetch).toHaveBeenCalled());
    const [url, opts] = (global.fetch as jest.Mock).mock.calls[0];
    expect(opts.method).toBe('DELETE');
    expect(url).toContain('/v1/student/sessions/session-1/nodes/n1');
    expect(url).toContain('confirmed=true');
    await waitFor(() => expect(onDeleted).toHaveBeenCalled());
  });

  /**
   * TC-M1 — NodeToolbar cascade full payload (M3-C SDD §9.4).
   * onDeleted must receive the full NodeDeletionResponse (deleted_node_ids + deleted_edge_ids),
   * NOT just the tapped node object (G1 gap fix).
   */
  it('TC-M1: onDeleted receives full NodeDeletionResponse, not just the tapped node', async () => {
    const deleteResponse = {
      session_id: 'session-1',
      root_node_id: 'n1',
      deleted_node_ids: ['n1', 'n2'],
      deleted_edge_ids: ['e1'],
      confirmed: true,
    };
    global.fetch = jest.fn().mockResolvedValue({ ok: true, json: async () => deleteResponse });
    const onDeleted = jest.fn();
    await render(<NodeToolbar {...TOOLBAR_PROPS} onDeleted={onDeleted} />);

    fireEvent.press(screen.getByText('Delete'));
    fireEvent.press(await screen.findByText('Confirm'));

    await waitFor(() => {
      expect(onDeleted).toHaveBeenCalledWith(deleteResponse);
      // Must NOT be called with just the OverlayNode (the old G1 partial-discard behaviour).
      expect(onDeleted).not.toHaveBeenCalledWith(TOOLBAR_PROPS.node);
    });
  });
});
