import React from 'react';
import {
  ActivityIndicator,
  Button,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  TextInput,
  View,
} from 'react-native';

import { useM4AppFlow } from './m4/useM4AppFlow';

interface Props {
  apiBaseUrl: string;
  supabaseUrl: string;
  supabaseAnonKey: string;
  onSessionStarted?: (session: { sessionId: string; accessToken: string }) => void;
}

export function M4CurriculumAuthScreen(props: Props) {
  const flow = useM4AppFlow(props);
  const configured = Boolean(
    props.apiBaseUrl.trim() && props.supabaseUrl.trim() && props.supabaseAnonKey.trim(),
  );

  if (!configured) {
    return (
      <View style={styles.centered}>
        <Text style={styles.title}>Mindmap</Text>
        <Text style={styles.errorTitle}>M4 configuration is incomplete</Text>
        <Text style={styles.statusText}>
          Set EXPO_PUBLIC_API_BASE_URL, EXPO_PUBLIC_SUPABASE_URL, and
          EXPO_PUBLIC_SUPABASE_ANON_KEY.
        </Text>
      </View>
    );
  }

  return (
    <View style={styles.root}>
      <ScrollView contentInsetAdjustmentBehavior="automatic" contentContainerStyle={styles.container}>
        <View style={styles.header}>
          <View>
            <Text style={styles.eyebrow}>CLASS 10 · CBSE · SCIENCE</Text>
            <Text style={styles.title}>Mindmap</Text>
          </View>
          {flow.authSession ? <Button title="Sign out" onPress={flow.signOut} disabled={flow.busy} /> : null}
        </View>

        {!flow.authSession ? (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Continue learning</Text>
            <Text style={styles.supporting}>Create an account or sign in to open your curriculum.</Text>
            <Text style={styles.label}>Email</Text>
            <TextInput
              testID="m4-email-input"
              value={flow.email}
              onChangeText={flow.setEmail}
              style={styles.input}
              autoCapitalize="none"
              autoCorrect={false}
              keyboardType="email-address"
            />
            <Text style={styles.label}>Password</Text>
            <TextInput
              testID="m4-password-input"
              value={flow.password}
              onChangeText={flow.setPassword}
              style={styles.input}
              secureTextEntry
              autoCapitalize="none"
              autoCorrect={false}
              spellCheck={false}
            />
            <View style={styles.actions}>
              <Button title="Create account" onPress={() => flow.authenticate('signup')} disabled={flow.busy} />
              <Button title="Sign in" onPress={() => flow.authenticate('signin')} disabled={flow.busy} />
            </View>
          </View>
        ) : null}

        {flow.dashboard?.continueLearning ? (
          <View style={styles.continueCard}>
            <Text style={styles.eyebrow}>CONTINUE LEARNING</Text>
            <Text style={styles.chapterTitle}>{flow.dashboard.continueLearning.chapterTitle}</Text>
            <Text style={styles.supporting}>Your existing mind map is ready where you left it.</Text>
            <Button
              title={`Resume ${flow.dashboard.continueLearning.chapterTitle}`}
              onPress={() => flow.resumeSession(flow.dashboard!.continueLearning!.sessionId)}
              disabled={flow.busy}
            />
          </View>
        ) : null}

        {flow.launchPath ? (
          <View style={styles.card}>
            <Text style={styles.eyebrow}>CURRICULUM SELECTION</Text>
            <Text style={styles.cardTitle}>Choose your chapter</Text>
            <View style={styles.selectionGrid}>
              <Selection label="Class" value={flow.launchPath.classLabel} />
              <Selection label="Exam" value={flow.launchPath.examName} />
              <Selection label="Subject" value={flow.launchPath.subjectName} />
              <Selection label="Chapter" value={flow.launchPath.chapterTitle} />
              <Selection label="Starting concept" value={flow.launchPath.conceptTitle} />
            </View>
            {flow.consentPreviouslyGranted ? (
              <Text style={styles.consentRecorded}>Consent already recorded</Text>
            ) : (
              <View style={styles.consentRow}>
                <View style={styles.consentCopy}>
                  <Text style={styles.label}>Learning-data acknowledgement</Text>
                  <Text style={styles.supporting}>
                    I agree that my learning activity may be used to personalize this experience.
                  </Text>
                </View>
                <Switch
                  testID="m4-consent-switch"
                  value={flow.consentAccepted}
                  onValueChange={flow.setConsentAccepted}
                />
              </View>
            )}
            <Button
              title={`Start ${flow.launchPath.chapterTitle}`}
              onPress={flow.startSession}
              disabled={!flow.consentAccepted || flow.busy}
            />
          </View>
        ) : null}

        {flow.dashboard && flow.dashboard.recentSessions.length > 0 ? (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Recent sessions</Text>
            {flow.dashboard.recentSessions.map((session) => (
              <View key={session.sessionId} style={styles.recentRow}>
                <View>
                  <Text style={styles.label}>{session.chapterTitle}</Text>
                  <Text style={styles.supporting}>{session.status}</Text>
                </View>
                <Button title="Resume" onPress={() => flow.resumeSession(session.sessionId)} disabled={flow.busy} />
              </View>
            ))}
          </View>
        ) : null}

        <View style={styles.statusRow}>
          {flow.busy ? <ActivityIndicator testID="m4-loading" /> : null}
          <Text style={flow.status === 'error' ? styles.errorText : styles.statusText}>{flow.message}</Text>
        </View>
        {flow.sessionId ? <Text style={styles.sessionText}>Session: {flow.sessionId}</Text> : null}
      </ScrollView>
    </View>
  );
}

function Selection({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.selection}>
      <Text style={styles.selectionLabel}>{label}</Text>
      <Text style={styles.selectionValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: '#f4f7f5' },
  centered: { flex: 1, justifyContent: 'center', padding: 24, gap: 10, backgroundColor: '#f4f7f5' },
  container: { padding: 20, paddingBottom: 40, gap: 16 },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 12 },
  eyebrow: { fontSize: 11, letterSpacing: 1.1, fontWeight: '700', color: '#52705b' },
  title: { fontSize: 30, fontWeight: '800', color: '#12251a' },
  card: { gap: 10, padding: 16, borderRadius: 14, backgroundColor: '#ffffff', borderWidth: 1, borderColor: '#d8e2db' },
  continueCard: { gap: 10, padding: 18, borderRadius: 14, backgroundColor: '#e5f4e9', borderWidth: 1, borderColor: '#afd1b8' },
  cardTitle: { fontSize: 19, fontWeight: '700', color: '#163521' },
  chapterTitle: { fontSize: 24, fontWeight: '800', color: '#14532d' },
  label: { fontSize: 13, fontWeight: '700', color: '#334b3b' },
  supporting: { fontSize: 13, lineHeight: 18, color: '#607066' },
  input: { borderWidth: 1, borderColor: '#b8c7bd', borderRadius: 9, padding: 11, fontSize: 15, backgroundColor: '#ffffff' },
  actions: { gap: 8, marginTop: 4 },
  selectionGrid: { gap: 8 },
  selection: { flexDirection: 'row', justifyContent: 'space-between', gap: 12, padding: 11, borderRadius: 9, backgroundColor: '#f1f6f2' },
  selectionLabel: { fontSize: 12, color: '#687a6e' },
  selectionValue: { flexShrink: 1, textAlign: 'right', fontSize: 13, fontWeight: '700', color: '#1d3b27' },
  consentRow: { flexDirection: 'row', alignItems: 'center', gap: 12, paddingVertical: 8 },
  consentCopy: { flex: 1, gap: 3 },
  consentRecorded: { fontSize: 13, color: '#52705b', fontWeight: '700', paddingVertical: 8 },
  recentRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 12, borderTopWidth: 1, borderTopColor: '#e6ece8', paddingTop: 10 },
  statusRow: { minHeight: 28, flexDirection: 'row', alignItems: 'center', gap: 8 },
  statusText: { color: '#4b6253', fontSize: 13 },
  errorTitle: { color: '#9f1239', fontSize: 18, fontWeight: '800' },
  errorText: { color: '#9f1239', fontSize: 13 },
  sessionText: { fontSize: 13, color: '#14532d', fontWeight: '700' },
});
