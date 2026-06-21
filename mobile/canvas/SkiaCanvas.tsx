/**
 * SkiaCanvas — M3 SDD §8/§9 hybrid canvas component.
 *
 * Skia draws the board and edges (§9); Native Views overlay node content (ADR-0013).
 * Pinch+pan are composed via Gesture.Simultaneous (§8). Ephemeral transform lives in
 * Reanimated SharedValues; Zustand (canonical store) is written once on gesture end
 * via runOnJS (§5/§7 dual-state rule). Scale clamped to [0.25, 4.0] via clampScale (§8).
 * Edges are viewport-culled before rendering (§9). Coordinate seam strictly via §4 module.
 *
 * Traceability: phase-3-m3-canvas-sdd.md §4, §5, §7, §8, §9; adr-log.md ADR-0013.
 */

import React, { useMemo } from 'react';
import { StyleSheet, View } from 'react-native';
import { Canvas, Path, Skia } from '@shopify/react-native-skia';
import { Gesture, GestureDetector, GestureHandlerRootView } from 'react-native-gesture-handler';
import { runOnJS, useSharedValue } from 'react-native-reanimated';
import { CanvasTransform, boardToCanvas, Point } from './coordinateSystem';
import { applyPinch, applyPan } from './gestureTransform';
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

// ── component ─────────────────────────────────────────────────────────────────

export function SkiaCanvas({
  nodes,
  edges,
  screen,
  transform,
  onTransformEnd,
}: SkiaCanvasProps) {
  // Ephemeral UI-thread transform — SharedValues updated every gesture frame (§5).
  const scale = useSharedValue(transform.scale);
  const translateX = useSharedValue(transform.translateX);
  const translateY = useSharedValue(transform.translateY);
  // Base snapshots captured on gesture start so relative deltas are correct.
  const baseScale = useSharedValue(transform.scale);
  const baseTX = useSharedValue(transform.translateX);
  const baseTY = useSharedValue(transform.translateY);

  /** JS-thread commit called via runOnJS on gesture end (§7). */
  function commitTransform(t: CanvasTransform) {
    scale.value = t.scale;
    translateX.value = t.translateX;
    translateY.value = t.translateY;
    onTransformEnd?.(t);
  }

  // ── Gesture.Simultaneous(pinch, pan) — §8 ────────────────────────────────
  const pinch = Gesture.Pinch()
    .onStart(() => {
      baseScale.value = scale.value;
      baseTX.value = translateX.value;
      baseTY.value = translateY.value;
    })
    .onUpdate((e) => {
      const next = applyPinch(
        { scale: baseScale.value, translateX: baseTX.value, translateY: baseTY.value },
        e.scale,
        { x: e.focalX, y: e.focalY },
      );
      scale.value = next.scale;
      translateX.value = next.translateX;
      translateY.value = next.translateY;
    })
    .onEnd(() => {
      runOnJS(commitTransform)({
        scale: scale.value,
        translateX: translateX.value,
        translateY: translateY.value,
      });
    });

  const pan = Gesture.Pan()
    .onStart(() => {
      baseTX.value = translateX.value;
      baseTY.value = translateY.value;
    })
    .onUpdate((e) => {
      const next = applyPan(
        { scale: scale.value, translateX: baseTX.value, translateY: baseTY.value },
        e.translationX,
        e.translationY,
      );
      translateX.value = next.translateX;
      translateY.value = next.translateY;
    })
    .onEnd(() => {
      runOnJS(commitTransform)({
        scale: scale.value,
        translateX: translateX.value,
        translateY: translateY.value,
      });
    });

  const composed = Gesture.Simultaneous(pinch, pan);

  // ── render data (JS-side snapshot of shared values per JS render) ─────────
  const currentTransform: CanvasTransform = {
    scale: scale.value,
    translateX: translateX.value,
    translateY: translateY.value,
  };

  const nodePositions = useMemo(
    () => Object.fromEntries(nodes.map((n) => [n.node_id, n.position])),
    [nodes],
  );

  const viewport = computeBoardViewport(currentTransform, screen);
  const visibleEdges = useMemo(
    () => cullEdges(edges, nodePositions, viewport),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [edges, nodePositions, viewport.minX, viewport.minY, viewport.maxX, viewport.maxY],
  );

  // Build Skia path objects from the pure-function SVG strings (§9).
  // Guarded: Skia.Path is undefined in the test environment (native mock → {}).
  const edgePaths = useMemo(() => {
    return visibleEdges.map((edge) => {
      const src = nodePositions[edge.source_node_id];
      const tgt = nodePositions[edge.target_node_id];
      if (!src || !tgt) return null;
      const p0 = boardToCanvas(src.x, src.y, currentTransform);
      const p1 = boardToCanvas(tgt.x, tgt.y, currentTransform);
      const svgStr = cubicBezierPath(p0, p1);
      const style = edgeStyleForKind(edge.edge_kind);
      const skiaPath = (Skia as any).Path?.MakeFromSVGString?.(svgStr) ?? null;
      return { edge_id: edge.edge_id, skiaPath, style };
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [visibleEdges, nodePositions, currentTransform.scale, currentTransform.translateX, currentTransform.translateY]);

  return (
    <GestureHandlerRootView style={styles.root}>
      <GestureDetector gesture={composed}>
        <View style={styles.root}>
          {/* Skia layer — Bézier edges (§9) */}
          <Canvas style={StyleSheet.absoluteFill}>
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
          </Canvas>

          {/* Native node overlay — ADR-0013 hybrid boundary */}
          {nodes.map((node) => {
            const pos = boardToCanvas(node.position.x, node.position.y, currentTransform);
            return (
              <View
                key={node.node_id}
                style={[styles.nodeChip, { left: pos.x - 40, top: pos.y - 20 }]}
              />
            );
          })}
        </View>
      </GestureDetector>
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1 },
  nodeChip: { position: 'absolute', width: 80, height: 40, backgroundColor: '#f0f0f8' },
});
