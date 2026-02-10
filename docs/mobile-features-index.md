# Mobile Feature Specification - Master Index

## Overview

This index provides navigation for the mobile feature specification, which has been split into 4 modular files optimized for AI coding agent context windows.

**Why the split?**  
The original `mobile-feature-specification.md` (1,029 lines ≈ 15,000-20,000 tokens) exceeded typical AI coding agent context window limits (4K-8K tokens). The specification has been reorganized into 4 focused files (162-381 lines each, ~2,400-5,700 tokens per file) to enable efficient AI-assisted development.

**Split Strategy:**  
Files are organized by **UI layer** to group related features that are typically implemented together as cohesive units.

---

## Navigation Guide

### 📱 [Core UI Components](mobile-features-core-ui.md) (358 lines)
**Sections 1-5**: Curriculum navigation, node types, canvas features, side panels, top-level navigation

**Use this file when:**
- Implementing curriculum/syllabus selection UI
- Building node types (Text, Story, AI, Video, Image nodes)
- Developing canvas interaction features (pan, zoom, selection, layout)
- Creating side panels (bottom sheet, properties, settings, PYQ panel)
- Implementing top-level navigation (header bar, bottom nav, FAB, context menus)

**Key features:** Dashboard, subject/chapter navigation, node toolbars, canvas constraints, session persistence

---

### 🤖 [AI Integration Features](mobile-features-ai-integration.md) (220 lines)
**Section 6**: All AI-powered capabilities

**Use this file when:**
- Implementing AI actions (summarize, expand, breakdown, generate questions)
- Building the dedicated AI assistant panel ("Ask")
- Developing AI-powered search functionality
- Creating the Question Discovery Flow (Section 6.5.1)
- Implementing phrase/word selection exploration
- Integrating Perplexity Sonar API

**Key features:** Node toolbar AI actions, context menu AI, learning-specific AI features, category invisibility enforcement

---

### ⚙️ [System Features](mobile-features-system.md) (162 lines)
**Section 7**: System-level infrastructure

**Use this file when:**
- Implementing authentication (mobile number + OTP, parental consent)
- Building data sync functionality
- Developing offline mode capabilities
- Creating notification system
- Implementing settings and preferences
- Building export/import features
- Optimizing performance for target devices
- Ensuring privacy compliance (COPPA, GDPR, DPDPA)

**Key features:** Mobile-first auth, offline-first architecture, device target specs (4GB RAM, Android 11+), data retention policies

---

### 🎯 [Enhancements & Summaries](mobile-features-enhancements.md) (381 lines)
**Sections 8-10**: Feature priorities, recommendations, version history

**Use this file when:**
- Understanding feature priorities (Basic vs Advanced vs Teacher vs Exclude)
- Planning implementation roadmap
- Reviewing additional feature recommendations (podcast generation, mobile-specific features, accessibility)
- Checking feature counts and version history
- Understanding business model placeholders

**Key features:** ~98 Basic features, ~70 Advanced features, podcast generation strategy, social/collaborative features, accessibility enhancements

---

## Section-to-File Mapping

| Section | Title | File | Lines |
|---------|-------|------|-------|
| **1** | **Curriculum & Syllabus Navigation** | [Core UI](mobile-features-core-ui.md) | 30-69 |
| 1.1 | Curriculum Selection | Core UI | 34-43 |
| 1.2 | Subject & Chapter Navigation | Core UI | 44-55 |
| 1.3 | Dashboard | Core UI | 56-69 |
| **2** | **Node-Level Features** | [Core UI](mobile-features-core-ui.md) | 70-165 |
| 2.1 | Text Node | Core UI | 74-90 |
| 2.2 | Story Node | Core UI | 91-107 |
| 2.3 | AI Node (Dynamic Content Node) | Core UI | 108-130 |
| 2.4 | Video Node (YouTube) | Core UI | 131-146 |
| 2.5 | Image Node | Core UI | 147-165 |
| **3** | **Canvas-Level Features** | [Core UI](mobile-features-core-ui.md) | 166-243 |
| 3.1 | Navigation | Core UI | 170-182 |
| 3.2 | Selection | Core UI | 183-194 |
| 3.3 | Layout | Core UI | 195-205 |
| 3.4 | Grid and Snap | Core UI | 206-214 |
| 3.5 | Background | Core UI | 215-223 |
| 3.6 | Canvas Constraints | Core UI | 224-243 |
| **4** | **Side Panel Features** | [Core UI](mobile-features-core-ui.md) | 244-310 |
| 4.1 | Bottom Sheet (Primary Panel) | Core UI | 248-261 |
| 4.2 | Node Properties Panel | Core UI | 262-273 |
| 4.3 | Settings Panel | Core UI | 274-291 |
| 4.4 | Previous Year Questions Panel | Core UI | 292-310 |
| **5** | **Top-Level Navigation** | [Core UI](mobile-features-core-ui.md) | 311-358 |
| 5.1 | Header Bar | Core UI | 315-326 |
| 5.2 | Bottom Navigation Bar | Core UI | 327-336 |
| 5.3 | Floating Action Button (FAB) | Core UI | 337-349 |
| 5.4 | Context Menus | Core UI | 350-358 |
| **6** | **AI Integration Features** | [AI Integration](mobile-features-ai-integration.md) | 30-220 |
| 6.1 | Node Toolbar AI Actions | AI Integration | 34-47 |
| 6.2 | Dedicated AI Panel ("Ask") | AI Integration | 48-64 |
| 6.3 | Context Menu AI Actions | AI Integration | 65-74 |
| 6.4 | AI-Powered Search | AI Integration | 75-85 |
| 6.5 | Learning-Specific AI Features | AI Integration | 86-101 |
| 6.5.1 | Question Discovery Flow | AI Integration | 102-150 |
| 6.5.2 | Phrase/Word Selection Exploration Flow | AI Integration | 151-195 |
| 6.6 | Perplexity Sonar Integration | AI Integration | 196-220 |
| **7** | **System-Level Features** | [System](mobile-features-system.md) | 30-162 |
| 7.1 | Authentication | System | 34-46 |
| 7.2 | Data Sync | System | 47-56 |
| 7.3 | Offline Mode | System | 57-69 |
| 7.4 | Notifications | System | 70-79 |
| 7.5 | Settings and Preferences | System | 80-90 |
| 7.6 | Export and Import | System | 91-100 |
| 7.7 | Performance and Optimization | System | 101-112 |
| 7.7.1 | Minimum Device Target Specifications | System | 113-130 |
| 7.8 | Privacy and Compliance | System | 131-162 |
| **8** | **Feature Summary by Priority** | [Enhancements](mobile-features-enhancements.md) | 30-94 |
| **9** | **Additional Feature Recommendations** | [Enhancements](mobile-features-enhancements.md) | 95-325 |
| 9.1 | Podcast Generation Features | Enhancements | 99-203 |
| 9.1.1-9.1.6 | Podcast subsections | Enhancements | 109-203 |
| 9.2 | Mobile-Specific Device Features | Enhancements | 204-221 |
| 9.3 | Learning Platform Enhancements | Enhancements | 222-264 |
| 9.4 | Social and Collaborative Features | Enhancements | 265-281 |
| 9.5 | Enhanced Accessibility Features | Enhancements | 282-301 |
| 9.6 | Missing Complementary Features | Enhancements | 302-325 |
| **10** | **Updated Feature Summary** | [Enhancements](mobile-features-enhancements.md) | 326-381 |

---

## AI Agent Usage Guidance

### For AI Coding Agents (Cursor, Aider, etc.)

**Context Window Optimization:**
- Each file is 162-381 lines (~2,400-5,700 tokens)
- Load only the file(s) relevant to your current task
- Avoid loading all 4 files simultaneously unless necessary

**Task-Based File Selection:**

| Task Type | Load This File | Why |
|-----------|---------------|-----|
| UI component implementation | Core UI | Contains all visual components and user interactions |
| AI/LLM integration | AI Integration | Contains all AI-powered features and API integrations |
| Backend infrastructure | System | Contains auth, sync, offline, performance, privacy |
| Feature planning/prioritization | Enhancements | Contains feature counts, priorities, recommendations |
| Multi-layer feature (e.g., AI node) | Core UI + AI Integration | Load both files for complete context |
| Full-stack feature (e.g., offline AI) | All 3 (Core UI + AI + System) | Load all relevant files |

**Best Practices:**
1. **Start with the index** (this file) to understand the overall structure
2. **Load specific files** based on your implementation task
3. **Cross-reference** between files using the section mapping table above
4. **Preserve design principles** (organic-first, syllabus-driven, category invisibility)
5. **Respect priority tiers** (Basic = essential, Advanced = enhancement)

---

## Related Documentation

- **Original specification**: `mobile-feature-specification.md` (preserved for reference, will be deprecated)
- **MVP features**: `mvp-features-specification.md` - Cross-references to mobile features
- **Architecture mapping**: `architecture-feature-mapping.md` - Maps features to system architecture
- **Market research**: `research/indian-student-market-analysis.md` - Target market analysis
- **System architecture**: `system-architecture.md` - Overall platform architecture

---

## Version Information

**Split Version**: 1.0  
**Original Specification Version**: 2.1  
**Split Date**: 2026-02-10  
**Split Rationale**: AI agent context window optimization (1,029 lines → 4 files of 162-381 lines each)

**File Breakdown:**
- Core UI Components: 358 lines (Sections 1-5)
- AI Integration: 220 lines (Section 6)
- System Features: 162 lines (Section 7)
- Enhancements & Summaries: 381 lines (Sections 8-10)
- **Total**: 1,121 lines (includes 4 document headers)

