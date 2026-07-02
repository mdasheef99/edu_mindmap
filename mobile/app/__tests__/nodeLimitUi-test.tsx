/**
 * TB7 — Node-limit mobile UI (M3-B SDD §5.5, §8; M3 SDD §11).
 *
 * The canvas mirrors the backend node-limit guard client-side: a non-blocking warning
 * banner appears at CANVAS_NODE_WARNING_COUNT (50) active nodes, and creation affordances
 * are disabled at CANVAS_NODE_HARD_LIMIT (65). The backend 409 guard remains the authority
 * (M3 SDD §11) — this is purely a learner-facing affordance.
 *
 * nodeLimitState is a pure helper (CI-testable, no device). NodeLimitBanner renders the
 * warning/limit chrome from that state.
 *
 * RED: neither mobile/canvas/nodeLimits.ts nor mobile/canvas/NodeLimitBanner.tsx exists.
 *
 * Traceability: phase-3-m3b-canvas-feature-parity-sdd.md §5.5, §8 TB7; M3 SDD §11;
 * configuration-reference.md §3 (CANVAS_NODE_WARNING_COUNT / CANVAS_NODE_HARD_LIMIT).
 */

import React from 'react';
import { render, screen } from '@testing-library/react-native';
import {
  nodeLimitState,
  CANVAS_NODE_WARNING_COUNT,
  CANVAS_NODE_HARD_LIMIT,
} from '../../canvas/nodeLimits';
import { NodeLimitBanner } from '../../canvas/NodeLimitBanner';

describe('TB7 — nodeLimitState pure helper (SDD §5.5)', () => {
  it('test_constants_match_canon', () => {
    expect(CANVAS_NODE_WARNING_COUNT).toBe(50);
    expect(CANVAS_NODE_HARD_LIMIT).toBe(65);
  });

  it('test_below_warning_is_clear', () => {
    const state = nodeLimitState(49);
    expect(state.showWarning).toBe(false);
    expect(state.creationBlocked).toBe(false);
  });

  it('test_warning_at_50', () => {
    const state = nodeLimitState(50);
    expect(state.showWarning).toBe(true);
    expect(state.creationBlocked).toBe(false);
  });

  it('test_creation_blocked_at_65', () => {
    const state = nodeLimitState(65);
    expect(state.showWarning).toBe(true);
    expect(state.creationBlocked).toBe(true);
  });
});

describe('TB7 — NodeLimitBanner chrome (SDD §5.5)', () => {
  it('test_no_banner_below_warning', async () => {
    await render(<NodeLimitBanner activeCount={10} />);
    expect(screen.queryByTestId('node-limit-banner')).toBeNull();
  });

  it('test_warning_banner_at_50', async () => {
    await render(<NodeLimitBanner activeCount={50} />);
    expect(screen.getByTestId('node-limit-banner')).toBeTruthy();
    // Warning copy must surface the count; must NOT yet say the hard limit is reached.
    expect(screen.queryByTestId('node-limit-blocked')).toBeNull();
  });

  it('test_creation_disabled_at_65', async () => {
    await render(<NodeLimitBanner activeCount={65} />);
    expect(screen.getByTestId('node-limit-banner')).toBeTruthy();
    expect(screen.getByTestId('node-limit-blocked')).toBeTruthy();
  });
});
