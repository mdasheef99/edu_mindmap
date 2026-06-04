# Master PRD: Path-Based Conceptual Exploration Platform

## 1. Product Vision

This platform is a syllabus-driven product for path-based conceptual exploration in exam preparation. Students explore a chapter through a bounded mind map while the system records what was offered, what was selected, and how the exploration path unfolded. Those signals are then interpreted through an internal analytic framework to support teacher judgment without exposing category logic to learners.

It is not designed to function as a question bank, a tutoring replacement, a freeform note canvas, or a mastery-certification engine.

The product is differentiated by combining chapter pre-analysis, runtime path capture, and teacher-support interpretation so that follow-up can reflect how a learner explored a concept, not only whether they answered something correctly or consumed content.

## 2. Primary User and Context

The initial learner focus is students in India preparing for defined-syllabus exams. This includes Class 10 and Class 12 board exams, competitive entrance exams such as JEE and NEET, and later exam sets once syllabus mapping is in place.

The primary launch context is school- and institution-led use. Students explore chapters independently, and teachers review exploration evidence before the next class. Direct-to-student usage may develop in parallel over time, but it is not the primary launch distribution strategy.

Secondary users are teachers and school administrators who use the interpretation layer to review student exploration, identify likely under-explored areas, and prepare targeted follow-up.

The platform is structurally exam-agnostic once Level 1 syllabus mapping and Level 2 chapter analysis are complete for a given exam, subject, and chapter set.

## 3. Core Problem Statement

Students preparing for syllabus-bound exams often accumulate notes, videos, and solved questions without a clear view of which parts of a concept they have actually explored. A learner can remain busy and still leave important boundaries, relationships, constraints, or variations thinly explored.

Most alternatives deliver static content, practice questions, or prescribed tutoring flows. They do not reliably capture the path of conceptual exploration, and they do not turn that path into a usable teacher-support signal.

This platform addresses that gap by grounding each chapter in a pre-analyzed conceptual structure, allowing students to explore through a bounded mind map, and surfacing probabilistic teacher-support signals about likely under-explored areas before the next class.

## 4. How the Platform Works

The foundational capability is a two-layer preparation and interpretation model.

**Layer 1: syllabus mapping** defines the structural skeleton of the product: exam to subject to chapter to concept. This is what makes the platform scalable across multiple exam types while keeping the learner experience chapter-bounded and syllabus-aligned.

**Layer 2: chapter analysis** prepares each launch chapter before students arrive. For each chapter, the system defines the concept inventory, key dependencies, intra-chapter connections, internal analytic availability, chapter-level weight modifiers, and seed questions. This layer improves generation quality by grounding responses in chapter structure and establishes the coverage landscape against which later exploration can be interpreted.

At runtime, the student selects an exam, subject, chapter, and concept entry point, then explores through AI-generated responses and bounded branching inside the mind map. Exploration remains organic-first: the system generates natural next-question options from current node context and phrase anchors rather than forcing visible category coverage.

Each selected question is classified post hoc against an internal 8-dimension engagement model. The system records ordered node visits, offer sets, question selections, timestamps, revisits, and thread context so that the learner path can be reconstructed as a sequence of exploration events rather than a flat activity log.

When the classified path shows a meaningful dimensional shift, the product may invite an optional **Reflective Checkpoint / Sensemaking Pause**. This is a low-stakes, category-neutral prompt to help the learner notice current thinking. It offers Try Now, Not Sure Yet, Snooze, and Skip actions; it is not a quiz, grade, mastery claim, or mandatory progression gate.

Those signals feed the teacher-support layer. Teachers can review a student's chapter path, see what was explored and what remains thin, inspect weighted coverage patterns, review checkpoint responses or opt-out patterns as cautious metacognitive signals, and use suggested follow-up prompts to prepare targeted scaffolding. The product is intended to inform teacher judgment, not replace it.

## 5. Product Principles and Boundaries

The platform is guided by six operating rules.

First, **student-facing category invisibility is mandatory**. Student surfaces must not reveal category names, hidden dimension labels, scores, meters, or language that implies the system can infer internal cognitive state with certainty.

Second, **claims are probabilistic, not definitive**. The system may surface likely under-explored areas or patterns worth follow-up, but it must not claim certainty about what a learner does or does not understand.

Third, **teacher-support interpretation is a separate layer from learner experience**. Teachers and admins may see richer category-visible interpretation; students should receive category-neutral exploration support only.

Fourth, **organic-first generation remains the runtime default**. Question generation should emerge from chapter context, node context, and phrase anchors rather than from visible analytic templates or forced category balancing.

Fifth, **the teacher is an informed conversational guide, not a replaced authority**. The product's value comes from making follow-up more targeted and timely, not from removing teacher judgment.

Sixth, **Reflective Checkpoints are optional sensemaking pauses, not tests**. They may actively probe current thinking after meaningful path shifts, but student choices to answer, skip, snooze, or mark uncertainty must be interpreted as low-stakes metacognitive evidence rather than grades or proof of mastery.

## 6. MVP Scope and User Journey

### In scope for MVP

- Exam, subject, chapter, and concept selection, including curriculum-guided entry and chapter search
- Dashboard-based re-entry through continue-learning and recent-session access
- Bounded mind map with concept-centered exploration nodes
- Session persistence and basic offline access so learners can resume chapter exploration and reopen previously stored session content across app restarts
- Organic question discovery from node and thread context
- Post-hoc dimensional classification for internal analysis
- Optional Reflective Checkpoints / Sensemaking Pauses triggered by meaningful dimensional shifts in the classified learner path
- AI responses to selected questions
- Phrase-anchored child-node creation
- Edge `+` question discovery on AI nodes
- Image and video nodes as supporting learning media
- Previous year questions as a chapter-linked exam-preparation support layer
- Podcast generation from exploration sessions as a reinforcement workflow
- Pre-analyzed launch chapters through syllabus mapping and chapter analysis
- Basic teacher view with per-student paths, explored vs unexamined concepts, weighted coverage patterns, and suggested follow-up prompts
- Teacher-support visibility into checkpoint response quality and opt-out patterns as cautious, probabilistic metacognitive signals
- Offer-set logging, path capture, and discovery/exploitation tagging from day one

**Image-node clarification**: Image nodes are in MVP as supporting learning media. The MVP commitment is a minimum standalone image-node surface for adding/importing, viewing, manually linking, and deleting image nodes. Richer image-specific AI/search workflows may remain advanced enhancement-tier capabilities without moving image nodes themselves out of MVP.

### Out of scope for MVP

- Full teacher dashboard with class-level analytics and ranked severity views
- Broader reflective guidance and self-review system beyond the bounded MVP Sensemaking Pause
- Broader offline capability beyond basic reopening of previously stored session content as a later platform feature rather than a current MVP requirement
- Formal quiz/testing framework, scoring, mastery certification, or mandatory assessment gates as a core product layer
- Cross-chapter concept tracking
- Collective-intelligence personalization from aggregate data
- Advanced analytics and outcome prediction
- Adaptive question ranking as the default experience

### MVP happy path: student

The student selects an exam, subject, chapter, and concept, opens an AI explanation node, and branches in only two ways: by selecting a phrase inside AI content or by tapping the left or right edge `+` on an AI node. Each selection creates a child AI node, extends the exploration path, and preserves context for later branching. Over the course of a session, the learner builds a bounded concept map that reflects what they actually explored rather than a generic content feed. When the path makes a meaningful conceptual move, the learner may receive an optional, non-graded Sensemaking Pause with Try Now, Not Sure Yet, Snooze, and Skip options. The learner can leave and later reopen previously stored session content to continue the same chapter exploration, pull in previous year questions where useful, and optionally generate a reinforcement podcast from the explored session.

### MVP happy path: teacher

Before the next class, the teacher opens the chapter-level teacher view, reviews each student's exploration path, checks which concepts were explored and which likely high-priority areas remain thin, reviews any checkpoint response quality or repeated opt-out patterns as low-stakes metacognitive signals, and uses suggested follow-up prompts to prepare class discussion or targeted student follow-up. The product succeeds only if this view is useful enough to change what the teacher does next.

### Minimum viable chapter coverage for launch

A chapter should not ship in MVP unless its Level 1 syllabus mapping and Level 2 chapter analysis are complete. At minimum, launch chapters need exam-subject-chapter mapping, a concept inventory, intra-chapter concept connections, dimensional availability analysis, and enough seed-question coverage to ground both generation and interpretation.

## 7. Mind Map Interaction Model

The mind map is a bounded exploration surface, not a freeform editing canvas.

The interaction rules are fixed for the current product scope. There is no Story Node. Students do not edit node body content. Branching happens only from AI nodes through phrase selection inside AI content or through the left/right edge `+`. Duplication may exist as a utility action, but it is not the primary branching model.

Current node types are AI nodes, text nodes, video nodes, and image nodes. AI nodes carry the exploration path; the other node types support context, media, or reference.

The product supports two edge categories. **AI-generated exploration path edges** are created only through phrase selection or edge `+` branching and represent the persistent parent-child learning path. **Manual reference links** are learner-created connections between nodes for reference purposes and remain a separate category in the product logic.

Deleting an AI path node should require clear confirmation and should also delete its descendant path nodes. Manual reference links are separate and do not define the same cascading structure.

## 8. Teacher Support Layer

In MVP, teacher support is chapter-level, per-student, and action-oriented. Teachers should be able to see each student's exploration path within a chapter, which concepts were explored or skipped, which weighted areas appear relatively strong or thin, optional checkpoint evidence where available, and suggested follow-up prompts framed for teacher use.

The teacher uses this information to decide what to ask next, which concept to revisit, which comparison to surface in class, or which student may need more targeted support. Optional checkpoint data may add evidence about current sensemaking or uncertainty, but the intended action is not high-stakes diagnosis or formal remediation planning; it is fast, evidence-informed instructional preparation.

The teacher layer must be framed consistently: it surfaces probabilistic interpretation and possible follow-up areas, not certainty claims about what a student definitively understands.

This layer is central to the school-first distribution strategy. If teachers do not find it useful enough to check before the next class, the institutional wedge weakens significantly.

## 9. Success Metrics

### Leading indicators

- Students complete at least one full concept exploration session per chapter
- Students return for a second session on the same chapter
- Average questions selected per session
- Reflective Checkpoint action distribution: Try Now / Not Sure Yet / Snooze / Skip after eligible shifts
- Breadth of distinct node exploration within a chapter
- Offer-set engagement rate: questions offered versus questions selected

### Teacher engagement indicators

- Teachers open the chapter-level teacher view before class after student exploration sessions
- Teachers report that the information changes their follow-up choices
- Teachers can identify a next instructional move quickly from the teacher view

### Lagging indicators

- Teacher-reported improvement in class discussion quality
- Student-reported improvement in readiness or confidence before the exam
- Measurable relationship between exploration depth and later performance where exam or assessment data is available

### What failure looks like

The core loop is likely not working if students stop after one shallow session, branching remains low, same-chapter return stays weak, teachers do not use the teacher view before class, or the surfaced signals do not influence instructional follow-up in practice.

## 10. Later Phase Capabilities

- **Expanded student reflective guidance and self-review**: richer category-neutral recap, next-step support, and low-stakes review beyond the MVP Sensemaking Pause. Source: `docs/student-reflective-guidance-and-self-review.md`.
- **Expanded teacher dashboard**: class-level analytics, stronger prioritization views, and richer trend interpretation beyond the MVP teacher view.
- **Broader offline continuity capability**: later offline behavior beyond basic MVP reopening of previously stored chapter/session content, including any richer offline workflows that are not part of current scope.
- **Formal quiz and testing layer**: bounded assessment or checking workflows beyond the non-mandatory MVP Sensemaking Pause, once validation and product role are clearly defined.
- **Cross-chapter and aggregate intelligence layers**: broader concept tracking, content-library reuse, and later personalization based on converged path data. Source: `docs/content-library-specification.md`.
- **Advanced optimization and prediction**: adaptive ranking, more advanced analytics, and outcome prediction only after measurement quality and validity requirements are met.

## 11. Open Questions and Risks

### Open questions

- Which exact exam, subject, and chapter set constitutes the first launch syllabus tranche?
- What is the smallest teacher-facing surface that is still useful enough for before-class MVP use: a dedicated dashboard, a lightweight chapter view, or another constrained surface?
- What operational threshold should define when an area is significant enough to surface as a likely follow-up without overstating certainty?
- How should checkpoint frequency, snooze cooldowns, and repeated opt-out thresholds be tuned to preserve learner agency while producing useful signals?
- What outcome data will be realistically available early enough to test relationships between exploration depth and exam performance?

### Key risks

- Teacher adoption risk: the teacher layer may not become useful enough to affect classroom preparation
- Measurement risk: weak offer-set logging or erosion of the discovery floor would reduce interpretability
- UX risk: the mind map may become visually complex before the value of path-based exploration is clear
- Trust risk: overly strong wording could create false certainty or expose internal category logic to learners
- Operations risk: pre-analyzing enough high-quality launch chapters is a real production bottleneck

## 12. Supporting Documentation

- `docs/framework-design-philosophy.md` — Core philosophy, category invisibility, path capture, organic-first rules, and teacher-support positioning. **Authoritative for product principles and claim boundaries.**
- `docs/theory-of-change.md` — Causal model linking natural exploration, analytic interpretation, and teacher follow-up. **Authoritative for theory-of-change framing.**
- `docs/system-architecture.md` — Runtime system flow, Stage 1 generation, Stage 1A phrase anchoring, Stage 2 classification, and overall product architecture. **Authoritative for pipeline structure.**
- `docs/subject-weighting-specification.md` — Subject-specific weighting as an interpretive lens rather than a proof mechanism. **Authoritative for weighting logic.**
- `docs/measurement-and-experimentation.md` — Offer-set logging, discovery/exploitation policy, randomized probes, and evaluation requirements. **Authoritative for measurement policy.**
- `docs/architecture/llm-pipeline.md` — Lower-level LLM flow and prompt-stage details supporting the architecture docs.
- `docs/architecture/data-collection.md` — Storage and data-model details supporting runtime logging and path capture.
- `docs/content-library-specification.md` — Content-library and aggregate reuse model for later-phase convergence and personalization.
- `docs/student-reflective-guidance-and-self-review.md` — Future learner-facing reflective guidance, self-review, and next-step support boundaries. **Authoritative for later-phase learner guidance positioning.**
- `docs/mobile-features-core-ui.md` — Current core mobile UI, node types, canvas behavior, and deletion/reference-link rules. **Authoritative for core mind map interaction details.**
- `docs/mobile-features-ai-integration.md` — Question discovery flow, phrase selection flow, edge `+` behavior, and AI-path edge logic. **Authoritative for AI branching behavior.**
- `docs/mvp-features-specification.md` — Current MVP feature reference tying product behavior to implementation areas.
- `docs/teacher-support-mvp-specification.md` — Current bounded teacher-facing MVP surface and minimum access boundary. **Authoritative for current MVP teacher-support scope.**
- `docs/architecture-feature-mapping.md` — Mapping from product behavior to implementation pillars and architectural constraints.

The split mobile feature documents above are the current authoritative source for mind map behavior. Legacy combined mobile specs should be treated as reference-only wherever they conflict with the split documents.