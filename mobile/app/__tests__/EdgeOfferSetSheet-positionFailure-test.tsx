import React from 'react';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react-native';

import { EdgeOfferSetSheet } from '../../canvas/EdgeOfferSetSheet';

const originalFetch = globalThis.fetch;

const offerSet = {
  offer_set_id: 'offer-set-1',
  session_id: 'session-1',
  source_node_id: 'source-node-1',
  launch_method: 'edge',
  options: [
    { option_id: 'option-1', text: 'Why does resistance increase?', rank_position: 1 },
  ],
};

const createdBranch = {
  offer_set_id: 'offer-set-1',
  outcome: 'selected',
  recorded: true,
  child_node_id: 'child-node-1',
  edge_id: 'edge-1',
};

const positionAcknowledgement = {
  node_id: 'child-node-1',
  position_x: 350,
  position_y: 100,
};

function response(ok: boolean, body: unknown, status = ok ? 200 : 503) {
  return { ok, status, json: async () => body };
}

function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason?: unknown) => void;
  const promise = new Promise<T>((resolvePromise, rejectPromise) => {
    resolve = resolvePromise;
    reject = rejectPromise;
  });
  return { promise, resolve, reject };
}

async function renderSheet(overrides: Partial<React.ComponentProps<typeof EdgeOfferSetSheet>> = {}) {
  const onClose = jest.fn();
  const onBranchCreated = jest.fn();
  const props: React.ComponentProps<typeof EdgeOfferSetSheet> = {
    visible: true,
    offerSet,
    threadContextId: 'thread-1',
    sourcePosition: { x: 10, y: 20 },
    apiBaseUrl: 'http://localhost:8000',
    authorizationToken: 'token-1',
    onClose,
    onBranchCreated,
    ...overrides,
  };
  return { ...(await render(<EdgeOfferSetSheet {...props} />)), props, onClose, onBranchCreated };
}

async function press(text: string) {
  await fireEvent.press(screen.getByText(text));
}

async function pressChoice() {
  await press('Why does resistance increase?');
}

function fetchCalls(method: string) {
  return (globalThis.fetch as jest.Mock).mock.calls.filter(
    ([, init]) => init?.method === method,
  );
}

describe('EdgeOfferSetSheet child-position recovery', () => {
  afterEach(() => {
    jest.restoreAllMocks();
    globalThis.fetch = originalFetch;
  });

  it('completes once after creation and checked child-position success', async () => {
    globalThis.fetch = jest
      .fn()
      .mockResolvedValueOnce(response(true, createdBranch))
      .mockResolvedValueOnce(response(true, positionAcknowledgement));
    const { onBranchCreated } = await renderSheet();

    await pressChoice();

    await waitFor(() => expect(onBranchCreated).toHaveBeenCalledTimes(1));
    expect(fetchCalls('POST')).toHaveLength(1);
    expect(fetchCalls('PATCH')).toHaveLength(1);
    expect(onBranchCreated).toHaveBeenCalledWith();
  });

  it.each([
    ['non-2xx', () => Promise.resolve(response(false, {}))],
    ['network rejection', () => Promise.reject(new Error('offline'))],
  ])('retains the durable branch when placement has a %s failure', async (_label, fail) => {
    globalThis.fetch = jest
      .fn()
      .mockResolvedValueOnce(response(true, createdBranch))
      .mockImplementationOnce(fail);
    const { onBranchCreated } = await renderSheet();

    await pressChoice();

    expect(await screen.findByText('Branch created')).toBeTruthy();
    expect(screen.getByText('Placement was not saved')).toBeTruthy();
    expect(screen.getByText('Retry placement')).toBeTruthy();
    expect(screen.getByText('Close and reload')).toBeTruthy();
    expect(fetchCalls('POST')).toHaveLength(1);
    expect(fetchCalls('PATCH')).toHaveLength(1);
    expect(onBranchCreated).not.toHaveBeenCalled();
  });

  it('retries only the existing child PATCH and completes once after retry success', async () => {
    globalThis.fetch = jest
      .fn()
      .mockResolvedValueOnce(response(true, createdBranch))
      .mockResolvedValueOnce(response(false, {}))
      .mockResolvedValueOnce(response(true, positionAcknowledgement));
    const { onBranchCreated } = await renderSheet();
    await pressChoice();
    await screen.findByText('Retry placement');

    await press('Retry placement');

    await waitFor(() => expect(onBranchCreated).toHaveBeenCalledTimes(1));
    expect(fetchCalls('POST')).toHaveLength(1);
    expect(fetchCalls('PATCH')).toHaveLength(2);
  });

  it('guards duplicate Retry presses while a placement request is active', async () => {
    const retry = deferred<ReturnType<typeof response>>();
    globalThis.fetch = jest
      .fn()
      .mockResolvedValueOnce(response(true, createdBranch))
      .mockResolvedValueOnce(response(false, {}))
      .mockImplementationOnce(() => retry.promise);
    const { onBranchCreated } = await renderSheet();
    await pressChoice();
    await screen.findByText('Retry placement');

    const retryButton = screen.getByText('Retry placement');
    await fireEvent.press(retryButton);
    await fireEvent.press(retryButton);

    expect(fetchCalls('PATCH')).toHaveLength(2);
    expect(screen.queryByText('Retry placement')).toBeNull();
    await act(async () => {
      retry.resolve(response(true, positionAcknowledgement));
      await retry.promise;
    });
    await waitFor(() => expect(onBranchCreated).toHaveBeenCalledTimes(1));
  });

  it('keeps a failed retry recoverable', async () => {
    globalThis.fetch = jest
      .fn()
      .mockResolvedValueOnce(response(true, createdBranch))
      .mockResolvedValueOnce(response(false, {}))
      .mockResolvedValueOnce(response(false, {}));
    const { onBranchCreated } = await renderSheet();
    await pressChoice();
    await screen.findByText('Retry placement');

    await press('Retry placement');

    await waitFor(() => expect(fetchCalls('PATCH')).toHaveLength(2));
    expect(await screen.findByText('Placement was not saved')).toBeTruthy();
    expect(screen.getByText('Retry placement')).toBeTruthy();
    expect(onBranchCreated).not.toHaveBeenCalled();
  });

  it('closes through canonical reload once without another placement attempt', async () => {
    globalThis.fetch = jest
      .fn()
      .mockResolvedValueOnce(response(true, createdBranch))
      .mockResolvedValueOnce(response(false, {}));
    const { onBranchCreated, onClose } = await renderSheet();
    await pressChoice();
    await screen.findByText('Close and reload');

    await fireEvent.press(screen.getByText('Close and reload'));
    await fireEvent.press(screen.getByText('Close and reload'));

    expect(onBranchCreated).toHaveBeenCalledTimes(1);
    expect(onClose).not.toHaveBeenCalled();
    expect(fetchCalls('PATCH')).toHaveLength(1);
  });

  it('ignores a late placement success after Close and reload', async () => {
    const placement = deferred<ReturnType<typeof response>>();
    globalThis.fetch = jest
      .fn()
      .mockResolvedValueOnce(response(true, createdBranch))
      .mockImplementationOnce(() => placement.promise);
    const { onBranchCreated } = await renderSheet();
    await pressChoice();
    await screen.findByText('Close and reload');

    await press('Close and reload');
    await act(async () => {
      placement.resolve(response(true, positionAcknowledgement));
      await placement.promise;
    });

    await waitFor(() => expect(onBranchCreated).toHaveBeenCalledTimes(1));
  });

  it('absorbs a late placement failure after unmount', async () => {
    const placement = deferred<ReturnType<typeof response>>();
    globalThis.fetch = jest
      .fn()
      .mockResolvedValueOnce(response(true, createdBranch))
      .mockImplementationOnce(() => placement.promise);
    const { unmount, onBranchCreated } = await renderSheet();
    await pressChoice();
    await waitFor(() => expect(fetchCalls('PATCH')).toHaveLength(1));

    await unmount();
    await act(async () => {
      placement.reject(new Error('late offline'));
      await placement.promise.catch(() => undefined);
    });
    expect(onBranchCreated).not.toHaveBeenCalled();
  });

  it('uses refreshed authorization for retry', async () => {
    globalThis.fetch = jest
      .fn()
      .mockResolvedValueOnce(response(true, createdBranch))
      .mockResolvedValueOnce(response(false, {}))
      .mockResolvedValueOnce(response(true, positionAcknowledgement));
    const rendered = await renderSheet();
    await pressChoice();
    await screen.findByText('Retry placement');

    await rendered.rerender(
      <EdgeOfferSetSheet {...rendered.props} authorizationToken="token-2" />,
    );
    await press('Retry placement');

    await waitFor(() => expect(rendered.onBranchCreated).toHaveBeenCalledTimes(1));
    expect(fetchCalls('PATCH')[1][1].headers.Authorization).toBe('Bearer token-2');
  });

  it('prevents repeated choice submission and dismissal while creation is pending', async () => {
    const creation = deferred<ReturnType<typeof response>>();
    globalThis.fetch = jest.fn(() => creation.promise) as unknown as typeof fetch;
    const { onClose } = await renderSheet();

    await fireEvent.press(screen.getByText('Why does resistance increase?'));
    await fireEvent.press(screen.getByText('Why does resistance increase?'));
    await fireEvent.press(screen.getByText('Close'));

    expect(fetchCalls('POST')).toHaveLength(1);
    expect(onClose).not.toHaveBeenCalled();
    await act(async () => {
      creation.resolve(response(false, {}));
      await creation.promise;
    });
    await screen.findByText(/failed/i);
  });

  it('offers reload without unsafe placement retry when the child identity is missing', async () => {
    globalThis.fetch = jest
      .fn()
      .mockResolvedValueOnce(response(true, { ...createdBranch, child_node_id: undefined }));
    const { onBranchCreated } = await renderSheet();

    await pressChoice();

    expect(await screen.findByText('Branch created')).toBeTruthy();
    expect(screen.getByText('Placement was not saved')).toBeTruthy();
    expect(screen.queryByText('Retry placement')).toBeNull();
    expect(screen.getByText('Close and reload')).toBeTruthy();
    expect(fetchCalls('PATCH')).toHaveLength(0);
    expect(onBranchCreated).not.toHaveBeenCalled();
  });
});
