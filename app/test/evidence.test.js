'use strict';

/* The evidence a run can honestly produce, and the fields it must leave alone.
 *
 * The last test is the one that matters: the drafted envelope is fed to the schema the suite
 * ships, so what the app writes is judged by the contract rather than by my reading of it. */

const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const g = require('../src/lib/graph.js');
const { APP } = require('./helpers/page.js');

const SCHEMA = JSON.parse(fs.readFileSync(
  path.join(APP, '..', 'schemas', 'evidence-envelope.schema.json'), 'utf8'));

const RUN = {
  exit: 0, at: '2026-09-04T10:00:00.000Z', folder: '/work',
  permissionMode: 'plan', command: 'claude -p "..."', durationMs: 8421, actor: '',
};

test('a passing run drafts a passed envelope, a failing run a failed one', () => {
  assert.equal(g.draftEvidence({ task_id: 'a' }, RUN).status, 'passed');
  assert.equal(g.draftEvidence({ task_id: 'a' }, { ...RUN, exit: 1 }).status, 'failed');
  assert.equal(g.draftEvidence({ task_id: 'a' }, { ...RUN, exit: 137 }).status, 'failed');
});

test('the exit status is carried, and is null when there was not one', () => {
  assert.equal(g.draftEvidence({ task_id: 'a' }, RUN).exit_status, 0);
  assert.equal(g.draftEvidence({ task_id: 'a' }, { ...RUN, exit: undefined }).exit_status, null);
});

test('the app never invents an artifact, a version or a hash', () => {
  const env = g.draftEvidence({ task_id: 'a' }, RUN);
  assert.equal(env.artifact, '');
  assert.equal(env.artifact_version, '');
  assert.equal(env.artifact_sha256, '');
});

test('the gaps are reported rather than left for a reader to notice', () => {
  const env = g.draftEvidence({ task_id: 'a' }, RUN);
  assert.deepEqual(g.evidenceGaps(env),
    ['artifact', 'artifact_version', 'artifact_sha256', 'expected_result', 'captured_by']);
  const filled = { ...env, artifact: 'report.md', artifact_version: '1.0.0',
    artifact_sha256: 'abc', expected_result: 'x', captured_by: 'kina2711' };
  assert.deepEqual(g.evidenceGaps(filled), []);
});

test('limitations state what the app did not check, in words', () => {
  const env = g.draftEvidence({ task_id: 'a' }, RUN);
  assert.ok(env.limitations.length >= 3);
  assert.ok(env.limitations.some((l) => /không kiểm tra kết quả có đúng không/.test(l)),
    'the envelope must say it did not judge correctness');
});

test('the evidence id is stable for the same task and moment', () => {
  const a = g.draftEvidence({ task_id: 'da-clarify-business-question' }, RUN);
  const b = g.draftEvidence({ task_id: 'da-clarify-business-question' }, RUN);
  assert.equal(a.evidence_id, b.evidence_id);
  const other = g.draftEvidence({ task_id: 'da-segment-entities' }, RUN);
  assert.notEqual(a.evidence_id, other.evidence_id);
});

/* A small checker rather than a JSON Schema dependency: required keys present, no key the schema
 * forbids, and the enums honoured. That is the part of the contract this draft can violate. */
function checkAgainstSchema(env) {
  const problems = [];
  for (const key of SCHEMA.required) {
    if (!(key in env)) problems.push(`missing required ${key}`);
  }
  if (SCHEMA.additionalProperties === false) {
    for (const key of Object.keys(env)) {
      if (!(key in SCHEMA.properties)) problems.push(`property not in schema: ${key}`);
    }
  }
  for (const [key, spec] of Object.entries(SCHEMA.properties)) {
    if (!(key in env)) continue;
    if (spec.enum && !spec.enum.includes(env[key])) problems.push(`${key} not in enum: ${env[key]}`);
    if (spec.minItems && Array.isArray(env[key]) && env[key].length < spec.minItems) {
      problems.push(`${key} needs at least ${spec.minItems} items`);
    }
  }
  return problems;
}

test('the drafted envelope satisfies the shape the suite schema requires', () => {
  for (const exit of [0, 1]) {
    const env = g.draftEvidence({ task_id: 'da-clarify-business-question' }, { ...RUN, exit });
    assert.deepEqual(checkAgainstSchema(env), [], `exit ${exit} produced a shape the schema rejects`);
  }
});

test('the checker itself rejects a broken envelope, so a pass means something', () => {
  const env = g.draftEvidence({ task_id: 'a' }, RUN);
  assert.notDeepEqual(checkAgainstSchema({ ...env, status: 'probably-fine' }), []);
  assert.notDeepEqual(checkAgainstSchema({ ...env, extra_field: 1 }), []);
  assert.notDeepEqual(checkAgainstSchema({ ...env, claim_ids: [] }), []);
  const { task_id, ...without } = env;
  assert.notDeepEqual(checkAgainstSchema(without), []);
});

/* Model choice follows the tier the suite already declared, and the envelope records it because
 * model-selection.md says a judgment whose model nobody wrote down has no answer six months on. */

test('each declared tier maps to a model, and an undeclared one maps to nothing', () => {
  assert.equal(g.modelForTier('light'), 'claude-haiku-4-5-20251001');
  assert.equal(g.modelForTier('standard'), 'claude-sonnet-5');
  assert.equal(g.modelForTier('strong'), 'claude-opus-5');
  for (const absent of ['', '  ', undefined, null, 'medium', 'STRONG']) {
    assert.equal(g.modelForTier(absent), '',
      `${JSON.stringify(absent)} must fall through to the CLI default rather than be guessed`);
  }
});

test('the three tiers map to three different models', () => {
  const chosen = ['light', 'standard', 'strong'].map(g.modelForTier);
  assert.equal(new Set(chosen).size, 3, 'a mapping that collapses tiers saves nothing');
});

test('the envelope records the model and the tier it came from', () => {
  const env = g.draftEvidence({ task_id: 'a' },
    { ...RUN, model: 'claude-haiku-4-5-20251001', modelTier: 'light' });
  assert.equal(env.environment.model, 'claude-haiku-4-5-20251001');
  assert.equal(env.environment.model_tier, 'light');
});

test('an unrecorded model is empty rather than assumed', () => {
  const env = g.draftEvidence({ task_id: 'a' }, RUN);
  assert.equal(env.environment.model, '');
  assert.equal(env.environment.model_tier, '');
});

test('the envelope with a model still satisfies the suite schema', () => {
  const env = g.draftEvidence({ task_id: 'a' },
    { ...RUN, model: 'claude-opus-5', modelTier: 'strong' });
  assert.deepEqual(checkAgainstSchema(env), []);
});
