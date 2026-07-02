/**
 * useSessionHydration — real canvas hydration from GET /sessions/{id} (M3-C SDD §5, §8).
 *
 * Replaces the App.tsx DEV_NODES/DEV_EDGES/DEV_TRANSFORM fixtures (G3 mobile side).
 * Fetches the student-safe canvas snapshot and maps it into the SkiaCanvas
 * CanvasNode[]/CanvasEdge[] shape. parent_node_id is derived from the edge set
 * (the ai_path/manual_reference source whose target is this node) since the
 * student snapshot is Category-Invisible and carries no analytic parent field.
 *
 * Null positions fall back to {0,0}; d3-hierarchy layout is applied downstream (M4).
 *
 * Traceability:
 * - docs/planning/sdd/phase-3-m3c-infrastructure-remediation-sdd.md §5, §8
 * - docs/api/student-api-spec.md §5 (canvas payload shape)
 */

import { useEffect, useState } from 'react';
import type { CanvasNode, CanvasEdge } from './SkiaCanvas';

export type HydrationStatus = 'idle' | 'loading' | 'ready' | 'error';

interface SnapshotNode {
  node_id: string;
  node_type: string;
  title?: string | null;
  content: string;
  position_x: number | null;
  position_y: number | null;
  thread_context_id?: string | null;
}

interface SnapshotEdge {
  edge_id: string;
  source_node_id: string;
  target_node_id: string;
  edge_kind: string;
  label?: string | null;
}

export interface UseSessionHydrationArgs {
  apiBaseUrl?: string;
  sessionId?: string;
  authorizationToken?: string;
}

export interface HydrationState {
  nodes: CanvasNode[];
  edges: CanvasEdge[];
  status: HydrationStatus;
  /** Re-fetches GET /sessions so newly created nodes/edges appear on the canvas. */
  reload: () => void;
}

/** Map a student-safe snapshot into SkiaCanvas node/edge shape (§5 return shape). */
function mapSnapshot(
  nodes: SnapshotNode[],
  edges: SnapshotEdge[],
): { nodes: CanvasNode[]; edges: CanvasEdge[] } {
  // Derive parent_node_id: the source of the first edge whose target is this node.
  const parentByTarget = new Map<string, string>();
  for (const e of edges) {
    if (e.edge_kind !== 'ai_path' && e.edge_kind !== 'manual_reference') {
      continue;
    }
    if (!parentByTarget.has(e.target_node_id)) {
      parentByTarget.set(e.target_node_id, e.source_node_id);
    }
  }

  const mappedNodes: CanvasNode[] = nodes.map((n) => ({
    node_id: n.node_id,
    parent_node_id: parentByTarget.get(n.node_id) ?? null,
    position: { x: n.position_x ?? 0, y: n.position_y ?? 0 },
    ...(n.title ? { title: n.title } : {}),
    ...(n.content ? { content: n.content } : {}),
    ...(n.thread_context_id ? { thread_context_id: n.thread_context_id } : {}),
  }));

  const mappedEdges: CanvasEdge[] = edges.map((e) => ({
    edge_id: e.edge_id,
    source_node_id: e.source_node_id,
    target_node_id: e.target_node_id,
    edge_kind: e.edge_kind,
    ...(e.label ? { label: e.label } : {}),
  }));

  return { nodes: mappedNodes, edges: mappedEdges };
}

/**
 * Hydrate the canvas from GET /v1/student/sessions/{id}. Returns idle (no fetch)
 * until a sessionId is supplied; ready once the snapshot is mapped.
 */
export function useSessionHydration({
  apiBaseUrl,
  sessionId,
  authorizationToken,
}: UseSessionHydrationArgs): HydrationState {
  const [nodes, setNodes] = useState<CanvasNode[]>([]);
  const [edges, setEdges] = useState<CanvasEdge[]>([]);
  const [status, setStatus] = useState<HydrationStatus>('idle');
  const [reloadKey, setReloadKey] = useState(0);

  /** Increment reloadKey to trigger a re-fetch of GET /sessions. */
  function reload() { setReloadKey((k: number) => k + 1); }

  useEffect(() => {
    if (!apiBaseUrl || !sessionId) {
      setNodes([]);
      setEdges([]);
      setStatus('idle');
      return;
    }

    let cancelled = false;
    setNodes([]);
    setEdges([]);
    setStatus('loading');

    const url = `${apiBaseUrl}/v1/student/sessions/${sessionId}`;
    fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(authorizationToken ? { Authorization: `Bearer ${authorizationToken}` } : {}),
      },
    })
      .then(async (response) => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const body = await response.json();
        if (cancelled) return;
        const mapped = mapSnapshot(body.canvas?.nodes ?? [], body.canvas?.edges ?? []);
        setNodes(mapped.nodes);
        setEdges(mapped.edges);
        setStatus('ready');
      })
      .catch(() => {
        if (!cancelled) {
          setNodes([]);
          setEdges([]);
          setStatus('error');
        }
      });

    return () => {
      cancelled = true;
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [apiBaseUrl, sessionId, authorizationToken, reloadKey]);

  return { nodes, edges, status, reload };
}
