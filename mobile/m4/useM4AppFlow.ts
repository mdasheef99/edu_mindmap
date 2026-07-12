import { useEffect, useState } from 'react';

import {
  bootstrapStudentAuth,
  loadElectricityLaunchPath,
  loadStudentDashboard,
  resumeStudentSession,
  startElectricitySession,
} from './studentApi';
import type { ElectricityLaunchPath, StudentDashboard } from './studentApi';
import {
  refreshSupabaseSession,
  signInWithEmailPassword,
  signOutSupabaseSession,
  signUpWithEmailPassword,
} from './supabaseAuth';
import type { SupabaseAuthResult } from './supabaseAuth';
import {
  clearStoredSupabaseSession,
  loadStoredSupabaseSession,
  saveStoredSupabaseSession,
} from './sessionStore';

type Status = 'restoring' | 'idle' | 'authenticating' | 'loading' | 'ready' | 'starting' | 'error';

interface Args {
  apiBaseUrl: string;
  supabaseUrl: string;
  supabaseAnonKey: string;
  onSessionStarted?: (session: { sessionId: string; accessToken: string }) => void;
}

export function useM4AppFlow(args: Args) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [authSession, setAuthSession] = useState<SupabaseAuthResult | null>(null);
  const [dashboard, setDashboard] = useState<StudentDashboard | null>(null);
  const [launchPath, setLaunchPath] = useState<ElectricityLaunchPath | null>(null);
  const [consentAccepted, setConsentAccepted] = useState(false);
  const [consentPreviouslyGranted, setConsentPreviouslyGranted] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [status, setStatus] = useState<Status>('idle');
  const [message, setMessage] = useState('Ready');

  async function initializeSession(session: SupabaseAuthResult): Promise<void> {
    setStatus('loading');
    setMessage('Loading dashboard');
    const bootstrap = await bootstrapStudentAuth({
      apiBaseUrl: args.apiBaseUrl,
      accessToken: session.accessToken,
    });
    setAuthSession(session);
    setConsentPreviouslyGranted(bootstrap.behavioralAnalyticsConsentGranted);
    setConsentAccepted(bootstrap.behavioralAnalyticsConsentGranted);
    const nextDashboard = await loadStudentDashboard({
      apiBaseUrl: args.apiBaseUrl,
      accessToken: session.accessToken,
    });
    setDashboard(nextDashboard);
    setMessage('Loading curriculum');
    const nextPath = await loadElectricityLaunchPath({
      apiBaseUrl: args.apiBaseUrl,
      accessToken: session.accessToken,
    });
    setLaunchPath(nextPath);
    setStatus('ready');
    setMessage('Electricity ready');
  }

  useEffect(() => {
    let active = true;
    async function restore() {
      try {
        const stored = await loadStoredSupabaseSession();
        if (!stored || !active) return;
        setStatus('restoring');
        setMessage('Restoring session');
        const refreshed = await refreshSupabaseSession({
          supabaseUrl: args.supabaseUrl,
          anonKey: args.supabaseAnonKey,
          refreshToken: stored.refreshToken,
        });
        const session = { ...refreshed, userId: refreshed.userId ?? stored.userId };
        await saveStoredSupabaseSession(session);
        if (active) await initializeSession(session);
      } catch {
        await clearStoredSupabaseSession();
        if (active) {
          setStatus('idle');
          setMessage('Session expired. Sign in again.');
        }
      }
    }
    void restore();
    return () => {
      active = false;
    };
  // Restore runs once for the build-time configuration supplied by App.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function authenticate(mode: 'signup' | 'signin') {
    if (!email.includes('@')) {
      setStatus('error');
      setMessage('Enter a valid email address.');
      return;
    }
    if (password.length < 8) {
      setStatus('error');
      setMessage('Password must be at least 8 characters.');
      return;
    }
    setStatus('authenticating');
    setMessage(mode === 'signup' ? 'Creating account' : 'Signing in');
    try {
      const authArgs = {
        supabaseUrl: args.supabaseUrl,
        anonKey: args.supabaseAnonKey,
        email,
        password,
      };
      const session = mode === 'signup'
        ? await signUpWithEmailPassword(authArgs)
        : await signInWithEmailPassword(authArgs);
      await saveStoredSupabaseSession(session);
      await initializeSession(session);
    } catch (error: unknown) {
      setStatus('error');
      setMessage(error instanceof Error ? error.message : String(error));
    }
  }

  async function startSession() {
    if (!authSession || !launchPath || !consentAccepted) return;
    setStatus('starting');
    setMessage('Starting Electricity');
    try {
      const session = await startElectricitySession({
        apiBaseUrl: args.apiBaseUrl,
        accessToken: authSession.accessToken,
        launchPath,
        behavioralAnalyticsConsent: !consentPreviouslyGranted,
      });
      setSessionId(session.sessionId);
      setConsentPreviouslyGranted(true);
      setConsentAccepted(true);
      setStatus('ready');
      setMessage('Session started');
      args.onSessionStarted?.({ sessionId: session.sessionId, accessToken: authSession.accessToken });
    } catch (error: unknown) {
      setStatus('error');
      setMessage(error instanceof Error ? error.message : String(error));
    }
  }

  async function resumeSession(existingSessionId: string) {
    if (!authSession) return;
    setStatus('starting');
    setMessage('Resuming session');
    try {
      const session = await resumeStudentSession({
        apiBaseUrl: args.apiBaseUrl,
        accessToken: authSession.accessToken,
        sessionId: existingSessionId,
      });
      args.onSessionStarted?.({ sessionId: session.sessionId, accessToken: authSession.accessToken });
    } catch (error: unknown) {
      setStatus('error');
      setMessage(error instanceof Error ? error.message : String(error));
    }
  }

  async function signOut() {
    let remoteSignOutFailed = false;
    if (authSession) {
      try {
        await signOutSupabaseSession({
          supabaseUrl: args.supabaseUrl,
          anonKey: args.supabaseAnonKey,
          accessToken: authSession.accessToken,
        });
      } catch {
        remoteSignOutFailed = true;
      }
    }
    await clearStoredSupabaseSession();
    setAuthSession(null);
    setDashboard(null);
    setLaunchPath(null);
    setConsentAccepted(false);
    setConsentPreviouslyGranted(false);
    setSessionId(null);
    setStatus('idle');
    setMessage(remoteSignOutFailed ? 'Signed out locally' : 'Signed out');
  }

  return {
    email, setEmail, password, setPassword, authSession, dashboard, launchPath,
    consentAccepted, setConsentAccepted, consentPreviouslyGranted, sessionId, status, message,
    busy: ['restoring', 'authenticating', 'loading', 'starting'].includes(status),
    authenticate, startSession, resumeSession, signOut,
  };
}
