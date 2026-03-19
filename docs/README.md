# Documentation Index

**Path-Based Conceptual Exploration and Teacher-Support Platform**  
**Repository**: `https://github.com/mdasheef99/edu_mindmap.git`  
**Last Updated**: March 2026

---

## Start Here

- **Understand the product and learning model**: start with `theory-of-change.md`, then `framework-design-philosophy.md`
- **Understand the system and implementation approach**: start with `system-architecture.md`, then `architecture/llm-pipeline.md`, then `mobile-features-index.md`
- **Understand current MVP scope boundaries**: use `prd/master-prd.md` and `mvp-features-specification.md` as the current scope anchors, including for basic offline access versus broader offline capability
- **Understand learner-facing guidance boundaries**: read `student-reflective-guidance-and-self-review.md` after the theory/system docs
- **Understand teacher-support MVP scope and broader teacher/admin references**: read `teacher-support-mvp-specification.md`, then `analytics-dashboard-inventory.md`, then `teacher-access-control-specification.md`

---

## Quick Navigation

### 📱 User-Facing Features
- **[Mobile Features - Master Index](mobile-features-index.md)** - Navigation guide for split mobile feature specification (193 lines)
- **[Mobile Features - Core UI](mobile-features-core-ui.md)** - Curriculum, nodes, canvas, panels, navigation (Sections 1-5, 358 lines)
- **[Mobile Features - AI Integration](mobile-features-ai-integration.md)** - AI-powered capabilities (Section 6, 220 lines)
- **[Mobile Features - System](mobile-features-system.md)** - Auth, sync, persistence, and narrow MVP basic offline access plus broader later offline references (Section 7, 162 lines)
- **[Mobile Features - Enhancements](mobile-features-enhancements.md)** - Feature priorities and recommendations (Sections 8-10, 381 lines)
- **[MVP Features Specification](mvp-features-specification.md)** - Current 19-feature MVP scope reference, including basic offline access boundary wording (492 lines)

### 🏗️ Architecture & Technical Design
- **[System Architecture](system-architecture.md)** - Core system design and high-level architecture (811 lines)
- **[LLM Pipeline](architecture/llm-pipeline.md)** - Two-stage question generation and classification (186 lines)
- **[Data Collection & Pattern Analysis](architecture/data-collection.md)** - Behavioral data and statistical analysis (236 lines)
- **[Architecture-Feature Mapping](architecture-feature-mapping.md)** - Maps V1 Master Strategy to mobile features (658 lines)
- **[Scalability Analysis](scalability-analysis.md)** - Scale assessment for Indian student market (535 lines)

### 📊 Analytics & Teacher Tools
- **[Teacher Support MVP Specification](teacher-support-mvp-specification.md)** - Bounded MVP teacher view and minimum access model
- **[Analytics Dashboard Inventory](analytics-dashboard-inventory.md)** - Complete dashboard feature inventory (714 lines)
- **[Teacher Access Control Specification](teacher-access-control-specification.md)** - Broader later-phase privilege and intervention reference (1,019 lines)
- **[Subject Weighting Specification](subject-weighting-specification.md)** - Subject-specific interpretive weighting for teacher-support analysis (326 lines)

### 🔬 Research & Market Analysis
- **[Indian Student Market Analysis](research/indian-student-market-analysis.md)** - Market demographics, device specs, connectivity (470 lines, consolidated)

### 📐 Framework & Philosophy
- **[Theory of Change](theory-of-change.md)** - Epistemological foundation and learning framework (261 lines)
- **[Framework Design Philosophy](framework-design-philosophy.md)** - Design principles and internal analytic framework (145 lines)
- **[Measurement and Experimentation](measurement-and-experimentation.md)** - Data collection and experimentation strategy (168 lines)
- **[Student Reflective Guidance Brief](student-reflective-guidance-brief.md)** - One-page internal product brief for the bounded learner-support layer
- **[Student Reflective Guidance and Self-Review](student-reflective-guidance-and-self-review.md)** - Future-facing student reflective guidance, self-review support, and next-step support capability

### 📚 Reference & Planning
- **[Content Library Specification](content-library-specification.md)** - Collective intelligence layer (94 lines)
- **[Documentation Gap Analysis](documentation-gap-analysis.md)** - Identifies missing documentation (251 lines)

---

## Document Organization

### By Development Phase

**Phase 1 (MVP - Basic Features)**
1. Mobile Features - Core UI, AI Integration, System (Sections 1-7)
2. MVP Features Specification (current 19-feature scope)
3. Teacher Support MVP Specification (bounded teacher-facing MVP scope)
4. System Architecture (Core components)
5. Indian Student Market Analysis (Device targets)

**Phase 2-3 (Advanced Features)**
1. Analytics Dashboard Inventory (Teacher dashboards)
2. Teacher Access Control Specification (Privilege system)
3. Subject Weighting Specification (subject-specific interpretive weighting)

**Phase 4-5 (Teacher & Advanced)**
1. Content Library Specification (Caching strategy)
2. Measurement and Experimentation (A/B testing)

### By Audience

**Developers**
- System Architecture
- Architecture-Feature Mapping
- Mobile Features - Master Index
- Scalability Analysis

**Product Managers**
- MVP Features Specification
- Indian Student Market Analysis
- Documentation Gap Analysis

**Researchers/Educators**
- Theory of Change
- Framework Design Philosophy
- Subject Weighting Specification

**Teachers/Administrators**
- Teacher Support MVP Specification
- Analytics Dashboard Inventory
- Teacher Access Control Specification

---

## Cross-Reference Map

### Most Referenced Documents

| Document | Referenced By | Reference Count |
|----------|---------------|-----------------|
| **mobile-features-*.md** (split files) | mvp-features-specification.md, architecture-feature-mapping.md, scalability-analysis.md | 25+ |
| **system-architecture.md** | mvp-features-specification.md, scalability-analysis.md, teacher-access-control-specification.md | 10+ |
| **indian-student-market-analysis.md** | mobile-features-system.md, mvp-features-specification.md, scalability-analysis.md | 8 |

### Documents with Most Outbound References

| Document | References To | Reference Count |
|----------|---------------|-----------------|
| **mvp-features-specification.md** | mobile-features-*.md (split files), architecture-feature-mapping.md, system-architecture.md | 22+ |
| **scalability-analysis.md** | indian-student-market-analysis.md, system-architecture.md, architecture-feature-mapping.md | 12 |
| **documentation-gap-analysis.md** | Planned future documents | 50+ |

---

## Document Status

| Document | Status | Last Major Update | Version |
|----------|--------|-------------------|---------|
| mobile-features-index.md | ✅ Current | Feb 2025 | 1.0 (Split) |
| mobile-features-core-ui.md | ✅ Current | Feb 2025 | 2.1 (Split) |
| mobile-features-ai-integration.md | ✅ Current | Feb 2025 | 2.1 (Split) |
| mobile-features-system.md | ✅ Current | Feb 2025 | 2.1 (Split) |
| mobile-features-enhancements.md | ✅ Current | Feb 2025 | 2.1 (Split) |
| mvp-features-specification.md | ✅ Current | Mar 2026 | 1.2 |
| teacher-support-mvp-specification.md | ✅ Current | Mar 2026 | 1.0 |
| system-architecture.md | ✅ Current | Feb 2025 | 1.0 |
| analytics-dashboard-inventory.md | ✅ Current | Feb 2025 | 1.0 |
| teacher-access-control-specification.md | 📎 Reference | Mar 2026 | 1.1 |
| indian-student-market-analysis.md | ✅ Current | Feb 2025 | 2.0 (Consolidated) |
| architecture-feature-mapping.md | ✅ Current | Feb 2025 | 1.0 |
| scalability-analysis.md | ✅ Current | Feb 2025 | 1.0 |
| subject-weighting-specification.md | ✅ Current | Feb 2025 | 1.0 |
| theory-of-change.md | ✅ Current | Feb 2025 | 2.0 |
| framework-design-philosophy.md | ✅ Current | Feb 2025 | 1.0 |
| measurement-and-experimentation.md | ✅ Current | Feb 2025 | 1.0 |
| content-library-specification.md | ⚠️ Needs Expansion | Feb 2025 | 1.0 |
| documentation-gap-analysis.md | ✅ Current | Feb 2025 | 1.0 |

---

## Recent Changes

### February 2025 - Documentation Reorganization

**Phase 1: Market Research Consolidation** ✅ COMPLETE
- ✅ Merged `indian-student-device-market-research.md` into `indian-student-market-analysis.md`
- ✅ Created `research/` subdirectory
- ✅ Updated 8 cross-references across 4 files
- ✅ Consolidated 634 lines → 470 lines (removed redundancy)

**Phase 2: System Architecture Split** ✅ COMPLETE
- ✅ Created `architecture/llm-pipeline.md` (186 lines) - LLM pipeline specification
- ✅ Created `architecture/data-collection.md` (236 lines) - Data collection and pattern analysis
- ✅ Reduced `system-architecture.md` from 1,209 → 811 lines (removed 398 lines)
- ✅ Added cross-references to new architecture files

**Phase 3: Content Library Expansion** ⏳ IN PROGRESS
- ⏳ Expand `content-library-specification.md` with details from system-architecture.md
- ⏳ Reduce Collective Intelligence section in system-architecture.md to high-level summary

---

*For questions or updates, see the repository: https://github.com/mdasheef99/edu_mindmap.git*

