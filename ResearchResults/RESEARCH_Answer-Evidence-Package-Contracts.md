# Answer evidence package platform contracts

_Primary-source research for Issue #4, accessed 2026-07-19. Product implications are explicitly labeled as inferences._

## Question

What do the current Apps SDK, MCP, citation, and provenance contracts imply for the smallest practical citation-complete Answer evidence package?

## Executive synthesis

The platform supports a compact, schema-validated evidence contract, but it does not automatically guarantee that freely generated narration remains aligned with that evidence. A candidate boundary is therefore a model-visible `structuredContent` payload containing ordered, citation-bound Answer statements and the minimal evidence relationships needed to validate them. User-deliverable presentation data can remain component-only in `_meta`, but `_meta` is not a confidentiality or licensing boundary.

This is a product inference, not a requirement imposed by OpenAI or MCP. It follows from four primary-source facts:

1. ChatGPT reads `structuredContent` to narrate the result.
2. Both `structuredContent` and `content` are visible to the model and component, while `_meta` is component-only.
3. Structured results can be validated against a declared `outputSchema`.
4. Citation reliability depends on explicit, resolvable source identities rather than an unstructured prose-generation step.

## Current platform contract

### The result has three distinct payload surfaces

OpenAI documents three sibling tool-result fields:

- `structuredContent`: concise JSON read by both the model and component.
- `content`: optional text or other MCP content read by both the model and component.
- `_meta`: component-only data hidden from the model.

Only `structuredContent` and `content` enter the conversation transcript. OpenAI recommends keeping `structuredContent` tight because the model reads it and oversized payloads degrade model performance and rendering. The component still receives the full result envelope, including `_meta`. [OpenAI, “Build your MCP server”](https://developers.openai.com/apps-sdk/build/mcp-server) · [OpenAI, “Apps SDK reference — Tool results”](https://developers.openai.com/apps-sdk/reference#tool-results)

**Product inference:** put the semantic evidence spine in `structuredContent`; put display-oriented denormalization and other user-deliverable component hydration in `_meta`. Do not hide any fact in `_meta` that ChatGPT must use to compose or qualify the answer, and do not send source content in any tool-result field unless its delivery rights permit client exposure.

### Structured output should have an explicit schema

The Apps SDK documentation recommends declaring `outputSchema` for tools returning `structuredContent`, both so clients can validate results and so the model can reason about follow-up calls. The MCP 2025-06-18 specification likewise says servers must conform to a declared output schema and clients should validate against it. For backward compatibility, MCP recommends also serializing structured output in a text content block. [OpenAI, “Apps SDK reference — Tool descriptor parameters”](https://developers.openai.com/apps-sdk/reference#tool-descriptor-parameters) · [MCP, “Tools — Structured Content and Output Schema”](https://modelcontextprotocol.io/specification/2025-06-18/server/tools#structured-content)

**Product inference:** the Answer evidence package should be one versioned root object with a closed JSON Schema, stable local identifiers, and cross-references checked by a deterministic validator. Avoid independent nested copies of claims or sources that can drift.

### ChatGPT narrates from the structured result

OpenAI describes the model as narrating the experience from the structured data returned by the MCP server. The same guide says structured content and component state flow through the conversation, allowing the model to refer to identifiers in follow-up turns or render the component later. [OpenAI, “MCP”](https://developers.openai.com/apps-sdk/concepts/mcp-server) · [OpenAI, “Build your MCP server — Architecture flow”](https://developers.openai.com/apps-sdk/build/mcp-server#architecture-flow)

The docs do not promise that arbitrary model paraphrases will preserve a package's claim boundaries or citation bindings.

**Product inference:** substantive answer wording should enter the package as ordered atomic Answer statements, each linked directly to the Citations and evidence modes that license the entire proposition. ChatGPT may add conversational transitions but should not create new substantive propositions outside those statements. This makes package-level citation coverage mechanically testable; Developer Mode testing must still determine whether native host narration preserves it.

## Citation implications

For MCP `search` and `fetch` compatibility, OpenAI recommends a stable result `id`, human-readable title, and an absolute user-openable HTTP(S) `url`; a result without a user-openable URL remains ordinary tool output rather than becoming a host citation. Provider-internal identifiers belong in `id`, not `url`. [OpenAI, “Build your MCP server — Company knowledge compatibility”](https://developers.openai.com/apps-sdk/build/mcp-server#company-knowledge-compatibility)

That guidance is specifically for MCP search/fetch and Company Knowledge compatibility; it does not establish automatic inline citation rendering for every custom tool result.

**Product inference:** every Citation record needs both a stable internal identity and a resolvable user target where rights permit. Scripture and Tradition source identities should not be reduced to display URLs, and citations should bind Answer statements to exact source locators rather than only to whole documents.

## Provenance graph implications

The W3C PROV starting point distinguishes Entities, Activities, and Agents, and constructs provenance chains by recording which entities an activity used and generated. It also permits named bundles of provenance assertions. [W3C, “PROV-O: The PROV Ontology”](https://www.w3.org/TR/prov-o/)

**Product inference:** Corvus does not need to implement PROV-O, but its minimum graph should preserve the same crucial distinction:

- retrieval or analysis operations are activities;
- Citations, position blocks, Evidence gaps, and Answer statements are entities;
- canonical typed-tree references record how operations produce Citations or gaps and how direct evidence relationships authorize atomic statements.

The UI derives graph edges from those references rather than storing a second generic edge list. Collapsing operations and evidence into one generic node type would make provider impact difficult to express, while adding PROV-style Agents is unnecessary unless responsibility delegation becomes material.

## Recommended minimum payload split

### `structuredContent`

- schema and corpus versions, explicit analysis scope, and a discriminated answer outcome;
- shared-ground, named-position, qualification, abstention, and Pastoral-handoff blocks;
- ordered atomic Answer statements with direct evidence relationships;
- compact source and citation records with exact locators;
- provider reports and Evidence gaps linked to the statements or positions they affect;
- compact Material-operation receipts only when needed for inspection or an implemented Analysis branch.

The Evidence graph should be derived from these canonical relationships rather than duplicated in a generic edge list. Reusable Claim records should be introduced only when concrete fixtures demonstrate enough cross-statement reuse to justify normalization.

### `_meta`

- only source excerpts whose delivery rights permit client exposure;
- display-ready source details and denormalized indexes;
- graph layout coordinates and UI state;
- other component-only data that must not affect the semantic answer.

### `content`

- a short compatibility summary or narration instruction;
- no competing substantive answer that can drift from the structured Answer statements.

## Fixture-dependent questions

The agreed direction now requires prototypes rather than more schema-by-prose debate. Successful, degraded, and abstaining fixtures must determine exact field shapes, payload size, operation-receipt requirements, hostile-content limits, rights-safe delivery behavior, and whether native ChatGPT preserves citations and substantive wording in Developer Mode.

All provider and source strings must be treated as untrusted data: bound their lengths, render them as quoted data rather than instructions, reject unsafe control content, and require synthesized Answer statements to pass the same evidence-policy validation as the rest of the package.
