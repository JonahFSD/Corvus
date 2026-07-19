# Review standards

These standards belong to the fresh Standards reviewer. Do not preload them into every implementation session unless the ticket directly requires one.

Review in this order:

1. Correctness, data loss, security, authorization, and concurrency.
2. Faithfulness to documented repository conventions and ADRs.
3. Public behavior and missing tests at stable seams.
4. Fowler-style smells as judgment calls: duplicated logic, long functions, divergent change, shotgun surgery, feature envy, primitive obsession, speculative generality, and inappropriate intimacy.
5. Deep-module quality: narrow stable interfaces, hidden implementation detail, locality, and tests that survive internal refactors.

Report only actionable findings with evidence and file references. A documented repository decision overrides a generic smell heuristic.
