/**
 * EdgeOfferSetSheet — renders the student-safe questions returned by
 * POST /v1/student/offer-sets/edge and, on selection, records the choice
 * (POST /offer-sets/{id}/choices → outcome "selected"). The backend then creates
 * an `ai` child node ("Explore: <question>") + an `ai_path` edge; we PATCH the
 * child's position next to its parent (Seam C) and ask the canvas to re-hydrate
 * so the new node/edge appear.
 *
 * Category Invisibility: the request body carries no analytic fields and no tenant_id.
 *
 * Traceability: phase-3-offer-set-logging-sdd.md §7; phase-3-m3c-infrastructure-
 * remediation-sdd.md §6 (Seam C); backend/app/domain/student/offer_choices.py.
 */

import React, { useState } from 'react';
import { Button, Modal, ScrollView, StyleSheet, Text, View } from 'react-native';

export interface EdgeOfferOption {
  option_id: string;
  text: string;
  rank_position: number;
}

export interface EdgeOfferSet {
  offer_set_id: string;
  session_id: string;
  source_node_id: string;
  launch_method: string;
  options: EdgeOfferOption[];
}

export interface EdgeOfferSetSheetProps {
  visible: boolean;
  offerSet: EdgeOfferSet;
  threadContextId: string;
  sourcePosition: { x: number; y: number };
  apiBaseUrl: string;
  authorizationToken?: string;
  onClose: () => void;
  /** Fired after a child node/edge is created + positioned; canvas should re-hydrate. */
  onBranchCreated: () => void;
}

// Offset of the new child node from its parent (board units) so the edge reads clearly.
const CHILD_OFFSET = { x: 340, y: 80 };

export function EdgeOfferSetSheet({
  visible,
  offerSet,
  threadContextId,
  sourcePosition,
  apiBaseUrl,
  authorizationToken,
  onClose,
  onBranchCreated,
}: EdgeOfferSetSheetProps) {
  const [status, setStatus] = useState('Pick a question to explore');
  const [busy, setBusy] = useState(false);

  function headers() {
    return {
      'Content-Type': 'application/json',
      ...(authorizationToken ? { Authorization: `Bearer ${authorizationToken}` } : {}),
    };
  }

  async function chooseOption(option: EdgeOfferOption) {
    if (busy) return;
    setBusy(true);
    setStatus('Creating new node…');
    try {
      const res = await fetch(
        `${apiBaseUrl}/v1/student/offer-sets/${offerSet.offer_set_id}/choices`,
        {
          method: 'POST',
          headers: headers(),
          body: JSON.stringify({
            session_id: offerSet.session_id,
            source_node_id: offerSet.source_node_id,
            outcome: 'selected',
            selected_option_id: option.option_id,
            selected_option_text: option.text,
            thread_context_id: threadContextId,
          }),
        },
      );
      if (!res.ok) {
        setStatus(`Failed: HTTP ${res.status}`);
        setBusy(false);
        return;
      }
      const result = await res.json();
      // Position the new child next to its parent so the ai_path edge is visible (Seam C).
      if (result.child_node_id) {
        await fetch(
          `${apiBaseUrl}/v1/student/sessions/${offerSet.session_id}/nodes/${result.child_node_id}`,
          {
            method: 'PATCH',
            headers: headers(),
            body: JSON.stringify({
              position_x: sourcePosition.x + CHILD_OFFSET.x,
              position_y: sourcePosition.y + CHILD_OFFSET.y,
            }),
          },
        ).catch(() => undefined);
      }
      setBusy(false);
      setStatus('Pick a question to explore');
      onBranchCreated();
    } catch {
      setStatus('Failed: network error');
      setBusy(false);
    }
  }

  return (
    <Modal animationType="slide" transparent visible={visible} onRequestClose={onClose}>
      <View style={styles.backdrop}>
        <View style={styles.sheet}>
          <Text style={styles.title}>Explore a question</Text>
          <Text style={styles.status}>{status}</Text>
          <ScrollView>
            {offerSet.options.map((option) => (
              <View key={option.option_id} testID={`offer-option-${option.rank_position}`} style={styles.option}>
                <Button title={option.text} onPress={() => chooseOption(option)} disabled={busy} />
              </View>
            ))}
          </ScrollView>
          <View style={styles.option}>
            <Button title="Close" color="#b91c1c" onPress={onClose} />
          </View>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  backdrop: { flex: 1, justifyContent: 'flex-end', backgroundColor: 'rgba(0,0,0,0.35)' },
  sheet: {
    backgroundColor: '#ffffff',
    borderTopLeftRadius: 16,
    borderTopRightRadius: 16,
    padding: 20,
    maxHeight: '70%',
  },
  title: { fontSize: 18, fontWeight: '700', color: '#1f2937', marginBottom: 4 },
  status: { fontSize: 13, color: '#6b7280', marginBottom: 12 },
  option: { marginVertical: 6 },
});
