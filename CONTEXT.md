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

**Explicit analysis scope**:
Scope the user states in the question itself, such as a named tradition, canonical collection, translation, or historical period. The Theological assistant has no belief inference, user profile, hidden personalization, or default tradition setting. Without explicit scope it simply answers from shared textual ground and labels material disagreements; it asks a clarification only when the question itself is incomplete or genuinely cannot be answered responsibly as written.
_Avoid_: Inferred beliefs, personalized theology, implicit tradition

**Answer evidence package**:
The structured result returned by the Bible Ontology MCP: relevant Scripture references and text, provenance, theological claims, interpretive positions, identified tensions, and provider-level completeness status. Gloo produces tradition-aware analysis inside this boundary; ChatGPT uses the package to present the final conversational answer. When an integration is unavailable, the package may be partial but must identify the gap and exclude or abstain from claims the missing evidence would materially affect.
_Avoid_: AI response, context blob

**Tradition source**:
An identifiable confessional, conciliar, catechetical, or scholarly source used to substantiate a claim about a theological tradition. Gloo may synthesize Tradition sources, but model memory alone is not provenance.
_Avoid_: Tradition knowledge, model knowledge

**Tradition corpus**:
The versioned, curated collection of primary documents and explicitly approved scholarship from which Tradition sources may be cited. Gloo may synthesize, compare, and identify tensions within this corpus, but arbitrary live-web material and unverified model recollection are not admissible evidence for the Challenge submission.
_Avoid_: Web search results, model bibliography

**Pastoral handoff**:
The Theological assistant's explicit redirection of a user toward qualified human clergy when a question calls for personal spiritual direction, sacramental judgment, crisis care, or an ongoing pastoral relationship. The assistant supports the handoff with relevant context but never presents itself as clergy.
_Avoid_: Pastoral advice, clergy disclaimer

**Citation surface**:
The Theological assistant's Palantir-style answer presentation in which every substantive scriptural or theological claim carries a tappable inline citation linked to the corresponding source or tool result. The same citations appear in a Sources dropdown beneath that message. Greetings, clarification questions, and purely conversational transitions do not require citations.
_Avoid_: Global bibliography, persistent sources sidebar

**Evidence component**:
The message-scoped Apps SDK component beneath an answer. It preserves the minimal Palantir-style Sources dropdown and provides an on-demand interactive graph of the analysis dependency path. Ordinary answers remain native ChatGPT prose without persistent application chrome or a permanently expanded dashboard.
_Avoid_: Persistent evidence dashboard, application shell

**Evidence graph**:
A Palantir-style interactive dependency graph showing the attributable flow from the user's question through MCP retrieval and analysis steps to cited answer statements. Users can inspect intermediate tool results and see how Scripture, Tradition, and lexical sources support, qualify, dispute, or inform named positions and conclusions. It exposes reproducible operations and evidence lineage, never private chain-of-thought or an undirected visualization of the entire Bible ontology.
_Avoid_: Hidden-reasoning transcript, ontology browser, knowledge-graph decoration

**Analysis branch**:
A rerun created from a selected Evidence graph step after the user changes an explicit input such as tradition, canonical collection, translation, or search scope. It preserves the original answer and graph unchanged while producing a separately inspectable evidence path and conclusion.
_Avoid_: Edit answer, overwrite analysis

**Original-language evidence**:
Sourced Hebrew or Greek lexical and morphological data used only when it materially changes an answer. It must enter through the Bible ontology with provenance and be presented plainly rather than improvised from model memory.
_Avoid_: Word-study insight, original-language color

**Canonical collection**:
A tradition-dependent set of scriptural books recognized as canon. The Bible ontology records collection membership explicitly; availability of licensed display text does not determine canonical status.
_Avoid_: The canon, Bible version

**Bible Ontology MCP**:
The stateless evidence service invoked by the Theological assistant. It integrates the Bible ontology, YouVersion text retrieval, and Gloo analysis to return Answer evidence packages without retaining conversation history, inferred beliefs, or pastoral situations.
_Avoid_: App backend, theology API

**Operational telemetry**:
Privacy-preserving diagnostics retained by the Bible Ontology MCP: random request identifiers, component and schema versions, provider status and latency, usage counts, evidence-shape counts, validation outcomes, result classification, and sanitized errors. User questions, answers, stable identities, IP addresses, inferred beliefs, pastoral context, raw model exchanges, credentials, and exact evidence content are excluded. Request content exists only transiently during execution; caches are source-oriented rather than conversation-oriented.
_Avoid_: Conversation logs, theological analytics

**Theological investigation**:
The primary deep MCP tool exposed to ChatGPT. Its sole user-authored input is the question as written; it does not accept or construct belief, tradition, or profile settings. It internally orchestrates Bible ontology traversal, licensed YouVersion text retrieval, and Gloo-powered structured analysis, then returns one citation-complete Answer evidence package. Explicit scope contained in the question is respected. Provider-level tools remain hidden behind this seam; separate narrow tools support source inspection and user-initiated Analysis branch reruns.
_Avoid_: Provider tool chain, API orchestration prompt

**Evidentiary abstention**:
The required response when available evidence cannot support a confident answer. The Theological assistant states what is supported, exposes the unresolved gap or competing readings, and may ask a narrower follow-up instead of smoothing over uncertainty.
_Avoid_: Refusal, fallback answer

**Deterministic evidence gate**:
The Challenge submission's release gate. Automated checks verify citation coverage, citation resolvability, claim-to-source linkage, Evidence graph integrity, provider-completeness reporting, graceful degradation, and required abstention behavior. Human clergy or scholar review is not part of the gate or runtime.
_Avoid_: Clergy approval, human-in-the-loop answering

**Faith-open posture**:
The Theological assistant's stance of treating Scripture and Christian traditions seriously on their own terms without assuming the user shares those commitments. It welcomes skeptical and academic questions, distinguishes textual evidence, historical claims, and confessional belief, and does not pressure the user toward belief.
_Avoid_: Neutral theology, apologetics mode
