/**
 * Manual reference link payload builder (M3 SDD §3, §9, §14).
 *
 * §3 in-scope: draw-gesture UI → edge_created with edge_kind: manual_reference. edge_created v1
 * allows a `client` producer (backend/app/events/registry.py), consistent with the other
 * client-produced canvas events. This builder emits the edge_created *payload* the mobile client
 * sends; its key set must match the registry's required_payload_fields contract exactly, with
 * edge_kind pinned to manual_reference so a learner link is never path progression
 * (student-api-spec.md §7).
 *
 * Traceability: phase-3-m3-canvas-sdd.md §3, §9, §14; student-api-spec.md §7;
 * backend/app/events/registry.py edge_created v1.
 */

import {
  MANUAL_REFERENCE_CREATED_BY,
  buildManualReferenceEdgePayload,
} from '../../canvas/edgeEvents';

// Registry contract: edge_created v1 required_payload_fields.
const REQUIRED_PAYLOAD_FIELDS = [
  'created_by',
  'edge_id',
  'edge_kind',
  'session_id',
  'source_node_id',
  'target_node_id',
].sort();

describe('manual reference edge payload (M3 SDD §3, §9)', () => {
  const input = {
    edgeId: 'edge-1',
    sessionId: 'session-1',
    sourceNodeId: 'node-a',
    targetNodeId: 'node-b',
  };

  it('test_payload_keys_match_registry_contract', () => {
    const payload = buildManualReferenceEdgePayload(input);
    expect(Object.keys(payload).sort()).toEqual(REQUIRED_PAYLOAD_FIELDS);
  });

  it('test_edge_kind_pinned_to_manual_reference', () => {
    expect(buildManualReferenceEdgePayload(input).edge_kind).toBe('manual_reference');
  });

  it('test_created_by_records_manual_link_trigger', () => {
    const payload = buildManualReferenceEdgePayload(input);
    expect(payload.created_by).toBe(MANUAL_REFERENCE_CREATED_BY);
    expect(payload.created_by.length).toBeGreaterThan(0);
  });

  it('test_payload_carries_through_inputs', () => {
    const payload = buildManualReferenceEdgePayload(input);
    expect(payload.edge_id).toBe('edge-1');
    expect(payload.session_id).toBe('session-1');
    expect(payload.source_node_id).toBe('node-a');
    expect(payload.target_node_id).toBe('node-b');
  });
});
