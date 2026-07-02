# 04 Feature Inventory

## 1. Mindmap Canvas (M3/M3-B)
- **Ownership**: Mobile (`mobile/canvas/`).
- **Core Files**:
    - `SkiaCanvas.tsx`: Main rendering surface.
    - `store.ts`: Zustand selection and transient state.
    - `useCanvasGestures.ts`: Pan, zoom, and node drag logic.
- **Patterns**: Hybrid Rendering, D3-Force physics.
- **Status**: Complete (Gate Closed 2026-06-22).

## 2. Phrase Selection & Reader (M2)
- **Ownership**: Mobile (`mobile/PhraseSelectionReaderSheet.tsx`).
- **Core Files**:
    - `PhraseSelectionReaderSheet.tsx`: Bottom sheet with selectable text.
    - `M2PhraseSmokeScreen.tsx`: Entry point for testing the flow.
- **Status**: Complete (Gate Closed 2026-06-20).

## 3. Session Persistence & Hydration (M1/M3-C)
- **Ownership**: Shared (Backend API + Mobile Hook).
- **Core Files**:
    - `mobile/canvas/useSessionHydration.ts`: Fetch and map snapshot.
    - `backend/app/runtime/canvas_state.py`: Snapshot reconstruction logic.
- **Status**: Complete (2026-06-24).

## 4. AI Question Generation (M2)
- **Ownership**: Backend (`backend/app/runtime/offer_workflow.py`).
- **Core Files**:
    - `offer_workflow.py`: Orchestrates LLM calls and offer-set creation.
    - `llm_gateway/`: Handles provider-specific prompting.

## 5. Async Classification (Tier 2)
- **Ownership**: Backend Worker (`backend/app/workers/classify.py`).
- **Status**: Locally Complete.

## Areas Not to Reuse Without Review
- **Legacy Components**: Any files in `mobile/` not under `mobile/app/` or `mobile/canvas/` (check `docs/mobile-features-index.md` for legacy refs).
- **In-Memory Fixtures**: Do not use `InMemory*` stores in production routes; ensure `SessionRuntime` is correctly configured for the environment.
