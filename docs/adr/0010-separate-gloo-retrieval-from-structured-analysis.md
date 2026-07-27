# ADR-0010: Separate Gloo retrieval from structured analysis

- Status: accepted
- Date: 2026-07-26

## Context

The Investigation module needs semantic retrieval over a deployed copy of the admitted Tradition corpus and bounded model assistance to turn validated evidence into candidate structured Answer statements. Gloo provides both capabilities, but its provider contract does not itself enforce Corvus's evidence policy.

Gloo's grounded endpoints default `rag_publisher` to the shared `GlooGrounded` dataset when the caller omits it. Grounded generation can also continue when retrieval returns no sources. Its optional `tradition` control changes retrieval and generation but recognizes only `evangelical`, `catholic`, `mainline`, and `not_faith_specific`. Those categories cannot represent Corvus's guaranteed tradition families, recognizing bodies, canonical collections, or source-authority rules without collapsing material distinctions.

Gloo also exposes a publisher-data Search API independently from its Responses API. Separating those calls lets Corvus resolve provider results against the pinned Corpus snapshot before any model analyzes them. It also lets the runtime use the current Responses shape, direct model selection, structured output, and its own explicit Analysis scope rather than provider values-alignment.

## Decision

Treat Gloo as one external dependency with two private, replaceable capabilities inside the Investigation module:

1. **Publisher-scoped semantic retrieval** returns candidate corpus items from the deployment mapping for exactly one pinned Corpus snapshot.
2. **Structured analysis** receives only bounded, rights-permitted evidence already resolved and admitted by Corvus, then returns schema-constrained candidate analysis.

Gloo is neither an evidentiary authority nor a tradition taxonomy. Provider output is untrusted data. The deterministic evidence gate remains the only path from a provider result to an Answer statement, Citation, Evidence link, Evidence gap, or Answer outcome.

### Retrieval contract

Use Gloo's publisher-data Search API rather than a grounded-generation endpoint for Tradition-corpus retrieval. The production adapter must provide an explicit, versioned collection and tenant mapping resolved from deployment configuration for the pinned Corpus snapshot. The MCP caller cannot supply or override that mapping.

Every returned item is only a retrieval candidate until the adapter and corpus policy can map its producer or item identity to one exact admitted artifact and chunk in that Corpus snapshot. The mapping validates source identity, edition, recognizing body, tradition and authority scope, locator, checksum, rights mode, and permitted content delivery. Provider titles, publishers, snippets, scores, URLs, and other metadata cannot create or repair those facts. An unmapped, ambiguous, stale, or rights-incompatible result is rejected and may create a scoped Evidence gap when it affects a required Answer obligation.

Semantic certainty and ranking scores may bound and order candidate work. They never express theological confidence, evidence sufficiency, source authority, or package outcome. Search limits, thresholds, and query templates are versioned operational policy selected through fixtures and benchmarks, not user-facing controls.

Never call a Gloo retrieval path with an omitted publisher, collection, or tenant value whose omission could select shared or provider-default content. Do not use `GlooGrounded` or arbitrary Gloo-hosted material as an admitted corpus. The repository-governed corpus manifest remains the source of record; a Gloo deployment is a disposable derived retrieval index.

### Analysis contract

Use the Gloo Responses API with one explicitly configured model identifier. Do not use auto-routing, model-family routing, grounded generation, or the Gloo `tradition` control in the production evidentiary path. Corvus represents tradition semantics through explicit Analysis scope, Position memberships, recognizing bodies, and admitted source metadata.

The configured model, prompt-contract version, structured-output schema version, temperature and sampling settings, token limit, timeout, and retry policy form one versioned analysis profile. A deployment changes that profile only after the benchmark and evidence-contract suites pass. Each Material-operation receipt records the requested and actual model identifiers, profile and schema versions, bounded usage data, status, and sanitized replay inputs.

The normal contested-question execution is:

1. plan required Answer obligations and Position memberships from explicit Analysis scope or the validated versioned benchmark-category plan for an unscoped contested question;
2. retrieve candidate evidence independently for each required membership;
3. resolve, rights-check, and admit candidates against the pinned Corpus snapshot;
4. run bounded structured analysis separately for each membership using only its admitted evidence bundle;
5. deterministically validate the candidate source-grounded statements and Evidence links in that membership's scope;
6. run a final structured comparison only over the validated statements and identifiers needed for synthesis; and
7. validate every Derived statement's `derivedFrom` lineage before package assembly.

Independent membership retrieval and analysis may run concurrently under a fixed concurrency limit, but their package order and provenance are deterministic. Keeping membership calls separate prevents one tradition's evidence, authority scope, or gap from leaking into another. The planner executes materially distinct benchmark-required positions, not one call per nominally guaranteed family; mechanically equivalent memberships may share presentation only after their evidence is independently validated. Factual, undisputed, or explicitly narrow questions execute only the memberships and comparison steps their Answer obligations require. A plan that is missing, ambiguous, or over the release envelope fails visibly rather than silently omitting positions.

The analysis prompt may instruct the model to abstain from unsupported additions, but prompts are not enforcement. The parser rejects malformed output, unknown identifiers, invented Citations, statements outside the supplied evidence and scope, invalid Evidence roles, and unsupported lineage. No repair pass may silently add evidence or broaden scope; a bounded syntactic repair may be attempted only when it preserves the same supplied evidence and is recorded as a Material operation.

### Degradation and fallback

A retrieval timeout, empty result, unmapped item, provider error, or analysis failure affects only the Answer obligations and Position memberships that depend on it. The package records a Capability report and scoped Evidence gap, then deterministically derives Answered, Partially answered, or Abstained under ADR 0005.

There is no model-memory fallback, cross-membership evidence substitution, automatic switch to `GlooGrounded`, or hidden switch to a provider `tradition` value. If final comparative synthesis fails, the product may return independently validated source-grounded positions while omitting the unsupported synthesis or Conclusion. If no required obligation remains supported, it returns an abstaining package rather than unsupported prose.

Retries are bounded and limited to requests safe to repeat. Cancellation and request-wide deadlines propagate through search and analysis. Gloo authentication tokens are server-side, short-lived, and coalesced in memory; credentials, raw exchanges, prompts, and provider endpoints never enter the Answer evidence package or component state.

### Adapters and verification

The internal Gloo seam has production HTTP implementations and deterministic fixture implementations for retrieval and structured analysis. Fixtures cover successful, empty, partial, malformed, hostile, stale-mapping, rights-blocked, rate-limited, timeout, and provider-error responses. Contract tests against Gloo's live sandbox verify authentication, endpoint shapes, direct-model behavior, search mappings, limits, and failure semantics without making the ordinary test suite depend on live credentials.

The offline Corpus-snapshot publisher verifies that every uploaded Gloo item has a stable manifest mapping and removes or quarantines obsolete deployment items before a mapping is eligible for production. A release cannot depend on a provider item that the snapshot compiler cannot resolve exactly.

## Rejected alternatives

- Use Grounded Completions with `tradition` set from each Corvus Position membership.
- Treat `evangelical`, `catholic`, or `mainline` as aliases for the guaranteed tradition families.
- Omit `rag_publisher` and accept Gloo's shared grounded corpus as supplemental evidence.
- Let one comparative generation call retrieve and analyze evidence for every membership at once.
- Accept Gloo citation metadata, URLs, snippets, or model output directly as package Citations or provenance.
- Use auto-routing or model-family routing in the release path without a pinned model and benchmarked profile.
- Fall back to ungrounded model knowledge when retrieval or validation fails.

## Consequences

Corvus owns theological scope and evidence admission while still using Gloo for the capabilities it provides well. Provider defaults and coarse tradition categories cannot silently alter an answer. Per-membership isolation, manifest resolution, direct model pinning, and deterministic validation make degradation attributable and reproducible.

The implementation requires two Gloo call shapes, an exact deployment-item mapping, corpus-publishing checks, per-membership orchestration, and a second comparison stage. This costs more requests and code than one grounded completion, but it prevents retrieval, generation, authority, and tradition semantics from collapsing into an opaque provider call. Benchmarks must establish practical concurrency, request, token, and latency budgets before release.
