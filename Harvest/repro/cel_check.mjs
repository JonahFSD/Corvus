// Verifies the CEL submission-criteria that 01_WEDGE_ONTOLOGY_CONFIG actually ships.
// Engine: @marcbachmann/cel-js (full-spec: exists, comparisons, in, value.matches()).
// The simple `cel-js` is a lighter subset (no matches()); we pin the full-spec engine.
// EXITS NONZERO on any wrong result or evaluation error, so the [verified] mark is real.
import * as cel from '@marcbachmann/cel-js';

let fails = 0;
const check = (label, expr, ctx, expected) => {
  let got;
  try { got = cel.evaluate(expr, ctx); }
  catch (e) { got = 'ERR:' + (e.message || e); }
  const pass = got === expected;
  if (!pass) fails++;
  console.log(`  ${pass ? 'PASS' : 'FAIL'}  ${String(got).padEnd(6)} (want ${expected})  ${label}: ${expr}`);
};

const mgr    = { actor: { roles: ['carrier_manager'] } };
const noc    = { actor: { roles: ['noc_analyst'] } };
const viewer = { actor: { roles: ['viewer'] } };

console.log('open_escalation:');
check('manager may escalate', "'carrier_manager' in actor.roles", mgr, true);
check('viewer may not',       "'carrier_manager' in actor.roles", viewer, false);
check('reason present',        'size(params.reason) > 0', { params: { reason: 'SLA breached 3x' } }, true);
check('reason empty rejected', 'size(params.reason) > 0', { params: { reason: '' } }, false);
check('not already escalated', "circuit.status != 'red'", { circuit: { status: 'amber' } }, true);
check('already red rejected',  "circuit.status != 'red'", { circuit: { status: 'red' } }, false);

console.log('flag_for_renegotiation:');
check('manager may flag',      "'carrier_manager' in actor.roles", mgr, true);
check('active/expiring ok',    "contract.status in ['active','expiring']", { contract: { status: 'active' } }, true);
check('expired rejected',      "contract.status in ['active','expiring']", { contract: { status: 'expired' } }, false);
// date math is done server-side: the executor supplies a derived days_to_renewal, CEL does a plain compare
check('within 90 days',        'contract.days_to_renewal >= 0 && contract.days_to_renewal <= 90', { contract: { days_to_renewal: 30 } }, true);
check('too far out rejected',  'contract.days_to_renewal >= 0 && contract.days_to_renewal <= 90', { contract: { days_to_renewal: 200 } }, false);

console.log('record_sla_breach:');
check('manager or noc may',    "'carrier_manager' in actor.roles || 'noc_analyst' in actor.roles", noc, true);
check('viewer may not',        "'carrier_manager' in actor.roles || 'noc_analyst' in actor.roles", viewer, false);
check('uptime in range',       'params.observed_uptime >= 0.0 && params.observed_uptime <= 100.0', { params: { observed_uptime: 99.9 } }, true);
check('uptime out of range',   'params.observed_uptime >= 0.0 && params.observed_uptime <= 100.0', { params: { observed_uptime: 150.0 } }, false);

console.log('row policy (compiled into WHERE, but the predicate is CEL):');
check('region match',          'object.region == actor.attributes.region', { object: { region: 'west' }, actor: { attributes: { region: 'west' } } }, true);
check('region mismatch',       'object.region == actor.attributes.region', { object: { region: 'east' }, actor: { attributes: { region: 'west' } } }, false);

console.log(`\n${fails === 0 ? 'ALL CEL CRITERIA VERIFIED on @marcbachmann/cel-js' : fails + ' CEL CHECK(S) FAILED'}`);
console.log('NOTE: value-type constraints (email regex, money min) are NOT runtime CEL — they compile to SQL CHECK (see 02 §3).');
process.exit(fails === 0 ? 0 : 1);
