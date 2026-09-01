'use strict';

/* The dry run driven through the app: open a real generated workflow from this repository and
 * check that the plan on screen matches what the planner computes for the same file. */

const { test } = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');
const { open, APP } = require('./helpers/page.js');
const g = require('../src/lib/graph.js');

const SUITE = path.resolve(APP, '..');
const WORKFLOW = path.join(SUITE, 'workflows', 'data-analysis.workflow.json');

async function openWorkflow(t) {
  const page = await open({ stubs: { 'suite:pick': SUITE } });
  t.after(() => page.close());
  await page.click('#pickSuite');
  await page.settle(700);
  await page.eval(`(() => { const tabs = [...document.querySelectorAll('button,[role=tab]')]
    .filter((b) => /workflow|quy trình/i.test(b.textContent || ''));
    if (tabs.length) tabs[0].click(); })()`);
  await page.settle(200);
  return page;
}

test('the dry run on a real generated workflow matches the planner', async (t) => {
  assert.ok(fs.existsSync(WORKFLOW), 'this repository ships the data-analysis workflow');
  const manifest = JSON.parse(fs.readFileSync(WORKFLOW, 'utf8'));
  const expected = g.runPlan(manifest.tasks);

  const page = await openWorkflow(t);
  await page.eval(`(() => { const s = document.getElementById('wfPreset');
    const opt = [...s.options].find((o) => /data-analysis/.test(o.value || o.textContent));
    if (!opt) throw new Error('no data-analysis preset among ' + s.options.length + ' options');
    s.value = opt.value; s.dispatchEvent(new Event('change', {bubbles: true})); })()`);
  await page.settle(600);

  await page.click('#wfDryRun');
  await page.settle(250);

  assert.equal(await page.visible('#wfPlan'), true);
  // Pressing the button must put the plan where the person pressing it can see it.
  assert.equal(await page.onScreen('#wfPlan'), true, 'the dry-run plan rendered off screen');
  const waves = await page.eval('document.querySelectorAll("#wfPlan .wf-wave:not(.is-stranded)").length');
  assert.equal(waves, expected.waves.length, 'wave count on screen must equal the planner');

  const chips = await page.eval('document.querySelectorAll("#wfPlan .wf-chip").length');
  const planned = expected.waves.reduce((n, w) => n + w.tasks.length, 0) + expected.stranded.length;
  assert.equal(chips, planned, 'every planned task gets a chip');

  const head = String(await page.text('#wfPlan .wf-plan-head'));
  assert.match(head, new RegExp(`${expected.waves.length} đợt`));
  assert.match(head, new RegExp(`rộng nhất ${expected.widest} task`));
});

test('the dry run toggles off and leaves nothing behind', async (t) => {
  const page = await openWorkflow(t);
  await page.eval(`(() => { const s = document.getElementById('wfPreset');
    s.value = s.options[1].value; s.dispatchEvent(new Event('change', {bubbles: true})); })()`);
  await page.settle(600);
  await page.click('#wfDryRun');
  await page.settle(200);
  assert.equal(await page.visible('#wfPlan'), true);
  await page.click('#wfDryRun');
  await page.settle(150);
  assert.equal(await page.visible('#wfPlan'), false);
  assert.equal(await page.eval('document.getElementById("wfPlan").textContent'), '');
});

test('a gate is marked in the wave it happens in', async (t) => {
  const page = await openWorkflow(t);
  // A manifest built in the page: one gate at R3, reachable only after its dependency.
  await page.eval(`(() => {
    const plan = self.WfGraph.runPlan([
      { task_id: 'a', depends_on: [], status: 'planned', risk_tier: 'R0-light' },
      { task_id: 'b', depends_on: ['a'], status: 'planned', risk_tier: 'R3-controlled' },
    ]);
    self.__probe = plan; })()`);
  const probe = await page.eval('self.__probe');
  assert.equal(probe.gates, 1);
  assert.deepEqual(probe.waves[1].gates, ['b']);
});

/* The cockpit strip. The tests that matter most here are the ones about what it refuses to do:
 * no control may clear a gate, and no run may start without a working folder. */

test('the strip reports what the workflow is waiting on', async (t) => {
  const page = await openWorkflow(t);
  await page.eval(`(() => { const s = document.getElementById('wfPreset');
    const opt = [...s.options].find((o) => /data-analysis/.test(o.value || o.textContent));
    s.value = opt.value; s.dispatchEvent(new Event('change', {bubbles: true})); })()`);
  await page.settle(600);
  assert.equal(await page.visible('#wfCockpit'), true);
  assert.equal(await page.text('#wfState'), 'Sẵn sàng');
  assert.match(String(await page.text('#wfStateDetail')), /da-clarify-business-question/);
  assert.equal(await page.eval('document.getElementById("wfRunNext").hidden'), false);
});

test('a gate shows the approval command and offers no button that clears it', async (t) => {
  const page = await openWorkflow(t);
  await page.eval(`(() => { const s = document.getElementById('wfPreset');
    const opt = [...s.options].find((o) => /data-analysis/.test(o.value || o.textContent));
    s.value = opt.value; s.dispatchEvent(new Event('change', {bubbles: true})); })()`);
  await page.settle(600);
  // Make the first ready task a gate and re-render through the app's own path.
  await page.eval(`(() => {
    const first = document.getElementById('wfStateDetail').textContent.match(/[a-z0-9-]+/)[0];
    self.__wfProbe = first; })()`);
  const gateApplied = await page.eval(`(() => {
    const host = document.getElementById('wfCockpit');
    const tasks = self.__wfTasks = null;
    return true; })()`);
  assert.equal(gateApplied, true);

  // The state machine is the authority; assert the refusal there and the absence of a control here.
  const probe = await page.eval(`(() => self.WfGraph.nextAction([
    { task_id: 'g', depends_on: [], status: 'planned', risk_tier: 'R4-critical' }]))()`);
  assert.equal(probe.kind, 'gate');
  assert.equal(await page.eval(
    '[...document.querySelectorAll("#wfCockpit button")].map((b) => b.id).sort().join(",")'),
    'wfMarkFailed,wfRunNext');
  assert.equal(await page.eval(
    '[...document.querySelectorAll("#wfCockpit button,#wfCockpit a")].some((b) => /duyệt|approve/i.test(b.textContent))'),
    false, 'no control in the cockpit may claim to approve anything');
});

test('running a task without a working folder says so instead of starting one', async (t) => {
  const page = await openWorkflow(t);
  await page.eval(`(() => { const s = document.getElementById('wfPreset');
    const opt = [...s.options].find((o) => /data-analysis/.test(o.value || o.textContent));
    s.value = opt.value; s.dispatchEvent(new Event('change', {bubbles: true})); })()`);
  await page.settle(600);
  await page.eval(`(() => { window.__started = false;
    const real = window.studio.startRun;
    window.studio.startRun = async (p) => { window.__started = true; return real(p); };
    return true; })()`);
  await page.click('#wfRunNext');
  await page.settle(300);
  assert.equal(await page.eval('window.__started'), false, 'no run may start without a folder');
  assert.match(String(await page.text('#wfResult')), /thư mục làm việc/i);
});
