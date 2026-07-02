# 02 Critical Flows

## 1. Student Session Start
- **Description**: Learner launches a chapter and starts a new session.
- **Trigger**: `POST /v1/student/sessions`
- **Flow**:
    1. Mobile: `M2PhraseSmokeScreen.tsx` calls API.
    2. Backend: `app/api/student/sessions.py` -> `runtime.start_session`.
    3. Events: Appends `session_started` event.
    4. Projection: Updates `student_rm.sessions`.
    5. Response: Returns `StudentSession` object.

## 2. Phrase Selection & Question Discovery
- **Description**: Learner selects text in the reader to generate AI questions.
- **Trigger**: `POST /v1/student/offer-sets/phrase`
- **Flow**:
    1. Mobile: `PhraseSelectionReaderSheet.tsx` captures selection.
    2. Backend: `app/runtime/offer_workflow.py` -> `create_phrase_offer_set_workflow`.
    3. AI: `llm_gateway` calls model to generate questions.
    4. Response: Returns `PhraseOfferSetResponse` with questions.

## 3. Node Creation (Branching)
- **Description**: Learner chooses a question, creating a new node on the map.
- **Trigger**: `POST /v1/student/offer-sets/{id}/choices`
- **Flow**:
    1. Mobile: Tapping a question calls choice endpoint.
    2. Backend: `app/runtime/offer_workflow.py` -> `record_offer_choice_workflow`.
    3. Events: Appends `offer_set_choice` and `node_created`.
    4. Worker: Enqueues `classify` job.
    5. Sync: Updates `student_rm.nodes`.

## 4. Canvas Hydration
- **Description**: App loads and restores the mindmap state.
- **Hook**: `mobile/canvas/useSessionHydration.ts`
- **Flow**:
    1. Mobile: `useSessionHydration` calls `GET /v1/student/sessions/{id}`.
    2. Backend: `app/runtime/canvas_state.py` replays events to build snapshot.
    3. Mobile: Maps snapshot to `CanvasNode[]` and `CanvasEdge[]`.
    4. Render: `SkiaCanvas.tsx` renders nodes and edges.

## 5. Node Deletion (Cascade)
- **Description**: Deleting a parent node removes all descendant AI-generated nodes.
- **Workflow**: `backend/app/runtime/canvas_deletion.py` -> `delete_node_cascade_workflow`.
