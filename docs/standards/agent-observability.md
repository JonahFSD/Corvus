# Agent observability standard

This standard governs repository automation such as `run-afk`. It does not
govern Corvus product telemetry or the theological Investigation record.

## Purpose and authority

Agent observability records consequential external operations and repository
state so a maintainer can determine what an automated run attempted, where it
stopped, and which evidence supports its mechanical outcome.

Run Records report execution facts; they do not explain model cognition.
Evaluation remains separate: wrapper-executed checks, exact Git state, schema
validation, fixtures, and human diff review determine whether work is
acceptable. Product-domain provenance remains in Corvus's own evidence and
Investigation contracts.

Use this order of authority:

1. wrapper-observed deterministic checks;
2. exact Git and filesystem state;
3. repository-owned schema validation;
4. fixture assertions;
5. human judgment for normative decisions;
6. model reports and automated reviewers as advisory evidence.

An agent's claim that a check passed is never equivalent to an observed zero
exit code.

## Required Run Record

Every attempted automated agent run must record:

- task identity and base repository revision;
- workflow, runner version, sandbox, approval policy, and start time;
- named externally observable stages and their process outcomes;
- deterministic verification command, duration, and outcome;
- resulting commits, head revision, and final worktree state;
- one outcome from the workflow's closed mechanical outcome set;
- the first failed boundary, without speculative root-cause analysis; and
- references to raw execution artifacts.

The manifest must exist before the workflow's first consequential mutation,
including issue assignment or worktree creation, and before the agent process
starts. Repository-owned JSON records carry an explicit `schemaVersion` and are
validated before use. Interrupted and timed-out runs attempt to finalize a
summary rather than masquerading as absent runs.

`candidate_ready` means only that the automated candidate met its documented
mechanical contract. Human diff review remains mandatory.

## Normalized-data boundary

Normalized Run Records must not contain:

- hidden chain-of-thought or inferred mental state;
- credentials, tokens, authentication headers, or secret configuration;
- complete source documents or licensed excerpts;
- unnecessarily duplicated prompts, completions, questions, or answers;
- raw provider exchanges;
- inferred beliefs or pastoral context; or
- unsupported claims about why a model behaved as it did.

Reference prompt templates by source, version, and digest where practical.
Record externally selected actions and results, not model confidence,
reasoning-quality scores, or invented cognition stages.

## Raw output

Raw agent stdout, stderr, and check output:

- remain local under ignored `.agent-runs/` by default;
- use restrictive file permissions where the platform supports them;
- preserve native output rather than rewriting it into a speculative event
  ontology;
- are inspected only when normalized records do not explain the failure;
- are not product-domain provenance; and
- may be deleted independently of normalized summaries.

Stdout and stderr are separate artifacts whenever mixing them would corrupt a
machine-readable stream.

## Incremental instrumentation

A new field, stage, backend, evaluator, alert, or visualization requires a
recurring real failure or demonstrated diagnosis cost. Speculative future
usefulness is insufficient.

Do not add a database, OpenTelemetry pipeline, remote trace backend, dashboard,
LLM judge, generic agent-state ontology, or record-and-replay system until its
specific escalation condition has been observed and accepted. Plain local JSON
and JSONL are the intended solution while they answer operational questions
quickly.

Do not unify engineering Run Records with Corvus product Operational telemetry
without a demonstrated shared requirement. Their authorities, privacy
boundaries, and success criteria differ.
