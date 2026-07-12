import React from 'react';

jest.mock('@shopify/react-native-skia', () => ({
  Canvas: ({ children }: any) => <>{children}</>, Group: ({ children }: any) => <>{children}</>,
  Path: () => null, DashPathEffect: () => null, Text: () => null, matchFont: () => ({}), Skia: {},
}));
jest.mock('react-native-reanimated', () => {
  const { View } = require('react-native');
  return { __esModule: true, default: { View, createAnimatedComponent: (c: any) => c },
    useSharedValue: (value: any) => ({ value }), useDerivedValue: (fn: any) => ({ value: fn() }),
    useAnimatedStyle: (fn: any) => fn(), useAnimatedReaction: jest.fn(), runOnJS: (fn: any) => fn };
});
jest.mock('react-native-gesture-handler', () => {
  const { View } = require('react-native');
  const gesture = () => ({ onStart: jest.fn().mockReturnThis(), onUpdate: jest.fn().mockReturnThis(),
    onEnd: jest.fn().mockReturnThis(), onFinalize: jest.fn().mockReturnThis() });
  return { GestureHandlerRootView: View, GestureDetector: ({ children }: any) => <>{children}</>,
    Gesture: { Pan: gesture, Pinch: gesture, Tap: gesture,
      Simultaneous: (...items: any[]) => items, Race: (...items: any[]) => items } };
});
jest.mock('../../canvas/NodeChip', () => {
  const { Text } = require('react-native');
  return { NodeChip: ({ node }: any) =>
    <Text testID={`position-${node.node_id}`}>{`${node.position.x},${node.position.y}`}</Text> };
});

import { act, render, screen, userEvent, waitFor } from '@testing-library/react-native';
import * as Gestures from '../../canvas/useCanvasGestures';
import type { UseCanvasGesturesResult } from '../../canvas/useCanvasGestures';
import { SkiaCanvas } from '../../canvas/SkiaCanvas';
import { useMindMapStore } from '../../canvas/store';

function deferred<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((res) => { resolve = res; });
  return { promise, resolve };
}

const originalFetch = globalThis.fetch;
const props = {
  nodes: [{ node_id: 'node-1', parent_node_id: null, position: { x: 0, y: 0 } }], edges: [],
  screen: { width: 375, height: 812 }, transform: { scale: 1, translateX: 0, translateY: 0 },
  apiBaseUrl: 'http://localhost:8000', authorizationToken: 'token-1', sessionId: 'session-1',
};

describe('SkiaCanvas position lifecycle integration', () => {
  let dragEnd: ((nodeId: string, x: number, y: number) => void) | undefined;
  beforeEach(() => {
    useMindMapStore.getState().resetPositionSession();
    jest.spyOn(Gestures, 'useCanvasGestures').mockImplementation((options: any) => {
      dragEnd = options.onNodeDragEnd;
      return { scaleShared: { value: 1 }, translateXShared: { value: 0 }, translateYShared: { value: 0 },
        dragNodeIdx: { value: -1 }, dragCurrBX: { value: 0 }, dragCurrBY: { value: 0 },
        groupTransform: { value: [] }, composed: {} } as unknown as UseCanvasGesturesResult;
    });
  });
  afterEach(() => { globalThis.fetch = originalFetch; jest.restoreAllMocks(); });

  it('commits exactly one checked write for one completed drag', async () => {
    globalThis.fetch = jest.fn().mockResolvedValue({ ok: true,
      json: async () => ({ node_id: 'node-1', position_x: 15, position_y: 25 }) });
    await render(<SkiaCanvas {...props} />);
    await act(async () => dragEnd?.('node-1', 15, 25));
    await waitFor(() => expect(globalThis.fetch).toHaveBeenCalledTimes(1));
    expect(screen.getByTestId('position-node-1').props.children).toBe('15,25');
  });

  it('keeps the newest drag visible while writes dispatch FIFO', async () => {
    const first = deferred<any>();
    globalThis.fetch = jest.fn().mockReturnValueOnce(first.promise).mockResolvedValueOnce({ ok: true,
      json: async () => ({ node_id: 'node-1', position_x: 20, position_y: 20 }) });
    await render(<SkiaCanvas {...props} />);
    await act(async () => { dragEnd?.('node-1', 10, 10); dragEnd?.('node-1', 20, 20); });
    expect(globalThis.fetch).toHaveBeenCalledTimes(1);
    expect(screen.getByTestId('position-node-1').props.children).toBe('20,20');
    await act(async () => { first.resolve({ ok: true,
      json: async () => ({ node_id: 'node-1', position_x: 10, position_y: 10 }) }); await Promise.resolve(); });
    await waitFor(() => expect(globalThis.fetch).toHaveBeenCalledTimes(2));
  });

  it('shows neutral retry state after a failed write', async () => {
    globalThis.fetch = jest.fn().mockResolvedValueOnce({ ok: false, status: 503 })
      .mockImplementation(() => new Promise(() => undefined));
    await render(<SkiaCanvas {...props} />);
    await act(async () => dragEnd?.('node-1', 10, 10));
    await waitFor(() => expect(screen.getByTestId('position-write-retry')).toBeTruthy());
    expect(screen.getByText(/node position.*not saved/i)).toBeTruthy();
    await userEvent.setup().press(screen.getByTestId('position-write-retry'));
    expect(globalThis.fetch).toHaveBeenCalledTimes(2);
  });
});
