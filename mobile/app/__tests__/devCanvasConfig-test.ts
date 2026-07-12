import { resolveDevCanvasConfig } from '../devCanvasConfig';

describe('resolveDevCanvasConfig', () => {
  it('does not require variables when development Canvas mode is disabled', () => {
    expect(resolveDevCanvasConfig(false, {})).toEqual({ enabled: false });
  });

  it('reports missing variables when development Canvas mode is enabled', () => {
    expect(resolveDevCanvasConfig(true, {})).toEqual({
      enabled: true,
      error:
        'Development Canvas configuration is missing: ' +
        'EXPO_PUBLIC_DEV_API_BASE_URL, EXPO_PUBLIC_DEV_SESSION_ID, ' +
        'EXPO_PUBLIC_DEV_AUTH_TOKEN',
    });
  });

  it('returns the environment-backed development configuration', () => {
    expect(
      resolveDevCanvasConfig(true, {
        EXPO_PUBLIC_DEV_API_BASE_URL: ' http://dev.invalid ',
        EXPO_PUBLIC_DEV_SESSION_ID: ' session-id ',
        EXPO_PUBLIC_DEV_AUTH_TOKEN: ' token-value ',
      }),
    ).toEqual({
      enabled: true,
      config: {
        apiBaseUrl: 'http://dev.invalid',
        sessionId: 'session-id',
        authorizationToken: 'token-value',
      },
    });
  });
});
