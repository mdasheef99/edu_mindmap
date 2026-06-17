# /bootstrap — re-establish Phase 1 context

Re-ground yourself in the Context Continuity Framework before doing anything else.
Read the following, in order, then **state the current Phase 1 status back to the user
before proposing or editing anything**:

1. `.augment/rules/00-canon.md` — the canon (hierarchy, invariants, blacklist).
2. `docs/planning/sdd/phase-1-walking-skeleton-sdd.md` — the active blueprint
   (authoritative requirement text).
3. `docs/planning/worklog.md` — the live tracker. Report:
   - Red-test progress (count of not-started / red / green / deferred out of 25).
   - Definition-of-Done checklist progress (done / open).
   - The current **Open Decisions** entry (the consent-gate status).

## Rules for this re-grounding
- Resolve any ambiguity using the Source-of-Truth hierarchy in `00-canon.md`
  (higher-ranked documents win on conflict).
- Every requirement or edit you propose must cite a specific section (§) in a
  source-of-truth document. Do not originate requirements.
- Honor the non-negotiable invariants: Category Invisibility, Organic-First,
  Tenant Isolation, Event Sourcing.
- Do NOT propose or edit until you have stated the current status back to the user.
