# Codex-native agentic engineering runbook

This repository implements the complete workflow as:

```text
Grill → Research → Prototype → Spec → Tickets → Implement → Review
```

## Start a session

Trust the repository so Codex loads `.codex/config.toml`, project skills, hooks,
rules, and custom agents. Review and trust the project hooks with `/hooks`.

Use a fresh context for each implementation ticket. Prefer clearing over
compaction. Use a handoff only when hard-won context must cross sessions.

## Choose the front door

- Small, clear effort: invoke `grill-with-docs` and resolve one decision at a time.
- Large or foggy effort: invoke `wayfinder`; chart decision tickets and work one per session.
- Unknown fact: delegate the `research` skill to the read-only researcher.
- Uncertain feel or state model: use `prototype`, then capture the validated artifact on a disposable branch.

Keep Grill → Spec → Tickets in one context when possible. Then clear and use a
fresh `/implement` session per ticket.

## Specification and tickets

A spec contains Problem, Solution, user stories, implementation/module
decisions, testing seams, and explicit Out of Scope. Avoid volatile file paths.
Remove the active spec after delivery; Git and the closed issue preserve history.

Tickets are GitHub Issues with native dependencies. Prefer many thin AFK tracer
bullets over horizontal layers. Wide mechanical changes use expand-contract.
Every spec backlog ends with a HITL QA issue blocked by all implementation work.

## Implementation

Invoke the `implement` skill for one issue. Work red-green through a confirmed
public seam, one vertical slice at a time. Run focused checks while working and
`npm run check` once at completion. Structural refactoring belongs in the fresh
review phase unless required to keep the suite green.

## Review

Every ticket receives two independent reports:

- Standards axis: repository guidance plus the review baseline.
- Spec axis: originating issue/spec and acceptance behavior.

Run `npm run review -- main <issue-number>` for a local pinned review. For
high-stakes changes, delegate to `rubber_duck` in a fresh context. A human then
reads the actual diff before merge.

## AFK execution

Native bounded execution:

```bash
npm run afk -- --max-iterations 1 --timeout-seconds 1800
```

This claims only unassigned `ready-for-agent` issues, creates a dedicated
worktree/branch, launches one ephemeral `codex exec` process, forbids publishing,
and leaves the candidate for human diff review. The iteration limit is capped at
20 and defaults to one.

Sandcastle factory:

```bash
npm run sandbox:auth
npm run sandcastle
```

Sandcastle plans an AFK frontier, runs at most two issue branches concurrently,
implements, performs separate Standards and Spec reviews, and stops for human
diff review. Set `SANDCASTLE_RUBBER_DUCK=1` for the independent high-effort pass.
Only after reviewing every branch should a human explicitly opt into local merge
with `SANDCASTLE_AUTO_MERGE=1`. It never pushes.

## Safety

- Interactive default: workspace-write sandbox with on-request approvals.
- AFK default: workspace-write sandbox, no approvals, no network, fresh process.
- Sandcastle: Docker, non-root agent, pinned Codex CLI, bounded cycles/parallelism.
- Project rules forbid push, hard reset, git clean, recursive forced deletion,
  and repository deletion.
- Secrets and run logs are ignored. Never commit auth files or `.env` values.

## Maintenance

- Every run: one issue per fresh context and complete checks before handoff.
- Every few active-development days: run `improve-codebase-architecture` where change is landing.
- Every few weeks: audit skills, research, ADRs, glossary, active specs, and memory for staleness.
- Continuously: turn repeated review feedback into reviewer standards or a narrow skill.
