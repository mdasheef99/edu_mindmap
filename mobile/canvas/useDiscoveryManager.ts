/**
 * useDiscoveryManager — edge-`+` discovery sheet state (M3-B SDD §5.2, M3-C SDD §6).
 *
 * Manages the active offer-set sheet and the error banner. Keeping this in a dedicated
 * hook keeps the SkiaCanvas orchestrator focused on rendering composition.
 */

import { useCallback, useRef, useState } from 'react';
import type { CanvasNode } from './SkiaCanvas';
import type { EdgeOfferSet } from './EdgeOfferSetSheet';

export interface DiscoveryState {
  activeOfferSet: { offerSet: EdgeOfferSet; sourceNode: CanvasNode } | null;
  discoveryError: string | null;
  beginDiscovery: () => number | null;
  handleOfferSet: (offerSet: EdgeOfferSet, sourceNode: CanvasNode, generation?: number) => void;
  handleOfferError: (generation?: number) => void;
  handleBranchCreated: () => void;
  closeOfferSet: () => void;
}

export function useDiscoveryManager(onReloadCanvas?: () => void): DiscoveryState {
  const [activeOfferSet, setActiveOfferSet] = useState<{
    offerSet: EdgeOfferSet;
    sourceNode: CanvasNode;
  } | null>(null);
  const [discoveryError, setDiscoveryError] = useState<string | null>(null);
  const generationRef = useRef(0);
  const acceptedGenerationRef = useRef<number | null>(null);

  const beginDiscovery = useCallback(() => (
    acceptedGenerationRef.current === generationRef.current ? null : generationRef.current
  ), []);

  const handleOfferSet = useCallback((offerSet: EdgeOfferSet, sourceNode: CanvasNode, generation?: number) => {
    if (generation !== undefined) {
      if (generation !== generationRef.current || acceptedGenerationRef.current === generation) return;
      acceptedGenerationRef.current = generation;
    }
    setDiscoveryError(null);
    setActiveOfferSet({ offerSet, sourceNode });
  }, []);

  const handleOfferError = useCallback((generation?: number) => {
    if (generation !== undefined
      && (generation !== generationRef.current || acceptedGenerationRef.current === generation)) return;
    setDiscoveryError('Question options could not load. Try again.');
  }, []);

  const closeOfferSet = useCallback(() => {
    generationRef.current += 1;
    acceptedGenerationRef.current = null;
    setActiveOfferSet(null);
  }, []);

  const handleBranchCreated = useCallback(() => {
    generationRef.current += 1;
    acceptedGenerationRef.current = null;
    setActiveOfferSet(null);
    onReloadCanvas?.();
  }, [onReloadCanvas]);

  return {
    activeOfferSet,
    discoveryError,
    beginDiscovery,
    handleOfferSet,
    handleOfferError,
    handleBranchCreated,
    closeOfferSet,
  };
}
