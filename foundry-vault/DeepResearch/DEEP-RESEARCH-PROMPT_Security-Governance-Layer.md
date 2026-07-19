# Deep Research Prompt — Reverse-Engineering Foundry's *Security & Governance* Layer

**What this is:** the sixth in the set. Its single job is to reconstruct, as exhaustively as the public record allows, Palantir Foundry's **full security and governance model** — from identity (**Multipass**, SSO) through the authorization model (roles, markings, row/column policies) to audit, secrets, egress, and compliance.

**How to use it:** paste everything below the line into any deep-research tool. Tool-agnostic. Keep role, scope, question bank, methodology, and output spec; trim the seed list if input is tight.

**Scope note:** the security/governance *spine* as its own layer. We have fragments from the other reconstructions (markings, restricted views, object/property policies, projects/roles); this prompt fills the **identity/auth root** and assembles the end-to-end authorization model. The data/semantic/kinetic/app/AIP internals are out of scope except where access control touches them.

---

# ▼▼▼ PASTE FROM HERE ▼▼▼

## Role

You are a senior security architect and reverse-engineer specializing in enterprise identity (SAML/OIDC/SCIM), authorization models (RBAC/ABAC, row- and cell-level security), audit/compliance, and zero-trust platform design. You are rigorous, source-driven, and allergic to marketing language. Your task is to reconstruct the internal design of **Palantir Foundry's security and governance layer**: identity (**Multipass**), authentication/SSO, the authorization model (roles/operations, markings, granular/object/property policies, CBAC/purpose-based controls), the resource hierarchy, audit/lineage, secrets/egress, encryption, and compliance/deployment security.

## Objective

Produce an **exhaustive, citation-backed technical reconstruction** of how Foundry authenticates users, models their attributes/groups, and authorizes every access — at the resource, row, and cell level — plus how it audits, encrypts, controls egress, and meets compliance regimes. Detailed enough that a competent team could use it as the functional-and-architectural reference to build a faithful (appropriately simplified) clone of the security model. **Prioritize concrete mechanics** (the identity/attribute model, the end-to-end authorization flow, the policy types and how they compose, the audit record, encryption and egress) over conceptual or promotional description.

## Precise scope

**In scope:**
- **Identity & authentication** — **Multipass** (Foundry's internal identity system); external **identity providers** (SAML, OIDC), **SSO**, **MFA**; **user attributes** (key-value; the `multipass:` reserved prefix), **groups** and **provider groups**, attribute mappings; **Organization assignment** (incl. legacy Multipass Group AUM rules); user **preregistration**; service users / tokens (PATs, OAuth2 scopes).
- **The authorization model** — **roles** as sets of **operations**; the request **authorization flow** (how a call is checked end-to-end); resource ownership/sharing; inheritance.
- **Mandatory controls** — **markings** (all-or-nothing), **organizations**, **classification-based access control (CBAC)**, **purpose-based access control**; how mandatory controls compose with roles.
- **Row/column/cell security** — **restricted views**, **granular policies**, **object security policies** (row-level), **property security policies** (column-level), and how they relate to backing-dataset permissions and the Ontology.
- **Resource hierarchy & boundaries** — **Projects** (the primary security boundary), Spaces, the **Compass** resource graph, folders, sharing, and dev→prod separation.
- **Audit, lineage & monitoring** — the **audit log** (audit.2/audit.3): who/what/when/where, retention, append-only guarantees; governance reporting; how lineage supports governance.
- **Secrets, egress & encryption** — credential/secret storage and rotation; **egress policies** (direct vs agent-proxy); **encryption** at rest/in transit (e.g., AES-256-GCM); key management.
- **Compliance & deployment security** — zero-trust posture; FedRAMP / IL / other accreditations; air-gapped/sovereign deployments; tenancy isolation.
- **Admin surface & APIs** — Control Panel; the admin/user/group/role-management APIs; the named internal services (verify).

**Out of scope** (touch only at the seam): the internal mechanics of the data/semantic/kinetic/app/AIP layers — referenced only where a policy is *enforced* there (e.g., marking propagation through transforms, object security policies on object types, AI tools running in a user's permissions).

## Research question bank

Answer every question you can substantiate; record the rest as known unknowns.

**A. Identity & authentication**
1. **Multipass** — what it is, what it stores (users, groups, attributes, tokens), and its role as the identity backbone.
2. **External IdPs / SSO** — supported protocols (SAML, OIDC), the login flow, **MFA**, session management, and how Foundry maps IdP identities to Foundry users.
3. **User attributes** — the key-value model, the reserved `multipass:` prefix, admin-defined attributes, and how SSO populates them on login.
4. **Groups & provider groups** — group membership (direct/inherited), mirroring IdP groups, and how groups drive access.
5. **Organization assignment** — orgs, assignment rules (incl. legacy **Multipass Group AUM rules**), and **preregistration** of users.
6. **Service identities** — service users, **personal access tokens**, **OAuth2 scopes**, third-party app registration.

**B. The authorization model**
7. **Roles & operations** — the default roles (Owner/Editor/Viewer/Discoverer…), how roles are sets of **operations**, custom roles, and grant rules (equal-or-lesser).
8. The **end-to-end authorization decision**: given a request, how are role grants + mandatory controls + granular policies combined to allow/deny? Order of evaluation; default-deny.
9. **Inheritance & sharing** — how grants flow down the resource hierarchy.

**C. Mandatory controls**
10. **Markings** — semantics (must hold all), management, and **propagation** downstream through transforms; stopping propagation.
11. **Organizations**, **CBAC** (classification levels, max-classification), and **purpose-based** controls — definitions and how they layer on markings.

**D. Row/column/cell security**
12. **Restricted views** + **granular policies** — the rule model (user attributes vs columns/values), the documented weighting/limits, request-time query conversion.
13. **Object/property security policies** — row- and column-level security on object types; cell-level security; relation to backing-dataset permissions.

**E. Resource hierarchy & boundaries**
14. **Projects** as the primary boundary; **Spaces**; the **Compass** resource/folder graph; sharing model; dev→prod and environment separation.

**F. Audit, lineage & monitoring**
15. The **audit log** — structure (who/what/when/where), event coverage, append-only guarantees, retention, and export/monitoring.
16. How **lineage** and the dependency graph support governance and impact analysis.

**G. Secrets, egress & encryption**
17. **Secret/credential** storage, encryption, and rotation (incl. how connector credentials are protected).
18. **Egress policies** (direct-connection vs agent-proxy) and network controls.
19. **Encryption** at rest and in transit (algorithms, e.g., AES-256-GCM) and **key management**.

**H. Compliance & deployment security**
20. **Zero-trust** architecture; **accreditations** (FedRAMP, IL levels, others); **air-gapped/sovereign** deployments; **tenancy isolation**.

**I. Admin surface, APIs & internal architecture**
21. **Control Panel** admin surface; the **admin/user/group/role** APIs (e.g., `api/v2/admin`).
22. The named **internal services** (Multipass, the authorization/marking services) — verify names and roles.
23. **History/evolution** of the security model.

## Source strategy (prioritized)

1. **Primary — official docs:** `palantir.com/docs/foundry/authentication/**` (overview, SAML, MFA, org-assignment), `security/**` (markings, restricted-views, single-sign-on-security, projects-and-roles), `platform-security-management/**` (manage-users, manage-markings, manage-granular-policies, manage-roles), `object-permissioning/**`, `api/admin-v2-resources/**`.
2. **Primary — blog, whitepapers & filings:** `blog.palantir.com`; Palantir security/architecture white papers; trust/compliance pages (FedRAMP, etc.).
3. **Primary — source & API refs:** `github.com/palantir`; the admin API reference.
4. **Primary — training:** `learn.palantir.com` (admin/security tracks).
5. **Secondary/Tertiary:** credible third-party (e.g., Microsoft Entra SSO tutorials); community — leads/corroboration only.

Prefer primary, recent, version-stamped sources; capture URL + access date.

## Reverse-engineering methodology & rigor

- **Triangulate** non-trivial claims across ≥2 sources where possible.
- **Tag every claim** — **[Documented]** / **[Inferred]** / **[Speculative]** — with **confidence** and citation.
- **Separate current from legacy** (e.g., legacy Multipass Group AUM rules vs Control Panel org assignment); date-stamp facts; flag in-development features.
- **Flag contradictions** explicitly.
- **Never fabricate** service names, policy semantics, operation names, or accreditation claims. Where the record is silent (e.g., the internal authorization-service design or the full operation catalog), say so and give one best-supported hypothesis labeled **[Speculative]**.
- **Chase named mechanisms** to source: **Multipass** (and the `multipass:` attribute namespace), **markings**, **granular policies**, **object/property security policies**, **roles/operations**, **organizations**, **CBAC**, **Compass**, the **audit log** (audit.2/audit.3), **egress policies**.

## Required output structure

1. **Executive summary** (≈1 page) + the 5–10 most important findings.
2. **Identity & authentication** — Multipass, IdPs/SSO/MFA, attributes, groups, orgs.
3. **The authorization model** *(most technical)* — roles/operations and the end-to-end allow/deny decision.
4. **Mandatory controls** — markings, orgs, CBAC, purpose-based.
5. **Row/column/cell security** — restricted views, granular policies, object/property policies.
6. **Resource hierarchy & boundaries** — projects, spaces, Compass.
7. **Audit, lineage & monitoring.**
8. **Secrets, egress & encryption.**
9. **Compliance & deployment security.**
10. **Admin surface, APIs & internal architecture.**
11. **History & evolution.**
12. **Glossary.**
13. **Confidence & gaps register** — claims + confidence, known-unknowns + resolving source.
14. **Source bibliography** — URLs + access dates, by tier.

Use **tables** for roles/operations, policy types, attribute/marking semantics, encryption, and accreditations. Favor precise mechanics over prose; quote exact semantics/limits verbatim.

## Exhaustiveness bar

Do **not** stop at the overview. Drill until each mechanism is concretely described with a primary citation or recorded as a known unknown with a best-supported hypothesis. Pay special attention to the **end-to-end authorization decision** (how roles + markings + granular policies compose) and the **identity/attribute model** — the make-or-break details for a clone. Aim for a detailed technical white paper; cite extensively; neutral tone.

## Confirmed starting leads (verified — begin here, then expand)

- **Authentication:** `palantir.com/docs/foundry/authentication/overview` (IdPs validate users and provide attributes/groups), `…/authentication/saml-getting-started`, `…/authentication/multi-factor-auth`, `…/authentication/org-assignment` (orgs; legacy **Multipass Group AUM rules**).
- **Identity/attributes:** user **attributes** are key-value; the **`multipass:`** prefix is reserved for internal use → **Multipass** is the identity backbone. **Provider groups** mirror IdP groups; attribute mappings configured in **Control Panel**. `…/platform-security-management/manage-users` (preregistration).
- **Authorization & policies:** `…/security/projects-and-roles` (Owner/Editor/Viewer/Discoverer; roles = sets of **operations**), `…/security/markings`, `…/security/restricted-views`, `…/platform-security-management/manage-granular-policies`, `…/object-permissioning/*` (object/property security policies).
- **Admin API:** `…/api/admin-v2-resources/users/get-user`.

**Named mechanisms to chase:** **Multipass** (+ `multipass:` namespace) · external **IdP / SAML / OIDC / SSO / MFA** · **user attributes** · **groups / provider groups** · **Organization** assignment (+ legacy **AUM rules**) · **PAT / OAuth2 scopes** · **roles** as **operations** · **markings** · **granular policies** · **object/property security policies** · **CBAC** / **purpose-based** controls · **Projects / Spaces / Compass** · the **audit log** (audit.2/audit.3) · **egress policies** · **AES-256-GCM** encryption · *(verify)* the internal **authorization service** design · *(verify)* the full **operation/role catalog** · *(find)* FedRAMP/IL **accreditations**.

# ▲▲▲ PASTE TO HERE ▲▲▲
