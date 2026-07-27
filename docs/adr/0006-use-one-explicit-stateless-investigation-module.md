# ADR-0006: Use one explicit stateless Investigation module

- Status: accepted
- Date: 2026-07-26

## Context

The Bible Ontology MCP must support a normal Theological investigation, Citation-bound Source inspection, and non-destructive Analysis branch reruns. The implementation must coordinate ontology access, the repository-governed Tradition corpus, licensed YouVersion retrieval, Gloo structured analysis, evidence validation, package assembly, degradation, replay, and content-free Operational telemetry. Live providers must be replaceable with deterministic fixtures, while the product must remain stateless with respect to users and conversations.

Splitting these behaviors into provider-facing MCP tools would make ChatGPT responsible for orchestration, rights policy, failure handling, and evidentiary correctness. Splitting the runtime into investigation, source, evidence, provider, or workflow services would add distributed state and failure modes before any independent scaling or ownership need exists. A hierarchy of internal application modules and generic registries would likewise optimize for hypothetical future reuse rather than the three operations the product requires now.

## Decision

Build one cohesive, stateless Investigation module and deploy it initially in the same executable process as a thin Apps SDK/MCP transport adapter. The module exposes three explicit read-only operations:

```ts
interface Investigation {
  investigate(input: { question: string }): Promise<AnswerEvidencePackage>;

  inspectSource(input: {
    citationReference: CitationReference;
  }): Promise<SourceInspection>;

  branchAnalysis(input: {
    replayReference: ReplayReference;
    operationId: OperationId;
    scopeDelta: ScopeDelta;
  }): Promise<AnswerEvidencePackage>;
}
```

The MCP adapter maps these operations directly to `theological_investigation`, `inspect_source`, and `branch_analysis`. It owns transport schemas, tool annotations, result-envelope shaping, and the Evidence component resource; it does not orchestrate providers or construct answers. The normal tool accepts exactly `{ question }`, with the question as written as its sole user-authored input.

### Explicit execution path

The Theological investigation implementation keeps its material execution order apparent in one top-level path:

```text
validate question
  → resolve explicit Analysis scope and Answer obligations
  → pin Corpus snapshot and retrieve admitted evidence
  → hydrate rights-permitted Scripture text
  → request bounded structured analysis
  → assemble the candidate Answer evidence package
  → run the deterministic evidence gate
  → emit the immutable package and rights-safe presentation data
```

Internal helper functions exist when they remove duplication or isolate a meaningful computation. Scope resolution, admissibility, lineage validation, outcome derivation, graph derivation, and package validation are pure functions where practical: their complete state enters through parameters and their results return as values. Do not create an internal class hierarchy, operation registry, workflow engine, event bus, or interface for a helper called from only one place.

### Real seams and adapters

Use adapters only at real seams with at least production and fixture behavior:

- YouVersion retrieval: server-side REST adapter and deterministic fixture adapter.
- Gloo authentication, retrieval, and structured analysis: server-side OAuth/HTTP adapter and deterministic fixture adapter.
- MCP transport: production Streamable HTTP adapter and an in-process transport test harness.
- Any external telemetry sink actually selected for deployment: sanitized production sink and in-memory/no-op test behavior.

The repository-governed source manifest is compiled and validated offline into an immutable, versioned Corpus snapshot. The runtime reads that artifact directly. Do not introduce a corpus network service, generic provider registry, configurable orchestration graph, or independent cache interface until a second concrete implementation or measured deployment constraint creates a real seam. Infrastructure such as a database or cache may sit behind direct runtime access without becoming a separately deployed product module.

### Stateless continuation

The server retains no conversation, Answer evidence package, user profile, inferred belief, or pastoral situation. Source inspection and Analysis branching use package-emitted, short-lived, bounded, integrity-protected references:

- A `CitationReference` binds the Citation identity, source and edition identity, exact locator, Corpus snapshot identity, permitted content mode, expiry, and integrity signature. It is not an arbitrary URL or provider request.
- A `ReplayReference` carries the root question, immutable parent package identifier and digest, sanitized replay inputs, responsible operation and version identities, effective Analysis scope, Corpus snapshot identity, expiry, and integrity signature. It excludes credentials, raw provider exchanges, private chain-of-thought, unnecessary source content, and any stable user identity.

`branchAnalysis` accepts a user-authored Scope delta separately, verifies that the selected operation has a replayable receipt chain, and returns a new immutable package linked to its parent. Expired, oversized, tampered, non-replayable, or no-longer-admissible references fail closed. The original package remains valid and unchanged when inspection or branching is unavailable.

### Failure and performance behavior

Expected provider timeouts, rate limits, empty results, missing Topic packs, and rights restrictions become provider reports and scoped Evidence gaps inside a valid Answered, Partially answered, or Abstained package whenever a truthful package can still be constructed. Tool-level errors are reserved for malformed input, invalid references, unsupported schema versions, unsafe requests, or infrastructure failure that prevents even an abstaining package.

Apply explicit bounds to the question, Material operations, hydrated passages, citations, excerpts, replay references, total work, provider deadlines, serialized bytes, and approximate model-visible tokens. Determine the concrete budgets from successful, degraded, abstaining, and hostile fixtures rather than speculative capacity planning. Independent retrieval may run concurrently, but the visible logical order and package provenance remain deterministic. Persist only source-oriented data permitted by rights policy and content-free Operational telemetry.

### Verification

The three public operations are the primary test surface. End-to-end fixtures exercise them with production composition replaced by fixture adapters and assert complete observable packages and sanitized errors, not internal provider-call choreography. Focused tests directly exercise pure evidence-policy functions where their combinatorial state warrants it. Developer Mode fixtures separately verify Apps SDK result shaping, native ChatGPT narration fidelity, Evidence component behavior, payload size, and branch invocation.

## Rejected alternatives

- Expose ontology traversal, Scripture retrieval, corpus search, Gloo analysis, validation, or rendering as separate MCP tools.
- Split the first deployment into investigation, provider, corpus, evidence, workflow, or replay microservices.
- Create separate object-oriented application-module interfaces for Theological investigation, Source inspection, and Analysis branching.
- Publish a generic provider or operation registry for hypothetical future integrations.
- Persist packages or conversations server-side to make Source inspection or Analysis branching easier.
- Return prose or raw evidence for the MCP adapter or ChatGPT host to assemble into the canonical answer.

## Consequences

The main request path remains easy to read, debug, measure, and test. Evidence policy and provider failure semantics stay local to one implementation instead of leaking into callers. Fixture and production providers can replace one another without making the external interface generic. The first deployment has one application process, one release unit, and no conversation database.

The module may become large because it owns the complete investigation behavior; that is intentional while the external interface remains small and the execution path remains comprehensible. Extraction requires evidence: independent scaling, security isolation, a second real caller, or another concrete implementation at a seam. Replay references add signing, expiry, and payload-budget work, but preserve the required branch behavior without weakening the privacy posture.
