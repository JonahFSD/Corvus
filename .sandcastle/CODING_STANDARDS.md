# Coding standards

The authoritative review baseline is `docs/standards/review.md` plus applicable
`AGENTS.md`, `CONTEXT.md`, and ADR files.

- Implement one tracer-bullet behavior at a time.
- Observe a relevant test fail before implementation and pass afterward.
- Test through stable public seams rather than implementation details.
- Prefer deep modules, locality, and explicit interfaces.
- Preserve the ticket's out-of-scope boundary.
- Run `npm run check` before completion.
- Never publish, force-push, or merge to a protected remote branch autonomously.
