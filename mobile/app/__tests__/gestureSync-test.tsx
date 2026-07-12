/**
 * T3 — Dual-state sync and frame-budget protection (M3 SDD §12 / §7).
 *
 * The 60fps budget is protected by never writing to Zustand during a gesture: only the
 * (ephemeral, UI-thread) transform changes while the gesture is active, and the single
 * write back to Zustand happens on gesture end. Node drag end additionally flags the node
 * as positionOverridden so the layout engine skips it.
 *
 * These controllers model the gesture lifecycle as plain callbacks so the invariant is
 * unit-testable without a Reanimated/Gesture-Handler runtime.
 *
 * Traceability: phase-3-m3-canvas-sdd.md §7, §8, §12 T3.
 */

import {
  createNodeDragController,
  createViewportGestureController,
} from '../../canvas/gestureSync';

describe('T3 — dual-state sync', () => {
  it('test_gesture_end_writes_zustand_once', () => {
    const setViewport = jest.fn();
    const transform = { scale: 1, translateX: 0, translateY: 0 };
    const controller = createViewportGestureController({ store: { setViewport }, transform });

    controller.onStart();
    for (let i = 1; i <= 10; i += 1) {
      controller.onUpdate(i * 5, i * -3);
    }
    // No Zustand write may occur during the moves (frame-budget protection).
    expect(setViewport).not.toHaveBeenCalled();

    controller.onEnd();

    expect(setViewport).toHaveBeenCalledTimes(1);
    expect(setViewport).toHaveBeenCalledWith({ scale: 1, translateX: 50, translateY: -30 });
  });

  it('test_drag_end_sets_position_overridden', () => {
    const setNodePosition = jest.fn();
    const controller = createNodeDragController({
      store: { setNodePosition },
      nodeId: 'node-7',
      startPosition: { x: 100, y: 200 },
    });

    controller.onStart();
    controller.onUpdate(15, -25);
    controller.onUpdate(40, 60);
    // Nothing written to Zustand mid-drag.
    expect(setNodePosition).not.toHaveBeenCalled();

    controller.onEnd();

    expect(setNodePosition).toHaveBeenCalledTimes(1);
    expect(setNodePosition).toHaveBeenCalledWith(
      'node-7',
      { x: 140, y: 260 },
      { positionOverridden: true },
    );
  });
});
