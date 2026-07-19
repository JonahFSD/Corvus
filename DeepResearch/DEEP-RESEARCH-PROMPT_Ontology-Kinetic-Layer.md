# Deep Research Prompt — Reverse-Engineering Foundry's Ontology *Kinetic Layer*

**What this is:** the companion to the semantic-layer prompt. Its single job is to reconstruct, as exhaustively as the public record allows, how Palantir Foundry's **Ontology kinetic layer — Actions and Functions** — is structured, executed, secured, and written back, at the level of concrete mechanics rather than marketing.

**How to use it:** paste everything below the line into any deep-research tool (Claude, ChatGPT/o-series deep research, Gemini, Perplexity, etc.). It's tool-agnostic. The **Confirmed starting leads** section gives real entry points. Trim the seed list if your tool has a tight input limit; keep role, scope, question bank, methodology, and output spec.

**Scope note:** the *kinetic* layer only — how the Ontology **changes** (Actions) and how business **logic executes** (Functions). The semantic layer (object/property/link modeling, storage/indexing) is covered in the companion reconstruction and is out of scope here except at the exact seam where a write commits to the object index.

---

# ▼▼▼ PASTE FROM HERE ▼▼▼

## Role

You are a senior platform-architecture researcher and reverse-engineer specializing in enterprise data platforms, workflow/rules engines, and serverless function runtimes. You are rigorous, source-driven, and allergic to marketing language. Your task is to reconstruct the internal design of the **kinetic layer of Palantir Foundry's Ontology** — specifically **Action types** and **Functions** — the mechanisms by which the Ontology is changed and by which governed business logic executes.

## Objective

Produce an **exhaustive, citation-backed technical reconstruction** of how Foundry's Action types and Functions are defined, validated, executed, secured, metered, and written back into the Ontology — detailed enough that a competent engineering team could use your report as the functional-and-architectural reference to build a faithful clone of the kinetic layer. **Prioritize concrete mechanics** (the anatomy of an action, parameter and rule types, the Ontology Edits API surface, the end-to-end writeback path, function runtimes/limits/metering, atomicity and concurrency semantics, API shapes) over conceptual or promotional descriptions.

## Precise scope: what "kinetic layer" means here

**In scope** — the parts of the Ontology that govern *what can happen* and *how logic runs*:

- **Action types** — anatomy (parameters, rules, submission criteria, side effects), RIDs/API names, status/lifecycle, where they are defined, how they are versioned/branched.
- **Parameters** — the full set of parameter types (object/object-set references, primitives, attachment, marking, struct, etc.); validation; defaults; prompts/rendering; conditional required/visible logic; ordering; accessing an object's *current* property value before the edit; how parameters bind to consuming apps (Workshop, Slate, Object Views).
- **Rules** — Ontology rules (create / modify / delete object, add / remove link) and their constraints; setting properties from parameters/expressions; how the primary key is set on create; rule ordering; and non-edit / side-effect rules (webhooks, notifications, other effects) with their failure semantics.
- **Submission criteria** (formerly "validations") — how conditions are expressed; use of object, relation/link, and user information; VALID/INVALID semantics; client vs. server enforcement; relationship to data-quality/editing governance; difference from parameter-level validation.
- **Function-backed actions & the Ontology Edits API** — the (TypeScript) Ontology Edits API surface (create/modify/delete object, create/delete link, etc. — verify exact method names); how function inputs derive from action parameters; the documented "if a function rule is present, no other rule may be configured" constraint; complex/bulk multi-object edits; returning applied edits; error handling, atomicity, and rollback.
- **The writeback path & execution semantics** — end-to-end: Action submit → Actions service → Object Data Funnel → object-database index + materialization; offset tracking; immediate index apply vs. periodic flush; transactionality/atomicity of a multi-edit action; concurrency and conflict resolution; bulk limits; synchronous vs. asynchronous application; idempotency; audit/edit-history capture.
- **Functions** — categories (read/query functions, edit functions, **Functions on Objects (FOO)**, function-backed/derived properties, **functions on models**); the runtimes (**TypeScript v1, TypeScript v2, Python**) and their differences; the execution sandbox; default and configurable **runtime limits** (e.g., the documented 60-second elapsed-time default); memory/payload limits; **compute-second metering** (capture exact overheads); cold-start/latency; concurrency; the function type system and I/O (object types, object sets, primitives, edits); the in-function `@foundry`/Ontology SDK surface; authoring/publishing/versioning (repositories, function RIDs, releases/tags, scopes, testing).
- **External integration & side effects** — Action-triggered **webhooks** (config, how functions compute webhook parameters, auth, ordering vs. the ontology edit, failure handling); **external functions**; **making API calls from functions** (the Data Connection source requirement, egress, runtime/cert differences); limits.
- **Adjacent (include, lightly):** **Automate / automations** (running actions/functions on a schedule or in response to events) and how Actions/Functions are exposed as **tools to AIP Logic and agents** — the kinetic *surface* AIP consumes, not AIP's internals.

**Out of scope** (mention only at the seam, do not deep-dive): the **semantic-layer internals** (object/property/link modeling, the storage/indexing engines) — already reconstructed separately; touch only where a write commits to the index. The **application/UI layer** (building Workshop/Slate apps) except as the consumer of actions/parameters. **AIP platform internals** (model gateway, agent orchestration) beyond how functions/actions plug in as tools. The general **pipeline/transform** system. High-level **philosophy/marketing** (already understood).

## Research question bank

Answer **every** question you can substantiate; for any you cannot, record it explicitly as a known unknown. Organize findings under these headings.

**A. Action type anatomy & lifecycle**
1. The full structure of an action type (parameters, rules, submission criteria, side effects) and how they relate.
2. Action type RID/API name format, status/lifecycle, where defined (Ontology Manager), and how it is versioned and branched.
3. How an action type is exposed to and invoked from consuming applications.

**B. Parameters**
4. Enumerate **every parameter type** (object reference, object-set, each primitive, attachment, marking, struct, geotime, etc.) and what each supports.
5. Parameter **validation** options; default values; prompts/rendering; **conditional** required/visible logic; ordering.
6. How a rule accesses an object's **current property value before** the action changes it.
7. How parameters **bind** to inputs in Workshop, Slate, and Object Views.

**C. Rules (edit logic)**
8. **Ontology rules**: exact capabilities and constraints of create-object, modify-object, delete-object, add-link, remove-link; how properties are set from parameters/expressions; how the **primary key is determined on create**.
9. Multiple-rule **ordering** and combined-effect semantics.
10. **Side-effect / non-edit rules** (webhooks, notifications, other effects): configuration, ordering relative to edits, and **failure semantics** (does a failed side effect roll back the edit?).

**D. Submission criteria (validations)**
11. How submission conditions are **expressed**; the use of object, relation/link, and user attributes.
12. **VALID/INVALID** evaluation; **client vs. server** enforcement; bypass risks.
13. The relationship to **data-quality/editing governance**, and the difference from parameter-level validation.

**E. Function-backed actions & the Ontology Edits API**
14. The **Ontology Edits API** surface (TypeScript): exact method names and signatures for creating/modifying/deleting objects and links, batching edits, and returning applied edits — verify against docs/SDK.
15. How a **function rule** derives inputs from parameters; substantiate the documented constraint that **no other rule may coexist** with a function rule.
16. **Complex/bulk multi-object** edits via functions: documented limits, batching, partial-failure behavior.
17. **Atomicity & rollback**: is an action's set of edits applied transactionally? What happens on mid-action failure?

**F. Writeback path & execution semantics — the core reverse-engineering**
18. The **end-to-end write path**: Action submit → Actions service → Object Data Funnel → object-database index + materialization. Where is the edit durably recorded vs. ephemerally indexed?
19. **Offset tracking**, immediate index apply vs. periodic flush to the merged/materialized dataset; near-real-time visibility guarantees.
20. **Concurrency & conflict**: concurrent edits to the same object; the documented "most recent transaction wins"; user-edit vs. datasource-update conflict modes.
21. **Bulk limits** (e.g., the documented ~10,000 objects per Action, higher on request) and what triggers on-demand Spark compute.
22. **Synchronous vs. asynchronous** application; idempotency; retry semantics.
23. **Audit / edit history**: what is recorded per edit (who/what/when/before/after), where, and how it is queried; OSv1 vs. OSv2 differences.

**G. Functions: types, runtimes, execution**
24. The **function categories** (read/query, edit, FOO, function-backed/derived properties, functions on models) and how each is consumed.
25. The three **runtimes** (TS v1, TS v2, Python): differences in capability, type system, and performance; migration path v1→v2.
26. The **execution environment**: sandbox/runtime, isolation, cold-start/latency; the default **60-second** elapsed-time limit and how it's configured; memory/payload limits; concurrency.
27. **Compute-second metering**: capture exact overheads (e.g., FOO fixed overhead; per-action overhead + per-object increment) and how cost scales.
28. The function **type system & I/O** (object types, object sets, primitives, edits) and the in-function **`@foundry`/Ontology SDK** surface.
29. **Authoring/publishing/versioning**: repositories (Functions / Code Repositories), function RIDs, release/tag/publish flow, scopes/permissions, and testing.

**H. External integration & side effects**
30. Action-triggered **webhooks**: configuration, how functions compute webhook parameters, auth, ordering vs. the ontology edit, retries/failure handling.
31. **External functions** and **API calls from functions**: the Data Connection **source** requirement, egress controls, the documented runtime/cert differences between webhook and function environments, and limits.

**I. Adjacent: Automate, AIP-tool exposure, history & patents**
32. **Automate / automations**: trigger types (schedule, object/event-driven), running actions/functions without a human, monitoring/alerting.
33. How **Actions and Functions are exposed as tools** to AIP Logic and agents (the kinetic surface only).
34. **History**: the v1→v2 functions evolution and Actions' evolution; locate **engineering blog posts / AIPCon talks** describing the action/function runtime; find any **patents** touching governed writeback, action/validation, or function execution.

## Source strategy (prioritized)

1. **Primary — official docs:** `palantir.com/docs/foundry/**`, especially `action-types/**` (overview, getting-started, parameters, rules, submission-criteria, permissions, inline-edits, function-actions), `functions/**` (overview, getting-started, TS v1/v2, Python, webhooks, api-calls, manage-functions, use-functions, functions-on-models), `object-edits/**`, `automate/**`, and the `api` reference for **Apply Action / Validate Action**.
2. **Primary — engineering blog & talks:** `blog.palantir.com`; Palantir Developers / AIPCon YouTube.
3. **Primary — source & API refs:** `github.com/palantir` (`osdk-ts`, foundry-platform SDKs, function/edits typings, Conjure specs), the public API v2 reference.
4. **Primary — patents & filings:** Google Patents / USPTO for governed-writeback / dynamic-ontology-edit / validation methods.
5. **Primary — training:** `learn.palantir.com`.
6. **Secondary — credible third parties:** consultancy/engineering deep-dives, ex-Palantir engineers, conference write-ups.
7. **Tertiary — community:** r/palantir, Hacker News, Stack Overflow — leads and corroboration only.

Always prefer **primary, recent, version-stamped** sources. Capture URL + access date for everything.

## Reverse-engineering methodology & rigor

- **Triangulate** every non-trivial claim across ≥2 independent sources where possible.
- **Tag every claim** — **[Documented]** / **[Inferred]** / **[Speculative]** — plus **confidence** (High/Medium/Low) and an inline citation.
- **Separate current from legacy** (OSv2 vs. OSv1/Phonograph; TS v2 vs. v1); date-stamp version-specific facts; note the Phonograph EOL after 2026-06-30 where the write path depends on it.
- **Flag contradictions** between sources explicitly.
- **Never fabricate** API method names, limits, service names, or runtime internals. Where the record is silent (e.g., exact action atomicity guarantees, the function sandbox technology), say so and give a single best-supported hypothesis labeled **[Speculative]**.
- **Chase named mechanisms** to source: Rules, Submission criteria (formerly validations), Function-backed actions, the **Ontology Edits API**, Validate/Apply Action endpoints, Functions on Objects, the three function runtimes, webhooks, external functions, Automate. **Verify** exact Edits-API method names and the precise compute-second overheads.

## Required output structure

Produce one long-form technical report:

1. **Executive summary** (≈1 page) — the kinetic layer in a nutshell + the 5–10 most important reverse-engineering findings.
2. **Action type anatomy & lifecycle.**
3. **Parameters** — a complete parameter-type table.
4. **Rules** — edit rules and side-effect rules, with a capabilities table.
5. **Submission criteria (validations).**
6. **Function-backed actions & the Ontology Edits API** — with method signatures where available.
7. **Writeback path & execution semantics** *(most technical)* — the end-to-end write, atomicity, concurrency, limits, audit.
8. **Functions: types, runtimes & execution** — a runtime-comparison table (TS v1 / TS v2 / Python) and a limits/metering table.
9. **External integration & side effects** — webhooks, external functions, egress.
10. **Automate & AIP-tool exposure.**
11. **Security, governance & audit** across the kinetic layer (action permissions, mandatory-control enforcement at submit, edit history).
12. **Developer / API / SDK surface** — Apply/Validate Action endpoints, OSDK action invocation (`applyAction`, `$returnEdits`), function invocation; request/response shapes.
13. **History & patents** — provenance and a change timeline.
14. **Glossary** of Palantir-internal kinetic-layer terms.
15. **Confidence & gaps register** — claims with evidence label + confidence, plus an explicit **known-unknowns** list and the source that would resolve each.
16. **Source bibliography** — URLs + access dates, grouped by tier.

Use **tables** for every enumeration (parameter types, rule capabilities, runtime comparison, limits, metering, endpoints). Favor precise mechanics over prose. Quote exact limits **verbatim**.

## Exhaustiveness bar (definition of done)

Do **not** stop at the conceptual overview. For each mechanism, drill until you can either (a) describe it concretely with a primary citation, or (b) explicitly record it as a known unknown with a best-supported hypothesis and the missing source. Pay special attention to the **writeback path's atomicity/concurrency guarantees**, the **exact Ontology Edits API surface**, and the **function runtime limits and metering** — these are the make-or-break details for a clone. Aim for the depth of a detailed technical white paper; cite extensively. Neutral, technical tone; no marketing language.

## Confirmed starting leads (verified — begin here, then expand)

*Confirmed to exist as of mid-2026; treat as entry points and verify currency.*

- **Action types** — overview, getting-started, **parameters** (`action-types/parameter-overview`), **rules** (`action-types/rules`), **submission criteria** (`action-types/submission-criteria`), **permissions** (`action-types/permissions`), **inline edits** (`action-types/inline-edits`), **function-backed actions** (`action-types/function-actions-getting-started`): `palantir.com/docs/foundry/action-types/…`
- **Apply/Validate Action API:** `palantir.com/docs/foundry/api/.../actions/validate-action` (and the Apply Action endpoint)
- **Functions** — overview, getting-started, **TypeScript v2** (`functions/typescript-v2-getting-started`), Python, **webhooks** (`functions/webhooks`), **API calls from functions** (`functions/api-calls`), **manage/publish** (`functions/manage-functions`), **use in platform** (`functions/use-functions`), **functions on models** (`functions/functions-on-models`): `palantir.com/docs/foundry/functions/…`
- **External functions:** `palantir.com/docs/foundry/data-connection/external-functions`
- **Functions on Objects (FOO) in Workshop:** `palantir.com/docs/foundry/workshop/functions-overview`, `…/functions-use`
- **Object edits / writeback & history:** `palantir.com/docs/foundry/object-edits/…`

**Named mechanisms to chase to source:** action **Rules** (Ontology rules vs. side-effect rules) · **Parameters** · **Submission criteria** (formerly *validations*) · **Function-backed actions** · the **Ontology Edits API** (TypeScript) · **Validate Action** / **Apply Action** endpoints · **Inline edits** · **Functions on Objects (FOO)** · **TypeScript v1 / v2 / Python** runtimes · **webhooks** · **external functions** · **functions on models** · the **60-second** function runtime default · **compute-second** metering overheads · *(verify)* **Automate** · *(verify)* exact **Ontology Edits API method names** · *(verify)* action **atomicity/transaction** guarantees.

# ▲▲▲ PASTE TO HERE ▲▲▲
