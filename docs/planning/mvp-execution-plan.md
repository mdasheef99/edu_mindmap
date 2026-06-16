# MVP Execution Plan / Delivery Blueprint
## 1. Purpose and Scope of This Document
This document translates the current aligned MVP definition into an execution-oriented plan. It does not replace the PRD or feature specs; it organizes the first shippable slice, workstreams, dependencies, acceptance criteria, shared contracts, and ADR candidates.
### Source of truth
If this document conflicts with the current scope anchors, resolve the conflict explicitly rather than overriding them here.
- `docs/prd/master-prd.md`
- `docs/mvp-features-specification.md`
- `docs/teacher-support-mvp-specification.md`
- `docs/mobile-features-system.md`
- `docs/architecture-feature-mapping.md`
- `docs/README.md`
## 2. Execution Guardrails
- Product framing: path-based conceptual exploration; teacher-support interpretation as a separate protected layer; category-neutral learner experience.
- Fixed learner rules: no Story Node; no learner node-body editing; branching only through phrase selection inside AI content or the left/right edge `+` on an AI node.
- Edge/deletion rules: AI-generated path edges and manual reference links are distinct; deleting an AI-generated path node deletes descendant AI-path nodes after confirmation.
- MVP scope: podcast is in MVP; basic offline access is limited to reopening previously stored session/board state, already generated content stored locally, and resume continuity via persisted local session data.
- MVP exclusions: offline AI generation, offline editing beyond persisted state, offline sync/queued sync, offline video behavior, downloaded media or podcast offline playback, and broader "full offline mode" claims.
- Teacher-only surfaces must remain protected and role-gated.
## 3. First Shippable MVP Slice
The first shippable slice is an end-to-end learner exploration flow plus the minimum protected teacher-support surface and the minimum continuity/podcast workflows needed to prove the product model.
### Included learner capabilities
- Curriculum-guided entry into exam, subject, chapter, and concept context
- Dashboard re-entry through continue learning / recent sessions
- AI-node-based exploration on a bounded mind map
- Branching through phrase selection and AI-node edge `+` only
- Manual reference links as a distinct non-path edge type
- Previous year questions as a chapter-linked support layer
- Session persistence and narrow basic offline reopening of previously stored content
- Session-based podcast generation and in-app playback while online
### Included teacher-support capabilities
- Protected teacher-only access
- Per-student, chapter-level review surface
- Action-oriented support signals derived from learner path data
- Probabilistic interpretation only; no diagnostic certainty claims
### Explicit release exclusions
- Broader offline mode behavior; offline AI generation; offline editing beyond persisted state
- Offline sync or queued sync flows; downloaded podcast offline playback
- Broader class-level teacher analytics beyond the bounded MVP teacher-support surface
### Release boundary statement
The MVP is shippable when a learner can enter a chapter, explore through the fixed branching rules, return to a persisted session, reopen previously stored content offline in the narrow approved sense, generate a podcast from a session, and when an authorized teacher can review the bounded teacher-support view for a student and chapter.
## 4. MVP Success Conditions and Readiness Gates
- Core learner journey works end to end without violating interaction rules.
- Session/path data required by teacher-support and podcast generation is captured reliably.
- Basic offline reopening works only for previously stored content and does not imply broader offline behavior.
- Teacher access is protected by role/authorization boundaries.
- Podcast flow is functional from session input to playable audio.
### Non-blocking for MVP
- Richer teacher dashboards
- Broader offline continuity features
- Offline playback/download flows
- Additional reflective or social layers
## 5. Release-Critical User Journeys
- Learner enters through curriculum/chapter selection and opens the first AI node.
- Learner branches from phrase selection inside AI content.
- Learner branches from the left/right edge `+` on an AI node.
- Learner creates a manual reference link distinct from AI-path branching.
- Learner deletes an AI-generated path node and confirms descendant path deletion.
- Learner exits and later resumes via continue learning / recent session.
- Learner reopens previously stored session content while offline within the narrow MVP boundary.
- Learner generates and listens to a session-based podcast online.
- Authorized teacher opens the protected per-student, per-chapter support view.

## 6. Workstreams / Epics
- **Auth and role gating**: authentication, protected teacher access, and minimum authorization rules separating learner and teacher-only surfaces.
- **Curriculum entry and dashboard re-entry**: exam/subject/chapter entry, chapter search, continue learning, and recent-session access.
- **Learner session and mind map interactions**: bounded board/session creation, node rendering, selection, manual reference links, deletion behavior, and rule enforcement.
- **AI exploration and branching**: initial AI node creation, phrase-selection branching, AI-node edge `+` branching, and required path/thread context.
- **Session persistence and basic offline access**: local persistence, reopen/resume continuity, and narrow offline reopening of previously stored state/content.
- **Teacher-support minimum surface**: bounded teacher-only review surface and minimum action-oriented interpretation outputs.
- **Podcast MVP**: session-to-script-to-audio generation and in-app playback for online/generated content.

## 7. Dependency Order and Delivery Sequence
Recommended order:
1. Auth/roles plus shared session/path contract foundation
2. Curriculum entry and dashboard re-entry
3. Learner session/board infrastructure
4. AI node creation and fixed branching flows
5. Delete behavior, path-edge vs manual-link rules, and event capture
6. Session persistence and narrow basic offline reopening
7. Teacher-support minimum surface
8. Podcast generation MVP

### Parallelizable work after contracts stabilize
- Dashboard re-entry and persistence can overlap once session identity rules are stable.
- Teacher-support surface and podcast pipeline can proceed in parallel once learner-path/session data inputs are defined.

### Critical path note
Main blockers: session/path contract, deletion semantics, teacher authorization boundary, and local persistence boundary.

## 8. Shared Contracts and Data Dependencies
These contracts must be explicit before downstream implementation is treated as stable.
- Session contract: session identity, chapter context, timestamps, resume state
- Node contract: node type, content source, parent/child relationships, layout/system metadata
- Edge contract: AI-generated path edge vs manual reference link
- Interaction event contract: phrase selections, edge-`+` launches, node visits, revisits, offer sets, selected follow-up questions
- Deletion contract: confirmed cascade deletion for descendant AI-path nodes plus edge cleanup
- Local persistence contract: what is stored locally and what can be reopened offline
- Teacher-support input contract: per-student, per-chapter path and interpretation inputs
- Podcast input contract: which session/path artifacts are required for script and audio generation

### Open Question
The exact first persisted data shape should be specified in a dedicated shared data/session contract document rather than inferred piecemeal during implementation.

## 9. Acceptance Criteria by Workstream
- Auth and role gating: learner and teacher surfaces are separated; unauthorized teacher access is blocked.
- Curriculum entry and dashboard re-entry: learner can start and return to the correct chapter/session context.
- Learner session and mind map interactions: no Story Node appears; learner node-body editing is absent; manual reference links remain distinct from AI-path edges.
- AI exploration and branching: both approved branching flows work; each branch preserves required context; disallowed branching paths are not exposed.
- Deletion behavior: deleting an AI-path node removes descendant AI-path nodes after confirmation.
- Persistence/basic offline: previously stored session state and already generated content can be reopened later, including in the narrow offline case; no broader offline behavior is implied or exposed.
- Teacher-support minimum: authorized teacher can view the bounded per-student, per-chapter support surface only.
- Podcast MVP: learner can generate a podcast from session data and play it in-app online.

## 10. Validation Planning Inputs
- Verify the core learner journeys end to end.
- Verify teacher-only role gating and access denial when authorization is absent.
- Verify persistence and narrow offline reopening for previously stored content only.
- Verify podcast generation from valid session input.
- Verify the absence of Story Node creation, learner node-body editing, learner-facing category labels, offline AI generation, queued sync flows, and offline podcast playback.

## 11. ADR Candidates
These decisions should become ADRs because they are cross-cutting and hard to reverse.
- ADR 1: Learner session and mind map data model
- ADR 2: Basic offline access and local persistence boundary
- ADR 3: Teacher-support authorization boundary
- ADR 4: AI generation vs teacher-support interpretation boundary
- ADR 5: Podcast MVP service boundary (only if still needed after the shared data/session contract is drafted)

## 12. Resolved Decisions and Remaining Deferred Items
- Resolved: the backend shape is a FastAPI modular monolith backed by Supabase PostgreSQL, not a Supabase-only thin-functions backend.
- Resolved: session/path persistence is event-sourced. Raw events are append-only; `student_rm` renders/resumes learner state; `analytic_rm` powers teacher-support projections.
- Resolved: the first teacher entry point is the V1 class overview, with drill-down into protected per-student, per-chapter review.
- Resolved: teacher-student authorization is B2B/tenant-scoped through school-managed roster membership, active class membership, active teaching assignment, and consent-gated analytics.
- Resolved: the minimum teacher overview before drill-down is roster/activity/consent context, never ranked severity.
- Remaining: exact session/path artifacts for podcast input snapshots, audio retention, and retry behavior belong in the API/database specs.
- Deferred: broader offline/reconnect workflows; queued offline sync; downloaded media/podcast playback; high-scale Redis/Celery queues; broader class-level teacher analytics beyond the bounded V4 extension.

## 13. Immediate Next Planning Artifacts
This execution plan should directly feed:
- detailed user flow pack for the release-critical journeys listed above
- shared data/session contract spec for session, node, edge, event, deletion, persistence, teacher-support, and podcast inputs
- ADR set for the listed cross-cutting decisions
- Mermaid diagrams only after the execution plan, flows, and shared contracts are stable enough to visualize without inventing behavior

## 14. Planning Snapshot
- First shippable slice: bounded learner exploration + narrow persistence/basic offline reopening + bounded teacher-support + podcast MVP
- Critical dependencies: session/path contract, deletion semantics, teacher authorization, persistence boundary
- Highest-risk drift areas: broader offline interpretation, teacher-surface expansion, accidental reintroduction of legacy node/editing assumptions
- Recommended next artifact after this document: shared data/session contract spec
