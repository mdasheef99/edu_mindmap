#!/usr/bin/env bash
# Surfaces the live Phase 1 state at session start so the agent grounds itself in the
# current worklog rather than stale memory. Read-only; never mutates the repo.
set -euo pipefail

WORKLOG="docs/planning/worklog.md"
SDD="docs/planning/sdd/phase-1-walking-skeleton-sdd.md"

echo "=== MINDMAP — LIVE PHASE 1 CONTEXT (auto-surfaced at session start) ==="
echo
echo "ACTIVE SDD  : $SDD"
echo "LIVE TRACKER: $WORKLOG"
echo

if [ -f "$WORKLOG" ]; then
  echo "--- Current Phase ---"
  sed -n '/^## Current Phase/,/^## Phase 1 Live Tracker/p' "$WORKLOG" \
    | sed '$d' | grep -v '^## ' || true
  echo

  TRACKER="$(sed -n '/^## Phase 1 Live Tracker/,/^## Entry Template/p' "$WORKLOG")"

  echo "--- Red tests (SDD §9) status ---"
  # Count only numbered table rows so the legend line is never miscounted.
  ROWS="$(printf '%s\n' "$TRACKER" | grep -E '^\| [0-9]+ \|')" || ROWS=""
  total=$(printf '%s\n' "$ROWS" | grep -c .) || total=0
  ns=$(printf '%s\n' "$ROWS" | grep -c '| not-started |') || ns=0
  red=$(printf '%s\n' "$ROWS" | grep -c '| red |') || red=0
  green=$(printf '%s\n' "$ROWS" | grep -c '| green |') || green=0
  deferred=$(printf '%s\n' "$ROWS" | grep -c '| deferred |') || deferred=0
  echo "total=$total  not-started=$ns  red=$red  green=$green  deferred=$deferred"
  echo

  echo "--- Definition of Done (SDD §10) ---"
  dod_done=$(printf '%s\n' "$TRACKER" | grep -c '^- \[x\]') || dod_done=0
  dod_open=$(printf '%s\n' "$TRACKER" | grep -c '^- \[ \]') || dod_open=0
  echo "done=$dod_done  open=$dod_open"
  echo

  echo "--- Open Decisions ---"
  sed -n '/^### Open Decisions/,/^## Entry Template/p' "$WORKLOG" \
    | grep -v '^## Entry Template' || true
  echo
else
  echo "WARN: $WORKLOG not found — cannot surface live tracker."
  echo
fi

echo "--- Git ---"
git log --oneline -1 2>/dev/null || echo "(no git history)"
git status -s 2>/dev/null || true
echo "=== END LIVE CONTEXT ==="
