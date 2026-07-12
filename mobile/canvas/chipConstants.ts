/**
 * Node chip geometry constants — shared between the SkiaCanvas orchestrator and the
 * NodeChip native overlay (ADR-0013). Board units equal screen pixels at scale=1
 * (phase-3-m3-canvas-sdd.md §4 seam).
 *
 * CHIP_W / CHIP_H drive the visual chip size, the hit-test AABB, edge-`+` anchor
 * placement, and the culling padding that keeps a chip on screen until it is fully
 * outside the viewport (M3-B SDD §5.4).
 *
 * Traceability: phase-3-m3-canvas-sdd.md §4, §9; phase-3-m3b-canvas-feature-parity-sdd.md §5.2, §5.4.
 */

/** Chip width in board units (screen pixels at scale=1). */
export const CHIP_W = 280;

/** Chip height in board units (screen pixels at scale=1). */
export const CHIP_H = 180;
