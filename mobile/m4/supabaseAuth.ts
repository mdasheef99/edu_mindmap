export interface SupabaseEmailPasswordArgs {
  supabaseUrl: string;
  anonKey: string;
  email: string;
  password: string;
}

export interface SupabaseAuthResult {
  accessToken: string;
  userId: string | null;
}

interface SupabaseTokenResponse {
  access_token?: string;
  user?: { id?: string };
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

async function requestSupabaseAuth(
  url: string,
  args: SupabaseEmailPasswordArgs,
): Promise<SupabaseAuthResult> {
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      apikey: args.anonKey,
      Authorization: `Bearer ${args.anonKey}`,
    },
    body: JSON.stringify({ email: args.email, password: args.password }),
  });
  const body = (await response.json().catch(() => ({}))) as SupabaseTokenResponse;
  if (!response.ok) {
    throw new Error(body.error_description ?? body.msg ?? `Supabase auth failed: ${response.status}`);
  }
  if (!body.access_token) {
    throw new Error('Check your email to confirm your account before signing in.');
  }
  return {
    accessToken: body.access_token,
    userId: body.user?.id ?? null,
  };
}

function trimTrailingSlash(value: string): string {
  return value.replace(/\/+$/, '');
}
