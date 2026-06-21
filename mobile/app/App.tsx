import { StatusBar } from 'expo-status-bar';
import { M2PhraseSmokeScreen } from './M2PhraseSmokeScreen';
import { initSentry } from './observability/sentry';
import { SkiaCanvas } from '../canvas/SkiaCanvas';

// Mobile error tracking (M3 SDD §3, §14). DSN is SENTRY_DSN_MOBILE
// (configuration-reference.md §10), supplied to the bundle via its EXPO_PUBLIC_ form;
// absent locally, initSentry is a no-op.
initSentry(process.env.EXPO_PUBLIC_SENTRY_DSN_MOBILE);

// ── Temporary dev fixtures (SDD §9; replaced by real store in M4) ────────────
// A two-node tree so the canvas is non-empty during Stage 2 device verification.
const DEV_NODES = [
  { node_id: 'root', parent_node_id: null, position: { x: 0, y: 0 } },
  { node_id: 'child1', parent_node_id: 'root', position: { x: 0, y: 160 } },
];
const DEV_EDGES = [
  { edge_id: 'e1', source_node_id: 'root', target_node_id: 'child1', edge_kind: 'ai_path' },
];
const DEV_SCREEN = { width: 390, height: 844 };
const DEV_TRANSFORM = { scale: 1, translateX: 195, translateY: 200 };
// ─────────────────────────────────────────────────────────────────────────────

export default function App() {
  // Toggle: set EXPO_PUBLIC_SHOW_CANVAS=true to see the M3 canvas instead of the M2 smoke screen.
  const showCanvas = process.env.EXPO_PUBLIC_SHOW_CANVAS === 'true';

  if (showCanvas) {
    return (
      <>
        <SkiaCanvas
          nodes={DEV_NODES}
          edges={DEV_EDGES}
          screen={DEV_SCREEN}
          transform={DEV_TRANSFORM}
        />
        <StatusBar style="auto" />
      </>
    );
  }

  return (
    <>
      <M2PhraseSmokeScreen />
      <StatusBar style="auto" />
    </>
  );
}
