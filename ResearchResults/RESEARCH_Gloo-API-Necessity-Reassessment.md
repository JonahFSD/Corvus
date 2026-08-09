# Gloo API necessity reassessment

_Primary-source review checked 2026-08-09. This note compares current Gloo and YouVersion documentation with Corvus's accepted product documents. It makes no authenticated provider calls and records no credentials._

## Conclusion

Corvus does **not** need Gloo as a core product dependency. It needs the capabilities currently assigned to Gloo—semantic retrieval and model-assisted structured analysis—but neither capability is uniquely Gloo-specific.

The challenge once created the only external requirement to use Gloo: its rules say both the YouVersion and Gloo APIs must be meaningfully integrated. That requirement no longer justifies a new product dependency. Gloo's published schedule closed submissions on **July 31, 2026** and ended judging on August 7; today is August 9. The page still renders a stale “Registration is open” call to action, but its own dates and the repository's contemporaneous capture establish that the submission window has ended. Unless Corvus is preserving an already-submitted, provider-dependent judging artifact, Gloo is not essential for challenge eligibility now. [Gloo challenge](https://studio.ai.gloo.com/challenge) · [repository challenge-brief research](RESEARCH_Scripture-Platform-Challenge-Briefs.md) · [domain language](../CONTEXT.md)

The managed Gloo Data Engine, Publisher ingestion, Search API, and grounded-generation paths should be removed from the required architecture. They duplicate the Convex retrieval facility Corvus has already selected, add a second mutable index and release-mapping problem, require a paid Pro or Enterprise plan, and give Corvus less control over chunk identities and boundaries than its evidence contract requires.

Recommended classification:

| Gloo capability | Classification | Recommendation |
| --- | --- | --- |
| A meaningful Gloo API integration | **No longer essential** | The submission deadline was July 31, 2026. Preserve only if an already-submitted artifact still depends on it. |
| Responses API for structured candidate analysis | **Optional product dependency** | Keep only if benchmarks or an already-submitted artifact justify it, behind a replaceable analysis seam with a pinned model/profile and deterministic validation. |
| Data Engine ingestion and Publisher deployment | **Remove from required architecture** | Compile and publish rights-permitted chunks and embeddings directly to immutable Convex releases. |
| Search API / Publisher-scoped semantic retrieval | **Remove from required architecture** | Use release-pinned Convex traversal and vector discovery with application-owned filters and exact chunk identities. |
| Grounded Responses / Grounded Completions | **Remove from the evidentiary path** | They deliberately combine retrieval and generation, can continue ungrounded, and do not enforce Corvus's claim-level evidence policy. |
| Gloo `tradition`, shared `GlooGrounded`, auto-routing, provider citations | **Remove** | They conflict with accepted tradition scope, authority, provenance, and model-pinning rules. |

If challenge compliance is no longer required, Gloo should be removable without changing the Bible Ontology MCP's three-operation interface or the Answer evidence package. That is the stronger architecture test.

## What is verified, assumed, and inferred

### Verified current provider facts

#### Gloo access and model analysis

- Gloo authenticates API calls with OAuth2 client credentials: a client ID and secret are exchanged at `https://platform.ai.gloo.com/oauth2/token` with scope `api/access`, and the returned Bearer token is temporary. Current SDK guidance says tokens expire after one hour and must be refreshed. [Gloo authentication](https://docs.gloo.com/tutorials/authentication) · [Gloo SDK guidance](https://docs.gloo.com/api-guides/sdks-and-libraries)
- Gloo recommends `POST /ai/v1/responses` for new integrations. It accepts an explicitly selected model, typed `input` and `output` items, tools, streaming, reasoning controls, and `response_format` structured-output/JSON-schema controls. [Gloo Responses API](https://docs.gloo.com/api-guides/responses-v1)
- The Responses API is a direct model passthrough. Gloo explicitly says that it does not currently apply Gloo guardrails, output moderation, `tradition`, model-family selection, or intelligent auto-routing. Those features remain on Completions V2 or Grounded Completions. This means Gloo Responses provides a model-broker and schema surface, not a uniquely faith-governed analysis guarantee. [Gloo Responses API](https://docs.gloo.com/api-guides/responses-v1)
- Gloo's model catalog is dynamic and spans multiple providers. Current model IDs, capabilities, and prices are available on the supported-models page and programmatically through `GET /platform/v2/models`; Corvus therefore cannot safely hard-code a remembered catalog. [Gloo supported models](https://docs.gloo.com/api-guides/supported-models)

#### Gloo ingestion, indexing, and retrieval

- Gloo's Data Engine accepts asynchronous file uploads, parses the content, chunks it, embeds it, and indexes it. A caller can attach one stable `producer_id` to one file for later item lookup. [Gloo upload content](https://docs.gloo.com/api-guides/upload-content)
- Gloo's chunking is automatic. It uses natural text boundaries and overlapping, roughly paragraph-sized chunks, but the chunking stage cannot be disabled, bypassed, or tuned per upload. Gloo also owns the embedding model, vectors, storage, and retrieval index. [Gloo chunking](https://docs.gloo.com/api-guides/chunking)
- Current content-management endpoints can enumerate items and statuses, resolve a `producer_id` to a Gloo item ID, inspect metadata, and hard-delete up to 1,000 items per request. Gloo describes deletion as irreversible and as purging vector-database, file-storage, and related records. [Gloo content management](https://docs.gloo.com/api-guides/manage-content)
- A Gloo Publisher is a content entity within an organization. Uploaded material is associated with a Publisher, which Gloo describes as a way to manage rights and identity by author, division, or brand. The caller must belong to the organization that owns a Publisher to manage it. [Gloo Publishers](https://docs.gloo.com/studio/manage-publishers) · [Gloo content management](https://docs.gloo.com/api-guides/manage-content)
- Gloo's standalone Search API performs semantic search over ingested Publisher content and returns snippets plus relevance metadata. Current tutorials use `POST /ai/data/v1/search`, collection `GlooProd`, a Publisher tenant, a result limit, and an optional certainty threshold. The older `/ai/v1/kallm/search` endpoint is deprecated. [Gloo Search guide](https://docs.gloo.com/api-guides/search) · [deprecated Search reference](https://docs.gloo.com/api-reference/core/search)
- Gloo's Grounded Responses endpoint combines retrieval and generation. If `rag_publisher` is omitted, it defaults to the shared `GlooGrounded` dataset; an empty value disables retrieval. If no passage passes retrieval, generation still proceeds and only `sources_returned: false` signals that the answer was ungrounded. Grounded Responses does not return citation metadata; Gloo directs callers needing citations to Grounded Completions. [Gloo Grounded Responses](https://docs.gloo.com/api-guides/grounded-responses)
- Gloo itself states that grounding does not prove the generated answer is supported. Its guidance assigns claim verification, citation checking, decline behavior, and evaluation to the application. [Gloo trustworthy-grounding guidance](https://docs.gloo.com/best-practices/trustworthy-grounded-applications)

#### Gloo costs and service constraints

- Current billing documentation says Pay-as-you-go includes model API access but not Data Engine, Content Library, Search, or Item Recommendations. Those retrieval capabilities require Pro or Enterprise. Pro is advertised at **$25/month plus usage**. [Gloo billing and plans](https://docs.gloo.com/studio/billing)
- Pay-as-you-go has a maximum $100 weekly spend limit; Pro has a maximum $800 monthly spend limit. Gloo says API access pauses when the applicable spend limit is reached. A payment method is required to activate API access. [Gloo billing and plans](https://docs.gloo.com/studio/billing)
- Responses API usage is billed at the selected model's token rates. The current Responses documentation states that Gloo adds a **5.5% Studio markup**. Grounded Responses has no separately stated retrieval charge, but injected sources count as input tokens. [Gloo Responses pricing](https://docs.gloo.com/api-guides/responses-v1) · [Gloo Grounded Responses](https://docs.gloo.com/api-guides/grounded-responses)
- Public documentation does not establish a Corvus-specific SLA, fixed rate limit, immutable-index retention promise, chunk-version contract, or stable chunk-level locator contract. Absence from the public docs is not proof that enterprise contracts cannot supply these guarantees; it means Corvus must not assume them without a reviewed agreement and live contract tests.

#### YouVersion's separate role

- Every YouVersion REST request requires an application App Key in `X-YVP-App-Key`. The official authentication page says App Keys are rate-limited and documents rate-limit headers, but it does not publish a universal numeric quota. [YouVersion authentication](https://developers.youversion.com/authentication)
- The Bible API supplies licensed Bible-version metadata, structural indexes, and passage text. Passage requests use exact Bible-version IDs and USFM-style locators and return the passage identifier, content, and human-readable reference. Bible collections are filtered by the app's accepted licenses by default. [YouVersion API usage](https://developers.youversion.com/api-usage) · [YouVersion Bible API](https://developers.youversion.com/api/bibles) · [YouVersion licenses API](https://developers.youversion.com/api/licenses)
- YouVersion Platform access is limited to noncommercial, ad-free, non-paywalled uses, and YouVersion reserves the right to revoke access when an application does not align with its mission. [YouVersion Platform signup requirements](https://help.youversion.com/l/en/article/72ghg45c41-how-to-sign-up-for-platform)
- YouVersion says Bible-version rights belong to their respective publishers or Bible societies and advises checking the applicable publisher's rules for the intended use. YouVersion does not provide a blanket right to republish all hosted content. [YouVersion copyright FAQ](https://help.youversion.com/l/en/article/o8t2xmy9q2-copyright)

These facts support YouVersion as the selected request-time Scripture display provider. They do not make YouVersion a substitute for the Tradition corpus, tradition-aware interpretation, or model-assisted synthesis.

### Repository assumptions and decisions

The following are Corvus decisions, not verified provider guarantees:

- The Answer evidence package, deterministic evidence gate, scoped Evidence gaps, and categorical Answer outcome are Corvus contracts. Gloo does not provide them. [ADR 0005](../docs/adr/0005-keep-substantive-answer-statements-inside-the-evidence-package.md)
- The repository manifest and immutable Corpus snapshot are the authority for source identity, edition, tradition-relative authority, rights, and admission. A provider deployment is supposed to be disposable derived state. [ADR 0003](../docs/adr/0003-govern-the-tradition-corpus-in-the-repository.md) · [ADR 0012](../docs/adr/0012-require-runtime-rights-for-first-class-tradition-coverage.md)
- Accepted ADR 0010 assigns Gloo two roles: Publisher-scoped semantic retrieval followed by schema-constrained analysis. It rejects Gloo's shared corpus, coarse `tradition` values, auto-routing, provider citation metadata, and model-memory fallback. [ADR 0010](../docs/adr/0010-separate-gloo-retrieval-from-structured-analysis.md)
- Accepted ADR 0009 and the product Spec choose Convex as Corvus's sole application database **and vector facility**, including rights-permitted embeddings, release-pinned traversal, and quarantined vector Discovery candidates. [ADR 0009](../docs/adr/0009-store-immutable-ontology-releases-in-convex.md) · [product Spec](../docs/theological-assistant-spec.md)
- ADR 0011 assigns YouVersion only request-time Scripture hydration after locators have been selected. It forbids storing YouVersion passage text in Convex, Gloo, logs, or durable caches. [ADR 0011](../docs/adr/0011-use-web-us-as-the-recorded-scripture-display-default.md)
- The currently accepted source-rights audit says most desired Tradition sources are not yet permitted for storage, Gloo upload, embedding, model input, or excerpt delivery. That blocks a meaningful production Gloo Publisher corpus today regardless of technical availability. [ADR 0012](../docs/adr/0012-require-runtime-rights-for-first-class-tradition-coverage.md) · [artifact-rights audit](RESEARCH_Tradition-Corpus-Artifact-Rights.md)
- Implementation readiness keeps all paid providers disabled until caller isolation, rights, redaction, quotas, and spend controls pass. Production provider spend defaults to zero. [implementation readiness](../docs/implementation-readiness.md)
- The requirement to use both APIs meaningfully came from the challenge, not from an end-user evidence need, and the published submission deadline was July 31, 2026. The product Spec restates Gloo as a maintainer preference, while the actual user stories ask for evidence, scope, graceful degradation, and provenance rather than a named inference vendor. [Gloo challenge](https://studio.ai.gloo.com/challenge) · [challenge research](RESEARCH_Scripture-Platform-Challenge-Briefs.md) · [product Spec](../docs/theological-assistant-spec.md)

### Inferences from the comparison

The following conclusions are reasoned implications, not provider promises:

1. **Gloo Search is redundant in the accepted stack.** Corvus already pays the engineering cost of exact chunk identities, source metadata, rights decisions, immutable release pins, embeddings, and vector filtering in Convex. Publishing the same corpus to Gloo creates a second derived index whose chunks and embeddings Gloo controls.
2. **Gloo's non-tunable chunking conflicts with the evidence model.** A stable item-level `producer_id` helps reconciliation, but Corvus needs exact source artifact, locator, checksum, release, and chunk identity. Because Gloo chooses overlapping chunk boundaries and documents no immutable chunk-version contract, Corvus would still need its own chunk map and source resolver. That removes much of the managed-search benefit.
3. **Gloo retrieval increases rights scope.** Upload, parsing, chunking, embedding, storage, retrieval, model input, and deletion all become third-party processing operations that must be separately authorized. The current corpus is already blocked mainly on those permissions.
4. **Gloo grounding does not reduce Corvus's hardest work.** Gloo explicitly leaves claim verification and decline policy to the application. Corvus must still resolve exact sources, validate every Evidence link, reject unsupported statements, derive outcomes, and abstain on gaps.
5. **The Responses API is useful but not unique.** Its direct model selection and JSON-schema controls fit the structured-analysis role well. However, Gloo documents it as a passthrough without the Gloo governance features that might otherwise distinguish the service. Its value is provider aggregation and challenge compliance, not theological authority.
6. **One Gloo analysis call can be meaningful without making Gloo the evidence store.** If Gloo produces the candidate structured statements from an admitted evidence bundle and the answer cannot be assembled without that candidate analysis, the integration is functionally real. Whether challenge judges consider this sufficient is a competition-interpretation risk; the public rule says “meaningfully integrated” but publishes no more precise technical threshold.
7. **YouVersion remains independently justified.** It supplies licensed, exact-edition Scripture text and metadata required by the chosen display policy. Removing Gloo does not change that role or authorize caching YouVersion text.

## Requirement-by-requirement fit

| Corvus need | Does Gloo uniquely satisfy it? | Assessment |
| --- | --- | --- |
| Exact Scripture edition and passage hydration | No | This is YouVersion's role. Gloo must not ingest YouVersion passage responses under ADR 0011. |
| Runtime-admissible Tradition sources | No | Rights and admission come from the repository manifest and Corpus compiler. Gloo cannot launder missing rights. |
| Immutable source, locator, checksum, and release identity | No documented guarantee | Corvus must own these identities regardless of provider. |
| Semantic retrieval | No | Gloo Search can do it, but Convex vector discovery and deterministic traversal are already accepted and give Corvus release-pinned control. |
| Tradition-aware scope | No | Gloo's coarse `tradition` control is insufficient and is absent from Responses; Corvus's scope/Position model is authoritative. |
| Structured candidate analysis | Yes as a capability; no as a unique vendor | Gloo Responses is a good replaceable implementation of an analysis port. |
| Claim-level evidence sufficiency | No | Gloo assigns verification to the application; Corvus's deterministic evidence gate remains mandatory. |
| Citation-complete Answer evidence package | No | This is a Corvus schema and validator responsibility. |
| Login-free user experience | Compatible, not unique | Server-side OAuth hides Gloo credentials from users, but Corvus still bears abuse and spend risk. |
| Challenge eligibility | No current requirement | The brief required a meaningful Gloo call, but submissions closed July 31, 2026. Only preservation of an already-submitted artifact could still justify it. |

## Recommended architecture without Gloo retrieval

The viable target preserves the accepted deep Investigation-module seam and removes only provider-specific duplication:

```text
question
  -> deterministic scope / obligation / Position plan
  -> immutable Ontology release traversal in Convex
  -> release-pinned, rights-filtered Convex vector discovery
  -> exact Corpus-snapshot chunk resolution
  -> bounded YouVersion passage hydration after locator selection
  -> admitted evidence bundles per Position membership
  -> StructuredAnalysisPort
       optional profile: Gloo Responses
       replacement profile: another directly contracted model endpoint
  -> deterministic statement / Citation / lineage validation
  -> Answer evidence package and Evidence graph
```

Key properties:

- Convex holds one copy of the released retrieval data and rights-permitted embeddings; no Publisher synchronization, provider chunk mapping, or provider index revocation workflow is required.
- Retrieval and evidence admission remain separate even though both use Corvus-owned data. Vector results remain Discovery candidates until exact release, source, scope, rights, and locator checks pass.
- `StructuredAnalysisPort` accepts only bounded admitted evidence and returns schema-constrained candidate statements. It exposes no model memory as evidence and records the actual provider/model/profile in Operation receipts.
- Gloo can implement that port without appearing in the public MCP interface or canonical schema. Switching providers changes an internal adapter and benchmark profile, not the three public operations.
- If no approved analysis provider exists, Corvus should return a scoped analysis Capability gap rather than delegating canonical answer construction to unverified ChatGPT narration.

This is viable because the repository already committed to the necessary alternative retrieval substrate: Convex release-pinned traversal, optional rights-permitted embeddings, and a deterministic evidence gate. A replacement analysis provider still requires a separate current contract, privacy, price, structured-output, and model-behavior review; this audit does not assume one.

## Decision recommendation

1. **Supersede ADR 0010.** Keep the conceptual separation between retrieval and structured analysis, but change the provider decision: Convex owns corpus retrieval; a replaceable `StructuredAnalysisPort` owns candidate analysis; Gloo is one adapter rather than the architectural seam.
2. **Remove Gloo as a mandatory release dependency.** If an already-submitted artifact or benchmark still justifies Gloo Responses, pin one current model and schema profile, use no `tradition`, shared corpus, auto-routing, Grounded Responses, or provider citation metadata, and validate all output as untrusted candidate data.
3. **Delete Gloo Publisher/Search prerequisites from the production release path.** Do not buy Pro or upload Tradition artifacts merely to reproduce the vector index Corvus already has to govern in Convex.
4. **Keep YouVersion as currently bounded.** Continue server-side exact-edition passage hydration, license/attribution checks, no durable passage caching, and visible degradation.
5. **Re-benchmark the simpler path.** Measure Convex retrieval recall/latency and Gloo-analysis token cost within the existing six-Position, sixteen-provider-operation, 45-second application envelope. The comparison should include a Gloo-disabled fixture profile.
6. **Record the challenge closure.** The July 31 submission deadline has passed. Remove challenge-only Gloo language from forward-looking product requirements and choose the analysis provider through a separate evidence-backed decision.

This recommendation conflicts with accepted ADR 0010 and with Gloo-specific wording in ADRs 0003, 0006, 0008, 0012, and 0013, the product Spec, implementation readiness, and `CONTEXT.md`. Those documents should not be edited silently; an explicit superseding decision ticket should update them as one coherent change.

## Open checks before implementation

- Confirm in the signed-in Gloo account whether the current plan is Pay-as-you-go or Pro and whether Search/Data Engine access is actually enabled; do not infer entitlements from historical successful Responses calls.
- Confirm whether Corvus was actually submitted before July 31 and whether an already-submitted public artifact must remain reproducible. The live page's “Registration is open” text is stale relative to its own July 31 submission-close and August 3–7 judging dates.
- Obtain the governing Gloo data-processing, retention, training-use, regional-processing, deletion, and SLA terms before sending any Tradition source text, even for analysis-only use.
- Obtain the exact current YouVersion application status, numeric quota, license set, and approved public delivery mode before launch.
- Benchmark the actual Convex retrieval path against the accepted question set before declaring Gloo Search unnecessary on performance grounds. The architectural redundancy is established; comparative retrieval quality is not yet measured.

## Primary sources

### Gloo

- [Responses API](https://docs.gloo.com/api-guides/responses-v1)
- [Grounded Responses](https://docs.gloo.com/api-guides/grounded-responses)
- [Search](https://docs.gloo.com/api-guides/search)
- [Upload Content](https://docs.gloo.com/api-guides/upload-content)
- [How Chunking Works](https://docs.gloo.com/api-guides/chunking)
- [Manage Content](https://docs.gloo.com/api-guides/manage-content)
- [Manage Publishers](https://docs.gloo.com/studio/manage-publishers)
- [Authentication](https://docs.gloo.com/tutorials/authentication)
- [Billing & Plans](https://docs.gloo.com/studio/billing)
- [Building Trustworthy Grounded Applications](https://docs.gloo.com/best-practices/trustworthy-grounded-applications)
- [Scripture in New Frontiers challenge](https://studio.ai.gloo.com/challenge)

### YouVersion

- [Platform overview](https://developers.youversion.com/)
- [API Usage](https://developers.youversion.com/api-usage)
- [Authentication](https://developers.youversion.com/authentication)
- [Bible API reference](https://developers.youversion.com/api/bibles)
- [Licenses API reference](https://developers.youversion.com/api/licenses)
- [Platform signup requirements](https://help.youversion.com/l/en/article/72ghg45c41-how-to-sign-up-for-platform)
- [Copyright FAQ](https://help.youversion.com/l/en/article/o8t2xmy9q2-copyright)
