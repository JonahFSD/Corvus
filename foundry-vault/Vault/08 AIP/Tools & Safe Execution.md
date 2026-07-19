---
tags:
  - layer/aip
aliases:
  - AI Tool
  - Execution-Permission Contract
  - Tool-Calling Mode
updated: 2026-06-13
---

# Tools & Safe Execution

> What an LLM can actually do in Foundry and the contract that makes it safe: tools mapped onto object types, functions, and actions; the prompted-vs-native calling loop; and the make-or-break principle that the LLM only *asks* while the platform *executes* in the invoking user's permissions.

## AI Tool

> A platform capability an LLM can request: query objects (data), call a function (logic), or apply an action (action).

Tools map onto [[Objects#Object Type|object types]], [[Functions#Function|functions]], and [[Actions#Action Type|action types]]. Chatbots add update-variable, command, and request-clarification. The LLM's only way to touch the world — and always via the [[Tools & Safe Execution#Execution-Permission Contract|Execution-Permission Contract]].

**Invariants:** [[Governed Writeback]] · [[Semantic Model Over Data]]

**Related:** [[Tools & Safe Execution#Execution-Permission Contract|Execution-Permission Contract]] · [[Tools & Safe Execution#Tool-Calling Mode|Tool-Calling Mode]] · [[Actions#Action Type|Action Type]] · [[Functions#Function|Function]] · [[Objects#Object Set|Object Set]]

*clone: defer · kind: concept · layer: aip · source: AIP reconstruction §3.1*
#clone/defer #kind/concept #layer/aip

## Execution-Permission Contract

> The make-or-break AIP principle: the LLM only ASKS to use a tool; the platform EXECUTES it in the invoking user's permissions.

Verbatim: 'LLMs do not have direct access to tools; LLMs can only ask to use tools, and these tool calls are then executed … within the invoking user's permissions.' The LLM never holds credentials, sees only configured data, and can mutate only through [[Actions#Action Type|actions]]. This is why AI is *safe* on top of the engine.

**Invariants:** [[Governed Writeback]] · [[Security Travels With Data]]

**Related:** [[Tools & Safe Execution#AI Tool|AI Tool]] · [[Integration & Automation#AIP Tool Exposure|AIP Tool Exposure]] · [[Actions#Edits-Only-via-Actions|Edits-Only-via-Actions]] · [[Roles & Authorization#Role|Role]]

**For our clone:** Replicate exactly — we get a safe AI layer for free IF our action+role model is sound.

*clone: keep · kind: pattern · layer: aip · source: AIP reconstruction §3.3 (verbatim, verified)*
#clone/keep #kind/pattern #layer/aip

## Tool-Calling Mode

> How tools are invoked: prompted (one tool at a time, all models) or native (parallel, subset of models).

Prompted mode inserts tool instructions into the prompt; native mode uses the model's built-in tool-calling. The orchestration loop runs tools, feeds results back, and iterates until a final answer (bounded by an iterations limit).

**Invariants:** [[Governed Writeback]]

**Related:** [[Tools & Safe Execution#AI Tool|AI Tool]] · [[AIP Logic & Blocks#Use LLM Block|Use LLM Block]] · [[Agents & Chatbots#AIP Agent|AIP Agent]]

*clone: defer · kind: mechanism · layer: aip · source: AIP reconstruction §3.4*
#clone/defer #kind/mechanism #layer/aip
