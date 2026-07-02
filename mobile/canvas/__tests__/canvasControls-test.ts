import {
  CANVAS_GRID_SIZE_PX,
  fitTransformToNodes,
  formatZoomPercent,
  resetCanvasTransform,
  snapPointToGrid,
  zoomTransform,
} from '../canvasControls';
import { CANVAS_MAX_ZOOM, CANVAS_MIN_ZOOM } from '../gestureTransform';

const SCREEN = { width: 400, height: 300 };
const IDENTITY = { scale: 1, translateX: 0, translateY: 0 };

describe('M3.6 canvas control math', () => {
  it('zooms around the screen center and clamps to configured bounds', () => {
    expect(zoomTransform({ ...IDENTITY, scale: 3.9 }, SCREEN, 'in').scale).toBe(CANVAS_MAX_ZOOM);
    expect(zoomTransform({ ...IDENTITY, scale: 0.3 }, SCREEN, 'out').scale).toBe(CANVAS_MIN_ZOOM);

    const zoomed = zoomTransform(IDENTITY, SCREEN, 'in');
    expect(zoomed.scale).toBe(1.25);
    expect(zoomed.translateX).toBeCloseTo(-50);
    expect(zoomed.translateY).toBeCloseTo(-37.5);
  });

  it('fits all nodes into the screen without mutating node positions', () => {
    const nodes = [
      { node_id: 'n1', parent_node_id: null, position: { x: 0, y: 0 } },
      { node_id: 'n2', parent_node_id: 'n1', position: { x: 600, y: 300 } },
    ];

    const fitted = fitTransformToNodes(nodes, SCREEN);

    expect(fitted.scale).toBeLessThan(1);
    expect(fitted.translateX).toBeGreaterThan(0);
    expect(nodes[0].position).toEqual({ x: 0, y: 0 });
    expect(nodes[1].position).toEqual({ x: 600, y: 300 });
  });

  it('resets to the default canvas transform', () => {
    expect(resetCanvasTransform()).toEqual(IDENTITY);
  });

  it('formats the current zoom scale as a percentage', () => {
    expect(formatZoomPercent(1)).toBe('100%');
    expect(formatZoomPercent(1.25)).toBe('125%');
    expect(formatZoomPercent(0.255)).toBe('26%');
  });

  it('snaps a point to the fixed MVP grid size', () => {
    expect(CANVAS_GRID_SIZE_PX).toBe(15);
    expect(snapPointToGrid({ x: 22, y: 37 })).toEqual({ x: 15, y: 30 });
    expect(snapPointToGrid({ x: 23, y: 38 })).toEqual({ x: 30, y: 45 });
  });
});
