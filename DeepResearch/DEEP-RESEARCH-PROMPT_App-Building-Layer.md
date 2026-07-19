# Deep Research Prompt — Reverse-Engineering Foundry's *App-Building* Layer

**What this is:** the fourth in the set. Its single job is to reconstruct, as exhaustively as the public record allows, how Palantir Foundry's **application-building layer — Workshop, Slate, Object Views, and the widget/variable model** — works: how operational apps are built, how they hold state, and how they bind to the Ontology.

**How to use it:** paste everything below the line into any deep-research tool. Tool-agnostic. The **Confirmed starting leads** give real entry points. Keep role, scope, question bank, methodology, and output spec; trim the seed list if input is tight.

**Scope note:** the app *surface* only — the no-/low-code builders and their runtime. The Ontology (objects/actions/functions) and AIP are covered in companion reconstructions and are out of scope except where an app *binds* to them.

---

# ▼▼▼ PASTE FROM HERE ▼▼▼

## Role

You are a senior front-end/application-platform architect and reverse-engineer specializing in low-code app builders, reactive UI state models, and data-bound component systems. You are rigorous, source-driven, and allergic to marketing language. Your task is to reconstruct the internal design of **Palantir Foundry's app-building layer**: **Workshop**, **Slate**, **Object Views**, and the **widget + variable** model that powers operational applications.

## Objective

Produce an **exhaustive, citation-backed technical reconstruction** of how Foundry apps are composed, how they manage state and reactivity, what the full widget catalog is, and how apps bind to the Ontology (object sets, functions, actions, forms) — detailed enough that a competent team could use it as the functional-and-architectural reference to build a faithful clone of the app layer. **Prioritize concrete mechanics** (the widget catalog and configuration model, the variable/state/reactivity model, event handling, data binding, the action-form generation, embedding/extensibility) over conceptual or promotional description.

## Precise scope

**In scope:**
- **Workshop** — the primary no-code builder: the **module** model; the full **widget** catalog (layout, display, input, visualization, AIP widgets) and how widgets are configured with input/output variables, display options, and actions; layout/sections/responsive behavior; events and interactivity.
- **The variable & state model** — variable types, scoping, derived/computed state, reactivity/recomputation, how user interaction updates state, and how state binds to widgets.
- **Binding to the Ontology** — object sets as inputs; **Functions on Objects** for display/derived columns; invoking **Action Types** (and the auto-generated **Form**); writeback from the UI; live updates after edits.
- **Slate** — the power-user (HTML/JS) builder: widgets, variables (Number/String/Boolean/Array/Object/Null), queries, the scripting/logic and event model (e.g., `Slate.getMessage`), and the documented trade-offs vs. Workshop (customization vs. maintenance).
- **Object Views** — the per-object detail surface: full vs. legacy object views, tabs/widgets, configuration, and embedding (incl. the Object View widget inside Workshop).
- **Embedding & extensibility** — iframe / custom widgets, embedding Foundry apps and Slate inside Workshop, passing variables across boundaries.
- **App governance** — permissions, sharing, and how app access relates to underlying object/data permissions; performance and documented limits.
- **APIs/SDK & internal architecture** — any app/runtime APIs, and the named internal services/build artifacts behind Workshop/Slate (verify).

**Out of scope** (touch only at the seam): the Ontology internals (object/property/link/action/function modeling — already reconstructed); **AIP** internals (covered separately — but the AIP Agent widget and AIP-in-Workshop binding are in scope as the seam); the data/pipeline layer; Apollo. Analytical apps (Contour, Quiver, Map, Notepad/Reports) are adjacent — note their role briefly but focus on Workshop/Slate/Object Views as the app *builders*.

## Research question bank

Answer every question you can substantiate; record the rest as known unknowns.

**A. Workshop module & app model**
1. What is a Workshop **module**? Its anatomy (layout, widgets, variables, events), lifecycle, and how it's published/shared.
2. How is a module's UI laid out (sections, tabs, responsive/sizing), and what is the editing model (builder UX)?

**B. Widget catalog & configuration**
3. Enumerate the **widget catalog** as completely as possible, grouped (layout, display, input, visualization, AIP, embedding). For each major widget: purpose and key inputs/outputs.
4. How is a widget **configured** — input/output variables, display options, conditional visibility, and attached **actions**?
5. The **Object View widget**, **Resource List**, table/grid widgets, button groups, filter widgets, and AIP widgets specifically.

**C. Variable & state / reactivity model**
6. The full set of **variable types** and scoping rules; how variables are declared and referenced.
7. The **reactivity model**: how a change to one variable recomputes dependents and re-renders widgets; evaluation order; any documented performance caveats.
8. How **user interaction** (selection, input, button press) updates state and triggers actions/functions.

**D. Binding to the Ontology**
9. How **object sets** feed widgets (inputs, selection, filtering, search-around) and how selection flows back into state.
10. How **Functions on Objects** power derived columns, formatting, and computed display.
11. How an app invokes an **Action Type**: the **auto-generated Form**, parameter binding from app state, validation surfacing, and post-action refresh.
12. Real-time behavior: after an action edits an object, how/when does the UI reflect it?

**E. Slate (power-user builder)**
13. Slate's model: widgets, **variables**, **queries** (to datasets/objects/functions/APIs), and the **scripting/event** model (e.g., `Slate.getMessage`, events, JS).
14. When Slate is the right choice vs. Workshop (the documented customization-vs-maintenance trade-off); embedding Slate in Workshop and passing variables across.

**F. Object Views**
15. **Full vs. legacy Object Views**: structure (tabs, widgets), configuration, and how they're used standalone and embedded.
16. How an Object View maps app variables onto an object's interface.

**G. Embedding & extensibility**
17. **Iframe / custom widgets**: contract, sandboxing, message passing, auth; what a developer can build.
18. Embedding other **Foundry applications** inside Workshop and the cross-app variable contract.

**H. Governance, performance & limits**
19. App **permissions/sharing**, and how app visibility relates to underlying object/dataset permissions (can a user see an app but not its data?).
20. Documented **performance** guidance and **limits** (widget counts, object-set sizes, refresh behavior).

**I. APIs/SDK, internal architecture & history**
21. Any **APIs/SDK** to build, embed, or drive apps programmatically; the OSDK/React hooks used in custom widgets.
22. The named **internal services / build artifacts** behind Workshop and Slate (verify).
23. **History/evolution**: Slate (older) → Workshop (newer); Object Views full vs legacy; deprecations.

## Source strategy (prioritized)

1. **Primary — official docs:** `palantir.com/docs/foundry/workshop/**` (concepts-widgets, the widget pages, variables, functions-overview), `slate/**` (concepts-variables, widgets-platform, logic), `object-views/**`, and any app-building overview.
2. **Primary — engineering blog & talks:** `blog.palantir.com`; Palantir Developers / AIPCon (Workshop/operational-app demos).
3. **Primary — source & API refs:** `github.com/palantir` (osdk-ts, `@osdk/react` hooks used in custom widgets), the API reference.
4. **Primary — training:** `learn.palantir.com` (app-building tracks).
5. **Secondary/Tertiary:** credible third-party walkthroughs; community threads — leads/corroboration only.

Prefer primary, recent, version-stamped sources; capture URL + access date.

## Reverse-engineering methodology & rigor

- **Triangulate** non-trivial claims across ≥2 sources where possible.
- **Tag every claim** — **[Documented]** / **[Inferred]** / **[Speculative]** — with **confidence** (High/Med/Low) and an inline citation.
- **Separate current from legacy** (Workshop vs. Slate; full vs. legacy Object Views); date-stamp version-specific facts; flag in-development features.
- **Flag contradictions** explicitly.
- **Never fabricate** widget names, variable semantics, or service names. Where the record is silent (e.g., the reactivity engine internals), say so and give one best-supported hypothesis labeled **[Speculative]**.
- **Chase named mechanisms** to source: Workshop **module/widget/variable**, the **Object View widget**, the auto-generated **Form**, Slate **variables/queries/events**, iframe/custom widgets, the **AIP Agent widget**.

## Required output structure

1. **Executive summary** (≈1 page) + the 5–10 most important findings.
2. **Workshop module & app model.**
3. **Widget catalog** — a grouped, as-complete-as-possible **table** (widget · purpose · key inputs/outputs).
4. **Variable & state / reactivity model** *(most technical)*.
5. **Binding to the Ontology** — object sets, functions, actions/forms, live refresh.
6. **Slate** — model and when-to-use.
7. **Object Views** — full vs legacy.
8. **Embedding & extensibility** — iframe/custom widgets, cross-app variables.
9. **Governance, performance & limits.**
10. **APIs/SDK & internal architecture.**
11. **History & evolution.**
12. **Glossary.**
13. **Confidence & gaps register** — claims + confidence, plus known-unknowns and the source that would resolve each.
14. **Source bibliography** — URLs + access dates, by tier.

Use **tables** for the widget catalog, variable types, and limits. Favor precise mechanics over prose. Quote exact limits verbatim where they exist.

## Exhaustiveness bar

Do **not** stop at the overview. Drill until, for each mechanism, you can describe it concretely with a primary citation or record it as a known unknown with a best-supported hypothesis. Pay special attention to the **widget catalog**, the **variable/reactivity model**, and the **action-form binding** — the make-or-break details for a clone. Aim for a detailed technical white paper; cite extensively; neutral tone.

## Confirmed starting leads (verified — begin here, then expand)

- **Workshop:** `palantir.com/docs/foundry/workshop/concepts-widgets` (widgets are the core UI building blocks, configured with input/output variables, display options, and Actions); `…/workshop/widgets-object-view` (Object View widget); `…/workshop/widgets-resource-list`; `…/workshop/widgets-iframe` (custom widget via iframe); `…/workshop/widgets-aip-agent` (AIP Agent widget); `…/workshop/functions-overview` (Functions on Objects in Workshop).
- **Slate:** `…/slate/concepts-variables` (variable types: Number, String, Boolean, Array, Object, Null; vault-wide scope); `…/slate/widgets-platform`; `…/slate/logic` (events incl. `Slate.getMessage`).
- **Object Views:** `…/object-views/*` (full vs legacy; `widgets-apps-files`).

**Named mechanisms to chase:** Workshop **module** · **widget** (catalog) · **variable** (input/output, types, scope) · **Object View widget** · auto-generated **Form** (from an [[Action Type]]) · **Resource List** · **iframe / custom widget** · **AIP Agent widget** · Slate **variables / queries / events** (`Slate.getMessage`) · `@osdk/react` hooks · *(verify)* the Workshop **reactivity/state engine** internals · *(verify)* internal service/build-artifact names.

# ▲▲▲ PASTE TO HERE ▲▲▲
