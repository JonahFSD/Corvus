---
status: proposed
---

# Keep substantive answer statements inside the evidence package

The prototype defaults to a fixture-first typed tree: Direct answer, Shared ground, and Comparison blocks contain atomic, citation-bound Answer statements; Position blocks group Position memberships, each of which owns its tradition-specific Tradition position and supporting statements, Evidence links, authority scope, coverage status, and Evidence gaps; Pastoral handoff is a separate policy-controlled block that references existing statements rather than owning another statement collection; provider reports and Evidence gaps name the statements or memberships they affect; and Sources and the Evidence graph are derived rather than stored as duplicate answer structures. Blocks and Position memberships have stable identifiers. Canonical semantic links record ordered package-to-block containment, block-to-statement containment, Position-block-to-membership grouping, membership ownership of its statements and evidence state, and Pastoral-handoff references to existing statements. The Evidence graph renders these links rather than guessing structure from UI layout. Each package records Analysis scope as four distinct collections: normalized user-requested constraints retaining their original question spans and resolved canonical identifiers; effective constraints actually applied; system or provider defaults not requested by the user; and unresolved scope terms that cannot be normalized without guessing. No default may populate a tradition-bearing dimension, including tradition or family, canonical collection, confessional authority, or liturgical rite. For an unscoped contested question, a deterministic versioned benchmark-category plan selects the minimum set of materially distinct Position memberships required to represent the significant interpretations; it does not automatically execute one pipeline per guaranteed family. Guaranteed coverage means every benchmark-required material position is available and correctly scoped, not that every family must be narrated on every question. Scripture discovery searches the union of canonical collections needed by that position plan while preserving collection-membership differences. Until Issue #8 checks in and accepts that benchmark artifact, implementation is limited to scoped or factually undisputed fixtures plus explicit missing-plan failure behavior; it may not invent production category plans. Neutral operational defaults remain permitted only when recorded separately and unable to change doctrinal scope. Every Analysis branch records an explicit scope delta against its immutable parent package and may expand a grouped or omitted family into a separately evidenced position on demand. For an unscoped question with material theological disagreement, Shared ground precedes Direct answer; Direct answer may lead for factual, undisputed, or explicitly scoped questions. Position memberships are separate by default. A Position block may group them only as a reversible presentation optimization when their independently owned primary Tradition-position statements have mechanically identical canonical proposition text and polarity and no membership-specific qualifier or Evidence gap makes the grouped heading misleading. Grouping never changes validation, obligations, outcomes, ownership, or the rendering of each membership's authority scope, Citations, qualifiers, and gaps. Citation records may be deduplicated by exact cited identity, but each statement owns its own membership-scoped Evidence link and validates that link independently. Inline markers resolve first to component-controlled Citation details; external targets are optional, registry-derived or allowlist-validated HTTPS destinations rather than executable provider strings. Answer statements form a closed discriminated union of Textual observation, Tradition position, Historical context, Lexical observation, Comparative synthesis, and Conclusion, sharing an evidence-bearing contract rather than a generic prose record with a loosely interpreted kind. The statement-to-Citation relationship is first-class and carries its Evidence role, analogous to an object-backed link with relationship metadata. Deterministic validation rejects an Evidence role that cannot authorize the statement's concrete semantic type. Derived statements instead carry `derivedFrom` relationships to supported upstream Answer statements. Their inline evidence markers project the upstream Citations through that lineage and explicitly label them as inherited evidence; they do not manufacture direct source authority for a synthesis or conclusion. A source may additionally corroborate, qualify, or challenge a complete Derived statement under a derived-only Evidence-role policy, but that Citation never replaces lineage or authorizes an unsupported addition. Every Material operation produces a stable, versioned Operation receipt. First-class, many-to-many Operation output links connect receipts to the Citations, Evidence gaps, and Answer statements they produced or selected, so deduplicated entities do not erase provenance. Parent-operation links form the execution DAG used to derive the Evidence graph and resolve Analysis branch replay. Each package enumerates its required Answer obligations and derives one categorical Answer outcome from their dispositions: Answered when all are supported, Partially answered when some but not all are supported, and Abstained when none are supported. Shared ground or optional background cannot promote an otherwise unsupported requested answer, and only Evidence gaps affecting a required obligation may downgrade the package outcome. Numeric confidence scores do not stand in for theological truth. Reusable Claim records are deferred until fixtures demonstrate reuse that outweighs normalization cost. The Answer evidence package is the canonical answer data, including the ordered canonical wording of every substantive statement; native ChatGPT narration is the intended primary presentation, and the Evidence component is its audit and exploration surface. Because the MCP cannot observe or prove that later native ChatGPT narration did not drift, every required Developer Mode fixture must prove before release that narration adds no substantive proposition, preserves statement boundaries and Citation bindings, discloses every Evidence gap and Answer outcome, and retains every required Pastoral handoff. The same synthetic canaries run after every deployment and at least once every 24 hours while the public tool is enabled. Any required semantic mismatch disables ordinary native narration and enters the explicit narration-safe mode defined by ADR 0013: model-visible text is non-substantive and the clearly labeled Evidence component renders the unchanged canonical package from component-only hydration. If Developer Mode cannot prove that this mode prevents improvised narration while preserving faithful component presentation, the public-tool kill switch activates. Returning to ordinary narration requires a passing fixture suite. All provider and source strings are untrusted data: they must be length-bounded, safely rendered as data rather than instructions, and pass evidence-policy validation. Acceptance requires successful, degraded, abstaining, and narration-safe fixtures, serialized byte and approximate token measurements, rights-safe delivery checks, hostile-content and citation-target tests, and operation receipts sufficient to render and replay every promised Analysis branch. Component `_meta` may carry only user-deliverable presentation data, while `content` remains a short noncompeting summary.

## Proposed schema vocabulary

The terms in this section are local to this proposed decision. They are promoted to the canonical glossary only after the fixtures and contract tests validate the schema and this ADR becomes accepted.

- **Answer statement**: a human-readable atomic proposition belonging to exactly one semantic type. It is small enough that every attached Citation and Evidence role applies to the complete proposition.
- **Textual observation**: a source-grounded Answer statement describing what cited Scripture explicitly says, contains, or juxtaposes.
- **Tradition position**: a source-grounded Answer statement describing what a named tradition body teaches, confesses, or practices.
- **Historical context**: a source-grounded Answer statement about a historical event, chronology, reception, or doctrinal development.
- **Lexical observation**: a source-grounded Answer statement about a Hebrew, Aramaic, or Greek form, sense, morphology, or usage.
- **Comparative synthesis**: a Derived statement identifying material agreement, disagreement, or tension among supported upstream statements or memberships.
- **Conclusion**: a Derived statement answering or closing a line of analysis from named supported upstream statements.
- **Derived statement**: a Comparative synthesis or Conclusion whose `derivedFrom` relationships name the upstream statements that authorize it.
- **Evidence lineage**: the auditable path from a Derived statement through `derivedFrom` relationships to source-grounded statements and their Citations.
- **Answer block**: a stable-identity semantic section: Direct answer, Shared ground, Position, Comparison, or Pastoral handoff. Its package-containment link carries display order.
- **Position membership**: one tradition family's scoped participation in a Position block, owning that family's statements, Evidence links, authority scope, coverage status, and gaps.
- **Semantic structure link**: a canonical typed relationship recording ordered package containment, statement containment, Position membership grouping, membership ownership, or Pastoral-handoff reference. It is package data, not a relationship inferred from rendering.
- **Citation record**: an immutable package-local cited identity defined by its source artifact, exact locator, edition or translation, content mode, delivered excerpt, and resolvable target when available.
- **Evidence link**: a statement-owned, and when applicable membership-scoped, relationship to one Citation record carrying its Evidence role. Reusing a Citation record never reuses or transfers its Evidence links.
- **Evidence role**: relationship metadata whose valid values depend on statement class. A source-grounded statement permits `directlyAsserts`, `textuallyGrounds`, `interprets`, `contextualizes`, `challenges`, or `qualifies`; a Derived statement permits only `corroborates`, `challenges`, or `qualifies`.
- **Admissible evidence**: evidence whose source kind, authority and tradition scope, delivery rights, and complete set authorize the concrete statement under its policy.
- **Analysis scope record**: four separately attributable collections: `requested` constraints explicitly present in the user's question, with original spans and resolved canonical identifiers; `effective` constraints actually applied; `defaults` introduced by system or provider policy; and `unresolved` terms that cannot be normalized without guessing.
- **Scope delta**: the explicit additions, removals, or replacements applied by an Analysis branch relative to its immutable parent package's Analysis scope record.
- **Operation receipt**: the stable package-local record of one Material operation, including its kind, executor or provider, relevant schema/model/provider versions, sanitized replay inputs, effective scope, status, timing, parent operation identifiers, replayability, and a reason when it is not replayable.
- **Operation output link**: a many-to-many provenance relationship connecting an Operation receipt to a Citation record, Evidence gap, or Answer statement it produced or selected. The relationship records the output role without duplicating either endpoint.
- **Answer obligation**: a required unit of the user's requested answer, identified from each requested subquestion and, for an unscoped contested question, each materially distinct Position membership required by the versioned benchmark-category plan. It records `supported` or `unsupported` plus the Answer statement and Evidence-gap identifiers that determine that disposition.
- **Pastoral-handoff policy record**: a non-evidentiary block carrying one or more reason codes, urgency, recommended actions, and references to existing Answer statements. Its reason codes are `personalDiscernment`, `sacramentalOrEcclesialJudgment`, `ongoingPastoralRelationship`, and `acuteSafetyOrCrisis`.

## Scope invariants

- Every requested constraint retains its dimension, original question span, normalized value, and canonical identifier when one resolves.
- Every effective constraint names whether it came from `requested`, `defaults`, or a branch `scopeDelta`.
- A tradition-bearing dimension—including tradition or family, canonical collection, confessional authority, or liturgical rite—may enter effective scope only from an explicit requested constraint or an explicit user-created branch delta. The system has no tradition-bearing default or proxy default.
- An unscoped contested question uses the versioned benchmark-category position plan. That plan includes every materially distinct interpretation required for the category, may group only under the Position-grouping invariants, and never selects a tradition as the user's implied lens. If no validated plan applies or the required plan exceeds the release envelope, the tool asks for narrower scope or returns an explicit scope Evidence gap; it never silently drops positions.
- Neutral operational defaults may enter `defaults` only when they cannot change doctrinal scope. They remain attributable and may not be reclassified as user-requested constraints.
- An unresolved term remains visible and cannot be converted into effective scope by model inference.
- A branch preserves the parent package and records its parent package identifier, selected graph-step identifier, and scope delta before rerunning the affected investigation path.

## Outcome invariants

- Answer obligations cover every requested subquestion. An unscoped contested question also creates one obligation for every materially distinct Position membership required by its versioned benchmark-category plan. Family-level expansion remains available through Analysis branch without changing the original package.
- Each obligation has exactly one disposition: `supported` when its complete required answer is sufficiently evidenced, or `unsupported` with the Evidence-gap identifiers that prevent support.
- The package is `Answered` when all required obligations are supported, `Partially answered` when at least one but not all are supported, and `Abstained` when none are supported.
- Shared ground, historical background, lexical context, or other optional material does not satisfy a requested obligation by itself and cannot promote `Abstained` to `Partially answered`.
- An Evidence gap changes the package outcome only when it affects a required obligation. Other gaps remain disclosed and scoped without downgrading the result.
- The validator derives package outcome from obligation dispositions and rejects a conflicting model-supplied outcome.

## Provenance and replay invariants

- Operation identifiers, package entity identifiers, and Operation output links are stable and unique within the package.
- Parent-operation relationships are acyclic. Every operation that consumes another operation's result names that parent explicitly.
- Each receipt records operation kind, versioned execution contract, executor or provider, sanitized replay inputs, effective scope, status, timing, and replayability. A non-replayable receipt carries a machine-readable reason.
- Operation output links connect receipts to every Citation record, Evidence gap, and Answer statement they produced or selected. The links are many-to-many: separate operations may point to the same deduplicated Citation record without merging their provenance.
- The Evidence graph derives only from canonical package relationships: question and Analysis scope record to Operation receipts; parent-operation and Operation output links to Citations and Evidence gaps; Evidence links to source-grounded statements; and `derivedFrom` relationships to Derived statements.
- Every branchable graph node resolves to at least one responsible, replayable receipt chain. Only nodes backed by such a chain may render a branch control. A branch records the immutable parent package identifier, selected node and operation identifiers, Scope delta, and new receipt chain.
- Receipts and replay inputs exclude credentials, private chain-of-thought, unnecessary provider payloads, and any field forbidden by the product's data-retention policy.
- Every Answer block and Position membership has a stable package-local identifier.
- Semantic structure links record package `contains` block with order; ordinary block `contains` statement; Position block `groups` membership; membership `owns` statements, Evidence links, authority scope, coverage status, and Evidence gaps; and Pastoral handoff `references` existing statements.
- The Evidence graph includes Semantic structure links. Grouping is presentational and never merges membership-owned statements, Evidence links, or evidence state.

## Block invariants

| Answer block     | Allowed Answer statement types                                                                                                               |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Direct answer    | Conclusion                                                                                                                                   |
| Shared ground    | Textual observation, Historical context, Lexical observation, Comparative synthesis                                                          |
| Position         | None directly; each Position membership owns Tradition position, Textual observation, Historical context, and Lexical observation statements |
| Comparison       | Comparative synthesis, Conclusion                                                                                                            |
| Pastoral handoff | None; it references existing statements and carries policy reason and action data                                                            |

A Comparative synthesis may appear in Shared ground only when every in-scope Position membership is sufficiently supported. An absent or evidence-gapped membership prevents that proposition from being classified as shared.

## Position-grouping invariants

- Position memberships render separately by default.
- Grouping is a reversible presentation choice and never changes schema validation, Answer obligations, Answer outcome, evidence ownership, or graph provenance.
- Memberships may group only when their independently owned primary Tradition-position statements have byte-identical canonical proposition text and the same polarity.
- A membership-specific qualifier, scope distinction, or Evidence gap that would make the grouped heading misleading forbids grouping even when the primary proposition text matches.
- Every grouped membership still renders its own authority scope, Citations, qualifiers, coverage status, and Evidence gaps.
- If equivalence is not mechanically provable under these rules, the memberships remain separate. Any future semantic normalization requires a separately accepted decision backed by fixtures.

## Pastoral-handoff invariants

- A Pastoral handoff may coexist with `Answered`, `Partially answered`, or `Abstained` and never changes the Answer outcome or satisfies an Answer obligation.
- Every handoff carries at least one defined reason code, an urgency, one or more recommended actions, and any existing Answer statement identifiers needed to explain its context.
- The handoff owns no Answer statements and introduces no substantive theological proposition. Any theological explanation remains an ordinarily typed, evidenced, and cited Answer statement referenced by the handoff.
- `personalDiscernment`, `sacramentalOrEcclesialJudgment`, and `ongoingPastoralRelationship` may recommend appropriate local clergy without implying that the app can make the personal or ecclesial judgment.
- `acuteSafetyOrCrisis` invokes the separate safety-response policy and never presents clergy as the sole emergency resource.
- Sensitivity, disagreement, or controversy alone does not trigger a handoff; an ordinary doctrinal question remains an ordinary evidenced answer unless one of the defined reasons actually applies.

## Evidence admissibility

Every statement's evidence passes four independent gates:

1. **Resolvable**: each Citation identifies an exact source and locator.
2. **Admissible**: source kind, recognizing body, authority scope, tradition scope, and corpus version may authorize the statement and Position membership.
3. **Deliverable**: the artifact's rights and content mode permit every excerpt, text fragment, and target delivered to the model or component.
4. **Sufficient**: the complete evidence set satisfies the policy for the statement's concrete semantic type.

Approved scholarship cannot independently establish a Tradition position, a source scoped to one body cannot silently represent an entire tradition family, and a `reference_only` artifact cannot supply undisclosed full text merely because its Citation resolves.

Textual observations, Tradition positions, Historical context, and Lexical observations are source-grounded statements. Every Comparative synthesis and Conclusion is a Derived statement that names the supported upstream Answer statement identifiers through `derivedFrom` relationships. Its inline evidence marker exposes the named upstream statements and projects their Citations as inherited evidence. Projected Citations remain linked to their source-grounded statements and retain their original Evidence roles; they do not become direct evidence for the Derived statement. A source that independently states the complete derived proposition may be attached as `corroborates`; one that narrows or conditions it may be attached as `qualifies`; and one that disputes it may be attached as `challenges`. These derived-only roles never satisfy the mandatory lineage requirement, replace an upstream evidentiary path, or authorize a substantive addition absent from that path.

| Source-grounded statement type | Minimum admissible evidence                                                                                                                                                                     |
| ------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Textual observation            | Scripture Citation that directly asserts or textually grounds what the cited text explicitly says, contains, or juxtaposes                                                                      |
| Tradition position             | At least one primary Tradition source that directly asserts what the named body teaches, confesses, or practices; Approved scholarship may only interpret, contextualize, challenge, or qualify |
| Historical context             | Admitted primary historical evidence or Approved scholarship that directly asserts or contextualizes an event, chronology, reception claim, or development                                      |
| Lexical observation            | Admitted lexical or morphological source tied to the relevant Hebrew, Aramaic, or Greek text and exact locator                                                                                  |

| Derived statement Evidence role | Valid relationship                                                          |
| ------------------------------- | --------------------------------------------------------------------------- |
| `corroborates`                  | The cited source independently states the complete synthesis or conclusion  |
| `qualifies`                     | The cited source narrows or conditions the complete synthesis or conclusion |
| `challenges`                    | The cited source disputes the complete synthesis or conclusion              |

Source-grounding roles are invalid on Derived statements, and derived-only roles are invalid on source-grounded statements.

## Derived-lineage invariants

- Every `derivedFrom` identifier resolves to another Answer statement in the same immutable package and never to the statement itself.
- `derivedFrom` relationships form an acyclic graph. A deterministic topological traversal must terminate in one or more source-grounded statements.
- Every source-grounded statement in that transitive closure passes resolvability, admissibility, deliverability, and sufficiency checks in its own scope.
- A Derived statement is invalid when its proposition requires an upstream statement or membership whose Evidence gap prevents that support; a projected Citation cannot repair the missing lineage.
- A derived-only Citation role supplements this validated lineage and never participates in satisfying the closure requirement.

## Citation identity invariants

- The package contains one Citation record for each exact combination of source artifact, locator, edition or translation, content mode, delivered excerpt, and resolvable target.
- Two statements may reference the same Citation record only through separate Evidence links. Each link carries its own Evidence role and membership scope and passes admissibility and sufficiency checks independently.
- A shared Citation identifier conveys source identity only. It never transfers doctrinal support, tradition scope, authority, or coverage between statements or Position memberships.
- A difference in any identity field produces a distinct Citation record rather than mutating or ambiguously widening an existing record.
- The Sources dropdown is a derived, deduplicated presentation of Citation records; it is not a second source-of-truth collection.

## Citation target safety

- An inline marker resolves to component-controlled Citation details by Citation identifier. Provider-supplied strings are never executed or opened directly.
- External targets are constructed from the trusted Source registry whenever possible. Any accepted target is an absolute production `https:` URL whose origin is allowlisted for that Source.
- Validation rejects userinfo, non-HTTPS and custom schemes, localhost, private or link-local network targets, and redirect chains whose every hop and final origin have not passed the same policy.
- External navigation uses opener isolation and referrer protection. Source labels, locators, excerpts, and target text are escaped and rendered as data rather than markup or instructions.
- A rejected external target is omitted and reported by validation. The Citation's exact locator remains inspectable in component-controlled details and is never replaced with an unsafe best-effort link.

The minimum schema-driving fixture asks, “According to Matthew 22:37–40, which commandments does Jesus call greatest?” It uses reviewed public-domain World English Bible US fixture text and exact locators for Matthew 22:37–38 and Matthew 22:39–40. One requested Answer obligation is supported by two atomic Textual observations and a Derived Conclusion whose explicit lineage names both observations. Successful, degraded, abstaining, and hostile-data variants keep the question fixed so package-shape differences reflect evidence state rather than topic changes.

After Issue #8 is accepted, the contested stress fixture asks, “Does baptism save, and should infants be baptized?” Its successful maximum-coverage case exercises Catholic, Eastern Orthodox, Oriental Orthodox, and all six Major Protestant families through the benchmark's materially distinct Position plan. It proves coverage and grouping behavior; it does not require every ordinary contested question to execute every family. A Position block may group memberships only when their independently supported propositions are materially equivalent; each membership owns its own statements and Evidence links, so the fixture does not create repetitive visible sections merely to display nominal coverage.
