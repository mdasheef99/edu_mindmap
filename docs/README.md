# Documentation Index

**Path-Based Conceptual Exploration and Teacher-Support Platform**  
**Repository**: `https://github.com/mdasheef99/edu_mindmap.git`  
**Last Updated**: March 2026 — v1.3+ architecture reconciliation

---

## Start Here

- **Understand the product and learning model**: start with `theory-of-change.md`, then `framework-design-philosophy.md`
- **Understand the system and implementation approach**: start with `architecture/backend-architecture.md`, the ADR sequence (`architecture/adr-log.md` then `architecture/adr-log-02.md`), and `planning/development-approach.md`, then use `system-architecture.md` as the reconciled high-level architecture map
- **Understand current MVP scope boundaries**: use `prd/master-prd.md`, `mvp-features-specification.md`, and the v1.3+ planning docs as the current scope anchors, including for basic offline access versus broader offline capability
- **Understand learner-facing guidance boundaries**: read `student-reflective-guidance-and-self-review.md` after the theory/system docs
- **Understand teacher-support MVP scope and broader teacher/admin references**: read `teacher-support-mvp-specification.md`, then `analytics-dashboard-inventory.md`, then `teacher-access-control-specification.md`

## Hierarchy of Truth

When documents conflict, apply this order:

1. `docs/planning/development-approach.md`, `docs/architecture/backend-architecture.md`, the ADR log sequence (`docs/architecture/adr-log.md` then active continuation `docs/architecture/adr-log-02.md`), and `docs/planning/session-path-data-contract.md` govern v1.3+ backend architecture, event sourcing, async jobs, read-model separation, and Category Invisibility.
2. `docs/prd/master-prd.md` and `docs/mvp-features-specification.md` govern product/MVP scope.
3. `docs/teacher-dashboard-specification.md`, `docs/teacher-support-mvp-specification.md`, and `docs/operations/b2b-onboarding-runbook.md` govern B2B/teacher support and access assumptions.
4. Older broad drafts remain useful reference material, but Redis, Celery, TimescaleDB, direct mobile AI-provider calls, broad offline sync, and broad intervention dashboards are deferred unless reaffirmed by the documents above.

**Documentation governance protocol:** active high-growth files are capped at 350 lines. When an
active ADR/worklog file would exceed the cap, continue in the next sequential file and begin it with
`AGENT ROTATION INSTRUCTION — READ FIRST` plus a `Legacy Context Summary` linking to the previous
file. Current active ADR continuation: `docs/architecture/adr-log-02.md`. Current active worklog:
`docs/planning/worklog-v2.md`; `docs/planning/worklog.md` is the closed first archive.

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
- **[Backend Architecture](architecture/backend-architecture.md)** - v1.3+ FastAPI modular monolith, event store, read models, worker lane, and API surface
- **[ADR Log Sequence](architecture/adr-log-02.md)** - active ADR continuation; previous ADRs 0001–0014 are in `architecture/adr-log.md`
- **[System Architecture](system-architecture.md)** - Reconciled high-level system design; older scale technologies annotated as deferred
- **[API Documentation Index](api/README.md)** - `/v1/student` and `/v1/teacher` API source of truth and boundary rules
- **[Student API Specification](api/student-api-spec.md)** - student-safe session, canvas, offer-set, checkpoint, podcast, and PYQ endpoints
- **[Teacher API Specification](api/teacher-api-spec.md)** - consent-gated teacher dashboard endpoint contracts
- **[API Traceability Matrix](api/feature-endpoint-traceability.md)** - feature → endpoint → event → read model → worker job mapping
- **[Database Schema Index](database/README.md)** - database conventions, namespaces, and Category Invisibility rules
- **[Event Store and Job Queue Schema](database/event-store-and-job-queue-schema.md)** - append-only events and Postgres `SKIP LOCKED` jobs
- **[Core Operational Schema](database/core-operational-schema.md)** - tenancy, membership, consent, curriculum, PYQ, and media metadata
- **[Read Models Schema](database/read-models-schema.md)** - physically separate `student_rm` and `analytic_rm` schemas
- **[Schema Traceability and Validation](database/schema-traceability-and-validation.md)** - database-layer traceability and validation checks
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
- **[Development Approach](planning/development-approach.md)** - pinned MVP stack and phase gates
- **[Configuration Reference](configuration-reference.md)** - thresholds, limits, environment variable names, and operational defaults
- **[Delivery and Operations Runbook](operations/delivery-and-operations.md)** - environments, deployment, migrations, secrets, observability, backup/restore
- **[Development Worklog](planning/worklog.md)** - implementation progress and decision log
- **[Session Path Data Contract](planning/session-path-data-contract.md)** - event-sourced session/path contract and offline boundary
- **[Release Critical User Flows](planning/release-critical-user-flows.md)** - end-to-end validation paths

---

## Document Organization

### By Development Phase

**Phase 1 (MVP - Basic Features)**
1. Mobile Features - Core UI, AI Integration, System (Sections 1-7)
2. MVP Features Specification (current 19-feature scope)
3. Backend Architecture + ADR Log (FastAPI modular monolith, events, jobs, read-model split)
4. API Documentation + Database Schema Specification (student/teacher contracts and persistence boundaries)
5. Teacher Support MVP Specification + Teacher Dashboard Specification (bounded B2B teacher scope)
6. System Architecture (reconciled high-level map)
7. Indian Student Market Analysis (Device targets)

**Phase 2-3 (Advanced Features)**
1. Analytics Dashboard Inventory (Teacher dashboards)
2. Teacher Access Control Specification (Privilege system)
3. Subject Weighting Specification (subject-specific interpretive weighting)

**Phase 4-5 (Teacher & Advanced)**
1. Content Library Specification (Caching strategy)
2. Measurement and Experimentation (A/B testing)

### By Audience

**Developers**
- Backend Architecture
- ADR Log
- Development Approach
- Session Path Data Contract
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
| mobile-features-ai-integration.md | ✅ Reconciled | Mar 2026 | 2.1 + v1.3 alignment |
| mobile-features-system.md | ✅ Reconciled | Mar 2026 | 2.1 + v1.3 alignment |
| mobile-features-enhancements.md | ✅ Current | Feb 2025 | 2.1 (Split) |
| mvp-features-specification.md | ✅ Reconciled | Mar 2026 | 1.2 + v1.3 alignment |
| teacher-support-mvp-specification.md | ✅ Reconciled | Mar 2026 | 1.0 + v1.3 alignment |
| teacher-dashboard-specification.md | ✅ Current | Mar 2026 | 1.0 draft |
| api/README.md | ✅ Current | Jun 2026 | 1.0 draft |
| api/student-api-spec.md | ✅ Current | Jun 2026 | 1.0 draft |
| api/teacher-api-spec.md | ✅ Current | Jun 2026 | 1.0 draft |
| api/feature-endpoint-traceability.md | ✅ Current | Jun 2026 | 1.0 draft |
| database/README.md | ✅ Current | Jun 2026 | 1.0 draft |
| database/event-store-and-job-queue-schema.md | ✅ Current | Jun 2026 | 1.0 draft |
| database/core-operational-schema.md | ✅ Current | Jun 2026 | 1.0 draft |
| database/read-models-schema.md | ✅ Current | Jun 2026 | 1.0 draft |
| database/schema-traceability-and-validation.md | ✅ Current | Jun 2026 | 1.0 draft |
| configuration-reference.md | ✅ Current | Jun 2026 | 1.0 draft |
| operations/delivery-and-operations.md | ✅ Current | Jun 2026 | 1.0 draft |
| planning/worklog.md | ✅ Active | Jun 2026 | 1.0 |
| architecture/backend-architecture.md | ✅ Source of Truth | Mar 2026 | v1.3+ |
| architecture/adr-log.md | 🔒 Rotated Source Archive | Jun 2026 | ADR-0001–0014 |
| architecture/adr-log-02.md | ✅ Active Source of Truth | Jun 2026 | starts ADR-0015 |
| planning/development-approach.md | ✅ Source of Truth | Mar 2026 | v1.3+ |
| planning/session-path-data-contract.md | ✅ Reconciled | Mar 2026 | v1.3+ |
| system-architecture.md | ✅ Reconciled | Mar 2026 | 1.0 + v1.3 alignment |
| analytics-dashboard-inventory.md | ✅ Current | Feb 2025 | 1.0 |
| teacher-access-control-specification.md | 📎 Reference | Mar 2026 | 1.1 |
| indian-student-market-analysis.md | ✅ Current | Feb 2025 | 2.0 (Consolidated) |
| architecture-feature-mapping.md | ✅ Reconciled | Mar 2026 | 1.0 + v1.3 alignment |
| scalability-analysis.md | ✅ Current | Feb 2025 | 1.0 |
| subject-weighting-specification.md | ✅ Current | Feb 2025 | 1.0 |
| theory-of-change.md | ✅ Current | Feb 2025 | 2.0 |
| framework-design-philosophy.md | ✅ Current | Feb 2025 | 1.0 |
| measurement-and-experimentation.md | ✅ Current | Feb 2025 | 1.0 |
| content-library-specification.md | ⚠️ Needs Expansion | Feb 2025 | 1.0 |
| documentation-gap-analysis.md | ✅ Current | Feb 2025 | 1.0 |

---

## Recent Changes

### March 2026 - v1.3+ Architecture Reconciliation

- ✅ Added API documentation suite for `/v1/student` and `/v1/teacher`
- ✅ Added database schema specification suite for events, jobs, core operational tables, read models, and validation
- ✅ Added configuration reference, delivery/operations baseline, and development worklog

- ✅ Pivoted backend references to FastAPI modular monolith + Supabase PostgreSQL data platform
- ✅ Marked Redis, Celery, and TimescaleDB as deferred scale forms
- ✅ Aligned AI integration with backend-managed LLM Gateway and no mobile-side provider credentials
- ✅ Reinforced Category Invisibility through separate `student_rm` / `analytic_rm` read models
- ✅ Resolved teacher entry point as V1 class overview → student/chapter drill-down
- ✅ Tightened basic offline access to exclude queued sync/conflict resolution

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

