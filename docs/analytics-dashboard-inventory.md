
# Analytics & Dashboard Inventory

**Document Version**: 1.0  
**Status**: Draft  
**Last Updated**: February 2025  
**Related Documents**: `system-architecture.md`, `mobile-feature-specification.md`, `teacher-access-control-specification.md`

---

## 1. Executive Summary

This document provides a complete inventory of all dashboard sections and analytics features for the Categorical Exploration Learning Platform. It covers student-facing, teacher-facing, and administrator dashboards, with detailed specifications for each component including data sources, user actions, development phases, and access requirements.

### Core Principles

1. **Category Invisibility (Students)**: All student-facing dashboards must NOT expose categorical dimensions
2. **Category Visibility (Teachers)**: Teacher dashboards are the ONLY place where 8 Kantian categories are visible
3. **Tiered Access**: Different dashboard capabilities based on user role/tier
4. **Tier-Aligned**: Features are assigned to priority tiers (MVP → Teacher)

---

## 2. Overview Structure

### 2.1 Dashboard Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DASHBOARD & ANALYTICS HIERARCHY                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  A. STUDENT-FACING DASHBOARDS (Category-Invisible)                          │
│  ─────────────────────────────────────────────────                          │
│     ├── A.1 Main Dashboard ────────────────────────────────── MVP           │
│     ├── A.2 Learning Stats ────────────────────────────────── Extended      │
│     ├── A.3 My Journey (Exploration Path Visualization) ──── Advanced      │
│     └── A.4 Weekly Exploration Report ─────────────────────── Advanced      │
│                                                                              │
│  B. TEACHER-FACING DASHBOARDS (Category-Visible)                            │
│  ───────────────────────────────────────────────                            │
│     ├── B.1 Class Overview ────────────────────────────────── Teacher       │
│     ├── B.2 Individual Student View ───────────────────────── Teacher       │
│     ├── B.3 Question Analytics ────────────────────────────── Teacher       │
│     └── B.4 Intervention Tools (Tier 2 only) ──────────────── Teacher       │
│                                                                              │
│  C. ADMINISTRATOR DASHBOARDS                                                │
│  ────────────────────────────                                               │
│     ├── C.1 Platform Health ───────────────────────────────── Teacher       │
│     ├── C.2 Content Quality Monitoring ────────────────────── Teacher       │
│     ├── C.3 Teacher Management ────────────────────────────── Teacher       │
│     └── C.4 A/B Test Overview ─────────────────────────────── Teacher       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Access Control Mapping

| Dashboard | Student | Teacher (Tier 1) | Approved Teacher (Tier 2) | Admin (Tier 3) |
|-----------|---------|------------------|---------------------------|----------------|
| A.1 Main Dashboard | ✅ | ❌ | ❌ | ❌ |
| A.2 Learning Stats | ✅ | ❌ | ❌ | ❌ |
| A.3 My Journey | ✅ | ❌ | ❌ | ❌ |
| A.4 Weekly Report | ✅ | ❌ | ❌ | ❌ |
| B.1 Class Overview | ❌ | ✅ | ✅ | ✅ |
| B.2 Individual Student View | ❌ | ✅ | ✅ | ✅ |
| B.3 Question Analytics | ❌ | ✅ | ✅ | ✅ |
| B.4 Intervention Tools | ❌ | ❌ | ✅ | ✅ |
| C.1 Platform Health | ❌ | ❌ | ❌ | ✅ |
| C.2 Content Quality | ❌ | ❌ | ❌ | ✅ |
| C.3 Teacher Management | ❌ | ❌ | ❌ | ✅ |
| C.4 A/B Test Overview | ❌ | ❌ | ❌ | ✅ |

---

## 3. Student-Facing Dashboards (Category-Invisible)

> **CRITICAL**: All student-facing dashboards must enforce strict category invisibility.
> Students never see categorical labels, radar charts, or dimension names.
> This ensures organic exploration without "gaming" the system.

### A.1 Main Dashboard

| Attribute | Specification |
|-----------|---------------|
| **Phase** | MVP |
| **Access** | All authenticated students |
| **UI Location** | Bottom nav → "Home" |
| **Dependencies** | Authentication, Session persistence, Curriculum data |
| **Category Visibility** | ❌ **STRICTLY INVISIBLE** |

#### Data Displayed

| Section | Data | Source Table/API | Notes |
|---------|------|------------------|-------|
| Continue Learning Card | Last active chapter, session timestamp, resume button | `learning_sessions` | Shows most recent incomplete session |
| Recent Sessions List | Last 5 sessions (chapter name, date, duration) | `learning_sessions` | Chronological order |
| Daily Streak Counter | Consecutive days of activity | Computed from `exploration_events` | Gamification element |
| Subjects Grid | Available subjects for selected exam | `curriculum.subjects` | 2-column card grid |
| Browse New Topic | Quick access to subject/chapter selection | Navigation only | Entry point for new learning |

#### User Actions

| Action | Description | Implementation |
|--------|-------------|----------------|
| Resume last session | Continue from saved mind map state | Load from AsyncStorage + Supabase |
| Start new session | Navigate to subject/chapter selection | Navigation |
| View session history | See recent sessions | Expand recent sessions list |
| Select subject | Navigate to chapter list | Navigation with exam filter |

---

### A.2 Learning Stats

| Attribute | Specification |
|-----------|---------------|
| **Phase** | Extended |
| **Access** | All authenticated students |
| **UI Location** | Profile → "Learning Stats" |
| **Dependencies** | Analytics aggregation, Session data |
| **Category Visibility** | ❌ **STRICTLY INVISIBLE** |

#### Data Displayed

| Metric | Data | Source | Aggregation |
|--------|------|--------|-------------|
| Days Active | Total days with learning activity | `exploration_events` | COUNT(DISTINCT date) |
| Questions Explored | Total questions selected | `exploration_events` | COUNT(*) |
| Boards Created | Mind map boards count | `boards` | COUNT(*) |
| Total Study Time | Aggregate session duration | `learning_sessions` | SUM(duration_ms) |
| Chapters Explored | Unique chapters count | `learning_sessions` | COUNT(DISTINCT chapter_id) |
| Average Session Length | Mean session duration | `learning_sessions` | AVG(duration_ms) |
| Current Streak | Consecutive activity days | Computed | Days since last gap |
| Best Streak | Longest consecutive streak | Computed | Historical max |

#### User Actions

| Action | Description | Notes |
|--------|-------------|-------|
| View stats | Read-only display | No category information exposed |
| Share stats | Share progress summary | Optional, anonymized |

---

### A.3 My Journey (Exploration Path Visualization)

| Attribute | Specification |
|-----------|---------------|
| **Phase** | Advanced |
| **Access** | All authenticated students |
| **UI Location** | Profile → "My Journey" |
| **Dependencies** | Path recording system, Session persistence, Visualization engine |
| **Category Visibility** | ❌ **STRICTLY INVISIBLE** |

#### Data Displayed

| Section | Data | Source | Notes |
|---------|------|--------|-------|
| Exploration Timeline | Visual timeline of learning sessions | `learning_sessions` | Scrollable vertical timeline |
| Session Path Cards | Per-session: chapter, questions explored, duration | `exploration_events` | Expandable cards |
| Path Visualization | Mini mind-map showing explored questions per session | `exploration_events` | Read-only visual |
| Chapter Coverage | Progress indicators per chapter | Computed aggregation | "X questions explored" |
| Milestone Badges | Achievements (first session, 10 chapters, etc.) | `student_achievements` | Gamification |

#### User Actions

| Action | Description | Notes |
|--------|-------------|-------|
| Browse timeline | Scroll through learning history | Read-only |
| Expand session | View detailed path for a session | Shows questions without categories |
| View coverage | See exploration progress per chapter | No category breakdown |
| Replay session | Resume from a previous session point | Optional feature |

---

### A.4 Weekly Exploration Report

| Attribute | Specification |
|-----------|---------------|
| **Phase** | Advanced |
| **Access** | All authenticated students |
| **UI Location** | Push notification + Profile → "Reports" |
| **Dependencies** | Analytics aggregation jobs, Notification system |
| **Category Visibility** | ❌ **STRICTLY INVISIBLE** |

#### Data Displayed

| Metric | Data | Aggregation | Notes |
|--------|------|-------------|-------|
| Week Summary | Total time, sessions, questions | SUM over 7 days | Top-level stats |
| Daily Breakdown | Activity per day | Daily aggregates | Bar chart |
| Top Chapters | Most explored chapters this week | COUNT by chapter | Top 3-5 |
| Streak Status | Current streak + comparison to last week | Computed | Motivational |
| Personal Best | Any new records achieved | Compare to historical max | Celebration moments |
| Suggested Next | Recommended chapters to explore | Based on coverage gaps | No category exposure |

#### User Actions

| Action | Description | Notes |
|--------|-------------|-------|
| View weekly report | Read-only summary | Auto-generated every Sunday |
| Share report | Export summary image | Social sharing |
| View historical reports | Access past weeks | Archive of reports |
| Set goals | Optional weekly goals | Future enhancement |

---

## 4. Teacher-Facing Dashboards (Category-Visible)

> **IMPORTANT**: Teacher dashboards are the ONLY location where categorical dimensions
> (Define, Distinguish, Decompose, Connect, Delimit, Predict, Contextualize, Vary) are visible.
> This visibility is essential for pedagogical diagnosis but must never leak to students.

### B.1 Class Overview

| Attribute | Specification |
|-----------|---------------|
| **Phase** | Teacher |
| **Access** | All Teachers (Tier 1+) |
| **UI Location** | Teacher Dashboard → "My Classes" |
| **Dependencies** | Teacher-student linking, Analytics aggregation, Categorical classification |
| **Category Visibility** | ✅ **VISIBLE** (aggregate only) |

#### Data Displayed

| Section | Data | Source | Notes |
|---------|------|--------|-------|
| Class List | All linked classes with student counts | `teacher_classes` | Selectable cards |
| Class Engagement | Active students, avg sessions/week | `learning_sessions` | Rolling 7-day |
| Class Categorical Radar | Aggregate categorical profile for entire class | `exploration_events` + classification | 8-dimension radar chart |
| Category Gaps | Top 3 weak categories across class | Computed from radar | "Class struggles with Decompose" |
| Top Performers | Students with highest engagement | Ranked by sessions/time | Top 5 |
| At-Risk Students | Students with declining activity | Trend analysis | Requires 2+ weeks data |
| Chapter Coverage | Class-wide progress per chapter | Aggregated coverage | Heatmap view |

#### User Actions

| Action | Description | Notes |
|--------|-------------|-------|
| Select class | View specific class details | Navigation |
| View categorical breakdown | See 8-dimension radar for class | Aggregate only |
| Identify gaps | See which categories need attention | Actionable insight |
| Export report | Generate PDF class report | Optional |
| Drill into student | Navigate to individual student view | Link to B.2 |

---

### B.2 Individual Student View

| Attribute | Specification |
|-----------|---------------|
| **Phase** | Teacher |
| **Access** | All Teachers (Tier 1+) |
| **UI Location** | Teacher Dashboard → Class → Student Card |
| **Dependencies** | Teacher-student linking, Individual analytics, Categorical classification |
| **Category Visibility** | ✅ **VISIBLE** (individual profile) |

#### Data Displayed

| Section | Data | Source | Notes |
|---------|------|--------|-------|
| Student Profile | Name, class, exam, joined date | `user_profiles` | Basic info |
| Engagement Summary | Sessions, time, questions explored | `learning_sessions` | Lifetime + recent |
| **Categorical Exploration Radar** | 8-dimension radar showing student's categorical profile | `exploration_events` + classification | **Key diagnostic tool** |
| Category Trend | How each category has changed over time | Time-series aggregation | Sparkline per category |
| Strength Categories | Top 2-3 categories student explores | Ranked by selection frequency | "Strong in Define, Connect" |
| Gap Categories | Bottom 2-3 categories student avoids | Ranked by selection frequency | "Rarely explores Predict, Vary" |
| Chapter-by-Chapter Profile | Categorical breakdown per chapter | Pivot table | Detailed view |
| Path Pattern Analysis | Common exploration patterns | `path_patterns` | Shows preferred sequences |
| Quiz Performance | Scores by chapter and category | `quiz_attempts` | Category-aligned scoring |

#### Categorical Exploration Radar Specification

```
                    Define
                      ▲
                     /|\
                    / | \
          Vary ────/  |  \──── Distinguish
                 /    |    \
                /     |     \
    Contextualize ────┼──── Decompose
                \     |     /
                 \    |    /
        Predict ──\   |   /── Connect
                   \  |  /
                    \ | /
                     \|/
                    Delimit

    Each axis: 0-100 scale (percentage of questions explored in that category)
    Radar shows: Current profile vs. class average (overlay)
    Color coding: Green (strength), Yellow (average), Red (gap)
```

#### User Actions

| Action | Description | Notes |
|--------|-------------|-------|
| View radar | See categorical profile | Primary diagnostic |
| Compare to class | Overlay class average on radar | Contextual insight |
| View trends | See category changes over time | Requires 2+ weeks data |
| View chapter breakdown | Drill into per-chapter profile | Detailed analysis |
| Add notes | Private teacher notes on student | Stored in `teacher_notes` |
| Flag for intervention | Mark for targeted support | Links to intervention tools |

---

### B.3 Question Analytics

| Attribute | Specification |
|-----------|---------------|
| **Phase** | Teacher |
| **Access** | All Teachers (Tier 1+) |
| **UI Location** | Teacher Dashboard → "Question Analytics" |
| **Dependencies** | Question bank, Selection metrics, Categorical classification |
| **Category Visibility** | ✅ **VISIBLE** (per-question categorization) |

#### Data Displayed

| Section | Data | Source | Notes |
|---------|------|--------|-------|
| Question Browser | Searchable/filterable question list | `question_bank` | Filter by chapter, category |
| Question Details | Question text, category, metadata | `question_bank` | Single question view |
| Selection Metrics | Presentation count, selection rate, position bias | `question_transitions` | How often selected when shown |
| Engagement Metrics | Time spent, follow-up selections | `exploration_events` | Engagement depth |
| Category Distribution | Distribution of questions by category | Aggregation | Overall content balance |
| Popular Questions | Most frequently selected questions | Ranked list | Class or platform-wide |
| Avoided Questions | Low selection rate questions | Ranked list | May indicate issues |
| Category Performance | How each category performs on selection | Category aggregates | Which categories engage students |

#### User Actions

| Action | Description | Notes |
|--------|-------------|-------|
| Browse questions | Search and filter question bank | Read-only for Tier 1 |
| View question detail | See full question with metrics | Read-only |
| Filter by category | Show only specific category | 8 category filters |
| Filter by chapter | Show only specific chapter | Chapter selector |
| View selection trends | See how selection changes over time | Time-series view |
| Identify engagement issues | Find low-performing questions | Diagnostic |

---

### B.4 Intervention Tools (Tier 2 Only)

| Attribute | Specification |
|-----------|---------------|
| **Phase** | Teacher |
| **Access** | **Approved Teachers Only (Tier 2+)** |
| **UI Location** | Teacher Dashboard → "Intervention Tools" |
| **Dependencies** | Privilege approval, A/B testing engine, Organic preservation guard |
| **Category Visibility** | ✅ **VISIBLE** (for variant targeting) |

#### Data Displayed

| Section | Data | Source | Notes |
|---------|------|--------|-------|
| My Variants | All question variants created by teacher | `question_variants` | Status, metrics |
| My Interventions | Active and pending interventions | `path_interventions` | Deployment status |
| My A/B Tests | Running and concluded tests | `ab_tests` | Results, significance |
| Limits & Quotas | Current usage vs. limits | `teacher_quality_metrics` | "10/20 active interventions" |
| Promotion Queue | Variants ready for promotion | Test results | Pending action |
| Quality Metrics | Personal promotion rate, lifts | `teacher_quality_metrics` | Self-assessment |
| Warnings | Any active warnings | `teacher_quality_metrics` | Alert status |

#### User Actions

| Action | Description | Notes |
|--------|-------------|-------|
| Create variant | Write enhanced question version | Opens variant editor |
| Deploy intervention | Place variant on a path | Requires path selection |
| Start A/B test | Begin testing variant vs. organic | Traffic allocation |
| View test results | See ongoing test metrics | Real-time stats |
| Promote variant | Mark winning variant as default | Post-test action |
| Retire variant | Remove underperforming variant | Cleanup action |
| View quality dashboard | See personal metrics | Self-monitoring |

---

## 5. Administrator Dashboards (Tier 3 Only)

> **ACCESS**: All administrator dashboards are restricted to Tier 3 (platform administrators only).
> These dashboards provide system-wide visibility and control capabilities.

### C.1 Platform Health Dashboard

| Attribute | Specification |
|-----------|---------------|
| **Phase** | Teacher |
| **Access** | **Administrators Only (Tier 3)** |
| **UI Location** | Admin Console → "Platform Health" |
| **Dependencies** | Observability stack (Sentry, Grafana), System metrics |
| **Category Visibility** | N/A (system metrics) |

#### Data Displayed

| Section | Data | Source | Notes |
|---------|------|--------|-------|
| Active Users | Current DAU, WAU, MAU | Analytics aggregation | Real-time counter |
| Session Metrics | Active sessions, avg duration | `learning_sessions` | Live metrics |
| API Performance | Latency percentiles, error rates | Sentry/Grafana | p50, p95, p99 |
| LLM API Status | Anthropic/OpenAI response times, costs | API monitoring | Critical for cost control |
| Cache Performance | Redis hit rates, latency | Redis metrics | Library effectiveness |
| Database Health | Connection pool, query times | PostgreSQL metrics | Supabase stats |
| Error Log | Recent errors with stack traces | Sentry | Filterable |
| Cost Dashboard | Daily/weekly/monthly API costs | Cost tracking | Budget monitoring |

#### User Actions

| Action | Description | Notes |
|--------|-------------|-------|
| View real-time metrics | Monitor live system health | Auto-refresh |
| Drill into errors | View error details | Sentry integration |
| View cost breakdown | Analyze API spending | By endpoint/feature |
| Set alerts | Configure threshold alerts | Notification rules |
| View historical trends | See metrics over time | Time range selector |

---

### C.2 Content Quality Monitoring

| Attribute | Specification |
|-----------|---------------|
| **Phase** | Teacher |
| **Access** | **Administrators Only (Tier 3)** |
| **UI Location** | Admin Console → "Content Quality" |
| **Dependencies** | Content Library, A/B testing engine, Quality metrics |
| **Category Visibility** | ✅ **VISIBLE** (for content classification review) |

#### Data Displayed

| Section | Data | Source | Notes |
|---------|------|--------|-------|
| Library Status | Total paths, coverage %, phase | `path_patterns` | Library maturity |
| Library Growth | Paths added per week | Time-series | Convergence tracking |
| LLM vs. Cached | Percentage of requests from each source | Serving logs | Cost efficiency |
| Content Quality Scores | Average quality metrics for library content | `path_patterns` | Quality assurance |
| Low-Performing Content | Paths with declining metrics | Quality analysis | Candidates for refresh |
| Category Balance | Distribution of content across 8 categories | Aggregation | Content health |
| Flagged Content | User-reported or auto-flagged issues | Flag system | Review queue |
| Organic Preservation | Actual organic floor percentage | Serving logs | Must stay ≥30% |

#### User Actions

| Action | Description | Notes |
|--------|-------------|-------|
| Review flagged content | Approve or remove flagged items | Moderation |
| Adjust quality thresholds | Modify promotion criteria | Configuration |
| Force content refresh | Regenerate specific paths | Manual override |
| View category distribution | Analyze content balance | Balance monitoring |
| Export quality report | Generate quality audit report | Compliance |

---

### C.3 Teacher Management

| Attribute | Specification |
|-----------|---------------|
| **Phase** | Teacher |
| **Access** | **Administrators Only (Tier 3)** |
| **UI Location** | Admin Console → "Teacher Management" |
| **Dependencies** | User profiles, Privilege system, Quality metrics |
| **Category Visibility** | ✅ **VISIBLE** (for privilege management) |

#### Data Displayed

| Section | Data | Source | Notes |
|---------|------|--------|-------|
| Teacher Directory | All teachers with role/status | `user_profiles` | Searchable list |
| Privilege Applications Queue | Pending applications | `privilege_applications` | Review queue |
| Approved Teachers | Tier 2 teachers with metrics | `teacher_quality_metrics` | Performance monitoring |
| At-Risk Teachers | Teachers with warnings/low metrics | Quality analysis | Intervention candidates |
| Revocation History | Past privilege revocations | `intervention_audit_log` | Audit trail |
| Activity Summary | Teacher login/usage patterns | Activity tracking | Engagement monitoring |
| Intervention Impact | Aggregate impact of teacher interventions | A/B test results | Overall teacher value |

#### User Actions

| Action | Description | Notes |
|--------|-------------|-------|
| Review application | Approve/reject privilege application | Decision workflow |
| Request more info | Ask applicant for clarification | Application workflow |
| View teacher detail | See full teacher profile and metrics | Drill-down |
| Issue warning | Formal warning for policy issues | Escalation action |
| Suspend privileges | Temporary privilege suspension | Enforcement action |
| Revoke privileges | Permanent privilege removal | Serious enforcement |
| Adjust limits | Modify teacher's intervention limits | Trust-based adjustment |
| Export audit log | Download teacher activity history | Compliance |

---

### C.4 A/B Test Overview

| Attribute | Specification |
|-----------|---------------|
| **Phase** | Teacher |
| **Access** | **Administrators Only (Tier 3)** |
| **UI Location** | Admin Console → "A/B Tests" |
| **Dependencies** | A/B testing engine, Statistical analysis |
| **Category Visibility** | ✅ **VISIBLE** (for test analysis) |

#### Data Displayed

| Section | Data | Source | Notes |
|---------|------|--------|-------|
| Active Tests | All running A/B tests platform-wide | `ab_tests` | Status, progress |
| Test Queue | Tests awaiting start/approval | `ab_tests` | Pending items |
| Concluded Tests | Historical test results | `ab_tests` | Winners, lifts |
| Test by Teacher | Tests grouped by creator | Join query | Teacher attribution |
| Statistical Health | Tests with significance issues | Statistical analysis | Underpowered tests |
| High-Traffic Tests | Tests on popular paths | Traffic analysis | High-impact tests |
| Promotion Pipeline | Tests with winners ready to promote | Test results | Action queue |
| System-Wide Impact | Aggregate impact of all interventions | Meta-analysis | Platform ROI |

#### User Actions

| Action | Description | Notes |
|--------|-------------|-------|
| View test detail | See full test configuration and results | Drill-down |
| Override test | Force conclude or cancel a test | Emergency action |
| Approve high-traffic test | Approve test on popular path | Gatekeeping |
| View statistical analysis | See detailed significance calculations | Verification |
| Bulk promote | Promote multiple winning variants | Efficiency action |
| Export test report | Generate PDF test summary | Reporting |

---

## 6. Analytics Features Summary

### 6.1 Student Analytics Features

| Feature | Dashboard | Phase | Data Source | Category Visible |
|---------|-----------|-------|-------------|------------------|
| Session resume | A.1 Main | MVP | `learning_sessions` | ❌ |
| Daily streak | A.1 Main | MVP | `exploration_events` | ❌ |
| Total study time | A.2 Stats | Extended | `learning_sessions` | ❌ |
| Questions explored count | A.2 Stats | Extended | `exploration_events` | ❌ |
| Chapter coverage | A.2 Stats | Extended | `learning_sessions` | ❌ |
| Exploration timeline | A.3 Journey | Advanced | `learning_sessions` | ❌ |
| Path visualization | A.3 Journey | Advanced | `exploration_events` | ❌ |
| Weekly summary | A.4 Report | Advanced | Aggregation | ❌ |
| Personal bests | A.4 Report | Advanced | Historical max | ❌ |

### 6.2 Teacher Analytics Features

| Feature | Dashboard | Phase | Data Source | Category Visible |
|---------|-----------|-------|-------------|------------------|
| Class engagement summary | B.1 Class | Teacher | `learning_sessions` | ✅ |
| Class categorical radar | B.1 Class | Teacher | Classification | ✅ |
| Class category gaps | B.1 Class | Teacher | Computed | ✅ |
| At-risk student alerts | B.1 Class | Teacher | Trend analysis | ✅ |
| Individual categorical radar | B.2 Student | Teacher | Classification | ✅ |
| Category trend analysis | B.2 Student | Teacher | Time-series | ✅ |
| Question selection metrics | B.3 Questions | Teacher | `question_transitions` | ✅ |
| Category performance | B.3 Questions | Teacher | Aggregation | ✅ |
| Variant performance | B.4 Intervention | Teacher | `question_variants` | ✅ |
| A/B test results | B.4 Intervention | Teacher | `ab_tests` | ✅ |

### 6.3 System Analytics Features

| Feature | Dashboard | Phase | Data Source | Access |
|---------|-----------|-------|-------------|--------|
| DAU/WAU/MAU | C.1 Health | Teacher | Analytics | Tier 3 |
| API latency metrics | C.1 Health | Teacher | Observability | Tier 3 |
| LLM cost tracking | C.1 Health | Teacher | Cost tracking | Tier 3 |
| Cache hit rates | C.1 Health | Teacher | Redis metrics | Tier 3 |
| Library coverage | C.2 Quality | Teacher | `path_patterns` | Tier 3 |
| Content quality scores | C.2 Quality | Teacher | Quality metrics | Tier 3 |
| Organic preservation % | C.2 Quality | Teacher | Serving logs | Tier 3 |
| Teacher metrics | C.3 Teachers | Teacher | `teacher_quality_metrics` | Tier 3 |
| Platform-wide A/B impact | C.4 A/B Tests | Teacher | Meta-analysis | Tier 3 |

---

## 7. Development Phase Summary

### 7.1 Tiered Dashboard Delivery

| Phase | Dashboards Delivered | Priority Features |
|-------|---------------------|-------------------|
| **MVP** | A.1 Main Dashboard | Session resume, subject grid, streak counter |
| **Extended** | A.2 Learning Stats | Basic statistics, time tracking, chapter counts |
| **Advanced** | A.3 My Journey, A.4 Weekly Report | Path visualization, timeline, weekly insights |
| **Teacher** | B.1-B.4 (Teacher), C.1-C.4 (Admin) | Full diagnostic capability, intervention tools |

### 7.2 Implementation Order Within Phases

**MVP Implementation Order:**
1. Authentication integration
2. Session persistence (AsyncStorage + Supabase)
3. A.1 Main Dashboard UI

**Extended Implementation Order:**
1. Analytics aggregation jobs
2. A.2 Learning Stats UI

**Advanced Implementation Order:**
1. Path recording system
2. Exploration event storage
3. A.3 My Journey visualization
4. Weekly report generation jobs
5. A.4 Weekly Report UI + notifications

**Teacher Implementation Order:**
1. Teacher-student linking
2. Categorical classification pipeline
3. B.1 Class Overview
4. B.2 Individual Student View
5. B.3 Question Analytics
6. Teacher privilege system
7. B.4 Intervention Tools
8. C.1 Platform Health (observability integration)
9. C.2 Content Quality Monitoring
10. C.3 Teacher Management
11. C.4 A/B Test Overview

---

## 8. Dependency Graph

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DASHBOARD DEPENDENCY GRAPH                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  INFRASTRUCTURE LAYER                                                        │
│  ════════════════════                                                        │
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Authentication│  │ Supabase DB  │  │    Redis     │  │ Observability│     │
│  │   (Supabase) │  │  + pgvector  │  │    Cache     │  │(Sentry/Grafana)    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                 │                 │              │
│         ▼                 ▼                 ▼                 ▼              │
│  DATA COLLECTION LAYER                                                       │
│  ═════════════════════                                                       │
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ exploration_ │  │  learning_   │  │    path_     │  │   question_  │     │
│  │   events     │  │   sessions   │  │   patterns   │  │  transitions │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                 │                 │              │
│         └────────────┬────┴────────────┬────┴────────────┬────┘              │
│                      ▼                 ▼                 ▼                   │
│  ANALYTICS AGGREGATION LAYER                                                 │
│  ═══════════════════════════                                                 │
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                       │
│  │   Student    │  │  Categorical │  │   Teacher    │                       │
│  │  Aggregates  │  │Classification│  │   Metrics    │                       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                       │
│         │                 │                 │                                │
│         ▼                 ▼                 ▼                                │
│  DASHBOARD LAYER                                                             │
│  ═══════════════                                                             │
│                                                                              │
│  MVP:           ┌─────────────┐                                             │
│                 │ A.1 Main    │                                             │
│                 │ Dashboard   │                                             │
│                 └──────┬──────┘                                             │
│                        │                                                     │
│  Extended:       ┌──────▼──────┐                                             │
│                 │ A.2 Learning│                                             │
│                 │    Stats    │                                             │
│                 └──────┬──────┘                                             │
│                        │                                                     │
│  Advanced:       ┌──────▼──────┐  ┌─────────────┐                            │
│                 │ A.3 My      │──│ A.4 Weekly  │                            │
│                 │ Journey     │  │ Report      │                            │
│                 └─────────────┘  └─────────────┘                            │
│                                                                              │
│  Teacher:       ┌─────────────────────────────────────────────────────┐     │
│                 │              TEACHER DASHBOARDS                      │     │
│                 │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │     │
│                 │  │B.1 Class│ │B.2 Indiv│ │B.3 Quest│ │B.4 Inter│   │     │
│                 │  │Overview │◄┤Student  │◄┤Analytics│◄┤vention  │   │     │
│                 │  └─────────┘ └─────────┘ └─────────┘ └────┬────┘   │     │
│                 └───────────────────────────────────────────┼───────┘     │
│                                                              │              │
│                 ┌────────────────────────────────────────────▼─────────┐    │
│                 │              ADMIN DASHBOARDS                         │    │
│                 │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐    │    │
│                 │  │C.1 Plat │ │C.2 Cont │ │C.3 Teach│ │C.4 A/B  │    │    │
│                 │  │Health   │ │Quality  │ │Mgmt     │ │Overview │    │    │
│                 │  └─────────┘ └─────────┘ └─────────┘ └─────────┘    │    │
│                 └──────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.1 Critical Path Dependencies

| Dashboard | Hard Dependencies | Soft Dependencies |
|-----------|------------------|-------------------|
| A.1 Main | Auth, Sessions table | None |
| A.2 Stats | A.1, Analytics aggregation | None |
| A.3 Journey | A.2, Path recording | Visualization library |
| A.4 Report | A.3, Notification system | Email/push integration |
| B.1 Class | Teacher-student linking, Categorical classification | None |
| B.2 Student | B.1, Individual analytics | Radar chart library |
| B.3 Questions | Question bank, Selection metrics | None |
| B.4 Intervention | B.3, Privilege system, A/B engine | Organic preservation |
| C.1 Health | Observability stack | External integrations |
| C.2 Quality | Content Library, Quality metrics | None |
| C.3 Teachers | Privilege system, Audit log | None |
| C.4 A/B Tests | A/B testing engine | Statistical libraries |

---

*Document Version 1.0 | Analytics & Dashboard Inventory*
*Last Updated: February 2025*

