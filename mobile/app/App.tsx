import { useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { Text, View, StyleSheet } from 'react-native';
import { M2PhraseSmokeScreen } from './M2PhraseSmokeScreen';
import { initSentry } from './observability/sentry';
import { SkiaCanvas } from '../canvas/SkiaCanvas';
import { useSessionHydration } from '../canvas/useSessionHydration';
import { resolveDevCanvasConfig } from './devCanvasConfig';

// Mobile error tracking (M3 SDD §3, §14). DSN is supplied through the
// EXPO_PUBLIC form of the configuration-reference.md §10 setting.
initSentry(process.env.EXPO_PUBLIC_SENTRY_DSN_MOBILE);

const DEV_SCREEN = { width: 390, height: 844 };
const DEFAULT_TRANSFORM = { scale: 1, translateX: 0, translateY: 0 };

export default function App() {
  const showCanvas = process.env.EXPO_PUBLIC_SHOW_CANVAS === 'true';
  const devCanvas = resolveDevCanvasConfig(showCanvas, process.env);
  const config = devCanvas.enabled && 'config' in devCanvas ? devCanvas.config : undefined;
  const [canvasTransform, setCanvasTransform] = useState(DEFAULT_TRANSFORM);

  // The hook remains unconditional. When Canvas mode is disabled or invalidly
  // configured, undefined inputs keep hydration idle.
  const { nodes, edges, status, reload } = useSessionHydration({
    apiBaseUrl: config?.apiBaseUrl,
    sessionId: config?.sessionId,
    authorizationToken: config?.authorizationToken,
  });

  if (showCanvas) {
    if (!config) {
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
          screen={DEV_SCREEN}
          transform={canvasTransform}
          onTransformEnd={setCanvasTransform}
          apiBaseUrl={config.apiBaseUrl}
          authorizationToken={config.authorizationToken}
          sessionId={config.sessionId}
          onReloadCanvas={reload}
        />
        {status !== 'ready' || nodes.length === 0 ? (
          <View style={styles.canvasStatus} pointerEvents="none">
            <Text style={styles.canvasStatusText}>
              {status === 'loading'
                ? 'Loading canvas...'
                : status === 'error'
                  ? 'Canvas could not hydrate from the configured development backend.'
                  : 'No canvas nodes loaded.'}
            </Text>
          </View>
        ) : null}
        <StatusBar style="auto" />
      </View>
    );
  }

  return (
    <View style={styles.root}>
      <M2PhraseSmokeScreen />
      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1 },
  canvasStatus: {
    position: 'absolute',
    left: 16,
    right: 16,
    top: 24,
    padding: 12,
    borderRadius: 8,
    backgroundColor: 'rgba(17, 24, 39, 0.82)',
  },
  canvasStatusText: { color: '#ffffff', fontSize: 13, fontWeight: '600' },
  canvasConfigError: { margin: 24, color: '#991b1b' },
});
