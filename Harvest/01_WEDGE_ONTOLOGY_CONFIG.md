# 01 — Wedge Ontology Config (Bailey's domain)

> The artifact the PoC is built from. A declarative ontology for the **one** carrier-relations workflow: carriers, circuits, contracts, escalations, SLAs, their links, and three real governed actions. The engine (`02_WEDGE_DB_SCHEMA`) never changes; **this file is the entire surface Phase 2 produces** (blueprint §6).
>
> **Synthesized from**, with provenance:
> - OpenFoundry's action **`input_schema` + `config` split** (`action_types` table, VERIFIED; `action_type.rs` `ActionInputField`, VERIFIED TC-3) — its genuinely good shape.
> - The **validate → preview(dry-run) → execute** contract (`actions.rs` `validate_action`/`plan_action`/`execute_action`, VERIFIED AC-1).
> - The **enum vocabularies** from `type_system.rs` (VERIFIED). OpenFoundry defines **9 property types** `{string, integer, float, boolean, date, timestamp, json, array, reference}` (L3–5), **4 cardinalities** `{one_to_one, one_to_many, many_to_one, many_to_many}` (L42–46), and **5 operation kinds** `{update_object, create_link, delete_object, invoke_function, invoke_webhook}` (`action_type.rs`). We adopt the operation-kind set verbatim; we keep 3 cardinalities (modeling `many_to_one` as `one_to_many` reversed); and we use Postgres-friendly **aliases** for scalars — `text`←`string`, `decimal`←`float` — plus a real `enum` base type, since OpenFoundry has *no* value-type concept (its `json`/`array`/`reference` we don't need for this workflow). So this list is *informed by* OF, not copied verbatim.
> - Our resolved decisions: **CEL** for submission criteria + row policies (verified on `@marcbachmann/cel-js`, the macro-complete engine — see `repro/cel_check.mjs`, 17 assertions pass), PK mandatory on create, links first-class, soft-delete.

---

## Design choices baked in (and why they differ from OpenFoundry)

1. **Value types are reusable** (`sla_status`, `email`, `money`). OpenFoundry has *no* `value_type` table — validation is an inline per-property `validation_rules` blob that **nothing reads** (`type_system.rs`, VERIFIED). We make the constraint real (compiled to a `CHECK`, see `02` §3).
2. **Submission criteria and row policies are CEL; value-type constraints compile to a SQL `CHECK`** (enum/regex/range — see `02` §3, *not* runtime CEL). OpenFoundry has *no* expression language at all (B1, VERIFIED), so the CEL choice is unrefuted and stands. Pin **`@marcbachmann/cel-js`** (macro-complete: `in`, `size()`, comparisons, `exists`, `value.matches()`); the simpler `cel-js` is a lighter subset that lacks `matches()`. `[verified]`: all 17 criteria below — incl. role checks, `size()`, range, and `in` — evaluate correctly (`repro/cel_check.mjs`, exits 0). Keep date math *out* of CEL: the executor binds a server-derived `days_to_renewal` and CEL does a plain compare (avoids `timestamp()`/`duration()` portability traps).
3. **`create` rules specify a `pkey`.** OpenFoundry's `ActionPlan` has **no `CreateObject` variant at all** (VERIFIED AC-2) — it can't create objects via actions. We can, and the audit's A3 forces us to mint a key explicitly.
4. **Relationships are links, never denormalized foreign values** (audit E). The escalation is *linked* to its circuit via `circuit_has_escalation`, not stored as a bare `circuit_id` string.

---

## The config

```yaml
# ── reusable value types (a base type + a CEL/JSON constraint) ──────────────────
value_types:
  sla_status:   { base: enum,    enum: [green, amber, red] }
  health:       { base: enum,    enum: [healthy, degraded, down] }
  esc_severity: { base: enum,    enum: [low, medium, high, critical] }   # mirrors OF AuditSeverity (VERIFIED)
  esc_status:   { base: enum,    enum: [open, ack, resolved, cancelled] }
  contract_status: { base: enum, enum: [draft, active, expiring, expired, renegotiating] }
  email:        { base: text,    regex: '^[^@]+@[^@]+$' }   # compiled to a SQL CHECK (Postgres ~), not runtime CEL
  money:        { base: decimal, min: 0 }                    # compiled to a SQL CHECK

# ── object types ───────────────────────────────────────────────────────────────
object_types:

  carrier:
    title: Carrier
    primary_key: carrier_id
    title_prop: name
    properties:
      carrier_id:      { type: text,  required: true }
      name:            { type: text,  required: true }
      account_manager: { type: text }                       # Bailey or a teammate's email
      sla_status:      { value_type: sla_status, hot: true } # promoted to a generated column
      annual_spend:    { value_type: money, hot: true }      # filter/sort -> generated column
      region:          { type: text, hot: true }             # drives a row policy (see roles)

  circuit:
    title: Circuit
    primary_key: circuit_id
    title_prop: circuit_id
    properties:
      circuit_id: { type: text, required: true }
      bandwidth:  { type: text }                              # e.g. "10G"
      health:     { value_type: health, hot: true }
      status:     { value_type: sla_status, hot: true }
      site_a:     { type: text }
      site_z:     { type: text }

  contract:
    title: Contract
    primary_key: contract_id
    title_prop: contract_id
    properties:
      contract_id:  { type: text, required: true }
      status:       { value_type: contract_status, hot: true }
      mrc:          { value_type: money }                     # monthly recurring charge
      renewal_date: { type: date, hot: true }                # filter/sort -> generated column
      auto_renew:   { type: boolean }

  sla:                                                        # the SLA terms attached to a contract/circuit
    title: SLA
    primary_key: sla_id
    title_prop: sla_id
    properties:
      sla_id:           { type: text, required: true }
      uptime_target:    { type: decimal }                    # e.g. 99.95
      mttr_hours:       { type: integer }
      credit_pct:       { type: decimal }                    # service-credit % on breach

  escalation:
    title: Escalation
    primary_key: escalation_id
    title_prop: escalation_id
    properties:
      escalation_id: { type: text, required: true }
      reason:        { type: text, required: true }
      severity:      { value_type: esc_severity, hot: true }
      status:        { value_type: esc_status, hot: true }
      opened_by:     { type: text }                           # server-derived actor
      opened_at:     { type: timestamp }

# ── link types (first-class; cardinality is actually enforced — see 02 §3) ────────
link_types:
  carrier_provides_circuit: { from: carrier,  to: circuit,     cardinality: one_to_many,  from_name: circuits,     to_name: carrier }
  carrier_holds_contract:   { from: carrier,  to: contract,    cardinality: one_to_many,  from_name: contracts,    to_name: carrier }
  contract_covers_circuit:  { from: contract, to: circuit,     cardinality: many_to_many, from_name: circuits,     to_name: contracts }
  contract_has_sla:         { from: contract, to: sla,         cardinality: one_to_many,  from_name: slas,         to_name: contract }
  circuit_has_escalation:   { from: circuit,  to: escalation,  cardinality: one_to_many,  from_name: escalations,  to_name: circuit }

# ── actions (the kinetic core; params + CEL criteria + rules) ─────────────────────
action_types:

  # 1) open an escalation on a degraded circuit  (THE flagship; the closed loop)
  # NB: unlike OpenFoundry (one `operation_kind` per action), our action's `rules` list declares
  # each edit (update + create + link), all applied in ONE transaction (D14). No single operation_kind.
  open_escalation:
    object_type: circuit                 # the action's primary object (for UI grouping), not an operation
    parameters:
      circuit:  { type: reference, object_type: circuit, required: true }
      reason:   { type: text, required: true }
      severity: { value_type: esc_severity, required: true }
    submission_criteria:                  # CEL; server-enforced; each returns valid | {error}
      - expr: "'carrier_manager' in actor.roles"
        error: "Only carrier managers may open escalations."
      - expr: "size(params.reason) > 0"
        error: "A reason is required."
      - expr: "circuit.status != 'red'"
        error: "Circuit already has an open escalation (status is red)."
    rules:
      - update: { object: $circuit, set: { status: red } }
      - create:
          object_type: escalation
          pkey: "'ESC-' + uuid()"          # PK mandatory (fixes A3); minted by the executor
          set:
            reason:    $params.reason
            severity:  $params.severity
            status:    open
            opened_by: $actor              # server-derived (B5), never client-supplied
            opened_at: now()
      - link: { link_type: circuit_has_escalation, from: $circuit, to: $created.escalation }

  # 2) flag a contract for renegotiation  (a renewal decision -> writeback)
  flag_for_renegotiation:
    object_type: contract
    parameters:
      contract: { type: reference, object_type: contract, required: true }
      note:     { type: text }
    submission_criteria:
      - expr: "'carrier_manager' in actor.roles"
        error: "Only carrier managers may flag contracts."
      - expr: "contract.status in ['active','expiring']"
        error: "Only active or expiring contracts can be flagged."
      # date math stays OUT of CEL: the executor binds a derived days_to_renewal (renewal_date − today)
      # into the eval context, so this is a plain comparison (engine-portable). [verified]
      - expr: "contract.days_to_renewal >= 0 && contract.days_to_renewal <= 90"
        error: "Renewal is more than 90 days out; not eligible yet."
    rules:
      - update: { object: $contract, set: { status: renegotiating } }

  # 3) record an SLA breach against a circuit  (operational fact capture)
  record_sla_breach:
    object_type: circuit
    parameters:
      circuit:      { type: reference, object_type: circuit, required: true }
      observed_uptime: { type: decimal, required: true }
    submission_criteria:
      - expr: "'carrier_manager' in actor.roles || 'noc_analyst' in actor.roles"
        error: "Only managers or NOC analysts may record breaches."
      - expr: "params.observed_uptime >= 0.0 && params.observed_uptime <= 100.0"
        error: "Observed uptime must be a percentage."
    rules:
      - update: { object: $circuit, set: { health: degraded } }
      # post-commit side effect via the outbox (NOT inline HTTP like OpenFoundry's InvokeWebhook):
    side_effects:
      - notify: { template: sla_breach, to: $circuit.carrier.account_manager }

# ── roles + row policies (RBAC + security-travels-with-reads) ─────────────────────
roles:
  carrier_manager: { operations: [object:read:*, action:open_escalation, action:flag_for_renegotiation, action:record_sla_breach] }
  noc_analyst:     { operations: [object:read:circuit, object:read:escalation, action:record_sla_breach] }
  viewer:          { operations: [object:read:*] }

object_policies:
  # a regional viewer only sees carriers in their region (compiled into the read WHERE; see 02 §6)
  carrier_by_region:
    object_type: carrier
    role: viewer
    predicate: "object.region == actor.attributes.region"
```

---

## How this maps to the engine (the standardize/adapt boundary holds)

| This config (adapt to Bailey) | Engine table it loads into (`02`, fixed) |
|---|---|
| `value_types`, `object_types`, `properties` | `value_type`, `object_type`, `property_def` (+ generated columns for `hot` props, + per-type `CHECK`) |
| `link_types` | `link_type` (+ a partial-unique index per `one_to_*`) |
| `action_types` (`parameters`/`submission_criteria`/`rules`) | `action_type.spec` JSONB; executed by the action executor |
| `roles`, `object_policies` | `role_def`, `object_policy` (predicate compiled into read `WHERE`) |

Nothing in the left column requires a change to the right column — the audit's leak test passes. Loading this file gives the PoC the five object types, their links, three governed/validated/audited actions, and role-scoped reads **with no engine code written** (the validation functions, if any criterion outgrows CEL, are the one exception — exactly as `D10/D12` resolved).

---

## What we deliberately did **not** copy from OpenFoundry's action model

- **`invoke_webhook` / `invoke_function` as inline synchronous HTTP** (`HttpInvocationConfig`, VERIFIED AC-3). OpenFoundry fires an operator-declared URL mid-handler with no durability and no coupling to the DB write's success — a foot-gun (an HTTP call succeeds while the DB write rolls back, or vice-versa). Our `side_effects` go through a **post-commit outbox** instead.
- **`confirmation_required` as the only safety rail.** OpenFoundry's `action_types.confirmation_required` is an "are-you-sure" flag; real safety is the server-side CEL criteria above, which it lacks.
