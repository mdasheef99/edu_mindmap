/**
 * Dual-state sync controllers — frame-budget protection (M3 SDD §7, §8).
 *
 * During an active gesture only the ephemeral transform (a stand-in for Reanimated
 * SharedValues) changes; Zustand is never written on a per-frame basis. The single write
 * back to Zustand happens on gesture end. Node drag end additionally flags the node as
 * positionOverridden so the d3-hierarchy layout engine skips it on re-layout (§6).
 *
 * These controllers express the gesture lifecycle as plain callbacks so the
 * "write once, on end" invariant is enforced independently of the Reanimated runtime.
 *
 * Traceability: phase-3-m3-canvas-sdd.md §7, §8; ADR-0013 (positions are shared state).
 */

import { CanvasTransform, Point } from './coordinateSystem';

export interface ViewportStore {
  setViewport(viewport: CanvasTransform): void;
}

export interface NodePositionStore {
  setNodePosition(
    nodeId: string,
    position: Point,
    options: { positionOverridden: boolean },
  ): void;
}

/** Pan/zoom controller: mutates only `transform` mid-gesture; writes Zustand once on end. */
export function createViewportGestureController(opts: {
  store: ViewportStore;
  transform: CanvasTransform;
}) {
  const { store, transform } = opts;
  let baseTranslateX = 0;
  let baseTranslateY = 0;

  return {
    onStart() {
      baseTranslateX = transform.translateX;
      baseTranslateY = transform.translateY;
    },
    onUpdate(translationX: number, translationY: number) {
      // SharedValues only — no Zustand write inside the gesture worklet.
      transform.translateX = baseTranslateX + translationX;
      transform.translateY = baseTranslateY + translationY;
    },
    onEnd() {
      store.setViewport({
        scale: transform.scale,
        translateX: transform.translateX,
        translateY: transform.translateY,
      });
    },
  };
}

/** Node drag controller: tracks board position mid-drag; writes Zustand once on end. */
export function createNodeDragController(opts: {
  store: NodePositionStore;
  nodeId: string;
  startPosition: Point;
}) {
  const { store, nodeId, startPosition } = opts;
  let current: Point = { ...startPosition };

  return {
    onStart() {
      current = { ...startPosition };
    },
    onUpdate(boardDeltaX: number, boardDeltaY: number) {
      // SharedValues only — no Zustand write mid-drag.
      current = { x: startPosition.x + boardDeltaX, y: startPosition.y + boardDeltaY };
    },
    onEnd() {
      store.setNodePosition(nodeId, current, { positionOverridden: true });
    },
    get position(): Point {
      return current;
    },
  };
}
