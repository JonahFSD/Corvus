---
name: workflow-retrospective
description: Review completed Codex sessions, issue history, commits, review findings, and rework to improve the agentic engineering system. Use for standups, recurring-prompt detection, intent-mismatch analysis, workflow tips, and periodic continuous improvement.
---

# Workflow retrospective

1. Select a bounded period or delivered feature. Read raw evidence first: issue comments, commits, review reports, CI failures, handoffs, and available session summaries.
2. Separate product defects from process defects. Identify repeated prompts, repeated review comments, unnecessary exploration, stale context, missing seams, and decisions that arrived too late.
3. Rank improvements by recurrence and leverage.
4. Route each accepted improvement to the smallest durable surface:
   - Deterministic failure → test, typecheck, formatter, hook, or CI.
   - Repeated repository convention → nearest `AGENTS.md`.
   - Reusable procedure → project skill.
   - Domain-language gap → `CONTEXT.md`.
   - Hard irreversible decision → ADR.
   - Architecture friction → `improve-codebase-architecture`.
5. Apply the deletion test before adding instructions: if the sentence would not change agent behavior, omit it.
6. Report what changed, supporting evidence, and how the next run can verify improvement.

Do not auto-generate broad standing instructions from the codebase. Mine actual human corrections and observed failures.
