import { useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, useWindowDimensions, View } from 'react-native';

import { M4CurriculumAuthScreen } from '../M4CurriculumAuthScreen';
import { SkiaCanvas } from '../canvas/SkiaCanvas';
import { useSessionHydration } from '../canvas/useSessionHydration';
import { resolveDevCanvasConfig } from './devCanvasConfig';
import { M2PhraseSmokeScreen } from './M2PhraseSmokeScreen';
import { initSentry } from './observability/sentry';

initSentry(process.env.EXPO_PUBLIC_SENTRY_DSN_MOBILE);

const DEFAULT_TRANSFORM = { scale: 1, translateX: 0, translateY: 0 };

export default function App() {
  const showCanvas = process.env.EXPO_PUBLIC_SHOW_CANVAS === 'true';
  const showM2Smoke = process.env.EXPO_PUBLIC_SHOW_M2_SMOKE === 'true';
  const devCanvas = resolveDevCanvasConfig(showCanvas, {
    EXPO_PUBLIC_DEV_API_BASE_URL: process.env.EXPO_PUBLIC_DEV_API_BASE_URL,
    EXPO_PUBLIC_DEV_SESSION_ID: process.env.EXPO_PUBLIC_DEV_SESSION_ID,
    EXPO_PUBLIC_DEV_AUTH_TOKEN: process.env.EXPO_PUBLIC_DEV_AUTH_TOKEN,
  });
  const devConfig = devCanvas.enabled && 'config' in devCanvas ? devCanvas.config : undefined;
  const window = useWindowDimensions();
  const [m4Session, setM4Session] = useState<{ sessionId: string; accessToken: string } | null>(null);
  const [canvasTransform, setCanvasTransform] = useState(DEFAULT_TRANSFORM);

  const configuredApiUrl = configuredValue(process.env.EXPO_PUBLIC_API_BASE_URL);
  const apiBaseUrl = m4Session ? configuredApiUrl : devConfig?.apiBaseUrl;
  const activeSessionId = m4Session?.sessionId ?? devConfig?.sessionId;
  const activeToken = m4Session?.accessToken ?? devConfig?.authorizationToken;

  const { nodes, edges, status, reload } = useSessionHydration({
    apiBaseUrl,
    sessionId: activeSessionId,
    authorizationToken: activeToken,
  });

  if (m4Session || showCanvas) {
    if (!m4Session && !devConfig) {
      const error =
        devCanvas.enabled && 'error' in devCanvas
          ? devCanvas.error
          : 'Development Canvas configuration is unavailable.';
      return (
        <View style={styles.root}>
          <Text style={styles.canvasConfigError}>{error}</Text>
          <StatusBar style="auto" />
        </View>
      );
    }

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
        apiBaseUrl={configuredApiUrl ?? ''}
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
  canvasConfigError: { margin: 24, color: '#991b1b' },
});
