# Backend / Infrastructure MVP Strategy

> **Note**: This document has been partially superseded by `docs/architecture/backend-architecture.md`,
> which resolves the open questions and provisional items marked below. Where the two documents conflict,
> `backend-architecture.md` governs.
## 1. Purpose
This document defines the minimum backend and infrastructure strategy required to ship the current MVP without expanding scope beyond the approved learner, teacher-support, persistence, offline, and podcast boundaries.

## 2. Scope and Source of Truth
This strategy must stay aligned with:
- `docs/prd/master-prd.md`
- `docs/mvp-features-specification.md`
- `docs/teacher-support-mvp-specification.md`
- `docs/architecture-feature-mapping.md`
- `docs/system-architecture.md`
- `docs/planning/mvp-execution-plan.md`
- `docs/planning/session-path-data-contract.md`
- `docs/planning/release-critical-user-flows.md`

If those documents change the product boundary, update this strategy explicitly rather than inferring a broader backend scope here.

## 3. Strategy Guardrails
- Product framing remains path-based conceptual exploration with teacher-support as a separate protected layer.
- Learner-facing surfaces remain category-neutral.
- There is no Story Node and no learner editing of node body/content.
- Branching happens only through phrase selection inside AI content or the left/right edge `+` on an AI node.
- AI-generated path edges and manual reference links remain distinct in storage, events, and downstream processing.
- Deleting an AI-generated path node deletes descendant AI-path nodes after confirmation.
- MVP includes session persistence, narrow offline reopening of previously stored content, session-based podcast generation, and a protected teacher-support MVP surface.
- MVP excludes offline AI generation, offline editing beyond persisted state, offline sync/queued sync, offline video behavior, downloaded media/podcast offline playback, and broader full-offline behavior.
- Do not treat Redis, CDN, read replicas, Celery/worker fleets, TimescaleDB, or similar scale-oriented references as MVP requirements unless confirmed elsewhere.

## 4. Current Backend Direction Already Reflected in the Docs
The current documents already imply a backend direction, even though not every infrastructure choice is finalized:
- Supabase-backed authentication and durable product data storage are part of the current MVP direction.
- Local persistence via AsyncStorage supports resume continuity and narrow offline reopening.
- Learner session/path data is the shared contract feeding persistence, teacher-support, and podcast generation.
- AI exploration generation and post-hoc interpretation/classification are separate processing steps.
- Teacher-support is derived from learner session/path data and must stay protected by role/authorization boundaries.
- Podcast generation is session-based and should consume the same session/path contract rather than a separate summary model.
- Offer-set logging and interaction/event capture are required because final board state alone is not enough for reconstruction.

## 5. Stable MVP Backend Decisions
These decisions are stable enough to plan against now and later formalize as ADRs:
- ✅ **Auth and protected access are required**: learner and teacher-facing surfaces must be separated by authenticated, authorization-bound access control.
- ✅ **Supabase/Postgres is the working MVP data platform direction** for authenticated user data, curriculum-linked data, and durable learner session/path storage.
- ✅ **Local persistence is required** for session resume and narrow offline reopening of already stored content.
- ✅ **The shared session/path contract is the core backend data boundary** for persistence, teacher-support inputs, and podcast inputs.
- ✅ **Backend-managed AI/TTS integration is required as a service boundary** so teacher-support derivation, podcast generation, and credentialed third-party calls stay outside the mobile client.
- ✅ **Interaction/event capture is required**, including offer-set exposure and selection, because downstream interpretation depends on path reconstruction rather than final state alone.
- ✅ **Teacher-support remains a separate derived layer**, not a learner-visible categorization system.
- ✅ **Podcast generation is in scope for MVP**, but only as session-based generation and in-app online playback.

## 6. Provisional or Deferred Backend References
These appear in the docs or supporting references but should not be treated as finalized MVP commitments:
- ✅ **Backend runtime**: **FastAPI** confirmed as the implementation choice; see `backend-architecture.md` §3.
- ⚠️ **Realtime subscriptions**: explicitly **deferred** — not required for the first shippable slice (no multi-user sync in MVP).
- ⚠️ **Object/media storage details**: generated podcast audio may require temporary or durable storage, but retention policy and storage shape are not yet fixed.
- ✅ **Background job infrastructure**: **Postgres `SELECT ... FOR UPDATE SKIP LOCKED` queue** confirmed as the MVP form; see `backend-architecture.md` §8.1. Dedicated queue infrastructure (Redis, Celery) deferred to scale only.
- ⚠️ **Expanded analytics/storage layers**: broader experimentation, pattern mining, content-library promotion, or specialized analytics stores are beyond the minimum MVP need.
- ⚠️ **Teacher access-control expansion**: broader admin workflows, privilege tiers, and operational tooling belong to later-phase references, not the bounded MVP surface.
- ⚠️ **Redis**: explicitly **deferred to scale form only**; MVP uses the Postgres `SKIP LOCKED` pattern per `backend-architecture.md` §8.1.
- ⚠️ **B2B institutional model**: `backend-architecture.md` §5 introduces a `school_admin` role, institutional membership model, roster enrollment flow, and `api/admin` router that go beyond the original MVP scope described in this document. This is a **scope expansion** that should be reviewed against the MVP boundary before implementation begins.
- ⚠️ **Consent and DPDP Act 2023 handling**: `backend-architecture.md` §12 introduces consent as a **first-order design constraint** with structural consequences — consent gates projection building, and withdrawal triggers replay. This was not in the original strategy and is a **confirmed addition**; it affects the schema, event flow, and worker behavior from the first migration.

## 7. Open Questions
These should remain explicitly open until decided in an ADR or more detailed service/schema spec:
- ✅ **Persisted representation shape**: **resolved** — fully normalized relational schema with event sourcing (append-only event store + CQRS read models). See `backend-architecture.md` §7.
- ❓ What is the minimum local-versus-remote event history split needed for MVP continuity, teacher-support, and podcast generation?
- ✅ **Manual reference-link creation**: **resolved** — fully evented from day one via `edge_created` / `edge_deleted` events (distinguishing `ai_path` from `manual_reference`). See `backend-architecture.md` §6.2.
- ✅ **Teacher entry point**: **resolved** — V1 class overview followed by authorized class/student/chapter drill-down. See `docs/teacher-dashboard-specification.md` and `docs/api/teacher-api-spec.md`.
- ✅ **Teacher-student authorization linkage**: **resolved** — `teaching_assignments` table with active interval scoping (a teacher sees a student only while both hold active assignments/memberships in the same class). See `backend-architecture.md` §5.1 and §5.3.
- ✅ **Podcast inputs**: **resolved** — session-derived path artifacts (node summaries, selected questions) are the mandatory inputs; optional enrichments include checkpoint responses and prior-session context. Retention and storage shape defined in `backend-architecture.md` §8.2 and §11 (podcast worker row).

## 8. Minimal MVP Service Boundary
The MVP should be planned as five bounded layers:
1. **Mobile client**
   - Handles learner interaction, local state, local persistence, and online/offline reopen behavior.
   - Captures session, node, edge, and interaction events at the point of use.
2. **Backend application/service layer**
   - Authenticates requests and enforces learner/teacher authorization boundaries.
   - Accepts session/path writes from the client.
   - Orchestrates AI generation, post-hoc classification/interpretation, and podcast generation.
   - Exposes teacher-support and podcast endpoints derived from shared session/path data.
3. **Durable product data platform**
   - Stores users, roles, authorization relationships, curriculum-linked data, session metadata, nodes, edges, and server-side event history.
4. **AI services**
   - Provide exploration generation and secondary interpretation/classification steps.
5. **TTS/audio generation service**
   - Produces playable podcast audio from approved session-derived inputs.

### Boundary rule
For MVP planning, the client should not be treated as the long-term owner of protected teacher logic, podcast orchestration, or third-party AI/TTS credentials.

## 9. Persistence and Session/Event Strategy
### Local persistence responsibilities
- Persist chapter-scoped session context, current board state, already generated node content, and enough recent state to resume and reopen later.
- Support narrow offline reopening only for content already present on-device.
- Fail safely when required content was never stored locally.

### Remote persistence responsibilities
- Store authenticated user/account context and teacher authorization relationships.
- Store durable learner session metadata, nodes, edges, and the event trail needed for teacher-support and podcast generation.
- Preserve the distinction between `ai_path` edges and `manual_reference` edges.
- Retain deletion-aware current structure so removed path artifacts are not interpreted downstream.

### Sync behavior for MVP
- Treat the product as **online-first with local continuity**, not as a generalized offline-sync system.
- When online, client interactions should be persisted remotely quickly enough to support teacher-support and podcast workflows.
- Do not promise queued writes, conflict resolution, or eventual background sync while offline.

## 10. Infrastructure Required Now vs Deferred
### Required now
- Supabase Auth for authenticated access.
- PostgreSQL-backed durable storage for user/session/path data.
- A thin backend/service layer between client and AI/TTS providers.
- Local device persistence for resume and narrow offline reopen.
- AI provider integration for exploration generation and post-hoc interpretation/classification.
- TTS/audio generation integration for session-based podcast output.

### Deferred unless a concrete MVP blocker appears
- Redis or similar cache infrastructure.
- CDN/read replicas/multi-region scale infrastructure.
- Dedicated analytics database such as TimescaleDB.
- Large worker fleet or Celery-style task system.
- Broader content caching/library promotion pipelines.
- Realtime collaboration or expanded teacher analytics infrastructure.
- Offline media download/playback infrastructure.

## 11. ADR Candidates
These decisions are stable enough to convert into ADRs once implementation planning begins:
- ADR: MVP learner session/path persistence model.
- ADR: Local persistence and narrow offline boundary.
- ADR: Teacher-support authorization boundary.
- ADR: Backend service boundary for AI and TTS orchestration.
- ADR: Podcast MVP input/result boundary.

## 12. Recommended Immediate Follow-Up
The recommended **schema-and-endpoint decision set** has now been drafted in `docs/api/` and `docs/database/`. Those documents turn the shared session/path contract into:
- first-pass storage shape
- first-pass write/read API surface
- teacher authorization linkage model
- podcast request/result contract

The MVP is no longer blocked by broad backend direction or first-pass persistence/service-interface decisions. Development should now follow the phase gates in `docs/planning/development-approach.md`.

**Version History**:
- v1.0: Initial backend MVP strategy
- v1.1: Open questions closed and provisional items resolved per `backend-architecture.md`; B2B scope expansion and DPDP consent addition flagged; supersession note added.
- v1.2: Teacher entry point and schema/API decision-set status reconciled with `docs/api/` and `docs/database/`.