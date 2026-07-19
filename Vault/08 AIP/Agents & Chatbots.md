---
tags:
  - layer/aip
aliases:
  - AIP Agent
  - AIP Chatbot Studio
  - Agent-as-Function
  - Application State
  - AIP Assist
updated: 2026-06-13
---

# Agents & Chatbots

> Stateful conversational agents over the Ontology: the agent itself, the studio that builds it, the application state it carries across turns, its publication as a callable function, and the in-platform builder-help surface (AIP Assist).

## AIP Agent

> A stateful conversational agent that reasons over tools and retrieval context within a user's permissions.

Maintains a session (system prompt + history + injected context + [[Agents & Chatbots#Application State|Application State]]); reasons via a [[Tools & Safe Execution#Tool-Calling Mode|tool-calling loop]]; cannot exceed the [[Tools & Safe Execution#Execution-Permission Contract|Execution-Permission Contract]]. Formerly 'AIP Agent', now 'AIP Chatbot'.

**Invariants:** [[Governed Writeback]]

**Related:** [[Agents & Chatbots#AIP Chatbot Studio|AIP Chatbot Studio]] · [[Agents & Chatbots#Application State|Application State]] · [[Agents & Chatbots#Agent-as-Function|Agent-as-Function]] · [[Tools & Safe Execution#Execution-Permission Contract|Execution-Permission Contract]]

*clone: defer · kind: concept · layer: aip · source: AIP reconstruction §4*
#clone/defer #kind/concept #layer/aip

## AIP Chatbot Studio

> The builder for stateful conversational agents (formerly AIP Agent Studio).

Configures instructions, [[Tools & Safe Execution#AI Tool|tools]], model + temperature, [[Agents & Chatbots#Application State|Application State]], and [[Retrieval & Grounding#Retrieval Context|Retrieval Context]]. Publishes the agent as an [[Agents & Chatbots#Agent-as-Function|Agent-as-Function]]. Surfaces in the [[Widgets, Binding & Writeback#AIP Agent Widget|AIP Agent Widget]].

**Invariants:** [[Governed Writeback]] · [[Semantic Model Over Data]]

**Related:** [[Agents & Chatbots#AIP Agent|AIP Agent]] · [[Agents & Chatbots#Application State|Application State]] · [[Retrieval & Grounding#Retrieval Context|Retrieval Context]] · [[Agents & Chatbots#Agent-as-Function|Agent-as-Function]] · [[Widgets, Binding & Writeback#AIP Agent Widget|AIP Agent Widget]]

**For our clone:** Defer.

*clone: defer · kind: service · layer: aip · source: AIP reconstruction §4*
#clone/defer #kind/service #layer/aip

## Agent-as-Function

> An agent/chatbot published as an Ontology Function with a fixed userInput/sessionRid I/O contract.

Inputs `userInput` + optional `sessionRid` (+ app variables); outputs `markdownResponse` + `sessionRid`. Makes the agent callable by [[Integration & Automation#Automate|Automate]], [[Evals#AIP Evals|AIP Evals]], Code Repositories, and the OSDK — the same [[Define-Once Reuse]] pattern as every other [[Functions#Function|Function]].

**Invariants:** [[Governed Writeback]] · [[Define-Once Reuse]]

**Related:** [[Agents & Chatbots#AIP Agent|AIP Agent]] · [[Functions#Function|Function]] · [[Integration & Automation#Automate|Automate]] · [[Evals#AIP Evals|AIP Evals]]

*clone: defer · kind: mechanism · layer: aip · source: AIP reconstruction §4.3*
#clone/defer #kind/mechanism #layer/aip

## Application State

> Named string/object-set variables that hold an agent's context across turns (formerly 'parameters').

Can be tool inputs, retrieval inputs, or citation outputs; a value-visibility toggle controls whether the LLM may read each. Updated deterministically (pinned at loop start) or via the update-variable tool.

**Invariants:** [[Semantic Model Over Data]]

**Related:** [[Agents & Chatbots#AIP Agent|AIP Agent]] · [[Widgets, Binding & Writeback#AIP Agent Widget|AIP Agent Widget]] · [[Retrieval & Grounding#Retrieval Context|Retrieval Context]]

*clone: defer · kind: concept · layer: aip · source: AIP reconstruction §4.2*
#clone/defer #kind/concept #layer/aip

## AIP Assist

> An in-platform AI help tool trained on Foundry docs (no access to customer data), context-aware of the current app.

The 'meta' AI surface that helps builders use Foundry itself; can be backed by custom chatbots/content sources. Distinct from app-facing agents.

**Invariants:** [[Semantic Model Over Data]]

**Related:** [[Agents & Chatbots#AIP Chatbot Studio|AIP Chatbot Studio]] · [[AIP Logic & Blocks#AIP Logic|AIP Logic]]

*clone: defer · kind: service · layer: aip · source: AIP reconstruction §9*
#clone/defer #kind/service #layer/aip
