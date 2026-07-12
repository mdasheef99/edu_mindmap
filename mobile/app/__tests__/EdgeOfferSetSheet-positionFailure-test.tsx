import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react-native';

import { EdgeOfferSetSheet } from '../../canvas/EdgeOfferSetSheet';

const originalFetch = globalThis.fetch;
const offerSet = { offer_set_id: 'offer-1', session_id: 'session-1', source_node_id: 'source-1',
  launch_method: 'edge', options: [{ option_id: 'option-1', text: 'Why?', rank_position: 1 }] };
const branch = { child_node_id: 'child-1', edge_id: 'edge-1' };
const response = (ok: boolean, body: unknown, status = ok ? 200 : 503) =>
  ({ ok, status, json: async () => body });

describe('EdgeOfferSetSheet placement recovery', () => {
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
    globalThis.fetch = jest.fn()
      .mockResolvedValueOnce(response(true, branch))
      .mockResolvedValueOnce(response(false, {}))
      .mockResolvedValueOnce(response(true, { node_id: 'child-1', position_x: 350, position_y: 100 }));
    const { onBranchCreated } = await setup();
    await fireEvent.press(screen.getByText('Why?'));

    expect(await screen.findByText('Branch created')).toBeTruthy();
    expect(screen.getByText('Placement was not saved')).toBeTruthy();
    await fireEvent.press(screen.getByText('Retry placement'));
    await waitFor(() => expect(onBranchCreated).toHaveBeenCalledTimes(1));

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
