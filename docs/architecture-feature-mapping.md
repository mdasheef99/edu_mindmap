# V1 Master Strategy: Architecture-to-Feature Mapping

## Document Overview

This document maps the V1 Master Strategy (Hybrid Native Views + Skia Edges + D3-Force + Zustand/Reanimated) to specific features in the Mobile Feature Specification v2.0. It provides implementation guidance for each feature based on the three architectural pillars.

**Architecture Pillars**:
1. **Rendering Engine**: Hybrid — React Native Animated Views for nodes + Skia for edge rendering
2. **Layout Engine**: D3-Force for physics-based positioning
3. **State & Interaction**: Zustand (canonical) + Reanimated (transient)

> **Architecture Decision Record**: The hybrid rendering approach was chosen over a full Skia canvas approach. See [Why Hybrid Architecture?](#why-hybrid-architecture) at the end of this document for rationale, trade-offs, and escalation criteria.

---

## Pillar 1: Rendering Engine (Hybrid Native Views + Skia Edges) Feature Mapping

### Section 2: Node-Level Features

| Feature | Spec Reference | Implementation | Priority |
|---------|----------------|----------------|----------|
| Create text node | 2.1 | `<TextNode />` React Native Animated.View with native `<Text>` | MVP |
| Edit text content | 2.1 | Native `<TextInput>` inside node View (no overlay hack needed) | MVP |
| Change node color | 2.1 | `style.backgroundColor` prop on Animated.View | MVP |
| Node selection border | 2.1 | Conditional `borderWidth`/`borderColor` style on Animated.View | MVP |
| Create story node | 2.2 | `<StoryNode />` Animated.View with header/body sub-views | MVP |
| Collapse/expand animation | 2.2 | Reanimated `SharedValue` for height interpolation via `useAnimatedStyle` | MVP |
| Create AI node | 2.3 | `<AINode />` Animated.View with response area, loading indicator | MVP |
| AI response scrolling | 2.3 | Native `<ScrollView>` inside AI node View (free scrolling behavior) | MVP |
| Video node thumbnail | 2.4 | `<FastImage />` component inside node View | MVP |
| Connection lines (edges) | All nodes | Quadratic Bézier via `Skia.Path` (Skia used only for edges) | MVP |

#### Node Rendering Architecture

```typescript
// Hybrid approach: Nodes are React Native Animated.View components
// Edges are rendered via a Skia Canvas layer underneath
import Animated, { useAnimatedStyle, SharedValue } from 'react-native-reanimated';

interface NodeViewProps {
  node: Node;
  isSelected: boolean;
  zoomLevel: SharedValue<number>;
  position: { x: SharedValue<number>; y: SharedValue<number> };
}

const TextNode: React.FC<NodeViewProps> = ({ node, isSelected, zoomLevel, position }) => {
  // Animated position driven by D3-Force via SharedValues
  const animatedStyle = useAnimatedStyle(() => ({
    transform: [
      { translateX: position.x.value },
      { translateY: position.y.value },
    ],
    // LOD: Reduce detail at low zoom
    opacity: zoomLevel.value > 0.3 ? 1 : 0.7,
  }));

  return (
    <Animated.View style={[styles.nodeBase, animatedStyle, {
      backgroundColor: node.style.color,
      borderWidth: isSelected ? 2 : 0,
      borderColor: isSelected ? '#007AFF' : 'transparent',
    }]}>
      {/* Native text rendering — free accessibility, selection, RTL support */}
      <Text style={styles.nodeText}>{node.content}</Text>
    </Animated.View>
  );
};

// Benefits over full Skia approach:
// - Native touch targets (no custom hit testing)
// - Native TextInput for editing (no overlay positioning hack)
// - Native ScrollView for AI response scrolling
// - Native accessibility (screen readers work automatically)
// - React DevTools inspection works normally
```

### Section 3: Canvas-Level Features

| Feature | Spec Reference | Implementation | Priority |
|---------|----------------|----------------|----------|
| Pinch to zoom (25%-400%) | 3.1 | Reanimated animated transform on canvas container `Animated.View` | MVP |
| Pan/scroll | 3.1 | Reanimated `translateX`/`translateY` SharedValues on container | MVP |
| Zoom buttons (+/-) | 3.1 | Animate `scale` SharedValue with `withTiming()` | MVP |
| Fit to screen | 3.1 | Calculate bounding box → set transform SharedValues | MVP |
| Snap to grid | 3.4 | Round position SharedValues on drag end | MVP |
| Alignment guides | 3.4 | Conditional `react-native-svg` `<Line />` components | Extended |
| Node count indicator | 3.6 | Derived from Zustand store length | MVP |

#### Canvas Transform Architecture

```typescript
// Canvas container: Reanimated Animated.View wrapping all nodes + Skia edge layer
import Animated, { useSharedValue, useDerivedValue, useAnimatedStyle } from 'react-native-reanimated';

const useCanvasTransform = () => {
  const scale = useSharedValue(1);
  const translateX = useSharedValue(0);
  const translateY = useSharedValue(0);

  // Applied to the canvas container Animated.View
  const canvasStyle = useAnimatedStyle(() => ({
    transform: [
      { translateX: translateX.value },
      { translateY: translateY.value },
      { scale: scale.value },
    ],
  }));

  return { scale, translateX, translateY, canvasStyle };
};

// Canvas structure:
// <GestureDetector gesture={canvasGestures}>
//   <Animated.View style={canvasStyle}>
//     {/* Skia Canvas layer for edges (Bézier curves only) */}
//     <Canvas style={StyleSheet.absoluteFill}>
//       {edges.map(edge => <EdgePath key={edge.id} edge={edge} />)}
//     </Canvas>
//     {/* React Native node Views rendered on top */}
//     {visibleNodes.map(node => <NodeView key={node.id} node={node} />)}
//   </Animated.View>
// </GestureDetector>
```

### Section 4.4: Previous Year Questions Panel

| Feature | Spec Reference | Implementation | Priority |
|---------|----------------|----------------|----------|
| Add PYQ to mind map | 4.4 | Creates new node via Zustand action | MVP |

*Note: PYQ panel uses standard React Native components (bottom sheet). Node rendering uses Animated.View.*

---

## Pillar 2: Layout Engine (D3-Force) Feature Mapping

### Section 3.3: Auto-Arrange & Layout Features

| Feature | Spec Reference | D3-Force Implementation | Priority |
|---------|----------------|------------------------|----------|
| Auto-arrange nodes | 3.3 | Trigger full simulation with `alpha(1).restart()` | MVP |
| Organic layout | 3.3 | Default force configuration (link + charge + center) | MVP |
| Prevent overlap | 3.3 | `d3.forceCollide(nodeRadius + padding)` | MVP |
| Connected node clustering | 3.3 | `d3.forceLink()` with dynamic distance | MVP |
| Hierarchical layout | 3.3 | Custom radial force from root node | Extended |
| Layout presets | 3.3 | Store force configs; swap and restart | Extended |

#### D3-Force Configuration

```typescript
import * as d3 from 'd3-force';

interface ForceConfig {
  linkDistance: number;
  chargeStrength: number;
  collideRadius: number;
  centerStrength: number;
}

const DEFAULT_CONFIG: ForceConfig = {
  linkDistance: 120,
  chargeStrength: -300,
  collideRadius: 60,
  centerStrength: 0.05,
};

const createSimulation = (nodes: Node[], edges: Edge[], config = DEFAULT_CONFIG) => {
  return d3.forceSimulation(nodes)
    .force('link', d3.forceLink(edges)
      .id((d: Node) => d.id)
      .distance(config.linkDistance))
    .force('charge', d3.forceManyBody()
      .strength(config.chargeStrength))
    .force('collide', d3.forceCollide()
      .radius(config.collideRadius))
    .force('center', d3.forceCenter(canvasWidth / 2, canvasHeight / 2)
      .strength(config.centerStrength));
};
```

### D3 → Reanimated Bridge

The critical synchronization between D3-Force (JS thread) and Animated.View rendering (UI thread):

```typescript
// Bridge: D3 simulation tick → Reanimated SharedValues
const useD3ToReanimatedBridge = (
  simulation: d3.Simulation<Node, Edge>,
  nodePositions: Map<string, { x: SharedValue<number>; y: SharedValue<number> }>
) => {
  useEffect(() => {
    simulation.on('tick', () => {
      // Run on JS thread, but SharedValue updates propagate to UI thread
      runOnJS(() => {
        simulation.nodes().forEach((node) => {
          const pos = nodePositions.get(node.id);
          if (pos) {
            pos.x.value = node.x ?? 0;
            pos.y.value = node.y ?? 0;
          }
        });
      })();
    });

    return () => simulation.stop();
  }, [simulation]);
};
```

### Node Dragging with D3 Pinning (fx/fy)

| Feature | Spec Reference | D3-Force Implementation | Priority |
|---------|----------------|------------------------|----------|
| Drag node | 3.2 | Set `fx`/`fy` on gesture start | MVP |
| Smooth drag | 3.2 | Update SharedValue on gesture update | MVP |
| Release with physics | 3.2 | Clear `fx`/`fy` on gesture end; reheat simulation | MVP |

```typescript
const useNodeDrag = (nodeId: string, simulation: d3.Simulation<Node, Edge>) => {
  const gesture = Gesture.Pan()
    .onStart(() => {
      // Pin node to prevent D3 from moving it
      const node = simulation.nodes().find(n => n.id === nodeId);
      if (node) {
        node.fx = node.x;
        node.fy = node.y;
      }
      simulation.alphaTarget(0.3).restart(); // Reheat slightly
    })
    .onUpdate((e) => {
      const node = simulation.nodes().find(n => n.id === nodeId);
      if (node) {
        node.fx = e.absoluteX;
        node.fy = e.absoluteY;
      }
    })
    .onEnd(() => {
      // Release pin; let D3 take over smoothly
      const node = simulation.nodes().find(n => n.id === nodeId);
      if (node) {
        node.fx = null;
        node.fy = null;
      }
      simulation.alphaTarget(0); // Cool down
    });

  return gesture;
};
```

---

## Pillar 3: State & Interaction Feature Mapping

### Zustand Store (Canonical State)

All persistent data lives in Zustand. This maps to features requiring data persistence.

| Feature | Spec Reference | Zustand Implementation | Priority |
|---------|----------------|----------------------|----------|
| Create new node | 2.1, 2.2, 2.3 | `addNode(node: Node)` action | MVP |
| Delete node | 2.1 | `removeNode(nodeId)` + cascade edges | MVP |
| Edit node content | 2.1 | `updateNode(nodeId, changes)` action | MVP |
| Connect nodes | 2.1 | `addEdge(edge: Edge)` action | MVP |
| Session persistence | 7.4 | `persist` middleware with AsyncStorage | MVP |
| Undo/Redo | 3.5 | `temporal` middleware or manual history stack | Extended |
| Node limit (55-65) | 3.6 | Guard in `addNode` action | MVP |

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface MindMapState {
  nodes: Node[];
  edges: Edge[];
  selectedNodeId: string | null;
  chapterId: string | null;

  // Actions
  addNode: (node: Node) => void;
  removeNode: (nodeId: string) => void;
  updateNode: (nodeId: string, changes: Partial<Node>) => void;
  addEdge: (edge: Edge) => void;
  removeEdge: (edgeId: string) => void;
  selectNode: (nodeId: string | null) => void;
  loadSession: (chapterId: string) => Promise<void>;
  saveSession: () => Promise<void>;
}

const NODE_LIMIT = 65;

export const useMindMapStore = create<MindMapState>()(
  persist(
    (set, get) => ({
      nodes: [],
      edges: [],
      selectedNodeId: null,
      chapterId: null,

      addNode: (node) => set((state) => {
        if (state.nodes.length >= NODE_LIMIT) {
          console.warn('Node limit reached');
          return state;
        }
        return { nodes: [...state.nodes, node] };
      }),

      removeNode: (nodeId) => set((state) => ({
        nodes: state.nodes.filter(n => n.id !== nodeId),
        edges: state.edges.filter(e =>
          e.source !== nodeId && e.target !== nodeId
        ),
        selectedNodeId: state.selectedNodeId === nodeId ? null : state.selectedNodeId,
      })),

      // ... other actions
    }),
    {
      name: 'mindmap-session',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);
```

### Reanimated SharedValues (Transient State)

All 60fps animations and gestures use SharedValues, never triggering React re-renders.

| Feature | Spec Reference | Reanimated Implementation | Priority |
|---------|----------------|--------------------------|----------|
| Pan gesture | 3.1 | `translateX`, `translateY` SharedValues | MVP |
| Pinch zoom | 3.1 | `scale` SharedValue + focal point | MVP |
| Node drag position | 3.2 | Per-node `{ x, y }` SharedValue map | MVP |
| Selection animation | 3.2 | `withTiming()` for border opacity | MVP |
| Expand/collapse animation | 2.2 | `withSpring()` for node height | MVP |
| Loading spinner | 2.3 | `withRepeat(withTiming())` for rotation | MVP |

```typescript
import { useSharedValue, withTiming, withSpring } from 'react-native-reanimated';
import { Gesture } from 'react-native-gesture-handler';

// Per-node position tracking
const useNodePositions = (nodes: Node[]) => {
  const positions = useRef<Map<string, { x: SharedValue<number>; y: SharedValue<number> }>>(
    new Map()
  );

  // Create SharedValues for new nodes
  nodes.forEach((node) => {
    if (!positions.current.has(node.id)) {
      positions.current.set(node.id, {
        x: makeShareable(node.x),
        y: makeShareable(node.y),
      });
    }
  });

  return positions.current;
};

// Canvas gesture composition
const useCanvasGestures = (transform: CanvasTransform) => {
  const pinch = Gesture.Pinch()
    .onUpdate((e) => {
      transform.scale.value = Math.max(0.25, Math.min(4, e.scale));
    });

  const pan = Gesture.Pan()
    .onUpdate((e) => {
      transform.translateX.value += e.changeX;
      transform.translateY.value += e.changeY;
    });

  return Gesture.Simultaneous(pinch, pan);
};
```

---

## Section 1: Curriculum & Syllabus Navigation Mapping

These features use **standard React Native components** (same as the node rendering layer), interacting with Zustand for state.

| Feature | Spec Reference | Implementation | Priority |
|---------|----------------|----------------|----------|
| Class selection | 1.1 | React Native Picker → Zustand `setClass()` | MVP |
| Exam selection | 1.1 | Filtered list based on class → Zustand | MVP |
| Subject list | 1.2 | FlatList with Supabase query | MVP |
| Chapter list | 1.2 | FlatList filtered by subject | MVP |
| Progress indicators | 1.2 | Read from Zustand session history | MVP |
| Dashboard | 1.3 | Custom React Native screen | MVP |
| Continue learning | 1.3 | Load persisted Zustand state | MVP |
| Recent sessions | 1.3 | Query local AsyncStorage | MVP |

---

## Section 4: Side Panel Features Mapping

Side panels use **React Native Bottom Sheet** (`@gorhom/bottom-sheet`), consistent with the hybrid native Views approach.

| Feature | Spec Reference | Implementation | Priority |
|---------|----------------|----------------|----------|
| Questions list | 4.1 | Bottom sheet + FlatList | MVP |
| Generate new Qs | 4.1 | Trigger LLM API → update Zustand | MVP |
| Reader (selectable text) | 6.5.2 | Bottom sheet reader using native text surface (e.g., read-only multiline TextInput) | MVP |
| Phrase action sheet | 6.5.2 | Bottom sheet: fixed actions + recommended question cards | MVP |
| Resources panel | 4.2 | Tabbed bottom sheet | MVP |
| PYQ filter | 4.4 | Filter controls + query | MVP |
| Add PYQ to map | 4.4 | `addNode()` action → D3 simulation restart | MVP |

---

## Section 5: Top-Level Navigation Mapping

| Feature | Spec Reference | Implementation | Priority |
|---------|----------------|----------------|----------|
| FAB (add node) | 5.2 | React Native FAB → Zustand `addNode()` | MVP |
| Bottom nav (Questions/Resources) | 5.3 | React Native Tab Navigator | MVP |
| Header with chapter context | 5.1 | React Native View with Zustand selector | MVP |
| Back button | 5.1 | React Navigation `goBack()` | MVP |

---

## Section 6: AI Integration Features Mapping

| Feature | Spec Reference | Architecture Component | Priority |
|---------|----------------|----------------------|----------|
| Generate questions from phrase | 6.1 | Direct Anthropic API call | MVP |
| Stream AI response | 6.1 | `stream: true` in API request | MVP |
| Populate AI node | 6.1 | API response → `updateNode()` action | MVP |
| Cache responses | 6.1 | Zustand with TTL middleware | Extended |
| Post-hoc classification | 6.2 | Background API call (invisible), uses Claude Haiku | MVP |

**LLM Model Split**:
- **Question generation** (Stage 1): `claude-sonnet-4-20250514` — requires nuanced, organic question phrasing
- **Post-hoc classification** (Stage 2): `claude-haiku-4-20250514` — constrained structured-output task (10x cheaper, see `docs/scalability-analysis.md` §4.5)

```typescript
// AI Integration with Zustand
const useGenerateQuestions = () => {
  const updateNode = useMindMapStore((s) => s.updateNode);
  const currentNode = useMindMapStore((s) =>
    s.nodes.find(n => n.id === s.selectedNodeId)
  );

  const generate = async (phrase: string) => {
    // Update node to loading state
    updateNode(currentNode.id, { isLoading: true });

    try {
      const response = await anthropic.messages.create({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 1000,
        messages: [{
          role: 'user',
          content: buildQuestionPrompt(phrase, currentNode.context)
        }]
      });

      // Update node with response
      updateNode(currentNode.id, {
        isLoading: false,
        content: response.content[0].text
      });
    } catch (error) {
      updateNode(currentNode.id, { isLoading: false, error: error.message });
    }
  };

  return { generate };
};
```

---

## Section 7: System-Level Features Mapping

| Feature | Spec Reference | Architecture Component | Priority |
|---------|----------------|----------------------|----------|
| Authentication | 7.1 | Supabase Auth | MVP |
| Session sync | 7.4 | Zustand persist + Supabase upsert | MVP |
| Offline mode (core) | 7.3 | AsyncStorage + sync queue | MVP |
| Auto-save | 7.4 | Zustand subscribe + debounce | MVP |

*Note: Offline mode elevated to MVP per `mobile-features-system.md` Section 7.3 based on Indian student device market research. Core offline = cached board access + queued edits. AI features (question generation, classification) require network connectivity and are excluded from offline mode.*




---

## Performance Optimizations → Feature Mapping

The hybrid architecture uses different optimization strategies than a full Skia canvas. Here's how they map to features:

### Icon Caching

| Optimization | Applied To | Features Affected |
|--------------|-----------|-------------------|
| `react-native-fast-image` for cached icons | Node type icons | 2.1-2.4 (all node types) |
| Pre-loaded icon assets | Node backgrounds | 2.1-2.4 |
| Native text rendering (no glyph caching needed) | Text rendering | All text nodes |

### Viewport Culling

| Optimization | Applied To | Features Affected |
|--------------|-----------|-------------------|
| Conditionally render visible node Views | Node rendering | 3.1 (zoom/pan) |
| Skip off-screen edges in Skia canvas | Edge rendering | All connections |
| Disable D3 updates for hidden | Layout engine | 3.3 (auto-arrange) |

```typescript
// Viewport culling with hybrid approach: conditionally render node Views
// React handles mount/unmount automatically — simpler than Skia draw list management
const useViewportCulling = (nodes: Node[], viewport: Viewport) => {
  return useMemo(() => {
    return nodes.filter(node =>
      node.x >= viewport.left - BUFFER &&
      node.x <= viewport.right + BUFFER &&
      node.y >= viewport.top - BUFFER &&
      node.y <= viewport.bottom + BUFFER
    );
  }, [nodes, viewport]);
};

// Usage in canvas:
// {visibleNodes.map(node => <NodeView key={node.id} node={node} />)}
// Nodes outside viewport are simply not rendered (React unmounts them)
```

### Level of Detail (LOD)

| Zoom Level | Rendering Detail | Features Affected |
|------------|-----------------|-------------------|
| < 0.5 | Simplified node Views (no text, reduced styling) | 3.1 (zoom) |
| 0.5 - 1.0 | Text visible, simplified borders | 3.1 (zoom) |
| > 1.0 | Full detail, shadows, elevation | 3.1 (zoom) |

*LOD is implemented via conditional rendering within each node View component, driven by the `zoomLevel` SharedValue.*

### Edge Render Batching (Skia)

| Optimization | Applied To | Features Affected |
|--------------|-----------|-------------------|
| Single Skia `Path` for all edges | Edge rendering | All connections |
| Skia `Canvas` layer underneath node Views | Edge layer | All connections |

*Edge batching is the primary Skia optimization. All Bézier curves are combined into a single draw call.*

---

## Feature-to-Component Matrix

Quick reference: which architectural components each feature requires.

| Feature Area | Skia (Edges) | D3-Force | Zustand | Reanimated | RN Animated Views |
|-------------|-------------|----------|---------|------------|-------------------|
| **Section 1: Curriculum** | ❌ | ❌ | ✅ | ❌ | ✅ |
| **Section 2: Nodes** | Edges only | ✅ | ✅ | ✅ | ✅ (node Views) |
| **Section 3: Canvas** | Edges only | ✅ | ❌ | ✅ (container) | ✅ (node Views) |
| **Section 4: Side Panels** | ❌ | ❌ | ✅ | ❌ | ✅ |
| **Section 5: Navigation** | ❌ | ❌ | ✅ | ❌ | ✅ |
| **Section 6: AI Integration** | ❌ | ❌ | ✅ | ❌ | ❌* |
| **Section 7: System** | ❌ | ❌ | ✅ | ❌ | ✅ |

*API calls are pure TypeScript, no UI components

> **Key change from full Skia approach**: Nodes are now React Native Animated.View components (not Skia draw calls). Skia is used **only** for edge rendering (Bézier curves). This eliminates the need for custom hit testing, text overlay hacks, and custom scrolling within nodes.

---

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DATA FLOW DIAGRAM (Hybrid Architecture)              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐                                                        │
│  │   Supabase  │◄────── Session Load/Save                              │
│  │  (Remote)   │                                                        │
│  └──────┬──────┘                                                        │
│         │                                                               │
│         ▼                                                               │
│  ┌─────────────┐     addNode()     ┌─────────────────┐                 │
│  │   Zustand   │◄─────────────────│   User Actions   │                 │
│  │  (Source of │    updateNode()   │   (UI Events)   │                 │
│  │   Truth)    │    removeNode()   └─────────────────┘                 │
│  └──────┬──────┘                                                        │
│         │                                                               │
│         │ nodes[]                                                       │
│         ▼                                                               │
│  ┌─────────────┐     tick()        ┌─────────────────┐                 │
│  │  D3-Force   │──────────────────►│   SharedValues  │                 │
│  │ (Simulation)│     x, y          │    (Positions)  │                 │
│  └──────┬──────┘                   └────────┬────────┘                 │
│         │                                   │                           │
│         │ fx, fy (pinning)                  │ 60fps                    │
│         ▲                                   ▼                           │
│  ┌──────┴──────┐                   ┌─────────────────────────────┐     │
│  │   Gesture   │                   │  Animated.View (Nodes)      │     │
│  │   Handler   │                   │  + Skia Canvas (Edges only) │     │
│  │  (UI Thread)│                   │  (Hybrid Rendering)         │     │
│  └─────────────┘                   └─────────────────────────────┘     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Touch Handling (Hybrid Approach)

With the hybrid architecture, **custom hit testing is not required for nodes**. React Native's native touch system handles node selection automatically via `Pressable` or `TouchableOpacity` wrappers on each node View.

```typescript
// Node touch handling — native React Native, no custom coordinate math needed
const NodeView: React.FC<{ node: Node; onSelect: (id: string) => void }> = ({ node, onSelect }) => {
  return (
    <Pressable onPress={() => onSelect(node.id)}>
      <Animated.View style={[styles.node, animatedPositionStyle]}>
        <Text>{node.content}</Text>
      </Animated.View>
    </Pressable>
  );
};

// Edge tap detection still uses coordinate math (edges are rendered in Skia)
const useEdgeTapDetection = (edges: Edge[], transform: CanvasTransform) => {
  const handleCanvasTap = (canvasX: number, canvasY: number) => {
    const x = (canvasX - transform.translateX.value) / transform.scale.value;
    const y = (canvasY - transform.translateY.value) / transform.scale.value;

    const EDGE_TOLERANCE = 10;
    for (const edge of edges) {
      if (pointNearBezier(x, y, edge, EDGE_TOLERANCE)) {
        return edge.id;
      }
    }
    return null;
  };
  return handleCanvasTap;
};

// Benefits of hybrid touch handling:
// - Node taps: Zero custom code (native Pressable)
// - Node drags: Gesture.Pan() directly on node View
// - Canvas pan/zoom: Gesture on container, disambiguated via simultaneousWithExternalGesture
// - Edge taps: Lightweight coordinate check (only for edges, not nodes)
```

---

## Implementation Priority Order

Based on architectural dependencies, implement in this order:

| Phase | Components | Features Enabled |
|-------|-----------|------------------|
| 1 | Zustand store | All data persistence |
| 2 | D3-Force simulation | Node positioning, auto-arrange |
| 3 | Reanimated SharedValues + Animated.View nodes | 60fps node rendering, animations |
| 4 | Skia edge rendering | Visual edge/connection display (Bézier curves) |
| 5 | Gesture Handler integration | Pan, zoom, drag, tap (native touch targets for nodes) |
| 6 | Zustand ↔ D3 bridge | Node dragging with physics |
| 7 | Side panels (RN) | Questions, resources, PYQ |
| 8 | AI integration | Question generation |

---

## Testing Strategy by Architecture Layer

| Layer | Test Type | Key Scenarios |
|-------|----------|---------------|
| **Zustand** | Unit tests | CRUD operations, node limit, edge cascading |
| **D3-Force** | Integration tests | Simulation convergence, fx/fy pinning |
| **Reanimated + Animated.View** | Manual + E2E | 60fps verification, gesture smoothness, node rendering |
| **Skia (Edges)** | Visual regression | Edge rendering, Bézier curve accuracy |
| **Gesture Handler** | Integration tests | Touch disambiguation (node tap vs canvas pan vs pinch zoom) |

---

## Why Hybrid Architecture?

### Architecture Decision Record

The hybrid rendering approach (React Native Animated.View for nodes + Skia for edges) was chosen over a full Skia canvas approach after evaluating implementation complexity, AI agent development efficiency, and performance requirements.

### Rationale

1. **AI Agent Implementation Difficulty**: An AI coding agent is responsible for implementing these features. The full Skia approach requires ~8 pieces of fully custom infrastructure (custom hit testing, text overlay hacks, custom scrolling, viewport culling in Skia draw lists, D3→Skia bridge, LOD rendering, texture atlasing, render batching). Each piece has no off-the-shelf equivalent and very few community examples. The hybrid approach reduces custom infrastructure to ~3 systems (D3→Reanimated bridge, viewport culling via conditional rendering, Skia edge paths).

2. **Faster Time-to-MVP**: The hybrid approach eliminates the need for:
   - Custom hit testing (React Native handles touch targets natively)
   - Text editing overlay positioning (native `TextInput` lives inside the node View)
   - Custom scrolling for AI responses (native `ScrollView` inside AI node View)
   - Custom accessibility implementation (React Native provides it automatically)
   - Custom text rendering (native `Text` component with full Unicode/RTL support)

3. **Debugging and Iteration**: React DevTools can inspect node Views normally. Skia canvas rendering requires visual inspection and frame-by-frame debugging that AI agents cannot perform.

4. **Performance is Sufficient**: For the target of 50-65 nodes on Android 11+ devices with 4GB RAM, React Native Animated.View components driven by Reanimated SharedValues deliver 60fps. The Reanimated library runs animations on the UI thread, bypassing the JS thread bottleneck.

### Side-by-Side Comparison

| Dimension | Full Skia (Previous) | Hybrid Views + Skia Edges (Current) |
|---|---|---|
| **AI implementation difficulty** | 🔴 Very Hard (8/10) | 🟡 Moderate (4/10) |
| **Custom infrastructure required** | ~8 major systems | ~3 major systems |
| **Performance ceiling** | Highest possible | Excellent for 50-65 nodes |
| **Text handling** | Manual overlay hack | Native (free) |
| **Accessibility** | Must build from scratch | Native (free) |
| **Hit testing** | Custom coordinate math | Native touch targets (free) |
| **Community examples** | Very few | Abundant |
| **Debugging** | Visual inspection needed | React DevTools work normally |
| **Time to MVP** | 4-6 months | 2-3 months |
| **Risk of showstopper bugs** | 🔴 High | 🟢 Low |

### When to Escalate to Full Skia

The hybrid approach has a known performance ceiling. Selectively migrate components to full Skia rendering if **any** of these thresholds are exceeded during device testing:

| Trigger | Threshold | Migration Action |
|---------|-----------|-----------------|
| Canvas pan/zoom frame drops | Below 50fps at 50+ nodes | Migrate node rendering to Skia draw calls |
| Edge rendering jank | Below 55fps with 100+ edges | Optimize Skia path batching (single path for all edges) |
| Memory exceeds budget | Above 150MB with 65 node Views | Implement view recycling, then Skia if still over budget |
| Node rendering overhead | Above 2ms per node layout pass | Profile and migrate heaviest node types to Skia |

This provides a **progressive enhancement path**: ship fast with hybrid, optimize with Skia only where proven necessary on actual target devices.

---

*Document Version 2.0 | Architecture-Feature Mapping (Hybrid Architecture)*
*Aligned with: Mobile Feature Specification v2.0, V1 Master Strategy*

