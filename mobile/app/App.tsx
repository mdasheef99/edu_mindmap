import { useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { Platform, StyleSheet, Text, useWindowDimensions, View } from 'react-native';

import { M4CurriculumAuthScreen } from '../M4CurriculumAuthScreen';
import { SkiaCanvas } from '../canvas/SkiaCanvas';
import { useSessionHydration } from '../canvas/useSessionHydration';
import { M2PhraseSmokeScreen } from './M2PhraseSmokeScreen';
import { initSentry } from './observability/sentry';

// M3 SDD §3, §14: absent locally, Sentry initialization is a no-op.
initSentry(process.env.EXPO_PUBLIC_SENTRY_DSN_MOBILE);

const DEFAULT_TRANSFORM = { scale: 1, translateX: 0, translateY: 0 };
const DEV_SESSION_ID = '00000000-0000-4000-8000-000000000030';
const DEV_AUTH_TOKEN =
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDAwMDAwMC0wMDAwLTQwMDAtODAwMC0wMDAwMDAwMDAwMjAifQ.PdM8x6KPeHghg976eZbcxbeitCbWdqLXh-dqkTQUd-g';

export default function App() {
  const showCanvas = process.env.EXPO_PUBLIC_SHOW_CANVAS === 'true';
  const showM2Smoke = process.env.EXPO_PUBLIC_SHOW_M2_SMOKE === 'true';
  const window = useWindowDimensions();
  const [m4Session, setM4Session] = useState<{ sessionId: string; accessToken: string } | null>(null);
  const [canvasTransform, setCanvasTransform] = useState(DEFAULT_TRANSFORM);

  const configuredApiUrl = configuredValue(process.env.EXPO_PUBLIC_API_BASE_URL);
  const devCanvasApiUrl = Platform.OS === 'web'
    ? 'http://127.0.0.1:8000'
    : 'http://192.168.31.183:8000';
  const apiBaseUrl = configuredApiUrl ?? (showCanvas ? devCanvasApiUrl : '');
  const activeSessionId = m4Session?.sessionId ?? (showCanvas ? DEV_SESSION_ID : undefined);
  const activeToken = m4Session?.accessToken ?? (showCanvas ? DEV_AUTH_TOKEN : undefined);

  // M3-C §5/§8: authenticated M4 session values hydrate the durable canvas.
  const { nodes, edges, status, reload } = useSessionHydration({
    apiBaseUrl,
    sessionId: activeSessionId,
    authorizationToken: activeToken,
  });

  if (m4Session || showCanvas) {
    return (
      <View style={styles.root}>
        <SkiaCanvas
          nodes={nodes}
          edges={edges}
          screen={{ width: window.width, height: window.height }}
          transform={canvasTransform}
          onTransformEnd={setCanvasTransform}
          apiBaseUrl={apiBaseUrl}
          authorizationToken={activeToken}
          sessionId={activeSessionId}
          onReloadCanvas={reload}
        />
        {status !== 'ready' || nodes.length === 0 ? (
          <View style={styles.canvasStatus} pointerEvents="none">
            <Text style={styles.canvasStatusText}>
              {status === 'loading'
                ? 'Loading canvas...'
                : status === 'error'
                  ? 'Canvas could not hydrate from the backend.'
                  : 'No canvas nodes loaded.'}
            </Text>
          </View>
        ) : null}
        <StatusBar style="auto" />
      </View>
    );
  }

  if (showM2Smoke) {
    return (
      <View style={styles.root}>
        <M2PhraseSmokeScreen />
        <StatusBar style="auto" />
      </View>
    );
  }

  return (
    <View style={styles.root}>
      <M4CurriculumAuthScreen
        apiBaseUrl={apiBaseUrl}
        supabaseUrl={configuredValue(process.env.EXPO_PUBLIC_SUPABASE_URL) ?? ''}
        supabaseAnonKey={configuredValue(process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY) ?? ''}
        onSessionStarted={setM4Session}
      />
      <StatusBar style="auto" />
    </View>
  );
}

function configuredValue(value: string | undefined): string | undefined {
  const trimmed = value?.trim();
  if (!trimmed || trimmed.startsWith('<')) return undefined;
  return trimmed;
}

const styles = StyleSheet.create({
  root: { flex: 1 },
  canvasStatus: {
    position: 'absolute', left: 16, right: 16, top: 24, padding: 12,
    borderRadius: 8, backgroundColor: 'rgba(17, 24, 39, 0.82)',
  },
  canvasStatusText: { color: '#ffffff', fontSize: 13, fontWeight: '600' },
});
