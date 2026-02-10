# Basic Features Specification

## Executive Summary

This document consolidates the **20 core Basic features** for the Categorical Exploration Learning Platform mobile application. It serves as a focused reference for Basic tier scope, separate from the comprehensive mobile feature specification (see `docs/mobile-features-index.md` for navigation to split files) which includes Advanced tier features.

**Target Demographic**: Indian students (ages 14-18) preparing for CBSE, ICSE, NEET, and JEE examinations
**Platform**: React Native (iOS and Android)
**Document Version**: 1.0

### Basic Scope Definition

The Basic tier delivers a **syllabus-driven, AI-powered mind map learning experience** with:
- Curriculum-anchored navigation (Class → Exam → Subject → Chapter)
- Interactive mind map canvas with dynamic AI content generation
- Previous year questions integration
- Session persistence for learning continuity
- Core podcast generation from exploration sessions
- Offline capability for rural connectivity gaps

### Related Documents

| Document | Purpose |
|----------|---------|
| `docs/mobile-features-index.md` | Master index for mobile feature specification (split into 4 files) |
| `docs/architecture-feature-mapping.md` | Technical implementation mapping |
| `docs/system-architecture.md` | Backend architecture and LLM pipeline |
| `docs/research/indian-student-market-analysis.md` | Device targets and offline rationale |

---

## Basic Feature Categories

| Category | Feature Count | Core Capability |
|----------|---------------|-----------------|
| **1. Curriculum Navigation** | 4 features | Syllabus-driven content discovery |
| **2. Dashboard** | 4 features | Session continuity and quick access |
| **3. Mind Map Canvas** | 4 features | Interactive visual learning |
| **4. AI Node (Dynamic Content)** | 4 features | LLM-powered content generation |
| **5. Previous Year Questions** | 2 features | Exam-focused study resources |
| **6. Podcast Generation** | 2 features | Audio learning from exploration |
| **Total** | **20 features** | |

---

## Category 1: Curriculum Navigation

*Syllabus-driven content anchoring for Indian exam preparation*

### Feature 1.1: Class Selection

| Attribute | Specification |
|-----------|---------------|
| **Description** | Student selects their class level (Class 6-12) during onboarding |
| **UI Location** | Onboarding → Class picker |
| **Implementation** | React Native Picker → Zustand `setClass()` action |
| **Dependencies** | Curriculum data (Supabase) |
| **Priority Justification** | Foundation for all content filtering; required before any learning |
| **Spec Reference** | `mobile-features-core-ui.md` Section 1.1 |

### Feature 1.2: Target Examination Selection

| Attribute | Specification |
|-----------|---------------|
| **Description** | Student selects target exam (CBSE, ICSE, State Boards, NEET, JEE) filtered by class |
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

## Category 2: Dashboard

*Session continuity and learning engagement*

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

## Category 3: Mind Map Canvas

*Interactive visual learning with physics-based layout*

### Feature 3.1: Canvas Navigation (Pan/Zoom)

| Attribute | Specification |
|-----------|---------------|
| **Description** | Pinch to zoom (25%-400%), one-finger pan with momentum scrolling |
| **UI Location** | Canvas gestures |
| **Implementation** | React Native Gesture Handler → Reanimated SharedValues → Skia transform matrix |
| **Dependencies** | None |
| **Priority Justification** | Core interaction for exploring mind map |
| **Spec Reference** | `mobile-features-core-ui.md` Section 3.1 |
| **Architecture Reference** | `architecture-feature-mapping.md` Pillar 1 (Skia) |

### Feature 3.2: Node Creation (FAB)

| Attribute | Specification |
|-----------|---------------|
| **Description** | Floating Action Button expands to reveal 4 node types (Text, Story, AI, Video) |
| **UI Location** | Bottom right of canvas → "+" icon (56dp) |
| **Implementation** | React Native FAB → Zustand `addNode()` action |
| **Dependencies** | Canvas |
| **Priority Justification** | Primary content creation mechanism |
| **Spec Reference** | `mobile-features-core-ui.md` Section 5.3 |

### Feature 3.3: Node Selection & Editing

| Attribute | Specification |
|-----------|---------------|
| **Description** | Tap to select (shows border + toolbar), edit content inline or full-screen |
| **UI Location** | Tap node → selection state |
| **Implementation** | Hit testing via Zustand, overlay React Native TextInput for editing |
| **Dependencies** | None |
| **Priority Justification** | Core content manipulation |
| **Spec Reference** | `mobile-features-core-ui.md` Section 2.1 |

### Feature 3.4: Node Connections

| Attribute | Specification |
|-----------|---------------|
| **Description** | Connect nodes via toolbar action; visual connection line preview |
| **UI Location** | Node toolbar → "Connect" → tap target |
| **Implementation** | Zustand `addEdge()` action, Skia quadratic Bézier rendering |
| **Dependencies** | Target node |
| **Priority Justification** | Enables conceptual relationship building |
| **Spec Reference** | `mobile-features-core-ui.md` Section 2.1 |
| **Architecture Reference** | `architecture-feature-mapping.md` Pillar 1 (Edge Rendering) |

---

## Category 4: AI Node (Dynamic Content)

*LLM-powered content generation with organic question discovery*

### Feature 4.1: Create AI Node with Prompt

| Attribute | Specification |
|-----------|---------------|
| **Description** | Create AI node via FAB, enter custom prompt or select initial prompt options |
| **UI Location** | FAB → "Ask AI" → Prompt input |
| **Implementation** | Zustand `addNode(type: 'ai')`, API call to Claude/OpenAI |
| **Dependencies** | Canvas, AI service, Chapter context |
| **Priority Justification** | Core learning mechanism; enables curiosity-driven exploration |
| **Spec Reference** | `mobile-features-core-ui.md` Section 2.3 |

### Feature 4.2: Dynamic Content Population

| Attribute | Specification |
|-----------|---------------|
| **Description** | AI-generated answers and explanations populate node automatically |
| **UI Location** | Response area within AI node |
| **Implementation** | Streaming response display, auto-formatted markdown |
| **Dependencies** | AI service, Chapter context |
| **Priority Justification** | Delivers personalized learning content |
| **Spec Reference** | `mobile-features-core-ui.md` Section 2.3 |
| **Architecture Reference** | `system-architecture.md` LLM Processing Pipeline |

### Feature 4.3: Phrase Selection for New Questions

| Attribute | Specification |
|-----------|---------------|
| **Description** | Select a word/phrase from AI content to open a bottom sheet with: (1) Elaborate, (2) Ask custom, (3) 3–5 recommended follow-up questions; selection creates a child AI node |
| **UI Location** | AI Node → Reader (selectable text) → Phrase action sheet (bottom sheet) |
| **Implementation** | Phrase selection → generate phrase-conditioned offer set → create child AI node + parent→child edge → generate response using thread context packet → log offer set + selection |
| **Dependencies** | AI service, bottom sheet UI, node/edge creation |
| **Priority Justification** | Enables organic exploration flow; core to learning methodology |
| **Spec Reference** | `mobile-features-core-ui.md` Section 2.3 |
| **Architecture Reference** | `system-architecture.md` Stage 1 (Organic generation) + Learning path capture + Phrase selection logging |

**Basic UI behavior**:
- Selecting text must surface a bottom sheet with **fixed top actions** and **3–5 recommended questions**:
  1) **Elaborate on "[selected phrase]"** → immediate node creation
  2) **Ask custom question** → opens input; on submit create node
  3) **Recommended questions** → tap one to create node

**Graph / threading behavior**:
- Each phrase selection creates a **new branch (child node)** from the source node.
- Default structure is **sibling branches** for multiple phrase selections from the same parent.
- The created child node must persist a `thread_context` reference so subsequent exploration from that node remains grounded in the initiating phrase.

**Analytics requirements**:
- Log the phrase offer set (actions + recommended questions) and the selection (including “dismissed/no selection”).

### Feature 4.4: Question Discovery Flow

| Attribute | Specification |
|-----------|---------------|
| **Description** | Explore button on AI node opens popup box with 3-6 generated questions; selected question appears in new node header with AI response in body |
| **UI Location** | AI Node center of right edge → "+" button → Popup box |
| **Implementation** | Question generation API → Popup box with tappable cards → New node with question header |
| **Dependencies** | AI service, Question generation |
| **Priority Justification** | Core learning loop; guides exploration without forcing paths |
| **Spec Reference** | `mobile-features-ai-integration.md` Section 6.5.1 |

**Question Discovery UI**:
- Explore button: 44×44pt touch target, center of right edge of AI node
- Popup box: Small popup near button with 3-6 questions
- Question cards: Tappable, max 2 lines with ellipsis
- Selection creates new AI node with question text in header, AI response in body
- Permanent edge connects parent → child, labeled with question text

---

## Category 5: Previous Year Questions

*Exam-focused study resources anchored to curriculum*

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

## Category 6: Session Persistence & Podcast

*Learning continuity and audio content generation*

### Feature 6.1: Session Persistence

| Attribute | Specification |
|-----------|---------------|
| **Description** | Mind map state saved locally for resume across app restarts |
| **UI Location** | Automatic |
| **Implementation** | Zustand `persist` middleware with AsyncStorage |
| **Dependencies** | Secure storage |
| **Priority Justification** | Essential for learning continuity; enables "Continue Learning" |
| **Spec Reference** | `mobile-features-system.md` Section 7.1 |
| **Architecture Reference** | `architecture-feature-mapping.md` Section 3 (Zustand) |

### Feature 6.2: Generate Exploration Podcast

| Attribute | Specification |
|-----------|---------------|
| **Description** | Transform exploration session into personalized reinforcement audio podcast (path-optimized; may be non-linear) |
| **UI Location** | Board menu → "Create Podcast" → Full-screen wizard |
| **Implementation** | AI script generation → TTS service → Audio player |
| **Dependencies** | AI service, TTS service, Session data |
| **Priority Justification** | Differentiated learning experience; audio learning for commute/revision |
| **Spec Reference** | `mobile-features-enhancements.md` Section 9.1.1 |

**Podcast Generation Flow**:
1. Select length: Short (3-5 min), Medium (8-12 min), Long (15-20 min)
2. Preview/edit AI-generated script
3. Generate audio with progress indicator
4. Listen with standard audio controls, background playback

## Suggested implementation order (non-binding)

The following implementation sequence respects architectural dependencies.

**Note**: Any "Phase" / week labels should be treated as **non-binding**. Use this as a dependency/sequence suggestion, not a timeline commitment.

### Foundation

| Order | Feature | Rationale |
|-------|---------|-----------|
| 1 | Canvas Navigation (3.1) | Core rendering infrastructure |
| 2 | Node Creation (3.2) | Basic content creation |
| 3 | Node Selection & Editing (3.3) | Content manipulation |
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

### Features & polish

| Order | Feature | Rationale |
|-------|---------|-----------|
| 13 | Node Connections (3.4) | Relationship building |
| 14 | Continue Learning (2.2) | Session continuity |
| 15 | Recent Sessions (2.3) | Quick access |
| 16 | Daily Streak (2.4) | Engagement |
| 17 | PYQ Panel (5.1) | Exam prep |
| 18 | Add PYQ to Map (5.2) | Integration |
| 19 | Chapter Search (1.4) | Navigation |
| 20 | Podcast Generation (6.2) | Audio learning |

---

## Feature Dependencies

```
┌─────────────────────────────────────────────────────────────────────────┐
│  DEPENDENCY GRAPH                                                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  [Authentication] ──────────────────────────────────────────────────┐   │
│        │                                                             │   │
│        ▼                                                             │   │
│  [Class Selection] ──► [Exam Selection] ──► [Subject/Chapter Nav]   │   │
│        │                      │                      │               │   │
│        │                      ▼                      ▼               │   │
│        │              [PYQ Panel] ◄──────── [Chapter Context]        │   │
│        │                                            │                │   │
│        ▼                                            ▼                │   │
│  [Dashboard Home] ◄─────────────────────── [Session Persistence]     │   │
│        │                                            │                │   │
│        ▼                                            ▼                │   │
│  [Continue Learning] ◄──────────────────── [Mind Map State]         │   │
│        │                                            │                │   │
│        │                                            ▼                │   │
│        │                                    [Canvas + Nodes]         │   │
│        │                                            │                │   │
│        │                                            ▼                │   │
│        │                                    [AI Node + Questions]    │   │
│        │                                            │                │   │
│        │                                            ▼                │   │
│        └──────────────────────────────────► [Podcast Generation]     │   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Critical Path

1. **Authentication** → Required for all user-specific features
2. **Curriculum Selection** → Required for content filtering
3. **Canvas Infrastructure** → Required for all node features
4. **Session Persistence** → Required for Continue Learning
5. **AI Service Integration** → Required for AI Node and Podcast

---

## Success Criteria for Basic Tier Launch

### Functional Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| All 20 features implemented | Feature checklist | 100% |
| Core user flow complete | Onboarding → Learning → Resume | End-to-end |
| AI response quality | User satisfaction survey | >4.0/5.0 |
| Session persistence reliability | Data loss incidents | 0 |
| Offline mode functional | Cached board access | Works without network |

### Performance Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| App launch time | Cold start to dashboard | <3 seconds |
| Canvas frame rate | FPS during pan/zoom | 60fps |
| AI response time | Query to first token | <2 seconds |
| Memory footprint | Peak RAM usage | <150MB |
| Offline cache size | Per-board storage | <5MB |

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
| Onboarding completion | % completing curriculum setup | >90% |
| First session depth | Nodes created in first session | >5 |
| Return rate (Day 1) | % returning within 24 hours | >50% |
| Session duration | Average time per session | >10 minutes |

---

## Technical Stack Summary

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Rendering** | React Native Skia | 60fps canvas rendering |
| **Layout** | D3-Force | Physics-based node positioning |
| **State (Canonical)** | Zustand | Permanent data (nodes, edges) |
| **State (Transient)** | Reanimated SharedValues | 60fps UI updates |
| **Gestures** | React Native Gesture Handler | UI-thread gesture processing |
| **Persistence** | AsyncStorage | Local session storage |
| **Backend** | Supabase (PostgreSQL) | User data, curriculum, PYQ |
| **AI** | Claude/OpenAI API | Content generation |
| **TTS** | Platform TTS / AI voice | Podcast audio |

---

*Document Version 1.0 | Basic Features Specification*
*Platform: Categorical Exploration Learning Platform*
*Referenced by: Mobile Feature Specification (see `docs/mobile-features-index.md` for navigation)*
