# Teacher Access Control Specification

**Document Version**: 1.0  
**Status**: Draft  
**Last Updated**: February 2025  
**Related Documents**: `system-architecture.md`, `analytics-dashboard-inventory.md`

---

## 1. Executive Summary

This document specifies the three-tier access control system for the Teacher Dashboard, ensuring that question intervention privileges are properly gatekept while maintaining platform content quality and organic exploration principles.

### Core Principles

1. **Organic Preservation**: Teacher interventions must not compromise the natural exploration experience
2. **Quality Control**: Only vetted teachers can inject content into the Content Library
3. **Accountability**: All interventions are audited and metrics-tracked
4. **Gradual Access**: Privileges are earned through demonstrated platform engagement and quality

---

## 2. Three-Tier Access Control System

### Overview Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TEACHER DASHBOARD ACCESS TIERS                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  TIER 1: ALL TEACHERS ─────────────────────────────────────────────────────  │
│  Access: Automatic upon teacher account verification                        │
│  Population: All verified teachers                                          │
│                                                                              │
│  TIER 2: APPROVED TEACHERS ────────────────────────────────────────────────  │
│  Access: Requires application + administrator approval                      │
│  Population: ~10-20% of verified teachers (estimated)                       │
│                                                                              │
│  TIER 3: ADMINISTRATORS ───────────────────────────────────────────────────  │
│  Access: Internal platform staff only                                       │
│  Population: Platform operations team                                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Tier 1: All Teachers (View-Only Analytics)

**Access Requirements**:
- Verified teacher account (credential verification completed)
- At least one student linked to their class roster

**Capabilities**:

| Capability | Description |
|------------|-------------|
| ✅ View individual student profiles | Categorical coverage radar, diagnostic concern analysis, exploration patterns |
| ✅ View class-level analytics | Aggregate category concerns, accessibility rankings |
| ✅ View question analytics | Selection rates, avoided questions, entry points |
| ✅ View teaching recommendations | "Let explore" / "Scaffold" / "Direct teach" suggestions |
| ✅ Export analytics reports | PDF/CSV export of class and student data |
| ✅ View exploration patterns | Bridge questions, systematic avoidance patterns |

**Restrictions**:

| Restriction | Rationale |
|-------------|-----------|
| ❌ Cannot create question variants | Prevents unvetted content injection |
| ❌ Cannot inject interventions | Protects organic exploration principle |
| ❌ Cannot run A/B tests | Requires approval for experimentation |
| ❌ Cannot access admin functions | Reserved for platform administrators |

### 2.2 Tier 2: Approved Teachers (Intervention Privileges)

**Access Requirements**:
- All Tier 1 requirements
- Successful privilege application approval
- Completed "Content Intervention Training" module
- No active content violations or warnings

**Approval Criteria** (all must be met):

| Criterion | Threshold | Rationale |
|-----------|-----------|-----------|
| Account age | ≥ 30 days | Platform familiarity |
| Active students | ≥ 5 students | Demonstrated teaching engagement |
| Verified credentials | Required | Professional verification |
| Content violations | 0 active | Quality track record |
| Training completion | Required | Understanding of intervention guidelines |

**Capabilities** (in addition to Tier 1):

| Capability | Description | Limits |
|------------|-------------|--------|
| ✅ Create question variants | Enhanced, contextual, linguistic, or custom rewrites | Max 50 pending variants |
| ✅ Deploy path interventions | Inject variants at specific path positions | Max 20 active interventions |
| ✅ Run A/B tests | Compare variant performance vs. organic | Max 10 concurrent tests |
| ✅ View intervention metrics | Selection rate lift, quiz score impact | Own interventions only |
| ✅ Promote winning variants | Move successful variants to default | Requires metrics threshold |

**Restrictions & Guardrails**:

| Restriction | Threshold | Enforcement |
|-------------|-----------|-------------|
| Max active interventions | 20 (default, adjustable by admin) | Hard limit in system |
| High-traffic path interventions | Requires admin approval | Paths with >1000 sessions/month |
| Organic floor | 30% minimum | System-enforced, cannot be overridden |
| Max coverage per path | 70% of positions | Prevents over-intervention |
| Entry point interventions | Warning required | First position flagged as sensitive |

### 2.3 Tier 3: Administrators (Full Platform Control)

**Access Requirements**:
- Platform staff with admin role assignment
- Multi-factor authentication enabled
- Access audit logging enabled

**Capabilities** (in addition to Tier 1 & 2):

| Capability | Description |
|------------|-------------|
| ✅ Approve/reject privilege applications | Review teacher applications queue |
| ✅ Monitor all teacher variants | Quality review across platform |
| ✅ Revoke intervention privileges | Suspend or permanently revoke Tier 2 access |
| ✅ Adjust intervention limits | Increase/decrease per-teacher limits |
| ✅ Override A/B test results | Force promotion or retirement |
| ✅ System-wide interventions | Deploy interventions platform-wide |
| ✅ Content moderation | Remove inappropriate content |
| ✅ Configure thresholds | Organic floor, promotion criteria, etc. |
| ✅ View platform health | DAU/WAU/MAU, costs, error rates |
| ✅ Manage teacher roster | View/edit all teacher profiles |

---

## 3. Database Schema

### 3.1 Core Enums

```sql
-- User role hierarchy
CREATE TYPE user_role AS ENUM (
    'student',           -- Default for learners
    'teacher',           -- Tier 1: Verified teacher
    'approved_teacher',  -- Tier 2: Intervention privileges
    'admin'              -- Tier 3: Full platform control
);

-- Privilege application status
CREATE TYPE privilege_status AS ENUM (
    'not_applied',       -- Never applied for privileges
    'pending',           -- Application under review
    'approved',          -- Tier 2 privileges granted
    'suspended',         -- Temporarily revoked (can be reinstated)
    'revoked'            -- Permanently revoked
);

-- Intervention audit action types
CREATE TYPE audit_action AS ENUM (
    'variant_created',
    'variant_updated',
    'variant_deleted',
    'intervention_deployed',
    'intervention_paused',
    'intervention_retired',
    'ab_test_started',
    'ab_test_concluded',
    'ab_test_cancelled',
    'privilege_granted',
    'privilege_suspended',
    'privilege_revoked',
    'warning_issued',
    'limit_adjusted'
);
```

### 3.2 User Profiles Table

```sql
-- Extended user profiles with role and privilege management
CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id),

    -- Basic info
    display_name VARCHAR(100),
    email VARCHAR(255) NOT NULL,
    avatar_url TEXT,

    -- Role management
    role user_role NOT NULL DEFAULT 'student',
    role_updated_at TIMESTAMPTZ,
    role_updated_by UUID REFERENCES user_profiles(user_id),

    -- Teacher-specific fields (NULL for students)
    is_verified_teacher BOOLEAN DEFAULT FALSE,
    teacher_verification_date TIMESTAMPTZ,
    school_affiliation VARCHAR(200),
    school_verified BOOLEAN DEFAULT FALSE,
    subjects_taught JSONB DEFAULT '[]',
    -- Example: ["physics", "chemistry", "biology"]

    years_of_experience INTEGER,
    credential_document_url TEXT,

    -- Privilege management (Tier 2)
    intervention_privilege_status privilege_status DEFAULT 'not_applied',
    privilege_granted_at TIMESTAMPTZ,
    privilege_granted_by UUID REFERENCES user_profiles(user_id),
    privilege_revoked_at TIMESTAMPTZ,
    privilege_revoked_by UUID REFERENCES user_profiles(user_id),
    revocation_reason TEXT,

    -- Configurable limits (can be adjusted by admin)
    max_active_interventions INTEGER DEFAULT 20,
    max_pending_variants INTEGER DEFAULT 50,
    max_concurrent_ab_tests INTEGER DEFAULT 10,
    requires_approval_for_high_traffic BOOLEAN DEFAULT TRUE,
    high_traffic_threshold INTEGER DEFAULT 1000, -- sessions/month

    -- Account status
    account_created_at TIMESTAMPTZ DEFAULT NOW(),
    last_active_at TIMESTAMPTZ,
    is_suspended BOOLEAN DEFAULT FALSE,
    suspension_reason TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_user_profiles_role ON user_profiles(role);
CREATE INDEX idx_user_profiles_privilege_status ON user_profiles(intervention_privilege_status);
CREATE INDEX idx_user_profiles_verified_teacher ON user_profiles(is_verified_teacher)
    WHERE is_verified_teacher = TRUE;
CREATE INDEX idx_user_profiles_approved_teacher ON user_profiles(role)
    WHERE role = 'approved_teacher';
```

### 3.3 Privilege Applications Table

```sql
-- Teacher privilege application tracking
CREATE TABLE privilege_applications (
    application_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    teacher_id UUID NOT NULL REFERENCES user_profiles(user_id),

    -- Application status
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    -- 'pending', 'approved', 'rejected', 'more_info_needed', 'withdrawn'

    -- Application content
    teaching_experience_years INTEGER NOT NULL,
    credential_document_url TEXT,
    motivation_statement TEXT NOT NULL,
    sample_intervention_ideas JSONB,
    -- Example: [
    --   {
    --     "question_id": "q123",
    --     "proposed_change": "Simplify language for struggling students",
    --     "rationale": "Many students skip this question due to complex wording"
    --   }
    -- ]

    subjects_applying_for JSONB NOT NULL DEFAULT '[]',
    -- Example: ["physics", "chemistry"]

    -- Eligibility snapshot at application time
    eligibility_snapshot JSONB NOT NULL,
    -- {
    --   "account_age_days": 45,
    --   "active_student_count": 12,
    --   "is_verified": true,
    --   "violation_count": 0,
    --   "training_completed": true
    -- }

    -- Review tracking
    reviewed_by UUID REFERENCES user_profiles(user_id),
    reviewed_at TIMESTAMPTZ,
    review_notes TEXT,              -- Internal admin notes
    rejection_reason TEXT,          -- Shown to teacher if rejected
    additional_info_request TEXT,   -- If more_info_needed

    -- Resubmission tracking
    previous_application_id UUID REFERENCES privilege_applications(application_id),
    reapplication_allowed_after TIMESTAMPTZ,

    -- Timestamps
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_privilege_applications_status ON privilege_applications(status);
CREATE INDEX idx_privilege_applications_teacher ON privilege_applications(teacher_id);
CREATE INDEX idx_privilege_applications_pending ON privilege_applications(submitted_at)
    WHERE status = 'pending';

-- Constraint: One pending application per teacher
CREATE UNIQUE INDEX idx_one_pending_per_teacher ON privilege_applications(teacher_id)
    WHERE status = 'pending';
```

### 3.4 Intervention Audit Log Table

```sql
-- Complete audit trail for all intervention-related actions
CREATE TABLE intervention_audit_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Action details
    action_type audit_action NOT NULL,
    action_description TEXT,

    -- Who performed the action
    actor_id UUID NOT NULL REFERENCES user_profiles(user_id),
    actor_role user_role NOT NULL,
    actor_ip_address INET,
    actor_user_agent TEXT,

    -- What was affected
    target_type VARCHAR(50),
    -- 'question_variant', 'path_intervention', 'ab_test', 'user_profile', 'privilege_application'
    target_id UUID,
    target_details JSONB,
    -- Snapshot of target state at action time

    -- Change tracking
    previous_state JSONB,
    new_state JSONB,

    -- Admin override tracking
    is_admin_override BOOLEAN DEFAULT FALSE,
    admin_justification TEXT,
    requires_review BOOLEAN DEFAULT FALSE,
    reviewed_by UUID REFERENCES user_profiles(user_id),
    reviewed_at TIMESTAMPTZ,

    -- Context
    related_chapter_id VARCHAR(100),
    related_pattern_id UUID,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_audit_log_action ON intervention_audit_log(action_type);
CREATE INDEX idx_audit_log_actor ON intervention_audit_log(actor_id);
CREATE INDEX idx_audit_log_target ON intervention_audit_log(target_type, target_id);
CREATE INDEX idx_audit_log_created ON intervention_audit_log(created_at DESC);
CREATE INDEX idx_audit_log_review ON intervention_audit_log(requires_review)
    WHERE requires_review = TRUE;

-- Partition by month for performance (optional for large scale)
-- CREATE TABLE intervention_audit_log_y2025m01 PARTITION OF intervention_audit_log
--     FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
```

### 3.5 Teacher Quality Metrics Table

```sql
-- Aggregated quality metrics for teachers with intervention privileges
CREATE TABLE teacher_quality_metrics (
    teacher_id UUID PRIMARY KEY REFERENCES user_profiles(user_id),

    -- Cumulative intervention metrics
    total_variants_created INTEGER DEFAULT 0,
    total_variants_promoted INTEGER DEFAULT 0,
    total_variants_retired INTEGER DEFAULT 0,
    total_interventions_deployed INTEGER DEFAULT 0,

    -- Calculated rates
    variant_promotion_rate DECIMAL(5,4) DEFAULT 0,
    -- total_variants_promoted / total_variants_tested

    -- Performance lift metrics (average across all interventions)
    avg_selection_rate_lift DECIMAL(6,4),
    avg_quiz_score_lift DECIMAL(6,4),

    -- Recent activity (rolling 30-day window)
    variants_created_last_30_days INTEGER DEFAULT 0,
    interventions_deployed_last_30_days INTEGER DEFAULT 0,
    active_ab_tests INTEGER DEFAULT 0,

    -- Current counts
    active_interventions INTEGER DEFAULT 0,
    pending_variants INTEGER DEFAULT 0,

    -- Quality signals
    has_quality_warnings BOOLEAN DEFAULT FALSE,
    active_warning_count INTEGER DEFAULT 0,
    total_warning_count INTEGER DEFAULT 0,
    last_warning_at TIMESTAMPTZ,
    last_warning_reason TEXT,

    -- Content removal tracking
    content_removed_count INTEGER DEFAULT 0,
    last_content_removal_at TIMESTAMPTZ,

    -- Trust score (computed metric)
    trust_score DECIMAL(5,4) DEFAULT 1.0,
    -- Factors: promotion_rate, warning_count, account_age, activity_level

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    metrics_computed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for quality monitoring
CREATE INDEX idx_teacher_metrics_warnings ON teacher_quality_metrics(has_quality_warnings)
    WHERE has_quality_warnings = TRUE;
CREATE INDEX idx_teacher_metrics_trust ON teacher_quality_metrics(trust_score);
```

---

## 4. Approval Workflow

### 4.1 Complete Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TEACHER PRIVILEGE APPLICATION WORKFLOW                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  STEP 1: ELIGIBILITY CHECK (Automatic)                                      │
│  ─────────────────────────────────────                                      │
│  System validates:                                                          │
│  □ Account age ≥ 30 days                                                    │
│  □ Is verified teacher = TRUE                                               │
│  □ Active students ≥ 5                                                      │
│  □ Active violations = 0                                                    │
│  □ No pending application exists                                            │
│  □ Not in reapplication cooldown period                                     │
│           │                                                                  │
│           ├─── FAIL ──→ Show specific unmet criteria, block application     │
│           │                                                                  │
│           ▼ PASS                                                            │
│  STEP 2: APPLICATION FORM                                                   │
│  ────────────────────────                                                   │
│  Teacher provides:                                                          │
│  • Years of teaching experience                                             │
│  • Credential document (optional if already verified)                       │
│  • Motivation statement (why they want privileges)                          │
│  • Sample intervention ideas (optional, but recommended)                    │
│  • Subjects they want to create interventions for                           │
│           │                                                                  │
│           ▼                                                                  │
│  STEP 3: ADMIN REVIEW QUEUE                                                 │
│  ──────────────────────────                                                 │
│  Application enters queue with:                                             │
│  • Application details                                                      │
│  • Eligibility snapshot                                                     │
│  • Teacher's current analytics usage                                        │
│  • Student engagement metrics                                               │
│  • Any prior applications (with outcomes)                                   │
│           │                                                                  │
│           ├──────────────────┬───────────────────┐                          │
│           ▼                  ▼                   ▼                          │
│  STEP 4A: APPROVED       4B: REJECTED        4C: MORE INFO NEEDED           │
│  ─────────────────       ────────────        ────────────────────           │
│                                                                              │
│  APPROVED:                                                                  │
│  • Role → 'approved_teacher'                                                │
│  • Default limits applied                                                   │
│  • Welcome email + training reminder                                        │
│  • Audit log entry created                                                  │
│                                                                              │
│  REJECTED:                                                                  │
│  • Rejection reason provided                                                │
│  • Reapplication allowed after 90 days                                      │
│  • Can appeal within 14 days                                                │
│                                                                              │
│  MORE INFO NEEDED:                                                          │
│  • Specific questions sent to teacher                                       │
│  • 14 days to respond                                                       │
│  • Returns to queue when answered                                           │
│  • Auto-withdrawn if no response                                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Eligibility Check Implementation

```python
# app/services/privilege_eligibility.py

from datetime import datetime, timedelta
from typing import Tuple, List

class PrivilegeEligibilityChecker:
    """
    Validates teacher eligibility for intervention privileges.
    """

    # Configurable thresholds
    MIN_ACCOUNT_AGE_DAYS = 30
    MIN_ACTIVE_STUDENTS = 5
    REAPPLICATION_COOLDOWN_DAYS = 90

    async def check_eligibility(
        self,
        teacher_id: str
    ) -> Tuple[bool, List[str]]:
        """
        Check if teacher is eligible to apply for privileges.
        Returns (is_eligible, list_of_unmet_criteria).
        """
        unmet_criteria = []

        teacher = await self.get_teacher_profile(teacher_id)

        # 1. Account age check
        account_age = (datetime.now() - teacher.account_created_at).days
        if account_age < self.MIN_ACCOUNT_AGE_DAYS:
            unmet_criteria.append(
                f"Account must be at least {self.MIN_ACCOUNT_AGE_DAYS} days old. "
                f"Current: {account_age} days. "
                f"Eligible in: {self.MIN_ACCOUNT_AGE_DAYS - account_age} days."
            )

        # 2. Verified teacher check
        if not teacher.is_verified_teacher:
            unmet_criteria.append(
                "Teacher verification required. Please complete the teacher "
                "verification process in your profile settings."
            )

        # 3. Active students check
        active_students = await self.count_active_students(teacher_id)
        if active_students < self.MIN_ACTIVE_STUDENTS:
            unmet_criteria.append(
                f"Must have at least {self.MIN_ACTIVE_STUDENTS} active students. "
                f"Current: {active_students} students."
            )

        # 4. No active violations
        active_violations = await self.count_active_violations(teacher_id)
        if active_violations > 0:
            unmet_criteria.append(
                f"Cannot apply with active content violations. "
                f"Please resolve {active_violations} pending violation(s)."
            )

        # 5. No pending application
        has_pending = await self.has_pending_application(teacher_id)
        if has_pending:
            unmet_criteria.append(
                "You already have a pending application. "
                "Please wait for the current application to be reviewed."
            )

        # 6. Reapplication cooldown
        last_rejection = await self.get_last_rejection(teacher_id)
        if last_rejection:
            cooldown_end = last_rejection.reviewed_at + timedelta(
                days=self.REAPPLICATION_COOLDOWN_DAYS
            )
            if datetime.now() < cooldown_end:
                days_remaining = (cooldown_end - datetime.now()).days
                unmet_criteria.append(
                    f"Reapplication cooldown active. "
                    f"You can reapply in {days_remaining} days."
                )

        is_eligible = len(unmet_criteria) == 0
        return is_eligible, unmet_criteria
```

### 4.3 Admin Review Process

**Review Dashboard Information**:

| Section | Data Shown | Purpose |
|---------|------------|---------|
| Application Details | Motivation, experience, sample ideas | Understand teacher's intent |
| Eligibility Snapshot | Account age, students, violations | Verify eligibility at application time |
| Platform Activity | Dashboard logins, analytics viewed | Gauge platform engagement |
| Student Outcomes | Class quiz performance, completion rates | Quality of teaching |
| Prior Applications | Previous applications with outcomes | Application history |

**Decision Criteria**:

| Factor | Weight | Positive Signals | Negative Signals |
|--------|--------|------------------|------------------|
| Teaching Experience | 20% | 5+ years experience | <1 year experience |
| Motivation Quality | 25% | Specific, student-focused | Vague, self-focused |
| Sample Ideas | 25% | Thoughtful, pedagogically sound | Missing or low-quality |
| Platform Engagement | 15% | Regular analytics usage | Minimal platform activity |
| Student Outcomes | 15% | Above-average performance | Below-average performance |

### 4.4 Reapplication & Appeal Policies

**Reapplication**:
- Allowed 90 days after rejection
- Must address previous rejection reason
- Previous application visible to reviewer
- Maximum 3 applications per year

**Appeals**:
- Must be submitted within 14 days of rejection
- Reviewed by different admin than original reviewer
- Can include additional documentation
- Decision is final (no further appeal)

**Withdrawal**:
- Teacher can withdraw pending application anytime
- No cooldown for withdrawn applications
- Can resubmit immediately after withdrawal

---

## 5. Quality Monitoring & Guardrails

### 5.1 Intervention Limits

| Limit | Default Value | Adjustable? | Rationale |
|-------|---------------|-------------|-----------|
| Max active interventions | 20 | ✅ By admin | Prevent system flooding |
| Max pending variants | 50 | ✅ By admin | Encourage deployment over stockpiling |
| Max concurrent A/B tests | 10 | ✅ By admin | Statistical validity |
| Max interventions per path | 5 | ❌ System-wide | Organic preservation |
| Max coverage per path | 70% | ❌ System-wide | Organic preservation |
| Organic floor | 30% | ❌ System-wide | Guaranteed organic experience |

### 5.2 High-Traffic Path Approval

**Definition**: Paths with >1000 sessions in the past 30 days

**Approval Process**:
1. Teacher attempts to deploy intervention to high-traffic path
2. System flags intervention for admin approval
3. Admin reviews intervention in dedicated queue
4. Admin approves, rejects, or requests changes
5. Teacher notified of decision

**Admin Review Criteria**:
- Does the intervention align with organic principles?
- Is the teacher's rationale sound?
- Is there sufficient A/B test data to justify deployment?
- What is the potential impact (students affected)?

### 5.3 Quality Metrics Tracked

```python
# Quality metrics computation (daily job)

class TeacherQualityComputer:
    """
    Computes and updates teacher quality metrics.
    """

    async def compute_metrics(self, teacher_id: str) -> TeacherQualityMetrics:
        # Get all teacher's A/B tests
        tests = await self.get_concluded_tests(teacher_id)

        # Calculate promotion rate
        total_tested = len(tests)
        promoted = len([t for t in tests if t.winner_is_treatment])
        promotion_rate = promoted / total_tested if total_tested > 0 else 0

        # Calculate average lifts
        lifts = [t.metrics for t in tests if t.winner_is_treatment]
        avg_selection_lift = mean([l['selection_lift'] for l in lifts]) if lifts else None
        avg_quiz_lift = mean([l['quiz_lift'] for l in lifts]) if lifts else None

        # Count recent activity
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_variants = await self.count_variants_since(teacher_id, thirty_days_ago)
        recent_interventions = await self.count_interventions_since(teacher_id, thirty_days_ago)

        # Calculate trust score
        trust_score = self.calculate_trust_score(
            promotion_rate=promotion_rate,
            warning_count=await self.get_warning_count(teacher_id),
            account_age=await self.get_account_age(teacher_id),
            activity_level=recent_variants + recent_interventions
        )

        return TeacherQualityMetrics(
            variant_promotion_rate=promotion_rate,
            avg_selection_rate_lift=avg_selection_lift,
            avg_quiz_score_lift=avg_quiz_lift,
            variants_created_last_30_days=recent_variants,
            trust_score=trust_score
        )
```

### 5.4 Warning System

**Warning Triggers**:

| Trigger | Severity | Action |
|---------|----------|--------|
| Variant with <-15% selection lift | Low | Warning logged, teacher notified |
| 3 consecutive variants retired | Medium | Warning issued, limits reduced by 50% |
| Content flagged by multiple users | Medium | Warning issued, content paused |
| Intervention bypasses organic floor | High | Automatic suspension, admin review |
| Policy violation detected | Critical | Immediate suspension, investigation |

**Warning Escalation**:

```
Warning 1 → Notification + coaching resources
Warning 2 → Limits reduced by 25%
Warning 3 → Limits reduced by 50% + mandatory training
Warning 4 → Privileges suspended (7 days)
Warning 5 → Privileges revoked (must reapply after 180 days)
```

### 5.5 Revocation Procedures

**Temporary Suspension**:
- Duration: 7-30 days based on severity
- Active interventions paused (organic restored)
- Teacher cannot create new variants
- Can appeal within 7 days
- Automatic reinstatement after suspension period

**Permanent Revocation**:
- All active interventions retired
- Teacher demoted to Tier 1 (view-only)
- Cannot reapply for 180 days (or permanently for severe violations)
- Audit log entry with full details

---

## 6. Integration Points

### 6.1 A/B Testing Engine Integration

```python
# Access control enforcement in A/B testing

class ABTestAccessControl:
    """
    Enforces access control for A/B testing operations.
    """

    async def can_create_test(self, teacher_id: str) -> Tuple[bool, str]:
        """Check if teacher can create a new A/B test."""
        profile = await self.get_profile(teacher_id)

        # Must be approved teacher
        if profile.role != 'approved_teacher':
            return False, "Intervention privileges required"

        # Check suspension status
        if profile.intervention_privilege_status == 'suspended':
            return False, "Privileges currently suspended"

        # Check concurrent test limit
        metrics = await self.get_quality_metrics(teacher_id)
        if metrics.active_ab_tests >= profile.max_concurrent_ab_tests:
            return False, f"Maximum concurrent tests ({profile.max_concurrent_ab_tests}) reached"

        return True, ""

    async def can_deploy_to_path(
        self,
        teacher_id: str,
        pattern_id: str
    ) -> Tuple[bool, str]:
        """Check if teacher can deploy intervention to specific path."""
        profile = await self.get_profile(teacher_id)
        pattern = await self.get_pattern(pattern_id)

        # Check high-traffic threshold
        if pattern.monthly_sessions > profile.high_traffic_threshold:
            if profile.requires_approval_for_high_traffic:
                return False, "This high-traffic path requires admin approval"

        # Check intervention limit
        metrics = await self.get_quality_metrics(teacher_id)
        if metrics.active_interventions >= profile.max_active_interventions:
            return False, f"Maximum active interventions ({profile.max_active_interventions}) reached"

        return True, ""
```

### 6.2 Question Variant System Integration

```python
# Variant creation with access control

class VariantCreationService:
    """
    Handles question variant creation with access control.
    """

    async def create_variant(
        self,
        teacher_id: str,
        question_id: str,
        variant_text: str,
        variant_type: str,
        rationale: str
    ) -> QuestionVariant:
        # Check permissions
        can_create, reason = await self.access_control.can_create_variant(teacher_id)
        if not can_create:
            raise PermissionDenied(reason)

        # Create variant
        variant = QuestionVariant(
            question_id=question_id,
            variant_type=variant_type,
            question_text=variant_text,
            created_by_type='teacher',
            created_by_id=teacher_id
        )

        await self.db.insert(variant)

        # Audit log
        await self.audit_log.record(
            action_type='variant_created',
            actor_id=teacher_id,
            target_type='question_variant',
            target_id=variant.variant_id,
            new_state=variant.to_dict()
        )

        # Update teacher metrics
        await self.metrics.increment_variants_created(teacher_id)

        return variant
```

### 6.3 Organic Preservation Enforcement

```python
# Organic floor enforcement in serving logic

class OrganicPreservationGuard:
    """
    Enforces organic preservation rules at serving time.
    """

    ORGANIC_FLOOR = 0.30  # 30% minimum organic
    MAX_COVERAGE_PER_PATH = 0.70  # 70% maximum intervention coverage
    MAX_INTERVENTIONS_PER_PATH = 5

    async def should_serve_organic(
        self,
        student_id: str,
        pattern_id: str
    ) -> bool:
        """
        Determine if student should receive organic (non-intervened) content.
        Uses consistent hashing for reproducibility.
        """
        # Hash-based deterministic decision
        hash_input = f"{student_id}:{pattern_id}:organic_floor"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        organic_roll = (hash_value % 10000) / 10000

        # If roll < organic floor, serve organic
        return organic_roll < self.ORGANIC_FLOOR

    async def validate_intervention_deployment(
        self,
        pattern_id: str,
        new_intervention: PathIntervention
    ) -> Tuple[bool, List[str]]:
        """
        Validate that deploying this intervention doesn't violate organic rules.
        """
        errors = []
        warnings = []

        # Get existing interventions
        existing = await self.get_active_interventions(pattern_id)
        path_length = await self.get_path_length(pattern_id)

        # Check intervention count
        if len(existing) >= self.MAX_INTERVENTIONS_PER_PATH:
            errors.append(
                f"Path already has {len(existing)} interventions. "
                f"Maximum is {self.MAX_INTERVENTIONS_PER_PATH}."
            )

        # Check coverage
        covered_positions = {i.path_position for i in existing}
        covered_positions.add(new_intervention.path_position)
        coverage = len(covered_positions) / path_length

        if coverage > self.MAX_COVERAGE_PER_PATH:
            errors.append(
                f"This would cover {coverage:.0%} of the path. "
                f"Maximum is {self.MAX_COVERAGE_PER_PATH:.0%}."
            )

        # Warning for entry point
        if new_intervention.path_position == 1:
            warnings.append(
                "Intervening at the entry point may impact organic discovery. "
                "Consider targeting position 2+ for better organic preservation."
            )

        return len(errors) == 0, errors + warnings
```

---

## 7. Configuration & Thresholds

### 7.1 Configurable Parameters

```python
# config/access_control.py

ACCESS_CONTROL_CONFIG = {
    # Eligibility thresholds
    "min_account_age_days": 30,
    "min_active_students": 5,
    "reapplication_cooldown_days": 90,
    "appeal_window_days": 14,

    # Intervention limits (defaults, adjustable per-teacher)
    "default_max_active_interventions": 20,
    "default_max_pending_variants": 50,
    "default_max_concurrent_ab_tests": 10,

    # System-wide limits (not adjustable per-teacher)
    "max_interventions_per_path": 5,
    "max_coverage_per_path": 0.70,
    "organic_floor": 0.30,

    # High-traffic thresholds
    "high_traffic_sessions_threshold": 1000,  # per month

    # Warning thresholds
    "selection_lift_warning_threshold": -0.15,
    "consecutive_retirements_warning": 3,

    # Suspension durations
    "minor_suspension_days": 7,
    "major_suspension_days": 30,
    "revocation_reapplication_days": 180,
}
```

### 7.2 Role-Based Feature Flags

```python
# config/feature_flags.py

ROLE_FEATURE_FLAGS = {
    "student": {
        "can_view_own_analytics": True,
        "can_see_categories": False,  # Strict invisibility
    },
    "teacher": {
        "can_view_student_analytics": True,
        "can_view_class_analytics": True,
        "can_view_question_analytics": True,
        "can_export_reports": True,
        "can_see_categories": True,
        "can_create_variants": False,
        "can_deploy_interventions": False,
        "can_run_ab_tests": False,
    },
    "approved_teacher": {
        # All teacher flags plus:
        "can_create_variants": True,
        "can_deploy_interventions": True,
        "can_run_ab_tests": True,
        "can_promote_variants": True,
    },
    "admin": {
        # All approved_teacher flags plus:
        "can_approve_applications": True,
        "can_revoke_privileges": True,
        "can_adjust_limits": True,
        "can_override_ab_tests": True,
        "can_view_platform_health": True,
        "can_moderate_content": True,
        "can_configure_thresholds": True,
    },
}
```

---

## 8. API Endpoints

### 8.1 Privilege Application Endpoints

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/api/v1/privileges/eligibility` | Tier 1 | Check eligibility status |
| POST | `/api/v1/privileges/apply` | Tier 1 | Submit privilege application |
| GET | `/api/v1/privileges/application/{id}` | Tier 1 | View own application status |
| DELETE | `/api/v1/privileges/application/{id}` | Tier 1 | Withdraw application |
| GET | `/api/v1/admin/applications` | Tier 3 | List pending applications |
| POST | `/api/v1/admin/applications/{id}/approve` | Tier 3 | Approve application |
| POST | `/api/v1/admin/applications/{id}/reject` | Tier 3 | Reject application |
| POST | `/api/v1/admin/applications/{id}/request-info` | Tier 3 | Request more information |

### 8.2 Quality Monitoring Endpoints

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/api/v1/teachers/{id}/metrics` | Tier 2 (own), Tier 3 | View quality metrics |
| GET | `/api/v1/admin/teachers` | Tier 3 | List all teachers with metrics |
| POST | `/api/v1/admin/teachers/{id}/warn` | Tier 3 | Issue warning |
| POST | `/api/v1/admin/teachers/{id}/suspend` | Tier 3 | Suspend privileges |
| POST | `/api/v1/admin/teachers/{id}/revoke` | Tier 3 | Revoke privileges |
| PUT | `/api/v1/admin/teachers/{id}/limits` | Tier 3 | Adjust teacher limits |

---

*Document Version 1.0 | Teacher Access Control Specification*
*Last Updated: February 2025*

