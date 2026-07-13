import { computeLayout } from '../layout';
import { useMindMapStore } from '../store';

describe('canonical canvas position store', () => {
  beforeEach(() => useMindMapStore.getState().resetPositionSession());

  it('scopes positions to a session and clears them on session switch', () => {
    const store = useMindMapStore.getState();
    store.beginPositionSession('session-1');
    store.hydrateNodePosition('node-1', { x: 1, y: 2 }, false);
    expect(useMindMapStore.getState().positionAuthorityByNode['node-1'].position).toEqual({ x: 1, y: 2 });

    useMindMapStore.getState().beginPositionSession('session-2');
    expect(useMindMapStore.getState().positionAuthorityByNode).toEqual({});
  });

  it('does not let later hydration overwrite a manual committed position', () => {
    const store = useMindMapStore.getState();
    store.beginPositionSession('session-1');
    store.hydrateNodePosition('node-1', { x: 0, y: 0 }, false);
    store.commitNodePosition('node-1', { x: 20, y: 30 });
    useMindMapStore.getState().hydrateNodePosition('node-1', { x: -1, y: -1 }, false);

    expect(useMindMapStore.getState().positionAuthorityByNode['node-1']).toEqual({
      position: { x: 20, y: 30 }, positionOverridden: true,
    });
  });

  it('rejects invalid commits and removes deleted nodes', () => {
    const store = useMindMapStore.getState();
    store.beginPositionSession('session-1');
    expect(() => store.commitNodePosition('node-1', { x: Infinity, y: 1 })).toThrow(/finite/i);
    store.commitNodePosition('node-1', { x: 2, y: 3 });
    useMindMapStore.getState().removeNodePositions(['node-1']);
    expect(useMindMapStore.getState().positionAuthorityByNode).toEqual({});
  });

  it('preserves a manual override when layout runs after a structural change', () => {
    const store = useMindMapStore.getState();
    store.beginPositionSession('session-1');
    store.commitNodePosition('child', { x: 77, y: 88 });
    const authority = useMindMapStore.getState().positionAuthorityByNode;

    const result = computeLayout({
      root: { node_id: 'root', parent_node_id: null },
      child: { node_id: 'child', parent_node_id: 'root', ...authority.child },
      sibling: { node_id: 'sibling', parent_node_id: 'root' },
    });

    expect(result.child).toEqual({ x: 77, y: 88 });
  });
});
