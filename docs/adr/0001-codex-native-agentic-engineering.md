# ADR-0001: Use a Codex-native agentic engineering control plane

- Status: accepted
- Date: 2026-07-18

## Context

The repository needs a holistic implementation of the seven-phase Agentic Engineering workflow: Grill, Research, Prototype, Spec, Tickets, Implement, and Review. The source guide describes GitHub Copilot CLI, but this repository is operated with Codex.

## Decision

Use Codex-native primitives while preserving the workflow's behavioral contracts:

- `AGENTS.md` for the small standing brief.
- Project skills under `.agents/skills/` for progressive disclosure.
- Project settings, exec policies, hooks, and custom agents under `.codex/`.
- GitHub Issues for specs, decision maps, dependencies, and implementation tickets.
- `codex exec --ephemeral` for one-task-per-fresh-session AFK execution.
- Codex sandboxing plus Docker/Sandcastle for unattended isolation.
- Separate Standards and Spec review agents, followed by human diff review.

Because Codex uses OpenAI models, the guide's cross-family rubber-duck review becomes a deliberately separate model/configuration and fresh context rather than a non-OpenAI model family.

## Consequences

The workflow is reproducible from the repository and does not depend on personal prompts. Project-local Codex configuration activates only after the repository is trusted. Hooks must be reviewed and trusted by each developer. Stale specs, maps, research, and glossary entries require active lifecycle management.
