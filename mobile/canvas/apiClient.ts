/**
 * apiClient — lightweight client-event POST helper (M3-C SDD §7; G4/G5 fix).
 *
 * `postClientEvent` wraps POST /v1/student/sessions/{id}/events (Seam A).
 * Fire-and-forget: callers do NOT await. All required envelope fields
 * (event_id, occurred_at) are constructed here; scope fields (tenant_id,
 * actor_user_id, session_id) are overwritten server-side (_apply_backend_scope).
 *
 * `throttledPostViewport` rate-limits viewport_changed events to
 * VIEWPORT_EVENT_THROTTLE_MS (1000 ms default; configuration-reference.md §3).
 *
 * Traceability:
 * - docs/planning/sdd/phase-3-m3c-infrastructure-remediation-sdd.md §7.1, §7.2
 * - docs/api/student-api-spec.md §5 (POST /events whitelist)
 * - docs/configuration-reference.md §3 (VIEWPORT_EVENT_THROTTLE_MS)
 */

/** Milliseconds between consecutive viewport_changed events (§3). */
export const VIEWPORT_EVENT_THROTTLE_MS = 1000;

export interface ClientEvent {
  event_type: string;
  event_version: number;
  session_id: string;
  payload: Record<string, unknown>;
  /** Optional — included for node_visited / node_position_updated. */
  node_id?: string;
  [key: string]: unknown;
}

/** Simple RFC4122 v4 UUID without external deps (mirrors M2PhraseSmokeScreen). */
function randomUUID(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16);
  });
}

/**
 * Fire-and-forget: POST one event to the Seam A batch endpoint.
 * Envelopes the event with event_id + occurred_at; scope fields are
 * overwritten by the backend (Tenant Isolation invariant).
 */
export function postClientEvent(
  apiBaseUrl: string,
  sessionId: string,
  authorizationToken: string | undefined,
  event: ClientEvent,
): void {
  const envelope = {
    ...event,
    event_id: randomUUID(),
    occurred_at: new Date().toISOString(),
  };

  const url = `${apiBaseUrl}/v1/student/sessions/${sessionId}/events`;
  const body = JSON.stringify({ events: [envelope] });

  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(authorizationToken ? { Authorization: `Bearer ${authorizationToken}` } : {}),
    },
    body,
  }).catch(() => {
    // Swallow errors — event emission is best-effort and must not disrupt UX.
  });
}

export interface NodePositionAcknowledgement {
  nodeId: string;
  position: { x: number; y: number };
}

interface NodePositionResponseBody {
  node_id: string;
  position_x: number;
  position_y: number;
}

/** Persist one completed drag-end position and return the backend acknowledgement. */
export async function patchNodePosition(
  apiBaseUrl: string,
  sessionId: string,
  nodeId: string,
  authorizationToken: string | undefined,
  position: { x: number; y: number },
): Promise<NodePositionAcknowledgement> {
  const url = `${apiBaseUrl}/v1/student/sessions/${sessionId}/nodes/${nodeId}`;
  const response = await fetch(url, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      ...(authorizationToken ? { Authorization: `Bearer ${authorizationToken}` } : {}),
    },
    body: JSON.stringify({ position_x: position.x, position_y: position.y }),
  });
  if (!response.ok) {
    throw new Error(`Node position update failed with HTTP ${response.status}`);
  }
  const body = (await response.json()) as NodePositionResponseBody;
  return {
    nodeId: body.node_id,
    position: { x: body.position_x, y: body.position_y },
  };
}

// ── Throttled viewport helper ─────────────────────────────────────────────────

const _lastViewportPostBySession = new Map<string, number>();

/**
 * Throttled wrapper around postClientEvent for viewport_changed events.
 * Drops calls that arrive within VIEWPORT_EVENT_THROTTLE_MS of the last post.
 */
export function throttledPostViewport(
  apiBaseUrl: string,
  sessionId: string,
  authorizationToken: string | undefined,
  event: ClientEvent,
): void {
  const now = Date.now();
  const lastPostedAt = _lastViewportPostBySession.get(sessionId) ?? 0;
  if (now - lastPostedAt >= VIEWPORT_EVENT_THROTTLE_MS) {
    _lastViewportPostBySession.set(sessionId, now);
    postClientEvent(apiBaseUrl, sessionId, authorizationToken, event);
  }
}
