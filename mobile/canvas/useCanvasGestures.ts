/**
 * useCanvasGestures — UI-thread gesture state + composition for the hybrid canvas (M3 SDD §7, §8).
 *
 * Encapsulates the ephemeral Reanimated SharedValues, the pinch/pan/tap gesture lifecycle,
 * and the §7 write-once-on-end controller. All per-frame mutation stays on SharedValues;
 * canonical state is written only from the JS callbacks fired by gesture end (via runOnJS).
 *
 * Traceability: phase-3-m3-canvas-sdd.md §4, §5, §7, §8; adr-log-02.md ADR-0013.
 */

import { useEffect, useMemo, useRef } from 'react';
import { Gesture } from 'react-native-gesture-handler';
import { runOnJS, useDerivedValue, useSharedValue } from 'react-native-reanimated';
import type { SharedValue } from 'react-native-reanimated';
import { CanvasTransform, canvasToBoard, Point } from './coordinateSystem';
import { applyPinch, applyPan } from './gestureTransform';
import { createViewportGestureController } from './gestureSync';
import { hitTestNode } from './hitTest';
import type { CanvasNode } from './SkiaCanvas';

export interface UseCanvasGesturesOptions {
  /** Live node list (committed positions + drag overrides). */
  nodes: CanvasNode[];
  /** Mutable ref to the same node list, kept fresh across renders. */
  nodesRef: React.MutableRefObject<CanvasNode[]>;
  /** Committed transform at mount. */
  transform: CanvasTransform;
  /** Hit-test / drag AABB in board units. */
  nodeSize: [number, number];
  /** Fired once on viewport gesture end with the new canonical transform. */
  onTransformEnd?: (t: CanvasTransform) => void;
  /** Fired once on node-drag end with the final board position. */
  onNodeDragEnd?: (nodeId: string, x: number, y: number) => void;
  /** Fired on a tap that lands inside a node chip. */
  onSelectNode?: (nodeId: string) => void;
  /** Fired on a tap that lands on empty board space. */
  onClearSelection?: () => void;
}

export interface UseCanvasGesturesResult {
  scaleShared: SharedValue<number>;
  translateXShared: SharedValue<number>;
  translateYShared: SharedValue<number>;
  dragNodeIdx: SharedValue<number>;
  dragCurrBX: SharedValue<number>;
  dragCurrBY: SharedValue<number>;
  groupTransform: SharedValue<any>;
  composed: any;
}

export function useCanvasGestures(options: UseCanvasGesturesOptions): UseCanvasGesturesResult {
  const { nodes, nodesRef, transform, nodeSize, onTransformEnd, onNodeDragEnd, onSelectNode, onClearSelection } = options;

  // Ephemeral UI-thread SharedValues — updated every gesture frame, never writes Zustand (§5, §7).
  const scaleShared = useSharedValue(transform.scale);
  const translateXShared = useSharedValue(transform.translateX);
  const translateYShared = useSharedValue(transform.translateY);

  // Gesture base snapshots captured on gesture start so deltas are relative to start position.
  const baseScale = useSharedValue(transform.scale);
  const baseTX = useSharedValue(transform.translateX);
  const baseTY = useSharedValue(transform.translateY);

  // Node drag shared values (§7 node-drag path; dragNodeIdx=-1 = viewport pan mode).
  const dragNodeIdx = useSharedValue(-1);
  const dragStartBX = useSharedValue(0);
  const dragStartBY = useSharedValue(0);
  const dragCurrBX = useSharedValue(0);
  const dragCurrBY = useSharedValue(0);

  // §7 write-once-on-end controller. Mutable ref lets commitTransform update it before onEnd
  // fires so the store receives the correct final values.
  const ctrlTransformRef = useRef<CanvasTransform>({ ...transform });
  const onTransformEndRef = useRef(onTransformEnd);
  useEffect(() => {
    onTransformEndRef.current = onTransformEnd;
  }, [onTransformEnd]);

  const gestureController = useMemo(
    () =>
      createViewportGestureController({
        store: { setViewport: (t) => onTransformEndRef.current?.(t) },
        transform: ctrlTransformRef.current,
      }),
    [], // eslint-disable-line react-hooks/exhaustive-deps
  );

  /** JS-thread tap handler: convert to board space → hit-test → update selection (§7). */
  function handleTap(canvasPoint: Point) {
    const boardPoint = canvasToBoard(canvasPoint.x, canvasPoint.y, ctrlTransformRef.current);
    const hit = hitTestNode(boardPoint, nodesRef.current, nodeSize);
    if (hit) onSelectNode?.(hit);
    else onClearSelection?.();
  }

  /** JS-thread commit: update mutable ref then let the controller write to the store (§7). */
  function commitTransform(t: CanvasTransform) {
    ctrlTransformRef.current.scale = t.scale;
    ctrlTransformRef.current.translateX = t.translateX;
    ctrlTransformRef.current.translateY = t.translateY;
    gestureController.onEnd();
  }

  /** JS-thread node drag commit: report the final board position to the caller (§7). */
  function commitNodeDrag(idx: number, finalBX: number, finalBY: number) {
    const node = nodesRef.current[idx];
    if (!node) return;
    onNodeDragEnd?.(node.node_id, finalBX, finalBY);
  }

  // Skia Group reactive transform — UI-thread path, no React re-render needed (§5, Defect A fix).
  const groupTransform = useDerivedValue(() => [
    { translateX: translateXShared.value },
    { translateY: translateYShared.value },
    { scale: scaleShared.value },
  ]);

  // —— Gesture.Simultaneous(pinch, pan) ——
  const pinch = Gesture.Pinch()
    .onStart(() => {
      baseScale.value = scaleShared.value;
      baseTX.value = translateXShared.value;
      baseTY.value = translateYShared.value;
    })
    .onUpdate((e) => {
      const next = applyPinch(
        { scale: baseScale.value, translateX: baseTX.value, translateY: baseTY.value },
        e.scale,
        { x: e.focalX, y: e.focalY },
      );
      scaleShared.value = next.scale;
      translateXShared.value = next.translateX;
      translateYShared.value = next.translateY;
    })
    .onEnd(() => {
      runOnJS(commitTransform)({
        scale: scaleShared.value,
        translateX: translateXShared.value,
        translateY: translateYShared.value,
      });
    });

  const halfW = nodeSize[0] / 2;
  const halfH = nodeSize[1] / 2;

  const pan = Gesture.Pan()
    .onStart((e) => {
      baseTX.value = translateXShared.value;
      baseTY.value = translateYShared.value;
      // Hit-test in board space: node drag if touch lands inside a chip, else viewport pan (§7).
      const boardPt = canvasToBoard(e.x, e.y, {
        scale: scaleShared.value,
        translateX: translateXShared.value,
        translateY: translateYShared.value,
      });
      dragNodeIdx.value = -1;
      for (let i = 0; i < nodes.length; i++) {
        const n = nodes[i];
        if (
          Math.abs(boardPt.x - n.position.x) <= halfW &&
          Math.abs(boardPt.y - n.position.y) <= halfH
        ) {
          dragNodeIdx.value = i;
          dragStartBX.value = n.position.x;
          dragStartBY.value = n.position.y;
          dragCurrBX.value = n.position.x;
          dragCurrBY.value = n.position.y;
        }
      }
    })
    .onUpdate((e) => {
      if (dragNodeIdx.value >= 0) {
        // Node drag: canvas delta → board delta via inverse §4 seam.
        const s = scaleShared.value;
        dragCurrBX.value = dragStartBX.value + e.translationX / s;
        dragCurrBY.value = dragStartBY.value + e.translationY / s;
      } else {
        const next = applyPan(
          { scale: scaleShared.value, translateX: baseTX.value, translateY: baseTY.value },
          e.translationX,
          e.translationY,
        );
        translateXShared.value = next.translateX;
        translateYShared.value = next.translateY;
      }
    })
    .onEnd(() => {
      if (dragNodeIdx.value >= 0) {
        runOnJS(commitNodeDrag)(dragNodeIdx.value, dragCurrBX.value, dragCurrBY.value);
        dragNodeIdx.value = -1;
      } else {
        runOnJS(commitTransform)({
          scale: scaleShared.value,
          translateX: translateXShared.value,
          translateY: translateYShared.value,
        });
      }
    });

  // F3 — single tap selects/deselects nodes; Race ensures tap wins before pan/pinch begin.
  const tap = Gesture.Tap().onEnd((e: { x: number; y: number }) => {
    runOnJS(handleTap)({ x: e.x, y: e.y });
  });

  const composed = Gesture.Race(tap, Gesture.Simultaneous(pinch, pan));

  return {
    scaleShared,
    translateXShared,
    translateYShared,
    dragNodeIdx,
    dragCurrBX,
    dragCurrBY,
    groupTransform,
    composed,
  };
}
