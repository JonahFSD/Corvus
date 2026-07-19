---
tags:
  - hub
  - index
updated: 2026-06-13
---

# Build View — What We're Cloning

> The actionable spec view: every concept sorted by its **`clone`** property. Advisory — a layer default unless a concept-specific call was made. Filter it live via [[Taxonomy (Legend)]].

## Core — the irreducible essence  (7)

**Cross-cutting:** [[Define-Once Reuse]] · [[Digital Twin]] · [[Git for Data]] · [[Minimum Viable Foundry]] · [[Operational Application]] · [[Read-Your-Writes]] · [[The Closed Loop]]

## Keep — replicate faithfully (the build list)  (53)

**Data:** [[Dataset & Transactions]] · [[Data Health & Lineage]]

**Semantic:** [[Properties#Derived Property|Derived Property]] · [[Links#Link Cardinality|Link Cardinality]] · [[Links#Link Type|Link Type]] · [[Properties#Mandatory Control Property|Mandatory Control Property]] · [[Objects#Object|Object]] · [[Objects#Object Backing|Object Backing]] · [[Objects#Object Set|Object Set]] · [[Objects#Object Type|Object Type]] · [[Links#Object-Backed Link|Object-Backed Link]] · [[Ontology & Metadata#Ontology|Ontology]] · [[Ontology & Metadata#Ontology Metadata Service (OMS)|Ontology Metadata Service (OMS)]] · [[Objects#Primary Key|Primary Key]] · [[Properties#Property|Property]] · [[Properties#Property Base Type|Property Base Type]] · [[Properties#Shared Property|Shared Property]] · [[Properties#Title Property|Title Property]] · [[Properties#Value Type|Value Type]]

**Kinetic:** [[Actions#Action Atomicity|Action Atomicity]] · [[Audit & Writeback#Action Log|Action Log]] · [[Actions#Action Parameter|Action Parameter]] · [[Actions#Action Rule|Action Rule]] · [[Actions#Action Type|Action Type]] · [[Audit & Writeback#Edit History|Edit History]] · [[Actions#Edits-Only-via-Actions|Edits-Only-via-Actions]] · [[Functions#External Function|External Function]] · [[Functions#Function|Function]] · [[Functions#Function Runtime|Function Runtime]] · [[Functions#Function-Backed Action|Function-Backed Action]] · [[Functions#Functions on Objects (FOO)|Functions on Objects (FOO)]] · [[Actions#Inline Edit|Inline Edit]] · [[Functions#Ontology Edits API|Ontology Edits API]] · [[Actions#Side Effect|Side Effect]] · [[Actions#Submission Criteria|Submission Criteria]] · [[Integration & Automation#Webhook|Webhook]]

**App:** [[Widgets, Binding & Writeback#Action Form|Action Form]] · [[Workshop, Modules & Views#App vs Data Permissions|App vs Data Permissions]] · [[Reactive State Model#Reactivity Model|Reactivity Model]] · [[Workshop, Modules & Views#Workshop|Workshop]] · [[Reactive State Model#Workshop Event|Workshop Event]] · [[Reactive State Model#Workshop Variable|Workshop Variable]]

**AIP:** [[Tools & Safe Execution#Execution-Permission Contract|Execution-Permission Contract]]

**Security:** [[Audit & Lineage#Audit Log|Audit Log]] · [[Audit & Lineage#Audit Schema|Audit Schema]] · [[Roles & Authorization#Authorization Decision|Authorization Decision]] · [[Encryption, Network & Compliance#Encryption at Rest & in Transit|Encryption at Rest & in Transit]] · [[Mandatory Controls & Classification#Mandatory Control|Mandatory Control]] · [[Identity & Authentication#Multipass|Multipass]] · [[Roles & Authorization#Role|Role]] · [[Identity & Authentication#Service User & Tokens|Service User & Tokens]]

## Simplify — keep the idea, shrink the implementation  (49)

**Data:** [[Data Connection (Magritte)]] · [[Virtual Table & Export]] · [[Schema & Inference]] · [[Transforms & Build]] · [[RID]] · [[Materialization]]

**Dynamic:** [[Scenarios#State-Dependent Security|State-Dependent Security]]

**App:** [[Widgets, Binding & Writeback#Auto-Refresh|Auto-Refresh]] · [[Custom UI & Embedding#Bidirectional Iframe|Bidirectional Iframe]] · [[Custom UI & Embedding#Custom Widget|Custom Widget]] · [[Custom UI & Embedding#Embedded Foundry Apps|Embedded Foundry Apps]] · [[Workshop, Modules & Views#Embedded Module|Embedded Module]] · [[Slate (Legacy Builder)#Handlebars (Slate)|Handlebars (Slate)]] · [[Workshop, Modules & Views#Module Interface|Module Interface]] · [[Custom UI & Embedding#OSDK React Hooks|OSDK React Hooks]] · [[Widgets, Binding & Writeback#Object Set Binding|Object Set Binding]] · [[Widgets, Binding & Writeback#Object Set Filter|Object Set Filter]] · [[Workshop, Modules & Views#Object View|Object View]] · [[Reactive State Model#Recompute Behavior|Recompute Behavior]] · [[Slate (Legacy Builder)#Slate Node Graph|Slate Node Graph]] · [[Widgets, Binding & Writeback#Widget|Widget]] · [[Custom UI & Embedding#Widget Set|Widget Set]] · [[Workshop, Modules & Views#Workshop Module|Workshop Module]]

**Security:** [[Identity & Authentication#Authentication & Session|Authentication & Session]] · [[Data-Level Security Policies#Granular Policy|Granular Policy]] · [[Identity & Authentication#Group|Group]] · [[Mandatory Controls & Classification#Marking|Marking]] · [[Data-Level Security Policies#Object Security Policy|Object Security Policy]] · [[Roles & Authorization#Operation|Operation]] · [[Roles & Authorization#Project|Project]] · [[Data-Level Security Policies#Property Security Policy|Property Security Policy]] · [[Data-Level Security Policies#Restricted View|Restricted View]] · [[Roles & Authorization#Space|Space]] · [[Identity & Authentication#User Attribute|User Attribute]]

**Platform:** [[Marketplace & Packaging#Foundry DevOps|Foundry DevOps]]

## Defer — add later without rework  (46)

**Semantic:** [[Properties#Advanced Property Types|Advanced Property Types]] · [[Ontology & Metadata#Interface (Ontology)|Interface (Ontology)]] · [[Ontology & Metadata#Ontology Branching & Proposals|Ontology Branching & Proposals]]

**Kinetic:** [[Integration & Automation#AIP Tool Exposure|AIP Tool Exposure]] · [[Integration & Automation#Automate|Automate]]

**Dynamic:** [[Temporal & Streaming Substrate#As-Of Read|As-Of Read]] · [[Temporal & Streaming Substrate#Derived Series|Derived Series]] · [[Temporal & Streaming Substrate#Event Object Type|Event Object Type]] · [[Models, Inference & Simulation#Functions on Models|Functions on Models]] · [[Temporal & Streaming Substrate#Geotemporal Series|Geotemporal Series]] · [[Models, Inference & Simulation#Inference History|Inference History]] · [[Models, Inference & Simulation#Live Deployment|Live Deployment]] · [[Models, Inference & Simulation#Model|Model]] · [[Models, Inference & Simulation#Modeling Objective|Modeling Objective]] · [[Models, Inference & Simulation#Optimization|Optimization]] · [[Analysis Surfaces#Quiver|Quiver]] · [[Scenarios#Scenario|Scenario]] · [[Scenarios#Scenario Apply (Commit)|Scenario Apply (Commit)]] · [[Scenarios#Scenario Comparison|Scenario Comparison]] · [[Scenarios#Scenario Overlay|Scenario Overlay]] · [[Models, Inference & Simulation#Simulation|Simulation]] · [[Temporal & Streaming Substrate#Time-Series Property|Time-Series Property]] · [[Analysis Surfaces#Vertex|Vertex]]

**App:** [[Widgets, Binding & Writeback#AIP Agent Widget|AIP Agent Widget]]

**AIP:** [[Tools & Safe Execution#AI Tool|AI Tool]] · [[Agents & Chatbots#AIP Agent|AIP Agent]] · [[Agents & Chatbots#AIP Assist|AIP Assist]] · [[Agents & Chatbots#AIP Chatbot Studio|AIP Chatbot Studio]] · [[Evals#AIP Evals|AIP Evals]] · [[AIP Logic & Blocks#AIP Logic|AIP Logic]] · [[Agents & Chatbots#Agent-as-Function|Agent-as-Function]] · [[Agents & Chatbots#Application State|Application State]] · [[Evals#Evaluator|Evaluator]] · [[Model Gateway & Governance#Language Model Service|Language Model Service]] · [[AIP Logic & Blocks#Logic Block|Logic Block]] · [[Model Gateway & Governance#Model Gateway|Model Gateway]] · [[Retrieval & Grounding#Retrieval Context|Retrieval Context]] · [[Retrieval & Grounding#Semantic Search|Semantic Search]] · [[Tools & Safe Execution#Tool-Calling Mode|Tool-Calling Mode]] · [[AIP Logic & Blocks#Use LLM Block|Use LLM Block]] · [[Model Gateway & Governance#Zero Data Retention|Zero Data Retention]]

**Security:** [[Encryption, Network & Compliance#Cipher|Cipher]] · [[Encryption, Network & Compliance#Egress Policy|Egress Policy]] · [[Identity & Authentication#Identity Provider (SSO)|Identity Provider (SSO)]] · [[Roles & Authorization#Role Set|Role Set]] · [[Identity & Authentication#Scoped Session|Scoped Session]]

## Drop — Palantir-scale machinery we don't need  (39)

**Data:** [[Compute Backends & Economics]]

**Semantic:** [[Object Storage#Object Data Funnel|Object Data Funnel]] · [[Object Storage#Object Indexing|Object Indexing]] · [[Object Storage#Object Set Service (OSS)|Object Set Service (OSS)]] · [[Object Storage#Object Storage V2 (OSv2)|Object Storage V2 (OSv2)]] · [[Object Storage#Phonograph (OSv1)|Phonograph (OSv1)]]

**Kinetic:** [[Audit & Writeback#Writeback Path|Writeback Path]]

**Dynamic:** [[Models, Inference & Simulation#Model Mesh|Model Mesh]]

**App:** [[Slate (Legacy Builder)#Slate|Slate]]

**Security:** [[Mandatory Controls & Classification#Classification-Based Access Control (CBAC)|Classification-Based Access Control (CBAC)]] · [[Encryption, Network & Compliance#Compliance Accreditation|Compliance Accreditation]] · [[Mandatory Controls & Classification#Organization|Organization]] · [[Mandatory Controls & Classification#Purpose-Based Access Control|Purpose-Based Access Control]]

**Platform:** [[Apollo & the Delivery Engine#Apollo|Apollo]] · [[Apollo & the Delivery Engine#Apollo Constraint|Apollo Constraint]] · [[Apollo & the Delivery Engine#Apollo Plan|Apollo Plan]] · [[Releases, Channels & Promotion#Apollo Product|Apollo Product]] · [[Infrastructure Substrate#Compute Mesh|Compute Mesh]] · [[Ecosystem & Lineage#Enrollment|Enrollment]] · [[Ecosystem & Lineage#Enterprise Operating System|Enterprise Operating System]] · [[Releases, Channels & Promotion#Entity & Environment|Entity & Environment]] · [[Ecosystem & Lineage#Gotham|Gotham]] · [[Apollo & the Delivery Engine#Hub-and-Spoke|Hub-and-Spoke]] · [[Marketplace & Packaging#Linked Products|Linked Products]] · [[Marketplace & Packaging#Marketplace|Marketplace]] · [[Marketplace & Packaging#Marketplace Product|Marketplace Product]] · [[Apollo & the Delivery Engine#Orchestration Engine|Orchestration Engine]] · [[Releases, Channels & Promotion#Promotion Pipeline|Promotion Pipeline]] · [[Releases, Channels & Promotion#Recall & Roll-off|Recall & Roll-off]] · [[Releases, Channels & Promotion#Release & Version|Release & Version]] · [[Releases, Channels & Promotion#Release Channel|Release Channel]] · [[Infrastructure Substrate#Rubix|Rubix]] · [[Apollo & the Delivery Engine#Spoke Control Plane|Spoke Control Plane]] · [[Releases, Channels & Promotion#Zero-Downtime Upgrade|Zero-Downtime Upgrade]]

---

[[Foundry — Home (MOC)|← Home]]
