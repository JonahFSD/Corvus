---
aliases:
  - "Data Connection"
  - "Magritte"
  - "Connector"
  - "Source & Capability"
  - "Agent (Magritte)"
  - "Agent-Proxy vs Agent Worker"
  - "Foundry Worker"
tags:
  - layer/data
  - kind/service
  - clone/simplify
layer: data
kind: service
clone: simplify
invariants:
  - "[[Versioned Data Foundation]]"
  - "[[Security Travels With Data]]"
source: "Data reconstruction §2–2.5"
updated: 2026-06-13
---

# Data Connection (Magritte)

> Foundry's connectivity subsystem for moving data in and out — the engine, the sources and connectors it speaks to, the agents that reach private networks, and the isolated workers that run ingestion.

**Data Connection & Magritte (engine).** Data Connection is the connectivity tier; its long-standing engine is **Magritte** (coordinator `magritte-coordinator`; sources addressed `ri.magritte..source.*`). Agents and the Bootstrapper connect back over websocket. It defines sources and runs ingestion via agents or direct connections in isolated workers — the on-ramp to the [[Versioned Data Foundation|data foundation]]. *Clone: drop the engine — it's enterprise plumbing for hundreds of source systems, vastly over-scoped.*

**Source & Capability.** A *source* is one connection to an external system; *capabilities* are the discrete functions it can run — ingest into Foundry, push out (see [[Virtual Table & Export|Export]]), virtualize (see [[Virtual Table & Export|Virtual Table]]), and interactive requests. Each connector lists which capabilities it supports.

**Connector.** A pre-built integration to a source type (S3, JDBC, Salesforce, Kafka, SAP, …) spanning cloud-storage, relational, warehouse, enterprise-app, streaming, and NoSQL families. *Clone: drop almost all — start with spreadsheet upload + one API.*

**Agent (Magritte).** A downloadable program installed in the customer network to reach private data sources. Two modes — **agent-proxy** ('thin', a pure network tunnel to Foundry) and the legacy **agent worker** ('thick', runs connector code on the host).

**Agent-proxy vs agent worker.** The two connectivity axes: where compute runs and how the network is crossed. Modern agent-proxy keeps compute in an isolated Foundry worker and uses the agent only as a websocket tunnel; the legacy agent worker runs Java on the customer host. Proxy recommended; worker legacy-supported.

**Foundry Worker.** An isolated container with scalable compute that runs connector/processing code on Foundry's side, handling authenticated, encrypted requests; network egress is administered in-platform via egress policies. The modern alternative to running connector code on a customer host.

**Invariants:** [[Versioned Data Foundation]] · [[Security Travels With Data]]

**Related:** [[Virtual Table & Export]] · [[Dataset & Transactions]] · [[Transforms & Build]]

**For our clone:** Simplify hard — collapse the whole subsystem to one thin ingestion path (spreadsheet upload + a single API). Drop Magritte, the connector library, agents, and worker isolation.

*Source: Data reconstruction §2–2.5*
