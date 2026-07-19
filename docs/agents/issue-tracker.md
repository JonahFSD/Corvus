# Issue tracker: GitHub

Issues, specs, Wayfinder maps, and implementation tickets for this repository live in GitHub Issues. Use `gh` from inside the clone so it infers `JonahFSD/Corvus` from the remote.

## Core operations

- Create: `gh issue create --title "..." --body-file <file>`.
- Read: `gh issue view <number> --comments --json number,title,body,labels,assignees,state,comments`.
- List: `gh issue list --state open --json number,title,body,labels,assignees,state`.
- Claim first: `gh issue edit <number> --add-assignee @me`.
- Comment: `gh issue comment <number> --body-file <file>`.
- Label: `gh issue edit <number> --add-label <label>`.
- Close: `gh issue close <number> --comment "..."`.

Pull requests are not a triage request surface. They remain implementation and review artifacts.

## Publishing

When a skill says to publish a spec, map, or ticket, create a GitHub issue. Specs produced by `/to-spec` are immediately eligible for ticket slicing and do not enter external-request triage.

## Wayfinder

- The map is one parent issue labelled `wayfinder:map`.
- Decision tickets are sub-issues labelled `wayfinder:research`, `wayfinder:prototype`, `wayfinder:grilling`, or `wayfinder:task`.
- Use native issue dependencies for blocking edges. If the API is unavailable, place `Blocked by: #N` at the top of the child body.
- The frontier contains open, unblocked, unassigned children.
- A session claims a ticket by assignment before doing any work.
- Resolve by posting the answer, closing the child, and adding a one-line named pointer to the map.
- Refer to issues by title plus number, never by a wall of bare numbers.

## AFK eligibility

Only issues labelled `ready-for-agent` may be selected by unattended execution. `ready-for-human`, `needs-triage`, `needs-info`, and all Wayfinder HITL decisions are excluded.
