---
tags:
  - layer/aip
aliases:
  - Model Gateway
  - Language Model Service
  - Zero Data Retention
updated: 2026-06-13
---

# Model Gateway & Governance

> The model-agnostic serving layer: governed access to many interchangeable LLMs ('k-LLM'), the internal service that mediates every provider call, and the zero-data-retention guarantee that makes external models safe for enterprise data.

## Model Gateway

> The governed access layer to many LLMs ('k-LLM'): GPT, Claude, Gemini, Grok, Llama, and more.

Mediated by the [[Model Gateway & Governance#Language Model Service|Language Model Service]] with access controls, [[Model Gateway & Governance#Zero Data Retention|Zero Data Retention]], georestriction, and rate limits. Models are interchangeable per block/agent/node — the AI layer is model-agnostic by design.

**Invariants:** [[Security Travels With Data]]

**Related:** [[Model Gateway & Governance#Language Model Service|Language Model Service]] · [[Model Gateway & Governance#Zero Data Retention|Zero Data Retention]] · [[AIP Logic & Blocks#Use LLM Block|Use LLM Block]]

*clone: defer · kind: service · layer: aip · source: AIP reconstruction §6*
#clone/defer #kind/service #layer/aip

## Language Model Service

> The internal service that mediates all LLM calls between Foundry and model providers.

Fronts Azure / AWS Bedrock / Google Vertex backends; enforces [[Model Gateway & Governance#Zero Data Retention|Zero Data Retention]] and regional routing. Runs in the shared [[Platform & Ecosystem Layer|Rubix/Apollo]] mesh.

**Invariants:** [[Security Travels With Data]]

**Related:** [[Model Gateway & Governance#Model Gateway|Model Gateway]] · [[Model Gateway & Governance#Zero Data Retention|Zero Data Retention]] · [[Platform & Ecosystem Layer]]

*clone: defer · kind: service · layer: aip · source: AIP reconstruction §10.4*
#clone/defer #kind/service #layer/aip

## Zero Data Retention

> No customer data in prompts/completions is retained by third-party model providers, nor used to retrain.

Backed by technical + contractual guarantees; combined with georestriction it keeps AI use compliant. A precondition for putting governed enterprise data in front of external LLMs.

**Invariants:** [[Security Travels With Data]]

**Related:** [[Model Gateway & Governance#Model Gateway|Model Gateway]] · [[Model Gateway & Governance#Language Model Service|Language Model Service]]

*clone: defer · kind: property · layer: aip · source: AIP reconstruction §6.2*
#clone/defer #kind/property #layer/aip
