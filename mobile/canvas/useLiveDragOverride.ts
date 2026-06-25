/**
 * useLiveDragOverride — UI-thread → JS bridge for active node drags (M3 SDD §7).
 *
 * useAnimatedReaction reads the ephemeral Reanimated SharedValues every frame and mirrors
 * the dragged node's live board position to a JS state value. This state is used only for
 * edge-path rendering during the drag; committed positions remain write-once-on-end.
 */

import { useCallback, useState } from 'react';
import { runOnJS, useAnimatedReaction } from 'react-native-reanimated';
import type { CanvasNode } from './SkiaCanvas';
import type { UseCanvasGesturesResult } from './useCanvasGestures';

export interface LiveDragOverride {
  nodeId: string;
  x: number;
  y: number;
}

export function useLiveDragOverride(
  gestures: Pick<UseCanvasGesturesResult, 'dragNodeIdx' | 'dragCurrBX' | 'dragCurrBY'>,
  nodesRef: React.MutableRefObject<CanvasNode[]>,
): LiveDragOverride | null {
  const [liveDragOverride, setLiveDragOverride] = useState<LiveDragOverride | null>(null);

  const updateLiveDragPos = useCallback(
    (idx: number, bx: number, by: number) => {
      if (idx < 0) {
        setLiveDragOverride(null);
        return;
      }
      const node = nodesRef.current[idx];
      if (node) setLiveDragOverride({ nodeId: node.node_id, x: bx, y: by });
    },
    [nodesRef],
  );

  useAnimatedReaction(
    () => ({
      idx: gestures.dragNodeIdx.value,
      bx: gestures.dragCurrBX.value,
      by: gestures.dragCurrBY.value,
    }),
    (curr) => {
      runOnJS(updateLiveDragPos)(curr.idx, curr.bx, curr.by);
    },
  );

  return liveDragOverride;
}
