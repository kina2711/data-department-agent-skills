'use strict';

/* Screens compared against stored baselines.
 *
 * These catch what a DOM assertion cannot: a rule that stopped applying, a panel that overlaps a
 * button, a grid that collapses to one column at a width nobody tried. The cost is that a
 * deliberate redesign fails every one of them, which is the intended cost — a visual change should
 * have to be looked at and accepted, and `npm run shots:accept` is how it is accepted.
 *
 * The window size is fixed here rather than inherited, because a baseline is only meaningful
 * against the geometry it was taken at. */

const { test } = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');
const { open, APP } = require('./helpers/page.js');

const SUITE = path.resolve(APP, '..');
const SHOTS = path.join(__dirname, '__shots__');
const ACCEPT = process.env.DA_ACCEPT_SHOTS === '1';

function verdict(name, result) {
  if (result.created) return `baseline created: ${name}`;
  if (result.sizeMismatch) {
    assert.fail(`${name}: baseline is ${result.baseline.width}x${result.baseline.height}, `
      + `capture is ${result.actual.width}x${result.actual.height}`);
  }
  assert.ok(result.ratio <= result.limit,
    `${name}: ${(result.ratio * 100).toFixed(3)}% of pixels differ, limit ${(result.limit * 100).toFixed(3)}%. `
    + `See ${name}.actual.png next to the baseline, or accept with DA_ACCEPT_SHOTS=1.`);
  return null;
}

async function check(page, name) {
  const baseline = path.join(SHOTS, `${name}.png`);
  if (ACCEPT && fs.existsSync(baseline)) fs.unlinkSync(baseline);
  const result = await page.compare(baseline);
  const note = verdict(name, result);
  if (note) console.log(`  ${note}`);
}

test('empty state, before any suite is connected', async (t) => {
  const page = await open();
  t.after(() => page.close());
  await page.resize(1280, 900);
  await page.settle(300);
  await check(page, 'empty');
});

test('the grid, a skill detail, and the workflow canvas', async (t) => {
  const page = await open({ stubs: { 'suite:pick': SUITE } });
  t.after(() => page.close());
  await page.resize(1280, 900);
  await page.click('#pickSuite');
  await page.settle(800);
  await check(page, 'grid');

  await page.click('#grid .card');
  await page.settle(400);
  await check(page, 'detail');
});

test('the workflow canvas and the dry-run plan', async (t) => {
  const page = await open({ stubs: { 'suite:pick': SUITE } });
  t.after(() => page.close());
  await page.resize(1280, 900);
  await page.click('#pickSuite');
  await page.settle(800);
  await page.eval(`(() => { const tabs = [...document.querySelectorAll('button,[role=tab]')]
    .filter((b) => /workflow|quy trình/i.test(b.textContent || ''));
    if (tabs.length) tabs[0].click(); })()`);
  await page.settle(250);
  await page.eval(`(() => { const s = document.getElementById('wfPreset');
    const opt = [...s.options].find((o) => /data-analysis/.test(o.value || o.textContent));
    s.value = opt.value; s.dispatchEvent(new Event('change', {bubbles: true})); })()`);
  await page.settle(700);
  await check(page, 'workflow');
  await page.eval(`(() => { document.getElementById('wfCockpit')
    .scrollIntoView({ block: 'center' }); return true; })()`);
  await page.settle(300);
  await check(page, 'cockpit');

  await page.click('#wfDryRun');
  await page.settle(400);
  await check(page, 'dry-run');
});

test('the grid holds together at a narrow width', async (t) => {
  const page = await open({ stubs: { 'suite:pick': SUITE } });
  t.after(() => page.close());
  await page.resize(820, 900);
  await page.click('#pickSuite');
  await page.settle(800);
  await check(page, 'grid-narrow');
});
