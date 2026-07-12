import React from 'react';
import { render } from '@testing-library/react-native';
import type { SharedValue } from 'react-native-reanimated';

let mockCanvasRenderCount = 0;
let mockCapturedPaths: any[] = [];
let mockCapturedLabels: any[] = [];
let mockCapturedDashes: any[] = [];

jest.mock('@shopify/react-native-skia', () => ({
  Canvas: ({ children }: { children: React.ReactNode }) => {
    mockCanvasRenderCount += 1;
    return <>{children}</>;
  },
  Group: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  Path: (props: any) => {
    mockCapturedPaths.push(props);
    return <>{props.children}</>;
  },
  DashPathEffect: (props: any) => {
    mockCapturedDashes.push(props);
    return null;
  },
  Text: (props: any) => {
    mockCapturedLabels.push(props);
    return null;
  },
  matchFont: () => ({}),
}));

jest.mock('react-native-reanimated', () => ({
  useDerivedValue: (derive: () => unknown) => ({
    get value() {
      return derive();
    },
  }),
}));

import { CanvasEdges } from '../CanvasEdges';

function shared(value: number): SharedValue<number> {
  return { value } as SharedValue<number>;
}

function animatedValue<T>(value: T | SharedValue<T>): T {
  return typeof value === 'object' && value !== null && 'value' in value
    ? (value as SharedValue<T>).value
    : value as T;
}

const nodePositions = {
  n1: { x: 0, y: 0 },
  n2: { x: 100, y: 200 },
  n3: { x: 300, y: 400 },
};
const edges = [
  {
    edge_id: 'dragged-edge',
    source_node_id: 'n1',
    target_node_id: 'n2',
    edge_kind: 'ai_path' as const,
    label: 'Why?',
  },
  {
    edge_id: 'static-edge',
    source_node_id: 'n2',
    target_node_id: 'n3',
    edge_kind: 'manual_reference' as const,
  },
];

describe('CanvasEdges transient drag synchronization', () => {
  beforeEach(() => {
    mockCanvasRenderCount = 0;
    mockCapturedPaths = [];
    mockCapturedLabels = [];
    mockCapturedDashes = [];
  });

  async function renderEdges() {
    const dragNodeIdxShared = shared(-1);
    const dragCurrBXShared = shared(0);
    const dragCurrBYShared = shared(0);
    await render(
      <CanvasEdges
        nodePositions={nodePositions}
        nodeIndexById={{ n1: 0, n2: 1, n3: 2 }}
        edges={edges}
        visibleEdges={edges}
        visIds={new Set(['n1', 'n2', 'n3'])}
        groupTransform={{ value: [] } as any}
        dragNodeIdxShared={dragNodeIdxShared}
        dragCurrBXShared={dragCurrBXShared}
        dragCurrBYShared={dragCurrBYShared}
      />,
    );
    return { dragNodeIdxShared, dragCurrBXShared, dragCurrBYShared };
  }

  it('follows the dragged endpoint SharedValues without a React render', async () => {
    const drag = await renderEdges();
    expect(animatedValue(mockCapturedPaths[0].path)).toBe('M 0 0 C 0 100 100 100 100 200');

    drag.dragNodeIdxShared.value = 0;
    drag.dragCurrBXShared.value = 40;
    drag.dragCurrBYShared.value = 60;

    expect(animatedValue(mockCapturedPaths[0].path)).toBe('M 40 60 C 40 130 100 130 100 200');
    expect(mockCanvasRenderCount).toBe(1);
  });

  it('keeps unaffected edge geometry on its existing static path', async () => {
    const drag = await renderEdges();
    const original = animatedValue(mockCapturedPaths[1].path);

    drag.dragNodeIdxShared.value = 0;
    drag.dragCurrBXShared.value = 40;
    drag.dragCurrBYShared.value = 60;

    expect(animatedValue(mockCapturedPaths[1].path)).toBe(original);
    expect(original).toBe('M 100 200 C 100 300 300 300 300 400');
  });

  it('preserves edge styling and label rendering on the reactive path', async () => {
    const drag = await renderEdges();
    expect(mockCapturedPaths[0].strokeWidth).toBe(2);
    expect(mockCapturedPaths[1].strokeWidth).toBe(1.5);
    expect(mockCapturedDashes).toEqual([{ intervals: [8, 6] }]);
    expect(mockCapturedLabels[0].text).toBe('Why?');

    drag.dragNodeIdxShared.value = 0;
    drag.dragCurrBXShared.value = 40;
    drag.dragCurrBYShared.value = 60;

    expect(animatedValue(mockCapturedLabels[0].x)).toBe(70);
    expect(animatedValue(mockCapturedLabels[0].y)).toBe(130);
  });
});
