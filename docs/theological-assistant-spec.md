# Theological assistant product specification

## Problem Statement

People asking difficult theological questions in ChatGPT need more than a fluent answer. They need to know which claims come from Scripture, which claims describe a named Christian tradition, where materially different traditions disagree, which exact sources support each statement, and where the available evidence is insufficient. A generic model answer can silently select a tradition, collapse disagreement, invent provenance, overstate uncertain evidence, or quote material Corvus has no right to process or deliver.

The current repository has a comprehensive set of architectural decisions, research, domain language, security constraints, and operational gates, but it does not yet have the Product runtime that turns those decisions into an invokable ChatGPT app. The implementation must preserve the evidence contract end to end while using the owner's actual stack: Vercel for the public Apps SDK/MCP runtime and message-scoped Evidence component, and Convex as the sole application database and vector facility. It must remain testable without live credentials, stateless with respect to conversations, safe under provider and host failure, honest about incomplete evidence, and releasable only after the benchmark, rights, trust, abuse, narration, and recovery gates pass.

## Solution

Build the Theological assistant as a strict TypeScript, ESM, npm-managed ChatGPT app backed by one cohesive Investigation module and deployed as a Vercel Node.js Function. Expose exactly three read-only MCP operations: Theological investigation, Source inspection, and Analysis branch. Keep ontology access, Corpus policy, YouVersion retrieval, Gloo retrieval and analysis, validation, credentials, and provider failure handling behind that seam.

The primary operation accepts only the user's question as written and returns a citation-complete Answer evidence package. The package owns the canonical substantive answer, Analysis scope, Answer obligations and outcome, Position memberships, Evidence gaps, Citations, Operation receipts, semantic structure, and Evidence graph relationships. ChatGPT provides the ordinary conversational narration, while a message-scoped Evidence component renders the auditable source and dependency surface. Deterministic policy validates the package before delivery and requires Evidentiary abstention when required evidence is unavailable.

Build through gated vertical slices. Begin with shared contracts, pure evidence policy, deterministic fixtures, an in-memory store, the three-tool MCP harness, and an explicitly scoped or factually undisputed fixture path. Do not implement supported unscoped contested-question planning until the accepted versioned benchmark exists. Prove Vercel-to-Convex identity before implementing the live Convex adapter. Keep paid providers disabled until a login-free ChatGPT-origin caller gate is proven. Keep production blocked until runtime-admissible source rights, deployed narration fidelity, load, security, rollback, restore, and submission gates all pass.

## User Stories

1. As a ChatGPT user, I want to ask a theological question in ordinary language, so that I do not need to understand providers, ontology queries, or evidence schemas.
2. As a ChatGPT user, I want Corvus to preserve the question as written, so that hidden normalization does not change what I asked.
3. As a ChatGPT user, I want any explicit tradition, Canonical collection, translation, historical period, or other Analysis scope in my question to be applied visibly, so that the answer does not conceal its lens.
4. As a ChatGPT user, I want unresolved scope terms to remain visible, so that Corvus does not guess my meaning.
5. As a ChatGPT user, I want no tradition-bearing default or inferred belief profile, so that the assistant does not silently choose a theology for me.
6. As a ChatGPT user, I want a direct, readable answer when a question is scoped or factually undisputed, so that evidence rigor does not make simple answers unusable.
7. As a ChatGPT user, I want shared textual ground presented before competing positions on a contested question, so that disagreement is understandable rather than adversarial.
8. As a ChatGPT user, I want materially distinct Christian positions labeled and scoped, so that nominal family labels do not hide real differences or create fake ones.
9. As a ChatGPT user, I want Corvus to disclose when no validated benchmark-category plan applies, so that it never improvises which traditions count as representative.
10. As a ChatGPT user, I want every substantive scriptural or theological statement bound to evidence or explicit derivation, so that I can distinguish sourced claims from synthesis.
11. As a ChatGPT user, I want inherited evidence for a synthesis labeled differently from direct support, so that a citation is not presented as proving more than it does.
12. As a ChatGPT user, I want the exact Scripture display edition, locator, attribution, and safe target shown for a passage, so that I know which text I am reading.
13. As a ChatGPT user, I want tradition claims tied to exact editions, recognizing bodies, authority scope, and Corpus membership, so that one source does not silently speak for an entire family.
14. As a ChatGPT user, I want missing, partial, unavailable, stale, malformed, or rights-blocked evidence reported as scoped Evidence gaps, so that limitations are attached to the claims they affect.
15. As a ChatGPT user, I want an Answer outcome of Answered, Partially answered, or Abstained derived from required obligations, so that confidence is categorical and auditable rather than a vague number.
16. As a ChatGPT user, I want the assistant to abstain from unsupported propositions rather than fill gaps from model memory, so that fluency cannot bypass evidence policy.
17. As a ChatGPT user, I want a Pastoral handoff when a question requires personal spiritual, sacramental, or ecclesial judgment, so that the app does not impersonate an ongoing pastoral relationship.
18. As a ChatGPT user, I want pastoral language separated from substantive theological claims, so that pastoral care does not evade citation requirements.
19. As a ChatGPT user, I want tappable inline Citation markers and a compact Sources view, so that I can inspect support without leaving the conversation unnecessarily.
20. As a ChatGPT user, I want an on-demand Evidence graph derived from the actual package relationships, so that I can see how Material operations and Citations contributed to the presented answer.
21. As a ChatGPT user, I want the Evidence graph to omit private chain-of-thought and unused exploration, so that auditability does not expose hidden reasoning or irrelevant noise.
22. As a ChatGPT user, I want to inspect a Citation through a bounded package-issued reference, so that source inspection cannot become arbitrary URL fetching.
23. As a ChatGPT user, I want a Citation reference to remain usable for seven days, so that I can revisit evidence after the initial response.
24. As a ChatGPT user, I want to branch a replayable Analysis step by changing an explicit input, so that I can compare another tradition, Canonical collection, translation, or search scope without overwriting the original answer.
25. As a ChatGPT user, I want a branch to preserve its immutable parent and record the Scope delta, so that the comparison remains auditable.
26. As a ChatGPT user, I want branch controls only where a replayable receipt chain exists, so that the UI never promises an operation the server cannot reproduce.
27. As a ChatGPT user, I want a Replay reference to remain usable for 24 hours and display its expiry, so that branching is predictable without creating durable conversation state.
28. As a ChatGPT user, I want expired, tampered, oversized, revoked, or no-longer-admissible references to fail explicitly, so that Corvus does not substitute different evidence silently.
29. As a ChatGPT user, I want provider timeouts and empty results to yield a truthful degraded or abstaining package when possible, so that one dependency failure does not manufacture an answer or crash the whole experience.
30. As a ChatGPT user, I want the app to remain login-free, so that I do not need a Corvus, YouVersion, or Gloo account to ask a question.
31. As a source owner, I want Corvus to use only runtime-admissible exact artifacts for first-class evidence, so that public readability is not mistaken for permission.
32. As a source owner, I want storage, transformation, model input, excerpt delivery, linking, caching, and embeddings authorized separately, so that a broad product assumption does not override specific rights.
33. As a source owner, I want revocation to stop new use immediately and remove affected material through a new immutable release, so that historical provenance and current restrictions are both preserved.
34. As a maintainer, I want deterministic synthetic fixtures and reviewed public-domain artifacts, so that ordinary development and CI require no live provider or restricted corpus credentials.
35. As a maintainer, I want one deep Investigation module rather than a provider workflow exposed to ChatGPT, so that orchestration and evidence policy remain coherent and testable.
36. As a maintainer, I want exactly three public read-only MCP tools and no public provider, ontology-administration, publication, or arbitrary-fetch surface, so that the attack surface stays bounded.
37. As a maintainer, I want live and fixture adapters only at real external seams, so that tests can replace external behavior without creating a generic framework.
38. As a maintainer, I want immutable Ontology releases and Corpus snapshots with exact pins and digests in every package, so that answers can be attributed, replayed, rolled back, and compared.
39. As a maintainer, I want publication to stage, seal, validate, and atomically activate a release, so that a partially loaded or invalid graph is never visible to runtime reads.
40. As a maintainer, I want bounded indexed Convex traversal and quarantined vector Discovery candidates, so that retrieval remains predictable and algorithmic similarity never becomes theological evidence.
41. As a maintainer, I want Gloo retrieval separated from schema-constrained analysis, so that provider search, model generation, source authority, and evidence admission remain distinct.
42. As a maintainer, I want YouVersion text hydrated only after bounded locator selection and never durably retained, so that Scripture delivery honors provider and privacy constraints.
43. As a maintainer, I want Vercel production, staging, preview, and local compositions isolated, so that previews cannot receive production Corpus data, signing material, or provider credentials.
44. As a maintainer, I want Vercel-to-Convex calls authenticated with short-lived environment-specific identity, so that runtime reads do not depend on a standing deploy key.
45. As a maintainer, I want paid providers disabled until a real ChatGPT-origin gate is proven, so that an arbitrary direct caller cannot consume service-wide provider spend.
46. As a maintainer, I want global concurrency, operation budgets, provider quotas, spend caps, circuit breakers, and capability kill switches, so that overload fails before expensive work and remains reversible.
47. As a maintainer, I want content-free Operational telemetry with bounded retention, so that I can operate the service without recording questions, answers, beliefs, evidence text, IP addresses, or credentials.
48. As a maintainer, I want native-narration canaries after deployment and daily, so that a ChatGPT host change cannot silently distort the canonical package.
49. As a maintainer, I want a tested narration-safe mode, so that the component can present the unchanged package while model-visible output remains non-substantive when ordinary narration drifts.
50. As a maintainer, I want the public tool to fail closed if narration-safe mode is not faithful, so that availability never outranks semantic integrity.
51. As a maintainer, I want explicit request, data, traversal, latency, payload, concurrency, and retention envelopes, so that implementation cannot hide truncation or rely on platform ceilings.
52. As a maintainer, I want reproducible application and Convex rollback plus tested backup and restore, so that recovery does not assume Vercel rollback also reverts data.
53. As a maintainer, I want every non-live product suite included in `npm run check`, so that a green repository check eventually represents the implemented product contracts.
54. As a reviewer, I want implementation diffs reviewed separately against this Spec and repository Standards, so that functional completeness and engineering quality receive independent scrutiny.
55. As a Challenge judge, I want the complete app to work in ChatGPT Developer Mode with visible provenance and graceful failure, so that the submission demonstrates a real evidence-grounded product rather than a scripted demo.

## Implementation Decisions

- Implement the Product runtime in strict TypeScript and ESM on Node.js with npm. Python is not a production tier.
- Use one cohesive Investigation module as the primary deep module. Its public application interface consists of Theological investigation, Source inspection, and Analysis branch.
- Expose those operations through exactly three read-only Streamable HTTP MCP tools: `theological_investigation`, `inspect_source`, and `branch_analysis`.
- Theological investigation accepts exactly the question as written as its only user-authored top-level input. Scope is extracted from the question and remains attributable to source spans.
- Source inspection accepts only a signed package-emitted Citation reference. It cannot accept an arbitrary URL or provider query.
- Analysis branch accepts a signed package-emitted Replay reference plus a separately user-authored Scope delta. It never mutates the parent package.
- Keep MCP transport, result-envelope shaping, tool annotations, and component resources in a thin adapter. Provider orchestration and answer construction belong to the Investigation module.
- Create adapters only for YouVersion retrieval, Gloo retrieval and structured analysis, MCP transport, the Ontology read store, and any selected telemetry sink, because each has real fixture and production behavior.
- Start with shared runtime schemas, pure policy, deterministic fixtures, an in-memory Ontology read store, a transport harness, and the Evidence component.
- The first supported fixture asks, “According to Matthew 22:37–40, which commandments does Jesus call greatest?” It uses reviewed public-domain World English Bible US fixture text and exact locators for Matthew 22:37–38 and Matthew 22:39–40. Until Issue #8 produces an accepted versioned benchmark, an unscoped contested question returns a typed missing-plan scope gap or requests narrower scope; it is not a supported answer fixture.
- Represent Analysis scope as requested constraints with original spans, effective constraints, neutral defaults, and unresolved terms. No tradition-bearing dimension may originate from a default.
- Use a deterministic versioned benchmark-category plan to select the minimum materially distinct Position memberships for an unscoped contested question once the benchmark exists. Never execute one pipeline per nominal family by default.
- Cap one Answer evidence package at six materially distinct Position memberships. A required plan exceeding that envelope must be re-benchmarked or expressed as a truthful initial comparison with explicit branches; runtime may not drop positions silently.
- Make the Answer evidence package the canonical answer data. It contains stable package-local identifiers, ordered Answer blocks, Position memberships, atomic Answer statements, Evidence links, Citations, Evidence gaps, provider reports, Analysis scope, Answer obligations and outcome, Operation receipts, semantic structure links, and exact release pins.
- Use a closed Answer-statement union: Textual observation, Tradition position, Historical context, Lexical observation, Comparative synthesis, and Conclusion.
- Give every source-grounded statement a first-class Evidence link with a role valid for that concrete statement type.
- Give every Derived statement explicit `derivedFrom` lineage. Project upstream Citations as inherited evidence and never present them as direct authorization for added synthesis.
- Allow a complete Derived statement to carry corroborating, qualifying, or challenging Citations only under a derived-only evidence policy; those Citations never replace lineage.
- Derive Sources and the Evidence graph from canonical package relationships rather than storing duplicate answer structures.
- Give every Material operation a stable versioned receipt and many-to-many output links to every Citation, Evidence gap, and Answer statement it produced or selected. Parent-operation links form an acyclic execution graph.
- Record non-replayability explicitly. Render branch controls only for graph nodes backed by a complete replayable receipt chain.
- Create one Answer obligation for each requested subquestion and, after the benchmark exists, each required materially distinct Position membership.
- Derive Answered when all required obligations are supported, Partially answered when some are supported, and Abstained when none are supported. Optional background and shared ground cannot promote the outcome.
- Treat provider errors as scoped Evidence gaps when a truthful package can still be assembled. Reserve tool-level errors for malformed input, invalid references, unsupported contracts, unsafe requests, or infrastructure failure that prevents even abstention.
- Use the versioned Tradition corpus and Corpus-snapshot compiler as the authority for source identity, tradition-relative authority, provenance, rights, admission, and Topic-pack membership.
- Admit substantive evidence only from `included` or explicitly permissioned immutable `fetch_only` artifacts. Mutable, unavailable, checksum-mismatched, `reference_only`, or `blocked` content cannot support a claim.
- Require every `fetch_only` artifact to have an immutable versioned locator, expected checksum verified on every fetch, and exact-byte availability through the complete reference window.
- Keep confidential agreements outside the public repository. Store only enforceable rights decisions, restrictions, review provenance, and controlled evidence identifiers in the public manifest.
- Use YouVersion server-side only after bounded Scripture locator selection. Record World English Bible US, YouVersion version 206, as the operational default when no edition is requested, subject to deployment-time registry verification.
- Keep Canonical collection independent from Scripture display edition and provider book inventory.
- Never persist YouVersion passage text in Convex, logs, telemetry, Gloo, durable caches, or Replay references. A branch rehydrates under the recorded version registry and current rights denylist.
- Use Gloo as two private capabilities: Publisher-scoped retrieval over a deployment mapped to one Corpus snapshot, then schema-constrained analysis over evidence Corvus independently resolved and admitted.
- Do not use Gloo shared corpora, coarse tradition controls, auto-routing, provider citation metadata, or ungrounded model memory as evidence.
- Use Convex as the sole production application database and vector facility. Do not retain PostgreSQL, pgvector, Render, Neo4j, or a shadow application store.
- Store immutable content-digested Ontology releases and Corpus snapshots. Every runtime read accepts a complete release pin; it never infers `latest`.
- Publish through compiler validation, idempotent bounded chunk staging, sealing, sealed-release validation, and one atomic compare-and-set active-pin mutation. Application runtime cannot publish or mutate releases.
- Enforce release-scoped stable-key uniqueness, referential closure, policy-class compatibility, source identity, authority scope, rights, Corpus membership, and embedding provenance in the compiler and privileged publication workflow.
- Implement deterministic structural traversal as a bounded release-pinned indexed Convex query. Maximum depth is two, frontier width 64, visited entities 256, relations read 1,024, returned entities and relations 256, user code 500 ms, read volume 8 MiB, documents scanned 16,000, and index ranges 2,000.
- Keep vector search optional for the first slice. Vector results are Discovery candidates only and must be reloaded and revalidated against the exact release, policy class, Corpus snapshot, and rights decision before use.
- Store embeddings only when the exact artifact permits durable derived indexing. Similarity scores remain operational metadata and never become evidence authority or theological confidence.
- Deploy one Vercel Node.js Function with Fluid Compute for the public `/mcp` endpoint and serve content-addressed Evidence-component assets from the same deployment. Do not use Edge Functions or split tools/providers into services.
- Use separate long-lived production and staging Vercel projects paired with separate production and staging Convex projects. Use deterministic fixtures for PR previews by default.
- Keep Convex deploy and publication authority in separate CI credentials. No Convex deploy key enters Vercel configuration.
- Before live Convex implementation, prove Vercel team-issuer OIDC acquisition, Convex-specific audience exchange, exact issuer/JWKS/audience/project/environment enforcement, expiry and refresh, negative cases, and zero token leakage in an isolated deployment.
- Keep the live Convex adapter disabled until every trust-spike case passes. A failure does not authorize a standing runtime database credential, anonymous Convex reads, or a second database.
- Keep the Challenge access model login-free with `noauth` MCP tools. Paid provider capabilities remain disabled until Developer Mode proves a ChatGPT-origin gate using a verified OpenAI-managed client certificate or published OpenAI egress enforcement at Vercel.
- The caller-gate proof must accept intended ChatGPT traffic, reject direct non-OpenAI callers before provider work, resist forwarded-header spoofing, cover certificate or egress-range rotation, isolate previews, and fail closed. If neither approach works, production provider spend remains zero. Adding user OAuth requires a separate product decision.
- Treat per-IP rate limits as observe-only until shared OpenAI egress behavior is measured. They cannot become identity or a fairness boundary.
- Enforce the initial runtime envelope: 16 KiB and 8,000 Unicode scalar values per question; 16 provider operations with concurrency three; 12 hydrated Scripture locators; 24 candidates and eight admitted Citations per Position; 48 Citations, 64 statements, and 48 receipts per package; approximately 16,000 model-visible tokens; 32 KiB `content`, 256 KiB `structuredContent`, 512 KiB component hydration, and 768 KiB total response.
- Set Vercel `maxDuration` to 60 seconds and the application deadline to 45 seconds. Reserve shutdown time for cancellation and deterministic degraded or abstaining assembly. Target p95 at or below 30 seconds under five concurrent investigations.
- Use global concurrency, request and capability budgets, provider quotas, daily spend caps, circuit breakers, overload shedding before provider calls, and emergency capability switches. Production spend defaults to zero.
- Make every dynamic MCP, Source-inspection, Analysis-branch, error, and result-hydration response `no-store`. Only versioned component assets without user or licensed content may use immutable public caching.
- Use signed integrity-protected references with server UTC and at most five minutes of clock skew. Citation references are valid for exactly seven days; Replay references are valid for exactly 24 hours. Reject encoded expiries beyond those maxima.
- Retirement stops new reference issuance. Retain the release, Corpus snapshot, locator metadata, replay contracts, required exact bytes, and verification keys for at least seven days plus skew after retirement. Pruning also requires export and restore gates.
- Validate current rights and denylist policy when a reference is used. Revocation may invalidate an otherwise unexpired reference but cannot substitute different evidence.
- Keep ordinary native ChatGPT narration as the primary presentation. Store ordered canonical wording for every substantive statement and validate proposition set, boundaries, Position ownership, Citation bindings, qualifiers, Evidence gaps, outcome, and Pastoral handoff after deployment and at least every 24 hours.
- On narration drift, disable ordinary narration and enter a separately tested narration-safe mode with non-substantive model-visible status and component-only canonical package hydration. If ChatGPT improvises, suppresses, or misrenders the component, activate the public-tool kill switch.
- Render the Evidence component as the accepted narration-first audit rail validated by `prototype/issue-5-evidence-component@f281e28`: ordinary native narration remains primary; a compact categorical outcome and supported-obligation row leads the component; required-obligation gaps precede audit details; Sources with exact locators and component-controlled Citation details are the first disclosure; and the question-to-answer Evidence graph is a separate on-demand disclosure. A claim ledger may exist inside inspection flows but is not the default structure. Render branch controls only for complete replayable receipt chains and show a reason, not an inert pseudo-control, when replay is unavailable. In narration-safe mode, hide substantive native narration and place the clearly labeled component-owned canonical answer before the same audit surfaces. Preserve keyboard reachability, visible focus, safe external targets, responsive status/gap visibility, and hostile-string-safe rendering.
- Treat all provider and source strings as untrusted bounded data, never instructions or executable links.
- Emit only content-free Operational telemetry: random request identifiers, contract and component versions, provider status and latency, usage and evidence-shape counts, validation outcomes, result classification, and sanitized errors.
- Exclude questions, answers, excerpts, Citation content, raw providers, request bodies, authentication material, remote IP addresses, stable user identifiers, inferred beliefs, pastoral context, and Convex query arguments from application telemetry. Maximum application telemetry retention is 30 days.
- Back up and export every immutable production release when rights permit. Preserve compiler inputs, artifacts, digests, repository revision, deployed function version, environment inventory, and recovery procedures outside the deployment.
- Require zero RPO after a release and its export are durable, 15-minute application rollback, 15-minute Convex active-pin rollback, and four-hour full restore into an isolated deployment.
- Keep Vercel rollback and Convex release rollback separate and compatibility-checked.
- Build the deployment sequence as expand-compatible Convex functions, compatible release verification, Vercel deployment from approved provenance, production smoke gates, and later contraction of obsolete readers.
- Preserve the accepted phase boundary: fixture schema/core policy first; benchmark-driven contested planning after Issue #8; Vercel transport and identity spikes; live Convex only after trust proof; live providers only after rights, caller-gate, redaction, contract, and spend proof; production only after every release gate.

## Testing Decisions

- The highest behavioral seam is the three-operation Investigation interface exposed through the MCP adapter. End-to-end tests should make calls through that seam and assert complete observable packages, reference behavior, component resources, and sanitized errors rather than internal call order.
- The first successful vertical-slice fixture is explicitly scoped or factually undisputed. Add an unscoped contested fixture only to prove typed missing-plan failure until the accepted benchmark exists.
- Use focused direct tests for pure scope, evidence-role, derivation, obligation, outcome, grouping, rights, budget, replay, and reference-lifetime policy because their combinatorial state warrants a narrower seam.
- Run the same Ontology read-store contract against the deterministic in-memory store, `convex-test`, and the open-source local Convex backend. Use a real isolated hosted deployment for platform-limit, identity, backup, restore, and vector behavior that local doubles cannot prove.
- Add `test:contracts` for package schema, stable identifiers, Analysis scope, Position membership, statement unions, Evidence links, derivation, obligations, outcomes, Evidence gaps, Operation receipts, graph integrity, replayability, rights, and envelopes.
- Add `test:storage` for immutable release shape, release-prefixed indexes, bounded traversal, publication chunk idempotence, partial failure, seal immutability, validation, atomic activation, singleton corruption, compare-and-set races, rollback, vector quarantine, export, and restore.
- Add `test:providers` for fixture and staging YouVersion and Gloo contracts, exact edition and deployment mappings, attribution, empty and partial results, malformed and hostile payloads, timeouts, rate limits, stale mappings, rights rejection, model schema violations, and redaction.
- Add `test:mcp` for initialization, versioned tool schemas and annotations, normal and malformed inputs, cancellation, deadlines, dynamic `no-store`, unsupported contract versions, serialized payload limits, and sanitized errors. The first fixture slice proves `theological_investigation` through the local harness. The contract-complete three-tool slice is the first gate that must discover exactly `theological_investigation`, `inspect_source`, and `branch_analysis` with all three fixture flows functional.
- Add `test:component` for declared CSP, versioned resource compatibility, complete Answer outcome and Evidence-gap rendering, inline Citation details, Sources, Evidence graph relationships, progressive disclosure, responsive layouts, keyboard and screen-reader behavior, hostile strings, and safe links.
- Add `test:security` for Vercel-to-Convex OIDC positive and negative claims, cross-environment rejection, secret absence, reference size/lifetime/tampering/signing-key rotation, current denylist revalidation, URL safety, log allowlists, preview isolation, publisher/runtime privilege separation, and arbitrary-fetch rejection.
- Add `test:deployed` for MCP Inspector, ChatGPT Developer Mode, normal narration fidelity, narration-safe mode, daily canary behavior, component rendering, ChatGPT-origin versus direct-caller isolation, shared-egress WAF behavior, cold and warm latency, five-request sustained concurrency, twenty-request burst shedding, application rollback, Convex rollback, and full restore.
- Make every non-live suite part of `npm run check` during the first implementation slice. Keep `test:deployed` separate because it requires deployed environments and live platform behavior.
- In that first slice, every non-live command must contain non-placeholder assertions at the seams then available: canonical contracts and policy, the in-memory store contract, fixture-provider behavior, the local investigation transport, minimal component hydration, and content/URL/log safety. Later tickets expand the same named suites at their stable seams; the first slice does not fabricate live Convex, provider, identity, reference-signing, or deployment behavior.
- Treat the current `npm run check` as workflow scaffolding only until these suites exist. Do not cite it as product-readiness evidence prematurely.
- Require successful, degraded, abstaining, hostile-content, missing-plan, expired-reference, revoked-rights, narration-drift, and budget-exhaustion fixtures.
- Assert external invariants rather than mock choreography: final Answer statements and links, scoped gaps, categorical outcome, exact release pins, deterministic ordering, sanitized references, bounded result size, and user-visible failure semantics.
- Test that shared ground, optional background, and unrelated gaps cannot alter required-obligation outcomes.
- Test that a Citation cannot authorize an incompatible statement type and that a Derived statement cannot gain unsupported content through projected citations.
- Test that grouping Position memberships never merges their owned statements, evidence, qualifiers, authority scopes, or gaps.
- Test reference boundaries at issuance, nominal expiry, five-minute skew, overlong encoded expiry, retirement, key overlap, key compromise, artifact loss, rights revocation, and release pruning.
- Test provider retries and concurrency against the single request-wide operation, deadline, and spend budgets; retries cannot expand the envelope.
- Test that no failure falls back to model memory, another Scripture edition, an unadmitted source, a mutable `fetch_only` page, or an alternate database.
- Test that vector similarity cannot appear as evidence authority, satisfy an obligation, change Answer outcome, or become user-visible theological confidence.
- Test that narration-safe mode sends no substantive package prose to the model and that failure to render the canonical component trips the tool kill switch.
- Use repository tests for workflow-check behavior as prior art for deterministic, externally observable policy tests, while recognizing that no current product test provides sufficient prior art for the new runtime contracts.
- Before completion of each implementation diff, run `npm run check` and perform separate automated Standards and Spec reviews from the pinned base revision.

## Out of Scope

- A standalone web application, custom chat client, persistent dashboard, or application shell outside ChatGPT.
- More than the three accepted public MCP operations.
- Public provider APIs, arbitrary URL fetch, general ontology browsing, release administration, or direct component-to-Convex access.
- Conversation storage, Answer-package persistence, belief profiles, hidden personalization, user question history, or theological analytics.
- User OAuth or provider sign-in under the current login-free Challenge contract.
- Supported unscoped contested-question planning before Issue #8 checks in and accepts the deterministic benchmark artifact.
- Production launch before exact-artifact rights coverage exists for every guaranteed family and mandatory benchmark Position.
- Claiming comprehensive coverage across every Christian denomination, jurisdiction, historical dispute, language, or theological topic.
- Treating `reference_only` material, public web pages, provider snippets, model memory, vector scores, or Gloo output as admitted evidence.
- Human clergy or scholar review as a runtime step or automated release gate.
- Persisting YouVersion passage text or raw Gloo exchanges.
- A generic workflow engine, provider registry, corpus network service, cache abstraction, microservice split, or plugin framework without a second concrete need.
- PostgreSQL, pgvector, Render, Neo4j, a second vector service, or a shadow application database.
- Multi-region Vercel/Convex operation before a benchmark and explicit superseding decision.
- Production use of beta Convex preview environments as durable staging.
- Making vector discovery mandatory for the first vertical slice.
- Replacing missing rights, failed trust, failed caller isolation, narration drift, or provider outage with a silent fallback.
- Closing or relabeling existing Wayfinder and implementation issues as part of this spec publication.

## Further Notes

- This spec synthesizes the decisions produced by the Apps SDK/MCP architecture grilling, ADRs 0005 through 0013, the implementation-readiness envelope, and two independent rubber-duck review passes.
- The agreed highest test seam is the three-operation Investigation interface. Focused pure-policy tests are exceptions justified by combinatorial invariants, not additional architectural modules.
- Immediate agent-ready implementation is limited to the fixture schema/core-policy vertical slice. The broader spec is ready for ticket slicing, but later tickets must encode their listed entry gates and must not be marked executable while those gates remain open.
- Issue #8 remains the required human decision for the deterministic evidence benchmark. No implementation agent may invent its material-position plans.
- The Vercel-to-Convex trust proof and login-free ChatGPT-origin caller proof are falsifiable spikes. Failed spikes preserve the fixture composition and zero provider spend.
- Runtime-admissible rights are a production blocker, not an accepted launch risk. Synthetic fixtures and reviewed public-domain artifacts permit development without copying restricted prose.
- The initial numeric envelopes are support boundaries to test, not claims of measured capacity. A representative benchmark may tighten or supersede them through an explicit decision; runtime cannot silently raise or truncate them.
- The existing Wayfinder map and placeholder implementation issues should be reconciled during subsequent ticket slicing to avoid duplicate execution surfaces.
