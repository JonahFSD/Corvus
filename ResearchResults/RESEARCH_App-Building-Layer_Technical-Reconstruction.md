---
**Artifact:** Deep-research output — technical reconstruction of Foundry's *app-building* layer (Workshop, Slate, Object Views).
**Produced:** 2026-06-13, by a deep-research agent run on `DEEP-RESEARCH-PROMPT_App-Building-Layer.md`.
**Independent spot-check (by Claude, 2026-06-13):** Confirmed **verbatim** against primary docs — the **lazy reactivity model** ("compute and recompute lazily only when displayed by a visible widget") and the **sequential-but-non-awaiting event semantics** (events do not wait for downstream recomputation), plus the **OSDK custom-widget surface** (`FoundryWidget` from `@osdk/widget.client-react`, `useWorkshopContext`, `@osdk/workshop-iframe-custom-widget`, `OsdkProvider2`). High-confidence.
**Read with care:** the **Workshop reactivity-engine internals** (the scheduler/algorithm) are `[Speculative]` — behavior is documented, the engine is not. The `ri.slate…` RID prefix and the "Foundry Synchronizer" service name are unconfirmed known-unknowns. Numeric limits are Palantir-specific artifacts.
---

# Palantir Foundry App Layer — A Technical Reconstruction of Workshop, Slate & Object Views

*A functional-and-architectural reference for an application-platform team. Neutral, source-driven. Access date: June 13, 2026. Claims are tagged [Documented]/[Inferred]/[Speculative] with confidence where non-trivial.*

## TL;DR

- Foundry's app layer is built on a **reactive variable graph**: widgets declare input/output variables, variables recompute lazily ("compute and recompute lazily only when displayed by a visible widget or layout"), and Actions/Functions/events mutate state. Workshop is the modern no-code builder, Slate the legacy power-user HTML/JS builder, and Object Views the per-object detail surface (now themselves Workshop modules).
- The make-or-break clone details are: (1) the variable type system (Object set, Object set filter, String, Boolean, Numeric, Date, Timestamp, GeoPoint, GeoShape, Array, Struct, Time series set) with three recompute modes; (2) Action invocation via an **auto-generated Form** with parameter binding from app state, inline validation surfacing, and post-action refresh; and (3) ontology binding (object sets feed widgets; selection flows back as output object sets).
- Extensibility runs through OSDK React custom widgets (`@osdk/widget.client-react`, `FoundryWidget`, `useObjectSet`) and bidirectional iframes (`@osdk/workshop-iframe-custom-widget`, `useWorkshopContext`). App permissions are decoupled from data permissions, so a user can open a module but be blocked from its objects/actions/functions.

## Key Findings

1. **Module anatomy**: Header (persistent toolbar) → Pages (multi-screen) → Sections (subdividable; layouts: columns, rows, tabs, toolbar, loop) → Widgets. Only the header persists across pages. [Documented, High]
2. **Widget config has three tabs**: Widget setup (input/output variables + display options + attached Actions), Metadata (rename + raw JSON), Display (Auto (max) / Absolute / Flex sizing). [Documented, High]
3. **Reactivity is a lazy dependency graph**: in view mode variables compute only when shown; in edit mode all compute. Three recompute behaviors: Automatic (default), Only when triggered by event, On module load + event. [Documented, High]
4. **Events execute sequentially but do not await downstream recomputation** — confirmed verbatim: "Events in Workshop execute sequentially based on their configuration order. However, events do not wait for the downstream computations of previous events to complete before executing… Downstream variables that depend on the target variable will not be up-to-date before the next configured event executes." This is the single most consequential reactivity caveat for a faithful clone. [Documented, High]
5. **Actions auto-generate a Form** from the Action Type definition; parameters bind from Workshop variables (local defaults override global), validation issues surface inline ("1 issue"), and submission triggers data refresh. [Documented, High]
6. **Slate is a graph of nodes** (widgets, variables, queries, functions) referenced via Handlebars `{{ }}`; explicitly "lazy" and skips re-evaluation when an upstream value is unchanged. [Documented, High]
7. **Object Views are now Workshop-backed**; legacy YAML/widget views remain supported but cannot add new legacy tabs. Object View permissions sync with the object type. [Documented, High]
8. **App vs data permissions are separate**: "the ability to open or edit a Workshop module is separate from the ability to access the data, actions, or functions which may be needed to fully use a Workshop module." [Documented, High]
9. **Custom widgets** run in a restrictive sandbox (no Web Storage, restrictive non-configurable CSP, no external requests, no non-Ontology APIs) and use OSDK hooks. [Documented, High]

## 2. Workshop Module & App Model

**What a module is.** A Workshop module is the unit app/resource, identified by an RID of the form `ri.workshop.main.module.<uuid>`. Created via Projects & Files → New → Workshop module, it inherits the permissions of its parent Project/folder. The module name doubles as the browser/Carbon tab name.

**Anatomy / layout hierarchy:**

- **Header** — persistent toolbar holding title, application logo, tabs, and button groups; persists across all pages. Can be hidden, given a custom title color, and set to collapsed (collapsed headers show only icons for Button Group/Tabs; all other widgets hide).
- **Pages** — "each page is a blank canvas"; only the header persists between pages. Page navigation uses a Layout event (from Button Group or Tabs).
- **Sections** — subdivide each page; contain one or more widgets or a nested layout. Section layouts: **Columns** (vertical split), rows, **Tabs**, **Toolbar** (horizontal, optimized for small widgets like Button Groups/Metric Cards), and **Loop** (loops over an object set or array, rendering an embedded module per item). Sections can be configured as **drop zones** (toggle Drop Handling) to receive drag payloads for cross-app interactivity.
- **Widgets** — leaf UI building blocks.

**Editing model.** Canvas/drag editing: hover an empty section → "+ Add widget" or "Set layout"; select a widget to reveal its right-hand configuration panel, which "dynamically updates based on your selections."

**Lifecycle / publishing & versioning.** Module versioning decouples the builder's working copy from what end users see. The Versions dialog lists saved versions (timestamp, editor, description) with: **Publish this version**, **View this version** (shows a warning banner when viewing a non-published version), and **Revert to this version**. URLs distinguish `/latest/` (last published) from `/dev/` (last saved). A **Changelog panel** visualizes diffs between versions (additions, deletions, changes, moves, newly unused) including JSON diffs; it is reused for branch **rebasing** and conflict resolution.

**Module interface (the module's "API").** "The module interface is the set of variables that are able to be mapped to variables from a parent module when embedded, and initialized from the URL." Add a variable to the interface via Settings → external ID + enable the module interface toggle. URL query params (`?<externalId>=<value>`) set interface variables for deep-linking and state-sharing. The interface is consumed by embedded modules and the Open Workshop Module event.

**Embedded modules.** A child module can be reused across parents (loop layout or Embedded Module widget). Each child has its own variable scope; embedding enables parallel editing and maintainability. Parent↔child communication is via module interface variables. Module-level config (routing, state saving, auto-refresh) is NOT inherited by embedded children — auto-refresh must be configured per module; to auto-refresh inside a non-refreshing parent, embed via iframe as a sandbox. A module may not embed itself; embedded children are separately permissioned ("failed to load module" if the viewer lacks child permission).

## 3. Widget Catalog

Widgets "declare a configuration shape" and are configured with input variables (data in), output variables (data out, consumed downstream), display options, conditional visibility, and attached Actions/events. Grouped by Workshop's own documentation categories:

### Core display widgets

| Widget | Purpose | Key inputs / outputs |
|---|---|---|
| Object Table | Renders an object set as rows | In: object set; Out: Active object (singleton set), Selected objects (set). Columns, function-backed (derived) columns, action-backed inline editing, row-selection events, custom right-click row actions |
| Object List | Object set as list/cards/grid | In: object set; Out: Active object, Selected objects (multi-select toggle). Media display, reordering, hide-null |
| Object View | Embeds an object's detail view | In: "Object to display" set (first object in full form factor); Form factor full/panel; interface configuration |
| Property List | Properties from a single object | In: object set (first object); column count, label positioning, scenario loading |
| Links | Link types & linked objects in expandable sections | In: object set |
| Object Set Title | Object set summary as title | In: object set |

### Visualization widgets

| Widget | Purpose | Key inputs / outputs |
|---|---|---|
| Chart: XY | XY chart | In: object set; Out: object set filter (selection) |
| Vega Chart | Custom Vega/Vega-Lite | In: object set; Out: filter |
| Map | Interactive geospatial (MapboxGL, WebGL, desktop-only) | In: object set per layer; Out: Selected objects (bidirectional), drawn-shape GeoJSON. Base/object/overlay layers |
| Map [Legacy] | Mobile/non-WebGL fallback | In: object set |
| Gantt Chart | Objects with time props on a timeline | In: object set with time props |
| Pie Chart | Pie viz | In: object set |
| Timeline | Chronological events | In: object set with timestamps |
| Pivot Table | Dynamic grouping/aggregation in tabular form | In: object set; Out: filter |
| Metric Card | Highlight key metrics | In: number/aggregation/function output |
| Markdown | Formatted text with object references | In: object refs / strings |
| Media Preview | Render media from URL/RID/Base64 (PNG/JPEG/PDF) | In: URL/RID/base64 string |
| Spreadsheet Display | Tabular spreadsheet | In: tabular data |
| Video / Audio & Transcription Display | A/V playback | In: media |
| PDF Viewer | Render PDFs with keyword search | In: PDF resource |
| Image Annotation | Draw rectangles on images | In: image |
| Free-form Analysis | User-driven object exploration | In: object set |
| Time Series Analysis | Time-series investigation | In: time series set |
| Data Freshness | Last-updated timestamp per object type/datasource | In: object types |
| Edit History / Action Log Timeline | Audit of edits/actions | In: object set |
| Linked Compass Resources | Compass resources linked to an object | In: object |
| Resource List | Static/dynamic list of Files & Projects resources, object types, or object sets | In: resource refs / object set vars; Out: Selected object type / Selected object set |
| Stepper | Step navigation | layout/state |

### Filtering widgets

| Widget | Purpose | Key inputs / outputs |
|---|---|---|
| Filter List | Property-type filters as histograms, distribution charts, date pickers, type-ahead, keyword search | In: object set; Out: **Object set filter** variable |
| Object Dropdown | Select a single object | In: object set; Out: Selected object (singleton set) |
| Object Selector | Select multiple objects | In: object set; Out: selected objects set |
| String Selector | Select string(s) as dropdown/radio/checkboxes | In: static or string array var; Out: string or string array |
| Date and Time Picker | Single date or range | Out: date/timestamp |
| Text Input | Free text | Out: string |
| Numeric Input | Numeric value | Out: number |
| Checkbox | Binary toggle | Out: boolean |
| Exploration Filter Pills | Visualize/apply filters as pills | In/Out: object set + filter |
| Exploration Search Bar | Filters incl. linked types; modes Read only / Remove only / Update existing / Add, update, remove | In: object set (single type); Out: object set filter |
| Prominent Term | Filter by prominent terms | In: object set; Out: filter |
| User Select | Select Multipass user(s) | Out: string / string array of user IDs |

### Event-trigger & navigational widgets

| Widget | Purpose | Key inputs / outputs |
|---|---|---|
| Button Group | Buttons triggering Actions, events, URLs, or exports | On click: Action / events / URL / export; conditional disabled/hidden; event can fire at a point in the Action lifecycle |
| Inline Action | Inline auto-generated action form | bound action + parameters |
| Tabs | Tabbed navigation / page switching | Out: layout/page event |
| Comments | Threaded comments | per-object/local |
| Media Uploader | Upload media | uploads to Foundry |
| Audio Recorder | Record audio | media output |

### AIP widgets (the AIP↔Workshop seam)

| Widget | Purpose | Key inputs / outputs |
|---|---|---|
| AIP Interactive / AIP Chatbot (formerly "AIP Agent") | Embed an AIP Agent/Chatbot | Maps Studio "application variables" ↔ Workshop variables; `textbox` variable tied to chat input; tools = AIP Logic, FOO, other modules |
| AIP Analyst | AI-powered analysis embedded in a module | Inputs: object types/sets/datasets, custom system prompt, default model; Outputs: result variables |
| AIP Generated Content | Generated content | prompt → content |

### Embed Foundry applications

| Widget | Purpose | Key inputs / outputs |
|---|---|---|
| Iframe | Embed a custom widget URL or Slate app via iframe; bidirectional comms | URL; input params → Slate; output params Slate → Workshop; CSP/CORS config |
| Workshop: Embedded Module | Embed another module | module interface variable mapping |
| Map Application Template | Embed Map template | input params |
| Quiver Dashboard | Embedded Quiver dashboard | Quiver artifact |
| Notepad – Embedded Document | Embed Notepad doc | doc ref |
| Vertex Graph | Embed Vertex graph/template/diagram | object set input params |
| Derived series | Manage derived series | series mgmt |

### Mobile & Scenario widgets

Mobile: Mobile Navigation Bar, QR Code Reader, Current Location Manager. Scenarios: Scenario Manager, Scenario Selector, Scenario Summary.

## 4. Variable & State / Reactivity Model (most technical)

### Variable types

| Type | Semantics | Initialization |
|---|---|---|
| Object set | Set of ≥1 objects | From object type or another object set; optionally filtered or pivoted via Search Around |
| Object set filter | Property type/value pairs to filter object sets | From object type then property/value pairs; output by Filter List, charts, Pivot Table |
| String | Text | Static, or function/aggregation/object property |
| Boolean | true/false | Static or function/aggregation/object property |
| Numeric | Integer or float | Static or function/aggregation/object property |
| Date | Date | Static or function/aggregation/object property |
| Timestamp | Timestamp | Static or function/aggregation/object property |
| GeoPoint | Geopoint | Object property |
| GeoShape | Geoshape | Object property or function |
| Array | Array of boolean/date/numeric/geopoint/geoshape/string/timestamp/struct | various |
| Struct | Composite fieldID→value map; **nested structs unsupported** | Static, object struct property, or function returning CustomType |
| Time series set | Time series property of a single object, optional transforms | object time series property |

Note: "Complex non-performant object properties are not supported as variables in Workshop."

### Variable definition types

Static; Function; Object property; Aggregation; **Object set definition** (object types + filters + link traversals); **Variable transformation** (chained operations). Transformations include arithmetic, String concatenation, If/else, Cast, array ops, boolean & date/time comparisons, object set ops (Is empty / Object property / Object set aggregation [min·max·sum·average·cardinality] / Object RID), and geo extraction (Geohash/Latitude/Longitude/MGRS from geopoint).

### Scoping & declaration

Variables live in the left-sidebar Variables panel: searchable by name/unique ID, with a **dependency graph** view and definition-type filters; partitioned to show variables used by the selected widget or active page. Each variable has a name, external ID, settings (incl. module interface toggle), and a read-only current value. Output variables are auto-created when adding a widget.

### Reactivity model

- **Lazy compute** [Documented, High]: "In view mode, Workshop variables will compute and recompute lazily only when displayed by a visible widget or layout." Variables on non-visible pages/tabs/overlays/looped pages are not computed until shown. In edit mode all variables compute "for convenience."
- **Recompute behaviors**: **Automatic** (default — recomputes when any dependency changes; may also recompute when upstream objects reload, e.g., after an action submission or auto-refresh); **Only when triggered by an event** (`recompute {variable}` event); **On module load, and when triggered by an event**. Object set definition variables behave like Automatic and cannot be configured.
- **Function-backed result caching**: "Function-backed variables use result caching. If the same input is provided, the result returned will be from cache." To force recomputation, inject an incrementing numeric "entropy" variable via the Set variable value event.

### User interaction → state → action

User interaction updates an output variable that propagates to dependents. **Events** are the explicit mechanism. Documented event types: Set variable value, Apply Action, Layout (switch page, expand/collapse section, switch tab), Layers (open/close overlays), URL, Export, Open Workshop Module, Send to AIP Assist, Stream LLM response into variable (temperature 0–1).

**Critical caveat** [Documented, High] — verbatim: *"Events in Workshop execute sequentially based on their configuration order. However, events do not wait for the downstream computations of previous events to complete before executing. The source variable value is copied to the target variable value immediately… Downstream variables that depend on the target variable will not be up-to-date before the next configured event executes."* Workshop "does not support forcing events to wait for all downstream updates"; to force propagation, split into separate user-triggered events. **A clone must replicate this fire-immediately, propagate-asynchronously semantics, not a synchronous transactional update.**

## 5. Binding to the Ontology

**Object sets feed widgets.** The object set input variable feeds Object Table, Object List, Filter List, Charts, Map, etc.; a widget either reuses an existing object set variable or defines one inline.

**Selection flows back.** Object Table outputs Active object (singleton) and Selected objects; Object List the same with multi-select; Object Dropdown/Selector output selected object(s). Filtering widgets output **object set filter** variables, applied to other object set variables (the canonical Filter List → Object Table pattern — and critically you "define a new object set variable to back the Filter List widget so that the filter does not limit the base object set"). Map's Selected objects variable is bidirectional.

**Functions on Objects (FOO).** Functions power: (1) **derived/function-backed columns** in Object Table — "Use a runtime input" "dynamically pass[es] only the objects currently displayed… faster performance," returning a map keyed by object; (2) **function-backed variables** (with result caching); (3) **Metric Card** values; (4) function-backed Action types.

**Action invocation & the auto-generated Form.** Verbatim: "A Form component is automatically generated based on the Action definition, so writeback to object data and the user interface associated with it are not defined separately." Configuration flow: pick the Action, then bind parameters in Parameter Defaults — defaults can be a Workshop variable, an object property, or a local value. **Local default values (Workshop variables) always take precedence over global defaults.** Parameters without defaults appear as empty user-input fields.

**Validation surfacing.** Submission criteria (e.g., a regex `^[A-Z]{3}$`) produce inline issues — the form shows "1 issue"; hovering reveals the message; the submit button becomes available only "when the actions form is filled out and all parameters pass validation." Inline editing maps action parameters to columns.

**Real-time / live behavior.** After an Action edits an object, the UI reflects it via data reload (which may trigger Automatic-recompute variables). **Auto-refresh** watches registered object sets for updates "from anywhere in Foundry" and refreshes all module data without user interaction. **Limits** [Documented, High] — verbatim: *"Auto-refresh is limited to OSv2-backed object types."* (Failure: `InvalidObjectSetForPlanning: A watched object set contains a reference to an entity… indexed in Object Storage V1.`)

## 6. Slate — Model & When-to-Use

**Overview.** Slate is the older, power-user builder for "dynamic and responsive applications with a custom design," fully CSS-customizable (built on Palantir's open-source **Blueprint**; styles in **LESS** compiled at page load). Slate uniquely supports public, unauthenticated apps (write-only, static data, no OSDK).

**The node graph.** Verbatim: "In Slate, all widgets, functions, variables, and queries are modeled as nodes in a graph. Each node evaluates to a JSON output and other nodes are templated to reference that output." Handlebars references define dependencies; the graph is **lazy** — "it avoids unnecessary work by only re-evaluating a node when the upstream references have changed value" (workaround: `Math.random()` entropy).

**Variables.** Types: **Number, String, Boolean, Array, Object, Null**. Scope: **shared** (every page) or **local** (per-page). Values do NOT persist across page loads; use **user storage** to persist. URL query params override defaults (always strings). Every variable has a `.set` event.

**Handlebars.** Templating `{{ }}` accesses widgets, variables, environment (`{{$global.user.firstName}}`), and helpers; cannot be used in Variables/Styles editors or view mode.

**Functions.** JavaScript snippets; no DOM, no state; async supported; ships Lodash, Math.js, Moment, Numeral. Distinct from Foundry Functions.

**Queries.** Recommended: Object Set Builder (Ontology) or OSDK. Legacy: SQL against Postgres-synced datasets ("no longer in development"); API Gateway / HTTP JSON. All results JSON.

**Writeback.** Recommended via Ontology **Actions** using the **Action widget** (often in a Dialog). Legacy: Phonograph writeback (deprecated).

**Events & actions.** Global events: `slate.ready`, `slate.resize`, `slate.onNavigate[page]`, `slate.userStorageChanged`. Variable events: `<var>.changed`, `.set`. `{{slEventValue}}` carries the triggering value.

**Cross-boundary with Workshop.** Embed Slate in Workshop via the Iframe widget. Input params pass Workshop→Slate; Slate reads them with **`Slate.getMessage`**. Slate→Workshop uses **`Slate.sendMessage`** to set output params or trigger Workshop events. Mechanically `window.postMessage` with target `slate-parent-iframe-event`. A passed object set arrives as a filter spec/RID payload resolved via the object set service, with a **"100,000 object limit for `Objects().search()`"** requiring pagination.

**When Slate vs Workshop.** Workshop is the recommended object-oriented no-code builder, tightly bound to the Ontology with managed reactivity and lower maintenance. Slate is chosen for pixel-level custom design or public unauthenticated apps, at higher maintenance. Platform direction favors Workshop and OSDK; Slate's legacy data paths are deprecated though not removed.

## 7. Object Views — Full vs Legacy

**Default standard view.** Foundry auto-creates a standard Object View for every object type: prominent properties plus the object's links.

**Full (configured) Object Views — the modern model.** Each Object View tab is **backed by a Workshop module**, editable with the full widget set. Tab types: **Managed Workshop modules** (permissions auto-synced, not reusable), **Existing Workshop modules** (reusable), and **Legacy** tabs ("New tabs using this builder can no longer be added, but existing tabs are still supported"). Tabs support conditional visibility. Versioning is independent per module.

**Legacy Object Views.** YAML/widget-based, edited via legacy editor. Layout widgets: Horizontal Distribution, Vertical Stack Container, Tabbed Container, Conditional Container, Markdown. Many Apps-and-Files widgets are "not object-aware" — Comments and Linked Files do NOT write back (use Actions/Forms).

**Object View widget in Workshop.** Displays a single object's view inside a module. Config: Object to display, Form factor (full/panel), **Interface configuration** (maps the module's variables onto an object view tab's module interface — "Legacy object view tabs are not supported").

**Permissions.** Verbatim: "Unless you manually convert the Workshop module for an Object View tab to a standalone module… the Workshop module's permissions will be managed by the object type."

## 8. Embedding & Extensibility

**Custom widgets (OSDK React).** Verbatim: "Custom widgets enables application builders to securely extend Foundry applications with custom frontend code. Currently, custom widgets are only supported in Workshop." A **widget set** is a package of one or more widgets; each "declares a configuration shape" with **parameters** (host→widget) and **events** (widget→host, can update parameters via `parameterUpdateIds`).

Build artifacts and packages (verified via palantir.com/docs and github.com/palantir/osdk-ts):

- `@osdk/widget.client` — `defineConfig({ id, name, type: "workshop", parameters, events, refreshHostDataOnAction })`.
- `@osdk/widget.client-react` — the `FoundryWidget` root component.
- `@osdk/widget.vite-plugin` — `foundryWidgetPlugin()` build plugin.
- `@osdk/client` — `createClient(window.location.origin, $ontologyRid, tokenProvider)`.
- `@osdk/react` — experimental hooks (`useObjectSet`, `useOsdkAction`, `useOsdkObjects`, `useOsdkObject`, `useLinks`, `useOsdkAggregation`, `useOsdkFunction`) requiring **`OsdkProvider2`**; "automatic caching, loading states, and real-time updates."
- Widget set RID namespace: `ri.widgetregistry..widget-set.<LOCATOR>`.

**Auth & sandbox.** OSDK calls use the user's token and "adhere to the user's permissions at runtime." The runtime is restrictive [Documented, High] — verbatim: *"The custom widgets runtime does not support certain browser APIs for persisting data such as: Web Storage API (localStorage, sessionStorage)… Non-Ontology APIs are also not supported… the content security policy (CSP)… cannot be configured and is restrictive by design; no external requests are allowed."* **`refreshHostDataOnAction`** auto-refreshes object set parameters after the widget applies an action.

**Object set parameter sizing** [Documented, High] — verbatim from `palantir/workshop-iframe-custom-widget`: *"use objectSet, which gives you the value of a objectTypeId with up to 10,000 primary keys if you are using @osdk/client version < 2.0, and temporaryObjectSetRid if you are using @osdk/client >= 2.0… Using temporaryObjectSetRid also removes the 10,000 objects per object set limit."*

**Bidirectional iframe.** `@osdk/workshop-iframe-custom-widget` exposes **`useWorkshopContext(CONFIG)`**, returning a context to read/write Workshop variables and execute Workshop events. One call per bidirectional iframe instance. Iframe performance caveat [Documented, High] — verbatim: *"We do not recommend embedding more than one iframe widget on-screen."*

**Embedding other Foundry apps.** Another Workshop module (cross-app variable contract = module interface mapping), Slate, Map template, Quiver dashboard, Notepad, Vertex graph. Cross-app variables also flow via **drag-and-drop** drop zones and **App Pairing/Commands**.

## 9. Governance, Performance & Limits

**Permissions / sharing.** A module inherits its parent Project/folder permissions. **App access and data access are decoupled** [Documented, High] — verbatim: *"the ability to open or edit a Workshop module is separate from the ability to access the data, actions, or functions which may be needed to fully use a Workshop module."* A user can see an app but not its data. The **Check access** panel shows whether a user meets the module's access requirement plus data requirements.

**Performance tooling.** The **Performance Profiler** records network requests from initialization, showing total module load time and a per-widget/per-variable breakdown. "Only widgets and variables that affect the on-screen display are calculated."

**Documented limits & caveats:**

| Limit / caveat | Verbatim / source |
|---|---|
| OSv1 linked-object filter | "Object types on Object Storage V1 have a linked object filter limit of 100,000 objects." |
| Auto-refresh scope | "Auto-refresh is limited to OSv2-backed object types." |
| Custom widget object set parameter | "up to 10,000 primary keys… < 2.0… temporaryObjectSetRid… removes the 10,000 objects per object set limit" |
| Slate object search | "there is a 100,000 object limit for Objects().search()… handle pagination" |
| Iframe count | "We do not recommend embedding more than one iframe widget on-screen." |
| Slate Text Area debounce | "0.5s debounce delay used by the Text Area widget" |
| Phonograph (OSv1) deprecation | "unavailable after June 30, 2026." |
| Workshop variables | "Complex non-performant object properties are not supported as variables." |
| Workshop structs | "Nested structs are currently not supported." |

## 10. APIs/SDK & Internal Architecture

**Driving apps programmatically.** Apps bind to the Ontology through the public REST APIs and OSDK. Verified endpoints: Get/List Object, Search Objects (OSv1 capped at 10,000 results, no limit OSv2), Apply Action (+ apply_batch/validate), List Action Types, Execute Query, Get Ontology Full Metadata (v2). OAuth scopes `api:ontologies-read`/`api:ontologies-write`. Standalone SDKs: `foundry-platform-typescript`, `foundry-platform-python`.

**Named internal services / build artifacts (verified):**
- **Object Set Service (OSS)** — Ontology reads (search/filter/aggregate/load).
- **Ontology Metadata Service (OMS)** — ontology entity definitions.
- **Object Data Funnel ("Funnel")** — OSv2 write/index orchestration.
- **Actions service** — applies edits; produces action logs.
- **Object Storage V2 (OSv2)** / **Phonograph (OSv1)** — current / legacy stores.
- **Blobster** — blob/attachment/image store.
- RID namespaces: `ri.workshop.main.module.<uuid>`, `ri.object-set.main.temporary-object-set.<uuid>`, `ri.ontology.main.*`, `ri.widgetregistry..widget-set.<LOCATOR>`, `ri.carbon..core-module.object-view`, `ri.phonograph2-objects.main.object.<uuid>`, `ri.foundry.main.dataset.<uuid>`, `ri.quiver.main.artifact`.
- **Unverified**: a bare `ri.slate…` RID string; the name "Foundry Synchronizer" for Postgres-synced datasets. [Low confidence]

**Reactivity engine internals.** [Speculative, Low] Best-supported hypothesis from documented behaviors: a **pull-based, topologically-ordered lazy dependency graph** evaluated per visible widget, where variables are nodes with declared dependencies; evaluation is demand-driven by widget visibility; events imperatively write node values and enqueue downstream invalidation without awaiting completion; function-backed nodes memoize on input identity. Mirrors Slate's documented lazy node graph — the lowest-risk model for a clone.

## 11. History & Evolution

- **Slate → Workshop.** Slate is older (HTML/JS/Handlebars dependency graph, Blueprint/LESS). Workshop is the newer object-oriented no-code builder with managed reactivity; the recommended path.
- **Object Views: legacy → full.** Legacy YAML/widget views remain supported but cannot add new legacy tabs; full Object Views are Workshop-module-backed.
- **AIP Agent widget renamed.** "AIP Agent" → **AIP Chatbot / AIP Interactive**; in-Workshop legacy agent config deprecated in favor of AIP Agent/Chatbot Studio.
- **OSv1 (Phonograph) → OSv2.** Phonograph deprecated (after June 30, 2026); auto-refresh, custom widgets, and modern features target OSv2.
- **Custom widgets path matured.** OSDK + iframe/custom-widget is the recommended extensibility path.

## 12. Glossary

- **Module** — a Workshop application resource (`ri.workshop.main.module`).
- **Widget** — a UI component declaring a configuration shape (parameters + events).
- **Variable** — a typed reactive value (input/output).
- **Object set** — a set of Ontology objects, the primary data input.
- **Object set filter** — a reusable filter applied to object set variables.
- **Search Around** — pivoting an object set to linked objects.
- **Module interface** — externally-mappable variables = a module's API.
- **Action / Action Type** — a permissioned Ontology write; auto-generates a Form.
- **Function on Objects (FOO)** — function powering derived columns/variables/metrics.
- **Auto-refresh** — module-level live data updates watching OSv2 object sets.
- **Handlebars** — Slate's `{{ }}` templating/dependency mechanism.
- **OSDK** — Ontology SDK; the typed client/React layer for custom apps and widgets.
- **Custom widget / widget set** — developer-built React component(s) embedded in Workshop.

## 13. Confidence & Gaps Register

| Claim | Confidence | Source basis |
|---|---|---|
| Widget catalog completeness | High | Workshop doc sidebar + category overviews |
| Variable types & recompute behaviors | High | concepts-variables |
| Event sequential-no-await caveat | High | concepts-events (verbatim) |
| Action Form auto-generation + inline validation | High | actions-use, parameters-default-value |
| 100k OSv1 filter limit; OSv2-only auto-refresh; 10k object-set parameter | High | filter-list, auto-refresh, workshop-iframe-custom-widget (verbatim) |
| Object Views Workshop-backed; permissions synced | High | object-views/config-overview |
| Custom widget sandbox restrictions | High | custom-widgets/development (verbatim) |
| Reactivity engine internals (algorithm/scheduler) | Low [Speculative] | Behavior documented, engine not published |
| `ri.slate…` RID string | Low [known unknown] | Only permalink URL path confirmed |
| "Foundry Synchronizer" service name | Low [known unknown] | Phonograph sync documented; exact name unconfirmed |

**Open known-unknowns:** (1) the canonical Slate resource RID prefix; (2) the precise scheduler/evaluation order within a single recompute cycle; (3) whether Workshop's variable graph is push- or pull-based internally; (4) exact per-widget enumerated event lists; (5) any documented hard cap on widget count per module (not found — likely guidance-only).

## 14. Source Bibliography (access date June 13, 2026)

**Tier 1 — Primary (palantir.com/docs/foundry):** workshop/{concepts-widgets, concepts-variables, concepts-layouts, concepts-events, concepts-permissions, actions-use, functions-use, auto-refresh, performance-profiler, versions, module-interface, embedding-workshop-modules-overview, widgets-*}; slate/{overview, concepts-variables, logic-overview, concepts-handlebars, concepts-functions, concepts-events, references-writeback, widgets-platform, concepts-queries, faq}; object-views/{config-overview, config-tabs, config-legacy-object-views, widgets-apps-files}; custom-widgets/{overview, core-concepts, create, development, parameters-and-events, use-osdk}; action-types/{use-actions, parameters-default-value}; object-databases/object-storage-v1; api-reference.
**Tier 1 — GitHub (palantir):** osdk-ts; workshop-iframe-custom-widget.
**Tier 3 — Secondary (corroboration only):** Medium (D-ONE "Mastering Palantir Foundry Workshop"); Palantir Developer Community threads.
