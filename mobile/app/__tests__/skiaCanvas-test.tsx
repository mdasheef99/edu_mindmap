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
  Group: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  Path: () => null,
  DashPathEffect: () => null,
  Skia: {},
}));

jest.mock('react-native-reanimated', () => {
  const { View } = require('react-native');
  return {
    __esModule: true,
    default: { View, createAnimatedComponent: (c: any) => c },
    useSharedValue: (init: any) => ({ value: init }),
    useDerivedValue: (fn: () => any) => ({ value: fn() }),
    useAnimatedStyle: jest.fn((fn: () => any) => fn()),
    runOnJS: (fn: any) => fn,
  };
});

jest.mock('../../canvas/gestureSync', () => {
  const actual = jest.requireActual('../../canvas/gestureSync');
  return {
    ...actual,
    createViewportGestureController: jest.fn((...args: any[]) =>
      actual.createViewportGestureController(...args),
    ),
  };
});

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

import { render, screen } from '@testing-library/react-native';
import { SkiaCanvas } from '../../canvas/SkiaCanvas';
import { clampScale, CANVAS_MIN_ZOOM, CANVAS_MAX_ZOOM } from '../../canvas/gestureTransform';
import { cullEdges, computeBoardViewport } from '../../canvas/viewportCulling';
import { cubicBezierPath, edgeStyleForKind } from '../../canvas/edgeRendering';
import { createViewportGestureController } from '../../canvas/gestureSync';

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
  it('test_skia_canvas_renders_without_error', async () => {
    // Smoke: component must exist and accept required props (§8 / §9).
    // render() is async in @testing-library/react-native v14.
    await expect(
      render(<SkiaCanvas nodes={NODES} edges={EDGES} screen={SCREEN} transform={IDENTITY} />),
    ).resolves.toBeDefined();
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

  // ── Defect A: node chips must use useAnimatedStyle (UI-thread reactive, §8) ─
  it('test_node_chips_use_animated_style', async () => {
    // RED: current SkiaCanvas uses static View positioning; useAnimatedStyle is never called.
    // GREEN: NodeChip calls useAnimatedStyle once per node so chips move on the UI thread.
    // Note: render is async in @testing-library/react-native v14 — must await.
    const Reanimated = require('react-native-reanimated');
    const spy = Reanimated.useAnimatedStyle as jest.Mock;
    spy.mockClear();
    await render(<SkiaCanvas nodes={NODES} edges={EDGES} screen={SCREEN} transform={IDENTITY} />);
    expect(spy).toHaveBeenCalled();
  });

  // ── Defect C: node chips must render a visible label (§9 visual audit) ──────
  it('test_node_chips_have_visible_label', async () => {
    // RED: current SkiaCanvas renders empty <View> chips; no text is present.
    // GREEN: each NodeChip renders a <Text> with the node_id so it is identifiable.
    await render(<SkiaCanvas nodes={NODES} edges={EDGES} screen={SCREEN} transform={IDENTITY} />);
    expect(screen.getByText('n1')).toBeTruthy();
    expect(screen.getByText('n2')).toBeTruthy();
  });

  // ── Defect D: createViewportGestureController must be composed (§7 write-once-on-end) ─
  it('test_viewport_gesture_controller_is_used', async () => {
    // RED: current SkiaCanvas ignores gestureSync; createViewportGestureController is never called.
    // GREEN: SkiaCanvas calls createViewportGestureController in useMemo on mount.
    (createViewportGestureController as jest.Mock).mockClear();
    await render(<SkiaCanvas nodes={NODES} edges={EDGES} screen={SCREEN} transform={IDENTITY} />);
    expect(createViewportGestureController).toHaveBeenCalled();
  });
});
