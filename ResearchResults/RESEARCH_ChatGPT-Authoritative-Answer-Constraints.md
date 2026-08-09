# ChatGPT authoritative-answer constraints

**Decision research for:** Wayfinder ticket “Verify the current ChatGPT
authoritative-answer constraints” (#39)  
**Accessed:** 2026-08-09  
**Sources:** Current official OpenAI developer documentation only.  
**Confidence language:** *Documented* means the cited contract says so.
*Observed* means this Codex session made the stated capability available.
*Inference* is an architectural conclusion drawn from documented boundaries,
not a platform guarantee.

## Decision input

Corvus can own the **Canonical answer** as a validated, versioned server result
and can render that exact result in a ChatGPT message-scoped component. It
cannot make the ChatGPT model invoke its tool, render its component, or refrain
from independently narrating or reformulating the result. Therefore:

1. Ordinary mode may use native narration as a convenience layer, never as the
   authoritative theological answer.
2. A narration-safe mode may place the entire substantive answer in a
   Corvus-controlled component and return only non-substantive model-visible
   tool text. It must fail closed if the package is invalid or no safe
   component-compatible result can be returned.
3. That mode is an integrity-preserving presentation *attempt*, not a guarantee
   that ChatGPT will render the component, omit host narration, preserve it in
   history, or prevent a later host turn from answering differently. The UI must
   offer a component-controlled source/receipt route, and the server must retain
   no belief that a visual render occurred merely because it returned one.
4. Server validation, package identity, evidence lineage, source inspection,
   authorization, and research-completion classification are the enforcement
   boundary. Tool descriptors, component bridge methods, and tool descriptions
   are integration metadata—not policy enforcement.

This supports the existing **Authoritative answer surface** and **Evidence
component** glossary terms, but narrows their guarantee: Corvus can prevent
*its own* canonical package from becoming invalid or silently widened; it cannot
control all ChatGPT-authored prose in the surrounding conversation.

## What the documented contracts permit

| Need | What Corvus controls and can verify | Documented limit |
| --- | --- | --- |
| Canonical result | The MCP server can construct and validate the complete Answer evidence package before returning it. `structuredContent` must conform to a declared `outputSchema` when one is provided; `content` and `structuredContent` are visible to both model and component, while result `_meta` is delivered only to the component. | The OpenAI contract does not make `outputSchema` a substitute for server-side validation or prove the model will faithfully restate either visible field. [Tool results](https://developers.openai.com/plugins/reference#tool-results) |
| Exact component presentation | A selected tool may link a UI resource; ChatGPT runs that resource as an iframe and delivers tool results through the MCP Apps bridge. A component can render the server's structured result and widget-only metadata. | UI is optional; OpenAI explicitly says tools must remain useful when a client does not render components. Thus component rendering is not an availability guarantee. [Add UI to your MCP server](https://developers.openai.com/plugins/build/chatgpt-ui) |
| Authoritative data and state | The docs designate MCP server/external-service business data as authoritative; the server validates actions and returns the updated snapshot. Durable cross-session state belongs in storage Corvus controls, not widget state or `localStorage`. | `widgetState` is widget-scoped presentation state, not authoritative or durable product state. [Manage state](https://developers.openai.com/plugins/build/chatgpt-ui#manage-state) |
| Keep private UI hydration out of model context | Result `_meta` is hidden from the model but delivered to the component. It can hold a compact signed package reference or UI-only lookup data. | This is a model-visibility boundary, not permission to put credentials or unreviewed sensitive evidence into a client-rendered component. Server authorization and minimization still apply. [Tool results](https://developers.openai.com/plugins/reference#tool-results) |
| Tool access from the component | The component may call MCP tools through `tools/call` / `window.openai.callTool`; Corvus can validate every such call server-side, including replay-reference integrity and citation IDs. | The bridge lets a component request a call; it does not delegate authorization or validate arguments for Corvus. [ChatGPT UI bridge](https://developers.openai.com/plugins/reference#windowopenai-component-bridge) |
| Host-specific capabilities | ChatGPT exposes optional component features such as display-mode requests, widget persistence, follow-up messages, files, and modals. | They must be feature-detected. A component must not depend on an optional feature for answer integrity. `sendFollowUpMessage` specifically asks ChatGPT to author a message, so it cannot be an authoritative-answer mechanism. [ChatGPT UI bridge](https://developers.openai.com/plugins/reference#windowopenai-component-bridge) |
| Authentication failures | A tool error may return `_meta["mcp/www_authenticate"]` to initiate OAuth. The server can maintain its own authorization/session data and map authenticated requests to its own account model. | The cited Apps docs do not establish a general trustworthy ChatGPT-user identity field for Corvus. Do not equate widget/session identifiers, conversation context, or an OAuth challenge with product identity; require a Corvus-controlled auth binding when identity matters. [Tool-result error contract](https://developers.openai.com/plugins/reference#tool-results) |
| Progress and completion status | A tool descriptor may provide short “invoking” and “invoked” status strings, and the server can return a classified package or an explicit non-answer/error result. | These are display metadata, not a durable job protocol or proof that a long-running investigation completed. [Tool descriptor metadata](https://developers.openai.com/plugins/reference#_meta-fields-on-tool-descriptor) |

## What Corvus cannot guarantee inside ChatGPT

The following are **not** documented Apps SDK guarantees and must not be stated
as product invariants:

- **Invocation:** ChatGPT's model chooses whether and when to call a registered
  tool. A tool description can guide that decision but cannot compel it.
- **Narration fidelity or exclusivity:** the model receives visible
  `structuredContent`/`content` verbatim, and the component bridge can request
  a host-authored follow-up; neither contract constrains host prose to reproduce
  a canonical package exactly. [Tool results](https://developers.openai.com/plugins/reference#tool-results),
  [bridge capabilities](https://developers.openai.com/plugins/reference#windowopenai-component-bridge)
- **Component availability and lifetime:** docs require a tool-only useful
  fallback, so Corvus cannot infer that an iframe rendered, remained mounted,
  was retained in history, or is available on every client. [Add UI to your MCP
  server](https://developers.openai.com/plugins/build/chatgpt-ui)
- **Host UX control:** display mode, modal, close, and external navigation are
  requests to a host-controlled surface, not commands. [ChatGPT UI
  bridge](https://developers.openai.com/plugins/reference#windowopenai-component-bridge)
- **A host-managed background-job lifecycle:** the Apps documentation retrieved
  for this decision specifies invocation status copy and component callbacks,
  but no durable, ChatGPT-guaranteed async job/polling/resume contract. This is
  an absence-of-documentation finding, not proof that no future host facility
  can exist.
- **Cross-turn model context or transcript persistence:** authoritative
  business state must live in Corvus-controlled storage; no current cited Apps
  contract turns a widget instance or its local state into a durable,
  server-verifiable conversation record. [Manage
  state](https://developers.openai.com/plugins/build/chatgpt-ui#manage-state)

## Required fail-closed design

The following are implementation requirements implied by the boundary above;
they are **inferences**, not OpenAI platform behavior.

1. The Theological investigation tool accepts only the question (and a bounded,
   integrity-protected replay reference for Analysis branch). It returns either
   a complete validated Answer evidence package, a validated package with its
   exact Evidence gaps/outcome, or a non-substantive tool error. It never emits
   a plausible prose fallback from unvalidated intermediate data.
2. Package validation occurs on the server before any model-visible content is
   constructed. Validation derives Answer outcome from Answer obligations,
   confirms Citation/source/derivation relationships, enforces access and
   rights policy, and rejects unknown package/schema versions.
3. In narration-safe mode, `structuredContent` is the complete, schema-checked
   package or a bounded rendering projection; `content` contains only status
   text that cannot add theological claims; component-only `_meta` contains at
   most a signed, expiring package reference and harmless UI data. The component
   verifies the package version and integrity data before rendering.
4. Any missing source, invalid receipt, mismatched package digest, failed source
   inspection, rights failure, expired replay reference, or unsupported
   component feature produces an explicit Evidence gap/abstention or tool error.
   It never causes a host-generated “best effort” theological answer to be
   labeled canonical.
5. The server records the result as **returned**, not **shown**, unless a
   separate server-verified acknowledgement protocol is later designed. A UI
   receipt cannot establish what ChatGPT displayed or what the user read.
6. Long investigations use Corvus-owned job state and a narrow status/result
   tool (or finish within a bounded synchronous call). Polling, cancellation,
   idempotency, expiry, and authorization are enforced by Corvus. Do not rely on
   invocation status text or a mounted component as job control.
7. Every component-originated tool call undergoes the same server-side schema,
   authorization, capability, rate, and replay checks as a model-originated
   call. Widget state and model-visible context are untrusted inputs.

## Verification strategy

Contract tests can prove Corvus's side of this boundary:

- invalid package, unknown version, altered digest, incomplete obligation,
  insufficient evidence, expired replay, and unauthorized source inspection
  all return only the defined failure result;
- narration-safe tool results contain no substantive theological assertion in
  `content`, and `structuredContent` passes the exact schema;
- the component renders only a verified package projection and treats absent or
  malformed bridge data as unavailable;
- tool-only fallback preserves the categorical outcome and safe recovery route,
  while never claiming the component rendered;
- all operations remain correct if an optional bridge capability is absent.

An end-to-end ChatGPT Developer Mode fixture can *observe* current behavior:
tool invocation, component render, model narration, reload, follow-up, and
failure display. It cannot convert those observations into a durable platform
guarantee; repeat them after relevant Apps SDK or ChatGPT host changes.

## Current-session observation

*Observed:* this Codex session exposes the official OpenAI developer-docs MCP
server, which supplied the cited documents. It does **not** expose a deployed
Corvus Apps SDK server or a ChatGPT component runtime, so no runtime claim here
asserts that a Corvus tool will be invoked, a component will render, or host
narration will respect narration-safe mode. Those remain deployment-fixture
questions.

