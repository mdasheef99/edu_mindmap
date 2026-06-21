/**
 * Mobile Sentry init (M3 SDD §3, §14).
 *
 * Mirrors the backend invariant (tests/integration/test_observability_sentry.py):
 * Sentry is optional — initialize only when a DSN is supplied, otherwise no-op.
 * The mobile DSN is sourced from SENTRY_DSN_MOBILE (configuration-reference.md §10),
 * resolved at the App.tsx call site and passed in, keeping this module pure/testable.
 *
 * Traceability: phase-3-m3-canvas-sdd.md §3, §14.
 */

jest.mock('@sentry/react-native', () => ({ init: jest.fn() }));

import * as Sentry from '@sentry/react-native';

import { initSentry } from '../observability/sentry';

describe('Mobile Sentry init (M3 SDD §3, §14)', () => {
  beforeEach(() => {
    (Sentry.init as jest.Mock).mockClear();
  });

  it('test_init_sentry_calls_init_with_dsn', () => {
    const result = initSentry('https://examplePublicKey@o0.ingest.sentry.io/0');

    expect(result).toBe(true);
    expect(Sentry.init).toHaveBeenCalledTimes(1);
    expect(Sentry.init).toHaveBeenCalledWith(
      expect.objectContaining({ dsn: 'https://examplePublicKey@o0.ingest.sentry.io/0' }),
    );
  });

  it('test_init_sentry_is_noop_without_dsn', () => {
    const result = initSentry(undefined);

    expect(result).toBe(false);
    expect(Sentry.init).not.toHaveBeenCalled();
  });
});
