# ADR-0007: Use one TypeScript Product runtime

- Status: accepted
- Date: 2026-07-26

## Context

The repository is npm-managed, already type-checked with TypeScript, and must deliver both an Apps SDK/MCP server and a message-scoped interactive Evidence component. The historical `bible-ontology-spec.md` prescribed a FastAPI semantic tier and eight provider-shaped public tools, while ADR 0006 now requires one cohesive Investigation module behind three explicit MCP operations.

Current OpenAI guidance supports both the official TypeScript and Python MCP SDKs, explicit input and output schemas, Streamable HTTP transport, and stable public HTTPS deployment. The platform therefore does not require a polyglot architecture. Maintaining Python server models, TypeScript component models, cross-language schema generation, and two build/dependency systems would add state and contract drift without a product requirement.

## Decision

Implement all new product code in one strict TypeScript Product runtime:

- ESM modules managed by npm and the repository lockfile.
- The repository-supported Node.js baseline, currently Node.js 20 or newer.
- `@modelcontextprotocol/sdk` for the MCP host and Streamable HTTP transport.
- Zod as the executable source for tool input/output validation and package schemas, with JSON Schema emitted where MCP and Apps SDK contracts require it.
- TypeScript/React for the Evidence component, sharing generated or directly imported read-only domain types with the server package.
- TypeScript for the Corpus snapshot compiler, source-manifest validation, deterministic evidence gate, fixtures, provider adapters, and deployment entry point.
- One stable production HTTPS endpoint, conventionally `/mcp`, serving the MCP Streamable HTTP transport; stable versioned UI-resource identifiers serve the Evidence component.

The three MCP tools use explicit closed schemas and accurate read-only annotations. `structuredContent` carries the compact canonical Answer evidence package required by ChatGPT, `content` remains a short noncompeting compatibility summary, and `_meta` contains only rights-permitted user-deliverable component hydration. Provider credentials and secrets never enter any result field.

New Python code does not form part of the Product runtime. Existing Python research, vault, audit, or archival utilities may remain until a separately scoped cleanup or replacement is justified; the runtime does not invoke them. Do not introduce a Python sidecar, FastAPI tier, cross-language RPC seam, or duplicated Python domain models.

This decision supersedes the FastAPI and eight-public-tool mandates in `bible-ontology-spec.md`. It does not yet accept that document's proposed Postgres/pgvector schema, ontology ingestion plan, scoring formula, confidence fields, or corpus shape; those remain candidates for the separate storage and ontology decision.

## Consequences

The MCP host, Investigation module, validators, fixtures, and Evidence component share one language, one package graph, one lockfile, and one type system. Tool-result and UI contracts can be tested without cross-language serialization drift. Local development, CI, and deployment use the repository's existing npm workflow.

Node.js must still call true external systems and any selected database through explicit bounded adapters. TypeScript does not make provider output trustworthy; every boundary remains schema-validated, rights-checked, and sanitized. If a future workload demonstrably requires a Python-native library or independently scaled compute tier, that evidence must support a new ADR rather than introducing an incidental sidecar.

## References

- [OpenAI: Build an MCP server](https://developers.openai.com/plugins/build/mcp-server)
