/**
 * SkiaCanvas integration — component seam after M3.5 hook extraction.
 *
 * This file focuses on end-to-end composition: the component renders without throwing,
 * respects scale limits, culls native node views, wires edge-`+`/toolbar/delete flows,
 * and emits the expected `node_visited`/`viewport_changed` events. Hook-level internals
 * (deletion reconciliation, discovery state, live drag override, render-data memoization)
 * are covered by the dedicated hook unit tests in `mobile/canvas/__tests__/`.
 *
 * Native libraries (Skia, Reanimated, Gesture Handler) are mocked so tests run in
 * Node.js / CI without a device.
 *
 * Traceability: phase-3-m3-canvas-sdd.md §8, §9, §12; phase-3-m3c-infrastructure-
 * remediation-sdd.md §9.4, §9.6; ADR-0013.
 */

import React from 'react';

// ── native-module mocks (must appear before any React-Native imports) ──────────

jest.mock('@shopify/react-native-skia', () => ({
  Canvas: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  Group: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  Path: () => null,
  DashPathEffect: () => null,
  Text: () => null,
  matchFont: () => ({}),
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
    // No-op: the reaction bridges UI-thread shared values to JS state and is exercised
    // on device only; Jest tests assert state directly without simulating gesture frames.
    useAnimatedReaction: jest.fn(),
    runOnJS: (fn: any) => fn,
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
      Tap: mockGesture,
      Simultaneous: jest.fn((...gs: any[]) => gs),
      Race: jest.fn((...gs: any[]) => gs),
    },
  };
});

// ── imports after mocks ────────────────────────────────────────────────────────

import { cleanup, render, screen, fireEvent, waitFor, act } from '@testing-library/react-native';
import * as UseCanvasGesturesMod from '../../canvas/useCanvasGestures';
import type { UseCanvasGesturesResult } from '../../canvas/useCanvasGestures';
import { SkiaCanvas } from '../../canvas/SkiaCanvas';
import { clampScale, CANVAS_MIN_ZOOM, CANVAS_MAX_ZOOM } from '../../canvas/gestureTransform';
import { cullEdges, computeBoardViewport } from '../../canvas/viewportCulling';
import { cubicBezierPath, edgeStyleForKind } from '../../canvas/edgeRendering';
import { useMindMapStore } from '../../canvas/store';

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

  // ── Defect C: node chips must render a visible label (§9 visual audit) ──────
  it('test_node_chips_have_visible_label', async () => {
    // RED: current SkiaCanvas renders empty <View> chips; no text is present.
    // GREEN: each NodeChip renders a <Text> with the node_id so it is identifiable.
    await render(<SkiaCanvas nodes={NODES} edges={EDGES} screen={SCREEN} transform={IDENTITY} />);
    expect(screen.getByText('n1')).toBeTruthy();
    expect(screen.getByText('n2')).toBeTruthy();
  });
});

// ── TB6 — Native View culling (M3-B SDD §5.4, §8) ──────────────────────────────
// Off-screen NodeChips must NOT mount (the ADR-0013 perf lever), and the edge-`+`
// buttons (F2) + toolbar (F3) for an off-screen node are culled with it.
describe('TB6 — native view culling (M3-B SDD §5.4)', () => {
  // scale=10 makes the board window tiny (≈37×81 board units): n1 is in, n_off is out.
  const TIGHT = { scale: 10, translateX: 0, translateY: 0 };
  const CULL_NODES = [
    { node_id: 'n1', parent_node_id: null as null, position: { x: 0, y: 0 } },
    { node_id: 'n_off', parent_node_id: 'n1', position: { x: 0, y: 1000 } },
  ];
  const DISCOVERY = {
    apiBaseUrl: 'http://localhost:8000',
    authorizationToken: 'test-token',
    sessionId: 'session-1',
  };

  beforeEach(() => useMindMapStore.setState({ selectedNodeId: null }));

  it('test_culling_removes_offscreen_node_chips', async () => {
    await render(<SkiaCanvas nodes={CULL_NODES} edges={EDGES} screen={SCREEN} transform={TIGHT} />);
    expect(screen.getByText('n1')).toBeTruthy();
    expect(screen.queryByText('n_off')).toBeNull();
  });

  it('test_offscreen_plus_and_toolbar_culled_with_node', async () => {
    // Select the off-screen node so a toolbar WOULD render if culling were absent.
    useMindMapStore.getState().selectNode('n_off');
    await render(
      <SkiaCanvas nodes={CULL_NODES} edges={EDGES} screen={SCREEN} transform={TIGHT} {...DISCOVERY} />,
    );
    // Edge-`+` buttons exist only for the single visible node.
    expect(screen.getAllByTestId('edge-plus-left')).toHaveLength(1);
    // The selected node is off-screen → its toolbar (Delete action) is culled.
    expect(screen.queryByText('Delete')).toBeNull();
  });

  it('M3.5: failed edge-plus offer request shows a visible canvas error', async () => {
    const originalFetch = global.fetch;
    global.fetch = jest.fn().mockResolvedValue({
      ok: false,
      status: 503,
      statusText: 'Service Unavailable',
    });

    await render(
      <SkiaCanvas nodes={NODES} edges={EDGES} screen={SCREEN} transform={IDENTITY} {...DISCOVERY} />,
    );

    const plusButtons = screen.getAllByTestId('edge-plus-left');
    expect(plusButtons.length).toBeGreaterThan(0);
    fireEvent.press(plusButtons[0]);

    await waitFor(() => {
      expect(screen.getByText('Question options could not load. Try again.')).toBeTruthy();
    });

    global.fetch = originalFetch;
  });
});

// ── TC-M2 — SkiaCanvas deletion reconciliation (M3-C SDD §9.4) ────────────────
// After NodeToolbar fires onDeleted with NodeDeletionResponse, SkiaCanvas must
// remove the deleted nodes and edges from its local render state (G1 fix).
describe('TC-M2 — SkiaCanvas deletion reconciliation (M3-C SDD §9.4)', () => {
  const DISCOVERY_PROPS = {
    apiBaseUrl: 'http://localhost:8000',
    authorizationToken: 'test-token',
    sessionId: 'session-1',
  };
  const originalFetch = global.fetch;

  beforeEach(() => useMindMapStore.setState({ selectedNodeId: 'n1' }));
  afterEach(() => {
    global.fetch = originalFetch;
    useMindMapStore.setState({ selectedNodeId: null });
    jest.clearAllMocks();
  });

  it('TC-M2: deleted nodes and edges vanish from canvas after onDeleted fires', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        session_id: 'session-1',
        root_node_id: 'n1',
        deleted_node_ids: ['n1', 'n2'],
        deleted_edge_ids: ['e1'],
        confirmed: true,
      }),
    });

    await render(
      <SkiaCanvas nodes={NODES} edges={EDGES} screen={SCREEN} transform={IDENTITY} {...DISCOVERY_PROPS} />,
    );

    // Toolbar must be visible (n1 is selected and on-screen).
    expect(screen.getByText('Delete')).toBeTruthy();

    // Trigger deletion cascade.
    fireEvent.press(screen.getByText('Delete'));
    fireEvent.press(await screen.findByText('Confirm'));

    // Both n1 and n2 must disappear from the canvas (cascade includes n2).
    await waitFor(() => {
      expect(screen.queryByText('n1')).toBeNull();
      expect(screen.queryByText('n2')).toBeNull();
    });
  });
});

// ── TA-M1/TA-M2 — Tier-2 event emission (M3-C SDD §9.6) ─────────────────────
// SkiaCanvas must fire POST /events with node_visited on node tap (TA-M1) and
// viewport_changed on transform end (TA-M2) when sessionId is set (G4/G5 fix).
describe('TA-M1/TA-M2 — event emission (M3-C SDD §9.6)', () => {
  const DISCOVERY_PROPS = {
    apiBaseUrl: 'http://localhost:8000',
    authorizationToken: 'test-token',
    sessionId: 'session-1',
  };
  const originalFetch = global.fetch;

  // Capture the callbacks SkiaCanvas passes to useCanvasGestures so we can
  // invoke them directly (the gesture system is mocked in tests).
  let capturedOnSelectNode: ((nodeId: string) => void) | undefined;
  let capturedOnTransformEnd: ((t: any) => void) | undefined;

  beforeEach(() => {
    capturedOnSelectNode = undefined;
    capturedOnTransformEnd = undefined;
    jest.spyOn(UseCanvasGesturesMod, 'useCanvasGestures').mockImplementation((opts: any) => {
      capturedOnSelectNode = opts.onSelectNode;
      capturedOnTransformEnd = opts.onTransformEnd;
      return {
        scaleShared: { value: 1 },
        translateXShared: { value: 0 },
        translateYShared: { value: 0 },
        dragNodeIdx: { value: -1 },
        dragCurrBX: { value: 0 },
        dragCurrBY: { value: 0 },
        groupTransform: { value: [] },
        composed: {},
      } as unknown as UseCanvasGesturesResult;
    });
    useMindMapStore.setState({ selectedNodeId: null });
  });

  afterEach(() => {
    jest.restoreAllMocks();
    global.fetch = originalFetch;
    useMindMapStore.setState({ selectedNodeId: null });
  });

  it('TA-M1: node tap fires node_visited event to POST /events', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ accepted: 1, rejected: [] }),
    });

    await render(
      <SkiaCanvas nodes={NODES} edges={EDGES} screen={SCREEN} transform={IDENTITY} {...DISCOVERY_PROPS} />,
    );

    // Simulate a tap on node n1 via the captured callback.
    await act(async () => { capturedOnSelectNode?.('n1'); });

    await waitFor(() => expect(global.fetch).toHaveBeenCalled());
    const [url, opts] = (global.fetch as jest.Mock).mock.calls[0];
    expect(url).toContain('/events');
    const body = JSON.parse(opts.body as string);
    expect(body.events[0].event_type).toBe('node_visited');
    expect(body.events[0].payload.visit_source).toBe('tap');
    expect(body.events[0].payload.node_id).toBe('n1');
  });

  it('TA-M2: transform end fires viewport_changed event to POST /events', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ accepted: 1, rejected: [] }),
    });
    const newTransform = { scale: 2, translateX: 10, translateY: 20 };

    await render(
      <SkiaCanvas nodes={NODES} edges={EDGES} screen={SCREEN} transform={IDENTITY} {...DISCOVERY_PROPS} />,
    );

    // Simulate a transform-end via the captured callback.
    await act(async () => { capturedOnTransformEnd?.(newTransform); });

    await waitFor(() => expect(global.fetch).toHaveBeenCalled());
    const [url, opts] = (global.fetch as jest.Mock).mock.calls[0];
    expect(url).toContain('/events');
    const body = JSON.parse(opts.body as string);
    expect(body.events[0].event_type).toBe('viewport_changed');
    expect(body.events[0].payload.scale).toBe(2);
    expect(body.events[0].payload.translate_x).toBe(10);
    expect(body.events[0].payload.translate_y).toBe(20);
  });
});

// ── M3.6 — Canvas controls (pre-M4) ───────────────────────────────────────────
describe('M3.6 — canvas toolbar controls', () => {
  const DISCOVERY_PROPS = {
    apiBaseUrl: 'http://localhost:8000',
    authorizationToken: 'test-token',
    sessionId: 'session-1',
  };
  const originalFetch = global.fetch;

  beforeEach(() => {
    global.fetch = jest.fn().mockResolvedValue({ ok: true, json: async () => ({}) });
  });

  afterEach(() => {
    cleanup();
    jest.restoreAllMocks();
    global.fetch = originalFetch;
    useMindMapStore.setState({ selectedNodeId: null });
  });

  it('toolbar zoom, fit, and reset controls commit viewport transforms through onTransformEnd', async () => {
    const onTransformEnd = jest.fn();
    await render(
      <SkiaCanvas nodes={NODES} edges={EDGES} screen={SCREEN} transform={IDENTITY} onTransformEnd={onTransformEnd} />,
    );

    expect(screen.getByText('100%')).toBeTruthy();
    expect(screen.getByTestId('canvas-snap-grid-toggle')).toBeTruthy();

    fireEvent.press(screen.getByTestId('canvas-zoom-in'));
    expect(onTransformEnd).toHaveBeenLastCalledWith(expect.objectContaining({ scale: 1.25 }));

    fireEvent.press(screen.getByTestId('canvas-fit-screen'));
    expect(onTransformEnd).toHaveBeenCalledTimes(2);
    expect(onTransformEnd.mock.calls[1][0].scale).toBeGreaterThan(0);

    fireEvent.press(screen.getByTestId('canvas-reset-view'));
    expect(onTransformEnd).toHaveBeenLastCalledWith(IDENTITY);
  });
});
