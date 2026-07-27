# Domain language

This glossary defines the workflow language used in issues, specs, tests, reviews, and commits.

| Term                   | Meaning                                                                                                                           |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| Agentic engineering    | Human-directed software delivery in which Codex implements work inside explicit architectural, testing, review, and safety rails. |
| Grill                  | A one-question-at-a-time decision dialogue that reaches shared understanding before implementation.                               |
| Wayfinder map          | A parent GitHub issue that indexes decisions for work too uncertain or large for one session.                                     |
| Decision ticket        | A Wayfinder child issue that closes when its named decision is made.                                                              |
| Implementation ticket  | A ticket that closes when a decided behavior is implemented and verified.                                                         |
| Frontier               | Open, unblocked, unclaimed decision tickets that can be worked now.                                                               |
| Fog                    | In-scope uncertainty that cannot yet be expressed as a precise decision ticket.                                                   |
| Tracer bullet          | A small end-to-end vertical slice that produces observable behavior and immediate feedback.                                       |
| Seam                   | A stable public boundary where behavior can be tested or replaced without editing internals in place.                             |
| Deep module            | A small stable interface hiding a comparatively large implementation.                                                             |
| HITL                   | Human-in-the-loop work requiring live judgment, taste, or approval.                                                               |
| AFK                    | Away-from-keyboard work that is fully specified, bounded, tested, and safe to execute unattended.                                 |
| Deterministic check    | A pass/fail tool such as a test, typecheck, formatter, build, or policy check.                                                    |
| Automated review       | A fresh Codex agent judging a pinned diff against standards or a spec.                                                            |
| Human review           | A person reading the actual diff; reading an agent summary is not a human review.                                                 |
| Capture, don't dispose | Preserve a validated prototype on a disposable branch and link it from the deciding ticket while keeping it off the main branch.  |
| Expand-contract        | Introduce a new form beside the old, migrate callers in green batches, then remove the old form.                                  |

Add product-domain terms only when they become necessary during grilling. Prefer these defined terms over synonyms.

## Theological assistant

**Theological assistant**:
An invokable ChatGPT app that answers difficult theological questions with Scripture-grounded citations, explicit provenance, tradition-aware interpretation, and honest treatment of disagreement.
_Avoid_: Bible chatbot, theology bot

**ChatGPT app**:
The Theological assistant's end-user surface, built with the OpenAI Apps SDK as an MCP-backed app. ChatGPT owns invocation and conversational narration; optional message-scoped UI components render structured evidence inline inside ChatGPT. It is not a separate consumer chat application.
_Avoid_: Standalone web app, custom chat client

**Provider access**:
The Challenge submission's login-free access model. The Bible Ontology MCP holds YouVersion and Gloo credentials server-side and the user does not create or connect another account, unless a provider's binding terms require per-user authorization. Credentials never enter tool results, component state, or ChatGPT context.
_Avoid_: User API key, provider sign-in

**Challenge submission**:
The fully built Theological assistant together with its required public code, writeup, video, and invocation surface; it is the product delivery boundary, not a reduced prototype. Completion requires the deployed MCP app to work end to end in ChatGPT Developer Mode and all competition artifacts to be public. OpenAI plugin review may be submitted but external approval does not block the competition deadline.
_Avoid_: Demo, competition prototype

**Contested question**:
A theological question for which materially different interpretive traditions reach different answers from the relevant texts. Its default answer begins with shared textual ground and then labels the significant interpretations and their evidence.
_Avoid_: Unanswerable question, controversial question

**Tradition-aware interpretation**:
An interpretation that applies an explicitly named theological tradition as a lens without presenting that lens as neutral or concealing significant disagreement. When no tradition is named, the Theological assistant does not silently select one. The Challenge submission guarantees first-class comparison across Catholic, Eastern Orthodox, Oriental Orthodox, and major Protestant families; narrower traditions are named only when explicit sources support them and their difference materially affects the answer.
_Avoid_: Neutral theology, tradition setting

**Major Protestant family**:
One of the six Protestant families guaranteed first-class coverage in the Challenge submission: Anglican, Baptist, Lutheran, Pentecostal, Reformed/Presbyterian, or Wesleyan/Methodist. Anabaptist, Adventist, Restorationist, and independent Evangelical traditions may be added when a benchmark case demonstrates the need.
_Avoid_: Protestantism, denomination

**First-class tradition coverage**:
A corpus guarantee that a tradition family has an authoritative Source spine and adequate Topic packs for every benchmarked question category. It is not comprehensive doctrinal coverage; an evidence gap requires disclosure and Evidentiary abstention from characterizing the affected tradition.
_Avoid_: Comprehensive coverage, token representation

**Tradition-relative authority**:
A source's authority as claimed by a named tradition body, expressed through its source kind, recognizing body, recognition scope, tradition-namespaced status, and cited authority claim. Authorities from different traditions have no equivalence crosswalk or shared numeric rank.
_Avoid_: Universal authority score, cross-tradition authority ranking

**Explicit analysis scope**:
Scope the user states in the question itself, such as a named tradition, canonical collection, translation, or historical period. The Theological assistant has no belief inference, user profile, hidden personalization, or default tradition setting. Without explicit scope it simply answers from shared textual ground and labels material disagreements; it asks a clarification only when the question itself is incomplete or genuinely cannot be answered responsibly as written.
_Avoid_: Inferred beliefs, personalized theology, implicit tradition

**Answer evidence package**:
The citation-complete structured result returned by the Bible Ontology MCP, containing the answer content and evidence relationships needed to validate and present one answer. It identifies its Answer outcome and Evidence gaps and excludes or abstains from propositions materially affected by missing evidence. Its proposed schema is specified in ADR 0005 and does not become canonical domain language until fixture and contract validation accept that decision.
_Avoid_: AI response, context blob

**Citation**:
A precise reference connecting a presented claim to an identifiable source, exact locator, edition or translation, and a resolvable user target when available. A Citation is neither the source's identity nor an opaque provider tool result.
_Avoid_: Source link, bibliography entry

**Evidence gap**:
Missing, partial, empty, stale, unavailable, or rights-blocked evidence that names the affected answer content or interpretive positions and requires disclosure, qualification, or Evidentiary abstention. Provider availability alone does not determine whether an Evidence gap exists.
_Avoid_: Provider error, completeness flag

**Answer outcome**:
The package-level classification Answered, Partially answered, or Abstained. It states whether the Answer evidence package is fit to present and leaves every limitation to a scoped Evidence gap rather than expressing theological truth as a numeric confidence score.
_Avoid_: Confidence score, success flag

**Tradition source**:
An identifiable primary confessional, conciliar, catechetical, canonical, or liturgical source, or an approved secondary scholarly source, used to substantiate a claim about a theological tradition. A secondary source may explain context, diversity, reception, or disputed interpretation but cannot independently establish the tradition's stated position; Gloo may synthesize Tradition sources, but model memory alone is not provenance.
_Avoid_: Tradition knowledge, model knowledge

**Tradition corpus**:
The versioned, curated collection of primary documents and explicitly approved scholarship from which Tradition sources may be cited. Gloo may synthesize, compare, and identify tensions within this corpus, but arbitrary live-web material and unverified model recollection are not admissible evidence for the Challenge submission.
_Avoid_: Web search results, model bibliography

**Approved scholarship**:
A secondary Tradition source selected from an established scholarly editorial process only when a benchmark topic requires context, reception history, or explanation of internal diversity. It cannot independently establish a tradition's stated doctrine.
_Avoid_: Gloo-approved source, model-recommended source

**Source spine**:
The small authority and discovery map of tradition-owned doctrinal anchors needed to represent every guaranteed tradition family. It is not a comprehensive historical library, and inclusion does not by itself authorize full-text runtime use.
_Avoid_: Reading list, comprehensive theological library

**Topic pack**:
A benchmark-driven extension to the Source spine containing the primary sources, and only the necessary Approved scholarship, needed to compare traditions responsibly for one question category.
_Avoid_: Topic bibliography, arbitrary document bundle

**Pastoral handoff**:
The Theological assistant's policy-controlled redirection of a user toward qualified human clergy when a question calls for personal spiritual direction, sacramental or ecclesial judgment, or an ongoing pastoral relationship. It is independent of whether the theological question was answered and is not itself a substantive theological claim; any such claim presented with it remains subject to ordinary evidence and citation requirements. Acute safety or crisis cases invoke a separate safety response and never rely on clergy as the sole emergency resource.
_Avoid_: Pastoral advice, clergy disclaimer

**Citation surface**:
The Theological assistant's Palantir-style answer presentation in which every substantive scriptural or theological claim carries a tappable inline evidence marker. The presentation distinguishes a source that directly supports the complete claim from evidence inherited through an auditable synthesis. The same source Citations appear in a Sources dropdown beneath that message. Greetings, clarification questions, and purely conversational transitions do not require citations.
_Avoid_: Global bibliography, persistent sources sidebar

**Evidence component**:
The message-scoped Apps SDK audit and exploration surface beneath the native ChatGPT answer. It preserves the minimal Palantir-style Sources dropdown plus an on-demand interactive graph of the analysis dependency path without competing with or replacing the conversational answer. The Answer evidence package remains the canonical answer data for both surfaces.
_Avoid_: Persistent evidence dashboard, application shell

**Evidence graph**:
A Palantir-style interactive view derived from the Answer evidence package's canonical relationships, showing the attributable flow from the user's question through Material operations and Citations to presented answer claims. Users can inspect how Scripture, Tradition, and lexical sources contribute to conclusions without exposing unused exploratory work, private chain-of-thought, or an undirected visualization of the entire Bible ontology.
_Avoid_: Hidden-reasoning transcript, ontology browser, knowledge-graph decoration

**Material operation**:
A retrieval or analysis operation that affects the answer by producing included evidence or by exposing a failure or empty result that requires disclosure, qualification, or Evidentiary abstention. Exploratory operations and rejected candidates that do not affect the answer are omitted from the Answer evidence package.
_Avoid_: Tool log, reasoning step

**Analysis branch**:
A rerun created from a selected replayable Evidence graph step after the user changes an explicit input such as tradition, canonical collection, translation, or search scope. It uses a short-lived integrity-protected Replay reference, preserves the original answer and graph unchanged, and produces a separately inspectable evidence path and conclusion without server-side conversation storage.
_Avoid_: Edit answer, overwrite analysis

**Replay reference**:
A short-lived, bounded, integrity-protected, self-contained value emitted by the Bible Ontology MCP with the sanitized inputs and version identities needed to replay an eligible Material operation. It contains no credentials, raw provider exchanges, private chain-of-thought, or server-side conversation key.
_Avoid_: Session ID, conversation record, workflow token

**Original-language evidence**:
Sourced Hebrew or Greek lexical and morphological data used only when it materially changes an answer. It must enter through the Bible ontology with provenance and be presented plainly rather than improvised from model memory.
_Avoid_: Word-study insight, original-language color

**Canonical collection**:
A tradition-dependent set of scriptural books recognized as canon. The Bible ontology records collection membership explicitly; availability of licensed display text does not determine canonical status.
_Avoid_: The canon, Bible version

**Bible Ontology MCP**:
The stateless MCP host invoked by the Theological assistant. It is a thin transport adapter around one cohesive Investigation module, initially deployed with that module as one executable process. It exposes only Theological investigation, Source inspection, and Analysis branch operations while keeping ontology access, YouVersion, Gloo, validation, credentials, and provider policy behind the seam.
_Avoid_: App backend, theology API

**Operational telemetry**:
Privacy-preserving diagnostics retained by the Bible Ontology MCP: random request identifiers, component and schema versions, provider status and latency, usage counts, evidence-shape counts, validation outcomes, result classification, and sanitized errors. User questions, answers, stable identities, IP addresses, inferred beliefs, pastoral context, raw model exchanges, credentials, and exact evidence content are excluded. Request content exists only transiently during execution; caches are source-oriented rather than conversation-oriented.
_Avoid_: Conversation logs, theological analytics

**Theological investigation**:
The primary deep MCP tool exposed to ChatGPT. Its sole user-authored input is the question as written; it does not accept or construct belief, tradition, or profile settings. It internally orchestrates Bible ontology traversal, licensed YouVersion text retrieval, and Gloo-powered structured analysis, then returns one citation-complete Answer evidence package. Explicit scope contained in the question is respected. Provider-level tools remain hidden behind this seam; separate narrow tools support source inspection and user-initiated Analysis branch reruns.
_Avoid_: Provider tool chain, API orchestration prompt

**Source inspection**:
The narrow read-only MCP operation that resolves a package-emitted Citation reference into rights-permitted source identity, authority, edition, locator, excerpt, and safe external target details. It never accepts an arbitrary URL or exposes a provider search interface.
_Avoid_: Web fetch, source search, provider passthrough

**Investigation module**:
The one cohesive runtime module behind the Bible Ontology MCP's three explicit operations: Theological investigation, Source inspection, and Analysis branch. Its top-level execution order is visible, its evidence-policy computations are pure where practical, and only dependencies with real live and fixture behavior receive adapters.
_Avoid_: Workflow engine, provider framework, investigation microservices

**Product runtime**:
The strict TypeScript, ESM, npm-managed Node.js code that implements the Bible Ontology MCP, Investigation module, Corpus snapshot compiler, deterministic validators and fixtures, and React Evidence component. Python remains limited to pre-existing research or archival utilities and is not a production tier.
_Avoid_: FastAPI tier, polyglot runtime, Python backend

**Evidentiary abstention**:
The required response when available evidence cannot support a confident answer. The Theological assistant states what is supported, exposes the unresolved gap or competing readings, and may ask a narrower follow-up instead of smoothing over uncertainty.
_Avoid_: Refusal, fallback answer

**Deterministic evidence gate**:
The Challenge submission's release gate. Automated checks verify citation coverage, citation resolvability, claim-to-source linkage, Evidence graph integrity, Evidence-gap reporting, graceful degradation, and required abstention inside the Answer evidence package. The Developer Mode fidelity suite must also prove that native ChatGPT narration preserves the package's substantive propositions, citation bindings, Evidence gaps, Answer outcome, and Pastoral handoff. A failing fixture blocks release rather than switching authority to the component. Human clergy or scholar review is not part of the gate or runtime.
_Avoid_: Clergy approval, human-in-the-loop answering

**Faith-open posture**:
The Theological assistant's stance of treating Scripture and Christian traditions seriously on their own terms without assuming the user shares those commitments. It welcomes skeptical and academic questions, distinguishes textual evidence, historical claims, and confessional belief, and does not pressure the user toward belief.
_Avoid_: Neutral theology, apologetics mode
