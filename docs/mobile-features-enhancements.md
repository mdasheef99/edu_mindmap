# Mobile Features: Enhancements & Feature Summaries

## Document Overview

This document contains feature summaries by priority tier, additional feature recommendations (podcast generation, mobile-specific features, learning platform enhancements, social features, accessibility, and complementary features), and updated feature counts.

**Part of**: Mobile Feature Specification (split for AI agent optimization)
**Related files**:
- [Core UI Components](mobile-features-core-ui.md) - Curriculum, nodes, canvas, panels, navigation
- [AI Integration Features](mobile-features-ai-integration.md) - AI-powered capabilities
- [System Features](mobile-features-system.md) - Authentication, sync, offline mode
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
> The 8 Kantian categorical dimensions are used for **diagnostic purposes only** and are **never visible to students**. This ensures students explore naturally without "gaming" the system. Category-related analytics are reserved for the **Teacher Dashboard only** (Teacher tier).

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
| Category-specific question prompts | Teacher Dashboard → "Suggested Interventions" | Teacher | "Student needs Define questions" | Diagnostic data, Teacher auth |
| Category milestone tracking | Teacher Dashboard → Student View | Teacher | Shows which categories student has explored | Diagnostic data, Teacher auth |
| Category-based question filtering | Teacher Dashboard → Question Analytics | Teacher | Filter questions by categorical dimension | Question bank, Teacher auth |
| Bridge question identification | Teacher Dashboard → Pattern Analysis | Teacher | Shows which questions bridge categories effectively | Pattern analysis, Teacher auth |
| Class-level category gaps | Teacher Dashboard → Class View | Teacher | Aggregate category coverage across class | Diagnostic data, Teacher auth |
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
| Kantian Framework Enhancements | 1 | 9 | 0 |
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
| 1.1 | - | Added Podcast Generation, Device Features, Kantian Enhancements, Social Features, Accessibility |
| 1.2 | - | Added Question Discovery Flow (Section 6.5.1), Image Node (Section 2.5), Perplexity Sonar integration (Section 6.6), Canvas Constraints (Section 3.6), Privacy and Compliance (Section 7.8), Category visibility clarification (strict invisibility), Teacher Dashboard deferral note, Business model placeholder |
| 2.0 | - | **Major revision integrating reference note features**: Added Section 1 (Curriculum & Syllabus Navigation with Dashboard, Subject/Chapter selection), Section 4.4 (Previous Year Questions Panel), enhanced Section 2.3 (AI Node with phrase selection, initial prompts, auto-connect), promoted core podcast generation to MVP, added session persistence, chapter context display. Renumbered all sections to accommodate new curriculum section. Updated feature counts to reflect ~95 MVP features. |
| 2.1 | Current | **Market research integration**: Added Section 7.7.1 (Minimum Device Target Specifications) based on Indian student device market research. Added rationale notes to Section 7.3 (Offline Mode) explaining MVP priority for offline features. Updated feature counts to ~98 MVP features. Reference: `docs/research/indian-student-market-analysis.md`. |
