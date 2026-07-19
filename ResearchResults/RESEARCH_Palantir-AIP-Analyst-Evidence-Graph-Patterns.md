# Palantir AIP Analyst Evidence and Graph Patterns

*Primary-source research, accessed 2026-07-19. Product recommendations are explicitly marked as inferences; Palantir documents the reference interaction, not this assistant's theological model.*

## Executive synthesis

Palantir's reference pattern is a useful fit for the theological assistant if it is adapted as a **two-layer evidence experience**:

1. Keep the answer readable and conversational, with tappable citations attached to the claims they support.
2. Put the audit surface behind a message-scoped **Evidence** control. That surface can reveal source details and a directed graph of the answer's attributable evidence path.

AIP Analyst describes its graph as a directed view of provenance and analysis logic. Palantir positions it as a way to inspect how a result was reached, audit transformations and reproducibility, and verify grounding in actual data. Its adjacent outline separately shows questions, manually added context, and tool use. [Palantir, “Using AIP Analyst”](https://www.palantir.com/docs/foundry/aip-analyst/using-aip-analyst)

Palantir's related chatbot documentation supplies the complementary citation pattern: citations appear inline, open their source when selected, and are also collected in a per-message **Sources** dropdown. A citation selection can instead update application state so an overlay presents more information about the cited object. [Palantir, “Citations”](https://www.palantir.com/docs/foundry/chatbot-studio/citations)

**Product inference:** combine these patterns as native ChatGPT prose plus tappable inline citations, with one collapsed evidence component per substantive answer. A citation tap should open the relevant verse or source detail and focus the corresponding graph node. The graph is an audit view, not the default reading experience.

## Verified Palantir patterns

### 1. Context and tool use remain inspectable

AIP Analyst defines analysis context as prior messages, tool results, and explicitly added Foundry resources. Its outline distinguishes user questions, added context, and tool calls, and lets a user hide specific tool results. This keeps the working material inspectable without forcing all of it into the main answer. [Palantir, “Using AIP Analyst — Context and Outline”](https://www.palantir.com/docs/foundry/aip-analyst/using-aip-analyst#context)

**Transfer:** the Evidence component can disclose retrieved Scripture, tradition sources, Gloo outputs, and Bible Ontology operations while the conversational answer remains minimal.

### 2. The graph is provenance and logic lineage

The documented graph is directed and intended to expose the provenance and logic path of the analysis. Palantir says it supports checking the logic of steps, auditing transformations for reproducibility, and verifying results against the Ontology data used at each step. The official screenshot depicts typed nodes and directed edges, with a selected node revealing its underlying result and operation details in an adjacent panel. [Palantir, “Using AIP Analyst — Graph”](https://www.palantir.com/docs/foundry/aip-analyst/using-aip-analyst#graph)

**Transfer:** the theological graph should expose attributable evidence lineage, not hidden chain-of-thought. Its nodes should be inspectable source records, retrieved passages, documented interpretive positions, supported claims, and the answer. Its edges should carry explicit relationships such as `supports`, `qualifies`, `disputes`, `interprets`, and `cites`.

### 3. Citations are inline, tappable, and message-scoped

For document and Ontology context, Palantir renders citations in the response and collects the same citations in a Sources dropdown below that message. Selecting a citation opens the corresponding source. Citation behavior can also be configured to update application state and drive a pop-up overlay containing more information about the selected object. [Palantir, “Citations”](https://www.palantir.com/docs/foundry/chatbot-studio/citations)

**Transfer:** every substantive scriptural, historical, confessional, lexical, or theological claim should carry one or more inline citation identifiers. The default tap target should be a small evidence detail view; a secondary action can open or focus the full graph.

### 4. Tool-backed citations are not automatic

Palantir distinguishes document/Ontology context, which receives citation support automatically, from function-backed context and tools, which do not provide citations by default. Those paths require the chatbot to be instructed to emit a supported citation format. Palantir's retrieval-context documentation likewise describes deterministic retrieval on every new message and custom citation formatting for function-backed results. [Palantir, “Citations”](https://www.palantir.com/docs/foundry/chatbot-studio/citations) · [Palantir, “Retrieval context”](https://www.palantir.com/docs/foundry/chatbot-studio/retrieval-context)

**Product decision:** do not make citation coverage depend only on prompting. The Bible Ontology MCP answer-evidence package should make source identifiers and claim-to-source links mandatory structured fields. The app should reject, abstain from, or narrow any substantive claim whose citations are missing or cannot be resolved.

### 5. Ambiguity can trigger clarification

AIP Analyst may ask a clarifying question before proceeding when a request is ambiguous. It also separates search, lookup, analysis, action, and visualization tools, allowing the available tool set to be constrained to the task. [Palantir, “Capabilities”](https://www.palantir.com/docs/foundry/aip-analyst/capabilities)

**Transfer:** ask a narrow clarification only when canon, tradition, translation, historical period, or intended mode would materially change the answer. Do not treat genuine theological disagreement as mere ambiguity; show the materially different interpretations and their respective evidence.

### 6. Provenance is more durable than generated wording

Saved AIP Analyst analyses retain messages, invoked tools, referenced resources, settings, and model choice, but not prior tool results or agent responses. When reopened, tools are run against the latest Ontology state and the current viewer's permissions. [Palantir, “Analysis resources”](https://www.palantir.com/docs/foundry/aip-analyst/analysis-resources)

**Transfer:** stable source identities and claim/source relationships should be the durable audit primitives. Generated prose is presentation, not evidence. For this product's already agreed stateless-person design, the answer evidence package can remain message-scoped while still being internally reproducible during the active interaction.

## Recommended evidence component

The component should open collapsed and contain three progressively disclosed views:

| View | Default content | Interaction |
| --- | --- | --- |
| Sources | Cited passage/source title, tradition or corpus, translation/edition, retrieval provenance | Tap an inline citation to open and focus its source |
| Positions | Shared textual ground followed by materially different named interpretations | Select a position to highlight its claims and evidence |
| Graph | Directed evidence lineage for the current answer | Select any node to inspect the source record, claim, position, or retrieval operation |

Recommended graph vocabulary:

```text
Question
  -> Retrieval operation
    -> Passage / tradition source / lexical source
      -> Claim
        -> Shared ground or named interpretive position
          -> Answer statement
```

Cross-links should express challenge and qualification without flattening disagreement:

```text
Source --supports--> Claim
Source --qualifies--> Claim
Source --disputes--> Claim
Position --interprets--> Passage
Answer statement --cites--> Source
```

This is intentionally an **evidence graph**, not a decorative Bible knowledge graph and not a disclosure of private model reasoning. Every visible conclusion must be traceable to inspectable sources or explicitly labeled as inference, uncertainty, or disagreement.

## Acceptance implications

- Every substantive answer statement has at least one resolvable inline citation; greetings and navigation copy are exempt.
- Citation taps open the relevant source detail without navigating away from the conversation by default.
- The per-message Evidence component can focus the citation's node in the graph.
- Graph nodes are created only from the structured answer evidence package, never inferred from the final prose after generation.
- Competing positions remain distinct nodes with their own supporting and challenging evidence.
- Weak, contradictory, missing, or inaccessible evidence produces explicit abstention or a narrower clarifying question.
- The component exposes provenance and transformations, but never hidden chain-of-thought.

## Boundary of the reference

Palantir documents the outline, provenance graph, citation, overlay, retrieval, and clarification mechanics above. It does **not** prescribe a theological disagreement model, the proposed graph vocabulary, an always-cited policy, or a minimal-default ChatGPT design. Those are application-specific product decisions inferred from the reference patterns and the assistant's agreed posture.
