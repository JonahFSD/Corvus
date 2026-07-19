# claims.md — semantic claim ledger

The expensive pass: judgment, not regex. I extracted the vault's nontrivial, falsifiable claims (in its own wording, pulled from `build_vault.py` `CONCEPTS`) and verified each **two ways**:

- **External** — web search against Palantir primary sources (`docs.palantir.com`, engineering blog, patents, public OSDK).
- **Internal (source-grounding)** — does the note's *cited* `ResearchResults/` reconstruction actually *support* the claim? ("A citation that resolves is not a citation that supports.")

Verdicts: **VERIFIED** (primary source supports the specific assertion) · **REPORTED** (asserted by a source but not independently confirmed / name-only) · **CONTRADICTED** (a source says otherwise) · **STALE** (true but time-sensitive). Scope: hubs/invariants + the highest-inbound, most load-bearing concepts across all 8 layers. The long tail (the remaining ~170 concepts) is **REPORTED** by inheritance from the reconstructions — not individually re-verified here.

## Bottom line

**The vault's content is highly accurate.** 21 of 23 externally-checked claims VERIFIED with exact quotes from `docs.palantir.com`; all 12 internal source-groundings were SUPPORTED by verbatim passages. Only **two** content issues, both interpretive rather than factual:

1. **CONTRADICTED — "Slate (Legacy Builder)".** Current docs present Workshop and Slate as co-equal "primary application building tools"; Slate is not labeled legacy and is positioned as low-code. The "legacy/power-user" framing (and the note title) is the vault's editorial call, not documented fact.
2. **REPORTED/name-invented — "Model Gateway".** The capability is real and VERIFIED; the *name* is not Palantir's (official: "LLM-provider compatible APIs" / "Model Catalog").

One **STALE-watch**: Phonograph EOL "June 30, 2026" is accurate now (audit date 2026-06-14) but expires in 17 days.

---

## External verification — vs Palantir primary docs

### Data + Semantic storage internals

| # | Claim | Verdict | Source · evidence |
|---|---|:--:|---|
| 1 | Dataset txns = SNAPSHOT/APPEND/UPDATE/DELETE; view replays from latest SNAPSHOT | VERIFIED | docs/foundry/data-integration/datasets — enum exact; "SNAPSHOT … replaces the current view"; later txns applied in order |
| 2 | `@incremental`; APPEND-only → incremental, SNAPSHOT input → full rebuild | VERIFIED | docs/foundry/transforms-python/incremental-usage — "run incrementally if … inputs had only files added"; SNAPSHOT forces rewrite |
| 3 | Magritte is the Data Connection engine; `magritte-coordinator` | VERIFIED | docs/foundry/data-connection/agent-proxy — agent connects back to `magritte-coordinator`; connectors namespaced `magritte` |
| 4 | Phonograph = legacy OSv1, Elasticsearch-based, EOL 2026-06-30 | **VERIFIED (STALE-watch)** | docs/foundry/object-databases/object-storage-v1 — "legacy backing store"; "ElasticSearch-style syntax"; "unavailable after June 30, 2026" |
| 5 | OSv2 = next-gen backend, multi-modal storage queried in one request | VERIFIED | docs/foundry/object-backend/overview — "next-generation canonical data store … multi-modal storage backends … single request" |
| 6 | OSS serves reads (search/filter/aggregate/load) | VERIFIED | docs/foundry/object-backend/overview — "OSS allows … searching, filtering, aggregating, and loading of objects" |
| 7 | Object Data Funnel orchestrates writes + indexing | VERIFIED | docs/foundry/object-backend/overview — "Funnel is a microservice … orchestrating data writes into the Ontology … indexes" |

### Kinetic + App-Building

| # | Claim | Verdict | Source · evidence |
|---|---|:--:|---|
| 8 | Submission Criteria "formerly validations", server-enforced | VERIFIED | docs/foundry/action-types/submission-criteria — "(formerly known as validations) are the conditions that determine whether an action can be submitted" |
| 9 | Function-Backed Action computes edits via Ontology Edits API | VERIFIED | docs/foundry/action-types/function-actions-getting-started — "backed by an Ontology Edit function" (`@OntologyEditFunction()`) |
| 10 | Functions on Objects (FOO) | VERIFIED | docs/foundry/functions/functions-on-objects — "'functions on objects' (sometimes referred to as 'FOO')" |
| 11 | OSDK has `useObjectSet` + `useOsdkAction` | VERIFIED | palantir.github.io/osdk-ts/react — both hooks present in `packages/react/src` |
| 12 | Marking = conjunctive, must hold ALL to access | VERIFIED | docs/foundry/security/markings — "must be a member of all the Markings … conjunctive (boolean AND)"; "mandatory control" |
| 13 | Action atomicity — throw → no edits | VERIFIED | docs/foundry/functions/api-ontology-edits — "entire function must succeed … atomic transaction" |
| 14 | **Slate = legacy/power-user builder; Workshop = primary** | **CONTRADICTED** | docs/foundry/app-building/overview — both are "primary application building tools"; Slate never called legacy; Slate "minimal coding skills" |

### Security + Platform + AIP

| # | Claim | Verdict | Source · evidence |
|---|---|:--:|---|
| 15 | Multipass = identity backbone (users/groups/attrs/tokens) | VERIFIED | docs/foundry/quiver/card-multipass-attribute + admin API — attributes "key-value"; `multipass:email:primary`; tokens/JWT |
| 16 | Apollo = constraint-based pull model, no single target state | VERIFIED | docs/apollo/core/plans-and-constraints — "no single target state for an Environment"; "'pull' model"; proposes Plans |
| 17 | Rubix = hardened autoscaling K8s, nodes ≤48h | VERIFIED | docs/foundry/architecture-center/rubix — "Nodes … cannot live longer than 48 hours" |
| 18 | Gotham (2008) = defense platform, dynamic-ontology origin | VERIFIED | palantir.com/platforms/gotham + IEEE 10808897 — 2008; "based on dynamic ontology technology" |
| 19 | AIP Logic = no-code LLM Ontology-function builder | VERIFIED | docs/foundry/logic/overview — "no-code development environment for building … functions powered by LLMs" |
| 20 | AIP Assist = in-platform help, no customer data | VERIFIED | docs/foundry/assist/overview — "trained on Palantir's platform documentation" |
| 21 | AIP Chatbot Studio formerly "AIP Agent Studio" | VERIFIED | docs/foundry/chatbot-studio/core-concepts — "previously known as AIP Agent Studio" |
| 22 | **"Model Gateway" = the governed multi-LLM layer** | **REPORTED (name invented)** | Capability VERIFIED (proxy endpoints, ZDR, GPT/Claude/Gemini/Grok/Llama) but Palantir says "LLM-provider compatible APIs"/"Model Catalog"; "Model Gateway" is not a Palantir product name |
| 23 | CBAC = classification-level mandatory access control | VERIFIED | docs/foundry/security/classification-based-access-controls — "CBAC are mandatory controls … at or below their own classification level" |

## Internal source-grounding — note vs its cited ResearchResults

All 12 sampled claim/source pairs **SUPPORTED** by verbatim passages, each carrying the reconstruction's own confidence grade. Representative rows:

| Claim | Cited source | Verdict | Source confidence tag |
|---|---|:--:|---|
| 4 transaction types; view = replay from SNAPSHOT | Data §3.2 | SUPPORTED | [Documented, High] |
| Magritte / `magritte-coordinator` | Data §2, §2.2 | SUPPORTED | [Documented, High] |
| Phonograph OSv1 / Elasticsearch / EOL 2026-06-30 | Semantic §4.1 | SUPPORTED | [Documented] |
| OSv2 multi-modal backends | Semantic §4.2 | SUPPORTED | [Documented] |
| Submission Criteria "formerly validations" | Kinetic §5 | SUPPORTED | [Documented, High] |
| Function-Backed Action / Ontology Edits API | Kinetic §6 | SUPPORTED | [Documented, High] |
| Multipass identity backbone | Security §2 | SUPPORTED | [Documented, High] |
| Marking all-or-nothing | Security §4 | SUPPORTED | [Documented] |
| Apollo no-single-target-state | Platform §2.2 | SUPPORTED | [Documented] |
| Rubix nodes ≤48h | Platform §7.1 | SUPPORTED | [Documented] |
| Chatbot Studio formerly Agent Studio | AIP §4 | SUPPORTED | [Documented, High] |
| Model Gateway = many external LLMs | AIP §6.1 | SUPPORTED (capability) | [Documented] |

**Chain conclusion:** for the sampled load-bearing claims, the full provenance chain holds: *Palantir docs → ResearchResults reconstruction → vault note.* The notes do not embellish beyond their sources, and the sources match live documentation.

## Contradiction / drift list (content + cross-layer)

| # | Type | Where | Issue | Severity |
|---|---|---|---|:--:|
| C1 | note vs live docs | `Slate (Legacy Builder).md` (title + body) | Slate framed as "legacy"; docs call Workshop & Slate co-equal "primary" builders | P2/P3 |
| C2 | note vs live docs | `Model Gateway & Governance.md` | "Model Gateway" is a reconstruction-invented name; capability is real | P3 |
| C3 | note vs Spec | `Design Decisions.md`, `Minimum Viable Foundry.md` | D1–D15 shown "open"; `Build-Blueprint.md` resolved/committed all 15 | **P1** |
| C4 | note vs note vs Spec | README / Design Decisions / `Build-Blueprint.md` | project phase numbered inconsistently (Phase 2 / Phase 3 / "engine = pre-Phase 2") | P2 |
| C5 | view vs view vs generator | Build View + README vs Build Matrix + `disposition()` | build set 58 vs 60; keep/simplify/drop counts disagree | **P1** |
| C6 | note vs generator | `Foundry — Home (MOC).md` | hand-added hub links (`Build Matrix`, `Vault Metadata Standard`) absent from `build_vault.py:1342` | P3 |

## Staleness register

| Claim | Note | Status | Action |
|---|---|---|---|
| Phonograph EOL "after June 30, 2026" | `Phonograph (OSv1)` (in `Object Storage.md`) | accurate as of 2026-06-14; expires in 17 days | reword to "scheduled EOL 2026-06-30" / verify post-date |
| AIP Chatbot Studio "(formerly AIP Agent Studio)" | `Agents & Chatbots.md` | current & correct direction | none |
| "k-LLM": GPT/Claude/Gemini/Grok/Llama | `Model Gateway & Governance.md` | model roster rots as providers change | review periodically |

## Method & limits

- External checks performed against live Palantir docs on 2026-06-14; URLs in the tables are abbreviated paths under `palantir.com/docs/`.
- I marked VERIFIED only where a primary source supports the *specific* assertion; mere term-presence was treated as REPORTED.
- Not every one of the 194 concepts was individually re-verified — the pass was scoped (per the audit's own guidance) to hubs/invariants + highest-inbound + most-falsifiable claims. Given that the sampled chain held uniformly and the reconstructions are densely `[Documented]`-graded, residual risk in the long tail is **low but nonzero**; treat unsampled specific claims as REPORTED until checked.
