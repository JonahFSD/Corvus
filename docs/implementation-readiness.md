# Implementation readiness and runtime envelope

This document turns the accepted architecture into falsifiable entry and release gates. Its numbers are the initial supported envelope, not capacity claims. A mandatory benchmark that exceeds an envelope value reopens the affected design; implementation may not truncate evidence, silently omit a Position, or raise a platform limit merely to make the test green.

## Phase boundary

| Phase                       | Work permitted                                                                                                            | Entry gate                                                                                          |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| Fixture schema/core policy  | Package schemas, pure policy, scoped and factual fixtures, in-memory storage, MCP harness, and Evidence component         | May begin from the accepted docs                                                                    |
| Unscoped contested planning | Benchmark-category classifier, material-position plans, Topic-pack obligations, and contested-question fixtures           | Issue #8 is accepted and its minimal versioned deterministic benchmark artifact is checked in       |
| Vercel transport spike      | Fixture-backed `/mcp`, versioned component resource, cancellation, streaming, caller-gate proof, and Developer Mode tests | Fixture contracts pass; unscoped contested fixtures remain excluded until the preceding gate passes |
| Live Convex adapter         | Schema, read store, publication, traversal, vector quarantine, backup, and restore                                        | Vercel-to-Convex trust spike passes every positive and negative case below                          |
| Live provider adapters      | Staging-only YouVersion and Gloo calls behind fixture-tested contracts                                                    | Provider contract, rights, log-redaction, caller-gate, and spend-limit tests pass                   |
| Production candidate        | Full deployed composition                                                                                                 | Rights coverage, benchmark, narration, security, recovery, and submission gates all pass            |

The current repository is ready only for the fixture schema/core-policy slice. Its first successful fixture asks, “According to Matthew 22:37–40, which commandments does Jesus call greatest?” and uses reviewed public-domain World English Bible US fixture text with exact locators for Matthew 22:37–38 and Matthew 22:39–40. The slice may also test the missing-plan failure for an unscoped contested question but may not invent a category plan. “Do Christians believe baptism saves?” and equivalent unscoped contested questions are out of scope until Issue #8 supplies the accepted, versioned plan. The current `npm run check` validates the workflow control plane, formatting, the existing Sandcastle TypeScript surface, and GitHub helper tests; it does not yet validate product code. The first implementation slice must expand the TypeScript include paths and test commands before any live-stack ticket can close.

Two program blockers remain as of 2026-07-27. Issue #8 has not yet supplied the deterministic benchmark required for complete unscoped contested-question planning. Production also lacks runtime-admissible rights coverage for the guaranteed tradition families described in ADR 0012. Neither blocker prevents the narrowed fixture schema/core-policy slice, but both prevent claiming the complete question architecture is development-ready.

## Live trust spike

No live Convex adapter is approved until an isolated Vercel Function proves all of the following against an isolated Convex deployment:

1. Function-time acquisition of the short-lived Vercel team-issuer OIDC token.
2. Exchange to the exact environment-specific Convex read audience.
3. Convex `customJwt.applicationID`, issuer, JWKS, signature, lifetime, and exact Vercel project/environment subject validation.
4. Acceptance of the intended production-shaped caller.
5. Rejection of an untrusted issuer, wrong audience, wrong project, wrong environment, expired token, not-yet-valid token, missing token, and tampered token.
6. Refresh or reacquisition behavior across token expiry and warm Fluid Compute reuse.
7. No token, claim set, authorization header, or Convex credential in logs, errors, tool results, component data, or telemetry.
8. Fixture-only local composition that does not weaken the deployed authorization path.

Failure keeps production code on the fixture store. It does not authorize a shared long-lived runtime credential, public anonymous Convex reads, or another database.

## Initial data envelope

One published release supports at most:

| Record class                         | Maximum |
| ------------------------------------ | ------: |
| Ontology entities                    |  60,000 |
| Structural relations                 | 750,000 |
| Interpretive assertions              | 100,000 |
| Discovery candidates                 | 250,000 |
| Rights-permitted embeddings          |  75,000 |
| Corpus source and membership records |  20,000 |
| Embedding dimensions                 |   1,536 |

The release benchmark measures actual document and index sizes, stage/validation duration, query usage, and cost in the local Convex backend and an isolated hosted deployment. A release outside this envelope needs a new benchmarked envelope or a superseding storage decision before ingestion.

## Per-investigation envelope

| Dimension                                |                             Hard limit |
| ---------------------------------------- | -------------------------------------: |
| UTF-8 question body                      | 16 KiB and 8,000 Unicode scalar values |
| Citation reference                       |                                  4 KiB |
| Replay reference                         |                                 32 KiB |
| Materially distinct Position memberships |                                      6 |
| Provider operations                      |                                     16 |
| Concurrent provider operations           |                                      3 |
| Scripture locators hydrated              |                                     12 |
| Retrieval candidates per Position        |                                     24 |
| Admitted Citations per Position          |                                      8 |
| Citations in one package                 |                                     48 |
| Answer statements in one package         |                                     64 |
| Material-operation receipts              |                                     48 |
| Model-visible package data               |            approximately 16,000 tokens |
| MCP `content`                            |                      32 KiB serialized |
| MCP `structuredContent`                  |                     256 KiB serialized |
| Component `_meta` hydration              |                     512 KiB serialized |
| Complete HTTP response                   |                     768 KiB serialized |

A validated benchmark-category plan may require fewer memberships than the guaranteed family count because it represents materially distinct positions rather than nominal labels. If a mandatory category needs more than six material positions, the release fails until the plan is split into a truthful initial comparison plus explicit user-expandable branches or this envelope is re-benchmarked. Runtime never drops the excess positions silently.

Set Vercel `maxDuration` to 60 seconds. The application deadline is 45 seconds, reserving the final five seconds for cancellation, deterministic validation, and a degraded or abstaining package. Target p95 end-to-end latency is 30 seconds or less in the five-concurrent-request profile. Individual network attempts use a two-second connect budget; no individual retrieval attempt exceeds ten seconds and no analysis attempt exceeds twenty seconds. Retries remain inside the request-wide provider-operation and deadline budgets.

## Convex query envelope

Each traversal is one release-pinned query with these hard bounds:

| Dimension                       | Hard limit |
| ------------------------------- | ---------: |
| Depth                           |          2 |
| Frontier width                  |         64 |
| Visited entities                |        256 |
| Relations read                  |      1,024 |
| Returned entities and relations |        256 |
| Function user code              |     500 ms |
| Data read                       |      8 MiB |
| Documents scanned               |     16,000 |
| Index ranges                    |      2,000 |
| Vector candidates               |         64 |

Budget exhaustion returns a typed reason and affects only its dependent Answer obligations. The benchmark fails if a mandatory successful fixture exhausts a budget. Vector discovery is optional: deterministic traversal and admitted Gloo retrieval must remain capable of completing the first vertical slice with Convex embeddings disabled.

## Load, abuse, and spend profiles

Run all three deployment profiles:

1. one cold and ten warm sequential investigations;
2. five concurrent investigations sustained for five minutes, meeting the 30-second p95 target without policy or provenance failures; and
3. a twenty-request burst that either remains inside budgets or sheds excess work within two seconds before starting provider calls.

The MCP tools remain login-free and declare `noauth`, but fixture-only transport keeps every paid provider capability disabled. Enabling a paid provider requires an end-to-end caller-gate spike in ChatGPT Developer Mode using a verified OpenAI-managed client certificate or published OpenAI egress enforcement at Vercel. Expected ChatGPT calls must pass, while a direct internet caller outside the proved origin boundary must be rejected before any provider call. Certificate rotation, egress-range updates, forwarded-header spoofing, preview bypass, and fail-closed behavior must be tested. Network metadata used for this gate is not copied into Answer packages, provider calls, question logs, belief profiles, or product analytics.

Assume legitimate ChatGPT traffic may share OpenAI egress addresses. Ordinary per-IP rate limits begin in observe-only mode and cannot serve as user identity or a fairness boundary. The origin allowlist, if selected, is a binary ChatGPT-origin gate over the complete published range rather than a per-address quota. Enforcing it requires a Developer Mode capture proving normal ChatGPT traffic is preserved and direct non-OpenAI traffic is rejected. Inside that boundary, rely on request validation, global concurrency, capability kill switches, provider quotas, and spend caps. If neither managed client-certificate verification nor safe OpenAI-origin enforcement works on Vercel, production stays fixture/read-only with provider spend fixed at zero; accepting service-wide paid-call denial of service is not an approved release alternative. Introducing user OAuth would require an explicit product decision because it would violate the current login-free Challenge contract.

Production provider spend defaults to zero. Enabling production requires an explicit nonzero daily monetary cap in the release profile and matching provider-side quota where available. Exhaustion disables the expensive capability and returns a retryable/degraded result without widening evidence or falling back to model memory. No IP, cookie, fingerprint, question, or belief history is introduced for rate limiting.

## Reference and release lifetime

All reference times use server UTC and allow at most five minutes of clock skew. A `CitationReference` is valid for exactly seven days from issuance and is rejected if its encoded expiry is more than seven days plus skew after issuance. A `ReplayReference` is valid for exactly 24 hours and is rejected if its encoded expiry is more than 24 hours plus skew after issuance. The UI displays the expiry and does not render a branch control after local expiry; the server remains authoritative.

The active release may issue references continuously. Once a release is retired, no new reference may name it, and the release, Corpus snapshot, locator metadata, replay contracts, verification keys, and rights-permitted exact bytes required by its outstanding references remain available for at least seven days plus five minutes after retirement. Pruning is forbidden before that interval ends and before the post-release export and restore checks pass. Signing-key rotation retains every verification key for at least seven days plus five minutes after its last possible issuance; compromise may revoke a key immediately, in which case affected references fail closed with an explicit reason.

The rights compiler rejects an `included` or `fetch_only` evidence class whose permission, artifact hosting, deletion terms, or immutable-byte guarantee cannot cover the applicable maximum lifetime. A branch revalidates current denylist and rights policy; revocation may therefore invalidate an otherwise unexpired reference, but never silently substitutes different evidence.

## Narration canary

The package contains ordered canonical wording for every substantive statement. Synthetic Developer Mode canaries run after every deployment and at least once every 24 hours while the public tool is enabled. They compare:

- the exact substantive proposition set;
- statement boundaries and Position ownership;
- inline Citation bindings;
- qualifiers and Evidence gaps;
- Answer outcome; and
- required Pastoral handoff.

Any missing, added, broadened, or misbound substantive proposition disables ordinary native narration and alerts the maintainer. The tool may remain available only in an explicit narration-safe mode that returns non-substantive model-visible status text and presents the unchanged canonical package through the clearly labeled Evidence component using component-only hydration. In safe mode the model receives no package prose from which it could improvise an answer, and Source-inspection and Analysis-branch results use the same presentation constraint. A Developer Mode test must prove those properties. If the host narrates substantive claims anyway, suppresses the component, or prevents faithful component rendering, the public-tool kill switch activates. Restoring ordinary mode requires a passing canary and either rollback to the last known-good integration or an accepted response-shaping change.

## Recovery objectives

| Objective                          | Requirement                                                                                 |
| ---------------------------------- | ------------------------------------------------------------------------------------------- |
| Published-release RPO              | Zero after canonical artifacts, digests, and the post-release export are durably stored     |
| Application rollback               | Routing and smoke verification within 15 minutes                                            |
| Convex release rollback            | Active-pin change and read-contract verification within 15 minutes                          |
| Full data restore RTO              | Four hours into an isolated deployment, including digest and singleton-pointer verification |
| Content-free application telemetry | Maximum 30-day retention                                                                    |

If a platform's immutable minimum retention exceeds the product limit, record the exact fields and period, prevent content from entering those fields, and block any optional drain or export with a longer uncontrolled lifetime.

## Required test commands

The first fixture implementation adds these independently runnable suites and makes every non-live suite part of `npm run check`:

- `test:contracts`: package schema, obligation, evidence, replay, rights, and budget invariants;
- `test:storage`: fixture/Convex read-store contract, publication failure injection, traversal, vector quarantine, rollback, export, and restore;
- `test:providers`: fixture and staging contract tests for YouVersion and Gloo, including failures and redaction;
- `test:mcp`: initialization, versioned schemas, annotations, malformed inputs, cancellation, and payload limits; the first fixture proves `theological_investigation`, while the contract-complete three-tool gate later requires discovery and successful fixture behavior for exactly all three approved tools;
- `test:component`: CSP, versioned resources, complete rendering, hostile strings, and responsive layouts;
- `test:security`: OIDC negative cases, reference lifetime/tampering/key rotation, URL safety, log allowlist, preview isolation, and secret absence; and
- `test:deployed`: MCP Inspector, Developer Mode fidelity, narration-safe mode and canary, ChatGPT-origin/direct-caller isolation, WAF/shared-egress behavior, load, rollback, and recovery.

`test:deployed` belongs to the production-candidate gate rather than ordinary offline checks. A green current workflow suite must never be reported as proof that these product contracts pass before the suites exist.

During the first fixture slice, every non-live command contains non-placeholder assertions for the seams then available: canonical contracts and pure policy, the in-memory read-store contract, fixture-provider behavior, the local investigation transport, minimal component hydration, and content, URL, and log safety. Later tickets extend those same suites. The first slice does not fake live Convex, provider, OIDC, reference-signing, deployment, backup, or restore behavior merely to populate a command.

## Remaining external blocker

Fixture implementation and the trust spike can proceed without restricted source text. Production cannot. ADR 0012's rights compiler must report complete runtime-admissible coverage for every guaranteed family and mandatory benchmark Position. Mutable or merely public `fetch_only` pages do not count; only included artifacts or immutable, checksummed, permissioned fetch-only artifacts with availability through the complete inspection/replay window qualify.
