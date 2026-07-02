# 08 Future Development Readiness

## Recommended Reading Order
1. `.augment/rules/00-canon.md`: The non-negotiable architectural invariants.
2. `docs/planning/development-approach.md`: High-level strategy.
3. `CODEBASE_INTELLIGENCE/01-system-map.md`: Current runtime architecture.
4. `CODEBASE_INTELLIGENCE/02-critical-flows.md`: Critical workflow files.

## Likely Touchpoints for New Features
- **Adding an AI Step**: `backend/app/runtime/offer_workflow.py` and `backend/app/llm_gateway/`.
- **New Mobile Interaction**: `mobile/canvas/SkiaCanvas.tsx` and `mobile/canvas/store.ts`.
- **New Read Model**: `backend/app/projections/` and `docs/database/read-models-schema.md`.
- **New Event Type**: `backend/app/events/` (Registry + Schema).

## Known Stale/Uncertain Areas
- **Mobile Agent Docs**: `mobile/app/AGENTS.md` (included by `CLAUDE.md`) now points to this pack and the Expo v56 versioned docs; keep both in sync if the mobile runtime changes.
- **Supabase Auth Integration**: Milestone M4 is the transition from test tokens to real Supabase Auth. Live verification of the JWT resolution in `backend/app/tenancy/auth.py` is needed.

## Next Recommended Tasks
- **Milestone M4**: Implement real Supabase Auth integration.
- **Milestone M4**: Implement Curriculum Entry surface (Teacher dashboard).
- **Optimization**: Transition from replaying all events to using periodic read-model snapshots for canvas hydration.

## Assumptions Needing Verification
- **Network Latency**: Evaluate the impact of replaying events server-side for every `GET /sessions` call as the session grows.
- **Device Support**: Skia performance has been verified on Android; iOS verification is still "operationally pending".
