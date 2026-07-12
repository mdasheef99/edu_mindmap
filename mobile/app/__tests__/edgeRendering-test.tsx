/**
 * Skia edge geometry + edge_kind styling (M3 SDD §9, §14).
 *
 * §9: edge geometry is a cubic Bézier between boardToCanvas-mapped endpoints; edge styling
 * is keyed by edge_kind — ai_path (solid) vs manual_reference (dashed/distinct). The Skia
 * renderer consumes the path command string + style descriptor produced here; the math/branch
 * is kept pure so it is deterministic and CI-testable without a device.
 *
 * Traceability: phase-3-m3-canvas-sdd.md §9, §4, §14.
 */

import {
  cubicBezierPath,
  edgeStyleForKind,
} from '../../canvas/edgeRendering';

describe('edge geometry — cubic Bézier (M3 SDD §9)', () => {
  it('test_bezier_path_is_deterministic_vertical_s_curve', () => {
    // Control points sit on the vertical midline → smooth parent→child S-curve.
    expect(cubicBezierPath({ x: 0, y: 0 }, { x: 100, y: 200 })).toBe(
      'M 0 0 C 0 100 100 100 100 200',
    );
  });

  it('test_bezier_path_starts_at_source_ends_at_target', () => {
    const path = cubicBezierPath({ x: 12, y: 34 }, { x: 56, y: 78 });
    expect(path.startsWith('M 12 34 ')).toBe(true);
    expect(path.endsWith(' 56 78')).toBe(true);
  });
});

describe('edge styling — keyed by edge_kind (M3 SDD §9)', () => {
  it('test_ai_path_is_solid', () => {
    expect(edgeStyleForKind('ai_path').dashed).toBe(false);
  });

  it('test_manual_reference_is_dashed', () => {
    const style = edgeStyleForKind('manual_reference');
    expect(style.dashed).toBe(true);
    expect(style.dashIntervals.length).toBeGreaterThan(0);
  });
});
