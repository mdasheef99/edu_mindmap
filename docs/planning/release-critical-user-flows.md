# MVP Release-Critical User Flows
## 1. Purpose
This document identifies the current MVP flow set, separates release-critical flows from supporting flows, and defines the flow outlines needed to validate the first shippable slice end to end.
## 2. Source of Truth
This flow pack must stay aligned with:
- `docs/prd/master-prd.md`
- `docs/mvp-features-specification.md`
- `docs/teacher-support-mvp-specification.md`
- `docs/planning/mvp-execution-plan.md`
- `docs/planning/session-path-data-contract.md`
## 3. Scope Guardrails
- The product is path-based conceptual exploration.
- Teacher-support interpretation is a separate protected layer from the learner experience.
- Learner-facing surfaces remain category-neutral.
- There is no Story Node.
- Learners do not edit node body/content.
- Branching happens only through phrase selection inside AI node content or the left/right edge `+` on an AI node.
- AI-generated path edges and manual reference links are distinct.
- Deleting an AI-generated path node deletes descendant AI-path nodes after confirmation.
- MVP includes session persistence, narrow basic offline reopening of previously stored content, podcast generation from exploration sessions, and a protected teacher-support MVP surface.
- MVP excludes offline AI generation, offline editing beyond persisted state, offline sync/queued sync, offline video behavior, downloaded media or podcast offline playback, and broader full-offline behavior.
## 4. Full MVP Flow Inventory
### Release-critical flows
- **RC1** Learner chapter entry and first AI-node opening
- **RC2** Learner branching via phrase selection inside AI content
- **RC3** Learner branching via AI-node edge `+`
- **RC4** Learner deletion of an AI-path node with confirmed descendant cascade
- **RC5** Learner exit and return via Continue Learning / Recent Sessions
- **RC6** Learner reopening previously stored content in the narrow approved offline case
- **RC7** Learner podcast generation and in-app playback while online
- **RC8** Authorized teacher opens the protected per-student, per-chapter teacher-support view
### Supporting / secondary flows
- **S1** Learner creates a manual reference link
- **S2** Unauthorized teacher access is denied
- **S3** Offline reopen fails safely when required content was never stored locally
## 5. Why These Are the Release-Critical Flows
The release-critical set proves the first shippable MVP slice end to end:
1. learner enters a chapter and starts a real session
2. learner explores through both approved branching flows
3. learner path integrity survives deletion behavior
4. learner can leave and return to persisted work
5. previously stored content can be reopened in the narrow offline case
6. a session can produce a podcast while online
7. an authorized teacher can open the bounded teacher-support view derived from the same session/path data
Supporting flows still matter, but they do not define the minimum release boundary as directly as the RC set.
## 6. Release Boundary Sequence
Recommended validation sequence:
1. RC1
2. RC2 and RC3
3. RC4
4. RC5
5. RC6
6. RC7
7. RC8
S1-S3 should be validated alongside the sequence above where relevant.
## 7. Release-Critical Flow Outlines
### RC1. Learner chapter entry and first AI-node opening
- **Goal:** start the correct chapter-scoped exploration session.
- **Preconditions:** learner is authenticated; curriculum context is available; network is available for first AI load.
- **Happy path:** learner selects exam/subject/chapter/concept → app creates or opens the chapter session → first AI node loads → session context and initial node state are persisted.
- **Contract touchpoints:** session context, first node record, node-visit/open event, last-active node.
- **Acceptance focus:** correct chapter/session opens; no Story Node or learner node-body editing appears.
### RC2. Learner branching via phrase selection
- **Goal:** prove branching path 1 of the exploration model.
- **Preconditions:** learner is viewing an AI node with selectable content; network is available.
- **Happy path:** learner selects a phrase → system shows phrase-conditioned offer set → learner chooses an action/question → child AI node is created with an AI-path edge.
- **Contract touchpoints:** offer-set exposure, selected option, child node, AI-path edge, thread-context reference.
- **Acceptance focus:** child branch is path-linked, not a manual reference link; dismissed/no-selection can be represented.
### RC3. Learner branching via AI-node edge `+`
- **Goal:** prove branching path 2 of the exploration model.
- **Preconditions:** learner is viewing an AI node; network is available.
- **Happy path:** learner taps left/right edge `+` → system shows generated follow-up questions → learner selects one → child AI node is created with an AI-path edge.
- **Contract touchpoints:** offer-set exposure, selected question, child node, labeled AI-path edge, thread/path continuity.
- **Acceptance focus:** edge-triggered branching works as a distinct launch method while still producing the same path data category.
### RC4. Learner deletion of an AI-path node with confirmed descendant cascade
- **Goal:** preserve valid session/path structure after destructive changes.
- **Preconditions:** learner has an existing AI-path branch with descendants.
- **Happy path:** learner requests deletion → system shows confirmation → confirmed deletion removes the chosen AI-path node, descendant AI-path nodes, and related edges.
- **Contract touchpoints:** cascade deletion semantics, deletion event, updated node/edge state, deletion-aware current structure.
- **Acceptance focus:** descendant AI-path nodes are removed; manual reference links attached to removed nodes are cleaned up; deleted artifacts do not remain active downstream.
### RC5. Learner exit and return via Continue Learning / Recent Sessions
- **Goal:** prove normal persistence and resume continuity.
- **Preconditions:** a persisted chapter session already exists.
- **Happy path:** learner leaves app or session → app persists state → learner returns through Continue Learning or Recent Sessions → correct session reopens at the right chapter/context.
- **Contract touchpoints:** session identifier, chapter context, last-updated timestamp, last-active node, persisted node/edge state.
- **Acceptance focus:** learner returns to the correct session without path corruption or category-visible interpretation.
### RC6. Learner reopening previously stored content in the narrow approved offline case
- **Goal:** prove the included MVP offline boundary without implying broader offline mode.
- **Preconditions:** required session/content has already been stored locally.
- **Happy path:** learner loses connectivity or reopens while offline → app loads previously stored session/content from local persistence → learner can view prior state.
- **Contract touchpoints:** persisted session context, persisted node/edge state, stored generated content, safe-failure boundary if data is missing.
- **Acceptance focus:** reopen works only for previously stored content; no offline AI generation, no queued sync behavior, no offline playback claim.
### RC7. Learner podcast generation and in-app playback while online
- **Goal:** prove the confirmed MVP reinforcement workflow.
- **Preconditions:** a valid exploration session exists; network and audio generation services are available.
- **Happy path:** learner opens podcast generation from the session → chooses length → previews script → generates audio → listens in the in-app player.
- **Contract touchpoints:** session identifier, chapter/context identifiers, explored AI-path, retained generated node content, selected branch history.
- **Acceptance focus:** podcast input comes from the shared session/path contract; playback is in-app and online-only for MVP.
### RC8. Authorized teacher opens the protected per-student, per-chapter teacher-support view
- **Goal:** prove the bounded teacher-support MVP surface.
- **Preconditions:** teacher account exists; authorization relationship exists for the target student/chapter context.
- **Happy path:** authorized teacher opens protected teacher-facing surface → selects or lands on an authorized student/chapter → sees chapter path, explored vs relatively thin areas, weighted follow-up areas, and suggested prompts.
- **Contract touchpoints:** learner identifier, chapter identifier, ordered AI-path progression, node visits/revisits, offer-set exposure and selection history, deletion-aware current structure.
- **Acceptance focus:** teacher-facing interpretation stays protected and separate from learner-facing surfaces.
## 8. Supporting / Secondary Flow Notes
### S1. Learner creates a manual reference link
- Important for canvas completeness, but secondary to the release boundary.
- Must remain clearly distinct from AI-path branching in both UI and data.
### S2. Unauthorized teacher access is denied
- Required security behavior tied to RC8.
- Can be validated as a negative access case rather than a primary release journey.
### S3. Offline reopen fails safely when content is missing
- Required guardrail tied to RC6.
- The product should fail safely rather than implying unsupported offline completion.
## 9. Open Questions
- Open Question: what is the exact first teacher entry point before the per-student, per-chapter view: dedicated teacher dashboard or lighter chapter-review surface?
- Open Question: what is the first teacher-student authorization linkage model: roster import, school-managed assignment, or another constrained model?
- Open Question: what exact session/path artifacts are mandatory podcast inputs versus optional enrichments?
## 10. Immediate Use of This Document
This flow pack should now drive:
- detailed acceptance criteria and QA checks
- screen/state transition mapping
- ADR drafting where flow decisions become cross-cutting
- Mermaid diagrams only after these flow outlines remain stable

