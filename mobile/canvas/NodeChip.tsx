/**
 * NodeChip — animated native overlay for a single canvas node (M3 SDD §9, ADR-0013).
 *
 * Position and scale are driven by Reanimated SharedValues on the UI thread, so the chip
 * tracks live pan/zoom without a React re-render per gesture frame (Defect A fix). The chip
 * is visually distinct: border + background + node label + placeholder body (Defect C fix).
 *
 * Traceability: phase-3-m3-canvas-sdd.md §4, §5, §8, §9; adr-log-02.md ADR-0013.
 */

import React from 'react';
import { StyleSheet, Text } from 'react-native';
import Animated, { useAnimatedStyle } from 'react-native-reanimated';
import type { SharedValue } from 'react-native-reanimated';
import { boardToCanvas } from './coordinateSystem';
import type { CanvasNode } from './SkiaCanvas';
import { CHIP_W, CHIP_H } from './chipConstants';

export interface NodeChipProps {
  node: CanvasNode;
  nodeIdx: number;
  scaleShared: SharedValue<number>;
  translateXShared: SharedValue<number>;
  translateYShared: SharedValue<number>;
  /** Shared index of the node currently being dragged; -1 = none (M3 SDD §7). */
  dragNodeIdxShared: SharedValue<number>;
  dragCurrBXShared: SharedValue<number>;
  dragCurrBYShared: SharedValue<number>;
}

export function NodeChip({
  node,
  nodeIdx,
  scaleShared,
  translateXShared,
  translateYShared,
  dragNodeIdxShared,
  dragCurrBXShared,
  dragCurrBYShared,
}: NodeChipProps) {
  const title = node.title?.trim() || compactNodeId(node.node_id);
  const body = node.content?.trim() || '';

  // While this chip is being dragged, board position is taken from live drag shared values (§7).
  const animStyle = useAnimatedStyle(() => {
    const scale = scaleShared.value;
    const isDragging = dragNodeIdxShared.value === nodeIdx;
    const bx = isDragging ? dragCurrBXShared.value : node.position.x;
    const by = isDragging ? dragCurrBYShared.value : node.position.y;
    const pos = boardToCanvas(bx, by, {
      scale,
      translateX: translateXShared.value,
      translateY: translateYShared.value,
    });
    return { left: pos.x - CHIP_W / 2, top: pos.y - CHIP_H / 2, transform: [{ scale }] };
  });
  return (
    <Animated.View pointerEvents="none" style={[styles.nodeChip, animStyle]}>
      <Text style={styles.nodeLabel}>{title}</Text>
      {body ? <Text style={styles.nodeBody}>{body}</Text> : null}
    </Animated.View>
  );
}

function compactNodeId(nodeId: string): string {
  return nodeId.split('-')[0] || nodeId;
}

const styles = StyleSheet.create({
  nodeChip: {
    position: 'absolute',
    width: CHIP_W,
    height: CHIP_H,
    backgroundColor: '#e8e4f8',
    borderWidth: 1,
    borderColor: '#9090b8',
    borderRadius: 6,
    padding: 8,
    overflow: 'hidden',
  },
  nodeLabel: { fontSize: 13, color: '#3a3a5c', fontWeight: '700', marginBottom: 4 },
  nodeBody: { fontSize: 10, color: '#3a3a5c', lineHeight: 13 },
});
