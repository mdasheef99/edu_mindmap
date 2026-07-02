/**
 * useSessionHydration — R3 smoke test (M3-C SDD §5, §8).
 *
 * Replaces the App.tsx DEV_NODES/DEV_EDGES/DEV_TRANSFORM fixtures (G3 mobile side):
 * the hook must call GET /v1/student/sessions/{id} and map the student-safe canvas
 * snapshot into the SkiaCanvas CanvasNode[]/CanvasEdge[] shape. The fetch URL must
 * resolve to the registered router path (§8 mobile fetch parity).
 *
 * Red: mobile/canvas/useSessionHydration.ts does not exist yet.
 *
 * Traceability: phase-3-m3c-infrastructure-remediation-sdd.md §5, §8; student-api-spec.md §5.
 */

import React from 'react';
import { Text } from 'react-native';
import { render, screen, waitFor } from '@testing-library/react-native';
import { useSessionHydration } from '../../canvas/useSessionHydration';

const SESSION_RESPONSE = {
  session_id: 'session-1',
  status: 'active',
  last_active_node_id: null,
  canvas: {
    nodes: [
      {
        node_id: 'n1',
        node_type: 'ai',
        title: 'Root question',
        content: 'Root',
        position_x: 10,
        position_y: 20,
        thread_context_id: 't1',
      },
      { node_id: 'n2', node_type: 'ai', content: 'Child', position_x: null, position_y: null },
    ],
    edges: [
      { edge_id: 'e1', source_node_id: 'n1', target_node_id: 'n2', edge_kind: 'ai_path', label: null },
    ],
  },
};

function Harness(props: { apiBaseUrl?: string; sessionId?: string; authorizationToken?: string }) {
  const { nodes, edges, status } = useSessionHydration(props);
  return (
    <>
      <Text>{`status:${status}`}</Text>
      {nodes.map((n) => (
        <Text key={n.node_id}>{`node:${n.node_id}:${n.position.x},${n.position.y}`}</Text>
      ))}
      {nodes.map((n: any) => (
        <Text key={`${n.node_id}-display`}>{`display:${n.title ?? ''}:${n.content ?? ''}`}</Text>
      ))}
      {edges.map((e) => (
        <Text key={e.edge_id}>{`edge:${e.edge_id}:${e.edge_kind}`}</Text>
      ))}
    </>
  );
}

const originalFetch = global.fetch;

describe('useSessionHydration — R3 (M3-C SDD §5, §8)', () => {
  afterEach(() => {
    jest.clearAllMocks();
    global.fetch = originalFetch;
  });

  it('TR3-1: fetches GET /sessions/{id} and maps the canvas snapshot', async () => {
    global.fetch = jest.fn().mockResolvedValue({ ok: true, json: async () => SESSION_RESPONSE });

    await render(
      <Harness apiBaseUrl="http://localhost:8000" sessionId="session-1" authorizationToken="tok" />,
    );

    await waitFor(() => expect(screen.getByText('status:ready')).toBeTruthy());

    // URL must resolve to the registered router path (§8 fetch parity) with bearer auth.
    const [url, opts] = (global.fetch as jest.Mock).mock.calls[0];
    expect(url).toBe('http://localhost:8000/v1/student/sessions/session-1');
    expect(opts.headers.Authorization).toBe('Bearer tok');

    // Snapshot fields are mapped into SkiaCanvas node/edge shape.
    expect(screen.getByText('node:n1:10,20')).toBeTruthy();
    expect(screen.getByText('display:Root question:Root')).toBeTruthy();
    // Null positions fall back to 0 (layout is applied downstream in M4).
    expect(screen.getByText('node:n2:0,0')).toBeTruthy();
    expect(screen.getByText('edge:e1:ai_path')).toBeTruthy();
  });

  it('TR3-2: no fetch when sessionId is absent (idle)', async () => {
    global.fetch = jest.fn();
    await render(<Harness apiBaseUrl="http://localhost:8000" />);
    expect(global.fetch).not.toHaveBeenCalled();
    expect(screen.getByText('status:idle')).toBeTruthy();
  });
});
