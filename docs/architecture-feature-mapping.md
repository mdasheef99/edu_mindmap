# V1 Master Strategy: Architecture-to-Feature Mapping

## Document Overview

This document maps the V1 Master Strategy (React Native Skia + D3-Force + Zustand/Reanimated) to specific features in the Mobile Feature Specification v2.0. It provides implementation guidance for each feature based on the three architectural pillars.

**Architecture Pillars**:
1. **Rendering Engine**: React Native Skia for 2D graphics
2. **Layout Engine**: D3-Force for physics-based positioning
3. **State & Interaction**: Zustand (canonical) + Reanimated (transient)

---

## Pillar 1: Rendering Engine (Skia) Feature Mapping

### Section 2: Node-Level Features

| Feature | Spec Reference | Skia Implementation | Priority |
|---------|----------------|---------------------|----------|
| Create text node | 2.1 | `<TextNode />` Skia component with `Skia.Text` | MVP |
| Edit text content | 2.1 | Overlay React Native `<TextInput>` on tap (hybrid approach) | MVP |
| Change node color | 2.1 | `style.color` prop → Skia `Paint.setColor()` | MVP |
| Node selection border | 2.1 | Conditional `strokeWidth` based on `isSelected` state | MVP |
| Create story node | 2.2 | `<StoryNode />` with header/body regions | MVP |
| Collapse/expand animation | 2.2 | Reanimated `SharedValue` for height interpolation | MVP |
| Create AI node | 2.3 | `<AINode />` with response area, loading indicator | MVP |
| AI response scrolling | 2.3 | Skia `ClipRect` + gesture-driven offset | MVP |
| Video node thumbnail | 2.4 | `<Image />` Skia component from texture atlas | MVP |
| Connection lines (edges) | All nodes | Quadratic Bézier via `Skia.Path` | MVP |

#### Node Rendering Architecture

```typescript
// Node component structure
interface SkiaNodeProps {
  node: Node;
  isSelected: boolean;
  zoomLevel: SharedValue<number>;
  position: { x: SharedValue<number>; y: SharedValue<number> };
}

const TextNode: React.FC<SkiaNodeProps> = ({ node, isSelected, zoomLevel, position }) => {
  // LOD: Simplify at low zoom
  const showText = useDerivedValue(() => zoomLevel.value > 0.5);

  return (
    <Group transform={[{ translateX: position.x.value }, { translateY: position.y.value }]}>
      <RoundedRect
        width={node.width}
        height={node.height}
        r={8}
        color={node.style.color}
      />
      {isSelected && (
        <RoundedRect
          width={node.width + 4}
          height={node.height + 4}
          r={10}
          style="stroke"
          strokeWidth={2}
          color="#007AFF"
        />
      )}
      {showText.value && (
        <Text text={node.content} x={8} y={24} font={font} />
      )}
    </Group>
  );
};
```

### Section 3: Canvas-Level Features

| Feature | Spec Reference | Skia Implementation | Priority |
|---------|----------------|---------------------|----------|
| Pinch to zoom (25%-400%) | 3.1 | Canvas transform matrix via SharedValue | MVP |
| Pan/scroll | 3.1 | Translation in transform matrix | MVP |
| Zoom buttons (+/-) | 3.1 | Animate `scale` SharedValue | MVP |
| Fit to screen | 3.1 | Calculate bounding box → set transform | MVP |
| Snap to grid | 3.4 | Round position on drag end | MVP |
| Alignment guides | 3.4 | Conditional `<Line />` components | Extended |
| Node count indicator | 3.6 | Derived from Zustand store length | MVP |

#### Canvas Transform Architecture

```typescript
// Canvas-level transform management
const useCanvasTransform = () => {
  const scale = useSharedValue(1);
  const translateX = useSharedValue(0);
  const translateY = useSharedValue(0);

  const transform = useDerivedValue(() => [
    { translateX: translateX.value },
    { translateY: translateY.value },
    { scale: scale.value },
  ]);

  return { scale, translateX, translateY, transform };
};
```

### Section 4.4: Previous Year Questions Panel

| Feature | Spec Reference | Skia Implementation | Priority |
|---------|----------------|---------------------|----------|
| Add PYQ to mind map | 4.4 | Creates new node via Zustand action | MVP |

*Note: PYQ panel itself uses standard React Native components (bottom sheet), not Skia.*

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

The critical synchronization between D3-Force (JS thread) and Skia rendering (UI thread):

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

These features use **standard React Native components** (not Skia), but interact with Zustand for state.

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

Side panels use **React Native Bottom Sheet** (not Skia canvas).

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

The V1 Master Strategy defines four key optimizations. Here's how they map to features:

### Texture Atlasing

| Optimization | Applied To | Features Affected |
|--------------|-----------|-------------------|
| Single spritesheet for icons | Node type icons | 2.1-2.4 (all node types) |
| Pre-rendered common shapes | Node backgrounds | 2.1-2.4 |
| Cached font glyphs | Text rendering | All text nodes |

### Viewport Culling

| Optimization | Applied To | Features Affected |
|--------------|-----------|-------------------|
| Only render visible nodes | Canvas rendering | 3.1 (zoom/pan) |
| Skip off-screen edges | Edge rendering | All connections |
| Disable D3 updates for hidden | Layout engine | 3.3 (auto-arrange) |

```typescript
const useViewportCulling = (nodes: Node[], viewport: Viewport) => {
  return useDerivedValue(() => {
    return nodes.filter(node =>
      node.x >= viewport.left - BUFFER &&
      node.x <= viewport.right + BUFFER &&
      node.y >= viewport.top - BUFFER &&
      node.y <= viewport.bottom + BUFFER
    );
  });
};
```

### Level of Detail (LOD)

| Zoom Level | Rendering Detail | Features Affected |
|------------|-----------------|-------------------|
| < 0.5 | Rectangles only, no text | 3.1 (zoom) |
| 0.5 - 1.0 | Text visible, simplified borders | 3.1 (zoom) |
| > 1.0 | Full detail, shadows, gradients | 3.1 (zoom) |

### Render Batching

| Optimization | Applied To | Features Affected |
|--------------|-----------|-------------------|
| Single path for all edges | Edge rendering | All connections |
| Grouped node backgrounds | Background fills | 2.1-2.4 |

---

## Feature-to-Component Matrix

Quick reference: which architectural components each feature requires.

| Feature Area | Skia | D3-Force | Zustand | Reanimated | RN Native |
|-------------|------|----------|---------|------------|-----------|
| **Section 1: Curriculum** | ❌ | ❌ | ✅ | ❌ | ✅ |
| **Section 2: Nodes** | ✅ | ✅ | ✅ | ✅ | Hybrid* |
| **Section 3: Canvas** | ✅ | ✅ | ❌ | ✅ | ❌ |
| **Section 4: Side Panels** | ❌ | ❌ | ✅ | ❌ | ✅ |
| **Section 5: Navigation** | ❌ | ❌ | ✅ | ❌ | ✅ |
| **Section 6: AI Integration** | ❌ | ❌ | ✅ | ❌ | ❌** |
| **Section 7: System** | ❌ | ❌ | ✅ | ❌ | ✅ |

*Hybrid: Text input overlays use React Native components
**API calls are pure TypeScript, no UI components

---

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATA FLOW DIAGRAM                               │
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
│  ┌──────┴──────┐                   ┌─────────────────┐                 │
│  │   Gesture   │                   │   Skia Canvas   │                 │
│  │   Handler   │                   │   (Rendering)   │                 │
│  │  (UI Thread)│                   │                 │                 │
│  └─────────────┘                   └─────────────────┘                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Hit Testing Implementation

Skia canvas requires custom hit testing for node selection (Section 3.2).

```typescript
interface HitTestResult {
  nodeId: string | null;
  edgeId: string | null;
}

const hitTest = (
  canvasX: number,
  canvasY: number,
  nodes: Node[],
  edges: Edge[],
  transform: CanvasTransform
): HitTestResult => {
  // Transform screen coords to canvas coords
  const x = (canvasX - transform.translateX) / transform.scale;
  const y = (canvasY - transform.translateY) / transform.scale;

  // Check nodes first (higher priority)
  for (const node of nodes) {
    if (
      x >= node.x &&
      x <= node.x + node.width &&
      y >= node.y &&
      y <= node.y + node.height
    ) {
      return { nodeId: node.id, edgeId: null };
    }
  }

  // Check edges (with tolerance for touch)
  const EDGE_TOLERANCE = 10;
  for (const edge of edges) {
    if (pointNearBezier(x, y, edge, EDGE_TOLERANCE)) {
      return { nodeId: null, edgeId: edge.id };
    }
  }

  return { nodeId: null, edgeId: null };
};
```

---

## Implementation Priority Order

Based on architectural dependencies, implement in this order:

| Phase | Components | Features Enabled |
|-------|-----------|------------------|
| 1 | Zustand store | All data persistence |
| 2 | D3-Force simulation | Node positioning, auto-arrange |
| 3 | Reanimated SharedValues | 60fps animations, gestures |
| 4 | Skia rendering | Visual node/edge display |
| 5 | Gesture Handler integration | Pan, zoom, drag, tap |
| 6 | Zustand ↔ D3 bridge | Node dragging with physics |
| 7 | Side panels (RN) | Questions, resources, PYQ |
| 8 | AI integration | Question generation |

---

## Testing Strategy by Architecture Layer

| Layer | Test Type | Key Scenarios |
|-------|----------|---------------|
| **Zustand** | Unit tests | CRUD operations, node limit, edge cascading |
| **D3-Force** | Integration tests | Simulation convergence, fx/fy pinning |
| **Reanimated** | Manual + E2E | 60fps verification, gesture smoothness |
| **Skia** | Visual regression | Node rendering, LOD transitions |
| **Hit Testing** | Unit tests | Touch accuracy, transform math |

---

*Document Version 1.0 | Architecture-Feature Mapping*
*Aligned with: Mobile Feature Specification v2.0, V1 Master Strategy*

