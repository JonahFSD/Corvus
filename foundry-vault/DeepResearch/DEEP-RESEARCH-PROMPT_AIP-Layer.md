# Deep Research Prompt — Reverse-Engineering Foundry's *AIP* (AI) Layer

**What this is:** the fifth in the set. Its single job is to reconstruct, as exhaustively as the public record allows, how Palantir's **Artificial Intelligence Platform (AIP)** connects LLMs and agents to the Ontology as *governed tools* — AIP Logic, Agent/Chatbot Studio, AIP Evals, the model gateway, and the tool-calling/permission model.

**How to use it:** paste everything below the line into any deep-research tool. Tool-agnostic. Keep role, scope, question bank, methodology, and output spec; trim the seed list if input is tight.

**Scope note:** the AIP *layer* — how AI is built, governed, and wired to the Ontology. The Ontology, app, and security layers are covered separately and are out of scope except where AIP *binds* to them (actions/functions as tools, agent widgets, the permission model).

---

# ▼▼▼ PASTE FROM HERE ▼▼▼

## Role

You are a senior AI-platform architect and reverse-engineer specializing in LLM application frameworks, agent/tool-calling systems, retrieval-grounded generation, and AI evaluation harnesses. You are rigorous, source-driven, and allergic to marketing language. Your task is to reconstruct the internal design of **Palantir's AIP** — specifically **AIP Logic**, **AIP Agent Studio / Chatbot Studio**, **AIP Evals**, the **model gateway**, and the mechanism by which Ontology **actions and functions become governed tools** for LLMs and agents.

## Objective

Produce an **exhaustive, citation-backed technical reconstruction** of how AIP lets builders create LLM-backed functions, agents, and evaluations grounded in the Ontology and executed within the platform's permission model — detailed enough that a competent team could use it as the functional-and-architectural reference to build a faithful clone of the AI layer. **Prioritize concrete mechanics** (the Logic block/prompt/tool/output model, the tool taxonomy and tool-calling contract, agent configuration and state, the evals scoring model, the model gateway, and the AI permission/governance model) over conceptual or promotional description.

## Precise scope

**In scope:**
- **AIP Logic** — the no-code builder for LLM-powered **functions**: the **block** model (prompt + tools + output), the documented **tool categories** (data, logic, action), prompt configuration, structured/typed **output**, and publishing Logic as a function.
- **AIP Agent Studio / Chatbot Studio** — building and managing **agents**: configuration (model selection, **temperature**), the **tool** set an agent can use (object query, function, apply-action, update-variable), conversation/session state and memory, retrieval/grounding, and publishing an agent as a function/API.
- **The tool model** — how an Ontology **function** or **action** becomes a callable **tool**; the tool-calling contract; how the LLM *asks* and the platform *executes* the tool within the invoking user's permissions; native tool calling.
- **AIP Evals** — evaluation suites: test cases/datasets, metrics/scorers, how agents/functions are evaluated and benchmarked, and how evals integrate with publishing/Automate.
- **The model gateway / governed model access** — the set of available LLMs/multimodal models, model selection, governance/auditing of model calls, rate/limit handling, and where inference runs (incl. any NVIDIA/partner acceleration).
- **Grounding & retrieval** — how AIP grounds generations in Ontology data (object queries, **vector** properties / semantic search, RAG-style retrieval, media/multimodal).
- **Governance, safety & lineage** — the AI permission model (edits only via **actions**; tools run in the user's permissions), auditing/lineage of AI operations, evaluation gating, prompt-injection / safety posture.
- **In-platform AIP** — AIP **widgets** in Workshop (the AIP Agent widget), AIP transforms in Pipeline Builder, **AIP Assist** (in-platform helper), and AIP + **Automate**.
- **APIs/SDK & internal architecture** — agent/Logic invocation APIs and the named internal services (verify).

**Out of scope** (touch only at the seam): the underlying foundation-model internals (not Palantir's); the Ontology internals (objects/actions/functions — already reconstructed); the app layer (covered — but the AIP Agent widget is the seam); the security layer (covered — but the AI permission model is the seam); Apollo.

## Research question bank

Answer every question you can substantiate; record the rest as known unknowns.

**A. AIP Logic**
1. The **block** model — how a Logic function is composed of a **prompt**, **tools**, and an **output**; supported block types; control flow.
2. **Prompt** configuration — variables/templating, system vs user content, grounding inputs.
3. **Output** — structured/typed outputs, how they map to Ontology types and downstream consumers; publishing Logic as a function.

**B. The tool model & tool-calling**
4. The documented **tool categories** (data, logic, action) — what each can do (query data, run logic, take governed actions).
5. How a **function** or **action** is **registered as a tool**; the tool schema/contract presented to the LLM.
6. The **execution contract**: "the LLM only asks to use a tool; the platform executes it within the invoking user's permissions." Detail exactly how this is enforced and audited.
7. Native/structured **tool calling** and multi-tool orchestration.

**C. AIP Agent Studio / Chatbot Studio**
8. **Agent** anatomy: instructions/persona, tool set, **model selection** and **temperature**, knowledge/grounding sources.
9. **Conversation/session state & memory** — how context is maintained across turns.
10. **Publishing** an agent (as a function, via Foundry APIs) and consuming it (e.g., the Workshop AIP Agent widget).

**D. AIP Evals**
11. The **eval suite** model: test cases/datasets, expected results, and how runs are structured.
12. **Metrics/scorers** — built-in and custom; how quality is measured (incl. LLM-as-judge if used).
13. How evals gate **publishing** and integrate with Automate/monitoring.

**E. Model gateway / governed model access**
14. The set of **available models** (LLM + multimodal) and how a model is selected/swapped.
15. **Governance** of model calls — access controls, auditing, lineage, rate/limit handling, data-residency; where inference runs (incl. partner acceleration, e.g., NVIDIA).

**F. Grounding & retrieval**
16. How generations are **grounded** in Ontology data (object queries as tools, retrieval).
17. **Semantic search** via **vector** properties; embeddings; media/multimodal grounding.

**G. Governance, safety & lineage**
18. The end-to-end **AI permission model** and how it guarantees AI cannot exceed a user's rights or bypass **edits-only-via-actions**.
19. **Auditing/lineage** of AI operations; safety posture (prompt injection, guardrails, evals-as-gates).

**H. In-platform AIP**
20. **AIP widgets** in Workshop (esp. the AIP Agent widget); AIP **transforms** in Pipeline Builder; **AIP Assist**; AIP + **Automate**.

**I. APIs/SDK, internal architecture & history**
21. **APIs/SDK** to invoke Logic functions and agents programmatically; auth/scopes.
22. The named **internal services/architecture** behind AIP (verify).
23. **History/evolution**: AIP launch (2023); **Agent Studio → Chatbot Studio** rename; recent additions.

## Source strategy (prioritized)

1. **Primary — official docs:** `palantir.com/docs/foundry/aip/**` (overview, aip-features), `logic/**` (blocks, faq), `agent-studio/**` (getting-started, tools, foundry-apis), AIP Evals docs, `workshop/widgets-aip-agent`.
2. **Primary — blog & talks:** `blog.palantir.com`; Palantir Developers / **AIPCon** keynotes and demos; the Palantir–NVIDIA announcement.
3. **Primary — source & API refs:** `github.com/palantir`; the API reference (agent/Logic endpoints).
4. **Primary — training:** `learn.palantir.com` (AIP tracks).
5. **Secondary/Tertiary:** credible third-party deep-dives; community — leads/corroboration only.

Prefer primary, recent, version-stamped sources; capture URL + access date.

## Reverse-engineering methodology & rigor

- **Triangulate** non-trivial claims across ≥2 sources where possible.
- **Tag every claim** — **[Documented]** / **[Inferred]** / **[Speculative]** — with **confidence** and citation.
- **Separate current from legacy** (the Agent Studio → Chatbot Studio rename; evolving features); date-stamp facts; flag in-development items.
- **Flag contradictions** explicitly.
- **Never fabricate** tool categories, agent config options, eval metrics, model names, or service names. Where the record is silent (e.g., the gateway's routing internals or memory implementation), say so and give one best-supported hypothesis labeled **[Speculative]**.
- **Chase named mechanisms** to source: AIP Logic **blocks** (prompt/tools/output), the **data/logic/action** tool categories, agent **tools** (object query, function, apply-action), **temperature**, publish-as-function, **AIP Evals**, **AIP Assist**, the **model gateway**.

## Required output structure

1. **Executive summary** (≈1 page) + the 5–10 most important findings.
2. **AIP Logic** — the block/prompt/tool/output model.
3. **The tool model & tool-calling** *(most technical)* — tool taxonomy, registration, the execution/permission contract.
4. **Agent Studio / Chatbot Studio** — agent anatomy, config, state, publishing.
5. **AIP Evals** — suites, metrics, gating.
6. **Model gateway & governed model access.**
7. **Grounding & retrieval** — object queries, vectors/semantic search, multimodal.
8. **Governance, safety & lineage.**
9. **In-platform AIP** — Workshop widgets, Pipeline Builder, AIP Assist, Automate.
10. **APIs/SDK & internal architecture.**
11. **History & evolution.**
12. **Glossary.**
13. **Confidence & gaps register** — claims + confidence, known-unknowns + resolving source.
14. **Source bibliography** — URLs + access dates, by tier.

Use **tables** for the tool taxonomy, agent config options, eval metrics, and available models. Favor precise mechanics over prose; quote exact limits/options verbatim.

## Exhaustiveness bar

Do **not** stop at the overview. Drill until each mechanism is concretely described with a primary citation or recorded as a known unknown with a best-supported hypothesis. Pay special attention to the **tool-calling/permission contract**, the **Logic block model**, and the **evals scoring model** — the make-or-break details for a clone. Aim for a detailed technical white paper; cite extensively; neutral tone.

## Confirmed starting leads (verified — begin here, then expand)

- **AIP overview/features:** `palantir.com/docs/foundry/aip/overview`, `…/aip/aip-features` (Logic, Chatbot Studio (formerly Agent Studio), Evals build production AI on the Ontology).
- **AIP Logic:** `…/logic/blocks` (a Logic block = **prompt + tools + output**; three tool categories — **data, logic, action**), `…/logic/faq`.
- **Agent Studio:** `…/agent-studio/getting-started`, `…/agent-studio/tools` (object query / function / apply-action tools; **model temperature** 0–1; the Function tool calls any Foundry function/published Logic; publish agent as a function for **Automate**/**Evals**), `…/agent-studio/foundry-apis`.
- **In Workshop:** `…/workshop/widgets-aip-agent` (the AIP Agent widget).
- **Partner acceleration:** the Palantir–NVIDIA "operationalize AI" announcement.

**Named mechanisms to chase:** AIP **Logic block** (prompt/tools/output) · **data / logic / action** tool categories · agent **tools** (object query, function, apply-action, update-variable) · **temperature** · **publish as function** · **AIP Evals** (metrics/scorers) · **AIP Assist** · the **model gateway** / governed model access · **vector** properties / semantic search for grounding · *(verify)* memory/session internals · *(verify)* internal AIP service names.

# ▲▲▲ PASTE TO HERE ▲▲▲
