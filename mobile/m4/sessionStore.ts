import * as SecureStore from 'expo-secure-store';

import type { SupabaseAuthResult } from './supabaseAuth';

const SESSION_KEY = 'mindmap.m4.supabase-session.v1';

function webStorage(): Storage | null {
  if (process.env.EXPO_OS !== 'web') return null;
  return typeof globalThis.localStorage === 'undefined' ? null : globalThis.localStorage;
}

export async function saveStoredSupabaseSession(session: SupabaseAuthResult): Promise<void> {
  const value = JSON.stringify(session);
  const web = webStorage();
  if (web) {
    web.setItem(SESSION_KEY, value);
    return;
  }
  await SecureStore.setItemAsync(SESSION_KEY, value);
}

export async function loadStoredSupabaseSession(): Promise<SupabaseAuthResult | null> {
  const web = webStorage();
  const value = web ? web.getItem(SESSION_KEY) : await SecureStore.getItemAsync(SESSION_KEY);
  if (!value) return null;
  try {
    const parsed = JSON.parse(value) as Partial<SupabaseAuthResult>;
    if (
      typeof parsed.accessToken !== 'string'
      || typeof parsed.refreshToken !== 'string'
      || typeof parsed.expiresAt !== 'number'
    ) {
      await clearStoredSupabaseSession();
      return null;
    }
    return {
      accessToken: parsed.accessToken,
      refreshToken: parsed.refreshToken,
      expiresAt: parsed.expiresAt,
      userId: typeof parsed.userId === 'string' ? parsed.userId : null,
    };
  } catch {
    await clearStoredSupabaseSession();
    return null;
  }
}

export async function clearStoredSupabaseSession(): Promise<void> {
  const web = webStorage();
  if (web) {
    web.removeItem(SESSION_KEY);
    return;
  }
  await SecureStore.deleteItemAsync(SESSION_KEY);
}

