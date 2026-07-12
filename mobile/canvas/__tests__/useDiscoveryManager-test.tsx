/**
 * useDiscoveryManager — unit tests (red-first).
 *
 * Verifies the edge-discovery sheet state machine: offer-set loading, error display,
 * branch-created cleanup, and reload callback wiring (M3-B/M3-C SDD §5.2, §6).
 */

import { renderHook, act } from '@testing-library/react-native';
import { useDiscoveryManager } from '../useDiscoveryManager';
import type { CanvasNode } from '../SkiaCanvas';
import type { EdgeOfferSet } from '../EdgeOfferSetSheet';

const NODE: CanvasNode = { node_id: 'n1', parent_node_id: null, position: { x: 0, y: 0 } };

const OFFER_SET: EdgeOfferSet = {
  offer_set_id: 'os-1', session_id: 's1', source_node_id: 'n1', launch_method: 'edge_plus', options: [],
};

describe('useDiscoveryManager', () => {
  it('starts with no active offer set and no error', async () => {
    const { result } = await renderHook(() => useDiscoveryManager());
    expect(result.current.activeOfferSet).toBeNull();
    expect(result.current.discoveryError).toBeNull();
  });

  it('sets active offer set and clears prior error', async () => {
    const { result } = await renderHook(() => useDiscoveryManager());
    await act(async () => { result.current.handleOfferError(); });
    await act(async () => { result.current.handleOfferSet(OFFER_SET, NODE); });
    expect(result.current.activeOfferSet?.offerSet.offer_set_id).toBe('os-1');
    expect(result.current.activeOfferSet?.sourceNode.node_id).toBe('n1');
    expect(result.current.discoveryError).toBeNull();
  });

  it('sets a category-neutral error message', async () => {
    const { result } = await renderHook(() => useDiscoveryManager());
    await act(async () => { result.current.handleOfferError(); });
    expect(result.current.discoveryError).toBe('Question options could not load. Try again.');
  });

  it('closes offer set on branch created and reloads canvas', async () => {
    const onReload = jest.fn();
    const { result } = await renderHook(() => useDiscoveryManager(onReload));
    await act(async () => { result.current.handleOfferSet(OFFER_SET, NODE); });
    await act(async () => { result.current.handleBranchCreated(); });
    expect(result.current.activeOfferSet).toBeNull();
    expect(onReload).toHaveBeenCalledTimes(1);
  });

  it('closes offer set without reload', async () => {
    const { result } = await renderHook(() => useDiscoveryManager());
    await act(async () => { result.current.handleOfferSet(OFFER_SET, NODE); });
    await act(async () => { result.current.closeOfferSet(); });
    expect(result.current.activeOfferSet).toBeNull();
  });
});
