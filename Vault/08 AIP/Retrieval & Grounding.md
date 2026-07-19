---
tags:
  - layer/aip
aliases:
  - Retrieval Context
  - Semantic Search
updated: 2026-06-13
---

# Retrieval & Grounding

> Foundry's RAG — 'Ontology-augmented generation': context injected into every prompt, and the nearest-neighbor vector search that grounds generations in real Ontology data.

## Retrieval Context

> Information injected into the prompt on every user message: Ontology, document, or function-backed context.

Grounds generations in real data — a fixed object set or [[Retrieval & Grounding#Semantic Search|semantic search]] over [[Objects#Object Type|objects]], document chunks, or a custom retrieval function. Foundry's RAG ('Ontology-augmented generation').

**Invariants:** [[Semantic Model Over Data]]

**Related:** [[Retrieval & Grounding#Semantic Search|Semantic Search]] · [[Agents & Chatbots#AIP Agent|AIP Agent]] · [[Agents & Chatbots#Application State|Application State]] · [[Objects#Object Set|Object Set]]

*clone: defer · kind: mechanism · layer: aip · source: AIP reconstruction §7.1*
#clone/defer #kind/mechanism #layer/aip

## Semantic Search

> Nearest-neighbor retrieval over Vector-type Ontology properties (embeddings).

An embedding property (Dimension + Similarity Function) is populated via Pipeline Builder/transforms; queries embed the input and return the K most similar objects. The grounding backbone of [[Retrieval & Grounding#Retrieval Context|Retrieval Context]] and the reason [[Properties#Advanced Property Types|vector properties]] exist.

**Invariants:** [[Semantic Model Over Data]]

**Related:** [[Retrieval & Grounding#Retrieval Context|Retrieval Context]] · [[Properties#Advanced Property Types|Advanced Property Types]] · [[Objects#Object Type|Object Type]]

*clone: defer · kind: mechanism · layer: aip · source: AIP reconstruction §7.2*
#clone/defer #kind/mechanism #layer/aip
