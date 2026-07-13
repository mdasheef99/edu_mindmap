import { renderHook } from '@testing-library/react-native';

const panHandlers: Record<string, (...args: any[]) => void> = {};

jest.mock('react-native-reanimated', () => ({
  useSharedValue: (value: unknown) => ({ value }),
  useDerivedValue: (derive: () => unknown) => ({ value: derive() }),
  runOnJS: (fn: (...args: any[]) => unknown) => fn,
}));

jest.mock('react-native-gesture-handler', () => {
  const gesture = (capture?: Record<string, (...args: any[]) => void>) => ({
    onStart(fn: (...args: any[]) => void) { if (capture) capture.start = fn; return this; },
    onUpdate(fn: (...args: any[]) => void) { if (capture) capture.update = fn; return this; },
    onEnd(fn: (...args: any[]) => void) { if (capture) capture.end = fn; return this; },
    onFinalize(fn: (...args: any[]) => void) { if (capture) capture.finalize = fn; return this; },
  });
  return { Gesture: {
    Pan: () => gesture(panHandlers), Pinch: () => gesture(), Tap: () => gesture(),
    Simultaneous: (...items: unknown[]) => items, Race: (...items: unknown[]) => items,
  } };
});

import { useCanvasGestures } from '../useCanvasGestures';

describe('useCanvasGestures lifecycle', () => {
  it('clears transient drag state without committing when the pan is cancelled', async () => {
    const onNodeDragEnd = jest.fn();
    const nodes = [{ node_id: 'n1', parent_node_id: null, position: { x: 0, y: 0 } }];
    const nodesRef = { current: nodes };
    const { result } = await renderHook(() => useCanvasGestures({
      nodes, nodesRef, transform: { scale: 1, translateX: 0, translateY: 0 },
      nodeSize: [100, 40], onNodeDragEnd,
    }));

    panHandlers.start({ x: 0, y: 0 });
    panHandlers.update({ translationX: 25, translationY: 30 });
    expect(result.current.dragNodeIdx.value).toBe(0);
    panHandlers.finalize({}, false);

    expect(result.current.dragNodeIdx.value).toBe(-1);
    expect(onNodeDragEnd).not.toHaveBeenCalled();
  });
});
