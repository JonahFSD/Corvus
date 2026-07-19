---
tags:
  - layer/aip
aliases:
  - AIP Logic
  - Logic Block
  - Use LLM Block
updated: 2026-06-13
---

# AIP Logic & Blocks

> The no-code builder for LLM-powered Ontology functions and its composable block model — prompts, tools, and typed outputs chained into deterministic logic wrapped around a non-deterministic LLM step.

## AIP Logic

> A no-code builder for LLM-powered Ontology functions, composed of chained blocks.

A Logic function takes objects/primitives, runs [[AIP Logic & Blocks#Logic Block|blocks]] (prompt + tools + output), and returns a value, object, struct, or [[Actions#Edits-Only-via-Actions|ontology edits]] (only persisted when run from an action). Published as a callable [[Functions#Function|Function]].

**Invariants:** [[Governed Writeback]] · [[Semantic Model Over Data]]

**Related:** [[AIP Logic & Blocks#Logic Block|Logic Block]] · [[AIP Logic & Blocks#Use LLM Block|Use LLM Block]] · [[Tools & Safe Execution#AI Tool|AI Tool]] · [[Functions#Function|Function]] · [[Agents & Chatbots#Agent-as-Function|Agent-as-Function]]

**For our clone:** Defer — but its block model is a clean template if we ever add AI.

*clone: defer · kind: service · layer: aip · source: AIP reconstruction §2*
#clone/defer #kind/service #layer/aip

## Logic Block

> A discrete step in an AIP Logic function whose output can feed later blocks.

Types: [[AIP Logic & Blocks#Use LLM Block|Use LLM Block]], Apply action, Execute function, Conditionals, Loops, Create variable. Chaining blocks builds complex operations deterministically around the non-deterministic LLM step.

**Invariants:** [[Governed Writeback]]

**Related:** [[AIP Logic & Blocks#AIP Logic|AIP Logic]] · [[AIP Logic & Blocks#Use LLM Block|Use LLM Block]] · [[Actions#Action Type|Action Type]] · [[Functions#Function|Function]]

*clone: defer · kind: concept · layer: aip · source: AIP reconstruction §2.1*
#clone/defer #kind/concept #layer/aip

## Use LLM Block

> 'The heart of AIP Logic' — a block composed of a prompt, tools, and a typed output.

Supports any platform model (k-LLM via the [[Model Gateway & Governance#Model Gateway|Model Gateway]]); temperature configurable; per-block token limit. The point where reasoning meets the [[Tools & Safe Execution#AI Tool|tools]] over the Ontology.

**Invariants:** [[Semantic Model Over Data]]

**Related:** [[AIP Logic & Blocks#Logic Block|Logic Block]] · [[Tools & Safe Execution#AI Tool|AI Tool]] · [[Model Gateway & Governance#Model Gateway|Model Gateway]] · [[AIP Logic & Blocks#AIP Logic|AIP Logic]]

*clone: defer · kind: concept · layer: aip · source: AIP reconstruction §2.1*
#clone/defer #kind/concept #layer/aip
