# Two-axis pull request review

Review the pinned pull-request diff in a fresh context. Delegate two independent
read-only subagents in parallel and wait for both:

1. **Standards axis** — read applicable `AGENTS.md`, `CONTEXT.md`, ADRs, and
   `docs/standards/review.md`. Review correctness, security, tests, documented
   conventions, code smells, seams, locality, and deep-module quality.
2. **Spec axis** — locate the originating issue/spec from the PR and commit
   messages. Review user stories, acceptance criteria, testing decisions, and
   out-of-scope limits.

Report the two results separately. Never merge or rerank them. Include only
actionable findings with severity, evidence, and file references. If either
axis cannot locate its authoritative sources, say so rather than guessing.
