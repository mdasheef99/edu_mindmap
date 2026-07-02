/**
 * TB1 — AI-path edge labels (M3-B SDD §5.1, §8).
 *
 * §5.1: a pure `edgeLabelLayout` produces the on-curve anchor + display text for the
 * question label drawn on an ai_path edge. Because the cubic Bézier control points sit on
 * the vertical midline (edgeRendering.cubicBezierPath), the curve point at t=0.5 equals the
 * straight midpoint of the endpoints — so the label anchors at the geometric midpoint.
 * Display text is single-line, truncated to opts.maxChars (default 28) with a trailing
 * ellipsis. The math is kept pure so it is deterministic and CI-testable without a device.
 *
 * RED: `edgeLabelLayout` does not exist in mobile/canvas/edgeRendering.ts yet.
 *
 * Traceability: phase-3-m3b-canvas-feature-parity-sdd.md §5.1, §8 TB1; MVP §4.4 L281;
 * adr-log-02.md ADR-0013.
 */

import { edgeLabelLayout } from '../../canvas/edgeRendering';

describe('TB1 — edgeLabelLayout Bézier-midpoint anchoring (SDD §5.1)', () => {
  it('test_label_anchored_at_bezier_midpoint', () => {
    // Control points on the midline → curve point at t=0.5 is the straight midpoint.
    const { position } = edgeLabelLayout({ x: 0, y: 0 }, { x: 100, y: 200 }, 'Why?');
    expect(position).toEqual({ x: 50, y: 100 });
  });

  it('test_label_midpoint_is_symmetric_for_arbitrary_endpoints', () => {
    const { position } = edgeLabelLayout({ x: 10, y: 20 }, { x: 30, y: 60 }, 'Q');
    expect(position).toEqual({ x: 20, y: 40 });
  });

  it('test_label_anchor_is_deterministic', () => {
    const a = edgeLabelLayout({ x: 12, y: 34 }, { x: 56, y: 78 }, 'same');
    const b = edgeLabelLayout({ x: 12, y: 34 }, { x: 56, y: 78 }, 'same');
    expect(a.position).toEqual(b.position);
  });
});

describe('TB1 — edgeLabelLayout truncation (SDD §5.1)', () => {
  const LONG = 'What is the long-run macroeconomic consequence of fiscal expansion?';

  it('test_label_truncated_with_ellipsis', () => {
    // Over default maxChars (28): single line, ends with the ellipsis glyph, length ≤ max.
    const { displayText } = edgeLabelLayout({ x: 0, y: 0 }, { x: 0, y: 160 }, LONG);
    expect(displayText.length).toBeLessThanOrEqual(28);
    expect(displayText.endsWith('…')).toBe(true);
    expect(displayText.includes('\n')).toBe(false);
  });

  it('test_short_label_is_unchanged', () => {
    const { displayText } = edgeLabelLayout({ x: 0, y: 0 }, { x: 0, y: 160 }, 'Define GDP');
    expect(displayText).toBe('Define GDP');
  });

  it('test_label_respects_custom_max_chars', () => {
    const { displayText } = edgeLabelLayout(
      { x: 0, y: 0 },
      { x: 0, y: 160 },
      LONG,
      { maxChars: 10 },
    );
    expect(displayText.length).toBeLessThanOrEqual(10);
    expect(displayText.endsWith('…')).toBe(true);
  });
});
