# Domain language

This glossary defines the workflow language used in issues, specs, tests, reviews, and commits.

| Term                   | Meaning                                                                                                                           |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| Agentic engineering    | Human-directed software delivery in which Codex implements work inside explicit architectural, testing, review, and safety rails. |
| Grill                  | A one-question-at-a-time decision dialogue that reaches shared understanding before implementation.                               |
| Wayfinder map          | A parent GitHub issue that indexes decisions for work too uncertain or large for one session.                                     |
| Decision ticket        | A Wayfinder child issue that closes when its named decision is made.                                                              |
| Implementation ticket  | A ticket that closes when a decided behavior is implemented and verified.                                                         |
| Frontier               | Open, unblocked, unclaimed decision tickets that can be worked now.                                                               |
| Fog                    | In-scope uncertainty that cannot yet be expressed as a precise decision ticket.                                                   |
| Tracer bullet          | A small end-to-end vertical slice that produces observable behavior and immediate feedback.                                       |
| Seam                   | A stable public boundary where behavior can be tested or replaced without editing internals in place.                             |
| Deep module            | A small stable interface hiding a comparatively large implementation.                                                             |
| HITL                   | Human-in-the-loop work requiring live judgment, taste, or approval.                                                               |
| AFK                    | Away-from-keyboard work that is fully specified, bounded, tested, and safe to execute unattended.                                 |
| Deterministic check    | A pass/fail tool such as a test, typecheck, formatter, build, or policy check.                                                    |
| Automated review       | A fresh Codex agent judging a pinned diff against standards or a spec.                                                            |
| Human review           | A person reading the actual diff; reading an agent summary is not a human review.                                                 |
| Capture, don't dispose | Preserve a validated prototype on a disposable branch and link it from the deciding ticket while keeping it off the main branch.  |
| Expand-contract        | Introduce a new form beside the old, migrate callers in green batches, then remove the old form.                                  |

Add product-domain terms only when they become necessary during grilling. Prefer these defined terms over synonyms.
