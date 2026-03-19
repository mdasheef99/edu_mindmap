# Shared Session/Path Data Contract (MVP)
## 1. Purpose
This document defines the minimum shared learner session/path contract required by the MVP so persistence/basic offline reopening, teacher-support interpretation, and podcast generation depend on the same bounded source data.
## 2. Scope and Source of Truth
This contract must stay aligned with:
- `docs/prd/master-prd.md`
- `docs/mvp-features-specification.md`
- `docs/teacher-support-mvp-specification.md`
- `docs/architecture-feature-mapping.md`
- `docs/planning/mvp-execution-plan.md`
If those documents change the product boundary, this contract should be updated explicitly.
## 3. Contract Guardrails
- The learner product is path-based conceptual exploration.
- Teacher-support interpretation is a separate protected layer built on learner session/path data.
- Learner-facing surfaces remain category-neutral.
- There is no Story Node.
- Learners do not edit node body/content.
- Branching happens only through phrase selection inside AI node content or the left/right edge `+` on an AI node.
- AI-generated path edges and manual reference links are distinct and must stay distinguishable in data.
- Deleting an AI-generated path node deletes descendant AI-path nodes after confirmation.
- MVP basic offline access is limited to reopening previously stored session state and content already generated online; no offline AI generation or queued sync behavior is implied.
## 4. Contract Model Overview
The minimum shared contract has six layers:
1. session context
2. nodes
3. edges
4. interaction events
5. locally persisted content/state
6. derived consumer inputs for teacher-support and podcast generation
## 5. Session Contract
Each learner exploration session must carry enough context to be resumed, interpreted, and converted into downstream inputs.
### Required session fields
- session identifier
- learner/user identifier
- exam identifier
- subject identifier
- chapter identifier
- concept entry identifier or equivalent starting-context reference
- created timestamp
- last-updated timestamp
- current/last-active node identifier
- session status marker sufficient for reopen/resume flows
### Session rules
- A session is chapter-scoped for MVP planning purposes.
- Resume behavior should restore the learner to the correct chapter/session context.
- Teacher-support and podcast generation should reference the same session identifier.
## 6. Node Contract
Nodes represent persisted board objects inside a session.
### Required node fields
- node identifier
- session identifier
- node type
- parent node identifier when applicable
- content payload already received online
- creation source marker
- created timestamp
- layout/system metadata needed to reopen the board state
### Node rules
- Node type must distinguish at least AI nodes from non-AI support nodes.
- Learner-authored body content is not part of the contract.
- Nodes created from phrase selection or edge `+` must retain enough lineage to reconstruct how they were reached.
## 7. Edge Contract
Edges define relationships between nodes and must preserve the difference between exploration-path structure and learner-created reference structure.
### Required edge fields
- edge identifier
- session identifier
- source node identifier
- target node identifier
- edge type
- creation label or trigger text when relevant
- created timestamp
### Edge rules
- Edge type must distinguish `ai_path` from `manual_reference` or equivalent values.
- Teacher-support and podcast consumers should treat AI-path edges as the ordered exploration structure.
- Manual reference links must not be misread as path progression.
## 8. Interaction Event Contract
Events are required because final node/edge state alone is not enough to reconstruct the learner path.
### Required event categories
- session opened/resumed; node viewed/visited; phrase offer set shown; phrase option selected
- edge-`+` offer set shown; follow-up question selected; manual reference link created
- node deleted with confirmed cascade; podcast generation requested
### Required event fields
- event identifier
- session identifier
- event type
- timestamp
- source node identifier when applicable
- target node identifier when applicable
- offer-set identifier when applicable
- selected option identifier/text when applicable
- thread-context reference when applicable
### Event rules
- Ordered node visits, offer sets, question selections, timestamps, revisits, and thread context must be reconstructable from the event stream.
- Offer-set exposure and selection should both be captured.
- A dismissed/no-selection outcome should be representable when an offer set is shown but not chosen.
## 9. Offer-Set and Thread-Context Requirements
- Each generated offer set should have its own identifier.
- Offer sets should retain origin context: source node, launch method, and generation timestamp.
- Child AI nodes should retain a thread-context reference sufficient to continue exploration from the correct prior context.
- Multiple sibling branches from the same parent should remain individually distinguishable.
## 10. Deletion and Cascade Semantics
- Deleting an AI-path node must remove descendant AI-path nodes after confirmation.
- Related AI-path edges for deleted descendants must also be removed.
- Manual reference links attached to removed nodes must be cleaned up as part of the same operation.
- The deletion event should record the root deleted node and the cascade result.
- Teacher-support and podcast consumers must not read deleted path artifacts as active session structure.
## 11. Local Persistence and Basic Offline Boundary
- Persist locally: session context, node state, edge state, recent interaction history needed for reopen/resume, and content already generated online.
- Do not treat local persistence as support for offline AI generation, offline editing beyond the persisted state, offline sync queues, offline video behavior, or offline podcast playback.
- Reopening while offline is limited to previously stored content/state that already exists on-device.
- If required session content was never stored locally, the contract should allow safe failure rather than implying offline completion.
## 12. Teacher-Support Input Contract
### Required teacher-support inputs
- learner identifier
- chapter identifier
- ordered path progression across AI-path nodes
- node visits and revisits
- offer-set exposure and selection history
- thread progression/context references
- deletion-aware current session structure
### Teacher-support rules
- Teacher-support remains per-student and chapter-level in MVP.
- Teacher-facing interpretation is derived from learner session/path data; it is not a separate learner-visible contract.
- Access to teacher-support views must remain role-gated and authorization-bound.
## 13. Podcast Input Contract
Podcast generation should consume the shared learner session/path contract rather than a parallel summary model.
### Required podcast inputs
- session identifier
- chapter/context identifiers
- ordered explored path across AI-path nodes
- retained node content already generated online
- selected follow-up questions or phrase-driven branch selections
- sufficient thread/context references to generate a coherent recap
### Podcast rules
- Podcast generation is session-based for MVP.
- Podcast playback is in-app for generated audio; offline playback/download is out of scope.
- Deleted or stale path artifacts should not be included in the generated podcast input.
## 14. Acceptance Checks
This contract is usable for MVP only if it supports:
- resume/reopen of the correct learner session
- clear distinction between AI-path edges and manual reference links
- reconstruction of ordered exploration events
- deletion-aware teacher-support inputs
- deletion-aware podcast inputs
- narrow local reopening of previously stored content while offline
## 15. Open Questions and ADR Follow-Up
- Open Question: what is the exact first persisted representation format: normalized relational shape, document snapshot shape, or a hybrid?
- Open Question: how much event history must be stored locally versus remotely for MVP continuity and interpretation?
- Open Question: should manual reference-link creation be fully evented from day one or only stored as final edge state plus timestamp?
- ADR follow-up: learner session/path data model; local persistence boundary; teacher-support authorization boundary; podcast service/input boundary