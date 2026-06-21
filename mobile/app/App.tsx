import { StatusBar } from 'expo-status-bar';
import { M2PhraseSmokeScreen } from './M2PhraseSmokeScreen';
import { initSentry } from './observability/sentry';

// Mobile error tracking (M3 SDD §3, §14). DSN is SENTRY_DSN_MOBILE
// (configuration-reference.md §10), supplied to the bundle via its EXPO_PUBLIC_ form;
// absent locally, initSentry is a no-op.
initSentry(process.env.EXPO_PUBLIC_SENTRY_DSN_MOBILE);

export default function App() {
  return (
    <>
      <M2PhraseSmokeScreen />
      <StatusBar style="auto" />
    </>
  );
}
