# Reproduction artifacts

Proof, not assertion. Both scripts were run on this machine (Node 25; PGlite = PostgreSQL 18 in WASM; `@marcbachmann/cel-js`).

```
npm install                   # @electric-sql/pglite, cel-js, @marcbachmann/cel-js
node wedge_schema_repro.mjs   # 02_WEDGE_DB_SCHEMA: runs clean + fixes 8 reproduced audit
                              #   defects (A1,A2,A3,A4,A5,A6,C3,B3) + B2/B6 resolutions
node cel_check.mjs            # 01 criteria: 17 CEL assertions (full-spec engine); exits nonzero on any miss
```

- `wedge_schema_repro.mjs` builds the wedge schema verbatim on real Postgres 18 and asserts each fix the
  audit (`SPEC_Foundry-Clone_Spec-Audit.md` L36–48) reproduced against the blueprint's §4 — plus the B2
  (two-layer merge) and B6 (compiled read WHERE) design resolutions. Last run: **ALL CHECKS PASSED** (exit 0).
- `cel_check.mjs` evaluates every submission criterion / row policy that `01` actually ships, on the
  macro-complete `@marcbachmann/cel-js`, and **exits nonzero on any wrong result or error** (so the
  `[verified]` mark is real). Last run: **ALL CEL CRITERIA VERIFIED** (exit 0). The simpler `cel-js` is a
  lighter subset (no `matches()`); value-type regex/range constraints are SQL `CHECK`, not runtime CEL.
