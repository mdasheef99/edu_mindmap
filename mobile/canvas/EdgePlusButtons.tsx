/**
 * EdgePlusButtons — Question Discovery edge-`+` affordances (M3-B SDD §5.2; MVP §4.4 L269–285).
 *
 * Native View touch targets (≥ 44×44pt, MVP L277) on the node's left/right vertical-edge
 * midpoints (screen anchors from edgePlusButtonPositions — ADR-0013, no inline seam math).
 * Pressing one POSTs the edge offer-set request (EdgeOfferSetRequest: session_id,
 * source_node_id, thread_context_id) — identical contract to the phrase flow; the client
 * never fires offer_set_* itself, and the request carries no analytic fields (Category
 * Invisibility). The returned offer set is handed up via onOfferSet for the popup to render.
 *
 * When `disabled` (node hard-limit reached, F6) the buttons render muted and do not fire.
 *
 * Traceability: phase-3-m3b-canvas-feature-parity-sdd.md §5.2, §5.5; adr-log-02.md ADR-0013;
 * backend/app/api/student/offer_sets.py POST /v1/student/offer-sets/edge.
 */

/**
 * EdgePlusButtons — Question Discovery edge-`+` affordances (M3-B SDD §5.2; MVP §4.4 L269–285).
 *
 * Positions itself from the same UI-thread shared values as NodeChip (§5, ADR-0013) so the
 * buttons track the live viewport during pan/pinch without waiting for a gesture-commit
 * React re-render. Each button is wrapped in an Animated.View driven by useAnimatedStyle;
 * the Pressable inside provides the touch target and appearance.
 *
 * Traceability: phase-3-m3b-canvas-feature-parity-sdd.md §5.2, §5.5; adr-log-02.md ADR-0013.
 */

import React, { useEffect, useRef, useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import Animated, { useAnimatedStyle } from 'react-native-reanimated';
import type { SharedValue } from 'react-native-reanimated';
import { boardToCanvas } from './coordinateSystem';
import { OverlayNode, NODE_SIZE } from './nodeOverlay';

export interface EdgePlusButtonsProps {
  node: OverlayNode;
  /** Index of this node in the live node list — matches dragNodeIdxShared (§7 drag path). */
  nodeIdx: number;
  /** Live UI-thread shared values — same objects passed to NodeChip (§5 reactive path). */
  scaleShared: SharedValue<number>;
  translateXShared: SharedValue<number>;
  translateYShared: SharedValue<number>;
  /** Live node-drag shared values — same objects passed to NodeChip so the buttons track
   *  the chip during an active drag instead of waiting for the gesture-commit re-render. */
  dragNodeIdxShared: SharedValue<number>;
  dragCurrBXShared: SharedValue<number>;
  dragCurrBYShared: SharedValue<number>;
  nodeSize?: [number, number];
  apiBaseUrl: string;
  authorizationToken?: string;
  sessionId: string;
  threadContextId: string;
  disabled?: boolean;
  onRequestStart?: () => number | null;
  onOfferSet?: (offerSet: unknown, requestGeneration?: number) => void;
  onError?: (error: unknown, requestGeneration?: number) => void;
}

const TOUCH = 44; // MVP L277 minimum touch target

export function EdgePlusButtons({
  node,
  nodeIdx,
  scaleShared,
  translateXShared,
  translateYShared,
  dragNodeIdxShared,
  dragCurrBXShared,
  dragCurrBYShared,
  nodeSize = NODE_SIZE,
  apiBaseUrl,
  authorizationToken,
  sessionId,
  threadContextId,
  disabled = false,
  onRequestStart,
  onOfferSet,
  onError,
}: EdgePlusButtonsProps) {
  // Board-space anchors for left/right chip edges (constant per render; update when node moves).
  const halfW = nodeSize[0] / 2;
  const bx = node.position.x;
  const by = node.position.y;

  // useAnimatedStyle runs on the UI thread each frame so buttons track live pan/pinch (§5) and,
  // while this node is being dragged, follow the live drag board position like NodeChip (§7).
  const leftStyle = useAnimatedStyle(() => {
    const isDragging = dragNodeIdxShared.value === nodeIdx;
    const cx = isDragging ? dragCurrBXShared.value : bx;
    const cy = isDragging ? dragCurrBYShared.value : by;
    const pos = boardToCanvas(cx - halfW, cy, {
      scale: scaleShared.value,
      translateX: translateXShared.value,
      translateY: translateYShared.value,
    });
    return { position: 'absolute' as const, left: pos.x - TOUCH / 2, top: pos.y - TOUCH / 2 };
  });

  const rightStyle = useAnimatedStyle(() => {
    const isDragging = dragNodeIdxShared.value === nodeIdx;
    const cx = isDragging ? dragCurrBXShared.value : bx;
    const cy = isDragging ? dragCurrBYShared.value : by;
    const pos = boardToCanvas(cx + halfW, cy, {
      scale: scaleShared.value,
      translateX: translateXShared.value,
      translateY: translateYShared.value,
    });
    return { position: 'absolute' as const, left: pos.x - TOUCH / 2, top: pos.y - TOUCH / 2 };
  });

  const [requestState, setRequestState] = useState<{
    phase: 'idle' | 'loading' | 'failed'; side: 'left' | 'right' | null;
  }>({ phase: 'idle', side: null });
  const busyRef = useRef(false);
  const mountedRef = useRef(false);
  const requestIdRef = useRef(0);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      requestIdRef.current += 1;
      busyRef.current = false;
    };
  }, []);

  async function launch(side: 'left' | 'right') {
    if (disabled || busyRef.current) return;
    const requestGeneration = onRequestStart?.();
    if (requestGeneration === null) return;
    busyRef.current = true;
    const requestId = ++requestIdRef.current;
    setRequestState({ phase: 'loading', side });
    try {
      const response = await fetch(`${apiBaseUrl}/v1/student/offer-sets/edge`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(authorizationToken ? { Authorization: `Bearer ${authorizationToken}` } : {}),
        },
        body: JSON.stringify({
          session_id: sessionId,
          source_node_id: node.node_id,
          thread_context_id: threadContextId,
        }),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      const offerSet = await response.json();
      if (!mountedRef.current || requestId !== requestIdRef.current) return;
      busyRef.current = false;
      setRequestState({ phase: 'idle', side: null });
      onOfferSet?.(offerSet, requestGeneration);
    } catch (err) {
      if (!mountedRef.current || requestId !== requestIdRef.current) return;
      busyRef.current = false;
      setRequestState({ phase: 'failed', side });
      onError?.(err, requestGeneration);
    }
  }

  const isLoading = requestState.phase === 'loading';
  function renderButton(side: 'left' | 'right', style: object) {
    const isActive = requestState.side === side;
    const retry = requestState.phase === 'failed' && isActive;
    const label = isLoading && isActive ? 'Loading questions'
      : retry ? `Retry loading questions from ${side} edge` : `Explore from ${side} edge`;
    return (
      <Animated.View testID={`edge-plus-${side}-wrapper`} style={style}>
        <Pressable
          testID={`edge-plus-${side}`}
          accessibilityRole="button"
          accessibilityLabel={label}
          disabled={disabled || isLoading || (requestState.phase === 'failed' && !isActive)}
          onPress={() => { void launch(side); }}
          style={styles.touchTarget}
        >
          <View style={[styles.glyphCircle, (disabled || isLoading) && styles.disabled]}>
            <Text style={styles.glyph}>+</Text>
          </View>
        </Pressable>
        {isActive && requestState.phase !== 'idle' ? (
          <View pointerEvents="none" style={[styles.feedback,
            side === 'left' ? styles.feedbackLeft : styles.feedbackRight]}>
            <Text accessibilityLiveRegion="polite" style={styles.feedbackText}>
              {isLoading ? 'Loading questions…' : 'Questions could not load. Tap to retry.'}
            </Text>
          </View>
        ) : null}
      </Animated.View>
    );
  }

  return (
    <>
      {renderButton('left', leftStyle)}
      {renderButton('right', rightStyle)}
    </>
  );
}

// The Pressable keeps the MVP L277 ≥44pt touch target; the visible circle (GLYPH) is smaller
// and centered within it so the affordance reads as a compact dot on the chip's vertical edge.
const GLYPH = 24;

const styles = StyleSheet.create({
  touchTarget: {
    width: TOUCH,
    height: TOUCH,
    justifyContent: 'center',
    alignItems: 'center',
  },
  glyphCircle: {
    width: GLYPH,
    height: GLYPH,
    borderRadius: GLYPH / 2,
    backgroundColor: '#4f46e5',
    justifyContent: 'center',
    alignItems: 'center',
  },
  disabled: { backgroundColor: '#c7c7d1' },
  glyph: { color: '#ffffff', fontSize: 15, fontWeight: '700', lineHeight: 17 },
  feedback: {
    position: 'absolute', top: TOUCH, width: 150, paddingHorizontal: 8, paddingVertical: 5,
    borderRadius: 6, backgroundColor: 'rgba(31, 41, 55, 0.92)',
  },
  feedbackLeft: { left: 0 },
  feedbackRight: { right: 0 },
  feedbackText: { color: '#ffffff', fontSize: 12, lineHeight: 16 },
});
