export interface SupabaseEmailPasswordArgs {
  supabaseUrl: string;
  anonKey: string;
  email: string;
  password: string;
}

export interface SupabaseAuthResult {
  accessToken: string;
  refreshToken: string;
  expiresAt: number;
  userId: string | null;
}

export interface SupabaseRefreshArgs {
  supabaseUrl: string;
  anonKey: string;
  refreshToken: string;
}

export interface SupabaseSignOutArgs {
  supabaseUrl: string;
  anonKey: string;
  accessToken: string;
}

interface SupabaseTokenResponse {
  access_token?: string;
  refresh_token?: string;
  expires_at?: number;
  expires_in?: number;
  user?: { id?: string };
  code?: string;
  error?: string;
  error_code?: string;
  msg?: string;
  error_description?: string;
}

export async function signUpWithEmailPassword(
  args: SupabaseEmailPasswordArgs,
): Promise<SupabaseAuthResult> {
  return requestSupabaseAuth(`${trimTrailingSlash(args.supabaseUrl)}/auth/v1/signup`, args);
}

export async function signInWithEmailPassword(
  args: SupabaseEmailPasswordArgs,
): Promise<SupabaseAuthResult> {
  return requestSupabaseAuth(
    `${trimTrailingSlash(args.supabaseUrl)}/auth/v1/token?grant_type=password`,
    args,
  );
}

export async function refreshSupabaseSession(
  args: SupabaseRefreshArgs,
): Promise<SupabaseAuthResult> {
  validateSupabaseAuthConfig({
    supabaseUrl: args.supabaseUrl,
    anonKey: args.anonKey,
    email: 'refresh@local.invalid',
    password: 'refresh-token',
  });
  return requestSupabaseToken(
    `${trimTrailingSlash(args.supabaseUrl)}/auth/v1/token?grant_type=refresh_token`,
    args.anonKey,
    { refresh_token: args.refreshToken },
  );
}

export async function signOutSupabaseSession(args: SupabaseSignOutArgs): Promise<void> {
  if (!args.supabaseUrl.trim() || !args.anonKey.trim()) {
    throw new Error('Supabase auth is not configured');
  }
  const response = await fetch(`${trimTrailingSlash(args.supabaseUrl)}/auth/v1/logout`, {
    method: 'POST',
    headers: {
      apikey: args.anonKey,
      Authorization: `Bearer ${args.accessToken}`,
    },
  });
  if (!response.ok) {
    throw new Error(`Supabase sign-out failed: ${response.status}`);
  }
}

async function requestSupabaseAuth(
  url: string,
  args: SupabaseEmailPasswordArgs,
): Promise<SupabaseAuthResult> {
  validateSupabaseAuthConfig(args);
  return requestSupabaseToken(url, args.anonKey, { email: args.email, password: args.password });
}

async function requestSupabaseToken(
  url: string,
  anonKey: string,
  bodyPayload: Record<string, string>,
): Promise<SupabaseAuthResult> {
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      apikey: anonKey,
      Authorization: `Bearer ${anonKey}`,
    },
    body: JSON.stringify(bodyPayload),
  });
  const body = (await response.json().catch(() => ({}))) as SupabaseTokenResponse;
  if (!response.ok) {
    const detail = body.error_description ?? body.msg ?? body.error ?? body.error_code ?? body.code;
    throw new Error(detail ?? `Supabase auth failed: ${response.status}`);
  }
  if (!body.access_token || !body.refresh_token) {
    throw new Error('Check your email to confirm your account before signing in.');
  }
  return {
    accessToken: body.access_token,
    refreshToken: body.refresh_token,
    expiresAt: body.expires_at ?? Math.floor(Date.now() / 1000) + (body.expires_in ?? 3600),
    userId: body.user?.id ?? null,
  };
}

function trimTrailingSlash(value: string): string {
  return value.replace(/\/+$/, '');
}

function validateSupabaseAuthConfig(args: SupabaseEmailPasswordArgs): void {
  if (!args.supabaseUrl.trim()) {
    throw new Error('Supabase URL is not configured');
  }
  if (!args.anonKey.trim() || args.anonKey.trim() === '<anon key>') {
    throw new Error('Supabase anon key is not configured');
  }
}
