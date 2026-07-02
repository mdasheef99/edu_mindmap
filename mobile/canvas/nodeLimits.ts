/**
 * Node-limit state — client mirror of the backend node-limit guard (M3-B SDD §5.5; M3 SDD §11).
 *
 * The backend 409 guard (offer_workflow / offer_choices) is the authority; this pure helper
 * only drives the learner-facing affordances: a non-blocking warning banner once the active
 * node count reaches CANVAS_NODE_WARNING_COUNT, and disabling of creation affordances once it
 * reaches CANVAS_NODE_HARD_LIMIT. No analytic state (Category Invisibility).
 *
 * Traceability: phase-3-m3b-canvas-feature-parity-sdd.md §5.5; phase-3-m3-canvas-sdd.md §11;
 * configuration-reference.md §3 (CANVAS_NODE_WARNING_COUNT / CANVAS_NODE_HARD_LIMIT).
 */

/** Active-node count at which the non-blocking warning banner appears (config §3). */
export const CANVAS_NODE_WARNING_COUNT = 50;

/** Active-node count at which client-side creation affordances are disabled (config §3). */
export const CANVAS_NODE_HARD_LIMIT = 65;

export interface NodeLimitState {
  showWarning: boolean;
  creationBlocked: boolean;
}

/** Derive banner/creation affordance state from the active node count. */
export function nodeLimitState(activeCount: number): NodeLimitState {
  return {
    showWarning: activeCount >= CANVAS_NODE_WARNING_COUNT,
    creationBlocked: activeCount >= CANVAS_NODE_HARD_LIMIT,
  };
}
