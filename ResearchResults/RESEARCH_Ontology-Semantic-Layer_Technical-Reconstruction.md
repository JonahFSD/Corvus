---
**Artifact:** Deep-research output — technical reconstruction of Foundry's Ontology *semantic layer*.
**Produced:** 2026-06-13, by a deep-research agent run on `DEEP-RESEARCH-PROMPT_Ontology-Semantic-Layer.md`.
**Independent spot-check (by Claude, 2026-06-13):** Confirmed against primary sources — the **Ontology Metadata Service (OMS)**, **Object Data Funnel**, the **OSv1 (Phonograph) → OSv2** split, and the **dynamic-ontology patent family** (incl. **US12386803B2**, filed 2023-06-16, issued 2025-08-12, assignee Palantir). These hold up.
**Read with care:** the lowest-confidence material is OSv2's *concrete physical storage engines* (§4.2, §11) — the report correctly flags this `[Speculative]`; treat as unknown, not fact. The exact numeric limits (2000 properties, 70 datasources, 2 MB/s, etc.) are Palantir-specific *scale artifacts* — useful reference, **not** part of the essential model we must replicate.
---

# The Semantic Layer of Palantir Foundry's Ontology: A Technical Reconstruction

## 1. Executive Summary

The semantic layer of Foundry's Ontology is a microservice-based system that maps Foundry datasources (datasets, restricted views, streams, virtual tables) into typed **object types**, **link types**, **properties**, **interfaces**, and **value types**, indexes them into specialized object databases, and serves reads through a dedicated query service. The Ontology backend is explicitly described by Palantir as having three responsibilities — verbatim: *"Datasource management to feed the Ontology... Querying, searching, and aggregating objects from the Ontology... Orchestration of writing to the Ontology, including indexing of datasources and edits to Ontology objects."* The canonical components are: the **Ontology Metadata Service (OMS)** (schema/definition store), **object databases** (Object Storage V1/Phonograph [planned deprecation after 2026-06-30] and Object Storage V2), the **Object Data Funnel** ("Funnel," write orchestration), the **Object Set Service (OSS)** (read serving), and the **Actions** service (edits).

Key reverse-engineering findings:

1. The Ontology backend is a microservices architecture with three documented responsibilities (datasource management, querying/searching/aggregating, write orchestration) [Documented].
2. OMS and OSS are confirmed named services with documented roles; Object Data Funnel is the OSv2 write orchestrator [Documented].
3. OSv2 separates indexing from querying. Per Palantir's object-backend overview: *"Increased indexing throughput on the order of tens of billions of objects for a single object type."* It supports up to 2000 properties per object type and uses a Spark-based query execution layer for large Search Arounds/aggregations [Documented].
4. Phonograph (OSv1) is documented as tightly coupled to an "underlying distributed document store and search engine"; Palantir's own legacy docs name ElasticSearch as the indexer behind Phonograph's row/Table Search Service — verbatim: *"All text-type columns are processed by the default ElasticSearch indexer, which tokenizes strings on breaking non-word characters."* [Documented].
5. OSv2's specific commercial storage engines are not publicly named; documented signals ("search nodes," "hydration," "Spark-based query execution layer," "multi-modal storage backends") point to a Lucene-family search engine plus Spark over a columnar index [Speculative].
6. One-datasource-per-object-type was the OSv1 rule; OSv2 supports multi-datasource object types (MDOs, column-wise only) up to 70 datasources [Documented].
7. Link types are implemented three ways: foreign-key/property-backed (1:1, many:1), join-table-dataset-backed (many:many), and object-backed (links carry their own object type with properties) [Documented].
8. Security is woven into the semantic model via object security policies (row-level), property security policies (column-level), and mandatory control properties (markings/orgs/classifications), all enforced at the object-storage indexing level [Documented].
9. The read API is the Ontology API v2 (REST), with typed OSDK clients (TypeScript, Python, Java) generated via Developer Console; object RIDs use the `ri.phonograph2-objects.main.object.<uuid>` namespace even in v2 [Documented].

## 2. Conceptual Data Model

### 2.1 Object types & instances

An **object type** is a schema definition of a real-world entity/event; an **object instance** is one set of primary-key + property values, analogous to a dataset row. Each object type has: API name (programmatic), display name + plural display name, description, icon/color, RID (`ri.ontology.main.object-type.<uuid>`), status (experimental/active/deprecated), groups, a primary key, and a title property. Object instances carry a `__rid` (`ri.phonograph2-objects.main.object.<uuid>`), a `__primaryKey`, and `__apiName` in API responses [Documented].

**Primary key:** the property uniquely identifying each instance; must be unique per row in the backing datasource. In OSv2 duplicate PKs within one transaction fail indexing; across transactions the later transaction wins. PKs should be deterministic (non-deterministic PKs lose edits/links). The following types cannot be primary keys: Geopoint, Geoshapes, Arrays, Time series, and real-number types (decimal, double, float) [Documented].

**Title property:** a display-name property (e.g., full name) shown across applications [Documented].

**Status/lifecycle:** active, experimental (default), deprecated — a signal to builders [Documented].

### 2.2 Property base types (complete table)

"All field types are valid base types except for `Map` and `Binary` types" [Documented]. Documented base types:

| Base type | Title key? | Primary key? | Notes |
|---|---|---|---|
| String | Yes | Yes | — |
| Integer | Yes | Yes | — |
| Short | Yes | Yes | — |
| Long | Yes | Discouraged | JS representation issues >1e15; recommend String for PK |
| Byte | Yes | Discouraged | Assignable in Actions only via Integer parameter |
| Boolean | Yes | Discouraged | Limits to two instances as PK |
| Float | Yes | No | — |
| Double | Yes | No | — |
| Decimal | Yes | No | OSv2 requires precision & scale set |
| Date | Yes | Discouraged | — |
| Timestamp | Yes | Discouraged | UTC; used for "apply most recent value" conflict resolution |
| Array | Yes (if inner valid) | No | No null elements; nested arrays unsupported in OSv2; max 100,000 elements |
| Struct | No | No | Depth one, cannot nest, fields cannot be arrays, ≥1 field; indexed like Elasticsearch object fields |
| Vector | No | No | For semantic search; not allowed in arrays |
| Geopoint | Yes | No | "Lat, Long" comma-separated, no parentheses |
| Geoshape | No | No | — |
| Marking | No | No | Mandatory control |
| Cipher (text) | Yes | No | String encoded with Cipher |
| Attachment | No | No | Files for functions on objects |
| Media reference | No | No | Points to media item in a media set; use for data >12 MB |
| Time series | No | No | Not allowed in arrays |

The base-types page lists the "advanced" types (Vector, Geopoint, Geoshape, Attachment, Time series, Media reference, Cipher text, Struct) requiring special configuration; the properties-overview "Supported property types" table enumerates the primitives and their PK/title eligibility. Geohash is **not** a documented standalone base type (only Geopoint/Geoshape). String properties max 12 MB; arrays max 100,000 elements; exceeding fails indexing [Documented]. OSv2 disallows NaN/±infinity and empty strings (OSv1 silently converted empty strings to null) [Documented].

### 2.3 Value types (semantic types)

**Value types** are semantic wrappers around a field/base type comprising metadata + constraints (e.g., email regex, enums, ranges) that enforce validation in both Pipeline Builder pipelines and the Ontology. They are reusable across object types and pipelines, are permissioned, and are versioned (metadata + constraints; breaking and non-breaking edits). Unlike base/field types (static, domain-agnostic), value types are created dynamically within a space. Inspired conceptually by RDF/OWL/XSD typing. Properties with value types cannot be converted to derived properties [Documented].

### 2.4 Struct, array, derived/computed

- **Struct:** schema-based multi-field property from a struct-type dataset column; depth one, no nesting, fields cannot be arrays, ≥1 field [Documented].
- **Array:** multiple values of a base type; no nested arrays, no null elements (OSv2) [Documented].
- **Derived properties:** computed at runtime from other properties or linked objects (linked-property selection or aggregations: count/avg/sum/min/max/approx-or-exact cardinality/collect list/collect set), traversing up to 3 link levels. Read-only; use security of all objects involved; cannot be PK, required, value-typed, or have constraints/formatting. Not available on OSv1-indexed object types; usable via OSDK `withProperties` (TypeScript `@osdk/client` ≥2.2.0-beta.x). Workshop sorting of object sets using derived properties limited to 200 rows (function-backed columns: 1000) [Documented].

### 2.5 Geospatial, time series, sensor, media, attachment, marking

- **Geopoint/Geoshape** base types; OSv2 has stricter geopoint validations [Documented].
- **Time series property (TSP):** added directly to an object type when all objects have that series; backed by a time series sync; a default TSP is designated. OSv2 required to back a TSP with multiple time series syncs (qualified series IDs) [Documented].
- **Sensor object types:** advanced config where a sensor object holds one time series per linked sensor; linked to a root object type via a link type carrying special metadata; supports units/interpolation (LINEAR/NEAREST/PREVIOUS/NEXT/NONE). Replaces deprecated "Measures." TSPs cannot be primary keys [Documented].
- **Geotemporal series (geotime/track):** geotemporal series reference (GTSR) property referencing a series in a geotemporal series integration, indexed into Foundry's geotemporal series database [Documented].
- **Media reference:** JSON pointing to mediaSetRid/mediaSetViewRid/mediaItemRid; backed by a dataset with a media reference column [Documented].
- **Attachment:** files on objects for functions [Documented].
- **Marking:** mandatory-control base type [Documented].

### 2.6 API name vs display name

API name is the programmatic identifier (e.g., `startDate`); display name is human-readable (e.g., "Start date"). All object properties are referenced in queries by API name, not display name. Materialized datasets in OSv2 use property API names as the schema [Documented].

### 2.7 Interfaces

An **interface** describes the shape (properties + link type constraints + metadata) of an object type and provides polymorphism. Interfaces are abstract (no backing dataset, cannot be instantiated directly), shown with dashed icons. Object types implement interfaces by mapping local properties onto required interface properties (optional properties may be skipped). Interfaces can extend multiple interfaces (multi-level inheritance); object types can implement multiple interfaces. Interface properties can be defined locally (recommended) or via shared properties. OSS searches against an interface return matching implementing object types. Support: Ontology Manager, Marketplace, TypeScript v2 functions, OSS search/sort (aggregation by interface in development), TypeScript OSDK (Java/Python in development), interface link types (in development) [Documented].

### 2.8 Shared properties

A **shared property** is a property reusable across multiple object types for consistent modeling and centralized metadata; can satisfy interface properties [Documented].

### 2.9 Per-object/property metadata

Properties carry: base type, description, RID, status, API name, keys (PK/title), value formatting (numeric/date/time/user-ID/resource-ID), render hints (e.g., searchable, sortable — deselecting improves reindex performance), visibility (prominent/normal/hidden), conditional formatting, type classes. Object types carry icon/color, groups, descriptions [Documented].

### 2.10 Worked example

Employee object type: apiName `employee`, primaryKey `[employeeId]` (Integer), properties `fullName` (String, title), `office` (String), `startDate` (Date), RID `ri.ontology.main.object-type.<uuid>`. Backed by an HR directory dataset (one row = one Employee). Linked to Company via `employer` foreign key (many Employees : one Company). A `directReport` link enables traversal. Security: a PII property security policy on `address`; an object security policy gating VIP rows by the VIP marking [Documented].

## 3. Backing Data & Materialization Model

### 3.1 Datasource → object-type

Property values come from backing datasources added in Ontology Manager. Columns auto-map to properties (property ID/display name/base type inferred from column name). Base type must match the backing column type [Documented].

**One-datasource-per-object-type:** In OSv1 a single datasource backs one object type (error `Phonograph2:DatasetAndBranchAlreadyRegistered` if reused). OSv2 introduced **multi-datasource object types (MDOs)** — column-wise only (join-like; distinct property subsets from different datasources, enabling column-level access control). Row-wise MDOs are not supported (use restricted views). MDOs support only datasets/restricted views (no streams), support edits/materializations, and are limited to **70 datasources** (only object-storage syncs count, not media sets / time series syncs) [Documented].

### 3.2 Excluded backing column types

Map and Binary field types are not valid base types. OSv2 forbids nested arrays and null array elements; disallows NaN/±infinity and empty strings; enforces datatype coherence between datasource and object schema on every sync [Documented].

### 3.3 Streams, restricted views, virtual tables, edit-only

- **Streams:** Ontology streaming supported only by OSv2; Funnel streaming pipelines use Flink "exactly once" checkpointing (default checkpoint frequency once/second dominates latency); preserve input ordering; support create/update/delete; cannot be cancelled; no edits on stream-backed object types [Documented].
- **Restricted views:** row-level security inherited by objects; in OSv1, to view RV-backed objects you need the object type permission + satisfy RV markings (not necessarily RV view) [Documented].
- **Virtual tables:** pointers to external tables (Delta/Iceberg etc.) usable to back object types without ingest; update detection via polling; objects reindex when source updates detected [Documented].
- **Edit-only properties:** Ontology properties not mapped to a backing column; permissioned to one backing dataset; can later be mapped to a column. Object types can be created without an existing datasource in OSv2 (generates an empty dataset for permissions) [Documented].

### 3.4 Sync/indexing process

OSv1: a single sync job; incremental only for APPEND/UPDATE transactions; SNAPSHOT triggers full batch reindex; health checks on sync jobs. OSv2: Funnel batch pipelines (changelog job computes per-transaction diffs into Funnel-owned changelog datasets receiving APPEND transactions; merge-changes job joins changelog + recent user edits by PK), incremental by default, "most recent transaction wins," `is_deleted` boolean honored. Schema/branch changes or replacement pipelines trigger reindex; jobs auto-retry on transient failure (~5 min) or on new data after terminal failure. RV-backed object types reindex when data or policy changes [Documented].

## 4. Storage & Indexing Architecture (most technical)

### 4.1 OSv1 (Phonograph) [planned deprecation after 2026-06-30]

Foundry's original object database: indexes/manages data, tracks user edits, serves searches/aggregations, orchestrates writeback. Documented as tightly coupled to an "underlying distributed document store and search engine." Palantir's legacy Slate writeback docs name **ElasticSearch** as the indexer behind the Phonograph Table Search Service — verbatim: *"All text-type columns are processed by the default ElasticSearch indexer, which tokenizes strings on breaking non-word characters"* and search syntax "similar to ElasticSearch search syntax" [Documented]. Stores data "in a distributed set of indices in a durable, horizontally scalable cluster" [Documented]. Datasource must be "registered" before querying; writeback datasets required for edits; index pruning minimizes "hits." No Cassandra reference found in any located source [Speculative that Cassandra is involved].

### 4.2 OSv2

Re-architected from first principles to separate indexing from querying for horizontal scale. Documented capabilities: incremental indexing by default; tens of billions of objects per object type; column/property-level permissions via MDOs; up to 10,000 objects edited per Action (higher on request); reduced edit latency; migrate edits after breaking schema changes; streaming datasources; **max 2000 properties per object type**; Spark-based query execution layer for high-scale Search Arounds and more accurate aggregations. Verbatim on the Search Around cap: *"By default, the Search Around limit is 100,000 objects. If your use cases require a higher scale Search Around of over 100,000 objects, contact Palantir Support."* Stores objects in "an enhanced indexing format optimized by Palantir." The query-compute docs state the Ontology "stores data in multi-modal storage backends that each have their own purposes and can be flexibly queried in a single request"; the May-2023 GA note describes backing object storage "with multiple data storage types in parallel" [Documented]. Verbatim on throughput: *"Indexing throughput is limited to 2 MB/s per object type into the Object Storage v2 object database."* Verbatim on index sizing: *"in the OSv2 data store this would be the disk space of the search nodes. If there is not enough disk space, indexing jobs will not succeed."* An indexing step called "hydration" downloads index files onto search-node disks [Documented].

**Specific engines [Speculative]:** Palantir does not publicly name OSv2's commercial engines. "Search nodes"/"hydration" semantics resemble a Lucene-family engine (Elasticsearch/OpenSearch) for full-text/typeahead/point lookups; a Spark-based execution layer (documented) over a columnar/Parquet-style index handles large aggregations/Search Arounds; a separate KV/document store for canonical state and Funnel offsets is plausible but unconfirmed. No evidence located for Cassandra/FoundationDB in OSv2.

### 4.3 Object Data Funnel

"Funnel" is the OSv2 microservice orchestrating writes into the Ontology: it reads from datasources (datasets, restricted views, streaming) and user edits (from Actions) and indexes into object databases, keeping data current. Funnel batch pipelines = series of Foundry build jobs (changelog → merge changes → index/hydrate). Funnel owns/controls intermediate changelog and merged datasets (not user-accessible). On an Action, the Actions service sends a modification instruction to Funnel, stored in a Funnel-managed queue with offset tracking (supporting concurrent edits; OSv2 tracks offsets per object type and per many-to-many join-table link type). Edits applied immediately to the index, periodically flushed to a persistent merged dataset (built on new datasource transactions or schedule). Indexed data in object databases is ephemeral; persistence is via datasources + Funnel datasets [Documented].

### 4.4 Query compute

Object queries (filters, aggregations, Search Arounds, writeback) run against object sets. Index "pruning" traverses large data structures to avoid scanning records ("hits"); claimed up to 1000x fewer records evaluated. OSv2 adds on-demand Spark clusters for Search Arounds >100,000 objects or writeback >10,000 objects. Metering: fixed overhead + scaling compute-seconds; Actions have 18 compute-second overhead +1/object beyond the first; functions-on-objects 4 compute-second fixed overhead. Indexing uses a parallelized Spark backend (driver+executors), measured in compute-seconds; changelog strategies reduce work [Documented].

### 4.5 Consistency & conflict

OSv2 "most recent transaction wins" by PK; user-edit vs datasource-update conflict resolution configurable per datasource: "Apply user edits" (default) or "Apply most recent value" (requires a UTC timestamp property). List Objects endpoint does not guarantee consistency across pages. Edits visible near-real-time; Analyze-using-SQL on materializations may lag ~30s [Documented].

### 4.6 Scale & limits (quoted)

- Max **2000 properties** per object type [Documented].
- Search Around default limit **100,000 objects** [Documented].
- Up to **10,000 objects** per Action [Documented].
- **70 datasources** per object type [Documented].
- String property **12 MB**; array **100,000 elements** [Documented].
- Indexing throughput **2 MB/s per object type** [Documented].
- OSv1 read endpoints cap at **10,000 objects** (`ObjectsExceededLimit`); no limit on OSv2 [Documented].
- Soak period during migration up to **14 days** [Documented].
- Ontology SQL: results truncated at **10,000 rows**, query timeout **20 seconds**, queue up to 6s [Documented].

## 5. Object Sets & Query/Search Surface

### 5.1 Object set abstraction

An **object set** is a saved/temporary query over objects, served by OSS. Definition: static (list of PKs, fixed) or dynamic (saved filter representation, updates as data matches). State: temporary (handed between apps, creator-only, RID like `ri.object-set.main.temporary-object-set.<uuid>`, expires within 24 hours) or permanent (stored for reuse). Composition via base/filter/search-around operations [Documented].

### 5.2 Object Set Service (OSS)

Confirmed: OSS serves reads — searching, filtering, aggregating, loading. OSS determines which compute engine executes a query (compute engine abstraction; some queries run in Spark). OSS APIs lack query-string support (OSv1 had it); cardinality metrics unsupported on mixed OSv1+OSv2 object sets [Documented].

### 5.3 Search/filter/aggregation/pagination

- **Search:** POST `/api/v2/ontologies/{ontology}/objects/{objectType}/search` with a `where` clause (eq, lt, isNull, etc.); queries at most three levels deep; tokenization on whitespace/punctuation [Documented].
- **Aggregation:** POST `.../objects/{objectType}/aggregate` or `/objectSets/aggregate` with aggregation specs (min/avg/etc.), `where`, `groupBy` (including range groups) [Documented].
- **Link traversal:** GET `.../objects/{objectType}/{pk}/links/{linkType}` and `.../{linkedPk}` [Documented].
- **Pagination:** `pageSize` (default 1000, max 10,000), `nextPageToken` opaque cursor [Documented].
- Typeahead/geo/temporal supported via property render hints and OSS; semantic search via Vector properties [Documented].

### 5.4 Sharing/caching/permissioning

Object sets saved as shareable resources; temporary sets creator-only/24h; reads enforce object + property security policies and backing-datasource permissions [Documented].

## 6. Security Model in the Semantic Layer

### 6.1 Two authorization levels

(1) Ontology resources (object/link/action type schema definitions), and (2) objects and links (the data). Resource access via Ontology roles / project permissions [Documented].

### 6.2 Object & property security policies

- **Object security policy:** row-level visibility of object instances; granular policies compare user attributes/properties/values; inherits mandatory controls from datasources; supports materialization (objects with OSP can only materialize to Foundry datasets, taking most-restrictive markings) [Documented].
- **Property security policy:** column-level; an OSP must exist first; PK cannot be in any property policy; a non-PK property in at most one property policy; properties not in any property policy are still covered by the OSP [Documented].
- Together provide cell-level security; managed directly in Ontology Manager independent of backing-datasource permissions [Documented].

### 6.3 Granular policies

Row-level rule sets used by restricted views and object security policies; template-based, converted to queries at request time; up to 10 comparisons; constant-vs-field weight 1, collection-vs-field weight 1000, total <10,000; no less/greater-than operators in OSPs; null policy-column rows inaccessible [Documented].

### 6.4 Mandatory control properties

A mandatory control property supports markings, organizations, and/or (with CBAC) classifications. Markings = mandatory access controls; user needs all markings to access. Constraints (allowed markings/orgs, max classification) enforced at the object-storage level — an object type violating constraints fails to index; invalid edits rejected at Action submit. Required properties can allow empty arrays (useful for mandatory controls). Markings propagate from backing data [Documented].

### 6.5 Restricted-view-backed permissions

Objects inherit RV granular permissions; RV combines policy definition + user attributes at a point in time; RV cannot be a transform input. OSv1: granular edit policies only for OSv1 object types not using "only allow edits via actions" [Documented].

### 6.6 Unauthorized rendering

If a user lacks Viewer permission on some MDO input datasources, properties from those datasources display as null, but the user can still see the object-type schema (access to object type controlled separately) [Documented].

## 7. Metadata, Versioning & Lifecycle

### 7.1 OMS

The **Ontology Metadata Service (OMS)** is "an overarching service that defines the set of ontological entities that exist" — object types, link types, action types, and more. OMS tracks incompatible OSv1 usage and alerts on migration; records ontology definition changes asynchronously (Funnel detects changes with a multi-second delay) [Documented].

### 7.2 Branching & proposals

The Ontology integrates with Global Branching: an **ontology proposal** (analogous to a pull request) is auto-created for branch changes, grouping all ontology resource changes under one proposal; reviewers approve per-resource tasks; merging the Global Branching proposal merges the ontology. Each branch is associated with a single ontology. Legacy ontology branches are being sunset in favor of global branches. Branch resources index for "preview"; indexing an object type counts as a modification (may require policy approval). OSv1-backed object types and Pipeline-Builder-created object types have branching limitations [Documented].

### 7.3 Schema migration / breaking changes

OSv2 enforces stricter validations than OSv1 (which inherited its data store's behavior). Breaking changes OSv1→OSv2: edits only via Actions; "writeback datasets" renamed "materializations" (required in OSv1, optional in OSv2); decimal properties need precision/scale; changelog "latest timestamp wins" not honored (OSv2 incremental by default). Migration is mandatory for all object types, can be incremental (mixed OSv1/OSv2 ontology), supports bulk migration, dual-indexes during a soak period (≤14 days; 0 deletes OSv1 immediately), routes all queries to OSv2 during soak. Changing PK/base type/backing datasource and changing a base type with incompatible existing values fails (`A property could not be cast to the new type`) [Documented].

### 7.4 One vs many ontologies

An ontology is mapped 1:1 with a space; created with the space, sharing org markings. Private (single org) or shared (multiple orgs, under a shared space). Ontology RID format `ri.ontology.main.ontology.<uuid>`; addressable by RID or API name (e.g., `palantir`) [Documented].

## 8. Developer / API / SDK Surface

### 8.1 Ontology API v2 (REST)

Base path `/api/v2/ontologies/{ontology}`. Representative endpoints:

| Operation | Method/Path |
|---|---|
| List ontologies | GET `/api/v2/ontologies` |
| Get ontology | GET `/api/v2/ontologies/{ontology}` |
| List/Get object types | GET `.../objectTypes`, `.../objectTypes/{type}` |
| List objects | GET `.../objects/{objectType}` |
| Get object | GET `.../objects/{objectType}/{primaryKey}` |
| Search objects | POST `.../objects/{objectType}/search` |
| Aggregate objects | POST `.../objects/{objectType}/aggregate` |
| Load object set | POST `.../objectSets/loadObjects` |
| Load objects or interfaces | POST `.../objectSets/loadObjectsOrInterfaces` |
| Aggregate object set | POST `.../objectSets/aggregate` |
| List/Get linked objects | GET `.../objects/{objectType}/{pk}/links/{linkType}[/{linkedPk}]` |

Response shapes include `__rid`, `__primaryKey`, `__apiName` (or `$`-prefixed for loadObjectsOrInterfaces, e.g., `$rid`, `$primaryKey`, `$objectTypeApiName`, `$interfaceTypeApiName`). Branch query param supported (experimental). Null properties not returned; vector properties returned only if selected. OAuth2 scope `api:ontologies-read` [Documented].

### 8.2 OSDK

The Ontology SDK generates typed clients (NPM/TypeScript, Pip/Conda/Python, Maven/Java, OpenAPI for others) via Developer Console; scoped tokens limited to selected ontology entities + user permissions. TypeScript v2 (`@osdk/client`) is directly invocable — `client(Restaurant).fetchPage({ $pageSize: 30 })` returns `PageResult<Osdk.Instance<T>>` with `nextPageToken`; `.where({...}).fetchPage()`, `$orderBy`, `.aggregate({$select:{$count:"unordered"}})`, `client(action).applyAction(args, {$returnEdits:true})`. v2 scales with ontology shape/metadata (lazy loading) vs v1 scaling with whole ontology. Python: `client.ontology.objects.X.where(...).page(page_size=..., page_token=...)`/`.iterate()`. `@osdk/react` hooks (`useOsdkObjects`, `useObjectSet`, `useLinks`, `useOsdkAggregation`) support pagination (`fetchMore`/`autoFetchMore`), `withProperties` derived props, and WebSocket `streamUpdates`. OSv1-backed reads cap at 10,000; OSv2 unlimited [Documented].

### 8.3 foundry-platform SDKs & repos

Public repos: `palantir/osdk-ts` (TypeScript OSDK libraries; supported Node 18.19+/20/22/24), `palantir/foundry-platform-python` (standalone platform APIs), `foundry-platform-typescript`. Auth via `@osdk/oauth` (`createPublicOauthClient`). Client construction: `createClient(foundryUrl, ontologyRid, auth)` [Documented].

### 8.4 Protocols/auth/limits

REST (Ontology API v2); WebSocket streaming via OSDK React hooks; OAuth2 bearer tokens + personal access tokens; Ontology SQL (Spark SQL dialect, OSv2 only, 10k-row cap, 20s timeout). Ontology SQL references object types by RID, properties by API name; many-to-many links queried via `ri.ontology.main.relation.<n>` with `<objectType>_<linkName>` foreign-key columns [Documented].

## 9. Link / Relationship Model

### 9.1 Cardinalities & implementation

| Cardinality | Implementation | Notes |
|---|---|---|
| One-to-one, many-to-one | Object-type foreign key (property → PK of other type) | Property-backed |
| One-to-many | Foreign key on the "many" side | Property-backed |
| Many-to-many | Join-table dataset (pairs of PKs) | Datasource backs the link itself; required for edit/writeback on M:N |
| (any, with link metadata) | Object-backed link type | A backing object type carries link + extra properties (e.g., Flight Manifest with Pilot/First Mate); supports restricted views |

A link type is analogous to a dataset join; a link to a joined row. M:N join tables map columns to each object type's PK. Object-backed links extend many-to-one, providing first-class object-type storage with metadata. Trade-offs: foreign-key links are cheapest but require a column on one side; join-table links enable arbitrary M:N and edits; object-backed links add link-level properties at the cost of an extra object type [Documented].

### 9.2 Directionality/metadata/limits

Link types carry RID (`ri.ontology.main.link-type...`/`relation`), status, the two object types, cardinality, per-side display name + plural display name. Changing M:N backing datasource, cardinality, foreign key, or deleting a link triggers reindex and may break dependent apps. OSv1 stores link edit history in Phonograph (reapplied on each writeback build); schema changes to edited link columns require unregister/reregister [Documented].

## 10. Glossary of Palantir-internal terms & service names

| Term | Definition | Source |
|---|---|---|
| OMS | Ontology Metadata Service — defines ontological entities | object-backend/overview [Documented] |
| Object databases | Services storing indexed object data (OSv1/OSv2) | object-backend/overview [Documented] |
| Phonograph (OSv1) | Legacy object DB; Elasticsearch-based; EOL after 2026-06-30 | object-databases/object-storage-v1 [Documented] |
| OSv2 | Next-gen canonical object store | object-backend/overview [Documented] |
| Object Data Funnel | OSv2 write-orchestration microservice | object-backend/overview [Documented] |
| OSS | Object Set Service — serves reads | object-backend/overview [Documented] |
| Actions | Service applying user edits | object-backend/overview [Documented] |
| Object set | Saved/temporary query over objects | object-backend/overview [Documented] |
| MDO | Multi-datasource object type (column-wise, OSv2) | object-permissioning/multi-datasource-objects [Documented] |
| Materialization | OSv2 optional dataset/RV output of object state | object-edits/materializations [Documented] |
| Value type | Semantic wrapper (constraints/metadata) over a field type | value-types-overview [Documented] |
| Interface | Abstract object-type shape (polymorphism) | interfaces/interface-overview [Documented] |
| Hydration | Downloading index files onto OSv2 search-node disks | object-indexing/faq [Documented] |

## 11. Confidence & Gaps Register

| Claim | Evidence | Confidence |
|---|---|---|
| OMS/OSS/Funnel named roles | Documented | High |
| Phonograph = Elasticsearch | Documented (legacy Slate page, verbatim "default ElasticSearch indexer") | Medium-High |
| Phonograph uses Cassandra | No source | Speculative/Low |
| OSv2 specific engines | Not named publicly | Speculative/Low |
| 2000 properties / 70 datasources / 100k Search Around / 10k edits / 2 MB/s / 12 MB string / 100k array | Documented (verbatim quotes captured) | High |
| Base-type table | Documented (two pages, minor inconsistencies) | High |
| Link implementations (FK/join/object-backed) | Documented | High |
| Object/property security policies | Documented | High |
| Patent US12386803B2 granted 2025-08-12 | Documented (Justia; priority US18/336,876 filed 2023-06-16) | High |

**Known unknowns (and the source that would resolve each):**

1. OSv2's concrete storage engines (search engine, columnar store, KV store) — would require a Palantir engineering blog/AIPCon talk or internal architecture doc.
2. Whether Phonograph also uses a KV/document store beyond Elasticsearch (e.g., Cassandra) — internal architecture doc.
3. Exact OSv2 consistency guarantees (read-after-write semantics formalization) — would require OSS/Funnel design docs.
4. Geohash as a distinct base type — not documented; only Geopoint/Geoshape confirmed.
5. Precise OSS object-set RID lifecycle/caching internals beyond temporary (24h) vs permanent.

## 12. History & Patents

The "dynamic ontology" concept originates in Palantir Gotham — a data model of object types and property types with parser definitions and validators, documented in a patent family: US7962495B2 → US8856153B2 → US9589014B2 → continuations US20150142766A1, US11714792B2, and US12386803B2. Per Justia, US12386803B2 ("Creating data in a data store using a dynamic ontology") was issued August 12, 2025, with priority application US18/336,876 filed 2023-06-16; inventors Akash Jain, Robert J. McGrew, and Nathan Gettings; assignee Palantir Technologies Inc. Claims cover storing an ontology of object types + object property types, parser definitions transforming input data into property-compatible form, and validators specifying permitted values/formats, with user-driven changes updating validators/parsers. Object types had URIs/base types/icons (e.g., `com.palantir.object.business` with base type `com.palantir.object.entity`) [Documented].

Timeline: Gotham dynamic ontology (2008–2013 patents) → Foundry Ontology (object/property/link/action types) → Phonograph (OSv1, Elasticsearch-based) → OSv2 GA (announced May 2023; incremental indexing, streaming, MDOs, Spark query layer) → interfaces, value types, shared properties, OSDK (TS v1 → v2 with lazy loading), derived properties, Ontology SQL → Phonograph planned deprecation after 2026-06-30 [Documented/Inferred].

## 13. Source Bibliography (by tier)

**Primary — Palantir docs (palantir.com/docs/foundry), accessed June 13, 2026:** object-backend/overview; object-backend/object-storage-v2-breaking-changes; object-backend/osv1-osv2-migration; object-databases/object-storage-v1; object-indexing/overview, funnel-batch-pipelines, funnel-streaming-pipelines, data-restrictions, faq; ontologies/query-compute-usage, compute-usage, ontologies-overview, shared-ontologies, test-changes-in-ontology, review-ontology-proposals, ontologies-proposals, ontology-branches-legacy; object-link-types/type-reference, base-types, properties-overview, property-metadata, create-object-type, edit-object-type, edit-link-types, link-type-metadata, create-link-type, edit-only-properties, required-properties, mandatory-control-properties, structs-overview, derived-properties, value-types-overview, value-types-versions, create-shared-property; interfaces/interface-overview, create-interface, implement-interface; object-permissioning/overview, managing-object-security, object-security-policies, configuring-rv-access-controls, multi-datasource-objects, object-and-property-policies; object-edits/how-edits-applied, materializations; time-series/*; geotemporal-series/concepts-glossary; ontology-sdk/overview, typescript-osdk, python-osdk, typescript-osdk-migration; api/v2 ontologies-v2-resources (list/get ontology, list/get/search/aggregate objects, load/aggregate object sets, linked objects); sql-warehousing/ontology-sql; resource-management/usage-types; slate/references-writeback; announcements/2023-05.

**Primary — patents (Google Patents/Justia):** US7962495B2, US8856153B2, US9589014B2, US20150142766A1, US11714792B2, US12386803B2 — "Creating data in a data store using a dynamic ontology" (inventors incl. Akash Jain, Robert J. McGrew, Nathan Gettings; assignee Palantir).

**Primary — GitHub/blog:** github.com/palantir/osdk-ts; github.com/palantir/foundry-platform-python; blog.palantir.com (Embedded Ontology / OSDK).

**Secondary:** deepwiki.com/palantir/osdk-ts; community.palantir.com; supplychaintoday.com; researchgate.net (Wikileaks dynamic-ontology slide).
