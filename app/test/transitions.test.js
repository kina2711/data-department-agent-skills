'use strict';

/* Status moves.
 *
 * The first test is the one that matters: it parses the table out of the suite's own validator and
 * asserts the copy in the app is identical. Two copies of a rule drift, and the way this one would
 * drift is silent — the app keeps writing manifests that were legal last month. */

const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const g = require('../src/lib/graph.js');
const { APP } = require('./helpers/page.js');

const VALIDATOR = path.join(APP, '..', 'skills', 'data-department-orchestrator',
  'scripts', 'validate_workflow.py');

function pythonTable() {
  const src = fs.readFileSync(VALIDATOR, 'utf8');
  const block = src.match(/ALLOWED_TASK_TRANSITIONS\s*=\s*\{([\s\S]*?)\n\}/);
  assert.ok(block, 'the validator still defines ALLOWED_TASK_TRANSITIONS');
  const table = {};
  for (const line of block[1].split('\n')) {
    const row = line.match(/^\s*"([a-z-]+)":\s*(?:\{([^}]*)\}|set\(\))/);
    if (!row) continue;
    table[row[1]] = (row[2] || '')
      .split(',')
      .map((s) => s.trim().replace(/^"|"$/g, ''))
      .filter(Boolean)
      .sort();
  }
  return table;
}

test('the app copy of the transition table matches the validator exactly', () => {
  const python = pythonTable();
  const js = Object.fromEntries(
    Object.entries(g.ALLOWED).map(([k, v]) => [k, [...v].sort()]));
  assert.deepEqual(js, python,
    'app/src/lib/graph.js ALLOWED has drifted from validate_workflow.py');
});

test('planned does not go straight to in-progress', () => {
  // The move a cockpit naively makes, and the reason this table is in the app at all.
  assert.ok(!g.ALLOWED.planned.includes('in-progress'));
  assert.deepEqual(g.statusPath('planned', 'in-progress'), ['ready', 'in-progress']);
});

test('a run start and a run finish are legal paths', () => {
  assert.deepEqual(g.statusPath('planned', 'implemented'), ['ready', 'in-progress', 'implemented']);
  assert.deepEqual(g.statusPath('in-progress', 'failed'), ['failed']);
  assert.deepEqual(g.statusPath('failed', 'ready'), ['ready']);
});

test('complete is terminal', () => {
  assert.deepEqual(g.ALLOWED.complete, []);
  assert.equal(g.statusPath('complete', 'ready'), null);
  assert.equal(g.statusPath('complete', 'failed'), null);
});

test('an unknown status has no path in either direction', () => {
  assert.equal(g.statusPath('planned', 'shipped'), null);
  assert.equal(g.statusPath('shipped', 'ready'), null);
});

test('a task already in the target status needs no transition', () => {
  assert.deepEqual(g.statusPath('ready', 'ready'), []);
  assert.deepEqual(g.transitionsFor({ task_id: 'a', status: 'ready' }, 'ready'), []);
});

test('transitions carry the intermediate steps, not just the destination', () => {
  const out = g.transitionsFor({ task_id: 'a', status: 'planned' }, 'implemented',
    { at: '2026-09-01T00:00:00Z' });
  assert.deepEqual(out.map((x) => `${x.from_status}->${x.to_status}`),
    ['planned->ready', 'ready->in-progress', 'in-progress->implemented']);
  assert.ok(out.every((x) => x.task_id === 'a'));
  assert.ok(out.every((x) => x.occurred_at === '2026-09-01T00:00:00Z'));
  assert.ok(out.every((x) => Array.isArray(x.evidence_refs)));
});

test('a move into a status that needs evidence is refused when none is given', () => {
  for (const target of ['tested', 'approved', 'released', 'complete']) {
    assert.equal(g.transitionsFor({ task_id: 'a', status: 'implemented' }, target), null,
      `${target} must not be reachable without evidence`);
  }
});

test('the same move is allowed once evidence is supplied', () => {
  const out = g.transitionsFor({ task_id: 'a', status: 'implemented' }, 'tested',
    { evidence: ['ev-1'] });
  assert.equal(out.length, 1);
  assert.deepEqual(out[0].evidence_refs, ['ev-1']);
});

test('an illegal move produces no transitions rather than a plausible one', () => {
  assert.equal(g.transitionsFor({ task_id: 'a', status: 'planned' }, 'nowhere'), null);
});

/* The closing check: feed what the app writes to the validator the suite ships, and see whether it
 * is accepted. Everything above tests the app against a copy of the rules; this tests it against
 * the rules themselves. */

const { spawnSync } = require('node:child_process');
const os = require('node:os');

const SUITE = path.join(APP, '..');

function validate(manifest, mode) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'wf-'));
  const file = path.join(dir, 'probe.workflow.json');
  fs.writeFileSync(file, JSON.stringify(manifest, null, 2) + '\n');
  const run = spawnSync('python3', [VALIDATOR, file, '--catalog',
    path.join(SUITE, 'task-catalog.json'), '--mode', mode || 'plan'], { encoding: 'utf8' });
  fs.rmSync(dir, { recursive: true, force: true });
  return { ok: run.status === 0, out: (run.stdout || '') + (run.stderr || '') };
}

function baseManifest(tasks, transitions) {
  return {
    workflow_id: 'probe', version: '1.0.0',
    objective: 'A manifest built the way the cockpit builds one, for the validator to judge.',
    status: 'draft', workflow_risk_tier: 'R0-light',
    current_task_id: tasks[0].task_id,
    tasks, transitions, claims: [], updated_at: '',
  };
}

test('what the cockpit writes for a run start is accepted by the validator', () => {
  const task = {
    task_id: 'da-clarify-business-question', owner: 'kina2711', depends_on: [], status: 'planned',
    risk_tier: 'R0-light', artifact_version: '', artifact_sha256: '',
    evidence_refs: [], approval_refs: [],
  };
  const steps = g.transitionsFor(task, 'in-progress', { at: '2026-09-01T00:00:00Z' });
  const moved = { ...task, status: 'in-progress' };
  const res = validate(baseManifest([moved], steps));
  assert.ok(res.ok, `validator rejected the cockpit's own output:\n${res.out}`);
});

test('the shortcut the cockpit must not take is rejected, which is why the path exists', () => {
  const task = {
    task_id: 'da-clarify-business-question', owner: 'kina2711', depends_on: [], status: 'in-progress',
    risk_tier: 'R0-light', artifact_version: '', artifact_sha256: '',
    evidence_refs: [], approval_refs: [],
  };
  const naive = [{
    task_id: task.task_id, from_status: 'planned', to_status: 'in-progress',
    occurred_at: '2026-09-01T00:00:00Z', evidence_refs: [],
  }];
  const res = validate(baseManifest([task], naive));
  assert.equal(res.ok, false, 'planned -> in-progress should not have been accepted');
  assert.match(res.out, /illegal transition/);
});

test('a completed run is accepted with its full history', () => {
  const task = {
    task_id: 'da-clarify-business-question', owner: 'kina2711', depends_on: [], status: 'implemented',
    risk_tier: 'R0-light', artifact_version: '', artifact_sha256: '',
    evidence_refs: [], approval_refs: [],
  };
  const steps = g.transitionsFor({ ...task, status: 'planned' }, 'implemented',
    { at: '2026-09-01T00:00:00Z' });
  const res = validate(baseManifest([task], steps));
  assert.ok(res.ok, `validator rejected a finished run:\n${res.out}`);
});
