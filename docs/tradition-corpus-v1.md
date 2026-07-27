# Tradition corpus v1

Issue #3 defines a small, externally curated Source spine and the minimum metadata needed to cite it responsibly. Corvus does not select a new theological canon: tradition-owned bodies establish authority, existing scholarly projects assist discovery, and the repository records the exact edition, scope, provenance, and usable rights.

## Source spine

These are anchor works, not automatically cleared runtime files. Every recognizing body and edition retains its real scope; a narrower source never silently speaks for an entire family.

| Coverage              | v1 anchor works                                                                                                                                                                      |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Shared early church   | Nicene-Constantinopolitan Creed, with textual recension and reception recorded per tradition                                                                                         |
| Catholic              | _Catechism of the Catholic Church_; underlying conciliar or papal acts enter Topic packs when a question requires them                                                               |
| Eastern Orthodox      | The first seven ecumenical councils; the 2016 Holy and Great Council documents with their actual signatory scope; OCA's _The Orthodox Faith_ as a scoped English catechetical anchor |
| Oriental Orthodox     | The first three ecumenical councils and current common declarations, each limited to its actual participating churches                                                               |
| Anglican              | The 1662 _Book of Common Prayer_, including the Thirty-Nine Articles and Ordinal                                                                                                     |
| Baptist               | Baptist World Alliance Beliefs Statement, explicitly treated as partial; member-body confessions enter Topic packs when disagreement matters                                         |
| Lutheran              | The complete _Book of Concord_                                                                                                                                                       |
| Pentecostal           | World Assemblies of God Fellowship Statement of Faith; member-body statements enter Topic packs when disagreement matters                                                            |
| Reformed/Presbyterian | Westminster Standards and the Three Forms of Unity as representative, scoped anchors                                                                                                 |
| Wesleyan/Methodist    | The United Methodist Church's four doctrinal standards: Articles of Religion, Confession of Faith, Wesley's Standard Sermons, and _Explanatory Notes upon the New Testament_         |

No secondary scholarship belongs in the Source spine. Pelikan/Hotchkiss, Denzinger, WCC Faith and Order, Schaff/CCEL, Clavis projects, and similar collections are discovery and comparison aids. Approved scholarship enters only a benchmark-driven Topic pack and cannot independently establish a tradition's doctrine.

## Lean manifest record

Each admitted source carries these nested fields in one record. A field may become a separate referenced entity later only when facts vary across editions, artifacts, or recognizing bodies.

### Identity and edition

- Stable source ID, canonical title, aliases, and source kind.
- Original language and edition language.
- Exact edition or translation, editor or translator, publisher, publication date, and edition statement.
- Stable external identifiers when available, such as URI, CTS URN, Clavis number, DS number, DOI, ISBN, or OCLC.
- Citation scheme and resolvable section or passage anchors.

### Tradition-relative authority

- Tradition family and recognizing body.
- Recognition scope and geographic or jurisdictional extent.
- Tradition-namespaced normative status, never a universal rank.
- Short authority claim and the recognizing body's official source URL.
- Adoption or promulgation date, reception state, binding extent, and signatories when relevant.

### Provenance, quality, and rights

- Canonical source URL, retrieval URL and date, content type, and checksum.
- Rights holder, license or terms URL, attribution requirements, and permitted content mode.
- Content mode: `included`, `fetch_only`, `reference_only`, or `blocked`.
- Immutable artifact version or revision, content checksum, versioned retrieval locator, and guaranteed availability window when content mode is `fetch_only`.
- Text or transcription quality, validation result, known omissions, and transformation history.

Only `included` and explicitly permitted, immutable `fetch_only` artifacts may support substantive claims. A first-class or replayable `fetch_only` artifact must have a versioned locator whose bytes are guaranteed stable through the seven-day Citation lifetime and 24-hour Replay lifetime, plus five minutes of clock skew after last issuance, an expected checksum verified on every fetch, and terms permitting every runtime use. A checksum of a mutable page is only a change detector: it does not make the page replayable. If exact bytes cannot be re-fetched for the required window, the artifact is `reference_only` for first-class evidence even when its current page is public or citable. `reference_only` retains metadata and a permitted outbound link; `blocked` cannot be used. Public availability is not permission. A validated public-domain English edition may be used when its wording is adequate, but it cannot support claims dependent on later revisions or materially uncertain translation.

## Rights-clearance release gate

ADR 0012 makes Runtime-admissible source coverage a hard production-release gate. Every guaranteed tradition family and every mandatory benchmark Position membership must have sufficient primary evidence in `included` or explicitly authorized, immutable `fetch_only` mode. `reference_only` sources do not count toward evidentiary coverage and their prose cannot enter Gloo, model input, excerpts, Citations, or the Evidence component.

Permission review covers the exact edition and artifact, acquisition and storage, transformations and chunking, provider/model processing, bounded delivery to each answer surface, links, caching, embeddings, attribution, embedded third-party material, territories, term, revocation, and deletion. Public-domain review applies to the exact translation, transcription, and acquired bytes rather than only the underlying work. The Corpus-snapshot compiler emits a coverage report and fails production publication when any guaranteed family or mandatory benchmark position depends on unavailable, expired, revoked, ambiguous, or unreviewed rights.

Fixture-first implementation continues with synthetic test sources and reviewed public-domain artifacts. Production remains blocked until the permission/acquisition workstream closes the artifact gaps recorded in [Tradition Corpus Artifact Rights](../ResearchResults/RESEARCH_Tradition-Corpus-Artifact-Rights.md).

### Corpus membership

- Corpus semantic version and manifest digest.
- Role as Source spine or named Topic pack.
- Admission date, responsible maintainer, rationale, and benchmark links.
- Inclusion, replacement, removal, and deployment-mapping history.

Released manifests are immutable. Patch versions correct non-semantic metadata, minor versions change source or topic coverage, and major versions change admission policy, authority semantics, or guaranteed tradition families. Every Answer evidence package identifies the corpus version used.

## v1 operating boundaries

- English is required for user-facing evidence. Preserve original-language identity and text when permitted, but model-generated translation is not authoritative evidence.
- Existing church or communion declarations determine authority. Maintainers verify provenance, edition, rights, citations, and product relevance; they do not approve doctrine.
- Gloo Publishers are derived retrieval indexes, never the authority or admission system of record.
- Topic packs are defined by the deterministic benchmark in Issue #8. A benchmark gap adds a versioned Topic pack or forces Evidentiary abstention.
- Coverage is representative and scoped, not exhaustive across every denomination, province, jurisdiction, or autocephalous church.

## Prior art and open work

The authority and candidate-source analysis is in [Tradition Corpus Prior Art](../ResearchResults/RESEARCH_Tradition-Corpus-Prior-Art.md); the exact-edition and rights audit is in [Tradition Corpus Artifact Rights](../ResearchResults/RESEARCH_Tradition-Corpus-Artifact-Rights.md). The remaining work is operational but release-blocking: obtain permission or independently licensed exact English artifacts, validate citation anchors and textual quality, and populate the manifest during Issue #12. Rights clearance—especially for modern Catholic, Orthodox, Anglican, Baptist, Pentecostal, Reformed, Methodist, ecumenical, and scholarly editions—is a mandatory release workstream rather than a risk accepted at launch.
