---
tags:
  - layer/aip
aliases:
  - AIP Evals
  - Evaluator
updated: 2026-06-13
---

# Evals

> Taming LLM non-determinism: the evaluation harness that scores functions and agents against expected outputs, and the evaluators (built-in, LLM-as-judge, Marketplace, or custom) that are the unit of measurable AI quality.

## AIP Evals

> An evaluation harness for LLM functions/agents: test cases, evaluators, objectives, and experiments.

Tames non-determinism by scoring target functions against expected outputs with [[Evals#Evaluator|evaluators]]; pass/fail objectives and thresholds gate publishing. Experiments grid-search model × prompt to optimize cost/performance.

**Invariants:** [[Governed Writeback]] · [[End-to-End Lineage]]

**Related:** [[Evals#Evaluator|Evaluator]] · [[Agents & Chatbots#Agent-as-Function|Agent-as-Function]] · [[AIP Logic & Blocks#AIP Logic|AIP Logic]]

**For our clone:** The discipline (evals-as-gates) matters even for non-AI logic.

*clone: defer · kind: service · layer: aip · source: AIP reconstruction §5*
#clone/defer #kind/service #layer/aip

## Evaluator

> A scoring function in AIP Evals: built-in (exact/range/regex), LLM-as-a-judge, Marketplace, or custom.

Returns boolean/numeric metrics per test case; an objective decides which result passes. LLM-as-a-judge lets one model grade another against a condition. The unit of measurable AI quality.

**Invariants:** [[End-to-End Lineage]]

**Related:** [[Evals#AIP Evals|AIP Evals]]

*clone: defer · kind: concept · layer: aip · source: AIP reconstruction §5.2*
#clone/defer #kind/concept #layer/aip
