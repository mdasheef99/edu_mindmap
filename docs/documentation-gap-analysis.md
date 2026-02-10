# Documentation Gap Analysis

**Document Version**: 1.0  
**Status**: Complete  
**Analysis Date**: February 2025  
**Analyzed Documents**: All conversation history + existing documentation in `/docs/`

---

## 1. Executive Summary

This gap analysis identifies documentation needs discovered through architectural discussions about the Categorical Exploration Learning Platform. The analysis covers database schemas, API endpoints, system components, integration workflows, and configuration thresholds discussed in conversation but not yet formally documented.

### Summary by Priority

| Priority | Count | Description |
|----------|-------|-------------|
| **Critical** | 4 | Blocks MVP/Phase 1 development |
| **High** | 8 | Needed for Phase 1-2 |
| **Medium** | 9 | Needed for Phase 3-5 |
| **Low** | 4 | Nice-to-have refinements |

---

## 2. Gap Analysis Table

### 2.1 Database Schema Gaps

| # | Gap Description | Priority | Suggested Document | Conversation Reference |
|---|-----------------|----------|-------------------|------------------------|
| D1 | **Complete `exploration_events` table schema** - Full DDL with all columns, indexes, partitioning strategy for high-throughput event ingestion | Critical | Create: `docs/database-schema-specification.md` | Path recording architecture discussion |
| D2 | **Complete `learning_sessions` table schema** - Session-level aggregation with path sequences, timestamps, device context | Critical | `docs/database-schema-specification.md` | Path recording architecture discussion |
| D3 | **Complete `path_patterns` table schema** - Aggregated patterns with library candidacy scores, caching status | Critical | `docs/database-schema-specification.md` | Content Library convergence discussion |
| D4 | **Complete `question_transitions` table schema** - Graph-like edge data for question-to-question transitions | High | `docs/database-schema-specification.md` | Path recording architecture discussion |
| D5 | **`question_bank` table schema** - Base question storage with categorical classification | High | `docs/database-schema-specification.md` | Question Analytics dashboard discussion |
| D6 | **`curriculum` schema** - Class, Exam, Subject, Chapter hierarchy tables | High | `docs/database-schema-specification.md` | Syllabus-driven architecture references |
| D7 | **`quiz_attempts` table schema** - Quiz performance tracking with category alignment | Medium | `docs/database-schema-specification.md` | Quiz checkpoint references |
| D8 | **`student_achievements` table schema** - Gamification milestone tracking | Low | `docs/database-schema-specification.md` | A.3 My Journey dashboard reference |
| D9 | **`teacher_classes` table schema** - Teacher-student linking for class management | Medium | `docs/database-schema-specification.md` | B.1 Class Overview dashboard |
| D10 | **`teacher_notes` table schema** - Private teacher notes on individual students | Low | `docs/database-schema-specification.md` | B.2 Individual Student View dashboard |
| D11 | **JSONB structure specifications** - `questions_presented`, `enhancements_applied`, `eligibility_snapshot`, etc. | High | `docs/database-schema-specification.md` | Multiple schema discussions |

### 2.2 API Endpoints & Data Flows

| # | Gap Description | Priority | Suggested Document | Conversation Reference |
|---|-----------------|----------|-------------------|------------------------|
| A1 | **Path Recording Ingestion API** - `/api/v1/events/exploration` endpoint with request/response schema, batching strategy | Critical | Create: `docs/api-specification.md` | Backend data flow discussion |
| A2 | **Session Management API** - Session start, pause, resume, end endpoints | High | `docs/api-specification.md` | Session persistence references |
| A3 | **Content Library Serving API** - Cache lookup → prefix match → LLM fallback flow | High | `docs/api-specification.md` | Novel path handling discussion |
| A4 | **A/B Test Assignment API** - Consistent hashing for group assignment | Medium | `docs/api-specification.md` | A/B testing engine discussion |
| A5 | **Question Generation API** - LLM orchestration for organic question generation | High | `docs/api-specification.md` | Two-stage LLM pipeline references |
| A6 | **Categorical Classification API** - Post-hoc classification endpoint | High | `docs/api-specification.md` | Post-hoc classification discussion |
| A7 | **Secondary Enhancement API** - Semantic tracking, contextual framing, linguistic framing | Medium | `docs/api-specification.md` | Secondary Enhancement system discussion |
| A8 | **Redis Streams Event Pipeline** - Complete specification of event ingestion via Redis Streams | High | `docs/api-specification.md` | High-throughput event pipeline |
| A9 | **Analytics Aggregation Jobs** - Celery job specifications for daily/weekly aggregations | Medium | `docs/api-specification.md` | Analytics aggregation references |

### 2.3 Features & System Components

| # | Gap Description | Priority | Suggested Document | Conversation Reference |
|---|-----------------|----------|-------------------|------------------------|
| F1 | **OrganicPreservationGuard** - Complete implementation specification beyond code snippet in access control doc | Medium | Merge into: `docs/teacher-access-control-specification.md` | Organic preservation discussion |
| F2 | **PromotionDecider** - Component that decides when A/B test variants should be promoted | Medium | Add to: `docs/teacher-access-control-specification.md` | Promotion metrics discussion |
| F3 | **InterventionPositionAdvisor** - Component that provides position guidance for interventions | Low | Add to: `docs/teacher-access-control-specification.md` | Position restriction discussion |
| F4 | **PathCachingManager** - Complete caching lifecycle: eligibility, generation, serving, eviction | High | Create: `docs/content-library-specification.md` | Content Library convergence discussion |
| F5 | **NovelPathHandler** - Exact match → prefix match → hybrid → full LLM generation flow | High | `docs/content-library-specification.md` | Novel path handling discussion |
| F6 | **LibraryMaturityTracker** - Tracks library phase (Learning → Convergence → Mature → Evergreen) | Medium | `docs/content-library-specification.md` | Four maturity phases discussion |
| F7 | **EnhancementVariantPrecomputer** - Pre-computes enhanced variants at library write time | Medium | `docs/content-library-specification.md` | Secondary Enhancement integration |
| F8 | **CategoryClassifier** - LLM-based post-hoc classification component | High | Add to: `docs/system-architecture.md` | Two-stage pipeline references |
| F9 | **DiagnosticEngine** - Generates categorical profile and gap analysis for teachers | Medium | Add to: `docs/system-architecture.md` | Teacher dashboard diagnostic features |

### 2.4 Integration & Workflow Specifications

| # | Gap Description | Priority | Suggested Document | Conversation Reference |
|---|-----------------|----------|-------------------|------------------------|
| I1 | **Event Pipeline Flow** - FastAPI → Redis Streams → Celery consumers → PostgreSQL complete specification | High | Create: `docs/event-pipeline-specification.md` or add to `docs/api-specification.md` | Backend architecture discussion |
| I2 | **Content Library Write-Time Flow** - When patterns get promoted to library, what happens | Medium | `docs/content-library-specification.md` | Library promotion discussion |
| I3 | **A/B Test Lifecycle Flow** - Draft → Running → Concluded → Promoted/Retired complete workflow | Medium | Add to: `docs/teacher-access-control-specification.md` | A/B testing engine discussion |
| I4 | **Staged Validation Pipeline** - How novel paths get validated and promoted to library | Medium | `docs/content-library-specification.md` | Novel path handling discussion |
| I5 | **Offline Sync Flow** - AsyncStorage ↔ Supabase synchronization specification | High | Add to: `docs/system-architecture.md` or `docs/mobile-feature-specification.md` | Offline-first architecture references |
| I6 | **Teacher Verification Flow** - How teachers get verified before applying for privileges | Low | Add to: `docs/teacher-access-control-specification.md` | Teacher verification references |

### 2.5 Configuration & Thresholds

| # | Gap Description | Priority | Suggested Document | Conversation Reference |
|---|-----------------|----------|-------------------|------------------------|
| C1 | **Content Library Thresholds** - MIN_SEQUENCE_FREQUENCY, MIN_PROBABILITY, MIN_SUCCESS_RATE documented but not in dedicated config file | Medium | Create: `docs/configuration-reference.md` | Content caching policy discussion |
| C2 | **Library Maturity Phase Thresholds** - When to transition between Learning → Convergence → Mature → Evergreen | Medium | `docs/configuration-reference.md` | Four maturity phases discussion |
| C3 | **A/B Test Statistical Thresholds** - Minimum sample size, significance level (p<0.05), minimum detectable effect | Medium | `docs/configuration-reference.md` | Promotion metrics discussion |
| C4 | **Warning Escalation Thresholds** - Complete warning trigger conditions and escalation path | Medium | Already in: `docs/teacher-access-control-specification.md` | Warning system discussion |
| C5 | **Mobile Performance Thresholds** - 60fps, <3s load, 150MB memory - scattered across docs | Low | `docs/configuration-reference.md` | Device specification references |
| C6 | **LLM Retry & Fallback Configuration** - Timeout, retry policy, fallback to cache behavior | High | `docs/configuration-reference.md` | Scalability discussion |

---

## 3. Recommended New Documentation Files

Based on the gap analysis, the following new documentation files should be created to achieve complete architectural coverage:

### 3.1 Critical Priority (Create First)

| File | Purpose | Gaps Addressed |
|------|---------|----------------|
| **`docs/database-schema-specification.md`** | Complete DDL for all database tables with indexes, constraints, JSONB structures, and partitioning strategies | D1-D11 |
| **`docs/api-specification.md`** | Complete API endpoint specification with request/response schemas, authentication, rate limiting | A1-A9, I1 |

### 3.2 High Priority (Create in Phase 1-2)

| File | Purpose | Gaps Addressed |
|------|---------|----------------|
| **`docs/content-library-specification.md`** | Complete specification of the Library-First Architecture including caching strategy, maturity phases, novel path handling, write-time processing | F4-F7, I2, I4, C1-C2 |
| **`docs/configuration-reference.md`** | Centralized reference for all configurable thresholds and parameters across the system | C1-C6 |

### 3.3 Medium Priority (Add to Existing Files)

| Action | File | Gaps Addressed |
|--------|------|----------------|
| Add A/B test lifecycle section | `docs/teacher-access-control-specification.md` | F2, F3, I3, I6 |
| Add offline sync specification | `docs/mobile-feature-specification.md` | I5 |
| Add CategoryClassifier component | `docs/system-architecture.md` | F8, F9 |

---

## 4. Gap Coverage Matrix

### 4.1 Current Documentation Coverage

| Document | Covers | Gaps |
|----------|--------|------|
| `system-architecture.md` | Core philosophy, LLM pipeline, collective intelligence, thresholds | Missing: CategoryClassifier details, DiagnosticEngine, offline sync |
| `mobile-feature-specification.md` | All mobile UI features, phase assignments | Missing: Offline sync specification |
| `teacher-access-control-specification.md` | Access tiers, privilege workflow, quality monitoring | Missing: PromotionDecider, InterventionPositionAdvisor, A/B lifecycle |
| `analytics-dashboard-inventory.md` | All dashboards with data sources and actions | Complete (just created) |
| `scalability-analysis.md` | Scale assessment, cost projections | Missing: LLM fallback configuration |
| `indian-student-market-analysis.md` | Market demographics, pricing strategy | Complete |

### 4.2 Coverage After Recommended Changes

| Category | Current Coverage | After Changes |
|----------|-----------------|---------------|
| Database Schema | ~30% (fragments in conversations) | 100% |
| API Endpoints | ~10% (implicit in architecture) | 100% |
| System Components | ~60% (architecture doc) | 95% |
| Integration Workflows | ~40% (scattered) | 90% |
| Configuration | ~50% (in architecture doc) | 100% |

---

## 5. Implementation Priority Matrix

### 5.1 Phase 1 (MVP Blockers)

Must document before development begins:

1. **D1**: `exploration_events` table - Core data collection
2. **D2**: `learning_sessions` table - Session persistence
3. **A1**: Path recording ingestion API - Event capture
4. **A5**: Question generation API - Core LLM functionality

### 5.2 Phase 2 (Early Development)

Document during initial development:

1. **D3**: `path_patterns` table - Content Library foundation
2. **D4-D6**: Remaining core tables
3. **A2-A3**: Session and content serving APIs
4. **F4-F5**: Caching manager and novel path handler
5. **C6**: LLM retry/fallback configuration

### 5.3 Phase 3-5 (Feature Development)

Document as features are built:

1. **A4, A7, A9**: A/B testing, enhancement, aggregation APIs
2. **F1-F3, F6-F9**: Advanced system components
3. **I2-I6**: Integration workflows
4. **D7-D11**: Supporting database tables
5. **C1-C5**: Configuration consolidation

---

## 6. Documentation Standards Recommendation

For consistency across new documentation:

### 6.1 Database Schema Files

```markdown
## Table: table_name

### Purpose
Brief description of what this table stores.

### DDL
```sql
CREATE TABLE table_name (
    -- columns with comments
);

-- Indexes
-- Constraints
-- Partitioning (if applicable)
```

### Relationships
- Belongs to: parent_table
- Has many: child_table

### JSONB Field Structures
Detailed structure for any JSONB columns.
```

### 6.2 API Endpoint Files

```markdown
## Endpoint: GET/POST /api/v1/resource

### Purpose
Brief description.

### Authentication
Required role/tier.

### Request
```json
{ "field": "type and constraints" }
```

### Response
```json
{ "field": "type and example" }
```

### Error Codes
| Code | Description |
```

---

## 7. Next Steps

1. **Immediate**: Create `docs/database-schema-specification.md` with critical tables (D1-D3)
2. **This Week**: Create `docs/api-specification.md` with core endpoints (A1, A5)
3. **This Sprint**: Create `docs/content-library-specification.md`
4. **Ongoing**: Update existing docs with missing sections as identified

---

*Document Version 1.0 | Documentation Gap Analysis*
*Last Updated: February 2025*

