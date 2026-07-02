/**
 * useLiveDragOverride — unit tests (red-first).
 *
 * Verifies the UI-thread → JS bridge that keeps edge paths anchored to a node while
 * it is being dragged (M3 SDD §7 dual-state rule).
 */

import React, { useRef } from 'react';
import { renderHook, act } from '@testing-library/react-native';
import type { SharedValue } from 'react-native-reanimated';
import { useLiveDragOverride } from '../useLiveDragOverride';
import type { UseCanvasGesturesResult } from '../useCanvasGestures';
import type { CanvasNode } from '../SkiaCanvas';

let lastReaction: { prepare: () => any; react: (value: any) => void } | null = null;

jest.mock('react-native-reanimated', () => {
  const { View } = require('react-native');
  return {
    __esModule: true,
    default: { View, createAnimatedComponent: (c: any) => c },
    useSharedValue: (init: any) => ({ value: init }),
    useAnimatedReaction: (prepare: () => any, react: (value: any) => void) => {
      lastReaction = { prepare, react };
    },
    runOnJS: (fn: any) => fn,
  };
});

const NODES: CanvasNode[] = [
  { node_id: 'n1', parent_node_id: null, position: { x: 0, y: 0 } },
  { node_id: 'n2', parent_node_id: null, position: { x: 100, y: 100 } },
];

interface GestureValues {
  dragNodeIdx: SharedValue<number>;
  dragCurrBX: SharedValue<number>;
  dragCurrBY: SharedValue<number>;
}

function makeSharedValue(value: number): SharedValue<number> {
  return { value } as SharedValue<number>;
}

function makeGestures(idx: number, x: number, y: number): GestureValues {
  return {
    dragNodeIdx: makeSharedValue(idx),
    dragCurrBX: makeSharedValue(x),
    dragCurrBY: makeSharedValue(y),
  };
}

function useWrapper(gestures: Pick<UseCanvasGesturesResult, 'dragNodeIdx' | 'dragCurrBX' | 'dragCurrBY'>) {
  const nodesRef = useRef<CanvasNode[]>(NODES);
  return useLiveDragOverride(gestures, nodesRef);
}

async function fireReaction() {
  await act(async () => { lastReaction?.react(lastReaction?.prepare()); });
}

describe('useLiveDragOverride', () => {
  it('returns null when no drag is active', async () => {
    const gestures = makeGestures(-1, 0, 0);
    const { result } = await renderHook((props: GestureValues) => useWrapper(props), { initialProps: gestures });
    await fireReaction();
    expect(result.current).toBeNull();
  });

  it('returns the live board position for the dragged node', async () => {
    const gestures = makeGestures(0, 50, 60);
    const { result } = await renderHook((props: GestureValues) => useWrapper(props), { initialProps: gestures });
    await fireReaction();
    expect(result.current).toEqual({ nodeId: 'n1', x: 50, y: 60 });
  });

  it('clears the override when the drag ends', async () => {
    const dragging = makeGestures(0, 50, 60);
    const { result, rerender } = await renderHook((props: GestureValues) => useWrapper(props), { initialProps: dragging });
    await fireReaction();
    expect(result.current).toEqual({ nodeId: 'n1', x: 50, y: 60 });
    await rerender(makeGestures(-1, 0, 0));
    await fireReaction();
    expect(result.current).toBeNull();
  });

  it('returns null for an out-of-bounds drag index', async () => {
    const gestures = makeGestures(5, 50, 60);
    const { result } = await renderHook((props: GestureValues) => useWrapper(props), { initialProps: gestures });
    await fireReaction();
    expect(result.current).toBeNull();
  });
});
