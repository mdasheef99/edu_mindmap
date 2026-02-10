# Mobile Features: AI Integration

## Document Overview

This document specifies all AI-powered capabilities for the mobile application, including node-level AI actions, the dedicated AI assistant panel, learning-specific features, and Perplexity Sonar integration.

**Part of**: Mobile Feature Specification (split for AI agent optimization)
**Related files**:
- [Core UI Components](mobile-features-core-ui.md) - Curriculum, nodes, canvas, panels, navigation
- [System Features](mobile-features-system.md) - Authentication, sync, offline mode
- [Enhancements & Summaries](mobile-features-enhancements.md) - Feature priorities and recommendations
- [Master Index](mobile-features-index.md) - Complete navigation guide

**Priority / tier labels (non-binding)**:
Treat all priority labels as **capability tiers**, not timeline commitments.

- **Basic**: Essential for the first usable release of the mobile app.
- **Advanced**: Enhancement features beyond the core experience.
- **Teacher**: Teacher/admin-only capabilities (not student-facing).
- **Exclude**: Not suitable for mobile or deferred indefinitely.

**Design Principles**:
- **Organic-First**: Students explore naturally; system observes invisibly
- **Syllabus-Driven**: All content anchored to curriculum (Class, Exam, Subject, Chapter)
- **Curiosity-Driven**: Exploration guided by student interest, not forced paths
- **Category Invisibility**: Kantian diagnostic categories never visible to students

---

## 6. AI Integration Features

All AI-powered capabilities organized by access point.

### 6.1 Node Toolbar AI Actions

*AI features accessible from individual node toolbars*

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Summarize content | Node toolbar → "AI" → "Summarize" | Basic | Generates concise summary | AI service, node content |
| Expand content | Node toolbar → "AI" → "Expand" | Advanced | Adds detail to existing content | AI service, node content |
| Break down into topics | Node toolbar → "AI" → "Breakdown" | Basic | Creates child nodes for subtopics | AI service, node content |
| Generate questions | Node toolbar → "AI" → "Questions" | Basic | Creates learning questions (core platform feature) | AI service, node content |
| Explain simply | Node toolbar → "AI" → "Simplify" | Advanced | Rewrites at lower complexity | AI service, node content |
| Translate content | Node toolbar → "AI" → "Translate" | Advanced | Translates to selected language | AI service, node content |
| Generate caption (for images) | Image node toolbar → "AI" → "Caption" | Advanced | Describes image content | AI service, image |

### 6.2 Dedicated AI Panel ("Ask")

*Standalone AI assistant interface*

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Open AI panel | Bottom nav → "AI" tab | Basic | Full-screen chat interface | AI service |
| Text input | AI panel → input field | Basic | Expandable, voice input button | AI service |
| Voice input | AI panel → microphone icon | Advanced | Speech-to-text conversion | Microphone permission |
| Send message | AI panel → send button | Basic | Keyboard submit also works | AI service |
| View conversation history | AI panel → scrollable chat | Basic | Message bubbles with timestamps | AI service |
| Clear conversation | AI panel → "New Chat" | Basic | Starts fresh context | AI service |
| Copy AI response | Long-press message → "Copy" | Basic | Copies to clipboard | None |
| Convert response to node | AI response → "Add to Board" | Basic | Creates node from AI content | Current board |
| Suggested prompts | AI panel → prompt chips | Advanced | Context-aware suggestions | AI service |
| Conversation context | Automatic | Basic | Maintains context within session | AI service |

### 6.3 Context Menu AI Actions

*Quick AI operations from context menus*

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Quick summarize | Long-press node → "Summarize" | Advanced | One-tap summary generation | AI service, node |
| Quick questions | Long-press node → "Generate Questions" | Advanced | Generates 3 questions | AI service, node |
| Explain selection | Select text → "Explain" | Advanced | Explains highlighted text | AI service, text selection |

### 6.4 AI-Powered Search

*AI-enhanced search functionality*

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Semantic search | Search bar → natural language query | Advanced | Finds conceptually related content | AI service, indexed content |
| Search within board | Board → search icon | Basic | Keyword search (non-AI) | Current board |
| Search across boards | Bottom sheet → search | Advanced | Searches all user boards | Authentication |
| AI search suggestions | Search bar → suggestions | Advanced | AI-generated query completions | AI service |

### 6.5 Learning-Specific AI Features

*AI features aligned with Kantian categorical learning framework*

> **Note: Category Framework Visibility**
> The 8 Kantian categorical dimensions (Define, Distinguish, Decompose, Connect, Delimit, Predict, Contextualize, Vary) are used for **diagnostic purposes only** and are **never visible to students**. Students explore naturally; the system observes and classifies invisibly. Category visibility is reserved for the Teacher Dashboard only.

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Generate organic questions | Automatic (invisible) | Basic | Questions emerge from exploration context | AI service, chapter context |
| Post-hoc classification | Backend (invisible to user) | Basic | Classifies questions into 8 categories invisibly | AI service |
| Suggest next questions | AI panel → "What should I explore?" | Basic | Based on current exploration path | AI service, session context |
| Knowledge gap hints | AI panel → subtle natural language prompts | Advanced | Uses phrases like "Try asking 'what if...'" with NO category labels | AI service, diagnostic data |
| Quiz generation | Node toolbar → "Quiz Me" | Advanced | Creates self-assessment questions | AI service, node content |


#### 6.5.1 Question Discovery Flow

*Core learning loop: How students discover and select follow-up questions*

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Explore button | AI Node → center of right edge → "+" circular button | Basic | 44×44pt touch target, appears after AI response loads | AI Node |
| Open question popup | Tap "+" button | Basic | Opens small popup box near the button displaying 3-6 questions | Question generation |
| View generated questions | Popup box → question list | Basic | Each question is a tappable card with preview text | AI service |
| Select question to explore | Tap question card | Basic | Creates new AI Node (question as header, AI response as body), closes popup | Canvas, AI service |
| Dismiss question popup | Tap outside popup | Basic | Returns to canvas without selection | None |
| Refresh questions | Popup box → "Show different questions" | Advanced | Generates new set of organic questions | AI service |
| Question loading state | Popup box → skeleton cards | Basic | Shows 3 placeholder cards while generating | None |

**Question Discovery Flow — Detailed Specification**:

**Explore Button**:
- Position: Center of the right edge of each AI Node (not floating, not in a toolbar)
- Appears after AI response loads in the node
- Visual design details: *Deferred — to be discussed later*

**Popup Box Behavior**:
- Trigger: Tap the "+" explore button
- Content: 3-6 generated questions displayed as tappable cards
- Dismissal: Tap outside the popup box
- Persistence: Popup closes automatically when a question is selected
- Visual design details: *Deferred — to be discussed later*

**New Node Creation (on question selection)**:
1. A new AI Node is created as a **child** of the current node
2. The **selected question text** is displayed in the new node's **header**
3. The AI-generated **response** to that question appears in the node **body** below the header
4. A **permanent edge** connects parent node → child node
5. The edge is labeled with the selected question text

**Question Generation Context**:
- Questions in the popup are generated by the LLM based on:
  - The **current node's content** (AI response text being viewed)
  - **Exploration context** (parent node chain, sibling nodes, chapter/subject)
  - **Thread context** from previous selections in the exploration path
- Generation follows **organic-first** principles: no category labels, no framework references, no forced coverage

**Multi-threading and Node Connections**:
- **Multiple child nodes** can branch from a single parent node (multi-threading)
- Each branch represents a **different exploration thread**
- Connections between nodes are **permanent once created** — they cannot be removed
- The **connection context** (parent content + edge label + sibling context) is used to inform subsequent question generation in child nodes
- This creates a growing mind map that visually represents the student's exploration path

#### 6.5.2 Phrase/Word Selection Exploration Flow (Basic)

*Learner-driven micro-exploration anchored to a highlighted phrase; integrates with the same node-creation pipeline as Question Discovery.*

**Trigger surface (implementation note)**:
- The Skia canvas renders text as graphics and does **not** provide native OS text selection.
- Basic tier uses a **Reader bottom sheet** (React Native text surface) to enable word/phrase highlighting.
- Implementation detail: showing highlight handles is easy (`selectable` text), but **capturing the exact selected substring** for downstream generation typically requires a surface that exposes selection range callbacks (e.g., a read-only multiline `TextInput` with `onSelectionChange`, or a purpose-built selectable-text component).

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Open Reader (selectable text) | AI Node → long-press response → "Read / Select text" | Basic | Full response in scrollable reader | Bottom sheet |
| Select phrase/word | Reader → native highlight gesture | Basic | Uses platform selection handles | React Native text surface |
| Open phrase action sheet | After selection | Basic | Bottom sheet with fixed top actions + 3–5 recommended questions | AI service |
| 1) Elaborate on "[phrase]" | Phrase action sheet (top slot) | Basic | One tap, no extra input | AI service |
| 2) Ask custom question | Phrase action sheet (second slot) | Basic | Opens text input with phrase pre-filled as context | AI service |
| 3) Recommended follow-up questions | Phrase action sheet (remaining slots) | Basic | 3–5 tappable cards | AI service |
| Create child AI node + edge | On any selection | Basic | Parent → child edge label = phrase or chosen question | Canvas |

**Node/edge creation rules (Basic)**:
1. Create a new AI node as a **child of the currently selected node** (the node whose content contained the phrase).
2. Create an edge `parent → child` labeled with:
   - the selected phrase (for Elaborate / Custom), or
   - the selected recommended question text (for Recommended).
3. Generate the child node's response using a **thread context packet** (see Context Propagation).

**Context Propagation (threading)**:
- The child node must store a durable `thread_context` reference so that **future question generation from that child** is grounded in the initiating phrase.
- Minimum context packet inputs:
  - `selected_phrase`
  - `source_excerpt` (local window around phrase)
  - `parent_node_summary`
  - `neighborhood_summaries` (recent/connected nodes)
  - `chapter/subject header`

**Recommended question generation constraints**:
- Must remain **organic-first** (no category labels, no framework references, no forced "cover all angles").
- Output 3–5 questions specifically conditioned on the phrase-in-context.

**Analytics / logging requirements**:
- Log **offer set impression** when the phrase action sheet is shown:
  - includes the top 2 actions (Elaborate, Ask custom) + the 3–5 recommended questions (with rank/order).
- Log the **selection** (which action/question was chosen) and the resulting `child_node_id`.
- Join keys: `phrase_selection_id`, `phrase_offer_set_id`, `parent_node_id`, `child_node_id`, `session_id`, `chapter_id`.

### 6.6 Perplexity Sonar Integration

*Contextual multimedia search and enrichment*

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Contextual image search | Image picker → "Search" tab | Advanced | Searches based on current node/exploration context | Perplexity API, network |
| Contextual video search | Video node → "Search" → "Related" | Advanced | Finds videos related to exploration context | Perplexity API, network |
| Media metadata extraction | Automatic on media selection | Advanced | Extracts descriptions, tags, context from Sonar API | Perplexity API |
| Media-enhanced AI responses | Automatic (invisible) | Advanced | Uses media context to enrich AI summarization | AI service, Perplexity API |
| Search result caching | Automatic | Advanced | Caches recent search results for 24 hours | Local storage |
| Fallback to standard search | Automatic on API failure | Advanced | Falls back to YouTube/image gallery if Sonar unavailable | Network |

**Perplexity Sonar Integration Specification**:

| Component | Specification |
|-----------|---------------|
| API Endpoint | Perplexity Sonar API (images, videos, web content) |
| Search Trigger | User initiates search OR system suggests based on exploration context |
| Context Passed | Current node content, connected nodes, chapter topic, recent questions |
| Result Presentation | Grid view for images (2 columns), list view for videos (thumbnail + title) |
| Caching Strategy | Cache search results for 24 hours; cache selected media metadata permanently |
| Rate Limiting | Max 10 searches per minute per user; queue excess requests |
| Error Handling | Show cached results if available; fallback to YouTube/gallery; show error toast |
