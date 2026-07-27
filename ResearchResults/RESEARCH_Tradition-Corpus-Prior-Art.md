# Tradition Corpus Prior Art for Issue #3

*Research conducted 2026-07-19 against official church and communion sources, official ecumenical archives, academic project documentation, publisher records, standards, and first-party source repositories. “Documented” statements below report what a source itself says; “Inference” statements are recommendations for Corvus.*

## Decision summary

The core theological selection has already been done by the churches themselves. Corvus should not assemble a neutral canon or rank documents across traditions. It should map each tradition's own authority claims and reception boundaries into a common operational record.

The accepted, deliberately lean scope is recorded in [Tradition corpus v1](../docs/tradition-corpus-v1.md). The broader candidate matrix below is research input, not the normative v1 source list.

No investigated cross-tradition collection combines all of the following: current tradition-owned texts, exact reusable editions, licensing, stable passage identifiers, and tradition-relative authority/recognition scope. The closest precedents solve separate layers:

1. tradition-owned constitutions, canons, formularies, confessions, catechisms, and councils identify the normative sources and their actual jurisdiction;
2. Pelikan/Hotchkiss, Denzinger, Schaff/CCEL, WCC Faith and Order, and scholarly *claves* provide high-quality discovery and comparison;
3. CatholicCorpus provides reproducible acquisition and provenance sidecars;
4. the Patristic Text Archive (PTA), Syriaca.org, and Coptic SCRIPTORIUM provide the best edition, identifier, revision, validation, and quality-state patterns.

**Inference for Issue #3:** adopt those layers and curate only the missing overlay: `tradition`, `issuing_body`, `recognition_scope`, `source_kind`, `normative_status`, a sourced `authority_claim`, and exact corpus-release membership. This is meaningful but much smaller than curating two thousand years of theology.

## Prior-art comparison

| Source/project | Documented contribution | Documented limitation | Corvus use (inference) |
| --- | --- | --- | --- |
| Pelikan & Hotchkiss, *Creeds and Confessions of Faith in the Christian Tradition* | Yale describes *Credo* as the guide volume of a four-volume work assembled through decades of translating, editing, and studying creeds ([Yale University Press](https://yalebooks.yale.edu/book/9780300109740/credo/)). | It is a copyrighted academic sourcebook, not a tradition-owned authority registry. Faithlife staff state that rights restrictions prevented licensing the set for Logos ([Faithlife forum](https://community.logos.com/discussion/comment/1016629)). | Best discovery bibliography and comparison index; license before runtime use. Never inherit its editorial selection as authority metadata. |
| Denzinger-Hünermann, *Enchiridion Symbolorum* | The 43rd Latin-English edition is a text-critical collection of official Catholic documents with introductions, indexes, stable “DS” references, ISBN 9780898707465, and coverage through Benedict XVI ([Ignatius Press](https://ignatius.com/enchiridion-symbolorum-denzh/)). | It is a copyrighted scholarly compilation, not itself a magisterial act and not a machine-readable open corpus. | Use DS identifiers and editorial apparatus for discovery/cross-checking; ingest the underlying official documents from licensable editions, or license Denzinger. |
| WCC Faith and Order | The digital edition is a numbered, century-long library containing study documents, final reports, minutes, church-union records, and official responses ([WCC](https://www.oikoumene.org/resources/publications/faith-and-order-papers-digital-edition)). *Baptism, Eucharist and Ministry* is explicitly a convergence text sent for church study and official response, not a universal confession ([WCC](https://www.oikoumene.org/resources/documents/baptism-eucharist-and-ministry-faith-and-order-paper-no-111-the-lima-text)). | Documents have different producers and reception states. Free online access does not imply redistribution rights; modern WCC publications commonly reserve rights. | Use dialogue/convergence documents as topic-pack evidence with `commission_only` or recorded reception status, never as doctrine binding every participant. |
| WCC/bilateral dialogues | An official Orthodox-Catholic consultation says its statements are issued on the commission's authority and do **not** bind either church ([Assembly of Canonical Orthodox Bishops](https://www.assemblyofbishops.org/ministries/ecumenical-and-interfaith-dialogues/orthodox-catholic/)). | “Agreed” does not mean “received as doctrine.” | Model producer, participants, dialogue level, reception by each church, and binding extent separately. |
| Schaff/CCEL | CCEL provides all three public-domain volumes of *Creeds of Christendom*, including original languages and English translations, in HTML, text, PDF, and ThML XML ([volume III](https://ccel.org/ccel/schaff/creeds3/creeds3)). ThML adds scripture references, identifiers, structural anchors, and Dublin Core metadata ([ThML 1.04](https://www.ccel.org/ThML/ThML1.04.htm)). | Schaff is a nineteenth-century editorial perspective and predates modern confessions. CCEL warns that its web editions and added content have separate rights and asks users to seek permission for republication/commercial use ([copyright policy](https://www.ccel.org/about/copyright.html)). | Useful open discovery and fallback text basis only after per-edition rights and textual accuracy checks. |
| CatholicCorpus | The project provides scripts, a generated manifest, 67,772 files, and a `_source.json` sidecar with source/upstream URL, retrieval date, license, digitizer, author, translator, editor, publisher, and year ([schema](https://github.com/CatholicCorpus/catholiccorpus/blob/main/docs/schema.md), [repository](https://github.com/CatholicCorpus/catholiccorpus)). Modern Vatican material is fetch-only because it is copyrighted ([about](https://catholiccorpus.org/about/)). | It mixes magisterial, patristic, scholastic, devotional, and reference texts without ecclesial authority, normative status, or recognition scope. Extraction quality varies. It is independent, not an official Catholic project. | Reuse the acquisition/provenance pattern and possibly public-domain inputs; do not treat collection membership as doctrinal approval. |
| Patristic Text Archive | PTA treats TEI-XML as the edition and web/print as derived presentations. Headers capture source, license, edition identifiers, external *clavis* IDs, structure, revision and annotation completeness. CTS/CapiTainS identifiers distinguish author, work, edition/translation, manuscript witness, and passage ([encoding guidelines](https://pta.bbaw.de/en/project/encoding-guidelines)). | Patristic coverage is incomplete and a critical edition's scholarly quality does not establish later ecclesial reception. | Strongest pattern for exact editions, passage citations, revision history, validation, and derived retrieval indexes. |
| Syriaca.org / New Handbook of Syriac Literature | Stable URIs distinguish entities from HTML pages and TEI records, support deprecation/redirects, and serialize relationships as RDF ([URI policy](https://syriaca.org/documentation/uris.html)). NHSL distinguishes conceptual works, witnesses, editions, translations, authors, and places under CC BY 4.0 while stating that coverage is incomplete ([NHSL](https://syriaca.org/nhsl)). | It is a scholarly identity/discovery layer, not an Oriental Orthodox authority registry. | Separate `work`, `edition_or_translation`, `digital_artifact`, and `authority_assertion`; use Syriaca URIs where available. |
| Coptic SCRIPTORIUM | Releases TEI, CoNLL-U, PAULA, relANNIS, and SGML; aggregates metadata; archives releases on Zenodo; records per-file licenses and annotation quality as `automatic`, `checked`, or `gold` ([repository](https://github.com/CopticScriptorium/corpora)). | Its purpose is linguistic/digital-humanities research. Some biblical corpora have special or share-alike licenses, and machine annotation quality varies. | Adopt explicit quality states, validated releases, and per-artifact licensing. It is a source of Coptic texts, not proof of Coptic doctrinal normativity. |
| TEI P5 | TEI requires a header that documents the digital file, source, encoding, and revisions; its schema is extensible and versioned ([TEI header](https://tei-c.org/release/doc/tei-p5-doc/en/html/HD.html), [guidelines](https://tei-c.org/guidelines/)). | TEI is a representation standard, not an authority, licensing, or corpus-governance model. | Use TEI where source structure warrants it; keep Corvus governance in a simpler manifest that can point to TEI artifacts. |
| Logos/Faithlife | Commercial Logos datasets connect licensed resources to manually curated concepts, scripture links, denominations, and systematic-theology categories ([Systematic Theology collection](https://faithlife.com/store/product/204596/systematic-theology-collection), [Cultural Ontology](https://faithlife.com/store/product/45476/lexham-cultural-ontology-supplemental-dataset)). | The products are licensed inside Logos, not documented as open reusable corpora or cross-tradition authority registries. Pelikan/Hotchkiss is not licensed there. | Useful proof that denomination/topic indexing improves retrieval, but not an ingestible source for Corvus. |

## What tradition-owned sources already decide

These facts demonstrate that `normative_status` cannot be one universal ladder.

| Family | Documented authority/recognition model | Consequence (inference) |
| --- | --- | --- |
| Catholic | The *Catechism of the Catholic Church* was promulgated as a “sure norm” and authentic reference for teaching; the 1997 Latin typical edition is the definitive text ([Fidei Depositum](https://www.vatican.va/content/john-paul-ii/en/apost_constitutions/documents/hf_jp-ii_apc_19921011_fidei-depositum.html), [Laetamur Magnopere](https://www.vatican.va/content/john-paul-ii/en/apost_letters/1997/documents/hf_jp-ii_apl_15081997_laetamur.html)). Canon law itself distinguishes divinely revealed teaching, definitive teaching, authentic non-definitive magisterium, episcopal teaching, and disciplinary decrees (canons 750–754, [Holy See](https://www.vatican.va/archive/cod-iuris-canonici/eng/documents/cic_lib3-cann747-755_en.html)). | Record the authority of each underlying act; do not flatten “Vatican document” or “in Denzinger” into one status. |
| Eastern Orthodox | OCA teaching identifies seven ecumenical councils as universally received and other councils as authoritative through reception; it also distinguishes dogmatic and alterable practical canons ([councils](https://www.oca.org/orthodoxy/the-orthodox-faith/doctrine-scripture/sources-of-christian-doctrine/the-councils), [canons](https://www.oca.org/orthodoxy/the-orthodox-faith/doctrine-scripture/sources-of-christian-doctrine/canons)). The 2016 Holy and Great Council publishes official documents in four languages, but its own record also exposes absent signatures and non-unanimous preparatory texts ([official documents](https://holycouncil.org/official-documents), [procedure](https://www.holycouncil.org/procedures)). | Reception and signatory scope are first-class fields. No patriarchate or catechetical website should silently stand for the entire family. |
| Oriental Orthodox | The 2025 declaration of the Coptic, Syriac, and Armenian patriarchs grounds their shared doctrinal position in Scripture, apostolic tradition, the first three ecumenical councils, and the Fathers ([Middle East Council of Churches](https://www.mecc.org/news-en/2025/5/20/the-full-text-of-the-common-declaration-issued-following-the-fifteenth-meeting-of-the-heads-of-fhe-oriental-orthodox-churches-in-the-middle-east)). Official Eastern–Oriental Orthodox agreed statements exist ([Syriac Patriarchate department](https://dss-syriacpatriarchate.org/second-agreed-statement-1990/?lang=en)), but acceptance and implementation have proceeded church by church. | Use first-three-council shared anchors plus church-specific liturgical/catechetical and synodal sources. Do not claim that a Middle Eastern three-patriarch declaration covers Ethiopian, Eritrean, or Malankara churches. |
| Anglican | Church of England Canon A5 locates doctrine in Scripture, compatible Fathers/councils, and especially the Thirty-Nine Articles, 1662 Prayer Book, and Ordinal ([Church of England](https://www.churchofengland.org/about/leadership-and-governance/legal-services/canons-church-england/section)). The Anglican Communion consists of autonomous provinces; ACC resolutions are consultative and require provincial reception ([Anglican Communion](https://www.anglicancommunion.org/acc-resolutions/)). | The historic formularies are a strong Church of England anchor, not a binding worldwide Anglican code. Track province and reception. |
| Baptist | The BWA calls its global statement partial and incomplete, while its constitution recognizes the autonomy of member bodies ([beliefs](https://baptistworld.org/beliefs/), [constitution](https://baptistworld.org/wp-content/uploads/2024/07/BWA-Constitution-and-Bylaws_Adopted-July-2024-FINAL.pdf)). The SBC describes its confession as a shared framework without authority over autonomous churches ([governance](https://www.sbc.net/about/what-we-do/sbc-governance/)). | A Baptist anchor must be representative and plurality-preserving, not “the Baptist confession.” |
| Lutheran | The LWF confesses Scripture as sole source/norm and the ecumenical creeds and Lutheran confessions—especially the unaltered Augsburg Confession and Small Catechism—as pure exposition, while acting only in matters member churches commit to it ([LWF Constitution](https://lutheranworld.org/sites/default/files/2024-02/lwf_constitution_en.pdf)). LCMS calls all Book of Concord texts binding for its workers and provides a public-domain 1921 translation ([LCMS](https://www.lcms.org/about/beliefs/lutheran-confessions)). | The Book of Concord is the shared doctrinal anchor; edition and denomination-specific subscription remain explicit. |
| Pentecostal | WAGF's Statement of Faith is a basis for belief, fellowship, and cooperation, while WAGF has no control over member bodies ([constitution](https://worldagfellowship.org/-/media/World-AG-Fellowship/Bylaws-Membership-Papers/WAGF-Constitution-and-Bylaws---2024-Update.pdf)). AG USA calls its Fundamental Truths essential but non-exhaustive ([AG USA](https://ag.org/en/Beliefs/Statement-of-Fundamental-Truths)). | Use a world-fellowship baseline plus member-body sources when questions expose real variation. |
| Reformed/Presbyterian | WCRC names Scripture, historic Reformed confessions, and ecumenical creeds as its basis without selecting one universal confessional book ([WCRC Constitution](https://wcrc.eu/wp-content/uploads/2026/01/WCRC-Constitution.pdf)). Member churches define different constitutional standards: PC(USA)'s Book of Confessions is constitutional; OPC calls Westminster its secondary standard; CRC explicitly distinguishes confession, confessional interpretation, binding synodical pronouncement, and pastoral advice ([PCUSA](https://pcusa.org/about-pcusa/agencies-entities/life-witness/ministry-areas/constitutional-interpretation/constitution), [OPC](https://www.opc.org/standards.html), [CRC](https://www.crcna.org/welcome/beliefs/position-statements)). | Represent Westminster, Three Forms, and modern multi-confession bodies through scoped member anchors; do not synthesize one Reformed standard. |
| Wesleyan/Methodist | UMC identifies four doctrinal standards: Articles of Religion, Confession of Faith, Wesley's Standard Sermons, and *Explanatory Notes upon the New Testament*; the first two are the foundational framework and are constitutionally protected ([UMC](https://www.umc.org/en/content/foundational-documents)). The Wesleyan Church places its Articles of Religion in constitutional law, superior to statutory acts ([Discipline](https://resources.wesleyan.org/wp-content/uploads/2021/02/DisciplineTWC-2016_CE-section.pdf)). | Use both Methodist and Wesleyan/Holiness member anchors when benchmark topics expose divergence. |

## Candidate v1 Source spine

This is a defensible **candidate**, not a claim that every runtime edition is cleared. Each row needs a rights and exact-edition decision before release.

| Coverage | Anchor set | Recognition scope and immediate caveat |
| --- | --- | --- |
| Shared early church | Nicene-Constantinopolitan Creed and the first councils, stored as distinct original-language/translation editions and mapped separately to each tradition that receives them | Do not manufacture a single “shared text”: filioque, council numbering, wording, and reception differ. PTA/Clavis identifiers can support work identity, but official tradition witnesses establish reception. |
| Catholic | 1997 Latin typical CCC plus an authorized English edition; Code of Canon Law canons 747–755 as authority semantics; topic-specific Vatican II/conciliar/papal acts added from the CCC's citations | Universal Catholic teaching reference. Vatican website content cannot be collected/reproduced beyond personal use without written authorization ([legal notes](https://www.vatican.va/content/vatican/en/legal-notes.html)); runtime ingestion needs permission or another licensed edition. |
| Eastern Orthodox | Nicene Creed and received seven councils; 2016 Holy and Great Council official documents with signatures; a named local-church teaching anchor such as OCA *The Orthodox Faith* | Seven councils have broad reception; Crete 2016 and OCA scope must remain explicit. Exact critical editions/translations and permission remain unresolved. |
| Oriental Orthodox | First three councils; current common declaration of Coptic/Syriac/Armenian patriarchs; one synodally or patriarchally issued catechetical/liturgical anchor for each of Coptic, Syriac, Armenian, Ethiopian, Eritrean, and Malankara churches | This is the largest remaining coverage gap. Digital Syriac/Coptic/Armenian corpora solve text access, not recognition. No one English family-wide normative catechism was found. |
| Anglican | Church of England 1662 Book of Common Prayer including Thirty-Nine Articles and Ordinal; Anglican Communion instruments only with their consultative status | Strong historic/provincial anchor. Add other province formularies only when benchmarks expose divergence. |
| Baptist | BWA Beliefs Statement; SBC *Baptist Faith and Message* 2000/2023; NAFWB 2016 *Treatise* | BWA is broad but partial; SBC and NAFWB expose major soteriological/polity difference but are US-heavy. A non-US member-body anchor is a desirable correction. The NAFWB PDF is copyrighted/all rights reserved ([official PDF](https://nafwb.org/site/wp-content/uploads/2022/10/2016-FWB-Treatise.pdf)). |
| Lutheran | LWF Constitution Article II; complete Book of Concord, with the LCMS-hosted public-domain 1921 Triglot translation as initial ingest candidate | The work is broadly shared; exact subscription and preferred modern translation vary. |
| Pentecostal | WAGF Statement of Faith; AG USA Statement of Fundamental Truths; General Presbytery position papers only as benchmark topic packs | World/member scope explicit; this represents Trinitarian Assemblies traditions, not all Pentecostals or Oneness bodies. |
| Reformed/Presbyterian | WCRC constitutional basis; Westminster Standards from OPC; Three Forms of Unity in the 2011 CRC/RCA translation; PC(USA) Book of Confessions only where a benchmark requires its broader confessional model | Each member source keeps denomination scope. The 2011 translation documents its source texts and use of NRSV ([CRC](https://www.crcna.org/welcome/beliefs/introduction-reformed-confessions-translation-2011)). Rights need confirmation. |
| Wesleyan/Methodist | UMC four doctrinal standards; Wesleyan Church Articles of Religion | UMC web presentation fixes the exact sermon numbering (1–52 in Jackson); pin it. Wesleyan *Discipline* allows non-commercial copying but contains separately licensed NIV quotations ([preface](https://discipline.wesleyan.org/wiki/Preface)). |

## Required manifest model

The following is inferred from the strongest combined precedents and the repository's existing ADRs.

### Identity and edition

- `source_id` (Corvus), `work_id`, `edition_id`, and `artifact_id` as separate identities.
- Stable external identifiers where available: URI, CTS URN, Clavis/CPG/BHG, DS number, DOI, ISBN, OCLC.
- Canonical title and aliases; source kind; original language; edition language.
- Exact edition/translation, editor, translator, publisher, publication date, edition statement, print basis, and witness where relevant.
- Passage/citation scheme and resolvable anchors; relationship to prior or superseded edition.

### Tradition-relative authority

- `tradition_family` and narrower `tradition_body`.
- `issuing_body`, `adopting_body`, adoption/promulgation date, and cited official act.
- `recognition_scope`: ecumenical reception, communion/world fellowship, autocephalous church/province, denomination/synod, local church, dialogue commission, or scholarly edition.
- `source_kind`: confessional, conciliar, catechetical, canonical, liturgical, doctrinal statement, dialogue/convergence, reception response, or scholarship.
- `normative_status`: a tradition-specific controlled value, never a cross-tradition numeric rank.
- Verbatim-short `authority_claim` plus official citation; `binding_extent`; signatories; reception status by body; reservations/dissent.

### Artifact provenance, rights, and quality

- Upstream canonical URL, retrieval URL/date, content type, byte length, content checksum, digitizer, and transformation history.
- Rights holder, license identifier and URL, jurisdiction/territory if relevant, attribution, commercial/RAG/redistribution permissions, and `content_mode: included | fetch_only | reference_only | blocked`.
- Transcription/OCR/annotation quality (`automatic`, `checked`, `gold`), schema version, validation result, known omissions, and whether passage anchors are original or imposed.
- Immutable revision history and redirect/deprecation record rather than identifier reuse.

### Admission and release

- Registry steward, admission date, provenance/rights/relevance rationale, benchmark/topic links, and known standpoint for scholarship.
- Corpus semantic version, manifest digest, artifact checksum, inclusion/removal history, and deployment mappings (including Gloo IDs) outside authority metadata.

## What Corvus can adopt versus must curate

**Documented reusable assets**

- Tradition bodies' own lists and declarations identify what counts and for whom.
- Public-domain LCMS Book of Concord text is explicitly reusable.
- PTA, Syriaca.org/NHSL, and much of Coptic SCRIPTORIUM provide open structured text, stable IDs, and per-file metadata.
- CatholicCorpus scripts/sidecars are reusable acquisition prior art, subject to every upstream license.
- CCEL/Schaff supplies machine-readable public-domain sourcebook material, but CCEL's own edition terms still require review.

**Corvus-only curation (inference)**

- Map church-established authority and reception into one operational schema without asserting theological authority.
- Choose and license one exact runtime edition/translation per admitted work.
- Preserve decentralized plurality and decide which member-body anchors are necessary for benchmark coverage.
- Verify citation anchors, checksums, quality, and release reproducibility.
- Admit only the minimum scholarship necessary for a Topic pack and record standpoint.

## Remaining true choices and risks

1. **Rights are the release blocker, not the reading list.** Vatican terms prohibit collection/reproduction beyond personal use without permission. WCC, modern denominational PDFs, Pelikan/Hotchkiss, Denzinger, modern Book of Concord translations, and scripture quotations embedded in confessions may carry separate rights.
2. **Oriental Orthodox English coverage is not solved by one collection.** The common three-council inheritance is clear, but family-wide current English normative editions across all six churches were not found. This requires direct verification with church bodies or specialist libraries.
3. **Eastern Orthodox reception is not reducible to publication by one see.** Signatories, later synodal reception, local-church scope, and disputed council status must remain visible.
4. **Protestant world communions often define fellowship, not exhaustive doctrine.** Their statements are excellent broad anchors but require member-body sources for contested benchmark topics.
5. **Digital availability is not edition fitness.** CatholicCorpus itself reports variable OCR; CCEL uses old translations; Corpus Corporum warns through its heterogeneous inputs; machine-readable does not mean critical, current, or authoritative.
6. **A shared-creed record can erase real differences.** Work identity, textual recension/translation, and tradition reception must be separate records.
7. **Versioning occurs at several layers.** The church document, scholarly edition, translation, digital transcription, annotation, and Corvus corpus release can all change independently.

## Resulting decision boundary

The accepted Source spine is a source-discovery and authority map, not an ingest list. A source enters v1 runtime only when an exact artifact has documented recognition scope, resolvable passage citations, sufficient textual quality, and permission compatible with the deployed product. Topic packs remain benchmark-driven under Issue #8; [Tradition corpus v1](../docs/tradition-corpus-v1.md) is the normative decision.
