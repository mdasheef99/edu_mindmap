/**
 * SkiaCanvas — thin hybrid-canvas orchestrator (M3/M3-B/M3-C).
 * Domain logic lives in dedicated hooks; the dual-state rule (M3 SDD §5/§7) is preserved.
 * Traceability: phase-3-m3-canvas-sdd.md §4, §5, §7, §8, §9, §15;
 * phase-3-m3b-canvas-feature-parity-sdd.md §5.1–§5.6;
 * phase-3-m3c-infrastructure-remediation-sdd.md §6, §7; adr-log-02.md ADR-0013.
 */

import React, { useCallback, useMemo, useRef, useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { GestureDetector, GestureHandlerRootView } from 'react-native-gesture-handler';
import { CanvasTransform, Point } from './coordinateSystem';
import { ScreenSize } from './viewportCulling';
import { useMindMapStore } from './store';
import { EdgePlusButtons } from './EdgePlusButtons';
import { NodeToolbar } from './NodeToolbar';
import { NodeLimitBanner } from './NodeLimitBanner';
import { nodeLimitState } from './nodeLimits';
import { NodeChip } from './NodeChip';
import { CanvasEdges } from './CanvasEdges';
import { useCanvasGestures } from './useCanvasGestures';
import { CHIP_W, CHIP_H } from './chipConstants';
import { postClientEvent, throttledPostViewport } from './apiClient';
import { EdgeOfferSetSheet } from './EdgeOfferSetSheet';
import type { EdgeOfferSet } from './EdgeOfferSetSheet';
import { useDeletionReconciliation } from './useDeletionReconciliation';
import { useDiscoveryManager } from './useDiscoveryManager';
import { useCanvasRenderData } from './useCanvasRenderData';
import { snapPointToGrid } from './canvasControls';
import { CanvasToolbar } from './CanvasToolbar';
import { useNodePositionWrites } from './useNodePositionWrites';

// ── public types ──────────────────────────────────────────────────────────────

export interface CanvasNode {
  node_id: string;
  parent_node_id: string | null;
  position: Point;
  title?: string;
  content?: string;
  thread_context_id?: string;
}

export interface CanvasEdge {
  edge_id: string;
  source_node_id: string;
  target_node_id: string;
  edge_kind: string;
  label?: string;
}

export interface SkiaCanvasProps {
  nodes: CanvasNode[];
  edges: CanvasEdge[];
  screen: ScreenSize;
  transform: CanvasTransform;
  onTransformEnd?: (t: CanvasTransform) => void;
  apiBaseUrl?: string;
  authorizationToken?: string;
  sessionId?: string;
  onReloadCanvas?: () => void;
}

// ── SkiaCanvas ─────────────────────────────────────────────────────────────────

export default function SkiaCanvas({
  nodes, edges, screen, transform, onTransformEnd,
  apiBaseUrl, authorizationToken, sessionId, onReloadCanvas,
}: SkiaCanvasProps) {
  const { selectedNodeId, selectNode, clearSelection } = useMindMapStore();
  const {
    activeOfferSet, discoveryError, beginDiscovery, handleOfferSet, handleOfferError,
    handleBranchCreated, closeOfferSet,
  } = useDiscoveryManager(onReloadCanvas);

  const [snapToGrid, setSnapToGrid] = useState(false);
  const positionWrites = useNodePositionWrites({
    nodes,
    apiBaseUrl,
    authorizationToken,
    sessionId,
  });
  const committedNodes = useMemo(
    () => nodes.map((n) => ({
      ...n,
      position: positionWrites.visiblePositions[n.node_id] ?? n.position,
    })),
    [nodes, positionWrites.visiblePositions],
  );
  const { liveNodes, liveEdges, handleDeleted } = useDeletionReconciliation(committedNodes, edges, clearSelection);

  const liveNodesRef = useRef(liveNodes);
  liveNodesRef.current = liveNodes;

  const emitEnabled = Boolean(apiBaseUrl && sessionId);
  const visIdsRef = useRef<Set<string>>(new Set());

  const handleSelectNode = useCallback(
    (nodeId: string) => {
      selectNode(nodeId);
      if (emitEnabled) {
        postClientEvent(apiBaseUrl!, sessionId!, authorizationToken, {
          event_type: 'node_visited', event_version: 1, session_id: sessionId!, node_id: nodeId,
          payload: { node_id: nodeId, session_id: sessionId!, visit_source: 'tap' },
        });
      }
    },
    [selectNode, emitEnabled, apiBaseUrl, sessionId, authorizationToken],
  );

  const handleTransformEnd = useCallback(
    (t: CanvasTransform) => {
      onTransformEnd?.(t);
      if (emitEnabled) {
        throttledPostViewport(apiBaseUrl!, sessionId!, authorizationToken, {
          event_type: 'viewport_changed', event_version: 1, session_id: sessionId!,
          payload: {
            session_id: sessionId!, scale: t.scale, translate_x: t.translateX, translate_y: t.translateY,
            visible_node_ids: Array.from(visIdsRef.current),
          },
        });
      }
    },
    [onTransformEnd, emitEnabled, apiBaseUrl, sessionId, authorizationToken],
  );

  const handleNodeDragEnd = useCallback(
    (nodeId: string, x: number, y: number) => {
      const position = snapToGrid ? snapPointToGrid({ x, y }) : { x, y };
      positionWrites.enqueuePosition(nodeId, position);
    },
    [snapToGrid, positionWrites.enqueuePosition],
  );

  const gestures = useCanvasGestures({
    nodes: liveNodes,
    nodesRef: liveNodesRef,
    transform,
    nodeSize: [CHIP_W, CHIP_H],
    onTransformEnd: handleTransformEnd,
    onNodeDragEnd: handleNodeDragEnd,
    onSelectNode: handleSelectNode,
    onClearSelection: clearSelection,
  });

  const nodeIndexById = useMemo(
    () => Object.fromEntries(liveNodes.map((node, idx) => [node.node_id, idx])),
    [liveNodes],
  );
  const { nodePositions, visIds, visibleEdges } = useCanvasRenderData(
    liveNodes, liveEdges, transform, screen,
  );
  visIdsRef.current = visIds;

  const limitState = nodeLimitState(liveNodes.length);
  const selectedNode =
    selectedNodeId != null && visIds.has(selectedNodeId)
      ? (liveNodes.find((n) => n.node_id === selectedNodeId) ?? null)
      : null;

  const discoveryEnabled = Boolean(apiBaseUrl && sessionId);
  const commitToolbarTransform = useCallback(
    (next: CanvasTransform) => {
      gestures.scaleShared.value = next.scale;
      gestures.translateXShared.value = next.translateX;
      gestures.translateYShared.value = next.translateY;
      handleTransformEnd(next);
    },
    [gestures.scaleShared, gestures.translateXShared, gestures.translateYShared, handleTransformEnd],
  );

  return (
    <GestureHandlerRootView style={styles.root}>
      <GestureDetector gesture={gestures.composed}>
        <View style={StyleSheet.absoluteFill}>
          <CanvasEdges
            nodePositions={nodePositions}
            nodeIndexById={nodeIndexById}
            edges={liveEdges}
            visibleEdges={visibleEdges}
            visIds={visIds}
            groupTransform={gestures.groupTransform}
            dragNodeIdxShared={gestures.dragNodeIdx}
            dragCurrBXShared={gestures.dragCurrBX}
            dragCurrBYShared={gestures.dragCurrBY}
          />

          {liveNodes
            .map((node, idx) => ({ node, idx }))
            .filter(({ node }) => visIds.has(node.node_id))
            .map(({ node, idx }) => (
              <NodeChip
                key={node.node_id}
                node={node}
                nodeIdx={idx}
                scaleShared={gestures.scaleShared}
                translateXShared={gestures.translateXShared}
                translateYShared={gestures.translateYShared}
                dragNodeIdxShared={gestures.dragNodeIdx}
                dragCurrBXShared={gestures.dragCurrBX}
                dragCurrBYShared={gestures.dragCurrBY}
              />
            ))}
          {discoveryEnabled &&
            liveNodes
              .map((node, idx) => ({ node, idx }))
              .filter(({ node }) => visIds.has(node.node_id))
              .map(({ node, idx }) => (
                <EdgePlusButtons
                  key={`epb-${node.node_id}`}
                  node={node}
                  nodeIdx={idx}
                  scaleShared={gestures.scaleShared}
                  translateXShared={gestures.translateXShared}
                  translateYShared={gestures.translateYShared}
                  dragNodeIdxShared={gestures.dragNodeIdx}
                  dragCurrBXShared={gestures.dragCurrBX}
                  dragCurrBYShared={gestures.dragCurrBY}
                  nodeSize={[CHIP_W, CHIP_H]}
                  apiBaseUrl={apiBaseUrl!}
                  authorizationToken={authorizationToken}
                  sessionId={sessionId!}
                  threadContextId={node.thread_context_id ?? ''}
                  disabled={limitState.creationBlocked}
                  onRequestStart={beginDiscovery}
                  onOfferSet={(offerSet, generation) => (
                    handleOfferSet(offerSet as EdgeOfferSet, node, generation)
                  )}
                  onError={(_error, generation) => handleOfferError(generation)}
                />
              ))}
          {discoveryEnabled && selectedNode && (
            <NodeToolbar
              node={selectedNode}
              transform={transform}
              apiBaseUrl={apiBaseUrl!}
              authorizationToken={authorizationToken}
              sessionId={sessionId!}
              onDeleted={handleDeleted}
            />
          )}
          <NodeLimitBanner activeCount={liveNodes.length} />
          {discoveryError ? (
            <View style={styles.discoveryError}>
              <Text style={styles.discoveryErrorText}>{discoveryError}</Text>
            </View>
          ) : null}
          {positionWrites.failedNodeCount > 0 ? (
            <View style={styles.positionWriteError}>
              <Text style={styles.positionWriteErrorText}>
                {positionWrites.failedNodeCount} node position
                {positionWrites.failedNodeCount === 1 ? '' : 's'} not saved.
              </Text>
              <Pressable
                testID="position-write-retry"
                accessibilityRole="button"
                accessibilityLabel="Retry saving node positions"
                onPress={positionWrites.retryFailed}
                style={styles.positionWriteRetry}
              >
                <Text style={styles.positionWriteRetryText}>Retry</Text>
              </Pressable>
            </View>
          ) : null}
          <CanvasToolbar
            transform={transform}
            screen={screen}
            nodes={liveNodes}
            snapToGrid={snapToGrid}
            onCommitTransform={commitToolbarTransform}
            onToggleSnapToGrid={() => setSnapToGrid((value) => !value)}
          />
        </View>
      </GestureDetector>
      {discoveryEnabled && activeOfferSet && (
        <EdgeOfferSetSheet
          visible
          offerSet={activeOfferSet.offerSet}
          threadContextId={activeOfferSet.sourceNode.thread_context_id ?? ''}
          sourcePosition={activeOfferSet.sourceNode.position}
          apiBaseUrl={apiBaseUrl!}
          authorizationToken={authorizationToken}
          onClose={closeOfferSet}
          onBranchCreated={handleBranchCreated}
        />
      )}
    </GestureHandlerRootView>
  );
}

export { SkiaCanvas };

const styles = StyleSheet.create({
  root: { flex: 1 },
  discoveryError: {
    position: 'absolute',
    left: 16,
    right: 16,
    bottom: 24,
    padding: 10,
    borderRadius: 8,
    backgroundColor: '#7f1d1d',
  },
  discoveryErrorText: { color: '#ffffff', fontSize: 13, fontWeight: '600' },
  positionWriteError: {
    position: 'absolute',
    left: 16,
    right: 16,
    bottom: 68,
    padding: 10,
    borderRadius: 8,
    backgroundColor: '#7f1d1d',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  positionWriteErrorText: { color: '#ffffff', fontSize: 13, fontWeight: '600' },
  positionWriteRetry: { paddingHorizontal: 12, paddingVertical: 8 },
  positionWriteRetryText: { color: '#ffffff', fontSize: 13, fontWeight: '700' },
});
