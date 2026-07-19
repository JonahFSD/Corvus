# Specs - very tentative rough draft - everything subject to change 



Foundry takes a company's scattered data and turns it into a single live model of the business: its customers, circuits, contracts, and the operations that act on them. People and AI change that model only through governed, recorded actions. This spec defines a smaller system built on the same model, and says which parts to replicate, which to simplify, and which to drop. Every call is grounded in primary-source research.

##  loop

The platform that surfaces the losing circuit is also where the disconnect happens, and the change is governed, recorded, and written straight back to the systems of record. Data flows up into meaning; decisions flow back down into the systems that run the business.

## How it works

This section follows Palantir's own architecture documentation, which is the source of truth here (Architecture Center: _The Ontology System_ and _AIP, Foundry, and Apollo_). At the center is the **Ontology**: one operational model of the enterprise's decisions, built from the four-fold integration of **data, logic, action, and security**. 

**The four-fold.** The Ontology integrates data, logic, and action, with security threading through all three rather than bolted onto the side. Every read and write, by a person or an agent, is reconciled against marking, role, and purpose at the moment of access.

```mermaid
flowchart TB
  ONT["The Ontology<br/>one model of the enterprise's decisions"]:::focus
  SEC["Security — reconciled at the moment of access<br/>humans + agents · marking · role · purpose · lineage + audit"]:::sec

  subgraph BASE["integrated by the Ontology"]
    direction LR
    DATA["Data<br/>objects · properties · links"]:::pillar
    LOGIC["Logic<br/>rules · ML · LLM functions · orchestration"]:::pillar
    ACTION["Action<br/>transactions → multi-step writeback"]:::pillar
  end

  ONT --> SEC
  SEC -.-> DATA
  SEC -.-> LOGIC
  SEC -.-> ACTION
  DATA -->|feeds| LOGIC
  LOGIC -->|powers| ACTION

  classDef focus fill:#1b5e3f,stroke:#0c2f20,color:#ffffff
  classDef sec fill:#5b3f8a,stroke:#33245c,color:#ffffff
  classDef pillar fill:#33415c,stroke:#1c2536,color:#ffffff
```

Palantir splits the Ontology system itself into three parts: a **Language** that defines the model (objects, properties, links, plus actions, automations, and the logic behind them), an **Engine** that runs it (a read architecture of high-scale queries, real-time subscriptions, and materializations, and a write architecture of atomic transactions, batch mutations, streams, and change-data-capture), and a **Toolchain** that builds on it (the Ontology SDK and DevOps tooling for governed production).

**One decision** A recommendation becomes a governed, validated, audited Action that commits to the Ontology as one atomic transaction. Propagating that decision to an external system of record is a separate step: no transaction spans Foundry and an outside system, so the writeback is idempotent and reconciled, not two-phase. For the clone we choose a human-in-the-loop policy — the AIP agent proposes the Action and an operator submits it under their own permissions. (In Foundry, automated actions can also run as an automation owner, a project scope, or a service user.)

```mermaid
sequenceDiagram
    autonumber
    participant AG as AIP agent
    actor U as Operator
    participant APP as Action Form
    participant AZ as Authorization
    participant ACT as Actions service
    participant ONT as Ontology
    participant LOG as Audit log
    participant SOR as Source system

    AG-->>U: proposes "Disconnect circuit"
    U->>APP: confirm and submit
    APP->>AZ: check the operator's permissions
    AZ-->>APP: default-deny check passes
    APP->>ACT: action + parameters
    ACT->>ACT: validate submission criteria
    ACT->>ACT: compute edits — declarative rules or a function
    ACT->>ONT: commit edits — one atomic transaction
    ACT->>LOG: append who, what, when
    ONT-->>U: read-your-writes
    Note over ACT,SOR: separate, non-atomic step
    ACT->>SOR: writeback via webhook — idempotent, reconciled
```

## Architecture

The same model as the full component stack, the way Palantir's Architecture Center layers it: infrastructure at the base, the apps at the top, security spanning all of it. 

```mermaid
flowchart TB
  SRC[("External systems<br/>data sources · systems of record")]:::ext

  subgraph NORTH["North of the Ontology — apps, automations, agents"]
    direction LR
    APPS["Human + AI apps<br/>Workshop · object views · analytics"]:::layer
    AUTO["Automations<br/>schedule · event · API-driven"]:::layer
    SDKS["Products &amp; SDKs<br/>OSDK · IDEs · Palantir MCP"]:::layer
  end

  subgraph AIPL["AIP — generative AI"]
    direction LR
    GW["Model access (k-LLM)<br/>Model Catalog · zero data retention"]:::layer
    AGENTS["Agent lifecycle<br/>AIP Logic · agents · Evals"]:::layer
    VTOOLS["Vector · compute · tool services"]:::layer
  end

  subgraph ONTS["The Ontology system — the core"]
    direction LR
    LANG["Language<br/>objects · properties · links · actions · functions"]:::core
    ENG["Engine<br/>read + write architecture · object storage (OSv2)"]:::core
    OTOOL["Toolchain<br/>OSDK · DevOps · Marketplace"]:::core
  end

  subgraph MMDP["Multimodal Data Plane — south of the Ontology"]
    direction LR
    ODATA["Open data<br/>Iceberg · virtual tables · media · streams · geo"]:::layer
    OCOMP["Open compute<br/>Spark · Flink · DataFusion · Polars · DuckDB · BYO"]:::layer
    PIPE["Integration &amp; pipelines<br/>connectors · Pipeline Builder · CDC"]:::layer
  end

  subgraph FOUND["Foundation"]
    direction LR
    APOLLO["Apollo<br/>continuous delivery · zero-downtime upgrades"]:::base
    RUBIX["Rubix<br/>hardened autoscaling Kubernetes · any cloud / on-prem"]:::base
  end

  SEC2["Security &amp; Governance<br/>spans every layer<br/>infra · platform · enterprise<br/>role · marking · purpose · audit · lineage"]:::sec

  SRC -->|ingest| MMDP
  MMDP -->|"data becomes meaning"| ONTS
  ONTS --> AIPL
  ONTS --> NORTH
  AIPL --> NORTH
  NORTH -.->|"decisions written back"| SRC
  FOUND -.->|"runs every service above"| MMDP
  SEC2 -.-> NORTH
  SEC2 -.-> ONTS
  SEC2 -.-> MMDP

  classDef ext fill:#222222,stroke:#000000,color:#ffffff
  classDef core fill:#1b5e3f,stroke:#0c2f20,color:#ffffff
  classDef layer fill:#33415c,stroke:#1c2536,color:#ffffff
  classDef base fill:#5e4109,stroke:#3a2906,color:#ffffff
  classDef sec fill:#5b3f8a,stroke:#33245c,color:#ffffff
```

**Data Plane.** Open data on Apache Iceberg with virtual tables, and a pluggable compute mesh (Spark, Flink, DataFusion, Polars, DuckDB, bring-your-own); connectors and change-data-capture turn raw sources into Ontology-ready data. for us: one relational store and a thin ingest path — but implemented append-only / event-sourced so the versioned-foundation invariant holds (an immutable edit log is the source of truth, current state is a projection; note Postgres has no native temporal tables)._

**Ontology** The core, in three parts: a Language (objects, properties, links, actions, functions), an Engine (read and write architecture over OSv2 object storage), and a Toolchain (OSDK, DevOps, Marketplace). 

**AIP** Secure k-LLM access to any model, vector and tool services, and the agent lifecycle (AIP Logic, Evals). Agentic actions pass through the same Ontology and the same default-deny controls as a human, evaluated against whatever identity runs them — an interactive user, an automation owner, a project scope, or a service user. 

**North of the Ontology.** Human and AI applications (Workshop), automations, and products, SDKs, and developer environments.

**Security & Governance.** Not a layer but three spheres spanning every one — infrastructure, platform (role-, marking-, and purpose-based controls with lineage and audit), and enterprise. _Clone: kept — roles, markings, row/cell policies, default-deny, and an append-only audit log._





## Why

Five why's

| Invariant                          | The idea                                                                                                                                                  |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Semantic model over data**       | People work with real things (a Circuit, a Carrier) instead of tables and columns, and each is defined once and reused everywhere.                            |
| **Versioned data foundation**      | The data underneath is immutable and historied; any value traces back to where it came from.                                                                  |
| **Governed writeback**             | Every change goes through a defined, validated, audited Action, never an ad-hoc edit. The rule is written once and holds no matter who, or what, triggers it. |
| **Security travels with the data** | Access belongs to the objects and rows themselves, on by default and checked on every query, rather than bolted onto each app.                                |
| **End-to-end lineage**             | Source → dataset → object → action → audit forms one continuous, inspectable chain.                                                                           |

The only way to change anything is an Action, and every Action validates and records itself. That is why the AI layer is safe: an agent can act only through the same governed Action and the same default-deny gate as a human, under whatever identity runs it and in the clone, we keep that identity the human operator.

---

