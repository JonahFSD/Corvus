# ADR-0011: Use WEB US as the recorded Scripture display default

- Status: accepted
- Date: 2026-07-26

## Context

The Investigation module discovers Scripture through translation-independent USFM identities and tradition-relative Canonical collections, but it needs an exact English edition when it hydrates and displays passage text. A translation selected without disclosure can affect wording and appear to select a theological lens. A Bible version's available books also cannot define a tradition's canon.

The authenticated YouVersion development application currently exposes eleven English editions without an additional publisher fast-track licence. YouVersion version 206, _World English Bible, American English Edition, without Strong's Numbers_ (`engWEBUS`), is marked public domain by the provider and currently exposes the broadest book inventory among those editions: the common 66-book collection plus fifteen deuterocanonical or apocryphal books. That inventory still does not cover every book recognized by every Oriental Orthodox church.

YouVersion requires displayed Bible text to carry the version's copyright attribution. The provider account is still in development, exposes no dependable numeric quota in observed responses, and has not established a general right to persist API responses. The product must therefore separate edition selection, Canonical collection membership, delivery rights, and server caching.

## Decision

Use YouVersion Bible version 206 (`engWEBUS`) as the recorded default **Scripture display edition** when the user's question does not name a translation. This is a neutral operational default for hydrating English display text, not a tradition-bearing Canonical collection, preferred interpretation, critical-text judgment, or source-authority claim.

### Selection order

For each requested Scripture locator:

1. If the question or an explicit Analysis-branch delta names a translation, resolve only that requested edition through the version registry.
2. Otherwise, record `engWEBUS` version 206 as the effective Scripture display edition.
3. Confirm at request time that the selected edition is enabled and contains the requested USFM book and locator.
4. If it does, retrieve the bounded passage from YouVersion and validate the response identity.
5. If it does not, return a scoped Evidence gap or ask a necessary narrowing question. Never select another edition silently.

An unavailable explicitly requested translation remains a visible unresolved or unsatisfied constraint. The runtime does not substitute WEB, accept a publisher licence, or infer that a similarly named edition is equivalent. If the requested edition or its wording is material to an Answer obligation, that obligation remains unsupported.

### Canon and interpretation independence

Ontology and Analysis-scope policy select Canonical collections before display hydration. The union of supported collections drives unscoped discovery under ADR 0005. A version's `books` inventory is only a delivery-capability check; it cannot include or exclude a book from any tradition's canon.

If a required canonical book is absent from version 206, the product discloses that YouVersion display-text gap and may still cite an independently admitted source or exact reference when its rights and evidence policy allow. It cannot hide the book, replace it with a different work, or treat unavailable English display text as proof that the book is noncanonical.

A Textual observation may accurately describe wording visible in the selected edition and must name that edition. A substantive claim whose force depends on a materially disputed translation cannot rely on the default edition alone. It requires rights-cleared comparison, textual-critical or Original-language evidence appropriate to the claim, and disclosure of the material variation. Multiple translations are witnesses to translation choices, not independent proof of an interpretation.

### Version registry and citations

Maintain a versioned, deployment-time YouVersion registry entry for every enabled edition. At minimum it records:

- provider version identifier, abbreviation, full title, language tag, and observed book inventory;
- copyright and promotional attribution returned by the API;
- YouVersion version and passage-link templates;
- the reviewed licence or access basis, attribution requirements, permitted delivery surfaces, and server-retention policy;
- registry observation time, verification status, and the release versions that admit it.

The release process rechecks version 206's identity, public-domain designation, book inventory, passage behavior, and deep-link construction. A material mismatch blocks release rather than causing a dynamic fallback.

Every delivered Scripture excerpt and Citation identifies the exact edition, USFM locator, human-readable reference, required attribution, and a registry-derived safe HTTPS target when available. YouVersion is recorded as the delivery provider, not as the translation's theological authority or the source of Canonical collection membership. Provider strings and returned HTML remain untrusted and are bounded and sanitized before model or component delivery.

### Content handling and degradation

Fetch YouVersion passage text server-side only after retrieval has selected a bounded set of locators. Hold it in request memory and in the rights-permitted Answer evidence package delivered for that message; do not retain it in server logs, Operational telemetry, Convex, Gloo indexes, durable caches, or Replay references. A branch may rehydrate text during the Replay reference's 24-hour lifetime only under the recorded version registry entry and the then-current denylist and rights policy. The release process admits an edition only when the provider contract and registry mapping can preserve that identity for the full replay window; otherwise the affected receipt is non-replayable and no branch control is rendered.

Durable caches may contain version identifiers, book inventories, copyright metadata, safe link templates, request-independent capability metadata, and other non-content registry data. Public-domain status alone does not authorize Corvus to republish a cached YouVersion response outside the provider contract. A future release may ingest an independently acquired public-domain WEB artifact under its own provenance and rights record, but that would be a Corpus-snapshot decision rather than a YouVersion cache.

Timeouts, `404`, `422`, rate limits, unavailable versions, malformed provider payloads, and missing books produce a Scripture-retrieval Capability report and a scoped Evidence gap. They never hide an affected Citation or component silently, manufacture verse text from model memory, or fall back to another edition. Required obligations and package outcome follow ADR 0005.

Use the server-side REST adapter with an `X-YVP-App-Key` held in deployment secrets and a deterministic fixture adapter. The caller and Evidence component never receive the key. Production release also requires the YouVersion application to be approved for the intended public access mode and its current terms and quotas to be reverified.

## Rejected alternatives

- Use the 66-book Berean Standard Bible because it is the simplest modern public-domain edition.
- Use the Catholic Public Domain Version for all deuterocanonical material and a Protestant edition elsewhere without disclosing the switch.
- Let the first available YouVersion edition or the user's prior YouVersion preference choose the text.
- Treat a YouVersion edition's book inventory as the Canonical collection.
- Accept publisher fast-track licences automatically during runtime or deployment.
- Persist API Scripture text merely because an edition is marked public domain.
- Hide Scripture cards or omit gaps when YouVersion retrieval fails.
- Use model-reconstructed or paraphrased verse text as if it were a retrieved edition.

## Consequences

Implementers have one deterministic English display default with broad current book coverage, while users can still request a specific available translation explicitly. Every package makes edition selection visible. Canonical collection, textual evidence, interpretation, and provider delivery remain separate concerns.

Some broader Canonical collections will lack display text, and some users will request editions not currently licensed. The product must expose those limitations instead of smoothing them over. Runtime hydration adds provider latency and availability risk because server-side Scripture-text caching remains disabled. Fixture, live-contract, rights, attribution, and Developer Mode tests must prove that these cases degrade honestly.
