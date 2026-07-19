---
**Artifact:** Deep-research output — technical reconstruction of Foundry's *AIP* (AI) layer.
**Produced:** 2026-06-13, by a deep-research agent run on `DEEP-RESEARCH-PROMPT_AIP-Layer.md`.
**Independent spot-check (by Claude, 2026-06-13):** Confirmed **verbatim** — the execution/permission contract ("LLMs do not have direct access to tools; LLMs can only ask to use tools, and these tool calls are then executed by AIP Logic within the invoking user's permissions") and the **Palantir–NVIDIA partnership** (Oct 2025, GTC DC; CUDA-X, cuOpt, Nemotron/NeMo into the Ontology; Lowe's first adopter). High-confidence.
**Read with care:** the **internal session-state store** implementation and the **tool-execution microservice topology** are `[Speculative]`. The docs describe **no dedicated prompt-injection guardrail model** — safety rests on the permission boundary + evals. Model lists and numeric limits are point-in-time artifacts.
**The clone takeaway:** AI is a *consumer* of the existing engine, not a new authority. The permission contract means we get a safe AI layer almost for free *if* our [[Edits-Only-via-Actions]] + role model are already sound. Defer building it; design so it slots in.
---

# Reconstructing Palantir AIP's AI Layer: A Functional-and-Architectural White Paper

## 1. Executive Summary

Palantir's Artificial Intelligence Platform (AIP), launched via Alex Karp's CEO letter "Our New Platform: Bending Artificial Intelligence to Our Collective Will" in April 2023, is the AI layer that sits atop Foundry's Ontology. Its central architectural thesis is that LLMs are never given direct execution authority: an LLM may only *ask* to use a tool, and the platform *executes* that tool within the invoking user's permissions. This single principle — verbatim from the AIP Logic docs ("LLMs do not have direct access to tools; LLMs can only ask to use tools, and these tool calls are then executed by AIP Logic within the invoking user's permissions") — is the make-or-break design feature for any faithful clone.

The AI layer comprises four primary builder surfaces plus shared infrastructure:
- **AIP Logic** — a no-code builder for LLM-powered functions composed of blocks (prompt + tools + output).
- **AIP Chatbot Studio** (renamed from **AIP Agent Studio**; "AIP Chatbots" were "AIP Agents") — a builder for stateful conversational agents.
- **AIP Evals** — an evaluation harness with test cases, built-in/custom/LLM-as-judge evaluators, objectives, and experiments.
- **A model gateway** ("k-LLM" philosophy) governing access to GPT, Claude, Gemini, Grok, Llama, and others, with zero data retention.

**Most important findings:**
1. **The execution/permission contract is enforced platform-side, not prompt-side.** Tool calls run with either user-scoped (default) or project-scoped permissions; the LLM never holds credentials. [Documented, high]
2. **Logic blocks and agent tools share a common Ontology-tool taxonomy** — data (Query objects), logic (Call function), and action (Apply actions) — mapped onto Ontology object types, Functions, and Action types. [Documented, high]
3. **Ontology edits cannot be written by an LLM directly.** Logic functions only persist edits when executed *from an Action*; even a function containing an Apply action block will not write back unless invoked via an action. [Documented, high]
4. **Two tool-calling modes exist**: prompted tool calling (single tool at a time, all models) and native tool calling (parallel tools, subset of Palantir-provided models, limited tool types). [Documented, high]
5. **Agents are published as Ontology Functions** with a fixed `userInput`/`sessionRid` input contract and `markdownResponse`/`sessionRid` output contract, making them callable by Automate, Evals, Code Repositories, and the OSDK. [Documented, high]
6. **Evals supports a rich built-in evaluator library plus LLM-as-a-judge and Marketplace evaluators** (Rubric grader, Contains key details, ROUGE), with pass/fail objectives and thresholds that gate publishing. [Documented, high]
7. **Grounding is via Ontology context (object queries + vector-property semantic search), document context, and function-backed context.** Retrieval context runs deterministically on every user message. [Documented, high]
8. **The internal substrate is named**: AIP runs in a shared service mesh with Foundry, deployed within "Rubix," orchestrated by Apollo, with a "Language Model Service" mediating model calls. [Documented, high]
9. **The Palantir–NVIDIA partnership (GTC DC, October 28, 2025)** integrates NVIDIA CUDA-X, accelerated computing, cuOpt, and open-source Nemotron/NeMo models into the Ontology at the core of AIP. [Documented, high]

## 2. AIP Logic — The Block / Prompt / Tool / Output Model

AIP Logic is a tool to "quickly and maintainably build LLM-driven processes." A Logic **function** takes inputs (Ontology objects or primitives), runs one or more **blocks**, and returns an output (a value, an object, a struct, or Ontology edits).

### 2.1 The block model

A Logic function is "composed of blocks, which take an input, return an output, and comprise a discrete interaction with your data. … The output of a block can be used in subsequent blocks." Commonly used block types:

| Block | Function |
|---|---|
| **Use LLM** | "The heart of AIP Logic." Composed of a prompt + tools + output. Supports any platform LLM (k-LLM). Per-block token limit; temperature configurable via the block's Configuration text field. |
| **Apply action** | Deterministically calls an Action without going via an LLM — precise parameter control, faster execution. |
| **Execute function** | Calls existing Foundry functions (TypeScript, Python, or other Logic functions) to reuse logic. |
| **Conditionals** | "if-then-else." Each branch returns via Define a Path / Return a Variable / Take No Action. All branches must return consistent output types. |
| **Loops** | Iterate over a collection; per element run a transformation and/or action. Loops with no actions run iterations in parallel. Output is a list of values or ontology edits. |
| **Create variable** | Creates a typed variable for later blocks (array, boolean, date, double, float, integer, long, object, short, string, timestamp). |

### 2.2 Prompt configuration

Prompts are natural-language instructions. Recommended structure: task overview, then data, then tool guidance. Inputs/variables are injected by typing `/`. A separate **system prompt** can be supplied. Few-shot examples recommended; 5–10 input/output pairs can be saved as unit tests. "An LLM only has access to what you specifically make available to it." Token usage shown per message in the Debugger; limits reset per block.

### 2.3 The three tool categories (data / logic / action)

"AIP Logic leverages three categories of Ontology-driven tools — data, logic, and action."

| Category | Tool (Logic) | Capability |
|---|---|---|
| **Data** | **Query objects** | Object types the LLM can access; select a property subset for token efficiency; "Configure object return limits." Supports filtering/aggregation. |
| **Logic** | **Call function** | Foundry functions (code-defined or other Logic functions) the LLM may call. |
| **Logic** | **Calculator** | Accurate mathematical calculations. |
| **Action** | **Apply actions** | Lets the LLM use Action types to edit the Ontology, with a description of when to use each. |

### 2.4 Structured/typed output and publishing

Logic output can be a **Value** (primitive or object), a **Struct** ("multiple named values"), or **all the Ontology edits** the function made. When run in the editor, proposed edits appear in the Debugger but are *not* executed; edits persist only when the Logic function is called from an Action or automation. After publishing, the **Uses** tab exposes a copyable curl request (not for edit-returning Logics). Published Logic functions are Ontology query functions callable anywhere Functions execute.

### 2.5 Control flow, execution mode, limits

Two **execution modes**: **user-scoped** (default — runs with the running user's permissions; logs persist 24 hours) and **project-scoped** (runs with the project's permissions; resources imported into the project; an optional run-history dataset preserves the last 10,000 runs). A five-minute execution time limit applies when invoked from Workshop or the function API (not in the Debugger).

## 3. The Tool Model & Tool-Calling (Most Technical)

### 3.1 Tool taxonomy in Chatbot Studio (six tool types)

| Tool | Capability |
|---|---|
| **Action** | Executes an Ontology edit; can run automatically or after user confirmation. |
| **Object query** | Object types the LLM can access; filtering, aggregation, inspection, link traversal; configurable accessible properties. |
| **Function** | Calls any Foundry function, including published AIP Logic functions; latest or pinned version. |
| **Update application variable** | Updates an application-state variable. |
| **Command** | Triggers operations in other Palantir apps via Workshop Commands. |
| **Request clarification** | Pauses execution and asks the user for clarification. |
| **(Legacy) Ontology semantic search** | Uses a vector property to retrieve Ontology context; deprecated in favor of Ontology context. |

### 3.2 How an Ontology Function/Action becomes a callable tool

A tool is registered by selecting an object type (object query), an Action type (action tool), or a Function (function tool) in the builder UI and writing a natural-language description of when to use it. "Instructions, tool descriptions, and variable descriptions are compiled into the raw system prompt for the LLM." The object query tool surfaces only configured object types and selected properties.

### 3.3 The execution/permission contract

The defining contract: **the LLM only asks to use a tool; the platform executes it within the invoking user's permissions.** Enforcement:
- Tool calls execute server-side under user-scoped or project-scoped permissions; the LLM never receives credentials.
- Object/property access is constrained to what the builder explicitly configured.
- Ontology edits flow only through Action types, which carry their own permission and validation logic.
- Action tools can require user confirmation before executing.
- All operations are audited; every action by a human or AI agent is logged and chained executions traceable.

### 3.4 Tool-calling modes and the orchestration loop

- **Prompted tool calling:** inserts tool instructions into the prompt; all tool types and models; "can only call a single tool at a time."
- **Native tool calling:** uses the model's built-in tool-calling; parallel tool calls; "a subset of Palantir-provided models and … actions, object query, function, and update application variable."

The loop: retrieval context runs deterministically on every new user message and is injected; the LLM reasons over tools, requests tool calls, the platform executes them under the user's permissions, results feed back, and the loop continues until a final markdown answer. "View reasoning" / Debugger expose the steps. `AgentIterationsExceededLimit` bounds the loop.

## 4. AIP Chatbot Studio (formerly AIP Agent Studio)

**Naming note:** "AIP Chatbot Studio was previously known as AIP Agent Studio, and AIP Chatbots were previously known as AIP Agents." Both URL trees are live; "application state" was previously called "parameters."

### 4.1 Agent anatomy

| Config element | Detail |
|---|---|
| **Instructions / system prompt** | The agent's function; reference tools/variables via `/`; compiled into the raw system prompt. |
| **Tools** | The six tool types in §3.1. |
| **Model selection** | "A subset of those enabled on your enrollment." |
| **Temperature** | Default 0 (focused), max 1 (random). |
| **Application state** | String or object-set variables, each named/described; value-visibility toggle controls LLM read access; can be tool inputs, retrieval inputs, or citation outputs. |
| **Retrieval context** | Ontology / document / function-backed (see §7). |

### 4.2 Conversation/session state & memory

"The context window includes the system prompt, conversation history, and the information injected to assist the LLM (including retrieval context, application state, and tools). Exceeding the context window … prompt[s] users to create a new session." Application variables persist as state and update deterministically (pinned to initial values at the start of the reasoning loop) or non-deterministically (via the Update application variable tool). Long-term memory can be built with Ontology objects.

### 4.3 Publishing and consumption

Agents publish as **Functions** (callable "anywhere … Functions can be executed"), enabling Automate, Evals, Code Repositories. The agent-as-Function contract:
- **Inputs:** `userInput` (string); `sessionRid` (optional, `ri.aip-agents..session.{uuid}`; omit to start a new session); plus all application variables as optional inputs.
- **Outputs:** `markdownResponse`; `sessionRid`; plus application variables (only if updated).

Consumption: the **AIP Chatbot widget** in Workshop; the OSDK (agents-as-functions for single-shot); the AIP Agents V2 platform APIs for multi-shot sessions.

## 5. AIP Evals — Suites, Metrics, Gating

AIP Evals is "a testing environment to evaluate the performance of your AIP Logic functions, AIP Agent functions, or code-authored functions … designed to help you deal with the non-deterministic nature of LLMs."

### 5.1 Suite model

- **Evaluation suite** = test cases + target functions + evaluation functions.
- **Test cases** = inputs + expected outputs (manual, from an object set, or both).
- **Target functions** = AIP Logic, AIP Chatbot (published as a Function), or code-authored functions; multiple per suite for comparison.
- **Metrics** = results of evaluation functions, per test case, comparable in aggregate.

### 5.2 Evaluators

Built-in (verbatim): Exact boolean/string/numeric matches and array variants; Regex match; Levenshtein distance; String length; Keyword checker; Exact object match; Object set contains; Object set size range; Integer/Floating-point/Temporal range; Generic exact match; **LLM-as-a-judge** ("Uses an LLM to evaluate whether a user-defined condition holds true"). **Marketplace:** Rubric grader, Contains key details, ROUGE score. **Custom:** any published function returning ≥1 boolean/numeric metric.

### 5.3 Objectives, gating, experiments

Each metric has an **objective** (boolean true/false passes; numeric maximize/minimize with optional threshold). "A test case iteration … is a pass if all metrics meet the configured objective." ≥3 iterations recommended for LLM-backed functions. **Experiments** use grid search over parameter combinations (model × prompt) to optimize cost/performance. Integrates with Automate/observability for production gating.

## 6. Model Gateway & Governed Model Access

### 6.1 The k-LLM model set

"Palantir AIP supports a wide range of LLMs … including xAI, OpenAI, Anthropic, Meta, and Google." Families (subject to enrollment): Grok (xAI); GPT-4o/o1/GPT-4 Turbo/GPT-5.x (OpenAI); Llama 3.x (Meta, Palantir-hosted); Mixtral; Claude 3.x–4.x (Anthropic); Gemini 2.5/3.x (Google/Vertex). Models carry **Experimental → Stable** lifecycle states; selectable per Logic block, per agent, or per Pipeline Builder node; bulk replacement via Workflow Lineage.

### 6.2 Governance of model calls

- **Access controls:** admins enable AIP at two levels and each model family (Enabled/Disabled/Experimental); restrictable by user group and Organization.
- **Zero data retention:** "no customer data contained in prompts or completions is retained by the applicable third party," and no customer data is used to retrain — technical + contractual guarantees.
- **Inference location:** mediated through Palantir-managed infrastructure (the Language Model Service) over Azure/AWS Bedrock/Google Vertex; regional endpoints (US, EU); georestriction.
- **Rate/limit handling:** enrollment-level TPM/RPM tiers; overrides/allowlists/reserved capacity; exponential backoff with jitter.
- **Provider-compatible proxy APIs:** `/api/v2/llm/proxy/anthropic/v1/messages`, `/openai/v1/chat/completions`, `/openai/v1/responses`, `/openai/v1/embeddings`, `[Beta] /xai/...`, `[Beta] /google/...` — all enforcing ZDR and georestriction.
- **Bring your own model:** registered models / function interfaces.

### 6.3 NVIDIA partnership

At GTC Washington, D.C. (October 28, 2025), NVIDIA and Palantir announced an "integrated technology stack for operational AI." "Palantir Ontology, at the core of the Palantir AI Platform (AIP), will integrate NVIDIA GPU-accelerated data processing and route optimization libraries, open models and accelerated computing" — NVIDIA CUDA-X data-science libraries, cuOpt decision-optimization (routing/inventory), and open NeMo/Nemotron models; with NVIDIA Blackwell to accelerate the end-to-end AI pipeline. **Lowe's** is the first major adopter, building a supply-chain digital twin for continuous global optimization.

## 7. Grounding & Retrieval

### 7.1 Retrieval context types

"Retrieval context is deterministically run with **every** new user message." Three types:
- **Ontology context:** a fixed set of *N* objects, or semantic search for the *K* most relevant (requires a vector embedding property). Selectable printed properties.
- **Document context:** full document text, or relevant chunks (semantic search returns *K* chunks).
- **Function-backed context:** a TypeScript function satisfying `AipAgentsContextRetrieval` (takes `messages: MessageList`), returning a `retrievedPrompt` string — enabling hybrid retrieval and custom citations.

### 7.2 Vector properties and semantic search

Semantic search is built on **Vector**-type Ontology properties: an embedding property configured with a **Dimension** and a **Similarity Function**. Embeddings generated via Pipeline Builder ("Text to embeddings," e.g. text-embedding-ada-002) or transforms. Queries embed the user input and run nearest-neighbor (`.near(embedding, {kValue: k})`, k 1–100 in Workshop). This is "Ontology-augmented generation" (the RAG pattern). Multimodal grounding via vision models in the Use LLM node and chatbot media handling.

### 7.3 Citations

Agents render citation bubbles when the LLM emits a specific XML format. Ontology: `<key>{objectRID}</key>` or `<objectTypeId>…</objectTypeId><primaryKey>…</primaryKey>`. Document: `<citation><mediaSetKey>…</mediaSetKey><mediaItemKey>…</mediaItemKey></citation>` with optional `<page>`. Selecting a citation can update an object-set application variable for downstream Workshop widgets.

## 8. Governance, Safety & Lineage

### 8.1 The AI permission model

The model guarantees an LLM cannot exceed a user's rights because: (a) tool calls execute server-side under the invoking user's (or project's) permissions; (b) the LLM has no direct data/credential access; (c) exposure is restricted to explicitly configured object types/properties; (d) mutations occur only via Action types (with validation and confirmation); (e) at the infra level every component "operates with zero trust … access-gated based on identity, device health, and verification."

### 8.2 Auditing, lineage, safety posture

AIP observability provides metrics (success/failure, P95 duration), 30-day execution history, distributed tracing across functions/actions/models/automations, and logging of prompts/tokens/errors — in Workflow Lineage. Safety posture: evals-as-gates, human-in-the-loop action confirmation, value-visibility controls, and the deterministic tool/permission boundary as the primary guard against prompt-injection escalation (a successful injection still cannot exceed the user's permissions or bypass actions). **The docs do not detail a dedicated prompt-injection classifier or guardrail model**; the architecture relies on the permission boundary and evals.

## 9. In-Platform AIP

- **Workshop — AIP Chatbot widget** (formerly AIP Agent widget): embeds a chatbot; maps application variables to Workshop variables; orchestrates Workshop Commands. AIP Generated Content widget renders Logic or direct-to-LLM output.
- **Pipeline Builder — Use LLM node:** runs LLMs over datasets at scale (prompt templates, output-type conformance, vision support, high-concurrency with retry/backoff). "Text to embeddings" generates vectors.
- **AIP Assist:** in-platform help trained on Foundry docs (no customer-data access); context-aware; supports custom content sources / custom chatbots.
- **AIP + Automate:** Logic functions and agents-as-Functions run in scheduled/event-driven automations; edits applied or staged for human review via actions.

## 10. APIs/SDK & Internal Architecture

### 10.1 AIP Agents V2 platform API (preview; `preview=true`)

| Endpoint | Method/Path | Scope |
|---|---|---|
| Create Session | `POST /api/v2/aipAgents/agents/{agentRid}/sessions` | `api:aip-agents-write` |
| Blocking Continue | `POST …/sessions/{sessionRid}/blockingContinue` | `api:aip-agents-write` |
| Streaming Continue | `POST …/sessions/{sessionRid}/streamingContinue` | `api:aip-agents-write` |
| Get Session / Content | `GET …/sessions/{sessionRid}[/content]` | `api:aip-agents-read` |
| Cancel | `POST …/sessions/{sessionRid}/cancel` | `api:aip-agents-write` |
| Get Rag Context | `PUT …/sessions/{sessionRid}/ragContext` | `api:aip-agents-write` |

- **Blocking Continue** request: `userInput` (`{text}`), `parameterInputs`, `contextsOverride` (if set, skips automatic retrieval), `sessionTraceId`. Response: `agentMarkdownResponse`, `parameterUpdates` (only `READ_WRITE` variables), `totalTokensUsed`, `interruptedOutput`, `sessionTraceId`.
- **Errors:** `RateLimitExceeded`, `RetryAttemptsExceeded`, `ContextSizeExceededLimit`, `AgentIterationsExceededLimit`. "Concurrent requests to continue the same session are not supported."

### 10.2 Invoking Logic functions over REST

A published Logic function is an Ontology **query function** invoked via `POST /api/v2/ontologies/{ontology}/queries/{queryApiName}/execute` with `{"parameters": {...}}`. OSDK method `executeFunction`. Edit-returning Logic functions must run from an Action. Five-minute execution limit applies.

### 10.3 Authentication

OAuth 2.0 with `Authorization: Bearer`. Two grants: Authorization Code (on behalf of users) and Client Credentials (a service user with stored secret → short-lived token). Granted access = intersection of scope and the user/service-user's permissions.

### 10.4 Internal architecture (named services)

- **Rubix** — the substrate/deployment environment for the shared AIP+Foundry service mesh.
- **Apollo** — continuous-delivery/orchestration (zero-downtime upgrades).
- **Language Model Service** — the named service mediating LLM calls (Azure-backed originally).
- AIP architecture enumerates 12 capability categories incl. "Secure LLM integration & access," "Vector, compute, tool services" (embeddings; Spark/Flink, DuckDB/Polars, BYO containers; an Ontology "tool factory"), "Agent lifecycle," "Security & governance." RIDs: `ri.aip-agents..session.{uuid}`, `ri.language-model-service..language-model.…`, `ri.mio.main.media-set…`.

[Speculative, low–med] The docs do not publish the tool-execution-loop microservice topology or the session-state store. Best hypothesis: session state/history persisted in an Ontology-/Foundry-backed store keyed by `sessionRid` (consistent with the contract, `estimatedExpiresTime`, and Get Content reload), orchestration in the agent runtime the Language Model Service fronts.

## 11. History & Evolution

- **April 2023** — AIP launched (Karp CEO letter; "AIP for Defense").
- **June 1, 2023** — first AIPCon.
- **2023** — AIP Assist and the Language Model Service; Azure-backed mediation with a no-training exception.
- **2023–2024** — AIP Logic, Agent Studio, AIP Evals matured; Pipeline Builder Use LLM + embeddings.
- **2024–2025** — model expansion (Claude, Gemini, Grok, Llama); native tool calling; agents-as-Functions; Evals experiments.
- **Agent Studio → Chatbot Studio rename**; "parameters" → "application state."
- **October 28, 2025** — Palantir–NVIDIA partnership (CUDA-X, cuOpt, Nemotron) at GTC DC; Lowe's first adopter.
- **2026** — GPT-5.x / Claude 4.x / Gemini 3.x; provider-compatible proxy APIs; Ontology MCP / MCP Hub.

## 12. Glossary

- **AIP** — Artificial Intelligence Platform; the AI layer atop the Ontology.
- **k-LLM** — Palantir's model-agnostic philosophy (many interchangeable LLMs).
- **AIP Logic** — no-code builder for LLM-powered Ontology functions, composed of blocks.
- **Block** — a discrete Logic step (Use LLM, Apply action, Execute function, Conditional, Loop, Create variable).
- **Tool** — a platform capability the LLM can request (data/logic/action; six agent tool types).
- **AIP Chatbot Studio / Chatbot / Agent** — builder for stateful conversational agents (formerly Agent Studio / AIP Agents).
- **Application state** — string/object-set variables maintaining agent context (formerly "parameters").
- **Retrieval context** — Ontology/document/function-backed context injected per user message.
- **Vector property** — Ontology property storing an embedding (Dimension + Similarity Function).
- **AIP Evals** — evaluation harness (suites, test cases, evaluators, objectives, experiments).
- **Language Model Service** — internal service mediating LLM calls.
- **Rubix / Apollo** — deployment substrate / orchestration platform.

## 13. Confidence & Gaps Register

| Claim | Confidence | Basis |
|---|---|---|
| LLM-asks/platform-executes under user permissions | High | AIP Logic Blocks/Concepts (verbatim, verified) |
| Three Logic tool categories + tools | High | Blocks page (verbatim) |
| Six agent tool types; two tool modes | High | Tools page (verbatim) |
| Temperature 0 default, max 1 | High | Getting started |
| Edits only via actions | High | Blocks/Getting started |
| Agent-as-Function I/O contract | High | Agents-as-Functions page |
| Evals evaluator list + objectives | High | Create-suite (verbatim) |
| Retrieval context types + vector search | High | Retrieval context page |
| AIP Agents V2 endpoints/scopes | High | API reference |
| ZDR / no-retrain guarantees | High | AIP security page |
| Named services (Rubix, Apollo, LMS) | High | Architecture pages |
| NVIDIA partnership specifics | High | NVIDIA newsroom (verified) |
| Internal session-state store implementation | Low–Med [Speculative] | Inference from sessionRid contract |

**Known unknowns:** exact session TTL / message-size cap; the tool-execution-loop microservice topology; whether a dedicated prompt-injection guardrail model exists (none documented — relies on permission boundary + evals); default *N*/*K* and embedding-model defaults for Ontology context.

## 14. Source Bibliography (by tier; accessed June 12–13, 2026)

**Tier 1 — Official Palantir docs:** aip/{overview, aip-features, security, enable-aip-features, supported-llms, llm capacity, provider-compatible APIs}; logic/{overview, concepts, getting-started, blocks, faq, compute-usage, execution-mode}; agent-studio & chatbot-studio/{overview, concepts, getting-started, application-state, retrieval-context, citations, tools, agents-as-functions, foundry-apis}; aip-evals/{overview, create-suite, run-suite, experiments, analyze, metrics-dashboard}; workshop/{widgets-aip-agent/chatbot, generated-content}; pipeline-builder Use LLM; ontology semantic search / Ontology-augmented generation; architecture-center (AIP architecture, platforms, Rubix); API reference (AIP Agents V2 sessions, queries execute, auth, OAuth2, limits).
**Tier 2 — Palantir/NVIDIA:** blog.palantir.com "Semantic Search," "AI Infrastructure and Ontology"; newsroom CEO letters (Apr 2023); prnewswire (AIPCon); NVIDIA newsroom / GlobeNewswire "Palantir and NVIDIA Team Up to Operationalize AI" (Oct 28, 2025).
**Tier 3 — Secondary (corroboration only):** Unit8; Oreate AI; Medium build write-ups; history aggregators.
