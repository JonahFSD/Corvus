# Bible Ontology + Semantic Layer — Build Spec v1

**Goal:** a typed graph of everything in the Bible, wrapped in a semantic (ontology) layer, exposed to an LLM as tools. The LLM never touches SQL. It calls objects and links.

**Stack decision (don't debate this):**
- One database: **Postgres + pgvector**. Graph = two tables (`nodes`, `edges`) + recursive CTEs. No Neo4j. No second DB.
- **Semantic layer** = a FastAPI service with ~8 typed endpoints. This is the whole product.
- **Text is never stored.** Bible text is fetched at runtime from YouVersion. Graph stores USFM refs only.
- LLM = Gloo AI (values-aligned, OpenAI-compatible, has a `tradition` param).

---

## 1. The one architectural rule

> **The graph stores references, not scripture.**

Node/edge IDs are USFM verse refs (`JHN.3.16`, `GEN.1.1`). That's YouVersion's own ID scheme, so the join is free, it's translation-agnostic, and you sidestep Bible licensing entirely. You are building an index, not a copy.

```
User → ChatGPT App → Semantic Layer (MCP tools)
                          ├─→ Postgres (ontology: nodes, edges, vectors)
                          ├─→ YouVersion API (verse text, on demand)
                          └─→ Gloo AI (reasoning + tradition alignment)
```

---

## 2. Ontology — Object Types

Palantir-shaped: Object Types, Link Types, Action Types.

| Type | Key | Notes |
|---|---|---|
| `Verse` | USFM `JHN.3.16` | atomic unit. Everything anchors here. |
| `Pericope` | `PER:...` | named passage span (Sermon on the Mount) |
| `Book`, `Chapter` | USFM | structural |
| `Person` | `PER:MOSES` | incl. divine persons, flagged |
| `Place` | `PLC:JERUSALEM` | lat/lng where known |
| `Group` | `GRP:PHARISEES` | nations, tribes, sects |
| `Event` | `EVT:EXODUS` | has fuzzy time bounds |
| `Object` | `OBJ:ARK_COVENANT` | physical things |
| `Theme` | `THM:GRACE` | abstract concept |
| `Claim` | `CLM:...` | a proposition asserted by a text |
| `Motif` | `MTF:LAMB` | symbol/image, drives typology |
| `Covenant` | `CVN:ABRAHAMIC` | |
| `Genre` | `GEN:APOCALYPTIC` | reading-mode hint for the AI |
| `Era` | `ERA:EXILE` | |

Every node: `{id, type, label, aliases[], props jsonb, embedding vector(1536)}`

---

## 3. Ontology — Link Types (the actual value)

Directional, typed, **and every edge carries metadata**:

```json
{
  "src": "MAT.2.15", "rel": "FULFILLS", "dst": "HOS.11.1",
  "confidence": 0.98,
  "source": "explicit_citation",     // explicit_citation | scholarly | algorithmic | llm_proposed | user
  "traditions": ["catholic","reformed","orthodox","evangelical"],
  "evidence": ["MAT.2.15"],
  "notes": "Matthew cites directly"
}
```

**Link types:**

*Textual*
`QUOTES`, `ALLUDES_TO`, `PARALLEL_TO` (synoptics), `VARIANT_OF`

*Theological*
`FULFILLS` / `PROPHESIES`, `TYPE_OF` (typology: Isaac → Christ), `ELABORATES`, `TENSION_WITH` ⭐

*Narrative*
`PRECEDES`, `CAUSES`, `PARTICIPATES_IN`, `LOCATED_AT`, `SPEAKS`, `ADDRESSED_TO`, `DESCENDANT_OF`

*Semantic*
`MENTIONS` (verse → entity, w/ char offsets), `ABOUT` (verse → theme, weighted), `INSTANCE_OF` (verse → claim), `SPEECH_ACT` (command / promise / warning / question / lament)

⭐ **`TENSION_WITH` is the differentiator.** Faith + works. Predestination + free will. Most Bible AI flattens hard passages into mush. Yours surfaces the tension *as a first-class edge* and answers: "these two texts pull against each other; here's how each tradition resolves it." That's the honest answer, and it maps directly onto Gloo's `tradition` parameter.

---

## 4. Schema (literally this)

```sql
CREATE TABLE nodes (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,
  label TEXT NOT NULL,
  aliases TEXT[],
  props JSONB DEFAULT '{}',
  embedding vector(1536)
);

CREATE TABLE edges (
  id BIGSERIAL PRIMARY KEY,
  src TEXT REFERENCES nodes(id),
  rel TEXT NOT NULL,
  dst TEXT REFERENCES nodes(id),
  confidence REAL DEFAULT 0.5,
  source TEXT NOT NULL,
  traditions TEXT[],
  evidence TEXT[],
  props JSONB DEFAULT '{}'
);

CREATE INDEX ON edges (src, rel);
CREATE INDEX ON edges (dst, rel);
CREATE INDEX ON nodes USING hnsw (embedding vector_cosine_ops);
```

That's it. Two tables. Traversal = recursive CTE.

---

## 5. Where the data comes from (don't hand-build 31,102 verses)

Seed order, all public domain or open-licensed:

1. **OpenBible.info cross-references** (CC-BY) — ~340k weighted verse links. Instant `ALLUDES_TO` / `PARALLEL_TO` backbone with a built-in vote score → your `confidence`.
2. **STEP Bible / Tyndale open data** — tagged people, places, Strong's numbers per verse. Gives `MENTIONS` for free.
3. **Nave's Topical Bible** (PD) — verse → `Theme` edges.
4. **Eusebian Canons** (PD) — gospel `PARALLEL_TO` links, ancient and accurate.
5. **NT-quotes-OT tables** (PD) — ~340 explicit `QUOTES` edges, confidence 1.0.
6. **LLM extraction pass** over a PD text (BSB/KJV) for `SPEECH_ACT`, `CLAIM`, `TENSION_WITH`, `TYPE_OF`. Tag `source: llm_proposed`, cap confidence at 0.6, and never let those alone drive an answer.

Steps 1–5 are downloads and a parser. You get ~80% of the graph in a weekend.

---

## 6. Semantic Layer API (= the MCP tools the AI gets)

Eight verbs. The model gets these, nothing else.

```
resolve(text)            → node ids  ("the guy who denied Jesus" → PER:PETER)
get_text(refs[], version)→ verse text via YouVersion
neighbors(id, rels[], k) → typed 1-hop expansion
path(a, b, max_hops)     → how are these connected? returns explained chain
theme_search(query, k)   → hybrid: vector seed + graph expansion
cross_refs(ref)          → ranked cross-references w/ reason for each
tensions(topic)          → passages in TENSION_WITH + per-tradition resolutions
timeline(entity)         → ordered events for a person/era
```

**Why a semantic layer instead of letting the LLM write Cypher/SQL:**
1. It can't invent a verse that doesn't exist — refs are validated against `nodes`.
2. Every response carries `provenance[]`, so the UI can render real citations.
3. You can change the DB without retraining/re-prompting anything.
4. Ontology is a contract: one schema file generates the TS types, the tool JSON schemas, and the DB DDL.

**Every tool returns the same envelope:**
```json
{ "results": [...], "provenance": [{"edge_id":..,"source":..,"confidence":..}],
  "contested": bool, "refs": ["JHN.3.16"] }
```

---

## 7. Query pipeline (the "smart answer" loop)

```
1. INTENT   Gloo model + ontology schema in prompt → {entities, link_types, intent}
2. RESOLVE  entities → node ids
3. SEED     pgvector top-k verses
4. EXPAND   k-hop along ONLY the link types the intent needs (2 hops max)
5. RANK     score = 0.5·cosine + 0.3·edge_confidence − 0.2·hop_penalty
6. HYDRATE  YouVersion GET /v1/bibles/{id}/passages/{usfm} for top ~12 refs
7. ANSWER   Gloo grounded completion, tradition param set, citations required
8. FLAG     if any edge has contested traditions → render "traditions differ" panel
```

Step 4 is why this beats plain RAG. Vector search finds *similar wording*. Graph expansion finds *theologically connected* passages that share no vocabulary at all — Genesis 22 to John 19, "lamb" to "Passover" to "crucifixion." No embedding model gets you that hop.

---

## 8. External APIs

**YouVersion Platform** — `https://api.youversion.com/v1/`
- Auth: `X-YVP-App-Key` header. Register at platform.youversion.com.
- `GET /v1/bibles/{version_id}/passages/{USFM}` → text
- `GET /v1/bibles` → available versions (after accepting license agreements)
- Pagination: `page_size` + `next_page_token`
- ⚠️ **Non-commercial terms.** Fine for a competition. Wrap it in a `BibleProvider` interface on day one anyway.
- ⚠️ Cache aggressively; never block a page render on it — 404 and hide the component on failure.

**Gloo AI** — `docs.gloo.com`
- OpenAI-compatible Responses / Completions APIs.
- `tradition` parameter for theological perspective — wire this straight to the `traditions[]` field on your edges. This is the single tightest integration point in the whole design.
- Search API / Data Engine if you want to ground on commentary content you upload.

---

## 9. ChatGPT App layer

Ship the semantic layer as an **MCP server**. The 8 tools above become the app's toolset.

UI components worth building:
- **Verse card** — text + translation switcher + the edges that made it show up
- **Graph mini-map** — the 2-hop subgraph that produced the answer (shows your work; this is the demo shot)
- **Tension panel** — side-by-side passages with per-tradition takes
- **Trace path** — "Passover lamb → John 1:29" rendered as an explained chain

---

## 10. Build order

| Day | Deliverable |
|---|---|
| 1 | Postgres + schema. Load 31,102 verse nodes from USFM index. |
| 2 | Parse OpenBible cross-refs + STEP tags → ~400k edges. |
| 3 | Embed all verses (batch, one pass). HNSW index. |
| 4 | Semantic layer: `resolve`, `get_text`, `neighbors`, `path`. |
| 5 | Query pipeline + Gloo grounded call. YouVersion hydration. |
| 6 | LLM extraction pass for `TENSION_WITH` + `TYPE_OF` on ~500 key passages. |
| 7 | MCP wrapper + UI components + demo. |

---

## 11. Non-negotiables

1. Never store Bible text. Refs only.
2. Every edge has `confidence` + `source`. No unattributed assertions.
3. Contested theology renders as contested — never as a single confident answer.
4. LLM proposals enter the graph quarantined (`source: llm_proposed`, conf ≤ 0.6).
5. No answer ships without verse refs the user can tap through to YouVersion.
