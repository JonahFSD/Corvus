# TASK — SPEC AXIS

Review branch `{{BRANCH}}` against issue {{TASK_ID}} and its parent spec, if any.

## Evidence

- Read the issue with `gh issue view {{TASK_ID}} --comments`.
- Read its linked parent spec and decision tickets.
- Inspect `git diff {{TARGET_BRANCH}}...{{BRANCH}}` and branch commits.

## Review

Check user stories, acceptance criteria, testing decisions, out-of-scope limits,
and every promised behavior. Identify omissions, contradictions, or unrequested
scope. Keep this report separate from the Standards axis.

If a clear spec defect can be corrected without a new human decision, fix it,
run `npm run check`, and commit the correction. Otherwise leave a precise report
for human judgment. Never close the issue or push.

Once complete, output <promise>COMPLETE</promise>.
