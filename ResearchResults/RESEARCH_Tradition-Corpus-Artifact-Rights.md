# Tradition-corpus artifact and rights release audit

_Primary-source audit checked 2026-07-26. This is an admission and release
audit, not an authority ranking or a new theological canon._

## Cross-cutting conclusion

The Source spine identifies authoritative works and recognition scope, but it
does **not** presently supply a complete rights-cleared runtime corpus. The
release rule follows [Tradition corpus v1](../docs/tradition-corpus-v1.md):
only `included` and explicitly permitted `fetch_only` artifacts may support a
substantive runtime claim. A publicly readable official page is not permission
to retain, embed, send to a model, or display it to the user.

Therefore `reference_only` records are still valuable: they preserve exact
work and edition identity, recognizing-body claim, locator, and safe external
target for Source inspection. They are **authority metadata**, not admissible
runtime evidence. They must never be used as a back door through provider
snippets, Gloo retrieval, model memory, embeddings, scraping, or an uncited
paraphrase. If no independently admitted artifact supports a required
Position membership, the package carries a scoped Evidence gap and performs
Evidentiary abstention.

At the date checked, the clearest `included` candidate is the LCMS-provided
public-domain 1921 *Book of Concord*. A counsel-reviewed, independently
acquired public-domain scan/transcription of Percival's 1900 council volume is
also feasible, but should begin as a fixture/discovery artifact until its
exact artifact and redistribution basis are admitted. All current modern
official pages and PDFs below are conservatively `reference_only` pending
written permission for storage, retrieval, model input, bounded excerpts,
component delivery, transformations/embeddings, and external targets.

All source-document Scripture is separately governed. A confessional or
catechetical work's rights do not license its embedded Bible text; Bible
references may be retained, while user-facing Scripture remains subject to
ADR-0011's edition registry and request-time delivery policy.

## Release method required for every admitted artifact

- Record distinct `work`, `edition_or_translation`, `digital_artifact`, and
  `authority_assertion` identities, as required by ADRs 0003 and 0004.
- Pin a retrieved artifact by byte length, media type, retrieval time, SHA-256
  (and preferably SHA-512), upstream URL, edition statement, rights decision,
  transformation provenance, and Corpus snapshot digest. A mutable URL is not
  a release identifier.
- Use native locators (paragraph, article, canon, session, question, sermon,
  or verse) before PDF-page locators. A page number is display metadata, not
  the only Citation key.
- Attribute authority only to the named recognizing body and recognition scope.
  No current source establishes a cross-tradition numeric authority ranking.
- Treat the following modes exactly: `included` = retained and delivered under
  affirmative rights; `fetch_only` = explicitly authorized request-time
  retrieval/delivery with no unauthorized durable text store; `reference_only`
  = metadata and safe link only; `blocked` = no usable runtime record.

## Shared early church and Oriental Orthodox

| Work / exact artifact | Authority and scope | Locators, reproducibility, and rights decision | Gap or acquisition |
| --- | --- | --- | --- |
| Nicaea 325, Constantinople 381, Ephesus 431 — H. R. Percival, trans./ed., *The Seven Ecumenical Councils of the Undivided Church*, NPNF Series II vol. XIV, 1900 | The translation is a scholarly/public-domain delivery artifact, not an ecclesial authority or critical normative recension. Each council and every body's reception must be recorded separately. | The [Internet Archive item](https://archive.org/details/sevenecumenicalc00perc) supplies an OCR text and scan data; observed OCR SHA-1 is `8959a923a0e74cf4e1bdd13852735bc0003d4fd9`. Cite council + document/session/canon/definition + printed page. A Corvus transcription must be checked against the scan and assigned SHA-256. CCEL's [HTML/PDF](https://ccel.org/ccel/schaff/npnf214/npnf214.) is a useful comparison, but CCEL terms require separate review. | `included` only after a jurisdiction/redistribution review of an independently acquired 1900 scan and verified transcription. Preserve historical embedded biblical wording as source text only; it does not replace separate Scripture evidence. Do not call it an official English Oriental Orthodox text. |
| Coptic reception: [Holy Synod, “The Ecumenical Councils”](https://copticorthodox.church/en/holy-synod/ecumenical-councils/) | Coptic Orthodox Church; explicitly names Nicaea, Constantinople, and Ephesus as the three councils received by the Coptic Church and Oriental Orthodox family. | HTML heading/paragraph locators are stable enough for metadata, but no stated reuse grant or release artifact was found. | `reference_only`; seek Holy Synod permission for an exact English source artifact. |
| Armenian reception: [Mother See of Holy Etchmiadzin overview](https://www.armenianchurch.org/en/Overview) | Mother See of Holy Etchmiadzin / Armenian Apostolic Holy Church; it identifies acceptance of the three councils. It is distinct from the Holy See of Cilicia. | HTML heading/paragraph locators; no reusable edition or licence found. | `reference_only`; permission and a named promulgated English artifact are needed. |
| 2025 Common Declaration, [MECC publication](https://www.mecc.org/news-en/2025/5/20/the-full-text-of-the-common-declaration-issued-following-the-fifteenth-meeting-of-the-heads-of-fhe-oriental-orthodox-churches-in-the-middle-east) | Signed by Pope Tawadros II, Mor Ignatius Aphrem II, and Catholicos Aram I; it affirms the three councils and Fathers. Its scope is the three named Middle-East heads/churches, not Ethiopian, Eritrean, Malankara, or automatically Etchmiadzin. | Dated HTML with paragraph locators, but no reuse licence. It includes an un-cleared modern English Bible quotation. | `reference_only`; obtain MECC/signatory permission before any model or component use. |
| Syriac: [Patriarchate department, 1990 Second Agreed Statement](https://dss-syriacpatriarchate.org/second-agreed-statement-1990/?lang=en) | Dialogue commission/signatory scope only; an agreed dialogue text is not automatically received doctrine. | Official HTML but no stated reusable release. | `reference_only`; seek a Syriac Patriarchate catechetical, liturgical, or synodal English artifact and explicit rights. |
| Ethiopian: [Nicene Creed](https://www.ethiopianorthodox.org/english/dogma/niceancreed.html) and [faith page](https://www.ethiopianorthodox.org/english/dogma/faith.html) | The pages identify a Holy Synod-published 1983 *Short History, Faith and Order*, but do not establish the displayed English text's exact edition/translator. | Fetchable HTML, no official downloadable source edition, release ID, or reuse grant. | `reference_only`; obtain a Holy Synod-authorized English edition and rights for retrieval/delivery. |
| Eritrean: [US/Canada diocesan “Our Churches” page](https://english.eritreantewahdo.org/our-churches/) | Diaspora diocesan descriptive scope only; it is not an Eritrean patriarchal/synodal doctrinal edition and does not furnish a council/creed text. | HTML only; no authoritative English doctrinal artifact or reusable licence found. | No runtime Tradition source. This is an explicit first-class-coverage Evidence gap pending Patriarchate/Holy Synod acquisition. |
| Malankara: [“What do we believe?”](https://mosc.in/the_church/what-do-we-believe/) and [Christology](https://mosc.in/the_church/theology/christology/) | Malankara Orthodox Syrian Church only. The prose acknowledges the Niceno-Constantinopolitan Creed but is not a dated promulgated English catechism. | Fetchable official HTML, no versioned text release or permission. | `reference_only`; acquire a Catholicos/synodal English liturgical or catechetical edition and written rights. |

**Oriental Orthodox release finding:** the common three-council inheritance is
well evidenced, but no rights-cleared English family-wide catechism was found.
The source spine cannot claim first-class coverage until Coptic, Armenian,
Syriac, Ethiopian, Eritrean, and Malankara sources cover the benchmarked
positions individually where their difference is material.

## Catholic and Eastern Orthodox

| Work / exact artifact | Authority and scope | Locators, reproducibility, and rights decision | Gap or acquisition |
| --- | --- | --- | --- |
| *Catechism of the Catholic Church* — definitive identity: *Catechismus Catholicae Ecclesiae*, 1997 Latin typical edition; English candidate is the 1997-modified English edition | [*Fidei Depositum*](https://www.vatican.va/content/john-paul-ii/en/apost_constitutions/documents/hf_jp-ii_apc_19921011_fidei-depositum.html) calls it a sure norm/authentic reference; [*Laetamur Magnopere*](https://www.vatican.va/content/john-paul-ii/en/apost_letters/1997/documents/hf_jp-ii_apl_15081997_laetamur.html) promulgates the Latin typical edition. Catholic scope, not a generic Christian source. | Cite `CCC` paragraph number, with part/section/chapter/article display metadata. Official browse sources are [Vatican](https://www.vatican.va/archive/ENG0015/_INDEX.HTM) and [USCCB](https://www.usccb.org/sites/default/files/flipbooks/catechism/755/). Holy See [legal notes](https://www.vatican.va/content/vatican/en/legal-notes.html) and USCCB policy do not clear corpus use. | `reference_only`; obtain LEV/USCCB permission covering the exact English artifact, bounded dynamic excerpts, model use, caching/embeddings, and user delivery. Inventory all embedded Scripture separately. |
| First seven Ecumenical Councils | OCA [“The Councils”](https://www.oca.org/orthodoxy/the-orthodox-faith/doctrine-scripture/sources-of-christian-doctrine/the-councils) identifies their Orthodox reception. OCA is a local autocephalous witness; it must not become a universal proxy. | Use the Percival artifact above with council/document/session/canon locators. | `reference_only` in production unless the independent public-domain inclusion decision above is accepted. No pan-Orthodox official English primary-text artifact was found. |
| Holy and Great Council, Crete 2016 — [official documents](https://www.holycouncil.org/official-documents) | Official document set of participating Churches; never call it the position of all Eastern Orthodox. Antioch, Russia, Bulgaria, and Georgia did not attend. | Cite document slug + title + section + paragraph ordinal. The official site is owned by the Ecumenical Patriarchate and reserves rights; it is technically hashable but no licensed release artifact was found. | `reference_only`; seek written permission from the Ecumenical Patriarchate/HGC covering retrieval, model input, excerpts, and display. |
| OCA, Fr Thomas Hopko, [*The Orthodox Faith*](https://www.oca.org/orthodoxy/the-orthodox-faith) | Scoped OCA English catechetical anchor; not an undifferentiated Eastern Orthodox authority. | Cite volume/part/chapter/heading/paragraph at the stable OCA article URL. OCA footer is all rights reserved, with no content licence or release manifest. | `reference_only`; obtain OCA permission. Embedded Scripture excerpts require independent provenance/rights. |

## Anglican, Baptist, and Lutheran

| Work / exact artifact | Authority and scope | Locators, reproducibility, and rights decision | Gap or acquisition |
| --- | --- | --- | --- |
| Church of England, 1662 *Book of Common Prayer* — [official hub](https://www.churchofengland.org/prayer-and-worship/worship-texts-and-resources/book-common-prayer), [official PDF](https://www.churchofengland.org/sites/default/files/2019-10/the-book-of-common-prayer-1662.pdf) | [Canon A5](https://www.churchofengland.org/about/leadership-and-governance/legal-services/canons-church-england/section) identifies Articles, BCP, and Ordinal as particular Church of England doctrine sources. It is not a binding worldwide Anglican code. | Use Articles I–XXXIX, named service/rubric, Psalm/verse, and Ordinal form locators. Observed PDF: 2,323,533 bytes, SHA-256 `d1eefa738f9e1ef3d877ed3beab063db41ffd7f9d3c6ca13ec8c8eb9a82c80a1`. Crown/CUP rights and the [copyright notice](https://www.churchofengland.org/help/copyright) do not grant production corpus rights. | `reference_only`; obtain Crown Patentee/CUP permission. KJV/Authorized Version and Coverdale Psalter material are separately governed. |
| Baptist World Alliance, [Beliefs Statement](https://baptistworld.org/beliefs/) | Its own text calls it partial and incomplete; the [2024 Constitution](https://baptistworld.org/wp-content/uploads/2024/07/BWA-Constitution-and-Bylaws_Adopted-July-2024-FINAL.pdf) describes an independently governed covenantal fellowship, not a creedal authority. | Cite §§1–17. Mutable HTML has observed SHA-256 `d34331b40f45537691065860123c9fd4e77cb87ad0780625f874e3252e726c8a`; no dated official release artifact or content license. | `reference_only`; obtain BWA permission/datable release. It cannot represent all Baptist doctrine. |
| Southern Baptist Convention, [*Baptist Faith & Message*](https://bfm.sbc.net/wp-content/uploads/2024/08/BFM2000.pdf), adopted 2000, amended 2023 | SBC only; its preamble calls confessions revisable guides without authority over conscience, and local churches are self-governing. | Cite Preamble and Articles I–XVIII. Observed SHA-256 `02c17d2c066a64353a88330531e667be2e2c108e1250cff62a1a4d0c1b481c3c`, Last-Modified 2024-08-01, ETag `66abce23-37f40`. No corpus/model licence found. | `reference_only`; seek SBC licence. Use embedded Bible references, not unlicensed quoted wording. |
| NAFWB, [*Treatise* (2016)](https://nafwb.org/site/wp-content/uploads/2017/01/2016-FWB-Treatise.pdf) | National Association of Free Will Baptists only; its preface/Part IV preserve fellowship and local-church variation. | Cite Part/chapter and Articles of Faith; observed SHA-256 `2b7acede6639669d55aa7783280ba5e33d39566cafa55ba0691911a5338794d1`. Explicit © 2016 NAFWB, all rights reserved. | `reference_only`; written NAFWB licence required. |
| Complete *Book of Concord*, [LCMS public-domain Triglot source set](https://www.lcms.org/about/beliefs/lutheran-confessions?theme=wiki), *Triglot Concordia*, 1921 | LCMS says it unconditionally subscribes to the complete Book; this establishes LCMS scope, not universal Lutheran subscription. LWF constitutional evidence has narrower stated scope. | Cite canonical document/article/paragraph. LCMS says these 1921 texts are public domain and may be copied/distributed freely. Example observed hashes: Augsburg `4a2de3fff7ac4f3718307520c18859e6fd3d8c655af710c1589085509bd85c59`; Apology `ec305901e6c5d87b8641c19efc45748ede92aca9c8c00ae071e9e8f94795ab73`. | `included`, subject to per-file capture, QA, paragraph map, and release digest. Do not substitute the modern CPH [online edition](https://bookofconcord.cph.org/), which is © 2005/2006 and `reference_only`. |
| LWF Constitution, [Article II](https://lutheranworld.org/sites/default/files/2024-02/lwf_constitution_en.pdf) | LWF/member-church constitutional scope; identifies Scripture, ecumenical creeds, and confessional relationship but does not make full Book-of-Concord subscription universal. | Cite Article/subparagraph and PDF page; no reusable licence established. | `reference_only`; obtain LWF permission if prose is needed at runtime. |

## Pentecostal, Reformed/Presbyterian, and Wesleyan/Methodist

| Work / exact artifact | Authority and scope | Locators, reproducibility, and rights decision | Gap or acquisition |
| --- | --- | --- | --- |
| WAGF [Statement of Faith, Updated 2024 PDF](https://worldagfellowship.org/-/media/World-AG-Fellowship/Bylaws-Membership-Papers/WAGF-Statement-of-Faith---Updated-2024.pdf) | A basis for belief/fellowship/cooperation for WAGF members; the [Constitution](https://worldagfellowship.org/-/media/World-AG-Fellowship/Bylaws-Membership-Papers/WAGF-Constitution-and-Bylaws---2024-Update.pdf) says WAGF is cooperative and has no member governance. Not all Pentecostals or Oneness Pentecostals. | Cite doctrines 1–11 or Constitution Art. II. [Terms](https://worldagfellowship.org/Terms-of-Use) reserve site content and allow only incidental church/personal copying; no immutable artifact ID. | `reference_only`; request WAGF permission. It uses Bible references rather than quoted Scripture, but still lacks a runtime text licence. |
| OPC Westminster Confession/Larger and Shorter Catechisms — [WCF](https://opc.org/wcf.html), [LC](https://opc.org/lc.html), [SC](https://opc.org/sc.html) | Orthodox Presbyterian Church secondary-standard scope only, subordinate to Scripture; not universal Reformed/Presbyterian authority. | Cite WCF chapter.paragraph or catechism question. OPC copyrighted presentation and proof-text edition lack reuse licence; proof text includes KJV quotations. | `reference_only`; acquire OPC rights or admit a separately verified historical public-domain edition without silently substituting it for OPC's constitutional form. |
| CRC/RCA 2011 Three Forms — [Belgic](https://www.crcna.org/welcome/beliefs/confessions/belgic-confession), [Heidelberg](https://www.crcna.org/welcome/beliefs/confessions/heidelberg-catechism), [Canons of Dort](https://www.crcna.org/welcome/beliefs/confessions/canons-dort) | CRC and RCA approved the joint translation; PC(USA) participated for Heidelberg only. Preserve denominational differences, including Belgic 36. | Cite article, Q&A, or Head/Rejection. The [translation introduction](https://www.crcna.org/welcome/beliefs/introduction-reformed-confessions-translation-2011) identifies its 2011 basis; its PDF notice reserves rights and uses NRSV quotations in parts. | `reference_only`; permission from Faith Alive/rights holder is required. |
| UMC [Articles of Religion](https://www.umc.org/en/content/articles-of-religion) and [Confession of Faith](https://www.umc.org/en/content/confession-of-faith) | Each is one of the UMC's four doctrinal standards; scope is UMC, not every Methodist/Wesleyan body. | Cite Article I–XXV or Confession Art. I–XVI. Current pages derive from Book of Discipline editions and are copyrighted by United Methodist Publishing House. UMC [terms](https://www.umc.org/en/content/united-methodist-church-global-terms-of-service) prohibit extraction/data-mining and public reuse. | `reference_only`; obtain UMPH/UMC permission. |
| Wesley's Standard Sermons 1–52 — [UMC/ResourceUMC index](https://www.resourceumc.org/en/topics/history/john-wesley-sermons/numeric-index) (1872 presentation) | UMC identifies precisely these 52 Jackson-numbered sermons as a standard; scope is UMC. | Cite sermon number/title/paragraph. The historical work is plausibly public domain, but the current transcription has no affirmative reuse licence. | `reference_only` for current presentation. A separate verified 1872 scan/transcription may become `included` after rights, textual QA, checksum, and Scripture-quotation review. |
| Wesley, *Explanatory Notes upon the New Testament* — [NNU/Wesley Center index](https://wesley.nnu.edu/john-wesley/john-wesleys-notes-on-the-bible/) | UMC names it the fourth standard; NNU is a delivery host, not the recognizing body. | Cite book.chapter.verse plus exact edition/transcription. Original work is 1755 but the online edited text/modern Bible material has no affirmative corpus licence. | `reference_only`; select and verify a public-domain source scan, remove or independently clear biblical text, and obtain any required modern-transcription permission. |

## Coverage and permission backlog

1. **Runtime admission is the release blocker.** Every guaranteed family needs
   admissible primary evidence for its benchmarked positions. `reference_only`
   pages do not satisfy first-class tradition coverage.
2. **Oriental Orthodox is the largest gap.** Secure one scoped, English,
   primary catechetical/liturgical/synodal artifact for each Coptic, Armenian,
   Syriac, Ethiopian, Eritrean, and Malankara body; the three-head declaration
   is not a substitute.
3. **Plural families require scoped Topic packs.** BWA does not represent SBC
   or NAFWB; WAGF does not represent all Pentecostalism; OPC Westminster and
   CRC/RCA Three Forms do not speak for all Reformed/Presbyterian bodies; UMC
   does not cover Wesleyan/Holiness bodies; Church of England formularies do
   not bind autonomous Anglican provinces.
4. **Each permissions request must explicitly cover** server retention,
   Publisher/Gloo ingestion, model input, extraction, chunking, embeddings,
   bounded answer and component excerpts, attribution, safe external links,
   checksum storage, and the intended public Challenge-submission territory.
5. **No silent fallback.** When acquisition is incomplete, fixture work can
   continue with admissible public-domain artifacts, but a production answer
   must emit its Evidence gap and abstain from the affected characterization.

