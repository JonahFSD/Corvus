# ADR-0013: Deploy the ChatGPT App on Vercel with Convex

- Status: accepted
- Date: 2026-07-26

## Context

ADR 0006 defines one cohesive stateless Investigation module behind a thin Apps SDK/MCP transport. ADR 0007 selects strict TypeScript/ESM on Node.js, and ADR 0009 selects Convex for immutable Ontology and Corpus releases plus vector discovery. The product needs a stable public HTTPS Streamable-HTTP endpoint at `/mcp`, versioned Evidence-component resources, private YouVersion and Gloo adapters, isolated environments, safe deployment and rollback, and end-to-end verification in ChatGPT Developer Mode.

Corvus already uses Vercel and Convex. A prior planning draft selected Render and PostgreSQL without repository or product evidence; that draft is rejected by this decision. No Render service or database is part of the architecture.

## Decision

Deploy Corvus as two long-lived Vercel/Convex project pairs: production and staging. The separate Vercel projects give each environment a distinct OIDC subject without depending on undocumented custom-environment claims; the separate Convex projects provide an independent data, function, configuration, and IAM boundary. Use a Vercel Node.js Function with Fluid Compute for the public MCP endpoint and serve content-addressed Evidence-component bundles from the same Vercel deployment.

Do not split individual MCP tools, providers, storage operations, or UI hydration into independently deployed services. The deployed composition preserves the accepted module boundaries:

- `/mcp`: Streamable HTTP for exactly `theological_investigation`, `inspect_source`, and `branch_analysis`;
- versioned MCP Apps UI resources and content-hashed static assets;
- a minimal bounded readiness endpoint; and
- no public provider, ontology administration, release publication, general Convex, or arbitrary URL-fetch API.

Use the Node.js runtime, not Vercel Edge Functions. Pin the Node major, lockfile, function region, and `maxDuration` in repository configuration. Streaming remains bounded by the application deadline and Vercel's configured duration; it is not a durable session.

### Network and deployment topology

Use a stable custom production hostname such as `mcp.<controlled-domain>/mcp` and a separate staging hostname. Vercel terminates public TLS and routes the MCP endpoint to the Node Function. The login-free ChatGPT tools declare `securitySchemes: [{ type: "noauth" }]`. Fixture transport keeps every paid provider capability disabled. A production tool may invoke YouVersion, Gloo, or another paid/limited provider only after the transport spike proves a ChatGPT-origin caller gate using OpenAI's managed client certificate or published OpenAI egress enforcement, with rejection before paid work for direct callers outside that boundary.

Do not claim inbound mTLS unless a Vercel proof verifies client-certificate handling end to end. OpenAI's managed client certificate and published egress ranges may be used as the paid-capability origin gate only after Developer Mode and production connectivity tests prove that the chosen Vercel/WAF configuration preserves normal requests, rejects a direct non-OpenAI caller, resists forwarded-header spoofing, handles certificate or range rotation, and fails closed. Anonymous fixture/read-only operation is not an authorization path to a paid capability. If neither mechanism can be enforced safely on Vercel, provider spend remains zero; adding user OAuth requires a separate product decision because the Challenge access contract is login-free.

Place Vercel compute in `iad1` and create Convex deployments in US East (N. Virginia) unless the pre-provisioning latency and residency benchmark records a different supported pairing. Convex region selection is effectively a migration decision, so record it before loading production data.

### Environments and promotion

Use four compositions:

1. **Local and CI** use deterministic fixture providers plus `convex-test` and the local Convex backend. Normal checks require no live provider or production credential.
2. **PR preview** runs in the staging Vercel project against synthetic fixtures by default. An ephemeral Convex preview may be used only behind a beta-feature gate that proves fresh creation, fixture-only seeding, non-reuse, expiry, and cleanup. It receives no YouVersion, Gloo, production Convex, production replay-signing, or restricted-corpus secret.
3. **Staging** is the persistent production deployment of the separate staging Vercel project, backed by the separate Convex staging project and separately scoped provider credentials. It is the MCP Inspector, Developer Mode, live-contract, security, failure-injection, component, and narration-fidelity environment.
4. **Production** is built from the exact verified commit and lockfile after compatible Convex functions have been deployed separately. CI compares source, dependency-lock, generated-contract, component-bundle, and server-build digests with the approved staging provenance and rejects unexplained differences.

A separate CI job deploys Convex functions with an environment-scoped deploy key carrying only the required deploy permission. The key never enters Vercel configuration or runtime. Deployment order is expand-compatible Convex schema/functions, verify the selected release and backward-compatible readers, deploy the matching Vercel runtime from the approved commit, run production smoke gates, and only later remove obsolete schema/readers. Environment changes require a new deployment and repeat the release gate.

Vercel rollback changes the application artifact and environment snapshot, not Convex data. A rollback runbook verifies that the target artifact supports the selected immutable Convex release. Convex rollback selects a previously validated release pin without mutating its documents.

### Vercel-to-Convex identity

Enable Vercel OIDC in team-issuer mode. At request time, the Node Function obtains its short-lived Vercel token and uses Vercel's audience exchange to mint a token whose `aud` is the exact Convex read audience for that environment. Convex `customJwt.applicationID` pins that audience and its issuer/JWKS configuration pins the Vercel team issuer. Every exported read also requires the exact production or staging Vercel project/environment subject.

Production and staging identities cannot cross projects. PR previews use fixtures by default; an optional Convex preview must have a separately verified preview subject and a fixture-only backend. The component and browser receive no Convex token or URL for privileged access. Release publication uses a separate short-lived CI publisher identity and internal Convex functions; the Vercel runtime cannot publish or mutate releases.

A pre-implementation trust spike must prove Function-time token acquisition, Convex-specific audience exchange, exact `customJwt.applicationID`, issuer/JWKS validation, exact project/environment subject enforcement, expiry/refresh behavior, wrong-project and wrong-environment rejection, local-test composition, and zero token leakage. Failure blocks implementation of the live store; it does not justify silently adding a shared database credential or second backend.

Until that spike passes, the only approved deployed composition is fixture-backed Vercel transport with an isolated synthetic component. Live Convex adapter work begins after—not in parallel with—the trust proof. The exact spike cases and phase boundary are mandatory in [Implementation readiness](../implementation-readiness.md).

### Request execution and caching

Each MCP call owns a complete request context, cancellation signal, global deadline, capability budget, provider budget, and exact release pins. The runtime may reuse stateless clients and immutable source-oriented caches across Fluid Compute invocations, but global process memory is never a conversation, authentication, replay, or user boundary.

Bound question, reference, evidence, structured-result, `_meta`, and total response sizes well below Vercel's 4.5 MB request/response limit. Oversized or deadline-exhausted work returns a valid degraded or abstaining Answer evidence package when possible. Provider calls use explicit connect/read deadlines, bounded retries with jitter, cancellation, and circuit breakers.

Every dynamic MCP, Source-inspection, Analysis-branch, error, and result-hydration response sends `Cache-Control: no-store`. Only versioned component HTML and content-hashed JS/CSS/assets that contain no request or licensed source data may use immutable public caching. Treat every component resource URI as a compatibility cache key and change it when its contract or bundle changes.

### Caller and abuse controls

The MCP surface remains read-only and login-free. Anonymous direct-internet access is limited to fixture or zero-provider-cost capabilities. Paid capabilities require an end-to-end-proven ChatGPT-origin gate. The application stores no IP address, fingerprint, cookie, belief profile, question history, or durable user quota profile. Protect provider cost and availability with layered, content-free controls:

- Vercel Firewall/WAF rate limits and DDoS protection scoped to `/mcp`;
- verified managed-client-certificate or OpenAI-origin enforcement before paid work, with spoofing and rotation tests;
- strict body, concurrency, deadline, traversal, evidence, and provider-call budgets in the application;
- provider-side quotas and spend caps;
- circuit breakers and emergency disable switches by capability; and
- narrow reference validation for `inspect_source` and signed, expiring Replay references for `branch_analysis`.

Exercise WAF rules against real ChatGPT connectivity before enforcing them. Do not key product analytics or authorization decisions from network metadata supplied by the platform.

Assume ChatGPT traffic may arrive through shared OpenAI egress. Per-IP WAF limits begin observe-only and are never treated as per-user fairness or identity. A published-range allowlist, if proven, treats the entire current OpenAI range as one origin class and is updated fail-closed through a tested runbook. Inside that gate rely on global concurrency, application work budgets, provider-side quotas and monetary caps, capability kill switches, and overload shedding before provider calls. Production provider spend defaults to zero until both the caller-gate spike and the release profile's explicit nonzero daily cap pass. If the gate cannot prevent a direct non-OpenAI caller from reaching paid work, provider spend remains zero. No stable identity is inferred from network metadata.

### Secrets and privacy

Scope runtime configuration to its Vercel and Convex project pair. Keep Convex deploy and release-publisher authority only in the separate CI secret boundary. At minimum, separate YouVersion, Gloo, replay-signing, Vercel OIDC/Convex trust configuration, restricted-corpus acquisition, and backup/export authority. Preview environments receive fixture-only values. Validate configuration without printing it and support overlap for replay-signing-key rotation.

Application logging uses an explicit allowlist and excludes questions, answers, excerpts, Citation content, raw provider exchanges, request bodies, authentication headers, remote IP addresses, inferred beliefs, pastoral context, and Convex query arguments. Platform logs and drains are part of the privacy boundary; no drain is enabled until its fields, destination, access, retention, and deletion behavior are reviewed.

### Availability, backup, and operations

Vercel readiness verifies application configuration, the exact compatible published Convex release pin, and component resources. It never calls YouVersion, Gloo, vector search, or broad ontology traversal. Provider degradation belongs in the Answer evidence package rather than instance health.

Use Convex scheduled backups where the selected plan supports them and export every immutable production release to separately controlled encrypted storage when its rights allow. A complete recovery set includes repository revision, compiled artifacts and digests, Convex data export, deployed function version, environment inventory, and secret-recovery procedures. Complete a nonproduction restore drill before submission and after material storage changes.

Maintain runbooks for deploy, promotion, application rollback, Convex release rollback, backup/restore, provider and signing-key rotation, corpus-rights revocation, provider outage, Convex outage, Vercel-region failure, WAF lockout, and emergency shutdown.

Run the synthetic native-narration fidelity canary after every deployment and at least every 24 hours while the public tool is enabled. Any added, missing, broadened, or misbound substantive proposition disables ordinary narration. A separately tested narration-safe mode may keep the tool online by returning only non-substantive model-visible status and rendering the unchanged canonical package from component-only hydration in a clearly labeled Evidence view. If the host still improvises substantive narration or does not render that component faithfully, activate the public-tool kill switch. Exact canary comparisons, safe-mode behavior, workload limits, reference lifetimes, load profiles, retention, RPO/RTO, and required test commands are defined in [Implementation readiness](../implementation-readiness.md).

### Release gates

A deployment is releasable only when:

1. `npm run check`, the deterministic evidence gate, storage contract suite, and production build pass, with `npm run check` expanded beyond its current workflow-only coverage to include every non-live product suite in Implementation readiness;
2. MCP Inspector and ChatGPT Developer Mode initialize the stable `/mcp` URL and discover exactly the three approved tools;
3. normal, malformed, degraded, abstaining, Source-inspection, Analysis-branch, cancellation, and timeout cases satisfy their contracts;
4. the Evidence component renders under its declared CSP and versioned resource URI while deployment-time and recurring native-narration canaries preserve the package's ordered substantive propositions, Citation bindings, Evidence gaps, Answer outcome, and Pastoral handoff, and narration-safe mode passes without improvised host claims;
5. Vercel OIDC audience exchange and Convex trust, ChatGPT-origin isolation for paid capabilities, separate-project isolation, CI-only deploy authority, preview secret absence, release compatibility, reference lifetime and key-overlap rules, payload budgets, WAF behavior, log redaction, and provider-spend controls pass;
6. the deployed custom domain, TLS, streaming, provenance comparison, rollback, Convex release rollback, and restore drill pass; and
7. the numerical data, latency, duration, traversal, concurrency, response-size, load, spend, retention, RPO, and RTO envelope in Implementation readiness is recorded in the release profile and met by the representative benchmark.

## Rejected alternatives

- Deploy Corvus on Render or provision Render PostgreSQL.
- Retain PostgreSQL/pgvector beside Convex.
- Use Vercel Edge Functions for the MCP runtime.
- Deploy one Function or service per tool/provider.
- Give runtime code a Convex deploy or release-publisher credential.
- Connect the Evidence component or browser directly to privileged Convex functions.
- Use one Vercel project whose custom staging environment cannot be distinguished from preview by documented OIDC claims.
- Put a Convex deploy key in Vercel environment variables.
- Give PR previews live-provider or restricted production data, or rely on a beta Convex preview as durable staging.
- Cache dynamic MCP or hydrated Scripture responses at the edge.
- Infer a durable user identity for anonymous rate limiting or analytics.
- Treat Vercel rollback as a Convex data rollback.

## Consequences

The deployment now matches the owner's platform: Vercel provides the public Node/Streamable-HTTP runtime, stable component assets, TLS, WAF, previews, promotion, and application rollback; Convex provides typed immutable release storage, vector discovery, environment isolation, and data recovery. The cohesive Investigation interface remains portable even though the deployment composition is intentionally concrete.

The architecture accepts bounded serverless execution, Vercel log/privacy constraints, Convex's document and transaction limits, application-enforced graph traversal, and function-surface read-only enforcement. These are measurable release obligations. Render and PostgreSQL are not fallback defaults; a different platform requires benchmark evidence and a superseding ADR.
