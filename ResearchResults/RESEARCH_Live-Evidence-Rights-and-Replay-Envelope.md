# Live-evidence rights and replay envelope

_Decision research for Wayfinder ticket #40. Primary sources checked 2026-08-09.
This is a product-policy input, not legal advice or a determination that any
particular use is lawful._

## Resolution

An exact **Live research source** may support a Canonical answer only after
per-investigation source admission records an affirmative, artifact-specific
rights basis for every intended operation. Citation or public readability alone
does not supply that basis. The admission record must distinguish, at minimum,
the rights to acquire, retain, transform, retrieve/index, process by each model
or provider, display/quote, cite/link, cache, inspect, and replay. An unknown,
conflicting, expired, or scope-mismatched right is an Evidence gap for the
affected operation, not an implicit permission.

This is a deliberately conservative product decision. It follows the Copyright
Act's distinct reproduction, derivative-work, distribution, and public-display
rights, and the fact that the source terms sampled below license materially
different subsets of those activities. [17 U.S.C. § 106](https://www.copyright.gov/title17/92chap1.html)

## What can be generalized

### 1. Rights are an operation vector, not a source label

For each exact work, edition/translation, digital artifact, and use, record a
separate decision for:

| Operation | Admission question |
| --- | --- |
| Acquisition | May Corvus request or obtain this exact artifact by this method? |
| Identity and provenance | May it retain the minimum metadata, locator, version, retrieval time, and integrity digest needed to identify what was consulted? |
| Durable text retention | May it retain the full artifact or an exact excerpt after the request? |
| Transformations | May it normalize, OCR, segment, translate, embed, summarize, or otherwise make a derivative representation? Each transformation is separately named. |
| Retrieval/indexing | May it create and query a search index or embedding store from the text? |
| Model processing | May Corvus transmit the text/excerpt to this named external model or processor, for this purpose? Is training or provider retention forbidden, allowed, or governed by a separate agreement? |
| Display and quotation | May it return the exact text to the reader, at what amount, medium, commercial status, attribution, and edition-notice conditions? |
| Citation and target | May it expose a bibliographic identity, locator, short non-copyrightable metadata, and/or an external link? Does a trusted registry supply a safe target? |
| Cache | What may be cached, for how long, subject to what refresh, deletion, country, audience, and security conditions? |
| Inspection | May the Citation-inspection endpoint expose an excerpt or only identity/locator/target? |
| Replay | May a later branch reuse retained text, or must it re-fetch under then-current authorization? May a receipt retain a content digest or excerpt? |

`citationAllowed` therefore never implies `textDisplayAllowed`,
`embeddingAllowed`, or `externalModelProcessingAllowed`. This matches, for
example, API.Bible's separate content-integrity, attribution, and caching
requirements, and its prohibition on modification or derivative works absent
express permission. [API.Bible Terms & Conditions](https://api.bible/terms-and-conditions)

### 2. Exact artifact identity and terms version are necessary evidence

The decision applies to an exact delivery artifact, not merely a title, domain,
or tradition. Admission needs the work, edition/translation, provider or rights
holder, acquisition method, native locator, retrieval timestamp, content
integrity digest where retention is permitted, applicable contract/terms URL,
terms version or snapshot digest, rights basis, and expiry/revalidation date.
Provider terms can change; API.Bible expressly reserves changes and may suspend
or revoke access, while its licence is personal, non-exclusive,
non-transferable, and revocable. [API.Bible Terms & Conditions](https://api.bible/terms-and-conditions)

The same exact source can be `citation-only` in one package, `fetch-and-display`
in another, or `blocked` for model input. A subsequent Corpus snapshot may only
reuse a live source after its own rights review; per-investigation admission is
not corpus inclusion.

### 3. Fair use is a human legal assessment, never an automated flag

U.S. fair use is a fact-specific four-factor inquiry. Neither a fixed word,
verse, or percentage count nor an assertion that the product performs research
decides it; the Copyright Office says that ultimately a federal court decides
whether a use is fair. [U.S. Copyright Office FAQ](https://www.copyright.gov/help/faq/faq-fairuse.html)
The Copyright Office's generative-AI training report further notes that the Act
has no express text-and-data-mining exception. [Copyright and Artificial
Intelligence, Part 3](https://www.copyright.gov/ai/Copyright-and-Artificial-Intelligence-Part-3-Generative-AI-Training-Report-Pre-Publication-Version.pdf)

Accordingly, `fairUse` may be a counsel-approved, bounded rights basis with a
recorded analysis and expiry/review owner, but it is never inferred from a
retrieval result and never stands for general ingestion, embeddings, model
input, retention, or replay. If the basis is uncertain, Corvus retains only
permitted identity/locator information and treats the requested evidence mode
as unavailable.

### 4. Model processing requires both source and processor authority

Before transmitting protected live-source content to an external model, Corvus
must have source-side authorization for that processing and an approved
processor configuration. A processor's contractual handling of Customer Content
does not convey any licence in the source text: OpenAI's business agreement says
the customer is responsible for having all rights, licences, and permissions
needed to provide Input. [OpenAI Services Agreement §4](https://openai.com/policies/services-agreement/)

For an approved OpenAI API configuration, record endpoint, provider terms
version, retention mode, and training/abuse-monitoring posture. OpenAI says API
data is not used to train models without opt-in, but its default abuse-monitoring
logs may retain customer content for up to 30 days and some endpoints retain
application state; Zero Data Retention eligibility is endpoint-specific.
[OpenAI API data controls](https://platform.openai.com/docs/models/default-usage-policies-by-endpoint)
This is a processor constraint, not source permission. Consumer ChatGPT and any
other processor require their own applicable agreement and retention analysis.

### 5. A replay receipt is provenance, not a text mirror

The safe default replay record contains sanitized inputs, source/artifact and
rights-decision identities, terms-policy digest, native locator, version or
release identity, retrieval time, permitted integrity digest, operation and
provider versions, and a revalidation deadline. It excludes raw provider
payloads, protected text, credentials, user conversation content, and private
reasoning unless each is separately authorized and necessary.

At replay time, Corvus must either:

1. reuse a retained excerpt only if the original rights decision expressly
   permits retention and the replay use, the authorization remains current, and
   its provenance matches; or
2. re-fetch the exact source under then-current terms, validate identity and
   rights again, and emit a new receipt; or
3. report a scoped Evidence gap and make the node non-replayable.

Replay may reproduce the investigation path and disclose that the answer relied
on an earlier admissible artifact; it may not bypass a provider's refresh,
removal, attribution, access, cache, or model-processing restrictions. This is
especially important where a provider says cached content must be refreshed:
API.Bible's published acceptable-use terms require refresh at least every 30
days, while its FAQ describes a 30-day maximum for cached content. Treat the
stricter applicable source/contract term as controlling and retain the precise
accepted terms version. [API.Bible acceptable use](https://api.bible/terms-and-conditions)
[API.Bible FAQ](https://api.bible/faq)

## Source-specific findings that cannot be generalized away

| Source / class | Verified source fact | Corvus admission consequence |
| --- | --- | --- |
| API.Bible content | The provider grants a revocable, personal, non-transferable licence; its terms restrict copying, derivatives, redistribution, and use to create a substitute service except where expressly allowed. Its acceptable-use material requires content-integrity, per-content copyright compliance, attribution, and refresh of cached content. [Terms](https://api.bible/terms-and-conditions) | Do not scrape the public site to evade API or IP-holder terms. Admit only the contracted API/edition licence, record its cache/revalidation and attribution rules, and prohibit unlicensed corpus reuse, sublicensing, or model processing. |
| Biblica translations | Default quotation limits are not a general AI permission. Biblica states that AI/ML/LLM/chatbot use needs a valid licence expressly permitting it, and its publisher AI policy controls licensed AI use. [Permissions](https://www.biblica.com/permissions/) [Publisher AI Policy](https://www.biblica.com/publisher-ai-policy/) | A baseline quotation allowance may authorize a narrowly attributed output, not ingestion, RAG, external-model prompts, training, or replay. Require a specific AI licence before any of those modes. |
| Crossway ESV | Its standard permission conditions limit quotations, require an edition-specific notice, prohibit certain uses including commentary/reference works, and prohibit public Creative Commons publication. [Crossway permissions](https://www.crossway.org/permissions/) | Store the exact text edition and required notice. Do not characterize standard display permission as authorization to build a theological reference corpus, index, or LLM context. |
| BibleGateway | Its terms grant a personal, non-commercial, revocable access/display licence and otherwise prohibit copying, archiving, modification, translation, retransmission, and distribution except as expressly allowed; a separate quotation allowance is bounded and translation notices can differ. [BibleGateway terms](https://www.biblegateway.com/legal/terms/) | A browser-readable page and short quotation allowance do not permit it to be a persistent live-evidence corpus, cache, or model-input route. The underlying translation holder's terms may also control. |
| Official church web pages | UMC's terms prohibit automated downloading, systematic retrieval/database creation, data mining, reproduction/modification/distribution, and public/commercial use without permission. [UMC Global Terms](https://www.umc.org/content/united-methodist-church-global-terms-of-service) | Treat an official page's theological authority and its runtime rights as independent. Unless the exact artifact has affirmative permission, retain safe source metadata and an allowlisted external target only; do not pass prose to a model or expose it as an excerpt. |
| Public-domain and permissively licensed texts | eBible.org distinguishes public-domain, Creative Commons, and copyrighted translations, says the individual translation page controls, and states that its World English Bible text is public domain while reserving its name as a trademark. [eBible public-domain guidance](https://ebible.org/publicdomain.htm) [WEB copyright notice](https://ebible.org/eng-web-c/copyright.htm) | A verified public-domain or compatible licence may support durable fixture text, checksums, replay, transformation, and model processing, subject to licence attribution, trademark, edition-integrity, and jurisdiction review. It still must be identified exactly; “old” or “online” does not prove public-domain status. |

## Required admission and state rules

1. **Fail closed by operation.** A source becomes runtime-admissible only for
   the explicitly allowed operations. An unresolved operation does not taint
   permitted metadata use, but blocks statements or UI behavior needing the
   missing mode.
2. **Citation has a minimal lane.** A citation may expose source identity,
   edition, native locator, authority scope, and a registry-validated external
   `https` target when those details are permitted. An excerpt is a display
   operation and separately gated. A source URL is not blindly opened or
   provider-supplied as executable content.
3. **Embedded works split.** A confessional document's rights do not license
   embedded Scripture, translations, images, or third-party material. Each
   delivered fragment inherits its own source/edition rights decision.
4. **No rights laundering.** Search snippets, OCR, browser rendering, a model's
   recollection, a provider response, or a generated paraphrase cannot convert
   a `reference_only` source into model context, derived evidence, or display
   text.
5. **Terms drift and removal are material.** Expiry, removal, changed terms,
   revoked access, failed revalidation, or a provider/processor configuration
   change produces a rights Evidence gap and, if material to an obligation,
   prevents Material saturation.
6. **Retention follows the shortest applicable rule.** Apply the narrowest
   source, contract, processor, privacy, and product-retention constraint; make
   deletion/revalidation executable and auditable.

## Recommended decision input

Adopt the following admission contract for a Live research source:

> An admitted live artifact carries a versioned `rightsEnvelope` whose allowed
> operations are individually enumerated, attributable to a reviewed rights
> basis, bounded by scope and expiry, and checked both before execution and
> before replay. The package may retain only the minimum provenance material
> necessary for inspection and reproduce protected text only under an active
> operation-specific permission. Every other evidence use is an explicit gap.

This validates the existing distinction between `included`, `fetch_only`,
`reference_only`, and `blocked`, but refines it: those are convenience modes,
not enough rights data by themselves. `fetch_only`, for example, may permit a
request-time reader display but prohibit caching, embeddings, external-model
input, or branch replay. The `rightsEnvelope` must decide each of those.

## Open questions for counsel / provider negotiation

- Which target providers will contractually permit protected source text to be
  processed by the precise models and hosting regions Corvus uses, including
  transient abuse-monitoring or application-state retention?
- Does each publisher grant (or forbid) segmentation, embeddings, OCR,
  non-verbatim summaries, and replay from retained excerpts? A display or quote
  licence should not be treated as answering any of these.
- What jurisdictions, user locations, commercial model, and downstream
  component delivery are within each permission? Copyright, database, contract,
  privacy, and moral-rights analysis may differ by jurisdiction.
- What provider takedown, correction, revocation, and audit procedures must the
  runtime implement before first-class tradition coverage can rely on the
  provider?

