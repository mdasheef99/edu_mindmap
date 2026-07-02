#!/usr/bin/env bash
# Surfaces the live Mindmap milestone state at session start so the agent grounds itself in
# the current SDD/worklog rather than stale memory. Read-only; never mutates the repo.
set -euo pipefail

WORKLOG="docs/planning/worklog-v9.md"
SDD="docs/planning/sdd/phase-3-m4-curriculum-auth-sdd.md"
CANON=".augment/rules/00-canon.md"

echo "=== MINDMAP - LIVE M4 CONTEXT (auto-surfaced at session start) ==="
echo
echo "ACTIVE MILESTONE: Phase 3 - M4 Curriculum entry + Supabase Auth"
echo "ACTIVE SDD      : $SDD"
echo "LIVE TRACKER    : $WORKLOG"
echo "CANON           : $CANON"
echo

if [ -f "$WORKLOG" ]; then
  echo "--- Worklog v9 summary ---"
  sed -n '1,45p' "$WORKLOG"
  echo
else
  echo "WARN: $WORKLOG not found - cannot surface live tracker."
  echo
fi

echo "--- Git ---"
git log --oneline -1 2>/dev/null || echo "(no git history)"
git status -s 2>/dev/null || true
echo "=== END LIVE CONTEXT ==="
