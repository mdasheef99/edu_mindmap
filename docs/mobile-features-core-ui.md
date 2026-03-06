# Mobile Features: Core UI Components

## Document Overview

This document specifies the core user interface components for the mobile application, including curriculum navigation, node types, canvas features, side panels, and top-level navigation.

**Part of**: Mobile Feature Specification (split for AI agent optimization)
**Related files**:
- [AI Integration Features](mobile-features-ai-integration.md) - AI-powered capabilities
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
