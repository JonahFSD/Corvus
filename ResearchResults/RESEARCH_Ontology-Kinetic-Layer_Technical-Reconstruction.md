---
**Artifact:** Deep-research output — technical reconstruction of Foundry's Ontology *kinetic layer* (Action types & Functions).
**Produced:** 2026-06-13, by a deep-research agent run on `DEEP-RESEARCH-PROMPT_Ontology-Kinetic-Layer.md`.
**Independent spot-check (by Claude, 2026-06-13):** Confirmed **verbatim** against primary docs — the **Ontology Edits API** surface (TS v2 `createEditBatch`/`getEdits` from `@osdk/functions`; Python `client.ontology.edits()`/`get_edits()`; TS v1 implicit `@OntologyEditFunction`/`@Edits`) and the **function limits** ("30 seconds of CPU time... up to 60 seconds... 128 Megabytes of memory"). The Actions/Funnel write path, Phonograph EOL, 10k-objects/action, and 18 + 1/object metering also match findings from the semantic-layer research. This report is high-confidence.
**Read with care:** the report's own *known unknowns* — Actions-service retry/idempotency internals, the function sandbox technology, exact webhook-vs-function certificate handling, and a specific patent enumeration — remain open. The exact numeric limits are Palantir-specific *scale artifacts*, not requirements for our clone.
---

# Palantir Foundry Ontology Kinetic Layer: A Technical Reconstruction of Action Types and Functions

## 1. Executive Summary

The "kinetic layer" of Palantir Foundry's Ontology — the part that governs *what can happen* and *how logic runs* — is built from two primary primitives: **Action types** (governed, transactional units of edit to objects/links plus side effects) and **Functions** (server-side code that reads from and writes to the Ontology). These sit atop a write path orchestrated by the **Actions service** and the **Object Data Funnel ("Funnel")** in Object Storage V2 (OSv2). [Documented, High]

The ten most important reverse-engineering findings:

1. **An Action is a single transaction.** "An action is a single transaction that changes the properties of one or more objects." Edits computed by an Action's rules/function are collected and applied as one atomic transaction by the Actions service. [Documented, High]
2. **Two rule families.** Ontology rules (create/modify/delete object, add/delete link) and side-effect rules (notifications, webhooks, schedule builds). When multiple Ontology rules touch one object, the backend "compiles rules to generate a single edit per object" with last-writer-wins per property. [Documented, High]
3. **The function rule is exclusive.** "When this rule is present, no other rule may be configured." A function-backed Action derives the function's inputs from Action parameters; the function returns a list of Ontology edits. [Documented, High]
4. **Edits API is explicit in v2/Python, implicit in v1.** TS v1 uses `@OntologyEditFunction`/`@Edits` with a `void` return; TS v2 uses `createEditBatch` from `@osdk/functions` and returns `batch.getEdits()`; Python uses `FoundryClient().ontology.edits()` and `get_edits()`. [Documented, High]
5. **The write path is index-first, persist-later.** On Action submit the Actions service sends a modification instruction to Funnel, stored in an offset-tracked queue; the edit is applied to the live object-database index immediately and flushed to a Funnel-owned merged dataset periodically (on new datasource transaction, or every 6 hours if edits exist). [Documented, High]
6. **Concurrency.** OSv1 (Phonograph) used object-version checks and threw `StaleObject` on conflict; OSv2 loads objects at consistent versions throughout an `/apply` and reduces StaleObject conflicts at the cost of weaker guarantees. Datasource-vs-user-edit conflicts are resolved by configurable strategies ("Apply user edits" default, or "Apply most recent value" requiring a UTC timestamp property). [Documented, High]
7. **Bulk limits.** Up to **10,000 objects** edited in a single Action and up to **50 object types**; per the "Ontology query compute" page, "OSv2 supports also on-demand Spark cluster searches when running search-arounds on over 100,000 objects, or running writeback operations on over 10,000 objects in a single request." [Documented, High]
8. **Function limits.** Per the "Enforced limits" page, "Each Function execution is limited to 30 seconds of CPU time, but if loading data over the network, can run for up to 60 seconds" and "is limited to 128 Megabytes of memory usage" (TS v1); the 60 s elapsed limit is configurable; serverless functions default 1024 MiB (configurable 512–5120 MiB); object loads capped at 100,000 per `.all()`. [Documented, High]
9. **Metering is fixed-overhead + scaling.** Per the "Ontology query compute" page: "Each action has a compute-second overhead of 18. Actions also scale with the number of objects that are edited in the write-back request, incurring an additional 1 compute-second per object edited beyond the first," and "each function execution has a fixed overhead of 4 compute-seconds." Ontology query overhead: 4 (OSv2) / 16 (OSv1). [Documented, High]
10. **Phonograph EOL.** Per the Object Storage V1 (Phonograph) doc page, "Object Storage V1 (Phonograph) is in the planned deprecation phase of development and will be unavailable after June 30, 2026." Any write-path facts that depend on Phonograph are legacy. [Documented, High]

## 2. Action Type Anatomy & Lifecycle

**Definition.** An action type is "the definition of a set of changes or edits to objects, property values, and links that a user can take at once. It also includes the side effect behaviors that occur with action submission." [Documented, High] It is authored in the **Ontology Manager** (Action types tab, or "Create new" from an object type). To "create, configure, or edit an action, a given Palantir Foundry user must belong to the actions-admins group." [Documented, High]

**Anatomy.** An action type consists of:

- **Overview** — API Name (unique ID; "cannot be edited after saving"), Display Name, Description, Status. [Documented, High]
- **Rules** — Ontology edit logic and side effects (Section 4).
- **Parameters / Form** — inputs and the auto-generated form (Section 3). "A Form component is automatically generated based on the Action definition." [Documented, High]
- **Security & Submission Criteria** — gating conditions (Section 5).
- Optional: Sections (form grouping), Inline edits, Action log, Action metrics.

**RID & API name format.** Action types carry a Resource Identifier of the form `ri.ontology.main.action-type.<uuid>` (e.g., `ri.ontology.main.action-type.7ed72754-7491-428a-bb18-4d7296eb2167`). The API name is a stable camelCase-style identifier (e.g., `promote-employee`, `rename-employee`). The applied-action operation returns an `operationId` of the form `ri.actions.main.action.<uuid>`. [Documented, High]

**Status / lifecycle.** The release status enum is **ACTIVE, ENDORSED, EXPERIMENTAL, DEPRECATED** (per the API reference); Ontology Manager surfaces statuses active / experimental / deprecated / example (and "promoted" for object types only). New resources default to experimental; "Changing an API name is only possible for those marked as experimental"; an active resource "cannot be deleted" until experimental or deprecated. [Documented, High]

**Versioning / branching.** Action types can be loaded and applied against a Foundry **branch** (`?branch=ri.branch..branch.<uuid>`), described as "an experimental feature and not all workflows are supported." There is a dedicated "Branching action types" capability. Action reverts allow an Action to be undone immediately after application. [Documented, Medium]

**Exposure & invocation.** Actions are exposed to consuming applications (Workshop Button Group, Object Views Actions widget, Object Explorer dropdowns, Slate) by reference to the Action RID/API name; a form is auto-generated. Programmatically, actions are invoked via the **Apply Action** API and the OSDK `applyAction` (Section 12). In Object Explorer, bulk contexts show only actions accepting object list parameters of the correct type. [Documented, High]

## 3. Parameters — Complete Parameter-Type Table

Parameters "are the inputs of an action type … the interface between the Rules and other Foundry applications, such as Workshop, Slate, and Object Views." They can be referenced "in rules … in submission criteria … to access the current value of an object property before it is changed by the action or in overrides to change the configuration of a following parameter." [Documented, High]

**Supported parameter types** (verbatim from the Action types "Scale and property limits" page, which maps object-property base types to parameter types; some are OSv2-only):

| Property base type | Parameter type | Single | Array/List | Notes |
|---|---|---|---|---|
| Attachment | Attachment | Yes | Yes | 200 MB global file limit; max 10 object links per attachment |
| Boolean | Boolean | Yes | Yes | |
| Byte | Integer | Yes | Yes | |
| Cipher text | String | Yes | Yes | |
| Date | Date | Yes | Yes | |
| Decimal | Decimal | Yes | Yes | |
| Double | Double | Yes | Yes | |
| Float | Double | Yes | Yes | |
| Geopoint | Geopoint | Yes | Yes | |
| Geoshape | Geoshape | Yes | Yes | |
| Geotime series reference | Geotime series reference | Yes (OSv2) | Yes (OSv2) | |
| Integer | Integer | Yes | Yes | |
| Long | Long | Yes | Yes | |
| Mandatory control | Mandatory control | Not as property/action (single) | Yes (array) | Asymmetric |
| Media reference | Media reference | Yes (OSv2) | Not supported in actions (array) | Asymmetric |
| String | String | Yes | Yes | |
| Short | Integer | Yes | Yes | |
| Struct | Struct | Yes (OSv2) | Yes (OSv2) | |
| Timestamp | Timestamp | Yes | Yes | |
| Time series reference | Time series reference | Yes (OSv2) | Not supported (array) | Asymmetric |
| Vector | Double list | Yes (OSv2) | Not supported (array) | Asymmetric |

Note: there is no distinct "geohash" parameter type; the geo types are Geopoint, Geoshape, and Geotime series reference. Beyond property-backed parameter types, the parameter system also supports **object reference**, **object set**, and **interface reference** parameters (used by Modify/Delete rules and dropdowns). Submission criteria "do not support attachment and object set parameters." [Documented, High]

**Configuration limits:** primitive list parameter ≤ 10,000 elements; object-reference list parameter ≤ 1,000 elements; list parameter used in submission criteria ≤ 1,000 elements. Each individual object edit ≤ 32 KB (OSv1) / 3 MB (OSv2). Actions "cannot be used to edit the primary key of an object." [Documented, High]

**Validation / defaults / rendering / conditional logic / ordering:**

- **Constraints:** e.g., "User input," "Multiple choice" (enumerated allowed values), regex (e.g., `^[A-Z]{3}$`), object-dropdown filters and Search Arounds. The selected value "is also validated before the Action is executed." [Documented, High]
- **Default values:** static value, property of an object reference parameter, or "local"/environment values (current user, current timestamp, current object). "Local default values (for example, Workshop variables) always take precedence over global default values." [Documented, High]
- **Visibility:** Visible / Hidden / Disabled (read-only). [Documented, High]
- **Conditional logic (overrides):** Override blocks have an "if" (conditions) and "then" (overrides). "Every parameter can contain multiple override blocks, however, if more than one is true, only the first one will be executed." Override conditions can only reference parameters that "appear above the current parameter in the form hierarchy." [Documented, High]
- **Ordering / grouping:** Sections group parameters into one or two columns, can be collapsible/hidden, support conditional overrides. [Documented, High]

**Accessing the current property value before the change.** The pattern is to bind a hidden parameter to the current property value (e.g., a Workshop variable `previous_status` capturing the current Status), passing both the prior and new values into the rules. The parameter system is explicitly designed "to access the current value of an object property before it is changed by the action." [Documented, High]

**Binding to Workshop/Slate/Object Views.** Default values are bound from Workshop module variables ("Active object"), Object View environment variables ("Current object"), and Slate. The auto-generated form renders each parameter as a field. [Documented, High]

## 4. Rules — Edit Rules and Side-Effect Rules

"Rules define the logic of the action type that transform the parameters into Ontology edits or other effects. There are two main types of rules: ones that edit the Ontology, and ones that trigger another effect in Foundry." [Documented, High]

### Capabilities table

| Rule | Capability | Constraints |
|---|---|---|
| Create object | "create an object of a predefined type. The primary key … is a required property which has to be filled." Additional properties optional. Can create many-to-many links at creation. | Cannot create an object twice in one submission |
| Modify object(s) | Modify an existing object "whose primary key is derived from object reference parameters." | "cannot reference an object created as a part of the current action"; cannot modify primary key |
| Delete object(s) | Delete object passed via object reference parameter | Cannot delete before add/modify |
| Add/Delete link (M:N) | Add/delete many-to-many link between objects from object reference parameters | One-to-many/one-to-one links require modifying the foreign key property via Modify object |
| Function rule | "reference an Ontology edit function whose inputs are derived from parameters of the action" | **"When this rule is present, no other rule may be configured since function code alone is capable of handling everything that other rules can do."** |
| Interface create/modify/delete/link | Create/modify/delete/link objects of types implementing an interface | Modify/delete only on shared properties; primary key cannot be modified |
| Notification (side effect) | Send notification; functions can compute recipients/content | Sent after edits applied; content rendered from pre-edit state. Per the Scale-and-property-limits page: "a maximum of 500 recipients can [be] notified in a single action. This limit is reduced to fifty recipients when notifications content is rendered 'From a function.'" |
| Webhook (side effect or writeback) | Call external system | Configurable before ("writeback") or after ("side effect") edits |
| Schedule build (advanced) | Trigger a schedule build | "Foundry applies Ontology edits after the build begins" |

**Setting properties from parameters/expressions.** A property can be set from a parameter, an object-parameter property, a static value, or contextual Current User/Time (string/timestamp only; non-interactive). [Documented, High]

**Primary key on create.** The primary key is a required field on Create object; for interface Create rules the interface property used as PK must be included or "an action will fail on submission." Actions cannot edit a primary key (equivalent to delete + create). [Documented, High]

**Multi-rule ordering & combined effects.** "When multiple rules are defined, the actions backend compiles rules to generate a single edit per object." Last-writer-wins per property: "if the result of one rule updates a property to 'A', but another rule … updates the same object's property to 'B', the resulting edit would just update the property to 'B'." Ordering constraints: cannot delete before add/modify; cannot modify before add; cannot create twice. [Documented, High]

**Side-effect ordering & failure semantics.** Notifications are "sent once all action edits have been applied"; "If notifications fail to send for whatever reason, edits may still succeed." Side-effect webhooks run after edits; writeback webhooks run before edits and provide partial transactionality: "Using a writeback webhook guarantees that if the request to the external system fails, no changes will be applied to the Foundry Ontology. However, it is still possible that the external request may succeed but Ontology changes could fail." Only one writeback webhook is allowed. If submission criteria fail, "side effects will not be triggered." [Documented, High]

## 5. Submission Criteria (formerly "validations")

"Submission criteria (formerly known as validations) are the conditions that determine whether an action can be submitted." They "consist of conditions and operators." A condition is "a single comparison check between two values" configured via one of two templates: **"based on current user"** or **"based on parameter."** "Actions can only be submitted if all the submission criteria are met." [Documented, High]

**Attributes used.** Object, relation/link, and user attributes. The Current User template checks user ID, group memberships (direct or inherited), or "any other multipass attribute" (treated as string lists). "Using the Other user attribute field, conditions can be configured against attributes the user does not have access to … If a user does not have access to an attribute, they will fail the condition." [Documented, High]

**VALID/INVALID & client-vs-server.** The **Validate Action** API returns `result: VALID|INVALID` with per-parameter `evaluatedConstraints` and a `submissionCriteria` array. Critically: "For performance reasons, validations will not consider existing objects or other data in Foundry. For example, the uniqueness of a primary key or the existence of a user ID will not be checked." Server-side enforcement occurs on Apply; client-side form validation is for UX only and must not be trusted as the sole gate. [Documented, High]

**Difference from parameter-level validation.** Parameter-level validation evaluates constraints on individual parameter values (type, allowed values, regex, dropdown filters). Submission criteria evaluate cross-parameter / user / object logical statements gating the whole submission. Both appear in the Validate/Apply response (`parameters` map vs `submissionCriteria` array, with `configuredFailureMessage` on failed criteria). [Documented, High]

**Relationship to governance.** Submission criteria "support encoding business logic into data editing permissions, ensuring Ontology data quality and editing governance." They are independent of the permission to edit the action type itself, and each action type has independent criteria. "Submission criteria do not support attachment and object set parameters." [Documented, High]

## 6. Function-Backed Actions & the Ontology Edits API

A function-backed Action references an **Ontology edit function**; "running an edit function outside of an Action will not actually modify any object data." The function must be published; the action connects to a chosen minimum function version (auto-upgrade optional). "If auto upgrades are enabled … users who do not have edit permissions on the action can modify the action's behavior by making changes to the backing function." Provenance is set by the minimum function version; edits outside that provenance cause failure. [Documented, High]

**Input derivation & exclusivity.** The function's inputs are derived from action parameters; "When this rule is present, no other rule may be configured." [Documented, High]

### Edits API surface (verified against docs)

**TypeScript v2 — `@osdk/functions`:**
- Declare edited entities via the `Edits` type, joined with `|`: `type OntologyEdit = Edits.Object<Employee> | Edits.Link<Employee, "assignedTickets"> | Edits.Interface<Person>;`
- Construct batch: `const batch = createEditBatch<OntologyEdit>(client);`
- Methods: `batch.create(Ticket, { ticketId, dueDate })` (PK supplied as a named field in the literal; interface creates use `$objectType`); `batch.update(employee, { lastName })` (or by `{ $apiName, $primaryKey }`); `batch.delete(ticket)`; `batch.link(employee, "assignedTickets", target)`; `batch.unlink(...)`. One-to-one/one-to-many links are changed by `batch.update` on the foreign-key property (e.g., `batch.update({ $apiName: "Ticket", $primaryKey: 13 }, { assignedEmployeeId: 52 })`).
- Return: `return batch.getEdits();` (function returns `OntologyEdit[]`). Note the methods are `link`/`unlink`, not `addLink`/`removeLink`. [Documented, High]

**Python — `functions.api`:**
- Decorate `@function(edits=[Employee, Ticket])`, return `list[OntologyEdit]`.
- `ontology_edits = FoundryClient().ontology.edits()`
- `new_ticket = ontology_edits.objects.Ticket.create(ticket_id)` (PK as first positional arg; properties may be passed as kwargs, e.g., `create(ticket_id, due_date=new_due_date)`); `editable = ontology_edits.objects.Employee.edit(employee)` then assign properties; multi-links via `editable_employee.assigned_tickets.add(...)` / `.remove(...)`, single-links via `.set(...)` / `.clear()`; delete via `ontology_edits.objects.Ticket.delete(ticket)`.
- Return: `return ontology_edits.get_edits()`. [Documented, High]

**TypeScript v1 — `@foundry/functions-api` + `@foundry/ontology-api`:**
- Decorate with `@OntologyEditFunction()` and `@Edits(Aircraft, Employee)`; return type `void`/`Promise<void>`.
- Create: `const newTicket = Objects.create().ticket(ticketId);` (typed factory; PK as argument). Modify: direct property reassignment (`employee.lastName = newName`). Delete: `ticket.delete()`. Links: `.add()`/`.remove()`/`.set()`/`.clear()`.
- Edits are captured implicitly; "the true return type of the function is a list of Ontology edits." Unique IDs via `Uuid.random()` from `@foundry/functions-utils` (not `functions-api`). The `@Edits` decorator declares edited object types up front so permissions can be enforced before the action runs. [Documented, High]

**Edit collapsing.** "Edits are collapsed intelligently so that the minimal set of edits are applied in an action … if you create a new object and then update its properties, a single Create Object edit will be returned." "The entire function must succeed in order to generate the list of edits which is passed to the actions service executing the atomic transaction." [Documented, High]

**Search-after-edit caveat.** "Changes to objects and links are propagated to the object set APIs after your function has finished executing … `Objects.search()` APIs will use the old objects." TS v2 makes this explicit via the edit batch; reading the property you just `update`d on the batch will not reflect the change later in the same execution. [Documented, High]

**Bulk/batched execution & partial failure.** Per the Scale-and-property-limits page: "An action can be called a maximum of 10,000 times in a batch. This limit is reduced to 20 when the action is function-backed and the function is not configured to use batched execution." With batched execution the function "must receive a single input parameter containing a list of structs"; "A batched action call will invoke a single function execution with several entries in the list input parameter"; "all edits are applied atomically at the end of the action call." In Automate's per-object execution, on failure "the object identifier surfaced … represents the object associated with the first request that caused the failure; there may be more hidden failures." [Documented, High]

**Atomicity & rollback.** The set of edits computed by an Action (whether from rules or a function) is applied as one atomic transaction by the Actions service. A function that throws produces no edits (whole-function-must-succeed). Cross-system writes are not transactional: an Ontology write can fail even if an external write succeeded. [Documented, High]

## 7. Writeback Path & Execution Semantics (Most Technical)

**Services.** The **Actions service** "is responsible for applying user edits to object databases." The **Object Data Funnel ("Funnel")** "orchestrat[es] data writes into the Ontology," reading from datasources and user edits and indexing into object databases. The **Object Set Service (OSS)** serves reads. The **Ontology Metadata Service (OMS)** defines types. [Documented, High]

**End-to-end write (OSv2).** "When an Action is triggered, the Actions service sends a modification instruction to the Funnel service. This instruction is stored in a Funnel-managed queue that has offset tracking to support simultaneous user edits. Object Storage V2 tracks these offsets for any object type and any many-to-many link type with join tables. The offsets are applied to the live indexed data in the object database; if an object read … happens after a user modification is sent, the object read is guaranteed to contain the user edits." [Documented, High]

**Durable vs ephemeral.** "All indexed data in object databases are considered ephemeral, requiring persistent storing of all Ontology data in other ways." User edits are persisted by a Funnel-owned **merged dataset** (joining datasource changelogs and recent user edits by primary key). The merge/build job is triggered "Whenever there is a new data transaction in object type datasources, or … every 6 hours, if edits had been detected." "user edits are applied to indexes in object databases immediately; a regular six-hour job interval allows a built-in control mechanism to persistently store this data in Foundry." [Documented, High]

**Near-real-time visibility.** Reads after a modification is sent are guaranteed to reflect the edit (read-your-writes at the index), but materialized datasets lag (automatic propagation "with a latency of a few minutes" if enabled). Funnel-managed metadata columns (e.g., `__is_deleted`, `__patch_offset`) appear in materialized datasets for deduplication and "should not be used in production workflows." [Documented, High]

**Concurrency & conflict resolution.**

- *Transactionality during apply:* "Object instances may change over the course of applying an Action, so it is important to guarantee transactionality." In OSv2 "the Actions service always loads objects at the same versions throughout an Action /apply, but does not guarantee that objects read outside of edit generation have not changed." This "reduces the frequency of StaleObject conflicts, with a consequence of weaker guarantees with OSv2." [Documented, High]
- *OSv1 (legacy):* "the Actions server tracks the version of a loaded object … When a user edit is applied … the object version is included in the request … checks if any of the object versions have changed and will throw a StaleObject error." [Documented, High]
- *Cross-backend:* an action that edits OSv1 and OSv2 objects simultaneously is "cross-backend" and runs additional checks. [Documented, High]
- *User-edit vs datasource conflict:* configurable per datasource — "Apply user edits" (default; user edits always win) or "Apply most recent value" (requires a UTC `timestamp` property; the `date` type will not work). [Documented, High]
- *"Most recent transaction wins":* for incremental/changelog datasources, "the data of the row in the most recent transaction will be present in the Ontology" — explicitly "not related to how user edits and datasource update conflicts are handled." [Documented, High]
- *Concurrent edits to same object via inline edits:* "Actions will return an error if an inline edit attempts to edit the same object twice." [Documented, High]

**Bulk limits & Spark.** Single action: ≤10,000 objects, ≤50 object types; each per-object edit ≤32 KB (OSv1) / 3 MB (OSv2). Per the Ontology query compute page, OSv2 "supports also on-demand Spark cluster searches when running search-arounds on over 100,000 objects, or running writeback operations on over 10,000 objects in a single request." Higher limits available on request. [Documented, High]

**Sync vs async / idempotency / retries.** Apply is synchronous from the caller's perspective: "a 200 HTTP status code only indicates that the request was received and processed by the server. See the validation result in the response body to determine if the action was applied successfully." Automate scheduled monitoring uses "at-least-once execution semantics rather than exactly-once"; designers are told to "Implement idempotent operations." Retry semantics for the Actions service itself are not documented in detail. [Documented, High; service-internal retry Inferred, Low]

**Audit / edit history.**

- **Edit History widget** (OSv2): "an immutable audit trail of all changes … cannot be deleted or modified by end users, even if the corresponding ontology edits are reverted or deleted," showing "who changed what, when, and the previous vs. new values." Requires "Track user edit history" enabled on the object type. [Documented, High]
- **Action Log**: `[LOG]`-prefixed object types mapping one-to-one with action types; each submission "generates a single new object … automatically linked to all objects edited." Captures edited objects' PKs, optional summary, contextual properties. For function-backed actions the backing function "must have Edits provenance configured." [Documented, High]
- **OSv1 vs OSv2:** Migration "will not [preserve edit history] except for Action Logs"; edit history must be re-enabled in OSv2. There is no documented public API to fetch the full OSv2 edit history (community-confirmed gap). [Documented, High]
- Platform-wide **audit logs** (audit.2/audit.3) capture who/what/when/where, append-only. [Documented, High]

## 8. Functions: Types, Runtimes & Execution

**Categories of functions and consumption:**

| Category | Consumption |
|---|---|
| Read/query functions (`@Function`/`@function`) | Workshop variables, Slate, Object Views, OSDK, query-function API gateway |
| Edit functions (`@OntologyEditFunction`/edits) | Only via function-backed Actions |
| Functions on Objects (FOO) | Object-aware logic; derived columns; Workshop/Quiver/Map |
| Function-backed / derived properties | Workshop derived columns, Vertex/Map node styling (FunctionsMap/Record/dict return) |
| Functions on models | Wrap model inference (TS v1/v2/Python) |

Edit functions only mutate the Ontology when invoked through a function-backed Action; in Automate, "functions with ontology edit return types will not have the edits applied when used as effects." Note that "Linked-object" derived properties (a separate, newer object-type feature) are read-only and "cannot be edited by functions or actions." [Documented, High]

### Runtime comparison (TS v1 / TS v2 / Python)

| Dimension | TypeScript v1 | TypeScript v2 | Python |
|---|---|---|---|
| Runtime | Limited V8 runtime | Full Node.js (fs, child_process, crypto) | Python |
| OSDK support | No (uses `@foundry/*`) | Yes (first-class, `@ontology/sdk`, `@osdk/functions`) | Yes (`ontology_sdk`, `functions.api`) |
| Edit model | Implicit capture, `void` return, `@OntologyEditFunction`/`@Edits` | Explicit `createEditBatch`, return `getEdits()` | Explicit `.edits()`, return `get_edits()` |
| CPU limit | 30 s CPU (non-configurable) | governed by elapsed limit | governed by elapsed limit |
| Memory | 128 MB | serverless default 1024 MiB (512–5120); up to 5 GB | deployed default 2 GB; serverless configurable |
| vCPU | single thread | up to 8 vCPUs; worker_threads | multithreading (threading) |
| Dates | LocalDate/Timestamp | DateISOString/TimestampISOString (ISO 8601) | datetime |
| Migration | source | target (recommended) | — |

The v1→v2 migration path is documented: replace `@foundry/functions-api`/`@foundry/ontology-api` with `@osdk/functions`/`@ontology/sdk`, switch from implicit edits to `createEditBatch`/`getEdits`, and adopt ISO date strings. [Documented, High]

### Limits & metering table

| Limit | Value |
|---|---|
| Default elapsed run time | 60 s (configurable on function configuration page) |
| Live preview max | 280 s |
| TS v1 CPU time | 30 s (non-configurable) |
| TS v1 memory | 128 MB |
| Serverless memory | 1024 MiB default (512–5120 MiB) |
| Deployed Python memory | 2 GB default |
| Object load cap (`.all()`/`.allAsync()`) | 100,000 objects |
| Search arounds | max 3 at once |
| Concurrent fetches | max 10 (except batched link loading) |
| Automate function effects | up to 4 hours, async |
| **FOO fixed overhead** | **4 compute-seconds per execution** |
| **Action overhead** | **18 compute-seconds + 1 per object beyond the first** |
| Ontology query overhead | 4 (OSv2) / 16 (OSv1) compute-seconds |

Function metering components: "Overhead: Each function execution has a fixed overhead of 4 compute-seconds, regardless of what it does. Compute time: The vCPU time the function needs to execute. External calls: Calls to other parts of the platform … incur their own costs." [Documented, High]

**Execution environment.** "This logic is executed on the server side in an isolated environment." Serverless functions "only incur costs when executed" and run different versions on demand; deployed functions are "a long-running environment … scaled according to … request volume and occasionally restarted." Cold-start behavior follows the serverless model (provisioning of fresh isolated environments). Snapshot isolation: a function-backed action and queries within "receives this benefit" of a consistent Ontology snapshot (configurable: Default / Disable snapshots). [Documented, High; cold-start internals Inferred, Medium]

**Type system & I/O / @foundry SDK surface.** Inputs/outputs span primitives (with numeric aliases Integer/Long/Float/Double), objects, object sets, interfaces, structs, media, markings, and edits. FOO returns: TS v1 `FunctionsMap<ObjectType, CustomType>`, TS v2 `Record<ObjectSpecifier<ObjectType>, CustomType>`, Python `dict[ObjectType, CustomType]`. The in-function Ontology SDK surface includes `Objects.search()`, link traversal, `Objects.create()`, edit batches, and media operations (`getMetadataAsync`, `readAsync`, `extractTextAsync`, `transcribeAsync`). [Documented, High]

**Authoring/publishing/versioning.** Functions live in **Code Repositories** (templates per language); imported Ontology resources via Resource Imports; published by committing and tagging releases. "Auto upgrades are disabled for function versions of the form 0.y.z." Functions carry RIDs and are searchable in Ontology Manager (Functions tab). Unit-testing utilities exist (stub objects, verify Ontology edits, mock users/dates). [Documented, High]

## 9. External Integration & Side Effects

**Webhooks.** Configured on a Data Connection **Source** (typically REST API). Two modes:

- **Writeback** — runs *before* edits; "if the webhook execution fails, no other changes will be made"; only one writeback webhook allowed; output parameters usable in subsequent rules.
- **Side effect** — runs *after* edits.

Auth: REST API sources with OAuth 2.0 outbound applications; "Foundry manages the OAuth 2.0 authorization flow … passes the correct access token with every webhook call." OAuth 2.0 authorization-code grant triggers interactive per-user prompts (and is "not currently recommended for workflows run through automation or the Foundry API"); client-credentials grant can be chained within webhook calls. Functions can compute webhook inputs (returning a custom interface mapped to webhook params). [Documented, High]

**External functions / API calls.** "By default, functions are not allowed to call external APIs." A Data Connection **Source** must be configured with code-import enabled and exports enabled, then imported into the repository. "External functions may not currently be used to make arbitrary API calls from TypeScript code without first defining the request as a webhook in Data Connection" (v1 constraint). Serverless functions "support external sources using the client from the provided source object, but they do not support third-party clients. You must deploy your function to make external API calls with third-party clients." Egress is governed by direct-connection (Foundry worker) or agent egress policies. When calling webhooks from `@Query` functions, "the webhook must perform only Read API calls that do not mutate the external system." "Currently, there are no limits to the number of requests … from within an Ontology edit function, but existing functions resource limits still apply." [Documented, High]

**Runtime/cert differences (webhook vs function environments).** The documentation distinguishes the webhook (Data Connection source/agent) environment from the function runtime, and notes serverless vs deployed differences for third-party clients; precise certificate-trust differences between the two environments are not fully specified in public docs. [Documented partial; cert specifics Speculative, Low]

## 10. Automate & AIP-Tool Exposure

**Automate** "replaces Object Monitoring as the single entry point for all business automation." Conditions: time-based (cron + timezone), object-data (objects added/removed/modified in set; run on all objects; threshold crossed; streaming), or combined (with AND/OR nesting). Effects: actions, functions, notifications, logic. [Documented, High]

- **Headless runs:** effects execute "without a human"; functions in Automate run async up to 4 hours; edit-returning functions don't apply edits as Automate effects (must be wrapped in an Action). [Documented, High]
- **Latency modes:** live (within minutes, OSv2 required), scheduled (at-least-once), automation-dependent (single parent→child; multi-level chains unsupported). [Documented, High]
- **Execution semantics:** parallel automations run nondeterministically; per-automation effects can be sequential (stop on failure, per-object) or parallel; batching via "Execute once for each batch of objects." Cycle detection auto-disables looping automations (overridable). [Documented, High]
- **Monitoring/alerting:** action metrics (success/failure, P95 duration, 7-day run history, 30-day usage); failure classes include Function failure, User-facing function failure, Conflict failure, Unclassified. [Documented, High]

**AIP tool exposure (kinetic surface only).** Actions and Functions are exposed as **tools** to AIP Logic and AIP Agent Studio (now AIP Chatbot Studio):

- **Apply actions / Action tool:** "enables the LLM to use Actions to edit the Ontology." "Calling an AIP Logic function from an action is required for edits to be written back … The Ontology will not be edited unless the Logic function is executed from an action, even if the function contains an Apply action block."
- **Function / Call function tool:** LLM can call any Foundry function (TS/Python/Logic).
- **Object query tool:** scoped object-type read access.
- Native tool calling supports actions, object query, function, update application variable. "LLMs do not have direct access to tools; LLMs can only ask to use tools, and these tool calls are then executed by AIP Logic within the invoking user's permissions." [Documented, High]

## 11. Security, Governance & Audit Across the Kinetic Layer

- **Edits-only-via-actions (default).** "By default, new object types only allow edits via actions." For such types "the user submitting the action will only need Read access on the objects that are being edited … it is possible for users to create objects that they cannot view." Reopening edits (Forms/Explorer/API) requires writeback-dataset Edit permissions or passing the Restricted View edit policy. [Documented, High]
- **Action application requirements.** The user "must be able to view the edited object types and link types and their datasources, and pass the submission criteria." [Documented, High]
- **Submission criteria** are the user-facing gate (Section 5); enforced server-side on Apply.
- **Mandatory controls / markings.** Markings "restrict access by requiring a user to have a particular classification marking." Functions can edit `MandatoryMarking[]` / `ClassificationMarking[]` properties. [Documented, High]
- **Webhook side-effect permissions.** "Webhook side effects are not enabled by default"; require Data Connection plugin permissions; if submission criteria fail, side effects don't fire. [Documented, High]
- **Auto-upgrade governance risk.** With function-backed action auto-upgrade, a user with function (not action) edit rights "can modify the action's behavior." [Documented, High]
- **Edit history & action logs** provide the immutable audit trail (Section 7). [Documented, High]

## 12. Developer / API / SDK Surface

**Apply Action (v2):** `POST /api/v2/ontologies/{ontology}/actions/{actionApiName}/apply` with body `{"parameters": {...}}`; optional `?branch=`. Response includes `operationId`, `validation.result`, and per-parameter `evaluatedConstraints`/`result`/`required`. A 200 indicates receipt, not success — check `validation`. Scopes: `api:ontologies-read` + `api:ontologies-write`. Batch apply: `apply_batch` / batch endpoint (returns edits, not validations; max 10,000, or 20 for non-batched function actions). [Documented, High]

**Validate Action (v1 path shown):** `POST /api/v1/ontologies/{ontologyRid}/actions/{actionApiName}/validate`. Returns `result: VALID|INVALID`, `submissionCriteria` array (with `configuredFailureMessage`), and `parameters` map with `evaluatedConstraints`/`required`. "validations will not consider existing objects or other data in Foundry." Scope: `api:ontologies-read`. [Documented, High]

**OSDK action invocation (TypeScript):**
```
const result = await client(addReview).applyAction(
  { restaurantId: "restaurantId", reviewRating: 5, reviewSummary: "It was great!" },
  { $returnEdits: true },
);
if (result.type === "edits") { /* result.edits, addedObjectCount, modifiedObjectsCount, ... */ }
```
With `$returnEdits: true`, the response carries `edits` (array of `{type: "modifyObject"|..., primaryKey, objectType}`) plus counts (`addedObjectCount`, `modifiedObjectsCount`, `deletedObjectsCount`, `addedLinksCount`, `deletedLinksCount`). [Documented, High]

**Function invocation.** Query functions can be published and called through the API gateway; OSDK exposes generated function bindings; FOO consumed in Workshop/Quiver/Map. [Documented, High]

**Get Action Type API:** `GET /api/v2/ontologies/{ontology}/actionTypes/{apiName}` or `/byRid/{rid}`; returns apiName, displayName, status, description, RID. [Documented, High]

## 13. History & Patents

- **OSv1 → OSv2.** Phonograph (OSv1) is Foundry's original object database, handling indexing, edits, and writeback. OSv2 introduces the Funnel-mediated architecture (separating indexing and querying), enabling incremental indexing, tens-of-billions-scale object types, multi-datasource column/property-level permissions, and "up to 10,000 objects to be edited in a single Action." Per the Phonograph doc page, it "will be unavailable after June 30, 2026." [Documented, High]
- **Writeback-dataset → materializations.** OSv2 renames "writeback datasets" as "materializations" and makes them optional. [Documented, High]
- **TS v1 → TS v2 functions.** TS v2 became generally available "the week of July 28[, 2025]," bringing Node.js runtime, OSDK, and configurable resources. Python serverless/deployed modes and model-function ontology binding (from February 2026) are recent. [Documented, High]
- **Object Monitoring → Automate.** Automate is the "fully backwards-compatible product that replaces Object Monitoring." [Documented, High]
- **Patents.** Palantir holds patents relating to dynamic/ontology-based data systems and governed data editing; a specific patent enumeration for the governed-writeback / action-validation / function-execution mechanisms was not retrieved in this research and is recorded as a known unknown. [Known unknown]

## 14. Glossary

- **Action / Action type** — a transactional, governed unit of Ontology edit + side effects, and its definition.
- **Rule** — edit logic (Ontology rule) or side-effect logic within an action type.
- **Submission criteria** — conditions (formerly "validations") gating whether an action can be submitted.
- **Function-backed action** — action whose edits are computed by an Ontology edit function (exclusive rule).
- **Ontology Edits API** — the in-function API for create/update/delete/link edits (`createEditBatch`/`get_edits`/`@OntologyEditFunction`).
- **FOO** — Functions on Objects.
- **Actions service** — applies user edits to object databases.
- **Object Data Funnel ("Funnel")** — orchestrates writes/indexing into OSv2 object databases.
- **OSS** — Object Set Service (reads).
- **OMS** — Ontology Metadata Service (type definitions).
- **OSv1 / Phonograph** — legacy object backend (EOL 2026-06-30).
- **OSv2** — canonical next-gen object backend.
- **Materialization** — OSv2 optional dataset reflecting object state (formerly "writeback dataset").
- **Writeback webhook** — webhook running before edits with partial transactionality.
- **Inline edit** — cell-level edit using an action type bound to a single object/type.
- **Action log** — `[LOG]` object type capturing action submissions.
- **Compute-second** — Foundry's unit of metered compute.

## 15. Confidence & Gaps Register

| Claim | Evidence | Confidence |
|---|---|---|
| Action = single atomic transaction | Documented | High |
| Function rule exclusivity | Documented (Rules page) | High |
| Edits API method names (v1/v2/Python) | Documented (verified) | High |
| Write path: index-first, 6-hour flush | Documented (how-edits-applied) | High |
| 10,000 objects / 50 types / Spark >10k | Documented | High |
| Action metering 18 + 1/object; FOO 4 | Documented (query-compute-usage) | High |
| 60 s default / 30 s CPU v1 / 128 MB | Documented (enforced-limits) | High |
| Conflict strategies (user-edit vs most-recent) | Documented | High |
| Actions-service internal retry/idempotency | Not documented | Low (known unknown) |
| Function sandbox technology (container/runtime internals) | Inferred from serverless model | Low (known unknown) |
| Webhook vs function cert-trust differences | Partial | Low (known unknown) |
| Patent enumeration | Not retrieved | Unknown (known unknown) |
| Full parameter base-type list incl. object/interface reference details | Documented partial | Medium |

**Known unknowns & resolving sources:** (1) Actions-service retry/idempotency internals — would require Palantir Conjure specs or engineering talks. (2) Function sandbox isolation technology — engineering blog/AIPCon. (3) Exact webhook vs function certificate handling — Data Connection runtime docs. (4) Specific patents — USPTO/Google Patents search. (5) Object-reference/object-set/marking parameter base-type enumeration beyond the property-mapping table — the action-types parameter-overview page body.

## 16. Source Bibliography (Tier 1 — Palantir primary docs, accessed June 13, 2026)

- action-types/overview, getting-started, rules, parameter-overview, parameters-default-value, parameters-override, parameters-filter, configure-sections, submission-criteria, permissions, scale-property-limits, inline-edits, function-actions-overview/getting-started/batched-execution, side-effects/webhooks, set-up-webhook, action-log, action-metrics, actions-on-interfaces, upload-attachments, upload-media
- functions/overview, language-feature-support, getting-started, types-reference, enforced-limits, manage-functions, optimize-performance, use-functions, edits-overview, api-ontology-edits, typescript-v2-ontology-edits, python-ontology-edits, typescript-v2-migration, typescript-v2-getting-started, functions-deployed, api-calls, webhooks, functions-on-models, foo-getting-started, media
- object-edits/how-edits-applied, materializations, user-edit-history
- object-backend/overview, object-storage-v2-breaking-changes, osv1-osv2-migration; object-databases/object-storage-v1 (Phonograph EOL)
- object-indexing/funnel-batch-pipelines, funnel-streaming-pipelines
- object-link-types/allow-editing, base-types, derived-properties, metadata-statuses
- ontologies/query-compute-usage; resource-management/usage-types
- automate/overview, condition-objects, effect-settings, effect-actions, effect-notification, condition-evaluation-latency, errors, automation-dependencies, streaming
- API reference: actions/apply-action, actions/validate-action, action-types/get-action-type(-by-rid), list-action-types; ontology-sdk/typescript-osdk
- agent-studio/tools; logic/blocks, getting-started, compute-usage; aip/aip-features
- security/monitor-audit-logs; workshop/widgets-edits-history, actions-use, derived-properties

Tier 2/3: Palantir Developer Community threads (batched execution, edit history API gap, function timeout); github.com/palantir/foundry-platform-python (Action.validate/apply_batch docs).

---
*Methodology note: ~18 web searches plus targeted page fetches and one focused subagent (Edits-API signatures + parameter-type enumeration), followed by an enrichment pass that confirmed the verbatim sourcing of the metering, limits, and EOL figures. All version-specific facts are dated; OSv1/Phonograph and TS v1 are flagged as legacy throughout. Claims are tagged [Documented]/[Inferred]/[Speculative] with confidence; numeric limits and API names are quoted verbatim from primary Palantir documentation. Where the public record is silent (Actions-service retry internals, function sandbox technology, webhook-vs-function certificate handling, specific patents), those are recorded as known unknowns rather than fabricated.*
