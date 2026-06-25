/**
 * useDiscoveryManager — edge-`+` discovery sheet state (M3-B SDD §5.2, M3-C SDD §6).
 *
 * Manages the active offer-set sheet and the error banner. Keeping this in a dedicated
 * hook keeps the SkiaCanvas orchestrator focused on rendering composition.
 */

import { useCallback, useState } from 'react';
import type { CanvasNode } from './SkiaCanvas';
import type { EdgeOfferSet } from './EdgeOfferSetSheet';

export interface DiscoveryState {
  activeOfferSet: { offerSet: EdgeOfferSet; sourceNode: CanvasNode } | null;
  discoveryError: string | null;
  handleOfferSet: (offerSet: EdgeOfferSet, sourceNode: CanvasNode) => void;
  handleOfferError: () => void;
  handleBranchCreated: () => void;
  closeOfferSet: () => void;
}

export function useDiscoveryManager(onReloadCanvas?: () => void): DiscoveryState {
  const [activeOfferSet, setActiveOfferSet] = useState<{
    offerSet: EdgeOfferSet;
    sourceNode: CanvasNode;
  } | null>(null);
  const [discoveryError, setDiscoveryError] = useState<string | null>(null);

  const handleOfferSet = useCallback((offerSet: EdgeOfferSet, sourceNode: CanvasNode) => {
    setDiscoveryError(null);
    setActiveOfferSet({ offerSet, sourceNode });
  }, []);

  const handleOfferError = useCallback(() => {
    setDiscoveryError('Question options could not load. Try again.');
  }, []);

  const closeOfferSet = useCallback(() => setActiveOfferSet(null), []);

  const handleBranchCreated = useCallback(() => {
    setActiveOfferSet(null);
    onReloadCanvas?.();
  }, [onReloadCanvas]);

  return {
    activeOfferSet,
    discoveryError,
    handleOfferSet,
    handleOfferError,
    handleBranchCreated,
    closeOfferSet,
  };
}
