/**
 * Creates a durable student-safe branch, then positions its child through checked PATCH.
 * Placement failure recovers the existing child and never recreates the branch.
 * Traceability: phase-3-m3c-infrastructure-remediation-sdd.md §6;
 * canvas-position-write-lifecycle-sdd.md §§8, 13.
 */
import React, { useEffect, useRef, useState } from 'react';
import { Button, Modal, ScrollView, StyleSheet, Text, View } from 'react-native';

import { patchNodePosition } from './apiClient';

export interface EdgeOfferOption { option_id: string; text: string; rank_position: number }
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
  onBranchCreated: () => void;
}

const CHILD_OFFSET = { x: 340, y: 80 };
interface PlacementRecovery {
  childNodeId?: string;
  position: { x: number; y: number };
  phase: 'positioning' | 'failed';
}

export function EdgeOfferSetSheet({
  visible, offerSet, threadContextId, sourcePosition, apiBaseUrl,
  authorizationToken, onClose, onBranchCreated,
}: EdgeOfferSetSheetProps) {
  const [status, setStatus] = useState('Pick a question to explore');
  const [creating, setCreating] = useState(false);
  const [recovery, setRecovery] = useState<PlacementRecovery | null>(null);
  const mountedRef = useRef(false);
  const creationBusyRef = useRef(false);
  const placementBusyRef = useRef(false);
  const requestIdRef = useRef(0);
  const completedRef = useRef(false);

  useEffect(() => {
    mountedRef.current = true;
    return () => { mountedRef.current = false; requestIdRef.current += 1; };
  }, []);

  const headers = () => ({
    'Content-Type': 'application/json',
    ...(authorizationToken ? { Authorization: `Bearer ${authorizationToken}` } : {}),
  });

  function completeThroughReload() {
    if (completedRef.current) return;
    completedRef.current = true;
    requestIdRef.current += 1;
    onBranchCreated();
  }

  async function attemptPlacement(next: PlacementRecovery) {
    if (!next.childNodeId || placementBusyRef.current || completedRef.current) return;
    placementBusyRef.current = true;
    const requestId = ++requestIdRef.current;
    setRecovery({ ...next, phase: 'positioning' });
    try {
      await patchNodePosition(
        apiBaseUrl, offerSet.session_id, next.childNodeId, authorizationToken, next.position,
      );
      if (!mountedRef.current || requestId !== requestIdRef.current || completedRef.current) return;
      placementBusyRef.current = false;
      completeThroughReload();
    } catch {
      if (!mountedRef.current || requestId !== requestIdRef.current || completedRef.current) return;
      placementBusyRef.current = false;
      setRecovery({ ...next, phase: 'failed' });
    }
  }

  async function chooseOption(option: EdgeOfferOption) {
    if (creationBusyRef.current || recovery || completedRef.current) return;
    creationBusyRef.current = true;
    setCreating(true);
    setStatus('Creating new node…');
    try {
      const response = await fetch(
        `${apiBaseUrl}/v1/student/offer-sets/${offerSet.offer_set_id}/choices`,
        { method: 'POST', headers: headers(), body: JSON.stringify({
          session_id: offerSet.session_id, source_node_id: offerSet.source_node_id,
          outcome: 'selected', selected_option_id: option.option_id,
          selected_option_text: option.text, thread_context_id: threadContextId,
        }) },
      );
      if (!response.ok) {
        if (mountedRef.current) {
          creationBusyRef.current = false;
          setCreating(false);
          setStatus(`Failed: HTTP ${response.status}`);
        }
        return;
      }
      const result = await response.json() as { child_node_id?: string };
      if (!mountedRef.current || completedRef.current) return;
      creationBusyRef.current = false;
      setCreating(false);
      setStatus('Branch created');
      const next: PlacementRecovery = {
        childNodeId: result.child_node_id,
        position: { x: sourcePosition.x + CHILD_OFFSET.x, y: sourcePosition.y + CHILD_OFFSET.y },
        phase: result.child_node_id ? 'positioning' : 'failed',
      };
      setRecovery(next);
      if (next.childNodeId) await attemptPlacement(next);
    } catch {
      if (mountedRef.current && !completedRef.current) {
        creationBusyRef.current = false;
        setCreating(false);
        setStatus('Failed: network error');
      }
    }
  }

  function handleClose() {
    if (creationBusyRef.current) return;
    if (recovery) completeThroughReload();
    else onClose();
  }

  const placementActive = recovery?.phase === 'positioning';
  return (
    <Modal animationType="slide" transparent visible={visible} onRequestClose={handleClose}>
      <View style={styles.backdrop}><View style={styles.sheet}>
        <Text style={styles.title}>Explore a question</Text>
        <Text style={styles.status}>{status}</Text>
        {recovery ? <Text style={styles.status}>
          {placementActive ? 'Saving placement…' : 'Placement was not saved'}
        </Text> : null}
        <ScrollView>{offerSet.options.map((option) => (
          <View key={option.option_id} testID={`offer-option-${option.rank_position}`} style={styles.option}>
            <Button title={option.text} onPress={() => { void chooseOption(option); }}
              disabled={creating || recovery !== null} />
          </View>
        ))}</ScrollView>
        {recovery?.phase === 'failed' && recovery.childNodeId ? <View style={styles.option}>
          <Button title="Retry placement" onPress={() => { void attemptPlacement(recovery); }} />
        </View> : null}
        <View style={styles.option}><Button
          title={recovery ? 'Close and reload' : 'Close'} color="#b91c1c"
          onPress={handleClose} disabled={creating}
        /></View>
      </View></View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  backdrop: { flex: 1, justifyContent: 'flex-end', backgroundColor: 'rgba(0,0,0,0.35)' },
  sheet: { backgroundColor: '#ffffff', borderTopLeftRadius: 16, borderTopRightRadius: 16,
    padding: 20, maxHeight: '70%' },
  title: { fontSize: 18, fontWeight: '700', color: '#1f2937', marginBottom: 4 },
  status: { fontSize: 13, color: '#6b7280', marginBottom: 12 },
  option: { marginVertical: 6 },
});
