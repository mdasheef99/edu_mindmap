/**
 * TB2 — Question Discovery edge-`+` UI (M3-B SDD §5.2, §8; MVP §4.4 L269–285).
 *
 * edgePlusButtonPositions is a pure helper (CI-testable): it places a `+` affordance on the
 * node's left and right vertical-edge midpoints, in SCREEN space, via boardToCanvas only
 * (ADR-0013 — no inline seam math). EdgePlusButtons renders those affordances as Native View
 * touch targets ≥ 44×44pt (MVP L277) and, on press, POSTs the edge offer-set request
 * (EdgeOfferSetRequest: session_id, source_node_id, thread_context_id) — identical contract
 * to the phrase flow; the client never fires offer_set_* / phrase_selected itself.
 *
 * Category Invisibility: the request body carries no analytic fields and no tenant_id.
 *
 * RED: neither mobile/canvas/nodeOverlay.ts nor mobile/canvas/EdgePlusButtons.tsx exists.
 *
 * Traceability: phase-3-m3b-canvas-feature-parity-sdd.md §5.2, §8 TB2; MVP §4.4;
 * backend/app/api/student/offer_sets.py POST /v1/student/offer-sets/edge.
 */

// EdgePlusButtons now uses useAnimatedStyle from react-native-reanimated (shared-value driven).
// The mock must be declared before any module imports that pull in reanimated.
jest.mock('react-native-reanimated', () => {
  const { View } = require('react-native');
  return {
    __esModule: true,
    default: { View, createAnimatedComponent: (c: any) => c },
    useSharedValue: (init: any) => ({ value: init }),
    useAnimatedStyle: jest.fn((fn: () => any) => fn()),
    runOnJS: (fn: any) => fn,
  };
});

import React from 'react';
import { StyleSheet } from 'react-native';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { boardToCanvas } from '../../canvas/coordinateSystem';
import { edgePlusButtonPositions } from '../../canvas/nodeOverlay';
import { EdgePlusButtons } from '../../canvas/EdgePlusButtons';

const NODE_SIZE: [number, number] = [200, 160]; // half-width 100
const NODE = { node_id: 'n1', position: { x: 50, y: 60 } };
const IDENTITY = { scale: 1, translateX: 0, translateY: 0 };

// Shared-value stubs matching the mock's useSharedValue shape.
const SHARED_SCALE = { value: 1 };
const SHARED_TX = { value: 0 };
const SHARED_TY = { value: 0 };
// Drag shared values — idx -1 means "no node dragging", so buttons use the committed position.
const SHARED_DRAG_IDX = { value: -1 };
const SHARED_DRAG_BX = { value: 0 };
const SHARED_DRAG_BY = { value: 0 };

const PROPS = {
  node: NODE,
  nodeIdx: 0,
  scaleShared: SHARED_SCALE as any,
  translateXShared: SHARED_TX as any,
  translateYShared: SHARED_TY as any,
  dragNodeIdxShared: SHARED_DRAG_IDX as any,
  dragCurrBXShared: SHARED_DRAG_BX as any,
  dragCurrBYShared: SHARED_DRAG_BY as any,
  nodeSize: NODE_SIZE,
  apiBaseUrl: 'http://localhost:8000',
  authorizationToken: 'test-token',
  sessionId: 'session-1',
  threadContextId: 'thread-1',
};

const originalFetch = global.fetch;

describe('TB2 — edgePlusButtonPositions pure placement (SDD §5.2)', () => {
  it('test_plus_buttons_on_left_and_right_edges', () => {
    const { left, right } = edgePlusButtonPositions(NODE, IDENTITY, NODE_SIZE);
    // Left/right midpoints are board (x ∓ halfWidth, y) projected through boardToCanvas.
    expect(left).toEqual(boardToCanvas(50 - 100, 60, IDENTITY));
    expect(right).toEqual(boardToCanvas(50 + 100, 60, IDENTITY));
  });
});

describe('TB2 — EdgePlusButtons touch target + endpoint (SDD §5.2)', () => {
  afterEach(() => {
    jest.clearAllMocks();
    global.fetch = originalFetch;
  });

  it('test_plus_touch_target_is_44pt', async () => {
    await render(<EdgePlusButtons {...PROPS} />);
    for (const id of ['edge-plus-left', 'edge-plus-right']) {
      const style = StyleSheet.flatten(screen.getByTestId(id).props.style);
      expect(style.width).toBeGreaterThanOrEqual(44);
      expect(style.height).toBeGreaterThanOrEqual(44);
    }
  });

  it('test_drag_follow_reads_drag_shared_values_when_dragging_this_node', async () => {
    // When dragNodeIdxShared.value === nodeIdx the worklet must compute left/top using
    // dragCurrBX/BY, not the committed node position (prevents visual lag during drag).
    // Verification: Animated.View wrappers carry testID "edge-plus-{side}-wrapper";
    // useAnimatedStyle(fn) mock calls fn() immediately so props.style IS the computed style.
    const dragProps = {
      ...PROPS,
      dragNodeIdxShared: { value: 0 } as any,   // matches nodeIdx=0
      dragCurrBXShared:  { value: 200 } as any,
      dragCurrBYShared:  { value: 300 } as any,
    };
    await render(<EdgePlusButtons {...dragProps} />);

    const TOUCH = 44;
    const halfW = NODE_SIZE[0] / 2; // 100
    // boardToCanvas at IDENTITY (scale=1, tx=0, ty=0): screenX = bx, screenY = by
    const leftFlat  = StyleSheet.flatten(screen.getByTestId('edge-plus-left-wrapper').props.style);
    const rightFlat = StyleSheet.flatten(screen.getByTestId('edge-plus-right-wrapper').props.style);

    expect(leftFlat.left).toBeCloseTo((200 - halfW) - TOUCH / 2);  // 100 - 22 = 78
    expect(leftFlat.top).toBeCloseTo(300 - TOUCH / 2);             // 300 - 22 = 278
    expect(rightFlat.left).toBeCloseTo((200 + halfW) - TOUCH / 2); // 300 - 22 = 278
    expect(rightFlat.top).toBeCloseTo(300 - TOUCH / 2);            // 300 - 22 = 278
  });

  it('test_non_dragging_node_uses_committed_position', async () => {
    // When dragNodeIdxShared.value !== nodeIdx the buttons must use the committed bx/by.
    const dragProps = {
      ...PROPS,
      dragNodeIdxShared: { value: 99 } as any,  // different node dragging — not this one
      dragCurrBXShared:  { value: 999 } as any,
      dragCurrBYShared:  { value: 999 } as any,
    };
    await render(<EdgePlusButtons {...dragProps} />);

    const TOUCH = 44;
    const halfW = NODE_SIZE[0] / 2;  // 100
    // committed position: node.position.x=50, node.position.y=60
    const leftFlat = StyleSheet.flatten(screen.getByTestId('edge-plus-left-wrapper').props.style);
    expect(leftFlat.left).toBeCloseTo((50 - halfW) - TOUCH / 2);  // -50 - 22 = -72
    expect(leftFlat.top).toBeCloseTo(60 - TOUCH / 2);             // 60 - 22 = 38
  });

  it('test_plus_press_posts_edge_offer_set', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ offer_set_id: 'os-1', options: [] }),
    });

    await render(<EdgePlusButtons {...PROPS} />);
    fireEvent.press(screen.getByTestId('edge-plus-left'));

    await waitFor(() => expect(global.fetch).toHaveBeenCalled());
    const [url, opts] = (global.fetch as jest.Mock).mock.calls[0];
    expect(url).toContain('/v1/student/offer-sets/edge');
    expect(opts.method).toBe('POST');

    const body = JSON.parse(opts.body as string);
    expect(body.session_id).toBe('session-1');
    expect(body.source_node_id).toBe('n1');
    expect(body.thread_context_id).toBe('thread-1');

    for (const forbidden of [
      'propensity', 'score', 'dimension', 'classification', 'confidence',
      'entropy', 'vector', 'profile', 'weight', 'tenant_id',
    ]) {
      expect(body).not.toHaveProperty(forbidden);
    }
    Object.keys(body).forEach((key) => expect(key).not.toMatch(/^teacher_/));
  });
});
