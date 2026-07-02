/**
 * NodeLimitBanner — learner-facing node-limit chrome (M3-B SDD §5.5; M3 SDD §11).
 *
 * Renders nothing below the warning threshold; a non-blocking warning at
 * CANVAS_NODE_WARNING_COUNT; and an additional "limit reached" notice once creation is
 * blocked at CANVAS_NODE_HARD_LIMIT. The backend 409 guard remains the authority — this is a
 * Native View overlay (ADR-0013) carrying no analytic state (Category Invisibility).
 *
 * Traceability: phase-3-m3b-canvas-feature-parity-sdd.md §5.5; phase-3-m3-canvas-sdd.md §11.
 */

import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import {
  nodeLimitState,
  CANVAS_NODE_HARD_LIMIT,
} from './nodeLimits';

export interface NodeLimitBannerProps {
  activeCount: number;
}

export function NodeLimitBanner({ activeCount }: NodeLimitBannerProps) {
  const { showWarning, creationBlocked } = nodeLimitState(activeCount);
  if (!showWarning) return null;
  return (
    <View testID="node-limit-banner" style={styles.banner} pointerEvents="none">
      <Text style={styles.warningText}>
        {activeCount} nodes — approaching the {CANVAS_NODE_HARD_LIMIT}-node limit.
      </Text>
      {creationBlocked ? (
        <Text testID="node-limit-blocked" style={styles.blockedText}>
          Node limit reached — new branches are disabled.
        </Text>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  banner: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    paddingVertical: 8,
    paddingHorizontal: 12,
    backgroundColor: '#fef3c7',
    borderBottomWidth: 1,
    borderBottomColor: '#f59e0b',
  },
  warningText: { fontSize: 12, color: '#92400e', fontWeight: '600' },
  blockedText: { fontSize: 12, color: '#b91c1c', fontWeight: '700', marginTop: 2 },
});
