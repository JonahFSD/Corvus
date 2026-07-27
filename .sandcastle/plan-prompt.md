# ISSUES

Here are the open issues in the repo:

<issues-json>

!`node scripts/list-ready-frontier.mjs`

</issues-json>

The list above has already been deterministically filtered to open, unassigned,
correctly labelled issues whose declared `Blocked by:` references are all closed.
Missing, malformed, duplicate, unknown, or open blockers fail closed before this
planner runs.

# TASK

Analyze the frontier issues for additional implementation-order or merge-conflict
constraints that cannot be expressed by their declared product dependencies.

An issue B is **blocked by** issue A if:

- B requires code or infrastructure that A introduces
- B and A modify overlapping files or modules, making concurrent work likely to produce merge conflicts
- B's requirements depend on a decision or API shape that A will establish

An issue is **unblocked** if it passed the declared dependency filter and has no
additional overlap or implementation-order constraint with another frontier issue.

For each unblocked issue, assign a branch name using the exact format `sandcastle/issue-{id}` (no slug or other suffix). This must be deterministic so that re-planning the same issue always produces the same branch name and accumulated progress is preserved.

# OUTPUT

Output your plan as a JSON object wrapped in `<plan>` tags:

<plan>
{"issues": [{"id": "42", "title": "Fix auth bug", "branch": "sandcastle/issue-42"}]}
</plan>

Include only unblocked, unassigned issues labelled `ready-for-agent`. Never include `ready-for-human`, `needs-info`, `needs-triage`, or Wayfinder grilling/prototype work. If every issue is blocked, return an empty list rather than guessing around a dependency.

Always emit the `<plan>` tags, even when there is nothing to do. If there are no issues to work on at all, output `<plan>{"issues": []}</plan>` so the run can exit cleanly.
