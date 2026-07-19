#!/usr/bin/env bash
set -euo pipefail

base="${1:-main}"
issue="${2:-unspecified}"
run_dir=".agent-runs/reviews/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$run_dir"

codex review --base "$base" \
  "Review only the pinned diff against docs/standards/review.md, applicable AGENTS.md, CONTEXT.md, and ADRs. Report actionable Standards-axis findings with evidence. Do not merge with spec findings." \
  > "$run_dir/standards.md"

codex review --base "$base" \
  "Review only the pinned diff against originating GitHub issue $issue, its parent spec, user stories, acceptance criteria, testing decisions, and out-of-scope boundary. Report the Spec axis separately." \
  > "$run_dir/spec.md"

printf 'Standards review: %s\nSpec review: %s\n' \
  "$run_dir/standards.md" "$run_dir/spec.md"
