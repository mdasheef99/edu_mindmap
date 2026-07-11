/**
 * Mobile Sentry wiring (M3 SDD §3, §14).
 *
 * Mirrors the backend pattern (backend/app/observability/sentry.py): Sentry is
 * optional and initialized only when a DSN is supplied, otherwise this is a no-op.
 * The DSN is EXPO_PUBLIC_SENTRY_DSN_MOBILE (configuration-reference.md §10), resolved at the
 * App.tsx call site and passed in so this module stays pure and CI-testable.
 *
 * Traceability: phase-3-m3-canvas-sdd.md §3, §14.
 */

import * as Sentry from '@sentry/react-native';

/**
 * Initialize Sentry when a mobile DSN is available.
 *
 * @returns true when Sentry.init was called, false when no DSN was supplied.
 */
export function initSentry(dsn?: string): boolean {
  if (!dsn) {
    return false;
  }

  Sentry.init({ dsn });
  return true;
}
