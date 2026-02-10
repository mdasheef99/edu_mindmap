# Content Library Specification (Collective Intelligence Layer)

## Purpose
The **Content Library** is a persistent, versioned repository of **promoted** learning content derived from statistically significant aggregate usage.

It exists to:
- Serve high-quality, consistent questions/answers to most learners when patterns have converged.
- Reduce LLM cost/latency by reusing vetted content.
- Enable aggregate-driven **media recommendations** (videos/images) based on what helped similar learners.
- Preserve measurement quality via an explicit **organic discovery floor** (do not fully eliminate fresh generation).

## Terminology
- **Library**: persistent, promoted content (stored in DB/object storage) with versions, provenance, and performance stats.
- **Cache**: fast serving layer (e.g., Redis) for hot library items / recent results.
- **Path fragment**: a short sequence/graph motif (e.g., node context + offer set + selected question) that recurs across learners.

## Non-goals / guardrails
- Not student-facing: no category labels, no “8 dimensions” UI.
- Not a replacement for organic exploration: keep a tunable **discovery budget**.
- Not “optimize for diagnostic coverage” during generation; promotion is based on observed effectiveness, not category quotas.

---

## Serving flow (NovelPathHandler)
Given current context (chapter, node, recent path history):

1. **Exact match**
   - If the current context key matches a library item, serve it.

2. **Prefix / partial match**
   - If no exact match, match on a shorter history (e.g., last 1–2 steps) or a context hash.

3. **Hybrid composition**
   - If partial matches exist, compose an offer set using:
     - top library candidates (high success / high selection rate), plus
     - a small amount of safe variation (to avoid stagnation).

4. **LLM fallback**
   - If no reliable matches, generate organically (Stage 1), then classify post-hoc (Stage 2).

**Policy requirement**: every served offer set must be tagged with `source` (`library` | `cache` | `organic_llm` | `hybrid`) and `policy_version`.

---

## Write-time lifecycle (PathCachingManager)
### Eligibility signals
A candidate path fragment becomes eligible for promotion when it has:
- sufficient frequency (e.g., `MIN_SEQUENCE_FREQUENCY`),
- stable selection/engagement patterns,
- acceptable learning outcomes (where measurable: quiz/retention/proxy signals),
- acceptable safety/quality checks (no harmful content, no leakage of internal taxonomy).

### Promotion steps (conceptual)
1. Mine high-frequency fragments from logged **paths + offer sets**.
2. Aggregate performance metrics (selection rate, completion, outcome proxies).
3. Create a **canonical library item**:
   - prompt + context packet (text-only),
   - generated questions + reference answers/explanations,
   - metadata + version.
4. Run automated checks (format, toxicity, policy) + optional human review.
5. Publish version; start serving to eligible traffic with an organic floor.

### Refresh / decay
- Library items have refresh rules (TTL or drift detection).
- Items can be downgraded if performance drops or curriculum changes.

---

## Maturity tracking (LibraryMaturityTracker)
Library coverage evolves per chapter/subject:
- **Learning**: mostly organic generation; collect clean discovery data.
- **Convergence**: some fragments promoted; increasing reuse.
- **Mature**: most common contexts served from library; organic reserved for exploration/novelty.
- **Evergreen**: stable, periodically refreshed; strong monitoring.

(These are **states**, not timelines. Treat as operational modes.)

---

## Data model (placeholders)
Minimum conceptual entities:
- `library_items` (content, version, provenance, curriculum refs)
- `library_keys` (context hash / matching index)
- `library_metrics` (presentation/selection/outcome aggregates)
- `library_media_links` (recommended videos/images + evidence)

## Key knobs (initial defaults; tune with data)
- `MIN_SEQUENCE_FREQUENCY = 50`
- `MIN_PROBABILITY_THRESHOLD = 0.40`
- `CACHE_TTL_DAYS = 30`
- `ORGANIC_GENERATION_FLOOR = 0.30`
- `VARIATION_INJECTION_RATE = 0.15`

