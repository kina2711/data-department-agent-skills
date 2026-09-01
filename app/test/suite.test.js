'use strict';

/* The suite reader, which parses the manifest with a hand-rolled reader rather than a YAML
 * dependency. Hand-rolled parsers fail quietly on shapes their author did not picture, so the
 * cases here are mostly shapes that are legal YAML and were never tried. */

const { test } = require('node:test');
const assert = require('node:assert/strict');
const { parseSuiteManifest } = require('../src/suite.js');

test('reads version and the role list', () => {
  const out = parseSuiteManifest([
    'version: "3.10.0"',
    'roles:',
    '  - skill: "data-analysis"',
    '    description: "Phân tích"',
    '  - skill: "data-engineering"',
    '    description: "Pipeline"',
  ].join('\n'));
  assert.equal(out.suiteVersion, '3.10.0');
  assert.deepEqual(out.roles.map((r) => r.skill), ['data-analysis', 'data-engineering']);
});

test('unquoted values are read the same as quoted ones', () => {
  const out = parseSuiteManifest('version: 3.10.0\nroles:\n  - skill: data-analysis\n');
  assert.equal(out.suiteVersion, '3.10.0');
  assert.deepEqual(out.roles.map((r) => r.skill), ['data-analysis']);
});

test('an empty manifest yields no roles rather than throwing', () => {
  const out = parseSuiteManifest('');
  assert.deepEqual(out.roles, []);
});

test('trailing whitespace does not create a role', () => {
  const out = parseSuiteManifest('roles:\n  - skill: "a"   \n\n   \n');
  assert.equal(out.roles.length, 1);
  assert.equal(out.roles[0].skill, 'a');
});

test('a comment line is not mistaken for a field', () => {
  const out = parseSuiteManifest('# version: 9.9.9\nversion: "1.0.0"\n');
  assert.equal(out.suiteVersion, '1.0.0');
});
