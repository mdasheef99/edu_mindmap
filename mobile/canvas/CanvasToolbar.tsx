import React from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import type { CanvasTransform } from './coordinateSystem';
import type { ScreenSize } from './viewportCulling';
import type { CanvasNode } from './SkiaCanvas';
import {
  fitTransformToNodes,
  formatZoomPercent,
  resetCanvasTransform,
  zoomTransform,
} from './canvasControls';

interface CanvasToolbarProps {
  transform: CanvasTransform;
  screen: ScreenSize;
  nodes: CanvasNode[];
  snapToGrid: boolean;
  onCommitTransform: (next: CanvasTransform) => void;
  onToggleSnapToGrid: () => void;
}

export function CanvasToolbar({
  transform,
  screen,
  nodes,
  snapToGrid,
  onCommitTransform,
  onToggleSnapToGrid,
}: CanvasToolbarProps) {
  return (
    <View style={styles.canvasToolbar}>
      <Pressable
        testID="canvas-zoom-out"
        accessibilityRole="button"
        accessibilityLabel="Zoom out"
        style={styles.toolbarButton}
        onPress={() => onCommitTransform(zoomTransform(transform, screen, 'out'))}
      >
        <Text style={styles.toolbarButtonText}>−</Text>
      </Pressable>
      <Text style={styles.zoomReadout}>{formatZoomPercent(transform.scale)}</Text>
      <Pressable
        testID="canvas-zoom-in"
        accessibilityRole="button"
        accessibilityLabel="Zoom in"
        style={styles.toolbarButton}
        onPress={() => onCommitTransform(zoomTransform(transform, screen, 'in'))}
      >
        <Text style={styles.toolbarButtonText}>+</Text>
      </Pressable>
      <Pressable
        testID="canvas-fit-screen"
        accessibilityRole="button"
        accessibilityLabel="Fit to screen"
        style={styles.toolbarButton}
        onPress={() => onCommitTransform(fitTransformToNodes(nodes, screen))}
      >
        <Text style={styles.toolbarButtonText}>Fit</Text>
      </Pressable>
      <Pressable
        testID="canvas-reset-view"
        accessibilityRole="button"
        accessibilityLabel="Reset view"
        style={styles.toolbarButton}
        onPress={() => onCommitTransform(resetCanvasTransform())}
      >
        <Text style={styles.toolbarButtonText}>Reset</Text>
      </Pressable>
      <Pressable
        testID="canvas-snap-grid-toggle"
        accessibilityRole="button"
        accessibilityLabel="Snap to grid"
        accessibilityState={{ selected: snapToGrid }}
        style={[styles.toolbarButton, snapToGrid ? styles.toolbarButtonActive : null]}
        onPress={onToggleSnapToGrid}
      >
        <Text style={styles.toolbarButtonText}>Grid</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  canvasToolbar: {
    position: 'absolute',
    left: 12,
    right: 12,
    bottom: 12,
    minHeight: 44,
    padding: 6,
    borderRadius: 8,
    backgroundColor: 'rgba(17, 24, 39, 0.9)',
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  toolbarButton: {
    minWidth: 36,
    height: 32,
    borderRadius: 6,
    backgroundColor: '#374151',
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 8,
  },
  toolbarButtonActive: { backgroundColor: '#2563eb' },
  toolbarButtonText: { color: '#ffffff', fontSize: 13, fontWeight: '700' },
  zoomReadout: {
    minWidth: 44,
    color: '#ffffff',
    fontSize: 13,
    fontWeight: '700',
    textAlign: 'center',
  },
});
