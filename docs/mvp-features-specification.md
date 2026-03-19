# MVP Features Specification

## Executive Summary

This document consolidates the current MVP feature scope for the mobile application of the path-based conceptual exploration product. It is intended to be a practical implementation-facing reference for the learner experience and the shared platform capabilities that support it.

It should be read alongside `docs/prd/master-prd.md`, which is the current master product definition. Where older tier language or legacy scope in surrounding documentation conflicts with the PRD or the split mobile feature docs, the PRD and the active split mobile docs should take precedence.

**Primary user context**: Students in India preparing for defined-syllabus exams
**Platform**: React Native (iOS and Android)
**Document Version**: 1.2

### Current MVP Scope Definition

The MVP delivers a syllabus-driven, AI-supported path-based conceptual exploration experience with:
- curriculum-anchored navigation (class or syllabus level → exam → subject → chapter)
- a bounded mind map for chapter exploration
- AI-generated responses and bounded branching through the two confirmed learner exploration flows
- previous year questions as a supporting exam-preparation resource
- session persistence and basic offline access for continuity, resume, and reopening previously stored session state
- podcast generation from exploration sessions as a reinforcement capability
- path capture, offer-set logging, and internal post-hoc interpretation hooks required for the teacher-support layer

### Scope Boundary Notes

- Learner-facing surfaces must remain category-neutral and must not expose internal analytic labels.
- Teacher-support interpretation remains a separate layer from the learner experience.
- The confirmed mind map interaction rules are fixed for current MVP scope: no Story Node, no node body editing, branching only through phrase selection or the left/right AI-node edge `+`, and AI-generated path edges are distinct from manual reference links.
- Deleting a node in an AI-generated exploration path must also delete its descendant path nodes after confirmation.
- Basic offline access to previously stored session content is part of the current MVP scope for this document, but broader offline capability is not.

### Related Documents

| Document | Purpose |
|----------|---------|
| `docs/prd/master-prd.md` | Current master product definition and scope anchor |
| `docs/teacher-support-mvp-specification.md` | Current teacher-facing MVP surface and minimum access boundary |
| `docs/mobile-features-core-ui.md` | Current authoritative source for node, canvas, and interaction behavior |
| `docs/mobile-features-ai-integration.md` | Current authoritative source for AI branching and question-discovery flows |
| `docs/mobile-features-system.md` | System-level capabilities such as authentication, sync, and persistence |
| `docs/mobile-features-enhancements.md` | Current podcast-generation capability reference |
| `docs/architecture-feature-mapping.md` | Technical implementation mapping |
| `docs/system-architecture.md` | Backend architecture and runtime pipeline |

---

## MVP Feature Groups

| Feature Group | Primary Capability |
|---------------|--------------------|
| **1. Curriculum Navigation** | Syllabus-driven content discovery |
| **2. Dashboard** | Session continuity and quick re-entry |
| **3. Mind Map Canvas** | Bounded exploration surface and manual reference operations |
| **4. AI Exploration Nodes** | AI-generated content and bounded branching |
| **5. Previous Year Questions** | Exam-focused supporting resources |
| **6. Session Persistence, Basic Offline Access & Podcast** | Save and reopen prior exploration state, then generate reinforcement audio |

---

## Feature Group 1: Curriculum Navigation

*Syllabus-driven entry into supported exam content*

### Feature 1.1: Class Selection

| Attribute | Specification |
|-----------|---------------|
| **Description** | Student selects the class or syllabus level relevant to the supported exam set during onboarding |
| **UI Location** | Onboarding → Class picker |
| **Implementation** | React Native Picker → Zustand `setClass()` action |
| **Dependencies** | Curriculum data (Supabase) |
| **Priority Justification** | Foundation for all content filtering; required before any learning |
| **Spec Reference** | `mobile-features-core-ui.md` Section 1.1 |

### Feature 1.2: Target Examination Selection

| Attribute | Specification |
|-----------|---------------|
| **Description** | Student selects the target exam filtered by the chosen class or syllabus level |
| **UI Location** | Onboarding → Exam picker |
| **Implementation** | Filtered list based on class → Zustand `setExam()` |
| **Dependencies** | Class selection (Feature 1.1) |
| **Priority Justification** | Determines subject list and PYQ filtering |
| **Spec Reference** | `mobile-features-core-ui.md` Section 1.1 |

### Feature 1.3: Subject & Chapter Navigation

| Attribute | Specification |
|-----------|---------------|
| **Description** | Browse subjects (card grid) and chapters (scrollable list with progress) |
| **UI Location** | Dashboard → Subjects grid → Chapter list |
| **Implementation** | FlatList with Supabase query, progress from Zustand session history |
| **Dependencies** | Exam selection (Feature 1.2), Session data |
| **Priority Justification** | Core navigation path to learning content |
| **Spec Reference** | `mobile-features-core-ui.md` Section 1.2 |

### Feature 1.4: Chapter Search

| Attribute | Specification |
|-----------|---------------|
| **Description** | Keyword search to filter chapters within a subject |
| **UI Location** | Chapters screen → Search bar |
| **Implementation** | Local filter on FlatList data |
| **Dependencies** | Subject selection |
| **Priority Justification** | Quick access for students with specific topics in mind |
| **Spec Reference** | `mobile-features-core-ui.md` Section 1.2 |

---

## Feature Group 2: Dashboard

*Session continuity and fast re-entry into chapter exploration*

### Feature 2.1: Dashboard Home

| Attribute | Specification |
|-----------|---------------|
| **Description** | Central hub with scrollable feed layout showing learning activity |
| **UI Location** | Bottom nav → "Home" |
| **Implementation** | Custom React Native screen with multiple sections |
| **Dependencies** | Authentication |
| **Priority Justification** | Primary entry point after login |
| **Spec Reference** | `mobile-features-core-ui.md` Section 1.3 |

### Feature 2.2: Continue Learning Card

| Attribute | Specification |
|-----------|---------------|
| **Description** | Shows last active chapter with resume button to restore mind map state |
| **UI Location** | Dashboard → Top section |
| **Implementation** | Load persisted Zustand state from AsyncStorage |
| **Dependencies** | Session persistence (Feature 6.1) |
| **Priority Justification** | Critical for learning continuity; reduces friction to resume |
| **Spec Reference** | `mobile-features-core-ui.md` Section 1.3 |

### Feature 2.3: Recent Sessions List

| Attribute | Specification |
|-----------|---------------|
| **Description** | Last 5 learning sessions with timestamps for quick access |
| **UI Location** | Dashboard → "Recent" section |
| **Implementation** | Query local AsyncStorage session history |
| **Dependencies** | Session data |
| **Priority Justification** | Enables multi-chapter study patterns |
| **Spec Reference** | `mobile-features-core-ui.md` Section 1.3 |

## Feature Group 3: Mind Map Canvas

*Bounded exploration surface for node placement, selection, and reference links*

### Feature 3.1: Canvas Navigation (Pan/Zoom)

| Attribute | Specification |
|-----------|---------------|
| **Description** | Pinch to zoom (25%-400%), one-finger pan with momentum scrolling |
| **UI Location** | Canvas gestures |
| **Implementation** | React Native Gesture Handler → Reanimated SharedValues → Animated.View transform on canvas container |
| **Dependencies** | None |
| **Priority Justification** | Core interaction for exploring mind map |
| **Spec Reference** | `mobile-features-core-ui.md` Section 3.1 |
| **Architecture Reference** | `architecture-feature-mapping.md` Pillar 1 (Hybrid Native Views + Skia Edges) |

### Feature 3.2: Node Creation Access (FAB)

| Attribute | Specification |
|-----------|---------------|
| **Description** | Floating Action Button expands to reveal the manual node-creation actions available in the current build. This is a canvas entry/control surface, not the primary branching mechanism for the AI exploration path. |
| **UI Location** | Bottom right of canvas → "+" icon (56dp) |
| **Implementation** | React Native FAB → Zustand `addNode()` action |
| **Dependencies** | Canvas |
| **Priority Justification** | Primary entry point for manual node creation and initial canvas composition |
| **Spec Reference** | `mobile-features-core-ui.md` Section 5.3 |

### Feature 3.3: Node Selection

| Attribute | Specification |
|-----------|---------------|
| **Description** | Tap to select nodes, reveal the node toolbar, and manage positioning or connections without learner-authored node body editing |
| **UI Location** | Tap node → selection state |
| **Implementation** | Hit testing via Zustand; selection state drives toolbar and node actions |
| **Dependencies** | None |
| **Priority Justification** | Core map interaction |
| **Spec Reference** | `mobile-features-core-ui.md` Section 3.2 |

### Feature 3.4: Node Connections

| Attribute | Specification |
|-----------|---------------|
| **Description** | Create manual reference connections via toolbar action; these links are separate from AI-generated exploration-path edges |
| **UI Location** | Node toolbar → "Connect" → tap target |
| **Implementation** | Zustand `addEdge()` action for manual/reference links, Skia `Path` quadratic Bézier rendering (Skia used for edges only) |
| **Dependencies** | Target node |
| **Priority Justification** | Enables conceptual relationship building |
| **Spec Reference** | `mobile-features-core-ui.md` Section 2.1 |
| **Architecture Reference** | `architecture-feature-mapping.md` Pillar 1 (Edge Rendering) |

**Connection model note**:
- Manual connections are learner-created **reference-style links** between nodes.
- AI-generated parent → child path edges are created only through the two exploration flows (phrase selection and edge `+`) and are a different connection category in the product logic.

---

## Feature Group 4: AI Exploration Nodes

*AI-generated responses with bounded, organic-first question discovery*

Learner-facing branching in the mind map is limited to **two entry points only**:
- phrase selection within AI node content
- edge-attached `+` buttons on the left and right sides of AI nodes

### Feature 4.1: Create AI Node with Prompt

| Attribute | Specification |
|-----------|---------------|
| **Description** | Create the initial AI exploration node for the current chapter or concept entry point, either through a custom prompt or initial prompt options |
| **UI Location** | FAB → "Ask AI" → Prompt input |
| **Implementation** | Zustand `addNode(type: 'ai')`, API call to Claude/OpenAI |
| **Dependencies** | Canvas, AI service, Chapter context |
| **Priority Justification** | Starts the AI exploration flow within the selected chapter context |
| **Spec Reference** | `mobile-features-core-ui.md` Section 2.3 |

### Feature 4.2: Dynamic Content Population

| Attribute | Specification |
|-----------|---------------|
| **Description** | AI-generated answers and explanations populate the node automatically in learner-facing, category-neutral language |
| **UI Location** | Response area within AI node |
| **Implementation** | Streaming response display, auto-formatted markdown |
| **Dependencies** | AI service, Chapter context |
| **Priority Justification** | Delivers the core explanatory content used for exploration |
| **Spec Reference** | `mobile-features-core-ui.md` Section 2.2 |
| **Architecture Reference** | `system-architecture.md` LLM Processing Pipeline |

### Feature 4.3: Phrase Selection for New Questions

| Attribute | Specification |
|-----------|---------------|
| **Description** | Select a word or phrase from AI content to open a bottom sheet with: (1) Elaborate, (2) Ask custom, (3) 3–5 recommended follow-up questions. Any selection creates a child AI node in the exploration path. |
| **UI Location** | AI Node → Reader (selectable text) → Phrase action sheet (bottom sheet) |
| **Implementation** | Phrase selection → generate phrase-conditioned offer set → create child AI node + parent→child AI-generated path edge → generate response using thread context packet → log offer set + selection |
| **Dependencies** | AI service, bottom sheet UI, node/path-edge creation |
| **Priority Justification** | Enables organic exploration flow; core to learning methodology |
| **Spec Reference** | `mobile-features-ai-integration.md` Section 6.5.2 |
| **Architecture Reference** | `system-architecture.md` Stage 1 (Organic generation) + Learning path capture + Phrase selection logging |

**Phrase selection UI behavior**:
- Selecting text must surface a bottom sheet with **fixed top actions** and **3–5 recommended questions**:
  1) **Elaborate on "[selected phrase]"** → immediate node creation
  2) **Ask custom question** → opens input; on submit create node
  3) **Recommended questions** → tap one to create node

**Graph / threading behavior**:
- Each phrase selection creates a **new branch (child node)** from the source node.
- Default structure is **sibling branches** for multiple phrase selections from the same parent.
- The created parent → child link is an **AI-generated path edge**, not a manual reference connection.
- The created child node must persist a `thread_context` reference so subsequent exploration from that node remains grounded in the initiating phrase.
- Deleting a node in an AI-generated exploration path also deletes its descendant path nodes after confirmation.

**Analytics requirements**:
- Log the phrase offer set (actions + recommended questions) and the selection (including “dismissed/no selection”).

### Feature 4.4: Question Discovery Flow

| Attribute | Specification |
|-----------|---------------|
| **Description** | Edge-attached `+` buttons on the left and right sides of an AI node open 3–6 generated follow-up questions; selecting one creates a child AI node connected by an AI-generated path edge |
| **UI Location** | AI Node left/right vertical edge → "+" button → Popup box |
| **Implementation** | Question generation API → edge-triggered popup with tappable cards → new child node + labeled AI-generated path edge + offer-set logging |
| **Dependencies** | AI service, Question generation |
| **Priority Justification** | Core learning loop; guides exploration without forcing paths |
| **Spec Reference** | `mobile-features-ai-integration.md` Section 6.5.1 |

**Question Discovery UI**:
- Edge `+` buttons: 44×44pt touch targets, centered on the left and right vertical edges of the AI node
- Popup box: Small popup near button with 3-6 questions
- Question cards: Tappable, max 2 lines with ellipsis
- Selection creates new AI node with question text in header, AI response in body
- Connected AI-generated path edge links parent → child, labeled with question text

**Analytics requirements**:
- Log the offered question set shown from each edge-triggered launch, including question order/rank.
- Log the learner selection or dismissal/no-selection outcome so the exploration offer set can be reconstructed later.

---

## Feature Group 5: Previous Year Questions

*Exam-focused study resources anchored to chapter context*

### Feature 5.1: PYQ Panel Access

| Attribute | Specification |
|-----------|---------------|
| **Description** | Access previous year questions filtered by exam year and type |
| **UI Location** | Side panel → "Previous Years" tab → Bottom sheet |
| **Implementation** | Bottom sheet with year picker, exam filter, question list |
| **Dependencies** | Chapter context, PYQ database, Curriculum selection |
| **Priority Justification** | Critical for exam-focused users (NEET, JEE, CBSE) |
| **Spec Reference** | `mobile-features-core-ui.md` Section 4.4 |

### Feature 5.2: Add PYQ to Mind Map

| Attribute | Specification |
|-----------|---------------|
| **Description** | Add question from PYQ panel to current mind map as a node |
| **UI Location** | Question detail → "Add to Map" |
| **Implementation** | Zustand `addNode()` with question content |
| **Dependencies** | Canvas, PYQ database |
| **Priority Justification** | Integrates exam prep with exploration learning |
| **Spec Reference** | `mobile-features-core-ui.md` Section 4.4 |

---

## Feature Group 6: Session Persistence, Basic Offline Access & Podcast

*Learning continuity, reopening of previously stored session content, and session-based reinforcement audio*

### Feature 6.1: Session Persistence

| Attribute | Specification |
|-----------|---------------|
| **Description** | Previously loaded mind map state, generated text already received online, and recent exploration context are saved locally so the learner can reopen and resume a session across app restarts, including basic offline access to that previously stored content |
| **UI Location** | Automatic |
| **Implementation** | Zustand `persist` middleware with AsyncStorage |
| **Dependencies** | Secure storage |
| **Priority Justification** | Essential for learning continuity; enables "Continue Learning" |
| **Spec Reference** | `docs/mobile-features-core-ui.md` Section 1.3 and `docs/mobile-features-system.md` (authentication/data persistence context) |
| **Architecture Reference** | `architecture-feature-mapping.md` Section 3 (Zustand) |

**Scope clarification**: This feature includes basic offline access to previously stored session state and content already generated online. It should not be read as support for new AI generation while offline, offline editing beyond that persisted state, offline sync/queued sync behavior, offline video behavior, downloaded media or podcast offline playback, or a broader offline product mode.

### Feature 6.2: Generate Exploration Podcast

| Attribute | Specification |
|-----------|---------------|
| **Description** | Transform an exploration session into a personalized reinforcement podcast generated from the learner's explored path and session context |
| **UI Location** | Board menu → "Create Podcast" → Full-screen podcast wizard/player |
| **Implementation** | AI script generation from session/path data → TTS service → audio playback |
| **Dependencies** | AI service, TTS service, Session data |
| **Priority Justification** | Confirmed MVP reinforcement feature derived from the learner's exploration session |
| **Spec Reference** | `docs/mobile-features-enhancements.md` Section 9.1.1 |

**Podcast flow (MVP)**:
1. Open podcast generation from the current board/session.
2. Choose podcast length.
3. Preview the generated script.
4. Generate audio and listen in the built-in player.

## Suggested implementation order (non-binding)

The following implementation sequence respects architectural dependencies.

**Note**: Any "Phase" or week labels from older planning should be treated as non-binding. Use the sequence below as a dependency suggestion, not a timeline commitment.

### Foundation

| Order | Feature | Rationale |
|-------|---------|-----------|
| 1 | Canvas Navigation (3.1) | Core rendering infrastructure |
| 2 | Node Creation Access (3.2) | Manual node entry and canvas controls |
| 3 | Node Selection & Management (3.3) | Core node interaction |
| 4 | Session Persistence (6.1) | State management foundation |

### Curriculum

| Order | Feature | Rationale |
|-------|---------|-----------|
| 5 | Class Selection (1.1) | Curriculum foundation |
| 6 | Exam Selection (1.2) | Content filtering |
| 7 | Subject & Chapter Navigation (1.3) | Content discovery |
| 8 | Dashboard Home (2.1) | Entry point |

### AI integration

| Order | Feature | Rationale |
|-------|---------|-----------|
| 9 | Create AI Node (4.1) | LLM integration |
| 10 | Dynamic Content Population (4.2) | Response handling |
| 11 | Phrase Selection (4.3) | Exploration flow |
| 12 | Question Discovery Flow (4.4) | Core learning loop |

### Supporting capabilities

| Order | Feature | Rationale |
|-------|---------|-----------|
| 13 | Node Connections (3.4) | Relationship building |
| 14 | Continue Learning (2.2) | Session continuity |
| 15 | Recent Sessions (2.3) | Quick access |
| 16 | PYQ Panel (5.1) | Exam prep resource access |
| 17 | Add PYQ to Map (5.2) | Chapter-context integration |
| 18 | Chapter Search (1.4) | Faster navigation |
| 19 | Generate Exploration Podcast (6.2) | Reinforcement and review from session history |

---

## Feature Dependencies

| Dependency | Enables |
|------------|---------|
| Authentication and app session | Dashboard access, saved progress, and user-specific persistence |
| Curriculum selection | Subject/chapter navigation, chapter context, and PYQ filtering |
| Canvas infrastructure | Node selection, manual reference links, and AI-node rendering |
| Initial AI node creation | Phrase-selection flow and edge `+` question discovery |
| Session persistence + session/path data | Continue Learning, Recent Sessions, and podcast generation |
| AI + TTS services | AI exploration content and podcast generation |
| Offer-set logging + path capture | Downstream teacher-support interpretation and measurement |

### Critical Path

1. **Authentication** → Required for all user-specific features
2. **Curriculum Selection** → Required for content filtering
3. **Canvas Infrastructure** → Required for all node features
4. **Session Persistence** → Required for Continue Learning and podcast inputs
5. **AI Service Integration** → Required for AI node creation, phrase branching, question discovery, and podcast script generation
6. **TTS Service Integration** → Required for podcast audio generation

**Product-level dependency note**: A basic teacher view is in MVP at the product level. Its bounded teacher-facing surface and minimum access model are defined in `docs/teacher-support-mvp-specification.md`. What *is* required here is the learner-path and offer-set data capture that the teacher-support layer depends on.

---

## Success Criteria for MVP Launch

### Functional Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Core learner flow complete | Curriculum selection → Chapter exploration → Resume | End-to-end |
| Both branching flows functional | Phrase selection + edge `+` flows | Working in production path |
| Path-edge vs manual-link rules implemented | Deletion, rendering, and edge-type behavior | Correct |
| Session persistence reliability | Data loss incidents | 0 |
| Podcast generation flow functional | Session → script → playable audio | End-to-end |
| Offer-set logging present for exploration flows | Logged offer-set + selection events | 100% of phrase/edge launches |

### Performance Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| App launch time | Cold start to dashboard | <3 seconds |
| Canvas frame rate | FPS during pan/zoom | 60fps |
| AI response time | Query to first token | <2 seconds |
| Memory footprint | Peak RAM usage | <150MB |

### Device Compatibility

| Criterion | Specification | Source |
|-----------|---------------|--------|
| Minimum Android | Android 11 (API 30) | Market research |
| Minimum RAM | 4GB | Market research |
| Minimum screen | 6.5" HD+ (720×1600) | Market research |
| Minimum storage | 32GB (8GB available) | Market research |

*See `docs/research/indian-student-market-analysis.md` for detailed rationale*

### User Experience Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Curriculum setup completion | % completing initial syllabus/exam setup | >90% |
| First exploration session depth | Questions selected / child nodes created in first chapter session | >5 |
| Same-chapter return rate | % returning to the same chapter for a second session | >40% |
| Offer-set engagement | % of shown phrase/edge offer sets that lead to a selection | Track and improve |

---

## Known Scope Notes

- **Teacher-support MVP surface**: The product-level MVP includes a basic teacher view, with the current high-level teacher-facing boundary defined in `docs/teacher-support-mvp-specification.md`. This file remains primarily the learner/mobile exploration scope plus the shared data-capture requirements that support teacher interpretation.
- **Offline scope alignment**: Current MVP includes basic offline access to previously loaded session state and content already generated online so learners can reopen and resume later. Broader offline capability remains out of MVP for this document and should not be inferred from this narrow behavior.
- **Image-node scope detail**: Image nodes are **in MVP** as supporting learning media. The minimum MVP surface is standalone image-node creation/import, viewing, manual reference linking, and deletion.
- **Image-node capability-tier clarification**: In the split mobile docs, image-specific enrichment such as contextual image search, OCR, or AI description may remain labeled **Advanced**. That label means enhancement-tier capability, not post-MVP status for image nodes themselves.

---

## Technical Stack Summary

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Rendering** | Hybrid: RN Animated.View (nodes) + Skia (edges) | 60fps canvas rendering; native Views for nodes, Skia for Bézier edge curves |
| **Layout** | D3-Force | Physics-based node positioning |
| **State (Canonical)** | Zustand | Permanent data (nodes, edges) |
| **State (Transient)** | Reanimated SharedValues | 60fps UI updates |
| **Gestures** | React Native Gesture Handler | UI-thread gesture processing |
| **Persistence** | AsyncStorage | Local session storage |
| **Backend** | Supabase (PostgreSQL) | User data, curriculum, PYQ |
| **AI** | Claude/OpenAI API | Content generation |
| **TTS** | Platform TTS / AI voice service | Podcast audio generation |

---

*Document Version 1.2 | MVP Features Specification*
*Platform: Path-Based Conceptual Exploration and Teacher-Support System*
*Referenced by: Mobile Feature Specification (see `docs/mobile-features-index.md` for navigation)*
