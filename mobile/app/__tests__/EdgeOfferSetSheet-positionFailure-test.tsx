import React from 'react';
import { View } from 'react-native';
import { act, fireEvent, render, screen } from '@testing-library/react-native';

jest.mock('react-native/Libraries/Modal/Modal', () => {
  const ReactModule = require('react');
  return {
    __esModule: true,
    default: ({ children }: { children: React.ReactNode }) => (
      ReactModule.createElement(ReactModule.Fragment, null, children)
    ),
  };
});

jest.mock('react-native/Libraries/Components/Button', () => {
  const ReactModule = require('react');
  return {
    __esModule: true,
    default: ({ title, onPress, disabled }: {
      title: string; onPress: () => void; disabled?: boolean;
    }) => ReactModule.createElement(
      'View',
      { accessibilityRole: 'button', accessibilityState: { disabled }, disabled, onPress },
      ReactModule.createElement('Text', null, title),
    ),
  };
});

jest.mock('react-native/Libraries/Components/ScrollView/ScrollView', () => {
  const ReactModule = require('react');
  return {
    __esModule: true,
    default: ({ children }: { children: React.ReactNode }) => (
      ReactModule.createElement('View', null, children)
    ),
  };
});

import { EdgeOfferSetSheet } from '../../canvas/EdgeOfferSetSheet';

const originalFetch = globalThis.fetch;
const offerSet = { offer_set_id: 'offer-1', session_id: 'session-1', source_node_id: 'source-1',
  launch_method: 'edge', options: [{ option_id: 'option-1', text: 'Why?', rank_position: 1 }] };
const branch = { child_node_id: 'child-1', edge_id: 'edge-1' };
const response = (ok: boolean, body: unknown, status = ok ? 200 : 503) =>
  ({ ok, status, json: async () => body });

function deferred<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((resolvePromise) => { resolve = resolvePromise; });
  return { promise, resolve };
}

async function resolveRequest<T>(request: ReturnType<typeof deferred<T>>, value: T) {
  await act(async () => {
    request.resolve(value);
    await request.promise;
    await Promise.resolve();
    await Promise.resolve();
  });
}

describe('EdgeOfferSetSheet placement recovery', () => {
  beforeAll(async () => {
    await render(<View />);
  });

  afterEach(() => { globalThis.fetch = originalFetch; jest.restoreAllMocks(); });

  async function setup() {
    const onBranchCreated = jest.fn();
    const onClose = jest.fn();
    await render(<EdgeOfferSetSheet
      visible offerSet={offerSet} threadContextId="thread-1" sourcePosition={{ x: 10, y: 20 }}
      apiBaseUrl="http://localhost:8000" authorizationToken="token"
      onClose={onClose} onBranchCreated={onBranchCreated}
    />);
    return { onBranchCreated, onClose };
  }

  it('retains a durable branch and retries only its failed placement PATCH', async () => {
    const creation = deferred<ReturnType<typeof response>>();
    const failedPlacement = deferred<ReturnType<typeof response>>();
    const retryPlacement = deferred<ReturnType<typeof response>>();
    globalThis.fetch = jest.fn()
      .mockReturnValueOnce(creation.promise)
      .mockReturnValueOnce(failedPlacement.promise)
      .mockReturnValueOnce(retryPlacement.promise);
    const { onBranchCreated } = await setup();
    await fireEvent.press(screen.getByText('Why?'));

    expect(globalThis.fetch).toHaveBeenCalledTimes(1);
    await act(async () => {
      creation.resolve(response(true, branch));
      failedPlacement.resolve(response(false, {}));
      await Promise.all([creation.promise, failedPlacement.promise]);
      await Promise.resolve();
      await Promise.resolve();
    });

    expect(globalThis.fetch).toHaveBeenCalledTimes(2);
    expect(screen.getByText('Branch created')).toBeTruthy();
    expect(screen.getByText('Placement was not saved')).toBeTruthy();
    await fireEvent.press(screen.getByText('Retry placement'));
    expect(globalThis.fetch).toHaveBeenCalledTimes(3);
    expect(screen.queryByText('Placement was not saved')).toBeNull();
    await resolveRequest(
      retryPlacement,
      response(true, { node_id: 'child-1', position_x: 350, position_y: 100 }),
    );
    expect(onBranchCreated).toHaveBeenCalledTimes(1);

    const methods = (globalThis.fetch as jest.Mock).mock.calls.map(([, init]) => init.method);
    expect(methods).toEqual(['POST', 'PATCH', 'PATCH']);
  });

  it('closes a placement failure through the canonical reload boundary once', async () => {
    globalThis.fetch = jest.fn()
      .mockResolvedValueOnce(response(true, branch))
      .mockResolvedValueOnce(response(false, {}));
    const { onBranchCreated, onClose } = await setup();
    await fireEvent.press(screen.getByText('Why?'));
    await screen.findByText('Close and reload');
    await fireEvent.press(screen.getByText('Close and reload'));
    await fireEvent.press(screen.getByText('Close and reload'));
    expect(onBranchCreated).toHaveBeenCalledTimes(1);
    expect(onClose).not.toHaveBeenCalled();
  });
});
