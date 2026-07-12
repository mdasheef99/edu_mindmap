/**
 * Manual reference link event payload builder (§3, §9).
 *
 * A manual reference link is created by a draw gesture between two nodes. edge_created v1 lists
 * `client` among its allowed producers (backend/app/events/registry.py), consistent with the other
 * client-produced canvas events (node_visited, viewport_changed). This builder emits the
 * edge_created payload the mobile client sends; the key set matches the registry's
 * required_payload_fields exactly, edge_kind is pinned to manual_reference, and created_by records
 * the manual-link trigger so a learner-created link is never read as path progression
 * (student-api-spec.md §7; session-path-data-contract.md §7).
 *
 * Note: the `manual_link` created_by token is the draw-gesture trigger analogue of the ai_path
 * edge's `offer_set_choice` token; it is owned by the forthcoming POST /edges backend handler.
 *
 * Traceability: phase-3-m3-canvas-sdd.md §3, §9; student-api-spec.md §7;
 * backend/app/events/registry.py edge_created v1.
 */

/** created_by trigger token for a manual draw-gesture reference link. */
export const MANUAL_REFERENCE_CREATED_BY = 'manual_link';

export interface ManualReferenceEdgeInput {
  edgeId: string;
  sessionId: string;
  sourceNodeId: string;
  targetNodeId: string;
}

export interface EdgeCreatedPayload {
  edge_id: string;
  session_id: string;
  source_node_id: string;
  target_node_id: string;
  edge_kind: string;
  created_by: string;
}

/** Build the edge_created payload for a learner-drawn manual reference link. */
export function buildManualReferenceEdgePayload(
  input: ManualReferenceEdgeInput,
): EdgeCreatedPayload {
  return {
    edge_id: input.edgeId,
    session_id: input.sessionId,
    source_node_id: input.sourceNodeId,
    target_node_id: input.targetNodeId,
    edge_kind: 'manual_reference',
    created_by: MANUAL_REFERENCE_CREATED_BY,
  };
}
