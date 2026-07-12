/**
 * CanvasEdges — Skia edge geometry + labels (M3 SDD §9; M3-B SDD §5.1).
 *
 * Renders all visible edges as cubic Bézier paths inside a reactive <Group> whose transform is
 * driven by a Reanimated derived value. Only ai_path edges carry labels; labels are drawn at
 * the Bézier midpoint and are culled with their source node. Manual_reference edges render as
 * dashed paths so a learner-created reference is never misread as exploration progression
 * (session-path-data-contract.md §7).
 *
 * Traceability: phase-3-m3-canvas-sdd.md §4, §9; phase-3-m3b-canvas-feature-parity-sdd.md §5.1;
 * adr-log-02.md ADR-0013; session-path-data-contract.md §7.
 */

import React, { useMemo } from 'react';
import { Platform, StyleSheet } from 'react-native';
import { Canvas, DashPathEffect, Group, Path, Text as SkiaText, matchFont } from '@shopify/react-native-skia';
import type { SharedValue } from 'react-native-reanimated';
import { Point } from './coordinateSystem';
import type { CanvasEdge } from './SkiaCanvas';
import { cubicBezierPath, edgeStyleForKind, edgeLabelLayout } from './edgeRendering';

export interface CanvasEdgesProps {
  /** Board-space positions indexed by node_id. */
  nodePositions: Record<string, Point>;
  /** All edges in the canvas (used for label culling). */
  edges: CanvasEdge[];
  /** Edges whose at least one endpoint is visible (used for path drawing). */
  visibleEdges: CanvasEdge[];
  /** Set of visible node ids (used to drop labels whose source is off-screen). */
  visIds: Set<string>;
  /** Reactive UI-thread transform for the Skia <Group>. */
  groupTransform: SharedValue<any>;
}

export function CanvasEdges({
  nodePositions,
  edges,
  visibleEdges,
  visIds,
  groupTransform,
}: CanvasEdgesProps) {
  // F1 — Skia font for edge labels (mocked in CI; matchFont returns {} from the test stub).
  const labelFont = useMemo(() => {
    try {
      return matchFont({
        fontFamily: Platform.OS === 'ios' ? 'Helvetica' : 'sans-serif',
        fontSize: 11,
      });
    } catch {
      return null;
    }
  }, []);

  // Board-space SVG path strings — passed directly to <Path path={string} /> (M3 SDD §9).
  const edgePaths = useMemo(
    () =>
      visibleEdges.map((edge) => {
        const src = nodePositions[edge.source_node_id];
        const tgt = nodePositions[edge.target_node_id];
        if (!src || !tgt) return null;
        const svgPath = cubicBezierPath(src, tgt);
        const style = edgeStyleForKind(edge.edge_kind);
        return { edge_id: edge.edge_id, svgPath, style };
      }),
    [visibleEdges, nodePositions],
  );

  // F1 — edge labels: only for edges whose source node is visible and a label is set.
  const edgeLabels = useMemo(
    () =>
      edges.flatMap((e) => {
        if (!e.label || !visIds.has(e.source_node_id)) return [];
        const src = nodePositions[e.source_node_id];
        const tgt = nodePositions[e.target_node_id];
        if (!src || !tgt) return [];
        return [{ edge_id: e.edge_id, layout: edgeLabelLayout(src, tgt, e.label) }];
      }),
    [edges, nodePositions, visIds],
  );

  return (
    <Canvas style={StyleSheet.absoluteFill}>
      <Group transform={groupTransform}>
        {edgePaths.map((ep) =>
          ep ? (
            <Path
              key={ep.edge_id}
              path={ep.svgPath}
              style="stroke"
              strokeWidth={ep.style.dashed ? 1.5 : 2}
              color="#5a5a72"
            >
              {ep.style.dashed && <DashPathEffect intervals={ep.style.dashIntervals} />}
            </Path>
          ) : null,
        )}
        {/* F1 — edge labels at Bézier midpoints (board space, scaled with Group) */}
        {labelFont
          ? edgeLabels.map((el) => (
              <SkiaText
                key={`lbl-${el.edge_id}`}
                x={el.layout.position.x}
                y={el.layout.position.y}
                text={el.layout.displayText}
                font={labelFont}
                color="#5a5a72"
              />
            ))
          : null}
      </Group>
    </Canvas>
  );
}
