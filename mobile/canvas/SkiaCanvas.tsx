/**
 * SkiaCanvas — M3 SDD §8/§9 hybrid canvas component (reactive rewrite 2026-06-21).
 *
 * Skia draws board edges inside a reactive <Group> whose transform is driven by
 * useDerivedValue — no React re-renders needed per gesture frame (§5, §8 Defect A fix).
 * Native NodeChip overlays use useAnimatedStyle for UI-thread position updates (ADR-0013).
 * Gesture worklets call worklet-annotated applyPinch/applyPan/boardToCanvas (Defect B fix).
 * Node chips are visually distinct: border + background + label (Defect C fix).
 * createViewportGestureController from gestureSync.ts owns the §7 write-once-on-end
 * invariant; commitTransform updates the mutable reference and fires onEnd (Defect D fix).
 *
 * Traceability: phase-3-m3-canvas-sdd.md §4, §5, §7, §8, §9, §15; adr-log-02.md ADR-0013.
 */

import React, { useRef, useMemo } from 'react';
import { StyleSheet, Text } from 'react-native';
import { Canvas, Group, Path, Skia } from '@shopify/react-native-skia';
import { Gesture, GestureDetector, GestureHandlerRootView } from 'react-native-gesture-handler';
import Animated, {
  runOnJS,
  useAnimatedStyle,
  useDerivedValue,
  useSharedValue,
} from 'react-native-reanimated';
import { CanvasTransform, boardToCanvas, Point } from './coordinateSystem';
import { applyPinch, applyPan } from './gestureTransform';
import { createViewportGestureController } from './gestureSync';
import { computeBoardViewport, cullEdges, ScreenSize } from './viewportCulling';
import { cubicBezierPath, edgeStyleForKind } from './edgeRendering';

// ── public types ──────────────────────────────────────────────────────────────

export interface CanvasNode {
  node_id: string;
  parent_node_id: string | null;
  position: Point;
}

export interface CanvasEdge {
  edge_id: string;
  source_node_id: string;
  target_node_id: string;
  edge_kind: string;
}

export interface SkiaCanvasProps {
  nodes: CanvasNode[];
  edges: CanvasEdge[];
  screen: ScreenSize;
  transform: CanvasTransform;
  /** Called once on gesture end with the new canonical transform (§7 dual-state). */
  onTransformEnd?: (t: CanvasTransform) => void;
}

// ── node chip constants ────────────────────────────────────────────────────────
const CHIP_W = 80;
const CHIP_H = 40;

// ── NodeChip — animated native overlay (ADR-0013, Defect A + C fix) ───────────

interface NodeChipProps {
  node: CanvasNode;
  scaleShared: { value: number };
  translateXShared: { value: number };
  translateYShared: { value: number };
}

function NodeChip({ node, scaleShared, translateXShared, translateYShared }: NodeChipProps) {
  // useAnimatedStyle drives chip position on the UI thread without JS re-renders (§5).
  // boardToCanvas is worklet-annotated (coordinateSystem.ts) so it runs in this worklet (Defect B).
  const animStyle = useAnimatedStyle(() => {
    const pos = boardToCanvas(node.position.x, node.position.y, {
      scale: scaleShared.value,
      translateX: translateXShared.value,
      translateY: translateYShared.value,
    });
    return { left: pos.x - CHIP_W / 2, top: pos.y - CHIP_H / 2 };
  });
  return (
    <Animated.View style={[styles.nodeChip, animStyle]}>
      <Text style={styles.nodeLabel}>{node.node_id}</Text>
    </Animated.View>
  );
}

// ── SkiaCanvas ─────────────────────────────────────────────────────────────────

export function SkiaCanvas({ nodes, edges, screen, transform, onTransformEnd }: SkiaCanvasProps) {
  // Ephemeral UI-thread SharedValues — updated every gesture frame, never writes Zustand (§5, §7).
  const scaleShared = useSharedValue(transform.scale);
  const translateXShared = useSharedValue(transform.translateX);
  const translateYShared = useSharedValue(transform.translateY);

  // Gesture base snapshots captured on gesture start so deltas are relative to start position.
  const baseScale = useSharedValue(transform.scale);
  const baseTX = useSharedValue(transform.translateX);
  const baseTY = useSharedValue(transform.translateY);

  // §7 write-once-on-end controller (Defect D fix). Mutable ref lets commitTransform
  // update it before onEnd fires so store.setViewport receives the correct final values.
  const ctrlTransformRef = useRef<CanvasTransform>({ ...transform });
  const gestureController = useMemo(
    () =>
      createViewportGestureController({
        store: { setViewport: (t) => onTransformEnd?.(t) },
        transform: ctrlTransformRef.current,
      }),
    [], // eslint-disable-line react-hooks/exhaustive-deps
  );

  /** JS-thread commit: update mutable ref then let the controller write to the store (§7). */
  function commitTransform(t: CanvasTransform) {
    ctrlTransformRef.current.scale = t.scale;
    ctrlTransformRef.current.translateX = t.translateX;
    ctrlTransformRef.current.translateY = t.translateY;
    gestureController.onEnd();
  }

  // Skia Group reactive transform — UI-thread path, no React re-render needed (§5, Defect A fix).
  // Order: translate first (screen-space offset), then scale — matches §4 formula
  // screenX = boardX * scale + translateX.
  const groupTransform = useDerivedValue(() => [
    { translateX: translateXShared.value },
    { translateY: translateYShared.value },
    { scale: scaleShared.value },
  ]);

  // ── Gesture.Simultaneous(pinch, pan) — §8 ────────────────────────────────────
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

  const pan = Gesture.Pan()
    .onStart(() => {
      baseTX.value = translateXShared.value;
      baseTY.value = translateYShared.value;
    })
    .onUpdate((e) => {
      const next = applyPan(
        { scale: scaleShared.value, translateX: baseTX.value, translateY: baseTY.value },
        e.translationX,
        e.translationY,
      );
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

  const composed = Gesture.Simultaneous(pinch, pan);

  // ── render data: culling uses committed transform (JS-side snapshot, §9/§10) ──
  const nodePositions = useMemo(
    () => Object.fromEntries(nodes.map((n) => [n.node_id, n.position])),
    [nodes],
  );
  const viewport = useMemo(() => computeBoardViewport(transform, screen), [transform, screen]);
  const visibleEdges = useMemo(
    () => cullEdges(edges, nodePositions, viewport),
    [edges, nodePositions, viewport],
  );

  // Board-space paths — the reactive Group transform converts them to screen space (§9).
  const edgePaths = useMemo(
    () =>
      visibleEdges.map((edge) => {
        const src = nodePositions[edge.source_node_id];
        const tgt = nodePositions[edge.target_node_id];
        if (!src || !tgt) return null;
        const svgStr = cubicBezierPath(src, tgt);
        const style = edgeStyleForKind(edge.edge_kind);
        const skiaPath = (Skia as any).Path?.MakeFromSVGString?.(svgStr) ?? null;
        return { edge_id: edge.edge_id, skiaPath, style };
      }),
    [visibleEdges, nodePositions],
  );

  return (
    <GestureHandlerRootView style={styles.root}>
      <GestureDetector gesture={composed}>
        <>
          {/* Skia layer — board-space paths inside a reactive Group (§9, Defect A fix) */}
          <Canvas style={StyleSheet.absoluteFill}>
            <Group transform={groupTransform}>
              {edgePaths.map((ep) =>
                ep?.skiaPath ? (
                  <Path
                    key={ep.edge_id}
                    path={ep.skiaPath}
                    style="stroke"
                    strokeWidth={ep.style.dashed ? 1.5 : 2}
                    color="#5a5a72"
                  />
                ) : null,
              )}
            </Group>
          </Canvas>

          {/* Native node overlay — animated position, visible style + label (ADR-0013, Defect A+C fix) */}
          {nodes.map((node) => (
            <NodeChip
              key={node.node_id}
              node={node}
              scaleShared={scaleShared}
              translateXShared={translateXShared}
              translateYShared={translateYShared}
            />
          ))}
        </>
      </GestureDetector>
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1 },
  nodeChip: {
    position: 'absolute',
    width: CHIP_W,
    height: CHIP_H,
    backgroundColor: '#e8e4f8',
    borderWidth: 1,
    borderColor: '#9090b8',
    borderRadius: 6,
    justifyContent: 'center',
    alignItems: 'center',
  },
  nodeLabel: { fontSize: 11, color: '#3a3a5c', fontWeight: '600' },
});
