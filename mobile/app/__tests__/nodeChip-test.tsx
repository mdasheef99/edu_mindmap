/**
 * M3.5 frontend readiness — NodeChip learner-safe display text.
 *
 * Pending gap: NodeChip still renders raw node_id + mock body text even when the
 * student-safe session snapshot carries learner-facing title/content fields.
 *
 * Traceability:
 * - phase-3-m3-5-frontend-readiness-sdd.md §5.2, §7.1
 * - mvp-features-specification.md Feature Group 3/4
 * - 00-canon.md Category Invisibility
 */

jest.mock('react-native-reanimated', () => {
  const { View } = require('react-native');
  return {
    __esModule: true,
    default: { View, createAnimatedComponent: (c: any) => c },
    useAnimatedStyle: jest.fn((fn: () => any) => fn()),
  };
});

import React from 'react';
import { render, screen } from '@testing-library/react-native';
import { NodeChip } from '../../canvas/NodeChip';

const SHARED = { value: 1 };
const ZERO = { value: 0 };
const NO_DRAG = { value: -1 };

function renderChip(node: any) {
  return render(
    <NodeChip
      node={node}
      nodeIdx={0}
      scaleShared={SHARED as any}
      translateXShared={ZERO as any}
      translateYShared={ZERO as any}
      dragNodeIdxShared={NO_DRAG as any}
      dragCurrBXShared={ZERO as any}
      dragCurrBYShared={ZERO as any}
    />,
  );
}

describe('M3.5 NodeChip learner-safe display', () => {
  it('renders title and content when student-safe display fields are present', async () => {
    await renderChip({
      node_id: '11111111-1111-4111-8111-111111111111',
      parent_node_id: null,
      position: { x: 0, y: 0 },
      title: 'Why do leaves look green?',
      content: 'Chlorophyll absorbs red and blue light more strongly than green light.',
    });

    expect(screen.getByText('Why do leaves look green?')).toBeTruthy();
    expect(screen.getByText(/Chlorophyll absorbs red and blue light/)).toBeTruthy();
    expect(screen.queryByText('11111111-1111-4111-8111-111111111111')).toBeNull();
    expect(screen.queryByText(/Photosynthesis is the process by which green plants/)).toBeNull();
  });

  it('falls back to a compact id only when no learner-facing text exists', async () => {
    await renderChip({
      node_id: '11111111-1111-4111-8111-111111111111',
      parent_node_id: null,
      position: { x: 0, y: 0 },
    });

    expect(screen.getByText('11111111')).toBeTruthy();
  });
});
