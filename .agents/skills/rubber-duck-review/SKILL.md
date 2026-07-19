---
name: rubber-duck-review
description: Run an independent fresh-context critique of a plan, architecture decision, test strategy, or high-stakes diff. Use when security, irreversibility, ambiguity, or design risk warrants a second model/configuration beyond ordinary two-axis code review.
---

# Rubber-duck review

1. Pin the artifact: name the plan, issue, commit, branch, or merge base under review.
2. Spawn the project `rubber_duck` custom agent in a fresh read-only context. Do not give it the originating agent's conclusions; give it the goal, authoritative sources, and raw artifact.
3. Ask it to reconstruct intent, then challenge assumptions, reversibility, security, failure modes, missing tests, and simpler competing designs.
4. Require falsifiable objections, concrete counterexamples, severities, and file references where applicable.
5. Keep its report separate from Standards and Spec reviews. Do not use majority voting to erase a dissenting risk.
6. Resolve or explicitly accept every material finding. Repeat only when changes were substantial.
7. Stop when both passes agree that remaining suggestions have diminishing return.

This is an escalation layer, not a replacement for deterministic checks, two-axis review, or human diff review.
