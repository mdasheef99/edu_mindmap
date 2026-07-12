export interface DevCanvasConfig {
  apiBaseUrl: string;
  sessionId: string;
  authorizationToken: string;
}

export type DevCanvasConfigResult =
  | { enabled: false }
  | { enabled: true; config: DevCanvasConfig }
  | { enabled: true; error: string };

type DevCanvasEnvironment = {
  EXPO_PUBLIC_DEV_API_BASE_URL?: string;
  EXPO_PUBLIC_DEV_SESSION_ID?: string;
  EXPO_PUBLIC_DEV_AUTH_TOKEN?: string;
};

const REQUIRED_VARIABLES = [
  'EXPO_PUBLIC_DEV_API_BASE_URL',
  'EXPO_PUBLIC_DEV_SESSION_ID',
  'EXPO_PUBLIC_DEV_AUTH_TOKEN',
] as const;

export function resolveDevCanvasConfig(
  enabled: boolean,
  environment: DevCanvasEnvironment,
): DevCanvasConfigResult {
  if (!enabled) return { enabled: false };

  const missing = REQUIRED_VARIABLES.filter((name) => !environment[name]?.trim());
  if (missing.length > 0) {
    return {
      enabled: true,
      error: `Development Canvas configuration is missing: ${missing.join(', ')}`,
    };
  }

  return {
    enabled: true,
    config: {
      apiBaseUrl: environment.EXPO_PUBLIC_DEV_API_BASE_URL!.trim(),
      sessionId: environment.EXPO_PUBLIC_DEV_SESSION_ID!.trim(),
      authorizationToken: environment.EXPO_PUBLIC_DEV_AUTH_TOKEN!.trim(),
    },
  };
}
