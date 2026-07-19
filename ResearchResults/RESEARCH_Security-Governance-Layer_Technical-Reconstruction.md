---
**Artifact:** Deep-research output — technical reconstruction of Foundry's *security & governance* layer.
**Produced:** 2026-06-13, by a deep-research agent run on `DEEP-RESEARCH-PROMPT_Security-Governance-Layer.md`.
**Independent spot-check (by Claude, 2026-06-13):** Confirmed **verbatim** — the **granular-policy weights** (constant-vs-field = 1, collection-vs-field = 1,000, ≤10 comparisons, sum < 10,000) and the **accreditations** (FedRAMP High, Dec 3 2024, covering AIP/Apollo/Foundry/Gotham; CMMC Level 2, Sep 17 2025; IL5/IL6 prior). High-confidence.
**Read with care:** the **end-to-end authorization composition order** is `[Inferred]` (no single doc states it verbatim — but the *layers* are documented). No public **authorization/marking service** is named ("gatekeeper operation" only). The full **operation catalog** is a documented subset. Audit **append-only/immutability** is not stated verbatim. One doc inconsistency flagged: `stemma:mutate-default-branch` vs `mutate-branch`.
**The clone takeaway:** the decisive rule = **a user must satisfy ALL mandatory controls (every Marking, ≥1 Org, classification ≤ max) AND hold a role granting the operation AND pass any granular/object/property policy; default-deny.** Mandatory controls are all-or-nothing and override roles. We replicate this composition; we drop the federal-grade apparatus (CBAC disjunctive releasability, IL6, Cipher) at v1.
---

# Palantir Foundry Security & Governance Layer — A Technical Reconstruction Reference

*Functional-and-architectural reference for a faithful (appropriately simplified) clone. Sources overwhelmingly Palantir primary docs (palantir.com/docs/foundry, accessed June 13, 2026), blog/press, github.com/palantir. Claims tagged [Documented]/[Inferred]/[Speculative]; current vs legacy separated.*

## TL;DR

- Foundry's security layer is a **layered, default-deny** model: external IdP authentication (SAML 2.0 / OIDC) → the **Multipass** identity backbone (users, groups, key-value attributes, tokens) → **discretionary roles** (sets of named operations) combined with **mandatory controls** (Organizations, Markings, CBAC) and **granular / row-column-cell policies**, bounded by **Projects** as the primary security boundary and propagated along the Compass resource hierarchy and data lineage.
- The decisive composition rule: **a user must satisfy ALL mandatory controls AND hold a role granting the specific operation AND pass any granular/object/property policy.** Mandatory controls are all-or-nothing and override roles; access is denied unless every layer passes.
- Accredited at **FedRAMP High plus DoD IL5 and IL6** (and CMMC Level 2 as of Sep 17, 2025), uses **AES-256-GCM** for modern connector credentials and TLS 1.2+ in transit, and exposes an admin API at `api/v2/admin` plus internal `/multipass/api/` endpoints.

## Key Findings

1. **Multipass is the identity backbone** — users, groups, attributes (key-value, multi-valued), tokens. The `multipass:` attribute prefix is reserved; Org RIDs are `ri.multipass..organization.<uuid>`; internal endpoints under `/multipass/api/`. [Documented, high]
2. **Roles are sets of operations.** Owner > Editor > Viewer > Discoverer; each grants only equal-or-lesser. Operations are namespaced (`stemma:`, `compass:`, `s3-proxy:`, `marketplace:`, `webhooks:`, `audit-export:`). Roles inherit down the hierarchy. [Documented, high]
3. **Mandatory controls are all-or-nothing and override roles.** Markings (hold ALL), Organizations (member/guest of ≥1), CBAC classifications (≤ max) gate access regardless of role and propagate along file hierarchy and direct data dependencies. [Documented, high]
4. **Granular policies have explicit weights/limits:** constant-vs-field = 1, collection-vs-field = 1,000; ≤10 comparisons; sum of weights < 10,000. [Documented, high]
5. **Object & property security policies** deliver Ontology-native row/column/cell security independent of backing datasets — a newer, near-instant alternative to restricted views (gated rollout). [Documented, high]
6. **Audit logging is migrating from audit.2 to audit.3** — category-based, low-latency (~15 min), SIEM-pollable via public API. [Documented, high]
7. **Connector credentials use AES-256-GCM** (Foundry worker / agent-proxy) or AES-128-GCM (legacy agent worker); egress governed by direct-connection vs agent-proxy policies enforced with Cilium/eBPF. [Documented, high]

## 2. Identity & Authentication

### Multipass

Foundry's internal identity system. A user record (Admin API `get-user`) contains: user ID, username, primary Organization RID (`ri.multipass..organization.<uuid>`), realm, status, and an attribute map. Verbatim: *"Attributes prefixed with 'multipass:' are reserved for internal use by Foundry and are subject to change,"* and additional attributes *"may be configured by Foundry administrators in Control Panel and populated by the User's SSO provider upon login."* The `palantir-internal-realm` is used for principals not tied to an SSO provider. Internal endpoints: `/multipass/api/{oauth2,me,authz,token,organizations}`; legacy `/multipass/api/administration/users/...`.

### External IdPs / SSO

SAML 2.0 and OpenID Connect 1.0 are supported (SAML documented in depth). Foundry is the Service Provider; metadata exchange includes Entity ID (`urn:uuid:[UUID]`), ACS URL, Single Logout URL, signing certificate. Email-domain regexes (case-sensitive unless prefixed `(?i)`) determine which IdP is offered at login. IdP metadata uploadable or fetched from a discovery URI (auto-refresh on cert rotation; 30-day expiry warning). A Palantir-managed Azure AD ("Central Auth") and a self-service FIDO2-passkey directory are alternatives.

### Attribute mapping & provider groups

Control Panel maps IdP attributes → Foundry attributes (Username, Email, First Name, custom), with a **First**/**All** toggle for multi-valued responses. **Provider groups** mirror IdP group memberships (read-only). Group membership for policy evaluation includes direct **and inherited** memberships.

### MFA & session management

MFA is mandatory (in-Foundry app-based 2FA or in the IdP). Strong methods preferred (FIDO2/CAC hardware, OTP tokens); SMS/email OTP deemed weak. The session token is an ephemeral cookie `PALANTIR_TOKEN`, **default TTL 16 hours**. Accounts auto-deactivate after **30 days** of no login. `revoke-all-tokens-user` forces re-auth.

### Organizations & assignment

Every user has exactly **one primary Organization** (assigned at login via the IdP integration) and can be a **guest** of multiple. **Current:** Control Panel org assignment. **Legacy:** *"Multipass Group AUM rules"* — *"If organization assignment is not configured in Control Panel, then these rules continue to apply. However, Multipass Group AUM rules will be ignored if organization assignment is configured in Control Panel."*

### Preregistration

Admins with preregister permission create the username, group memberships, Org and Marking access before first login (username must match exactly). API: `POST /api/v2/admin/enrollments/<rid>/authenticationProviders/<rid>/preregisterUser`.

### Service identities & tokens

- **Personal access tokens (PATs):** same permissions as the creating user; user-set TTL; not for production.
- **OAuth2:** Authorization Code (on behalf of a user; PKCE for public clients) and Client Credentials (creates a **service user** whose username = client ID; *"By default, the service account does not have access to any resources"*). Refresh tokens rotate each use; reuse after one minute invalidates the grant; inactive >30 days auto-invalidated.
- **Scopes:** Effective access = intersection of (user/service-user permissions) ∩ (app maximum scope) ∩ (scope requested). *"Attempting to request a token with no scope restrictions will generate a token with no permissions."* `api:use-*` scopes (Spring 2025) permit only public platform APIs. Third-party apps must be **registered** AND **enabled per Organization**.

## 3. The Authorization Model (most technical)

### Operations and roles

*"Operations are individual permissions that Foundry applications check… Roles are sets of operations."* Granting a role on a resource grants its operations on that resource and all children.

Confirmed operation catalog (subset):

| Identifier | Namespace | Default role | Capability |
|---|---|---|---|
| `stemma:mutate-default-branch` | stemma (Code Repos) | Owner | Change default branch |
| `compass:read-resource` | compass | Viewer | Basic read |
| `compass:import-resource-from` / `import-resource-to` | compass | Viewer / Editor | Project references |
| `s3-proxy:datasets-read` / `datasets-write` | s3-proxy | Viewer / Editor | Read/write via S3 API |
| `marketplace:read-local-marketplace` / `install-from-local-marketplace` | marketplace | Viewer | Read store / install |
| `marketplace:export-block-set` / `import-blockset-with-provenance` | marketplace | Owner | Export / import products |
| `webhooks:read-privileged-data` | webhooks | none (opt-in) | Full webhook history |
| `audit-export:view` / `orchestrate-v3` | audit-export | gatekeeper / Org admin | View / orchestrate audit export |

*Doc inconsistency:* manage-roles uses both `stemma:mutate-default-branch` and `stemma:mutate-branch` for the same capability — verify live. No public `ontology:`/`phonograph:` operation strings; the generic "Download" operation has no namespaced identifier.

### Default roles & the grant rule

**Owner > Editor > Viewer > Discoverer.** *"Each role can assign other users the same or lesser role."* Discoverer lacks download; Viewer/Editor/Owner include download.

### Custom roles & role sets

Roles are customized via **role sets** — context-scoped groups of roles. *"The three available contexts for role sets are the Project context, Ontology context, and Marketplace Installation context."* To edit a default role, copy an existing role set into a custom one; roles can "Include" other roles. Requires "Manage roles and role sets" (Org Administrator).

### End-to-end authorization decision (composition)

[Inferred from documented rules; default posture = **deny**] Access is granted only if all hold:
1. **Authentication/session valid** — Multipass token unexpired, MFA satisfied.
2. **Mandatory controls satisfied** — member/guest of ≥1 applied Organization; holds **all** applied Markings; if CBAC, classification ≥ resource max. All-or-nothing, independent of role: *"Regardless of role, a user cannot access a file in any way unless the user satisfies all Marking requirements."*
3. **Role grant** providing the specific operation (direct or inherited).
4. **Granular / object / property policy** (if configured) passes at row/column/cell level.

Role grants and mandatory controls **inherit down** the hierarchy. Data access (not role grants) additionally follows **direct data dependencies (lineage)** — being Editor on a Contour analysis does not guarantee access to its underlying data.

### Inheritance & sharing

Recommended pattern: grant **group** roles at the **Project** level (three groups → Viewer/Editor/Owner, Project default Discoverer). Moving data between Projects requires explicit **Project references** (`import-resource-from` on source + `import-resource-to` on destination).

## 4. Mandatory Controls

### Markings

Foundry's mandatory access control. *"Access to a Marking is binary (all-or-nothing)… a user must be a member of all Markings applied to a resource to access it."* Markings can hide a resource's existence. Grouped into **marking categories** (cannot be deleted once created). Per-marking permissions: Manage, Apply (apply ≠ membership), membership. **Propagation:** along file hierarchy and direct data dependencies, at the **transaction** level (SNAPSHOT depends on latest upstream transaction; APPEND/UPDATE carry older dependencies). *"Markings always propagate."* **Stopping:** `stop_propagating` (Markings) / `stop_requiring` (Organizations) on a **protected branch with ≥1 approver**; each removed Marking = a separate approval. "Severing" is deprecated.

### Organizations

All-or-nothing silo. *"Every user is a member of only one organization, but can be a guest member of multiple… users must be a member or guest member of at least one organization applied to a Project."* Inherited via hierarchy and dependencies.

### CBAC (classification-based access control)

*"Not enabled by default… Configuration requires Palantir involvement."* Hierarchical: *"Every user can only access data classified at or below their own classification level."* A **max classification** is required. **Distinctive: disjunctive components** — *"Classification markings can have disjunctive components, where users belonging to one of the groups… can satisfy the CBAC access condition"* (releasability, e.g., country A OR B). Can govern Ontology resources in Compass projects.

### Purpose-based access control (PBAC)

Users apply for a **Purpose** (a governance-scoped data bundle) rather than individual datasets; rationale is recorded persistently for audit by both requester and approver.

### Mandatory control properties (Ontology)

Object-type properties (**OSv2 only**) mapped to a marking column on a restricted view; secure **all other properties in the same datasource** per row. Support markings, orgs, or classifications (not combined). Must be **required and non-null** (empty array = all users pass that row).

### Project constraints

Limit which Markings may be applied in a Project: No constraints (default) / Allowed / Prohibited. Prevents accidental joins of incompatible data; a violating dataset cannot build.

## 5. Row / Column / Cell Security

### Granular policies

*"A granular policy is a set of rules and logical operators that compare user attributes, columns or properties, and values."* User attributes: User ID, Username, Group IDs/names, Authorized group IDs (scoped sessions), Organization Marking IDs, Marking IDs, custom. **Limits (verbatim):** *"A single policy can have up to ten comparisons."* *"A comparison of a constant against a field is given a weight of 1. A comparison of a collection against a field is given a weight of 1,000. The sum of the weights across all the comparisons in a policy must be under 10,000."* Identifiers must be UUIDs; null policy-column rows inaccessible to all. **Request-time conversion:** templates compile to a query returning only permitted rows.

### Restricted views (RVs)

Built on a backing dataset; **cannot be a transform input**; read-only; a granular policy determines visible rows; can back an object type. Marking column = STRING/STRING ARRAY of Marking UUIDs (optional `marking_type.mandatory` typeclass). **Policy changes require a rebuild.** Users who should only see data via the RV must **not** have upstream access.

### Object & property security policies (cell-level)

Configured on the object type in Ontology Manager, independent of backing sources (gated rollout). **Object policy** = row visibility; **property policy** = column visibility; a property requires passing **both** → **cell-level** security. Advantages over RVs: **near-instant updates** (no rebuild), **streaming support**, managed on the object type. To view an instance: Viewer on the object type + pass granular policy + pass marking/org/classification (backing-dataset Viewer not required when a policy is configured). Note: Multipass attribute changes "are still cached for a short period."

### Data source vs object/property policies

Data source policies (RVs + MDOs) suit control **outside the Ontology** (e.g., Code Workspaces); object/property policies are Ontology-scoped.

## 6. Resource Hierarchy & Boundaries

**Projects** are the primary security boundary ("buckets of shared work"); roles/access requirements best applied here; each user has a personal Project. **Compass** is the filesystem/resource-graph app. **Project references** link resources across Projects with acknowledgment. **Spaces** (formerly namespaces) are high-level containers of Projects sharing one Ontology, restricted by Organization(s); the space is the first path element (`space/project/sub-folder/my-file`). **Dev→prod** via discrete Projects (Datasource / Transform / Ontology) with separate groups + protected branches with required approvals. Cross-enrollment sharing via Peer Manager (peer connection's CBAC marking caps classification).

## 7. Audit, Lineage & Monitoring

### Audit logs (audit.2 → audit.3)

audit.3 is recommended for new implementations. **Properties:**
- **Category-based:** *"every event must be logged under one or more standardized categories"* (e.g., `dataLoad`, `dataExport`).
- **Promoted fields:** `categories`, `entities` (the "What"), `origins`, `product`, `result` (SUCCESS/ERROR/UNAUTHORIZED). `requestFields`/`resultFields` vs audit.2's `request_params`/`result_params`.
- **Latency:** *"Approximately 15 minutes or less, versus 24 or more hours for audit.2."* GA following a late-Nov 2025 infrastructure update.
- **Delivery:** SIEMs poll directly — `list-log-files` + `get-log-file-content` under `api/v2/audit/organizations/<org-rid>/...`; or export to a per-Org dataset (retention max **730 days**).
- **Limitation:** only the `uid` user field is populated (userName/realm/groups unset, by design, to avoid real-time IdP lookups).
- **Operations:** `audit-export:view` (gatekeeper) and `audit-export:orchestrate-v3` (Org admin).

Separate **Foundry application logs** exist but are *"not audit logs"* (no delivery guarantee).

### Lineage & dependency graph

The **Data Lineage** app: **simulation mode** previews where a Marking would propagate; **permissions coloring** ("View as" a user) troubleshoots access. Broader **Workflow Lineage** (objects/functions/actions/automations/apps/models) is backed by **Foundry Dependency Services (FDS)**. PRs surface impact analysis.

## 8. Secrets, Egress & Encryption

### Credential storage & rotation

*"All credentials are encrypted and stored securely."*
- **Foundry worker / agent-proxy:** *"External system credentials are stored with AES-256-GCM server-side encryption and can only be decrypted by containers triggered by authorized users."*
- **Legacy agent worker:** *"…AES-128-GCM encryption with keys stored on the agent… Decrypted credentials are automatically deleted from memory after execution."*
- **Rotation:** source-based external transforms support rotating credentials without code changes.

### Encryption algorithms & key management

| Layer | Algorithm | Notes |
|---|---|---|
| In transit | TLS 1.2 + strong ciphers | service-to-service |
| At rest (Filesystem/blob) | Application-level encryption | "all Foundry Filesystems… application level encryption" |
| Connector creds (modern) | **AES-256-GCM** | Foundry worker / agent proxy |
| Connector creds (legacy) | **AES-128-GCM** | keys on agent |
| Envelope (Cloud Pak) | AES wrapped by **RSA-2048** | |
| Cipher (field-level) | AES_GCM_SIV / AES_SIV / SHA-256/512 + pepper | user-facing |

**Cipher** is the in-platform field-level encryption product: **Channels** (algorithm/keys), **Licenses** (Operational User / Data Manager / Admin) control encrypt/decrypt at value vs column level; rate-limited and cell-level auditable.

### Egress & network controls

- **Direct connection** (Foundry worker): external system accepts inbound from Foundry; egress via direct-connection policies; Palantir proxies do SNI/TLS inspection on 443 by default.
- **Agent proxy:** *"no inbound connections are initiated from Foundry"*; agent host needs outbound; policies **only on Rubix**.
- **Legacy agent worker:** compute on customer host; Foundry-side egress policies don't apply.

Egress policies (domain/IP/CIDR) configured by the **Information Security Officer**; destinations immutable once created. Enforcement via **Cilium / eBPF** + an infra proxy. **Compute modules** default to *"a 'zero trust' security model"* (no external network until a source is attached).

## 9. Compliance & Deployment Security

### Accreditations

| Accreditation | Status | Source / date |
|---|---|---|
| FedRAMP High | Granted for PFCS & PFCS-SS; covers AIP, Apollo, Foundry, Gotham, FedStart, Mission Manager | Business Wire, **Dec 3, 2024** |
| DoD IL5 / IL6 | Authorized (one of few CSPs at IL6) | Apollo-based |
| CMMC Level 2 | Via C3PAO assessment (NIST SP 800-171) | Business Wire, **Sep 17, 2025** |
| SOC 2 Type II, ISO/IEC 27001 | Maintained | Trust portal |

### Zero-trust & deployment

**Apollo** is the deployment/change-management backbone for FedRAMP/IL5/IL6 environments (a centralized "Baseline" team approves changes; change history addresses AU controls). **PFCS** runs on AWS GovCloud / Azure Government; **FedStart** hosts third-party SaaS in Palantir's accredited environment. **Tenancy isolation** via Organizations + spaces + per-Org markings + member-discovery settings. Self-hosted guidance mandates network segmentation, deny-by-default ingress, proxied/allowlisted egress, DLP/IDS, and zero-trust device posture.

## 10. Admin Surface, APIs & Internal Architecture

### Control Panel

Authentication (IdP/SAML/MFA/Org assignment), Organizations & spaces, Roles/role sets, Users, Groups, Markings, Project constraints & templates, Third-party applications, Network egress/ingress, Scoped sessions, Log observability, File access presets.

### APIs

- **Admin API** `/api/v2/admin/...`: users (`get-user`, `get-current-user`, `search-users`, `preregisterUser`, `revoke-all-tokens-user`), groups, organizations (`list-available-roles`), authentication-providers, enrollments.
- **Audit API** `/api/v2/audit/organizations/<org-rid>/...`: `list-log-files`, `get-log-file-content`.
- **Internal** `/multipass/api/{oauth2,me,authz,token,organizations}`; OAuth2 under `/multipass/api/oauth2/`.

### Named internal services (confirmed in docs)

| Service | Role |
|---|---|
| **Multipass** | Identity backbone (users/groups/attributes/tokens, `/multipass/api/authz/`) |
| **Compass** | Filesystem / resource graph (`compass:` operations) |
| **Stemma** | Code Repositories (`stemma:` operations) |
| **Phonograph** | Object Storage V1 |
| **magritte-coordinator** | Data Connection coordination |
| **Foundry Dependency Services (FDS)** | Workflow lineage / dependency registry |
| **Apollo** | Deployment & change management |
| **Rubix** | Kubernetes infrastructure |

The docs use *"gatekeeper operation"* but do **not** name a discrete "authorization service" or "marking service" — these are documented as functional concepts only. The glossary names a **"credential collector"** (SAML collector) and an optional **"user manager"** login-flow module.

## 11. History & Evolution

- Org assignment: legacy Multipass Group AUM rules → Control Panel (current).
- Marking propagation: severing (deprecated) → `stop_propagating` / Marking removal with approval.
- Row/cell security: restricted views + MDOs → Ontology-native object/property policies (near-instant, streaming).
- Object storage: Phonograph (V1) → OSv2 (mandatory control properties).
- Audit: audit.2 → audit.3 (category-based, ~15-min, API-pollable; GA late 2025).
- Data connection: agent worker (legacy) → Foundry worker + agent proxy on Rubix.
- API security: broad namespace scopes → `api:use-*` (Spring 2025).
- OAuth management: Control Panel → Developer Console. Spaces: rebranded from namespaces.

## 12. Glossary

- **Multipass** — internal identity system / backbone.
- **Realm** — authentication source; `palantir-internal-realm` for Foundry-created principals.
- **Organization** — mandatory silo; one primary per user + guest memberships.
- **Space** — container of Projects + one Ontology, restricted by Org(s).
- **Project** — primary security boundary.
- **Marking** — all-or-nothing mandatory control; grouped in categories.
- **CBAC** — hierarchical classification control with disjunctive releasability.
- **Operation** — atomic permission (namespaced identifier).
- **Role / Role set** — set of operations / context-scoped group of roles.
- **Granular policy** — rule template compiled to a query at request time.
- **Restricted view** — row-filtered, read-only dataset.
- **Object / property security policy** — Ontology-native row/column/cell security.
- **Scoped session** — a session limited to a chosen subset of Markings.
- **Purpose** — PBAC access bundle with recorded rationale.
- **Cipher** — field-level encryption (Channels/Licenses).

## 13. Confidence & Gaps Register

| Claim / area | Confidence | Resolving source if open |
|---|---|---|
| Multipass stores users/groups/attrs/tokens; `multipass:` reserved | High [Documented] | Admin API `get-user` |
| Roles = namespaced operations; equal-or-lesser grant | High [Documented] | manage-roles |
| Composition order (auth → mandatory → role → granular) | Med-High [Inferred] | No single doc states ordering |
| Markings/Orgs all-or-nothing + propagate | High [Documented] | markings |
| Granular policy weights/limits (1 / 1,000; ≤10; <10,000) | High [Documented, verified] | manage-granular-policies |
| AES-256-GCM / AES-128-GCM creds | High [Documented] | data-connection/architecture |
| FedRAMP High + IL5/IL6; CMMC L2 | High [Documented, verified] | Business Wire (Dec 3 2024; Sep 17 2025) |
| audit.3 latency ~15 min, API-pollable | High [Documented] | monitor-audit-logs |
| Audit append-only / immutability | Open [Unknown] | Not stated verbatim |
| Full operation catalog | Partial [Documented subset] | No public exhaustive list |
| Named authorization / marking service | Resolved-negative | Not publicly named |
| OIDC login-flow specifics | Low [existence only] | SAML documented in depth |

**Known unknowns:** audit append-only/immutability guarantee; the exhaustive operation catalog (`ontology:`/`phonograph:` strings not public); OIDC specifics; the `stemma:mutate-default-branch` vs `mutate-branch` inconsistency.

## 14. Source Bibliography (by tier; accessed June 13, 2026)

**Tier 1 — Palantir docs:** authentication/{overview, saml-getting-started, saml-other-idp, multi-factor-auth, org-assignment, user-directory}; security/{single-sign-on-security, markings, restricted-views, classification-based-access-controls, project-constraints, projects-and-roles, orgs-and-spaces, security-glossary, audit-logs-overview, audit-log-categories, monitor-audit-logs, download-controls, checking-permissions, property-security-markings}; platform-security-management/{manage-users, manage-groups, manage-roles, manage-markings, manage-granular-policies, manage-restricted-views, manage-orgs-and-spaces}; platform-security-third-party/{writing-oauth2-clients, register-3pa, user-generated-tokens}; object-permissioning/{object-security-policies, managing-object-security, configuring-rv-access-controls}; object-link-types/mandatory-control-properties; data-connection/{architecture, agent-proxy, agent-worker, configure-egress, network-egress-observability}; administration/{configure-scoped-sessions, configure-logging}; api/{admin-v2-resources, audit-v2-resources}; cipher/{overview, core-concepts}; data-lineage/{see-impact-marking-changes, check-permissions}; peer-manager/core-concepts.
**Tier 2 — Palantir blog & press:** "Purpose-based Access Controls at Palantir"; "The Next Generation of Audit Logging at Palantir"; "How Palantir Meets IL6 Security Requirements with Apollo"; Business Wire — FedRAMP High (Dec 3 2024), CMMC Level 2 (Sep 17 2025); platforms/foundry/open-architecture.
**Tier 3 — GitHub:** palantir/palantir-oauth-client; palantir/foundry-platform-python; palantir/palantir-cloudpak.
