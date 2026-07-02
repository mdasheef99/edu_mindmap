/**
 * Canonical mindmap canvas store (M3-B SDD §6) — Zustand.
 *
 * This is the single source of truth for committed canvas state read by both the Skia edge
 * renderer and the Native node mapper. Per the write-direction rule (M3 SDD §5/§7), writes
 * happen on discrete commits (a tap, a gesture end) — never inside a Reanimated worklet;
 * ephemeral per-frame gesture values stay on SharedValues outside this store.
 *
 * Scope of this slice: node selection (§5.3). selectNode performs exactly one set(...) per
 * call (write-once rule), so a tap commits a single store mutation. No analytic fields are
 * held here (Category Invisibility).
 *
 * Persistence/hydration (M1 session resume) is layered later and is intentionally NOT part
 * of this selection slice; adding it will use the Expo v56 storage surface per
 * mobile/app/AGENTS.md.
 *
 * Traceability: phase-3-m3b-canvas-feature-parity-sdd.md §6, §7; phase-3-m3-canvas-sdd.md §5.
 */

import { create } from 'zustand';

export interface MindMapState {
  selectedNodeId: string | null;
  selectNode: (nodeId: string) => void;
  clearSelection: () => void;
}

export const useMindMapStore = create<MindMapState>()((set) => ({
  selectedNodeId: null,
  selectNode: (nodeId) => set({ selectedNodeId: nodeId }),
  clearSelection: () => set({ selectedNodeId: null }),
}));
