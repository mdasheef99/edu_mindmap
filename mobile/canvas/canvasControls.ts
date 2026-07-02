import type { CanvasTransform, Point } from './coordinateSystem';
import { canvasToBoard } from './coordinateSystem';
import type { ScreenSize } from './viewportCulling';
import type { CanvasNode } from './SkiaCanvas';
import { CHIP_H, CHIP_W } from './chipConstants';
import { clampScale } from './gestureTransform';

export const CANVAS_GRID_SIZE_PX = 15;
export const CANVAS_ZOOM_STEP = 1.25;
export const FIT_SCREEN_PADDING_PX = 24;

export function resetCanvasTransform(): CanvasTransform {
  return { scale: 1, translateX: 0, translateY: 0 };
}

export function formatZoomPercent(scale: number): string {
  return `${Math.round(scale * 100)}%`;
}

export function zoomTransform(
  current: CanvasTransform,
  screen: ScreenSize,
  direction: 'in' | 'out',
): CanvasTransform {
  const center = { x: screen.width / 2, y: screen.height / 2 };
  const boardCenter = canvasToBoard(center.x, center.y, current);
  const factor = direction === 'in' ? CANVAS_ZOOM_STEP : 1 / CANVAS_ZOOM_STEP;
  const scale = clampScale(current.scale * factor);
  return {
    scale,
    translateX: center.x - boardCenter.x * scale,
    translateY: center.y - boardCenter.y * scale,
  };
}

export function fitTransformToNodes(nodes: CanvasNode[], screen: ScreenSize): CanvasTransform {
  if (nodes.length === 0) {
    return resetCanvasTransform();
  }

  const halfW = CHIP_W / 2;
  const halfH = CHIP_H / 2;
  const minX = Math.min(...nodes.map((node) => node.position.x - halfW));
  const maxX = Math.max(...nodes.map((node) => node.position.x + halfW));
  const minY = Math.min(...nodes.map((node) => node.position.y - halfH));
  const maxY = Math.max(...nodes.map((node) => node.position.y + halfH));
  const boardW = Math.max(maxX - minX, 1);
  const boardH = Math.max(maxY - minY, 1);
  const availableW = Math.max(screen.width - FIT_SCREEN_PADDING_PX * 2, 1);
  const availableH = Math.max(screen.height - FIT_SCREEN_PADDING_PX * 2, 1);
  const scale = clampScale(Math.min(availableW / boardW, availableH / boardH));
  const boardCenterX = minX + boardW / 2;
  const boardCenterY = minY + boardH / 2;

  return {
    scale,
    translateX: screen.width / 2 - boardCenterX * scale,
    translateY: screen.height / 2 - boardCenterY * scale,
  };
}

export function snapPointToGrid(point: Point, gridSize = CANVAS_GRID_SIZE_PX): Point {
  return {
    x: Math.round(point.x / gridSize) * gridSize,
    y: Math.round(point.y / gridSize) * gridSize,
  };
}
