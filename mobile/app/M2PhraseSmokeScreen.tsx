/**
 * M2 Expo Go smoke screen — Phase 3 M2 Phrase Selection.
 *
 * Usage:
 *  1. Run backend/scripts/dev_smoke_bootstrap.py --dev-smoke
 *  2. Copy the printed apiBaseUrl and auth token into the inputs below.
 *  3. Tap "Start test session" → tap "Open phrase reader".
 *  4. Long-press to select a phrase in the reader, then "Use selected phrase".
 *  5. Tap an option to branch, verify "branch created" status.
 *
 * Security: authToken is entered via secureTextEntry and is never logged.
 * Traceability: docs/planning/sdd/phase-3-phrase-selection-sdd.md §12
 */

import React, { useState } from 'react';
import {
  Button,
  SafeAreaView,
  ScrollView,
  Text,
  TextInput,
  View,
  StyleSheet,
} from 'react-native';
import { PhraseSelectionReaderSheet, OfferChoiceResult } from '../PhraseSelectionReaderSheet';

// Fixed IDs must match backend/scripts/dev_smoke_bootstrap.py
const EXAM_ID = '00000000-0000-4000-8000-000000000001';
const SUBJECT_ID = '00000000-0000-4000-8000-000000000002';
const CHAPTER_ID = '00000000-0000-4000-8000-000000000003';
const CONCEPT_ENTRY_ID = '00000000-0000-4000-8000-000000000004';

/**
 * Dev-only defaults — deterministic because the bootstrap script always uses
 * the same hardcoded secret + fixed student UUID (no exp/iat claims).
 * Set the development URL and token through the documented EXPO_PUBLIC_DEV_* variables.
 */
const DEV_API_BASE_URL = process.env.EXPO_PUBLIC_DEV_API_BASE_URL?.trim() ?? '';
const DEV_AUTH_TOKEN = process.env.EXPO_PUBLIC_DEV_AUTH_TOKEN?.trim() ?? '';

// Passage seeded by the bootstrap script — must match READER_PASSAGE in bootstrap.
const SEEDED_CONTENT =
  'Electric current flows through a closed circuit.\n\n' +
  'When resistance increases, current decreases according to Ohm\'s Law.\n\n' +
  'A short circuit occurs when current bypasses the intended load.';

function randomUUID(): string {
  // Simple RFC4122 v4 UUID without external deps
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16);
  });
}

interface M2PhraseSmokeScreenProps {
  devApiBaseUrl?: string;
  devAuthToken?: string;
}

export function M2PhraseSmokeScreen({
  devApiBaseUrl = DEV_API_BASE_URL,
  devAuthToken = DEV_AUTH_TOKEN,
}: M2PhraseSmokeScreenProps = {}) {
  const [apiBaseUrl, setApiBaseUrl] = useState(devApiBaseUrl);
  const [authToken, setAuthToken] = useState(devAuthToken);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessionStatus, setSessionStatus] = useState('idle');
  const [readerVisible, setReaderVisible] = useState(false);
  const [branchResult, setBranchResult] = useState<string | null>(null);

  // Stable per-session IDs generated once after session starts
  const [nodeId] = useState(randomUUID);
  const [threadContextId] = useState(randomUUID);

  async function startSession() {
    setSessionStatus('starting…');
    setBranchResult(null);
    try {
      const response = await fetch(`${apiBaseUrl}/v1/student/sessions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authToken}`,
        },
        body: JSON.stringify({
          exam_id: EXAM_ID,
          subject_id: SUBJECT_ID,
          chapter_id: CHAPTER_ID,
          concept_entry_id: CONCEPT_ENTRY_ID,
        }),
      });
      const body = await response.json();
      if (response.ok) {
        setSessionId(body.session_id);
        setSessionStatus(`session started: ${body.session_id}`);
      } else {
        setSessionStatus(`failed: ${JSON.stringify(body)}`);
      }
    } catch (err: unknown) {
      setSessionStatus(`error: ${err instanceof Error ? err.message : String(err)}`);
    }
  }

  function openReader() {
    setReaderVisible(true);
  }

  function handleBranchCreated(result: OfferChoiceResult) {
    setBranchResult(result.child_node_id ?? null);
    setReaderVisible(false);
  }

  return (
    <SafeAreaView style={styles.root}>
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.heading}>M2 Phrase Selection Smoke</Text>

        <Text style={styles.label}>API Base URL</Text>
        <TextInput
          testID="api-base-url-input"
          style={styles.input}
          value={apiBaseUrl}
          onChangeText={setApiBaseUrl}
          placeholder="Development backend URL"
          autoCapitalize="none"
          autoCorrect={false}
          keyboardType="url"
        />

        <Text style={styles.label}>Auth Token</Text>
        {/* secureTextEntry masks the JWT at rest on screen (SDD §12).
            Keyboard-mangling workaround: use the "Fill dev defaults" button
            which writes the token programmatically — no secure-keyboard paste needed. */}
        <TextInput
          testID="auth-token-input"
          style={styles.input}
          value={authToken}
          onChangeText={setAuthToken}
          placeholder="Paste token from bootstrap script"
          secureTextEntry
          autoCapitalize="none"
          autoCorrect={false}
          spellCheck={false}
        />

        <View style={styles.button}>
          <Button
            title="Fill dev defaults"
            onPress={() => {
              setApiBaseUrl(devApiBaseUrl);
              setAuthToken(devAuthToken);
            }}
          />
        </View>

        <View style={styles.button}>
          <Button title="Start test session" onPress={startSession} />
        </View>
        <Text style={styles.status}>Status: {sessionStatus}</Text>

        {sessionId ? (
          <>
            <View style={styles.button}>
              <Button title="Open phrase reader" onPress={openReader} />
            </View>
            {branchResult ? (
              <Text style={styles.result}>Branch created: {branchResult}</Text>
            ) : null}
          </>
        ) : null}
      </ScrollView>

      {sessionId ? (
        <PhraseSelectionReaderSheet
          visible={readerVisible}
          apiBaseUrl={apiBaseUrl}
          authorizationToken={authToken}
          node={{
            sessionId,
            nodeId,
            threadContextId,
            content: SEEDED_CONTENT,
          }}
          onClose={() => setReaderVisible(false)}
          onBranchCreated={handleBranchCreated}
        />
      ) : null}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1 },
  container: { padding: 20, gap: 8 },
  heading: { fontSize: 18, fontWeight: 'bold', marginBottom: 8 },
  label: { fontSize: 14, fontWeight: '600', marginTop: 8 },
  input: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 6,
    padding: 10,
    fontSize: 14,
  },
  tokenInput: {
    fontSize: 11,
    fontFamily: 'monospace',
    minHeight: 72,
  },
  button: { marginTop: 12 },
  status: { fontSize: 12, color: '#555', marginTop: 4 },
  result: { fontSize: 13, color: '#007700', marginTop: 8, fontWeight: '600' },
});
