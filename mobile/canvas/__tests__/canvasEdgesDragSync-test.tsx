import React from 'react';
import { render } from '@testing-library/react-native';
import type { SharedValue } from 'react-native-reanimated';

let mockCapturedPaths: any[] = [];
let mockCapturedLabels: any[] = [];
let mockCanvasRenderCount = 0;

jest.mock('@shopify/react-native-skia', () => ({
  Canvas: ({ children }: any) => { mockCanvasRenderCount += 1; return <>{children}</>; },
  Group: ({ children }: any) => <>{children}</>,
  Path: (props: any) => { mockCapturedPaths.push(props); return <>{props.children}</>; },
  DashPathEffect: () => null,
  Text: (props: any) => { mockCapturedLabels.push(props); return null; },
  matchFont: () => ({}),
}));

jest.mock('react-native-reanimated', () => ({
  useDerivedValue: (derive: () => unknown) => ({ get value() { return derive(); } }),
}));

import { CanvasEdges } from '../CanvasEdges';

function shared(value: number): SharedValue<number> {
  return { value } as SharedValue<number>;
}

function animated<T>(value: T | SharedValue<T>): T {
  return typeof value === 'object' && value !== null && 'value' in value
    ? (value as SharedValue<T>).value : value as T;
}

const positions = { n1: { x: 0, y: 0 }, n2: { x: 100, y: 200 }, n3: { x: 300, y: 400 } };
const edges = [
  { edge_id: 'dragged', source_node_id: 'n1', target_node_id: 'n2', edge_kind: 'ai_path', label: 'Why?' },
  { edge_id: 'static', source_node_id: 'n2', target_node_id: 'n3', edge_kind: 'manual_reference' },
];

describe('CanvasEdges UI-thread drag geometry', () => {
  beforeEach(() => { mockCapturedPaths = []; mockCapturedLabels = []; mockCanvasRenderCount = 0; });

  async function setup() {
    const dragNodeIdxShared = shared(-1);
    const dragCurrBXShared = shared(0);
    const dragCurrBYShared = shared(0);
    await render(<CanvasEdges
      nodePositions={positions}
      nodeIndexById={{ n1: 0, n2: 1, n3: 2 }}
      edges={edges}
      visibleEdges={edges}
      visIds={new Set(['n1', 'n2', 'n3'])}
      groupTransform={{ value: [] } as any}
      dragNodeIdxShared={dragNodeIdxShared}
      dragCurrBXShared={dragCurrBXShared}
      dragCurrBYShared={dragCurrBYShared}
    />);
    return { dragNodeIdxShared, dragCurrBXShared, dragCurrBYShared };
  }

  it('moves the connected endpoint without a React render', async () => {
    const drag = await setup();
    expect(animated(mockCapturedPaths[0].path)).toBe('M 0 0 C 0 100 100 100 100 200');
    drag.dragNodeIdxShared.value = 0;
    drag.dragCurrBXShared.value = 40;
    drag.dragCurrBYShared.value = 60;
    expect(animated(mockCapturedPaths[0].path)).toBe('M 40 60 C 40 130 100 130 100 200');
    expect(mockCanvasRenderCount).toBe(1);
  });

  it('leaves unrelated edge geometry static', async () => {
    const drag = await setup();
    const original = animated(mockCapturedPaths[1].path);
    drag.dragNodeIdxShared.value = 0;
    drag.dragCurrBXShared.value = 40;
    drag.dragCurrBYShared.value = 60;
    expect(animated(mockCapturedPaths[1].path)).toBe(original);
  });

  it('moves the connected label on the same UI-thread path', async () => {
    const drag = await setup();
    drag.dragNodeIdxShared.value = 0;
    drag.dragCurrBXShared.value = 40;
    drag.dragCurrBYShared.value = 60;
    expect(animated(mockCapturedLabels[0].x)).toBe(70);
    expect(animated(mockCapturedLabels[0].y)).toBe(130);
  });
});
