# Rubber-duck review: Vercel and Convex architecture

- Date: 2026-07-27
- Review type: independent architecture and risk critique
- Review axis: assumptions, reversibility, security, failure behavior, testability, and simpler alternatives
- Excluded axes: repository Standards review and originating-ticket Spec review

## Pinned artifact

The review covered the complete uncommitted architecture package as it existed during this session:

- `AGENTS.md`, `CONTEXT.md`, and `bible-ontology-spec.md`;
- ADRs 0003 through 0013, including the Vercel/Convex deployment and storage decisions;
- `docs/tradition-corpus-v1.md` and `docs/implementation-readiness.md`;
- the answer-package, provider, rights, Convex, and Vercel research reports;
- current package scripts, TypeScript configuration, tests, and GitHub workflow; and
- the current state of GitHub Issues #1, #8, and #9.

The artifact was reviewed twice by fresh-context, read-only rubber-duck agents. The second agent received the revised artifact rather than the first agent's conclusions.

## First pass

The first pass judged the package coherent enough for a fixture-only prototype but not ready for live Vercel, Convex, or provider implementation and not production-ready. Production rights remained an external blocker.

| Severity | Objection | Resolution |
| -------- | --------- | ---------- |
| Blocker | `fetch_only` did not require an immutable artifact identity, stable exact bytes, or a replay-window availability guarantee. | `docs/tradition-corpus-v1.md` and ADR 0012 now require a versioned locator, expected checksum verified on every fetch, exact-byte stability through the complete reference window, and `reference_only` demotion when those requirements cannot be met. |
| Blocker | Vercel-to-Convex trust was only an asserted design. | ADRs 0009 and 0013 plus `docs/implementation-readiness.md` now keep all live Convex work behind an isolated positive-and-negative trust spike. Until it passes, only the fixture store is approved. |
| High | Unscoped contested questions fanned out across every guaranteed family, threatening truthfulness, latency, cost, and payload bounds. | ADRs 0005 and 0010 now require a versioned benchmark-category plan selecting materially distinct positions, fail visibly on absent or oversized plans, and reserve family detail for explicit branches. The runtime envelope caps a package at six material positions. |
| High | Native narration could drift after deployment. | ADRs 0005 and 0013 plus Implementation readiness require post-deploy and daily semantic canaries, ordered canonical wording, alerts, degraded presentation rules, and a public-tool kill switch. |
| High | Shared OpenAI egress made ordinary per-IP rate limiting unsafe and ineffective as a user boundary. | ADR 0013 and Implementation readiness treat per-IP limits as observe-only, require a proved ChatGPT-origin gate before paid work, and retain global concurrency, provider quota, monetary cap, and capability kill-switch controls. |
| High | The architecture had no concrete scale envelope. | `docs/implementation-readiness.md` now pins data, query, request, provider-operation, concurrency, latency, payload, load, spend, retention, rollback, and recovery limits. |
| Medium | `npm run check` covered workflow scaffolding, not product contracts. | Implementation readiness states that limitation explicitly and requires contract, storage, provider, MCP, component, security, and deployed suites. Every non-live suite must join `npm run check` during the first implementation slice. |

The first pass also suggested deferring vector discovery, reconciling Issue #9's process state, and turning blockers into implementation tickets. Vector discovery is now optional for the first slice. Issue and ticket mutation was not performed because the review did not authorize external tracker writes.

## Second pass

The revised package still had four material findings. The reviewer concluded that another rubber-duck pass would have diminishing returns after they were resolved or explicitly accepted.

| Severity | Objection | Resolution |
| -------- | --------- | ---------- |
| High | The required benchmark-category artifact does not exist while Issue #8 remains open, so unscoped contested planning was not actually development-ready. | The phase boundary now limits immediate implementation to package schema/core policy with explicitly scoped or factually undisputed fixtures. Unscoped contested questions implement only a typed missing-plan failure until Issue #8 supplies an accepted versioned benchmark. The implementation sequence and ADR 0005 say the same. |
| High | A public `noauth` endpoint with global caps could let one direct caller degrade service for everyone. | Login-free operation is preserved, but paid capabilities remain disabled until a Developer Mode spike proves a ChatGPT-origin gate using a managed client certificate or published OpenAI egress enforcement on Vercel. The test must reject direct non-OpenAI callers before provider work and cover spoofing, rotation, previews, and fail-closed behavior. If neither mechanism works, provider spend remains zero; user OAuth would require a separate product decision. |
| High | Citation, Replay, release-retention, artifact-availability, and signing-key lifetimes were unspecified. | A Citation reference is valid for seven days; a Replay reference is valid for 24 hours; server clock skew is limited to five minutes. Retirement stops issuance, and the release, Corpus data, required exact bytes, replay contracts, and verification keys remain available for at least seven days plus skew. Rights compilation and pruning enforce these windows. |
| Medium | Treating any narration drift as a full outage had no reversible degraded mode. | The architecture now defines a tested narration-safe mode: model-visible output is non-substantive and the clearly labeled component renders the unchanged canonical package from component-only hydration. If the host improvises, suppresses, or misrenders it, the public-tool kill switch still fails closed. |

## Resulting readiness decision

The package is ready to begin only the narrowed fixture schema/core-policy slice. It is not yet ready for complete unscoped contested-question planning, live Convex access, paid live providers, or production.

The gates are cumulative:

1. Issue #8 must produce the accepted versioned benchmark before unscoped contested planning begins.
2. The Vercel-to-Convex trust spike must pass before the live Convex adapter begins.
3. A login-free ChatGPT-origin gate must pass before any paid provider capability or nonzero production spend is enabled.
4. Exact-artifact rights coverage must pass for every guaranteed family and mandatory benchmark position before production.
5. The product test suites, deployed narration checks, load envelope, rollback, and restore drills must pass before submission.

The current `npm run check` passing state proves only the existing workflow control plane and Sandcastle surface. It is not product-readiness evidence until the first slice adds the required non-live suites.

## Remaining accepted risks and open work

- Rights acquisition is an external, release-blocking program of work, not an engineering fallback.
- Issue #8 is an architectural input, not implementation detail; the first slice must not fabricate its category plans.
- Vercel support for the intended login-free caller gate and Vercel-to-Convex identity remain falsifiable spikes. Failure keeps the affected live capability disabled.
- Convex vector discovery remains optional until deterministic traversal and Gloo retrieval establish a need.
- Issue #9 remained open with human-review workflow labels at review time. This report does not change tracker state.

No third independent pass was run because the second reviewer explicitly judged further review to have diminishing returns after these four findings were addressed. Standards and Spec reviews remain separate required checks for a future implementation diff.
