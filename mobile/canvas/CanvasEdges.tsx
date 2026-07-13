/**
 * Skia edges consume committed node positions and transient drag SharedValues directly.
 * Traceability: phase-3-m3-canvas-sdd.md §§4, 5, 7, 9; ADR-0013;
 * phase-3-m3b-canvas-feature-parity-sdd.md §5.1.
 */
import React, { useMemo } from 'react';
import { Platform, StyleSheet } from 'react-native';
import {
  Canvas, DashPathEffect, Group, Path, Text as SkiaText, matchFont,
} from '@shopify/react-native-skia';
import { useDerivedValue } from 'react-native-reanimated';
import type { SharedValue } from 'react-native-reanimated';

import type { Point } from './coordinateSystem';
import type { CanvasEdge } from './SkiaCanvas';
import { edgeLabelLayout, edgeStyleForKind } from './edgeRendering';

export interface CanvasEdgesProps {
  nodePositions: Record<string, Point>;
  nodeIndexById: Readonly<Record<string, number>>;
  edges: CanvasEdge[];
  visibleEdges: CanvasEdge[];
  visIds: Set<string>;
  groupTransform: SharedValue<any>;
  dragNodeIdxShared: SharedValue<number>;
  dragCurrBXShared: SharedValue<number>;
  dragCurrBYShared: SharedValue<number>;
}

interface ReactiveEndpoints {
  source: Point;
  target: Point;
  sourceIdx: number;
  targetIdx: number;
  dragNodeIdxShared: SharedValue<number>;
  dragCurrBXShared: SharedValue<number>;
  dragCurrBYShared: SharedValue<number>;
}

function endpointValues(props: ReactiveEndpoints) {
  'worklet';
  const draggedIdx = props.dragNodeIdxShared.value;
  return {
    sx: draggedIdx === props.sourceIdx ? props.dragCurrBXShared.value : props.source.x,
    sy: draggedIdx === props.sourceIdx ? props.dragCurrBYShared.value : props.source.y,
    tx: draggedIdx === props.targetIdx ? props.dragCurrBXShared.value : props.target.x,
    ty: draggedIdx === props.targetIdx ? props.dragCurrBYShared.value : props.target.y,
  };
}

function ReactiveEdgePath(props: ReactiveEndpoints & { edgeKind: string }) {
  const path = useDerivedValue(() => {
    const { sx, sy, tx, ty } = endpointValues(props);
    const midY = (sy + ty) / 2;
    return `M ${sx} ${sy} C ${sx} ${midY} ${tx} ${midY} ${tx} ${ty}`;
  });
  const style = edgeStyleForKind(props.edgeKind);
  return (
    <Path path={path} style="stroke" strokeWidth={style.dashed ? 1.5 : 2} color="#5a5a72">
      {style.dashed && <DashPathEffect intervals={style.dashIntervals} />}
    </Path>
  );
}

function ReactiveEdgeLabel(props: ReactiveEndpoints & { text: string; font: any }) {
  const labelX = useDerivedValue(() => {
    const { sx, tx } = endpointValues(props);
    return (sx + tx) / 2;
  });
  const labelY = useDerivedValue(() => {
    const { sy, ty } = endpointValues(props);
    return (sy + ty) / 2;
  });
  return <SkiaText
    x={labelX}
    y={labelY}
    text={edgeLabelLayout(props.source, props.target, props.text).displayText}
    font={props.font}
    color="#5a5a72"
  />;
}

export function CanvasEdges({
  nodePositions, nodeIndexById, edges, visibleEdges, visIds, groupTransform,
  dragNodeIdxShared, dragCurrBXShared, dragCurrBYShared,
}: CanvasEdgesProps) {
  const labelFont = useMemo(() => {
    try {
      return matchFont({
        fontFamily: Platform.OS === 'ios' ? 'Helvetica' : 'sans-serif', fontSize: 11,
      });
    } catch {
      return null;
    }
  }, []);

  const shared = { dragNodeIdxShared, dragCurrBXShared, dragCurrBYShared };
  const edgePaths = visibleEdges.flatMap((edge) => {
    const source = nodePositions[edge.source_node_id];
    const target = nodePositions[edge.target_node_id];
    return source && target ? [{
      edge, source, target,
      sourceIdx: nodeIndexById[edge.source_node_id] ?? -2,
      targetIdx: nodeIndexById[edge.target_node_id] ?? -2,
    }] : [];
  });
  const labels = edges.flatMap((edge) => {
    if (!edge.label || !visIds.has(edge.source_node_id)) return [];
    const source = nodePositions[edge.source_node_id];
    const target = nodePositions[edge.target_node_id];
    return source && target ? [{
      edge, source, target,
      sourceIdx: nodeIndexById[edge.source_node_id] ?? -2,
      targetIdx: nodeIndexById[edge.target_node_id] ?? -2,
    }] : [];
  });

  return (
    <Canvas style={StyleSheet.absoluteFill}>
      <Group transform={groupTransform}>
        {edgePaths.map((item) => <ReactiveEdgePath
          key={item.edge.edge_id}
          {...item}
          {...shared}
          edgeKind={item.edge.edge_kind}
        />)}
        {labelFont ? labels.map((item) => <ReactiveEdgeLabel
          key={`label-${item.edge.edge_id}`}
          {...item}
          {...shared}
          text={item.edge.label!}
          font={labelFont}
        />) : null}
      </Group>
    </Canvas>
  );
}
