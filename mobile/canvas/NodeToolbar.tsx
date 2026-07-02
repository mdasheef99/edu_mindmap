/**
 * NodeToolbar — node-level action toolbar for the selected node (M3-B SDD §5.3; MVP §3.3).
 *
 * Native View chrome (ADR-0013) anchored above the node via toolbarPosition (no inline seam
 * math). Actions are category-neutral and exclude body editing (data-contract §3 — learners
 * never edit node content):
 *   • Explore → opens the edge-`+` offer-set flow (F2), via onExplore.
 *   • Delete  → explicit confirmation → DELETE /v1/student/sessions/{session_id}/nodes/
 *               {node_id}?confirmed=true (cascade endpoint; data-contract §10). No reattach
 *               (ADR-blocked). onDeleted fires on success.
 *
 * Traceability: phase-3-m3b-canvas-feature-parity-sdd.md §5.3; MVP §3.3, §4.3 L260;
 * session-path-data-contract.md §3, §10; backend/app/api/student/nodes.py.
 */

import React, { useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { CanvasTransform } from './coordinateSystem';
import { toolbarPosition, OverlayNode, NODE_SIZE } from './nodeOverlay';

/**
 * Server response from DELETE /v1/student/sessions/{session_id}/nodes/{node_id}?confirmed=true.
 * Mirrors backend NodeDeletionResponse (domain/student/deletions.py).
 * Traceability: M3-C SDD §6 (TC-M1/TC-M2), session-path-data-contract.md §10.
 */
export interface NodeDeletionResponse {
  session_id: string;
  root_node_id: string;
  deleted_node_ids: string[];
  deleted_edge_ids: string[];
  confirmed: boolean;
}

export interface NodeToolbarProps {
  node: OverlayNode;
  transform: CanvasTransform;
  nodeSize?: [number, number];
  apiBaseUrl: string;
  authorizationToken?: string;
  sessionId: string;
  onExplore?: (node: OverlayNode) => void;
  /** Receives the full cascade response (not just the tapped node — G1 fix). */
  onDeleted?: (result: NodeDeletionResponse) => void;
  onError?: (error: unknown) => void;
}

export function NodeToolbar({
  node,
  transform,
  nodeSize = NODE_SIZE,
  apiBaseUrl,
  authorizationToken,
  sessionId,
  onExplore,
  onDeleted,
  onError,
}: NodeToolbarProps) {
  const [confirming, setConfirming] = useState(false);
  const anchor = toolbarPosition(node, transform, nodeSize);

  async function confirmDelete() {
    try {
      const url =
        `${apiBaseUrl}/v1/student/sessions/${sessionId}/nodes/${node.node_id}?confirmed=true`;
      const response = await fetch(url, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          ...(authorizationToken ? { Authorization: `Bearer ${authorizationToken}` } : {}),
        },
      });
      if (response.ok) {
        // Consume full cascade payload (G1 fix — do not discard response body).
        const body: NodeDeletionResponse = await response.json();
        onDeleted?.(body);
      } else {
        onError?.(new Error(`HTTP ${response.status}: ${response.statusText}`));
      }
    } catch (err) {
      // Surface network or fetch failures to the caller so they can show UI.
      onError?.(err);
    } finally {
      setConfirming(false);
    }
  }

  return (
    <View style={[styles.toolbar, { left: anchor.x, top: anchor.y - TOOLBAR_OFFSET }]}>
      {confirming ? (
        <>
          <Pressable
            style={styles.action}
            onPress={confirmDelete}
            accessibilityRole="button"
            accessibilityLabel="Confirm delete node"
          >
            <Text style={styles.danger}>Confirm</Text>
          </Pressable>
          <Pressable
            style={styles.action}
            onPress={() => setConfirming(false)}
            accessibilityRole="button"
            accessibilityLabel="Cancel delete"
          >
            <Text style={styles.label}>Cancel</Text>
          </Pressable>
        </>
      ) : (
        <>
          <Pressable
            style={styles.action}
            onPress={() => onExplore?.(node)}
            accessibilityRole="button"
            accessibilityLabel="Explore from node"
          >
            <Text style={styles.label}>Explore</Text>
          </Pressable>
          <Pressable
            style={styles.action}
            onPress={() => setConfirming(true)}
            accessibilityRole="button"
            accessibilityLabel="Delete node"
          >
            <Text style={styles.danger}>Delete</Text>
          </Pressable>
        </>
      )}
    </View>
  );
}

const TOOLBAR_OFFSET = 8; // small gap above the node's top edge

const styles = StyleSheet.create({
  toolbar: {
    position: 'absolute',
    flexDirection: 'row',
    backgroundColor: '#ffffff',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#d1d5db',
    paddingHorizontal: 4,
    paddingVertical: 2,
  },
  action: { paddingHorizontal: 10, paddingVertical: 6 },
  label: { fontSize: 13, color: '#3a3a5c', fontWeight: '600' },
  danger: { fontSize: 13, color: '#b91c1c', fontWeight: '700' },
});
