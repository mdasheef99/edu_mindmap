import { useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { Platform, Text, View, StyleSheet } from 'react-native';
import { M2PhraseSmokeScreen } from './M2PhraseSmokeScreen';
import { initSentry } from './observability/sentry';
import { SkiaCanvas } from '../canvas/SkiaCanvas';
import { useSessionHydration } from '../canvas/useSessionHydration';
import { M4CurriculumAuthScreen } from '../M4CurriculumAuthScreen';

// Mobile error tracking (M3 SDD §3, §14). DSN is SENTRY_DSN_MOBILE
// (configuration-reference.md §10), supplied to the bundle via its EXPO_PUBLIC_ form;
// absent locally, initSentry is a no-op.
initSentry(process.env.EXPO_PUBLIC_SENTRY_DSN_MOBILE);

// ── Canvas wiring (M3-C SDD §5, §8) ──────────────────────────────────────────
// Nodes/edges now hydrate from GET /v1/student/sessions/{id} via useSessionHydration
// (DEV_NODES/DEV_EDGES/DEV_TRANSFORM fixtures removed — G3 mobile side).
const DEV_SCREEN = { width: 390, height: 844 };
// transform: zero translate so §4 seam and §9 culling box agree from the start.
const DEFAULT_TRANSFORM = { scale: 1, translateX: 0, translateY: 0 };
// Edge-`+` discovery chrome (F2) renders only when apiBaseUrl + sessionId are supplied.
// Point at the backend LAN IP so the buttons can POST /v1/student/offer-sets/edge.
const DEV_API_BASE_URL =
  process.env.EXPO_PUBLIC_DEV_API_BASE_URL ??
  (Platform.OS === 'web' ? 'http://127.0.0.1:8000' : 'http://192.168.31.183:8000');
const DEV_SESSION_ID = '00000000-0000-4000-8000-000000000030';
const DEV_AUTH_TOKEN =
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDAwMDAwMC0wMDAwLTQwMDAtODAwMC0wMDAwMDAwMDAwMjAifQ.PdM8x6KPeHghg976eZbcxbeitCbWdqLXh-dqkTQUd-g';
// ─────────────────────────────────────────────────────────────────────────────

export default function App() {
  // Toggle: set EXPO_PUBLIC_SHOW_CANVAS=true to see the M3 canvas.
  const showCanvas = process.env.EXPO_PUBLIC_SHOW_CANVAS === 'true';
  const showM2Smoke = process.env.EXPO_PUBLIC_SHOW_M2_SMOKE === 'true';

  // Canonical transform kept in JS-thread state (§7 dual-state, onTransformEnd write-once-on-end).
  // SkiaCanvas shared values drive live rendering; this state drives the committed culling viewport.
  const [canvasTransform, setCanvasTransform] = useState(DEFAULT_TRANSFORM);

  // Hook runs unconditionally (rules-of-hooks); sessionId is only passed in canvas
  // mode so the M2 smoke screen does not trigger a hydration fetch.
  const { nodes, edges, status, reload } = useSessionHydration({
    apiBaseUrl: DEV_API_BASE_URL,
    sessionId: showCanvas ? DEV_SESSION_ID : undefined,
    authorizationToken: DEV_AUTH_TOKEN,
  });

  if (showCanvas) {
    return (
      <View style={styles.root}>
        <SkiaCanvas
          nodes={nodes}
          edges={edges}
          screen={DEV_SCREEN}
          transform={canvasTransform}
          onTransformEnd={setCanvasTransform}
          apiBaseUrl={DEV_API_BASE_URL}
          authorizationToken={DEV_AUTH_TOKEN}
          sessionId={DEV_SESSION_ID}
          onReloadCanvas={reload}
        />
        {status !== 'ready' || nodes.length === 0 ? (
          <View style={styles.canvasStatus} pointerEvents="none">
            <Text style={styles.canvasStatusText}>
              {status === 'loading'
                ? 'Loading canvas...'
                : status === 'error'
                  ? 'Canvas could not hydrate from the local backend.'
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
        apiBaseUrl={DEV_API_BASE_URL}
        supabaseUrl={process.env.EXPO_PUBLIC_SUPABASE_URL ?? ''}
        supabaseAnonKey={process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY ?? ''}
      />
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
});
