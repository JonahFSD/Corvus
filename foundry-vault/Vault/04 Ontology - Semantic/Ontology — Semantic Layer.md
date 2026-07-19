---
tags:
  - hub
  - layer/semantic
---

# Ontology — Semantic Layer

> The model of *what exists*: object types, properties, links — the nouns of the business, materialized over versioned data.

## Subdomains

Each concept is a section within its subdomain document; the links below jump straight to it.

- **[[Objects]]** — the object model
    - [[Objects#Object Type|Object Type]] · [[Objects#Object|Object]] · [[Objects#Primary Key|Primary Key]] · [[Objects#Object Backing|Object Backing]] · [[Objects#Object Set|Object Set]]
- **[[Properties]]** — typed attributes of objects
    - [[Properties#Property|Property]] · [[Properties#Property Base Type|Property Base Type]] · [[Properties#Value Type|Value Type]] · [[Properties#Derived Property|Derived Property]] · [[Properties#Shared Property|Shared Property]] · [[Properties#Title Property|Title Property]] · [[Properties#Advanced Property Types|Advanced Property Types]] · [[Properties#Mandatory Control Property|Mandatory Control Property]]
- **[[Links]]** — relationships between object types
    - [[Links#Link Type|Link Type]] · [[Links#Link Cardinality|Link Cardinality]] · [[Links#Object-Backed Link|Object-Backed Link]]
- **[[Ontology & Metadata]]** — the model as a whole, and its governance
    - [[Ontology & Metadata#Ontology|Ontology]] · [[Ontology & Metadata#Ontology Metadata Service (OMS)|Ontology Metadata Service (OMS)]] · [[Ontology & Metadata#Interface (Ontology)|Interface (Ontology)]] · [[Ontology & Metadata#Ontology Branching & Proposals|Ontology Branching & Proposals]]
- **[[Object Storage]]** — backend internals (we replace with a DB)
    - [[Object Storage#Object Storage V2 (OSv2)|Object Storage V2 (OSv2)]] · [[Object Storage#Object Data Funnel|Object Data Funnel]] · [[Object Storage#Object Indexing|Object Indexing]] · [[Object Storage#Object Set Service (OSS)|Object Set Service (OSS)]] · [[Object Storage#Phonograph (OSv1)|Phonograph (OSv1)]]

---

**Invariants this layer serves:** [[Semantic Model Over Data]] · [[Versioned Data Foundation]] · [[Governed Writeback]] · [[Security Travels With Data]] · [[End-to-End Lineage]]

[[Foundry — Home (MOC)|← Home]]
