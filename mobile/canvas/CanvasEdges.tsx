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
import { useDerivedValue } from 'react-native-reanimated';
import type { SharedValue } from 'react-native-reanimated';
import { Point } from './coordinateSystem';
import type { CanvasEdge } from './SkiaCanvas';
import { edgeStyleForKind, edgeLabelLayout } from './edgeRendering';

export interface CanvasEdgesProps {
  /** Board-space positions indexed by node_id. */
  nodePositions: Record<string, Point>;
  /** Node indices matching the gesture hook's live-node array. */
  nodeIndexById: Readonly<Record<string, number>>;
  /** All edges in the canvas (used for label culling). */
  edges: CanvasEdge[];
  /** Edges whose at least one endpoint is visible (used for path drawing). */
  visibleEdges: CanvasEdge[];
  /** Set of visible node ids (used to drop labels whose source is off-screen). */
  visIds: Set<string>;
  /** Reactive UI-thread transform for the Skia <Group>. */
  groupTransform: SharedValue<any>;
  /** Active node-drag SharedValues; also consumed directly by NodeChip. */
  dragNodeIdxShared: SharedValue<number>;
  dragCurrBXShared: SharedValue<number>;
  dragCurrBYShared: SharedValue<number>;
}

interface ReactiveEndpointsProps {
  source: Point;
  target: Point;
  sourceIdx: number;
  targetIdx: number;
  dragNodeIdxShared: SharedValue<number>;
  dragCurrBXShared: SharedValue<number>;
  dragCurrBYShared: SharedValue<number>;
}

function useReactivePath(props: ReactiveEndpointsProps) {
  const { source, target, sourceIdx, targetIdx, dragNodeIdxShared, dragCurrBXShared, dragCurrBYShared } = props;
  return useDerivedValue(() => {
    const draggedIdx = dragNodeIdxShared.value;
    const sx = draggedIdx === sourceIdx ? dragCurrBXShared.value : source.x;
    const sy = draggedIdx === sourceIdx ? dragCurrBYShared.value : source.y;
    const tx = draggedIdx === targetIdx ? dragCurrBXShared.value : target.x;
    const ty = draggedIdx === targetIdx ? dragCurrBYShared.value : target.y;
    const midY = (sy + ty) / 2;
    return `M ${sx} ${sy} C ${sx} ${midY} ${tx} ${midY} ${tx} ${ty}`;
  });
}

function useReactiveLabelPosition(props: ReactiveEndpointsProps) {
  const { source, target, sourceIdx, targetIdx, dragNodeIdxShared, dragCurrBXShared, dragCurrBYShared } = props;
  const labelX = useDerivedValue(() => {
    const draggedIdx = dragNodeIdxShared.value;
    const sx = draggedIdx === sourceIdx ? dragCurrBXShared.value : source.x;
    const tx = draggedIdx === targetIdx ? dragCurrBXShared.value : target.x;
    return (sx + tx) / 2;
  });
  const labelY = useDerivedValue(() => {
    const draggedIdx = dragNodeIdxShared.value;
    const sy = draggedIdx === sourceIdx ? dragCurrBYShared.value : source.y;
    const ty = draggedIdx === targetIdx ? dragCurrBYShared.value : target.y;
    return (sy + ty) / 2;
  });
  return { labelX, labelY };
}

function ReactiveEdgePath({
  source,
  target,
  sourceIdx,
  targetIdx,
  dragNodeIdxShared,
  dragCurrBXShared,
  dragCurrBYShared,
  edgeKind,
}: ReactiveEndpointsProps & { edgeKind: string }) {
  const path = useReactivePath({
    source, target, sourceIdx, targetIdx, dragNodeIdxShared, dragCurrBXShared, dragCurrBYShared,
  });
  const style = edgeStyleForKind(edgeKind);
  return (
    <Path
      path={path}
      style="stroke"
      strokeWidth={style.dashed ? 1.5 : 2}
      color="#5a5a72"
    >
      {style.dashed && <DashPathEffect intervals={style.dashIntervals} />}
    </Path>
  );
}

function ReactiveEdgeLabel({
  source,
  target,
  sourceIdx,
  targetIdx,
  dragNodeIdxShared,
  dragCurrBXShared,
  dragCurrBYShared,
  text,
  font,
}: ReactiveEndpointsProps & { text: string; font: any }) {
  const reactive = useReactiveLabelPosition({
    source, target, sourceIdx, targetIdx, dragNodeIdxShared, dragCurrBXShared, dragCurrBYShared,
  });
  const displayText = edgeLabelLayout(source, target, text).displayText;
  return (
    <SkiaText
      x={reactive.labelX}
      y={reactive.labelY}
      text={displayText}
      font={font}
      color="#5a5a72"
    />
  );
}

export function CanvasEdges({
  nodePositions,
  nodeIndexById,
  edges,
  visibleEdges,
  visIds,
  groupTransform,
  dragNodeIdxShared,
  dragCurrBXShared,
  dragCurrBYShared,
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

  // Static endpoint metadata; only the derived Skia props read transient drag SharedValues.
  const edgePaths = useMemo(
    () =>
      visibleEdges.map((edge) => {
        const src = nodePositions[edge.source_node_id];
        const tgt = nodePositions[edge.target_node_id];
        if (!src || !tgt) return null;
        return {
          edge,
          src,
          tgt,
          sourceIdx: nodeIndexById[edge.source_node_id] ?? -2,
          targetIdx: nodeIndexById[edge.target_node_id] ?? -2,
        };
      }),
    [visibleEdges, nodePositions, nodeIndexById],
  );

  // F1 — edge labels: only for edges whose source node is visible and a label is set.
  const edgeLabels = useMemo(
    () =>
      edges.flatMap((e) => {
        if (!e.label || !visIds.has(e.source_node_id)) return [];
        const src = nodePositions[e.source_node_id];
        const tgt = nodePositions[e.target_node_id];
        if (!src || !tgt) return [];
        return [{
          edge: e,
          src,
          tgt,
          sourceIdx: nodeIndexById[e.source_node_id] ?? -2,
          targetIdx: nodeIndexById[e.target_node_id] ?? -2,
        }];
      }),
    [edges, nodePositions, visIds, nodeIndexById],
  );

  return (
    <Canvas style={StyleSheet.absoluteFill}>
      <Group transform={groupTransform}>
        {edgePaths.map((ep) => ep ? (
          <ReactiveEdgePath
            key={ep.edge.edge_id}
            source={ep.src}
            target={ep.tgt}
            sourceIdx={ep.sourceIdx}
            targetIdx={ep.targetIdx}
            dragNodeIdxShared={dragNodeIdxShared}
            dragCurrBXShared={dragCurrBXShared}
            dragCurrBYShared={dragCurrBYShared}
            edgeKind={ep.edge.edge_kind}
          />
        ) : null)}
        {/* F1 — edge labels at Bézier midpoints (board space, scaled with Group) */}
        {labelFont
          ? edgeLabels.map((el) => (
              <ReactiveEdgeLabel
                key={`lbl-${el.edge.edge_id}`}
                source={el.src}
                target={el.tgt}
                sourceIdx={el.sourceIdx}
                targetIdx={el.targetIdx}
                dragNodeIdxShared={dragNodeIdxShared}
                dragCurrBXShared={dragCurrBXShared}
                dragCurrBYShared={dragCurrBYShared}
                text={el.edge.label!}
                font={labelFont}
              />
            ))
          : null}
      </Group>
    </Canvas>
  );
}
