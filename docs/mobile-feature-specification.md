# Mobile Application Feature Specification

## Document Overview

This document provides the authoritative specification of all features for the mobile application version of the Categorical Exploration Learning Platform. Features are organized by UI layer and component type, with priority levels and mobile adaptation notes.

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
- **Category Invisibility**: Diagnostic categories never visible to students

---

## 1. Curriculum & Syllabus Navigation

Features for navigating the educational curriculum hierarchy.

### 1.1 Curriculum Selection

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Select Class | Onboarding → Class picker | Basic | Scrollable list (Class 6-12) | Curriculum data |
| Select Target Examination | Onboarding → Exam picker | Basic | Filtered by class (CBSE, ICSE, State Boards, NEET, JEE, etc.) | Class selection |
| Save curriculum preference | Automatic on selection | Basic | Persisted to user profile | Authentication |
| Change curriculum | Settings → "My Curriculum" | Basic | Re-triggers selection flow | User profile |
| Multi-exam support | Settings → "Add Examination" | Advanced | Track multiple exam preparations | User profile |

### 1.2 Subject & Chapter Navigation

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| View subjects list | Dashboard → Subjects grid | Basic | Card grid (2 columns) with icons | Curriculum selection |
| Filter subjects by exam | Automatic based on exam | Basic | Only shows relevant subjects | Exam selection |
| View chapters list | Subject → Chapters list | Basic | Scrollable list with progress indicators | Subject selection |
| Chapter search | Chapters screen → Search bar | Basic | Filters chapters by keyword | Subject selection |
| Chapter progress indicator | Chapter card → Progress ring | Basic | Shows exploration coverage percentage | Session data |
| Mark chapter complete | Chapter card → "Mark Complete" | Advanced | Manual completion flag | Chapter data |
| Chapter difficulty indicator | Chapter card → Difficulty badge | Advanced | Easy/Medium/Hard based on content | Chapter metadata |

### 1.3 Dashboard

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Dashboard home | Bottom nav → "Home" | Basic | Scrollable feed layout | Authentication |
| Continue learning card | Dashboard → Top section | Basic | Shows last active chapter with resume button | Session persistence |
| ~~Browse new topic~~ | ~~Dashboard → "Explore" section~~ | Deferred | *(Deferred — to be discussed later)* | Curriculum data |
| Recent sessions list | Dashboard → "Recent" section | Basic | Last 5 sessions with timestamps | Session data |
| Daily learning streak | Dashboard → Streak counter | Basic | Days of consecutive activity | Analytics |
| Recommended chapters | Dashboard → "For You" section | Advanced | AI-suggested based on progress gaps | AI service, analytics |
| Exam countdown | Dashboard → Exam card | Advanced | Days remaining to selected exam | Exam dates |

---

## 2. Node-Level Features

Features that apply to individual nodes within the mind map canvas.

### 2.1 Text Node

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Create text node | FAB → "Add Text" | Basic | Single tap placement | Canvas |
| Edit text content | Tap node → inline edit | Basic | Full-screen editor on small screens | None |
| Change node color | Node toolbar → Color picker | Basic | 8-color palette (reduced from 16) | None |
| Copy/duplicate node | Node toolbar → "More" menu | Basic | Creates node offset by 20px | None |
| Delete node | Long-press → "Delete" or swipe left | Basic | Confirmation dialog | None |
| Connect to other node | Node toolbar → "Connect" → tap target | Basic | Visual connection line preview | Target node |
| Resize node | Drag corner handles | Advanced | 2 handles only (top-right, bottom-left) | None |
| AI summarize content | Node toolbar → "AI" → "Summarize" | Basic | Shows loading indicator | AI service |
| Audio narration | Node toolbar → "More" → "Listen" | Advanced | Uses device TTS or AI voice | Audio permissions |
| Text formatting (bold, italic) | Edit mode → formatting bar | Advanced | Simplified: bold, italic, bullet only | None |
| Download as text | Node toolbar → "More" → "Export" | Advanced | Saves to device or shares | File system |
| Highlight text | Edit mode → select → highlight | Exclude | Complex touch interaction | None |

### 2.2 Story Node

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Create story node | FAB → "Add Story" | Basic | Guided creation flow | Canvas |
| Edit header | Tap header area | Basic | Inline editing | None |
| Edit body content | Tap body area | Basic | Full-screen rich editor | None |
| Change node color | Node toolbar → Color picker | Basic | Same as text node | None |
| Collapse/expand | Tap collapse icon | Basic | Smooth animation | None |
| Copy/duplicate | Node toolbar → "More" menu | Basic | Copies with all content | None |
| Delete node | Long-press → "Delete" | Basic | Confirmation required | None |
| Connect to other node | Node toolbar → "Connect" | Basic | Same as text node | Target node |
| AI summarize | Node toolbar → "AI" → "Summarize" | Basic | Condenses to key points | AI service |
| AI expand content | Node toolbar → "AI" → "Expand" | Advanced | Generates additional detail | AI service |
| Add media (image) | Edit mode → "Add Image" | Advanced | Camera or gallery picker | Media permissions |
| Audio narration | Node toolbar → "More" → "Listen" | Advanced | Reads header + body | Audio permissions |

### 2.3 AI Node (Dynamic Content Node)

*Primary node type for LLM-generated learning content*

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Create AI node | FAB → "Ask AI" | Basic | Opens prompt input immediately | Canvas, AI service |
| Initial prompt options | First node → Prompt sheet | Basic | Type own question OR select common starting point | AI service |
| Enter custom prompt | Node input field | Basic | Expandable text area | None |
| Submit query | "Send" button or keyboard submit | Basic | Shows typing indicator | AI service |
| View AI response | Response area within node | Basic | Scrollable if long, auto-formatted | AI service |
| Dynamic content population | Automatic on query | Basic | AI-generated answers and explanations | AI service, chapter context |
| Regenerate response | Node toolbar → "Regenerate" | Basic | Clears and re-queries | AI service |
| Copy response | Node toolbar → "Copy" | Basic | Copies to clipboard | None |
| Phrase/word selection | AI response → long-press → open Reader (selectable text) → select phrase | Basic | Opens phrase action sheet (Elaborate / Ask / Recommended) and creates child AI node | AI service, bottom sheet |
| Convert to Story Node | Node toolbar → "More" → "Convert" | Advanced | Transforms node type | None |
| Branch into topics | Node toolbar → "AI" → "Breakdown" | Basic | Creates connected child nodes | AI service |
| Follow-up question | Response area → "Ask follow-up" | Advanced | Maintains conversation context | AI service |
| Delete node | Long-press → "Delete" | Basic | Standard deletion | None |
| Connect to other node | Node toolbar → "Connect" | Basic | Standard connection | Target node |
| Auto-connect on creation | Automatic | Basic | New nodes connect to parent node | Canvas |

### 2.4 Video Node (YouTube)

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Create video node | FAB → "Add Video" | Basic | Opens search/URL input | Canvas |
| Search YouTube | Video node → search field | Basic | Keyboard with search suggestions | Network |
| Select from results | Search results list | Basic | Thumbnail + title display | Network |
| Paste video URL | Video node → URL input | Basic | Auto-detects YouTube URLs | Network |
| Play video | Tap play button | Basic | Inline player or full-screen | Network |
| Pause video | Tap pause button | Basic | Standard controls | None |
| Full-screen playback | Tap expand icon | Basic | Native full-screen player | None |
| AI summarize video | Node toolbar → "AI" → "Summarize" | Advanced | Requires video transcript | AI service, transcript |
| Delete node | Long-press → "Delete" | Basic | Standard deletion | None |
| Connect to other node | Node toolbar → "Connect" | Basic | Standard connection | Target node |
| Copy video URL | Node toolbar → "More" → "Copy URL" | Advanced | Copies to clipboard | None |

### 2.5 Image Node

*Standalone image nodes for visual learning content*

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Create image node | FAB → "Add Image" | Advanced | Opens camera/gallery/search picker | Canvas, media permissions |
| Capture from camera | Image picker → "Camera" | Advanced | Opens device camera | Camera permission |
| Select from gallery | Image picker → "Gallery" | Advanced | Opens device photo library | Media permission |
| Search images (Perplexity Sonar) | Image picker → "Search" | Advanced | Contextual search based on exploration | Perplexity API, network |
| View image full-screen | Tap image | Advanced | Pinch-zoom enabled | None |
| AI describe image | Node toolbar → "AI" → "Describe" | Advanced | Generates text description of image content | AI service |
| AI extract text (OCR) | Node toolbar → "AI" → "Extract Text" | Advanced | Extracts text from image | AI service, OCR |
| Connect to other node | Node toolbar → "Connect" | Advanced | Standard connection | Target node |
| Delete node | Long-press → "Delete" | Advanced | Confirmation dialog | None |
| Download image | Node toolbar → "More" → "Save" | Advanced | Saves to device gallery | File system |

---

## 3. Canvas-Level Features

Features that apply to the entire workspace/canvas.

### 3.1 Navigation

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Pinch to zoom | Two-finger gesture on canvas | Basic | Native gesture, 25%-400% range | None |
| Pan/scroll | One-finger drag on empty canvas | Basic | Momentum scrolling | None |
| Zoom in button | Bottom toolbar → "+" | Basic | 25% increment | None |
| Zoom out button | Bottom toolbar → "−" | Basic | 25% decrement | None |
| Fit to screen | Bottom toolbar → "Fit" | Basic | Shows all nodes | None |
| Center on node | Double-tap node | Advanced | Animates to center | None |
| Minimap navigation | Bottom sheet → "Overview" | Advanced | Simplified thumbnail view | None |
| Breadcrumb navigation | Header → path display | Advanced | Shows current location in hierarchy | None |

### 3.2 Selection

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Select single node | Tap node | Basic | Shows selection border + toolbar | None |
| Deselect | Tap empty canvas | Basic | Clears selection | None |
| Multi-select | Long-press → drag selection box | Advanced | Visual selection rectangle | None |
| Select all | Canvas menu → "Select All" | Advanced | Selects all visible nodes | None |
| Move selected nodes | Drag selected node(s) | Basic | Real-time position update | Selection |
| Delete selected | Selection toolbar → "Delete" | Basic | Confirmation for multiple | Selection |
| Group selected | Selection toolbar → "Group" | Exclude | Too complex for mobile v1 | Selection |

### 3.3 Layout

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Auto-arrange nodes | Canvas menu → "Auto Layout" | Advanced | Tree or radial layout options | Multiple nodes |
| Align nodes horizontally | Selection toolbar → "Align" → "Horizontal" | Advanced | Requires multi-select | Multi-select |
| Align nodes vertically | Selection toolbar → "Align" → "Vertical" | Advanced | Requires multi-select | Multi-select |
| Distribute spacing | Selection toolbar → "Distribute" | Exclude | Complex for mobile | Multi-select |
| Manual positioning | Drag node | Basic | Snap feedback on release | None |
| Reset canvas position | Canvas menu → "Reset View" | Basic | Returns to origin (0,0) | None |

### 3.4 Grid and Snap

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Snap to grid | Always enabled (simplified) | Basic | 15px grid only (no options) | None |
| Show grid lines | Settings → "Show Grid" | Advanced | Subtle grid overlay | None |
| Alignment guides | Automatic during drag | Advanced | Shows when aligned with other nodes | None |
| Custom grid size | Settings → Grid options | Exclude | Simplified to single option | None |

### 3.5 Background

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Solid background color | Settings → "Background" | Advanced | 6 preset colors | None |
| Grid pattern background | Settings → "Background" → "Grid" | Exclude | Removed for performance | None |
| Dot pattern background | Settings → "Background" → "Dots" | Exclude | Removed for performance | None |
| Custom background image | N/A | Exclude | Not supported on mobile | None |

### 3.6 Canvas Constraints

*Performance and usability limits for mobile devices*

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Node count warning | Automatic toast at 50 nodes | Basic | "Board getting large. Consider creating a linked board." | None |
| Node count hard limit | Automatic block at 65 nodes | Basic | Prevents creation, suggests new board | None |
| Create linked board | Warning dialog → "Create New Board" | Basic | Creates new board with connection to current | Board service |
| View node count | Board info → node counter | Basic | Shows "X/65 nodes" in board header | None |
| Performance mode | Automatic at 40+ nodes | Basic | Reduces animations, simplifies rendering | None |

**Technical Rationale**:
- **55-65 node limit**: Optimal range for mobile memory management and rendering performance
- **Warning at 50**: Gives users time to organize before hitting limit
- **Linked boards**: Encourages modular thinking while maintaining conceptual connections
- **Cognitive load**: Research suggests 50-70 items is upper limit for effective visual navigation

---

## 4. Side Panel Features

Features accessible through sidebars, bottom sheets, or modal panels.

### 4.1 Bottom Sheet (Primary Panel)

*Replaces desktop left/right sidebars with swipe-up panel*

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Open bottom sheet | Swipe up from bottom edge | Basic | Partial (40%) and full (90%) heights | None |
| Close bottom sheet | Swipe down or tap overlay | Basic | Smooth animation | None |
| Recent boards list | Bottom sheet → "Recent" tab | Basic | Thumbnail + title + timestamp | Authentication |
| Favorites list | Bottom sheet → "Favorites" tab | Advanced | Starred boards only | Authentication |
| Board search | Bottom sheet → search bar | Advanced | Searches board titles and content | Authentication |
| Templates gallery | Bottom sheet → "Templates" tab | Advanced | Categorized template cards | Template service |
| Quick actions | Bottom sheet → "Actions" tab | Basic | Undo, redo, settings shortcuts | None |

### 4.2 Node Properties Panel

*Appears when node is selected*

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| View node properties | Select node → swipe up | Advanced | Shows type, created date, connections | Node selection |
| Edit node name/label | Properties panel → "Name" | Advanced | Inline text editing | Node selection |
| View connections list | Properties panel → "Connections" | Advanced | Tap to navigate to connected node | Node selection |
| Node statistics | Properties panel → "Stats" | Advanced | Word count, view count | Node selection |
| Node history | Properties panel → "History" | Exclude | Too complex for mobile | Node selection |

### 4.3 Settings Panel

*Accessed via header menu or bottom navigation*

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Open settings | Header menu → "Settings" or Profile tab | Basic | Full-screen settings page | None |
| Dark mode toggle | Settings → "Appearance" | Basic | System/Light/Dark options | None |
| Account settings | Settings → "Account" | Basic | Mobile number, profile | Authentication |
| Curriculum settings | Settings → "My Curriculum" | Basic | Change class/exam selection | Curriculum data |
| Notification preferences | Settings → "Notifications" | Advanced | Push notification controls | Notifications |
| Data and storage | Settings → "Storage" | Advanced | Cache size, clear data | None |
| Help and support | Settings → "Help" | Basic | FAQ, contact, feedback | None |
| About and version | Settings → "About" | Basic | App version, licenses | None |
| Language selection | Settings → "Language" | Exclude | Uses device language | None |
| Vision model selection | N/A | Exclude | Power user feature | None |

### 4.4 Previous Year Questions Panel

*Exam-focused study resource*

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Open PYQ panel | Side panel → "Previous Years" tab | Basic | Bottom sheet with year filter | Chapter context |
| Filter by exam year | PYQ panel → Year picker | Basic | Scrollable year list (last 10 years) | PYQ database |
| Filter by exam type | PYQ panel → Exam filter | Basic | CBSE/ICSE/State/NEET/JEE based on user selection | Curriculum selection |
| View question list | PYQ panel → Question cards | Basic | Scrollable list with question preview | PYQ database |
| Expand question | Tap question card | Basic | Full question with options/answer | PYQ database |
| View solution | Question detail → "Show Solution" | Basic | Step-by-step solution display | PYQ database |
| Add to mind map | Question detail → "Add to Map" | Basic | Creates node with question content | Canvas |
| Mark as practiced | Question card → Checkbox | Advanced | Tracks completion status | User progress |
| Difficulty filter | PYQ panel → Difficulty chips | Advanced | Easy/Medium/Hard filter | PYQ metadata |
| Topic-wise grouping | PYQ panel → "By Topic" toggle | Advanced | Groups questions by subtopic | PYQ metadata |

---

## 5. Top-Level Navigation

Features in the main navigation structure.

### 5.1 Header Bar

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Back navigation | Header → left arrow | Basic | Returns to previous screen | Navigation stack |
| Board title display | Header → center | Basic | Truncated with ellipsis if long | Current board |
| Chapter context display | Header → subtitle | Basic | Shows current chapter name | Chapter selection |
| Edit board title | Tap header title | Basic | Inline editing with keyboard | Current board |
| Share button | Header → right side | Advanced | Opens share sheet | Current board |
| More options menu | Header → "⋮" menu | Basic | Dropdown with board actions | Current board |
| Sync status indicator | Header → cloud icon | Basic | Shows sync state | Authentication |

### 5.2 Bottom Navigation Bar

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Home tab | Bottom nav → "Home" | Basic | Dashboard with recent activity | Authentication |
| Boards tab | Bottom nav → "Boards" | Basic | All boards list/grid view | Authentication |
| AI tab | Bottom nav → "AI" | Basic | Dedicated AI assistant interface | AI service |
| Profile tab | Bottom nav → "Profile" | Basic | Account and settings | Authentication |
| Notification badge | Bottom nav → badge on icon | Advanced | Shows unread count | Notifications |

### 5.3 Floating Action Button (FAB)

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Primary FAB | Bottom right of canvas | Basic | "+" icon, 56dp size | Canvas screen |
| FAB expansion | Tap FAB | Basic | Reveals 4 node type options | FAB |
| Add Text Node | FAB menu → "Text" | Basic | Icon + label | FAB expansion |
| Add Story Node | FAB menu → "Story" | Basic | Icon + label | FAB expansion |
| Add AI Node | FAB menu → "AI" | Basic | Icon + label | FAB expansion |
| Add Video Node | FAB menu → "Video" | Basic | Icon + label | FAB expansion |
| FAB collapse | Tap outside or tap FAB | Basic | Closes menu | FAB expansion |
| Mini FAB (secondary) | Above primary FAB when expanded | Advanced | Quick undo action | FAB expansion |

### 5.4 Context Menus

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Node context menu | Long-press on node | Basic | 6 items max visible | Node |
| Canvas context menu | Long-press on empty canvas | Advanced | Paste, add node options | Canvas |
| Connection context menu | Long-press on connection line | Advanced | Delete, edit connection | Connection |
| Selection context menu | Long-press on multi-selection | Advanced | Bulk actions | Multi-select |



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

*AI features aligned with the diagnostic learning framework*

> **Note: Category Framework Visibility**
> The 8 diagnostic dimensions (Define, Distinguish, Decompose, Connect, Delimit, Predict, Contextualize, Vary) are used for **diagnostic purposes only** and are **never visible to students**. Students explore naturally; the system observes and classifies invisibly. Category visibility is reserved for the Teacher Dashboard only.

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
- With the hybrid architecture, AI node content is rendered inside native React Native Views, which **do** support native OS text selection.
- Basic tier uses a **Reader bottom sheet** (React Native text surface) for an enhanced word/phrase highlighting experience, though in-node text selection is also possible.
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
3. Generate the child node’s response using a **thread context packet** (see Context Propagation).

**Context Propagation (threading)**:
- The child node must store a durable `thread_context` reference so that **future question generation from that child** is grounded in the initiating phrase.
- Minimum context packet inputs:
  - `selected_phrase`
  - `source_excerpt` (local window around phrase)
  - `parent_node_summary`
  - `neighborhood_summaries` (recent/connected nodes)
  - `chapter/subject header`

**Recommended question generation constraints**:
- Must remain **organic-first** (no category labels, no framework references, no forced “cover all angles”).
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

---

## 7. System-Level Features

App-wide functionality that operates across all screens.

### 7.1 Authentication

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Mobile number login | Login screen | Basic | OTP-based verification (SMS/WhatsApp) | Auth service, SMS gateway |
| Mobile number signup | Signup screen | Basic | Mobile number + OTP verification | Auth service, SMS gateway |
| Social login (Google) | Login screen → "Continue with Google" | Advanced | OAuth flow | Auth service, Google |
| Social login (Apple) | Login screen → "Continue with Apple" | Advanced | Sign in with Apple (iOS required) | Auth service, Apple |
| Account recovery | Login screen → "Can't access account?" | Basic | OTP to registered mobile number | Auth service, SMS gateway |
| Logout | Settings → "Log Out" | Basic | Clears local session | Auth service |
| Session persistence | Automatic | Basic | Stays logged in across app restarts | Secure storage |
| Biometric unlock | Settings → "Security" | Advanced | Face ID / Fingerprint | Biometric hardware |

### 7.2 Data Sync

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Auto-sync on change | Automatic | Basic | Syncs after each edit (debounced) | Network, authentication |
| Sync status indicator | Header → cloud icon | Basic | Shows syncing/synced/offline | Network |
| Manual sync trigger | Pull-to-refresh | Basic | Forces sync check | Network, authentication |
| Conflict resolution | Sync dialog | Advanced | Shows conflicting changes, pick version | Sync service |
| Sync history | Settings → "Sync" → "History" | Advanced | Shows recent sync events | Sync service |

### 7.3 Offline Mode

*Offline capabilities are Basic tier priority based on Indian student device market research (see `docs/research/indian-student-market-analysis.md`). Rural connectivity gaps (58.8% mobile penetration vs. 125.3% urban) and competitor offline offerings (Khan Academy, BYJU's) make offline mode essential for target market.*

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Offline data access | Automatic | Basic | Cached boards available offline | Local storage |
| Offline editing | Automatic | Basic | Edits queued for sync when online | Local storage |
| Offline indicator | Header → offline badge | Basic | Shows when no network connection | Network detection |
| Sync queue | Settings → "Offline" → "Pending" | Advanced | Shows queued changes with sync status | Local storage |
| Selective offline boards | Board menu → "Available Offline" | Advanced | Downloads full board for offline use | Local storage |
| Offline AI (limited) | N/A | Exclude | Requires network for AI features | N/A |

### 7.4 Notifications

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Push notifications | System notifications | Advanced | Learning reminders, streak alerts | Notification service |
| Quiz reminders | Notification → "Time to quiz!" | Advanced | Configurable timing | Quiz system |
| Learning streak alerts | Notification → streak status | Advanced | Daily engagement prompts | Analytics |
| In-app notifications | Notification center (bottom sheet) | Advanced | Activity feed | Notification service |
| Notification preferences | Settings → "Notifications" | Advanced | Enable/disable by type | Settings |

### 7.5 Settings and Preferences

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Dark mode | Settings → "Appearance" | Basic | System/Light/Dark toggle | None |
| Text size | Settings → "Accessibility" | Advanced | Small/Medium/Large/XL | None |
| Haptic feedback | Settings → "Haptics" | Advanced | Enable/disable touch feedback | Haptic hardware |
| Auto-save interval | Settings → "Editor" | Exclude | Always auto-save on mobile | None |
| Default node type | Settings → "Editor" | Advanced | Sets FAB default action | None |
| Clear cache | Settings → "Storage" → "Clear Cache" | Basic | Frees local storage | None |

### 7.6 Export and Import

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Export board as image | Board menu → "Export" → "Image" | Advanced | PNG/JPG to device gallery | File system |
| Export board as PDF | Board menu → "Export" → "PDF" | Advanced | PDF generation | File system |
| Share board link | Board menu → "Share" | Advanced | Generates shareable URL | Share service |
| Import board | N/A | Exclude | Use web for complex imports | N/A |
| Export all data | Settings → "Data" → "Export" | Advanced | Full data backup | File system |

### 7.7 Performance and Optimization

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Lazy loading | Automatic | Basic | Loads nodes as they enter viewport | None |
| Image compression | Automatic | Basic | Compresses images for mobile | None |
| Content caching | Automatic | Basic | Caches frequently accessed content | Local storage |
| Background sync | Automatic | Advanced | Syncs when app is backgrounded | Background tasks |
| Memory management | Automatic | Basic | Unloads off-screen nodes | None |
| Reduced animations | Settings → "Accessibility" → "Reduce Motion" | Advanced | Disables non-essential animations | None |

#### 7.7.1 Minimum Device Target Specifications

*Based on Indian student device market research (see `docs/research/indian-student-market-analysis.md`)*

| Specification | Minimum Requirement | Rationale |
|---------------|---------------------|-----------|
| **Android Version** | Android 11 (API 30) | ~95% coverage of Indian Android users (Android 11+ = 90%+) |
| **RAM** | 4GB | Entry-level segment floor; budget devices (₹10,000-₹20,000) have 4-6GB |
| **Screen Size** | 6.5" HD+ (720×1600) | Standard for budget smartphones in Indian market |
| **Storage** | 32GB (8GB available) | Minimum for app + offline cached boards |
| **GPU** | OpenGL ES 3.0 | Required for Skia edge rendering (Bézier curves) in the hybrid architecture |

**Performance Optimization Targets**:
- **Memory budget**: 150MB maximum app footprint (allows headroom on 4GB devices)
- **Viewport culling**: Aggressive culling at node count >30 on low-RAM devices
- **LOD thresholds**: Simplified rendering (rectangles only) below 0.5 zoom on budget devices
- **Texture atlas**: Single 1024×1024 spritesheet for all icons (reduces draw calls)

### 7.8 Privacy and Compliance

*Data protection and regulatory compliance (Basic tier)*

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Privacy policy display | Settings → "Privacy" → "Privacy Policy" | Basic | In-app WebView with full policy | None |
| Data collection consent | First launch → consent dialog | Basic | Clear opt-in for data collection | Consent service |
| Parental consent (minors) | Signup → age verification → parent mobile number | Basic | Required for users under 18 via parent OTP | Auth service, SMS gateway |
| Data export request | Settings → "Privacy" → "Export My Data" | Basic | Generates downloadable data package | Data service |
| Data deletion request | Settings → "Privacy" → "Delete My Data" | Basic | Initiates account and data deletion | Auth service, data service |
| Consent management | Settings → "Privacy" → "Manage Consent" | Basic | Toggle data collection categories | Consent service |
| Data residency indicator | Settings → "Privacy" → "Data Location" | Basic | Shows where data is stored | None |

**Compliance Framework**:

| Regulation | Requirement | Implementation |
|------------|-------------|----------------|
| **DPDP Act 2023 (India)** | Data localization for Indian users | Data stored in India-region servers for Indian users |
| **DPDP Act 2023 (India)** | Consent before data processing | Explicit opt-in consent dialog on first launch |
| **DPDP Act 2023 (India)** | Right to erasure | "Delete My Data" feature with 72-hour processing |
| **DPDP Act 2023 (India)** | Parental consent for minors | Verified parental consent for users under 18 |
| **DPDP Act 2023 (India)** | Data breach notification | In-app and SMS notification within 72 hours |
| **General** | Data minimization | Collect only data necessary for learning features |
| **General** | Purpose limitation | Data used only for stated educational purposes |

**Data Retention Policy**:
- Active account data: Retained while account is active
- Exploration session data: 2 years for learning analytics
- Deleted account data: Purged within 30 days of deletion request
- Anonymous aggregate data: Retained indefinitely for platform improvement

---

## 8. Feature Summary by Priority

<!-- BUSINESS MODEL SPECIFICATION - TO BE DEFINED
- Subscription models (individual or institutional)
- Pricing tiers and feature gating
- Institutional vs. individual access
Decision: Deferred until feature specification is complete -->

### Basic - Core learner features

**Total: ~98 features** *(Updated with market research-driven offline mode prioritization and device target specifications)*

| Category | Feature Count |
|----------|---------------|
| Curriculum & Navigation | 19 |
| Node-Level | 41 |
| Canvas-Level | 20 |
| Side Panels | 22 |
| Top-Level Navigation | 19 |
| AI Integration | 23 |
| System-Level | 32 |

*Note: System-Level count includes 3 offline mode Basic features (offline data access, offline editing, offline indicator) and device target specifications. See `docs/indian-student-device-market-research.md` for market research rationale.*

### Advanced - Enhancement features

**Total: ~70 features** *(Merged from former Extended and Advanced tiers)*

Focus areas:
- Audio and voice features
- Advanced selection and layout
- Notifications and engagement
- Social login and sharing
- Image nodes and Perplexity Sonar integration
- Podcast advanced features
- Templates and export
- Advanced search
- Node statistics
- Data export

### Teacher tier - Teacher dashboard

**Status**: Specification deferred until core student features are validated

**Scope** (per system-architecture.md):
- Individual student profiles with categorical coverage visualization
- Class-level analytics and gap identification
- Priority intervention recommendations
- Exploration pattern analysis
- Quiz performance tracking

**Note**: Teacher Dashboard will be defined after initial user validation. See `docs/system-architecture.md` Section "Teacher Dashboard Specification" for architectural details.

### Excluded Features

**Total: ~20 features**

Reasons:
- Too complex for mobile interaction
- Performance concerns
- Low priority for learning platform
- Better suited for web/desktop

---

## 9. Additional Feature Recommendations

The following features are recommended additions to enhance the mobile learning experience, organized by category.

### 9.1 Podcast Generation Features

*Transform exploration journeys into narrative audio content*

**Overview**: Podcast generation uses the learner's exploration path (questions chosen, nodes visited, media engaged, and derived insights) to create personalized audio learning content.

**Roadmap note (important)**: Any tier labels in this document should be treated as **non-binding**. For clarity in this section we use **capability tiers**:
- **Basic**: minimal end-to-end podcast experience
- **Advanced**: quality-of-life, library, multimodal, and meta-commentary features

#### 9.1.1 Session-Based Podcast Generation

| Feature | UI Location | Tier | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Generate exploration podcast | Board menu → "Create Podcast" | Basic | Full-screen generation wizard | AI service, TTS service, session data |
| Preview podcast script | Podcast wizard → "Preview Script" | Basic | Scrollable text with edit capability | AI service |
| Choose podcast length | Podcast wizard → "Length" | Basic | Short (3-5 min), Medium (8-12 min), Long (15-20 min) | AI service |
| Generate podcast audio | Podcast wizard → "Generate" | Basic | Background generation with progress indicator | AI service, TTS service |
| Listen to generated podcast | Podcast player (full-screen) | Basic | Standard audio controls, background playback | Audio permissions |
| Select voice style | Podcast wizard → "Voice" | Advanced | 4 options: Narrator, Conversational, Interview, Student-Teacher | TTS service |
| Download podcast | Podcast player → "Download" | Advanced | Saves MP3 to device | File system |
| Share podcast | Podcast player → "Share" | Advanced | Share via system share sheet | Share service |
| Include learning insights (category-neutral) | Podcast wizard → "Include Learning Insights" toggle | Advanced | Adds meta-commentary on exploration patterns (no category labels) | Diagnostic data |

#### 9.1.2 Node-Level Podcast Features

| Feature | UI Location | Tier | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Add node to podcast queue | Node toolbar → "More" → "Add to Podcast" | Advanced | Visual indicator on queued nodes | Podcast queue |
| Generate node narration | Node toolbar → "More" → "Narrate" | Advanced | Creates audio for single node content | TTS service |
| Include in exploration story | Node context menu → "Include in Story" | Advanced | Marks node as key point for podcast | Podcast queue |
| Record voice note | Node toolbar → "More" → "Record" | Advanced | Student records own explanation | Microphone permission |

#### 9.1.3 Podcast Library and Management

| Feature | UI Location | Tier | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| View podcast library | Bottom nav → "Podcasts" or Profile → "My Podcasts" | Advanced | List view with thumbnails and duration | Local storage |
| Play podcast offline | Podcast library → downloaded episode | Advanced | Cached audio playback | Local storage |
| Delete podcast | Podcast library → swipe left | Advanced | Confirmation dialog | Local storage |
| Podcast playback history | Podcast library → "History" tab | Advanced | Recently played with resume position | Local storage |
| Subscribe to topic podcasts | Explore → topic → "Subscribe" | Advanced | Curated podcasts from community | Podcast service |

#### 9.1.4 Podcast Voice and Style Options

| Feature | UI Location | Tier | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| AI narrator voice | Settings → "Podcast" → "Default Voice" | Advanced | 6 voice options (3 male, 3 female) | TTS service |
| Playback speed control | Podcast player → speed button | Advanced | 0.5x, 1x, 1.25x, 1.5x, 2x | None |
| Interview-style dialogue | Podcast wizard → "Style" → "Interview" | Advanced | Two-voice Q&A format | TTS service (multi-voice) |
| Student-teacher dialogue | Podcast wizard → "Style" → "Lesson" | Advanced | Simulates tutoring conversation | TTS service (multi-voice) |
| Background music | Podcast wizard → "Music" toggle | Advanced | Subtle ambient music options | Audio assets |

#### 9.1.5 Podcast Content Structure

*How exploration sessions transform into podcast narratives*

| Podcast Element | Source Data | AI Processing |
|-----------------|-------------|---------------|
| Introduction | Board title, chapter topic | Generates engaging hook based on topic |
| Path map (non-linear) | Session path graph (nodes, selections, revisits) | Explains the "shape" of learning: clusters, pivots, and loops |
| Concept clusters | Node clusters + selected questions | Summarizes each cluster into a compact explanation |
| Bridges | Cross-cluster transitions | Adds short bridging explanations to connect clusters |
| Media highlights | Videos/images engaged + derived text (captions/transcripts/OCR) | Pulls in brief supporting explanations/examples |
| Misconceptions & fixes (category-neutral) | Answer attempts / quiz errors / follow-up questions | Identifies likely confusion points and corrects them |
| Conclusion | Session summary | Synthesizes learning with forward prompts |

**Example Podcast Script Structure**:
```
[INTRO] "In this episode, we'll turn your mind-map exploration of photosynthesis into a clear mental model."

[PATH MAP] "You explored three main clusters: (1) what photosynthesis is, (2) what makes it work, and (3) what changes when conditions change."

[CLUSTER 1] Core meaning and purpose — concise explanation

[BRIDGE] "To understand the purpose, we need the mechanism—what parts do what?"

[CLUSTER 2] Parts and mechanism — stages, roles, and a small worked example

[MEDIA HIGHLIGHT] "From the video you watched, here's the key idea in one sentence..."

[CLUSTER 3] What-if variations — limiting factors and consequences

[NEXT STEPS] "If you want to strengthen this, try one comparison question and one what-if question..."
```

#### 9.1.6 Non-linear, path-optimized podcast generation strategy (required)

The podcast must be generated from the learner's **full exploration path structure**, not as a chronological recap.

**Core principle**: The system can reorder, synthesize, and bridge concepts to maximize reinforcement value — while staying faithful to what the learner actually engaged with.

**High-level pipeline**:
1. Build a **path graph** from events (node visits, offer sets, selections, revisits, media engaged).
2. Detect **clusters** (concept communities) and **pivots** (bridge transitions).
3. Identify **gaps / confusion points** from behavior signals (avoidance, repeated revisits, errors), expressed in category-neutral terms.
4. Generate an outline that:
   - starts with a path map,
   - teaches per cluster,
   - inserts short bridges,
   - adds targeted corrections/hints,
   - ends with next-step prompts.
5. Render script — then TTS — then store the episode with provenance (session_id, policy_version, inputs).

### 9.2 Mobile-Specific Device Features

*Leveraging mobile device capabilities*

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Camera OCR capture | FAB → "Scan Text" | Advanced | Photograph notes/textbook → extract text → create node | Camera permission, OCR service |
| Camera whiteboard capture | FAB → "Scan Whiteboard" | Advanced | Captures classroom whiteboard → creates nodes | Camera permission, OCR service |
| Voice-to-node creation | FAB → long-press → speak | Advanced | Speak to create text node | Microphone permission |
| Shake to undo | Gesture (shake device) | Advanced | Quick undo last action | Accelerometer |
| Location-based learning context | Automatic (optional) | Advanced | Tags boards with location (library, classroom, home) | Location permission |
| AR concept visualization | Node toolbar → "View in AR" | Exclude | Too complex for initial phases | ARKit/ARCore |
| Widget: Quick capture | Home screen widget | Advanced | Add thought to current board without opening app | Widget API |
| Widget: Daily question | Home screen widget | Advanced | Shows daily exploration prompt | Widget API, AI service |
| Siri/Google Assistant integration | Voice command | Advanced | "Ask about photosynthesis" | Voice assistant API |
| Apple Watch companion | Watch app | Exclude | View notifications, quick capture | watchOS |
| Handwriting input | Node edit → stylus mode | Advanced | Apple Pencil / stylus support for handwritten notes | Stylus API |

### 9.3 Learning Platform Enhancements

*Features supporting natural exploration without exposing categorical framework*

> **Category Visibility Policy: STRICT INVISIBILITY**
> The 8 diagnostic dimensions are used for **diagnostic purposes only** and are **never visible to students**. This ensures students explore naturally without "gaming" the system. Category-related analytics are reserved for the **Teacher Dashboard only** (Teacher tier).

#### 9.3.1 Student-Facing Features (Category-Invisible)

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Exploration path visualization | Board menu → "My Journey" | Advanced | Animated replay of exploration sequence (no categories shown) | Session data |
| Natural exploration hints | AI panel → "Explore More" section | Basic | Subtle natural language prompts (e.g., "Try asking 'what if...'" or "What causes this?") with **NO category labels** | Diagnostic data |
| Exploration depth indicator | Node badge | Advanced | Shows how deeply a concept has been explored (simple depth score, no categories) | Session data |
| Conceptual connection strength | Connection line thickness | Advanced | Thicker lines = stronger conceptual links | Exploration data |
| Learning streak tracking | Profile → "Learning Stats" | Advanced | Days active, questions explored, boards created | Analytics |

#### 9.3.2 Teacher Dashboard Features (Category-Visible) - Teacher tier

*These features expose categorical data and are ONLY available in Teacher Dashboard*

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Categorical exploration radar | Teacher Dashboard → Student View | Teacher | Visual radar chart of 8 categories | Diagnostic data, Teacher auth |
| Category-specific question prompts | Teacher Dashboard → "Suggested Follow-Ups" | Teacher | "Student would benefit from more Define questions" | Diagnostic data, Teacher auth |
| Category milestone tracking | Teacher Dashboard → Student View | Teacher | Shows which categories student has explored | Diagnostic data, Teacher auth |
| Category-based question filtering | Teacher Dashboard → Question Analytics | Teacher | Filter questions by categorical dimension | Question bank, Teacher auth |
| Bridge question identification | Teacher Dashboard → Pattern Analysis | Teacher | Shows which questions bridge categories effectively | Pattern analysis, Teacher auth |
| Class-level category concerns | Teacher Dashboard → Class View | Teacher | Aggregate category coverage across class | Diagnostic data, Teacher auth |
| Learning velocity by category | Teacher Dashboard → Analytics | Teacher | How quickly students progress through categories | Analytics, Teacher auth |

#### 9.3.3 Removed/Repositioned Features

The following features from the original specification have been **removed from student-facing UI** to enforce category invisibility:

| Original Feature | Original Priority | Decision | Reason |
|------------------|-------------------|----------|--------|
| Category-specific question prompts (student) | Advanced | **Removed** | Exposes categories to students |
| Category milestone celebrations | Advanced | **Removed** | Dimension-count milestones reveal the hidden diagnostic framework (category invisibility violation) |
| Category-based question filtering (student) | Advanced | **Moved to Teacher Dashboard** | Category labels not for students |
| Categorical exploration radar (student) | Advanced | **Moved to Teacher Dashboard** | Category visualization not for students |

### 9.4 Social and Collaborative Features

*Peer learning and community features*

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Share exploration journey | Board menu → "Share Journey" | Advanced | Generates shareable link to exploration path | Share service |
| View peer explorations | Explore tab → "Community" | Advanced | Browse anonymized exploration paths on same topic | Community service |
| Study group boards | Boards tab → "Groups" | Advanced | Shared boards with real-time collaboration | Collaboration service |
| Peer question suggestions | Question list → "From Peers" section | Advanced | Questions other students found valuable | Community data |
| Discussion threads on nodes | Node → "Discuss" | Exclude | Too complex for mobile v1 | Collaboration service |
| Mentor matching | Profile → "Find Mentor" | Exclude | Connect with advanced students | Matching service |
| Leaderboards (opt-in) | Profile → "Leaderboard" | Advanced | Exploration streaks, exploration breadth | Analytics, gamification |
| Share podcast with peers | Podcast player → "Share to Group" | Advanced | Share generated podcast in study group | Share service, groups |
| Collaborative podcast creation | Group board → "Create Group Podcast" | Exclude | Multiple students contribute to podcast | Collaboration, podcast service |
| Question upvoting | Question list → upvote icon | Advanced | Community rates question quality | Community service |

### 9.5 Enhanced Accessibility Features

*Beyond basic accessibility*

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Screen reader optimization | Automatic | Basic | Full VoiceOver/TalkBack support | Accessibility API |
| High contrast mode | Settings → "Accessibility" → "High Contrast" | Advanced | Enhanced color contrast throughout | None |
| Large touch targets | Settings → "Accessibility" → "Large Targets" | Advanced | Increases button/node tap areas by 50% | None |
| Voice navigation | Settings → "Accessibility" → "Voice Control" | Advanced | Navigate app entirely by voice | Voice control API |
| Dyslexia-friendly font | Settings → "Accessibility" → "OpenDyslexic Font" | Advanced | Switches to dyslexia-optimized typeface | Font assets |
| Reading ruler | Node view → "Reading Ruler" | Advanced | Highlights current line being read | None |
| Color blind modes | Settings → "Accessibility" → "Color Vision" | Advanced | Deuteranopia, Protanopia, Tritanopia modes | None |
| Reduced motion (enhanced) | Settings → "Accessibility" → "Reduce Motion" | Basic | Disables all animations, not just non-essential | None |
| Audio descriptions for images | Image node → "Describe" | Advanced | AI-generated audio description | AI service, TTS |
| Keyboard navigation (external) | Automatic with external keyboard | Advanced | Full keyboard shortcuts when keyboard connected | External keyboard |
| Focus mode | Settings → "Focus" | Advanced | Hides non-essential UI, enlarges current node | None |
| Session time limits | Settings → "Wellness" → "Session Limits" | Advanced | Reminds to take breaks after configurable time | Timer |
| Night shift integration | Automatic | Basic | Respects system night shift/blue light settings | System settings |

### 9.6 Missing Complementary Features

*Features that fill gaps in the current specification*

| Feature | UI Location | Priority | Mobile Adaptation | Dependencies |
|---------|-------------|----------|-------------------|--------------|
| Undo/redo history | Bottom sheet → "History" | Advanced | Visual list of recent actions | Action history |
| Board versioning | Board menu → "Versions" | Advanced | Restore previous board states | Version service |
| Duplicate board | Board menu → "Duplicate" | Advanced | Creates copy of entire board | None |
| Board templates (create) | Board menu → "Save as Template" | Advanced | Save current board as reusable template | Template service |
| Quick notes (scratchpad) | Swipe from right edge | Advanced | Temporary notes not attached to board | Local storage |
| Bookmark specific nodes | Node toolbar → "Bookmark" | Advanced | Quick access to important nodes | Bookmarks |
| Node linking (cross-board) | Node toolbar → "Link to..." | Advanced | Connect nodes across different boards | Cross-board service |
| Spaced repetition reminders | Automatic notifications | Advanced | Reminds to revisit concepts at optimal intervals | Notification service, SR algorithm |
| Learning goals | Profile → "Goals" | Advanced | Set and track learning objectives | Goals service |
| Progress milestones | Profile → "Achievements" | Advanced | Celebrate learning milestones | Gamification |
| Daily learning summary | Notification (end of day) | Advanced | Summary of day's exploration | Analytics, notifications |
| Weekly exploration report | Profile → "Reports" | Advanced | Detailed weekly learning analytics | Analytics |
| Content bookmarking | Any content → "Save for Later" | Advanced | Save AI responses, questions for review | Bookmarks |
| Flashcard generation | Node toolbar → "Create Flashcards" | Advanced | Generate flashcards from node content | AI service |
| Study session timer | Canvas → timer icon | Advanced | Pomodoro-style study timer | Timer |

---

## 10. Updated Feature Summary

### Feature Count by Tier (Version 3.0)

| Tier | Updated Total |
|------|---------------|
| **Basic** | ~98 |
| **Advanced** | ~145 |
| **Teacher** | ~7 |
| **Excluded** | ~25 |

### Feature Categories by Tier

| Category | Basic | Advanced | Excluded |
|----------|-------|----------|----------|
| Curriculum & Syllabus Navigation | 19 | 3 | 0 |
| Previous Year Questions | 7 | 3 | 0 |
| Podcast Generation | 5 | 18 | 0 |
| Mobile Device Features | 0 | 9 | 2 |
| Diagnostic Framework Enhancements | 1 | 9 | 0 |
| Social/Collaborative | 0 | 9 | 3 |
| Enhanced Accessibility | 3 | 11 | 0 |
| Complementary Features | 0 | 14 | 0 |

### Tier Rationale

**Basic (Essential for launch)**:
- Syllabus-driven navigation is core to the learning platform (Class, Exam, Subject, Chapter selection)
- Dashboard with resume/browse functionality enables session continuity
- Previous Year Questions are critical for exam-focused users (NEET, JEE, CBSE)
- Core podcast generation provides differentiated learning experience
- Session persistence ensures mind map state is saved for resume

**Advanced (Enhancement features)**:
- Advanced podcast features (voice styles, download, share, multi-voice dialogue)
- PYQ enhancement features (difficulty filter, topic grouping)
- Recommended chapters based on AI analysis
- Community podcast features require social infrastructure
- Templates, export, and advanced customization

---

*Document Version 2.1 | Mobile Feature Specification*
*Platform: Categorical Exploration Learning Platform*
*Target: iOS and Android mobile applications*

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Initial | Base feature specification with 6 sections |
| 1.1 | - | Added Podcast Generation, Device Features, Diagnostic Framework Enhancements, Social Features, Accessibility |
| 1.2 | - | Added Question Discovery Flow (Section 6.5.1), Image Node (Section 2.5), Perplexity Sonar integration (Section 6.6), Canvas Constraints (Section 3.6), Privacy and Compliance (Section 7.8), Category visibility clarification (strict invisibility), Teacher Dashboard deferral note, Business model placeholder |
| 2.0 | - | **Major revision integrating reference note features**: Added Section 1 (Curriculum & Syllabus Navigation with Dashboard, Subject/Chapter selection), Section 4.4 (Previous Year Questions Panel), enhanced Section 2.3 (AI Node with phrase selection, initial prompts, auto-connect), promoted core podcast generation to MVP, added session persistence, chapter context display. Renumbered all sections to accommodate new curriculum section. Updated feature counts to reflect ~95 MVP features. |
| 2.1 | Current | **Market research integration**: Added Section 7.7.1 (Minimum Device Target Specifications) based on Indian student device market research. Added rationale notes to Section 7.3 (Offline Mode) explaining MVP priority for offline features. Updated feature counts to ~98 MVP features. Reference: `docs/research/indian-student-market-analysis.md`. |
