import React, { useState } from 'react';
import {
  ActivityIndicator,
  Button,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import {
  ElectricityLaunchPath,
  bootstrapStudentAuth,
  loadElectricityLaunchPath,
  startElectricitySession,
} from './m4/studentApi';
import { signInWithEmailPassword, signUpWithEmailPassword } from './m4/supabaseAuth';

interface Props {
  apiBaseUrl: string;
  supabaseUrl: string;
  supabaseAnonKey: string;
}

type Status = 'idle' | 'authenticating' | 'ready' | 'starting' | 'error';

export function M4CurriculumAuthScreen({
  apiBaseUrl,
  supabaseUrl,
  supabaseAnonKey,
}: Props) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [launchPath, setLaunchPath] = useState<ElectricityLaunchPath | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [status, setStatus] = useState<Status>('idle');
  const [message, setMessage] = useState('Ready');

  async function authenticate(mode: 'signup' | 'signin') {
    setStatus('authenticating');
    setMessage(mode === 'signup' ? 'Creating account' : 'Signing in');
    setSessionId(null);
    setAccessToken(null);
    setLaunchPath(null);
    try {
      const authArgs = { supabaseUrl, anonKey: supabaseAnonKey, email, password };
      const authResult =
        mode === 'signup'
          ? await signUpWithEmailPassword(authArgs)
          : await signInWithEmailPassword(authArgs);
      await bootstrapStudentAuth({
        apiBaseUrl,
        accessToken: authResult.accessToken,
      });
      const loadedPath = await loadElectricityLaunchPath({
        apiBaseUrl,
        accessToken: authResult.accessToken,
      });
      setAccessToken(authResult.accessToken);
      setLaunchPath(loadedPath);
      setStatus('ready');
      setMessage('Electricity ready');
    } catch (error: unknown) {
      setStatus('error');
      setMessage(error instanceof Error ? error.message : String(error));
    }
  }

  async function startSession() {
    if (!accessToken || !launchPath) return;
    setStatus('starting');
    setMessage('Starting Electricity');
    try {
      const session = await startElectricitySession({
        apiBaseUrl,
        accessToken,
        launchPath,
      });
      setSessionId(session.sessionId);
      setStatus('ready');
      setMessage('Session started');
    } catch (error: unknown) {
      setStatus('error');
      setMessage(error instanceof Error ? error.message : String(error));
    }
  }

  const busy = status === 'authenticating' || status === 'starting';

  return (
    <View style={styles.root}>
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.title}>Mindmap</Text>

        <View style={styles.section}>
          <Text style={styles.label}>Email</Text>
          <TextInput
            testID="m4-email-input"
            value={email}
            onChangeText={setEmail}
            style={styles.input}
            autoCapitalize="none"
            autoCorrect={false}
            keyboardType="email-address"
          />

          <Text style={styles.label}>Password</Text>
          <TextInput
            testID="m4-password-input"
            value={password}
            onChangeText={setPassword}
            style={styles.input}
            secureTextEntry
            autoCapitalize="none"
            autoCorrect={false}
            spellCheck={false}
          />

          <View style={styles.actions}>
            <Button title="Create account" onPress={() => authenticate('signup')} disabled={busy} />
            <Button title="Sign in" onPress={() => authenticate('signin')} disabled={busy} />
          </View>
        </View>

        <View style={styles.launchPanel}>
          <Text style={styles.pathText}>Class 10 / CBSE / Science</Text>
          <Text style={styles.chapterText}>Electricity</Text>
          <Button
            title="Start Electricity"
            onPress={startSession}
            disabled={!launchPath || !accessToken || busy}
          />
        </View>

        <View style={styles.statusRow}>
          {busy ? <ActivityIndicator testID="m4-loading" /> : null}
          <Text style={styles.statusText}>{message}</Text>
        </View>
        {sessionId ? <Text style={styles.sessionText}>Session: {sessionId}</Text> : null}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: '#f6f8fb' },
  container: { padding: 20, gap: 16 },
  title: { fontSize: 28, fontWeight: '700', color: '#111827' },
  section: {
    gap: 8,
    padding: 16,
    borderRadius: 8,
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#dbe2ea',
  },
  label: { fontSize: 13, fontWeight: '600', color: '#334155' },
  input: {
    borderWidth: 1,
    borderColor: '#b8c2cc',
    borderRadius: 6,
    padding: 10,
    fontSize: 15,
    backgroundColor: '#ffffff',
  },
  actions: { gap: 10, marginTop: 8 },
  launchPanel: {
    gap: 8,
    padding: 16,
    borderRadius: 8,
    backgroundColor: '#eef7f1',
    borderWidth: 1,
    borderColor: '#b8d8c0',
  },
  pathText: { fontSize: 13, color: '#475569', fontWeight: '600' },
  chapterText: { fontSize: 22, color: '#14532d', fontWeight: '700' },
  statusRow: { minHeight: 28, flexDirection: 'row', alignItems: 'center', gap: 8 },
  statusText: { color: '#334155', fontSize: 13 },
  sessionText: { fontSize: 13, color: '#14532d', fontWeight: '700' },
});
