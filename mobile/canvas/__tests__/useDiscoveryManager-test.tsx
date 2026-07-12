/**
 * useDiscoveryManager — unit tests (red-first).
 *
 * Verifies the edge-discovery sheet state machine: offer-set loading, error display,
 * branch-created cleanup, and reload callback wiring (M3-B/M3-C SDD §5.2, §6).
 */

import React, { useRef } from 'react';
import { Pressable, Text } from 'react-native';
import { renderHook, act, render, screen, fireEvent, waitFor } from '@testing-library/react-native';
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

  it('keeps the first completed discovery visible and ignores a later competing completion', async () => {
    function DiscoveryHarness() {
      const discovery = useDiscoveryManager();
      const requests = useRef<Array<number | null>>([]);
      const secondOffer = { ...OFFER_SET, offer_set_id: 'os-2', source_node_id: 'n2' };
      const secondNode = { ...NODE, node_id: 'n2' };
      return (
        <>
          <Pressable accessibilityRole="button" accessibilityLabel="Start first" onPress={() => { requests.current[0] = discovery.beginDiscovery(); }} />
          <Pressable accessibilityRole="button" accessibilityLabel="Start second" onPress={() => { requests.current[1] = discovery.beginDiscovery(); }} />
          <Pressable accessibilityRole="button" accessibilityLabel="Complete first" onPress={() => { discovery.handleOfferSet(OFFER_SET, NODE, requests.current[0] ?? undefined); }} />
          <Pressable accessibilityRole="button" accessibilityLabel="Complete second" onPress={() => { discovery.handleOfferSet(secondOffer, secondNode, requests.current[1] ?? undefined); }} />
          <Pressable accessibilityRole="button" accessibilityLabel="Fail second" onPress={() => { discovery.handleOfferError(requests.current[1] ?? undefined); }} />
          <Text>{discovery.activeOfferSet?.offerSet.offer_set_id ?? 'No questions open'}</Text>
          <Text>{discovery.discoveryError ?? 'No discovery error'}</Text>
        </>
      );
    }

    await render(<DiscoveryHarness />);
    await fireEvent.press(screen.getByRole('button', { name: 'Start first' }));
    await fireEvent.press(screen.getByRole('button', { name: 'Start second' }));
    await fireEvent.press(screen.getByRole('button', { name: 'Complete first' }));
    await waitFor(() => expect(screen.getByText('os-1')).toBeTruthy());
    await fireEvent.press(screen.getByRole('button', { name: 'Complete second' }));
    await waitFor(() => {
      expect(screen.getByText('os-1')).toBeTruthy();
      expect(screen.queryByText('os-2')).toBeNull();
    });
    await fireEvent.press(screen.getByRole('button', { name: 'Fail second' }));
    await waitFor(() => expect(screen.getByText('No discovery error')).toBeTruthy());
  });
});
