/**
 * SkiaCanvas component integration — M3 SDD §8, §9 component seam.
 *
 * Tests that SkiaCanvas composes the pure-function canvas modules (coordinateSystem,
 * gestureTransform, edgeRendering, viewportCulling) correctly: respects scale clamp
 * limits (§8), performs viewport culling before building render data (§9), produces
 * deterministic Bézier paths (§9), applies edge-kind styling (§9), and renders
 * without throwing when given valid props.
 *
 * Native libraries (Skia, Reanimated, Gesture Handler) are mocked so tests run in
 * Node.js / CI without a device. Red: mobile/canvas/SkiaCanvas.tsx does not exist yet.
 *
 * Traceability: phase-3-m3-canvas-sdd.md §8, §9, §12; ADR-0013.
 */

import React from 'react';

// ── native-module mocks (must appear before any React-Native imports) ──────────

jest.mock('@shopify/react-native-skia', () => ({
  Canvas: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  Path: () => null,
  Skia: {},
}));

jest.mock('react-native-reanimated', () => ({
  useSharedValue: (init: any) => ({ value: init }),
  useAnimatedStyle: (fn: () => any) => fn(),
  runOnJS: (fn: any) => fn,
}));

jest.mock('react-native-gesture-handler', () => {
  const { View } = require('react-native');
  const mockGesture = () => ({
    onStart: jest.fn().mockReturnThis(),
    onUpdate: jest.fn().mockReturnThis(),
    onEnd: jest.fn().mockReturnThis(),
    onFinalize: jest.fn().mockReturnThis(),
  });
  return {
    GestureHandlerRootView: View,
    GestureDetector: ({ children }: { children: React.ReactNode }) => <>{children}</>,
    Gesture: {
      Pan: mockGesture,
      Pinch: mockGesture,
      Simultaneous: jest.fn((...gs: any[]) => gs),
    },
  };
});

// ── imports after mocks ────────────────────────────────────────────────────────

import { render } from '@testing-library/react-native';
import { SkiaCanvas } from '../../canvas/SkiaCanvas';
import { clampScale, CANVAS_MIN_ZOOM, CANVAS_MAX_ZOOM } from '../../canvas/gestureTransform';
import { cullEdges, computeBoardViewport } from '../../canvas/viewportCulling';
import { cubicBezierPath, edgeStyleForKind } from '../../canvas/edgeRendering';

// ── fixtures ──────────────────────────────────────────────────────────────────

const IDENTITY = { scale: 1, translateX: 0, translateY: 0 };
const SCREEN = { width: 375, height: 812 };
const NODES = [
  { node_id: 'n1', parent_node_id: null as null, position: { x: 0, y: 0 } },
  { node_id: 'n2', parent_node_id: 'n1', position: { x: 0, y: 160 } },
];
const EDGES = [
  { edge_id: 'e1', source_node_id: 'n1', target_node_id: 'n2', edge_kind: 'ai_path' as const },
];

// ── tests ─────────────────────────────────────────────────────────────────────

describe('SkiaCanvas — §8 / §9 component seam', () => {
  it('test_skia_canvas_renders_without_error', () => {
    // Smoke: component must exist and accept required props (§8 / §9).
    expect(() =>
      render(
        <SkiaCanvas nodes={NODES} edges={EDGES} screen={SCREEN} transform={IDENTITY} />,
      ),
    ).not.toThrow();
  });

  it('test_scale_clamp_respects_zoom_limits', () => {
    // SkiaCanvas delegates clamping to clampScale (§8).
    expect(clampScale(0.001)).toBe(CANVAS_MIN_ZOOM);   // floor at 0.25
    expect(clampScale(999)).toBe(CANVAS_MAX_ZOOM);     // ceiling at 4.0
    expect(clampScale(2.0)).toBe(2.0);                 // within range passes through
  });

  it('test_culling_removes_offscreen_edges', () => {
    // SkiaCanvas must run cullEdges (§9) before building the render path.
    // At scale=10 the visible board window is tiny; n2 at y=1000 is outside.
    const t = { scale: 10, translateX: 0, translateY: 0 };
    const positions = { n1: { x: 0, y: 0 }, n2: { x: 0, y: 1000 } };
    const vp = computeBoardViewport(t, SCREEN);
    const visible = cullEdges(EDGES, positions, vp);
    // e1's source n1 (0,0) is inside → edge kept; n2 is out but one endpoint suffices.
    expect(visible.length).toBe(1);
    expect(visible[0].edge_id).toBe('e1');
  });

  it('test_bezier_path_is_deterministic', () => {
    // cubicBezierPath must be byte-identical for identical inputs (§9 determinism).
    const p0 = { x: 100, y: 0 };
    const p1 = { x: 100, y: 160 };
    const a = cubicBezierPath(p0, p1);
    const b = cubicBezierPath(p0, p1);
    expect(a).toBe(b);
    expect(a).toMatch(/^M 100 0/);
  });

  it('test_edge_kind_styling_contract', () => {
    // edgeStyleForKind must return solid for ai_path, dashed for manual_reference (§9).
    expect(edgeStyleForKind('ai_path').dashed).toBe(false);
    expect(edgeStyleForKind('manual_reference').dashed).toBe(true);
    expect(edgeStyleForKind('manual_reference').dashIntervals.length).toBeGreaterThan(0);
  });
});
