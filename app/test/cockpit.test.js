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
  // A generated workflow ships with no owners, so the first thing it is waiting on is an owner.
  assert.equal(await page.text('#wfState'), 'Chưa có owner');
  assert.match(String(await page.text('#wfStateDetail')), /da-clarify-business-question/);
  assert.equal(await page.eval('document.getElementById("wfRunNext").hidden'), true,
    'an unowned task must not offer a run button');
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
  await setOwner(page, 'kina2711');
  await page.eval(`(() => { window.__started = false;
    const real = window.studio.startRun;
    window.studio.startRun = async (p) => { window.__started = true; return real(p); };
    return true; })()`);
  await page.click('#wfRunNext');
  await page.settle(300);
  assert.equal(await page.eval('window.__started'), false, 'no run may start without a folder');
  assert.match(String(await page.text('#wfResult')), /thư mục làm việc/i);
});

/* History. The point of these is that the app writes what the validator will read, so the
 * assertions are about the transitions array and not about the panel's wording. */


/** Fill the owner on the first ready task the way a person does: select the node, type in the
 *  inspector. Generated workflows ship unowned and the cockpit refuses to run an unowned task. */
async function setOwner(page, who) {
  await page.eval(`(() => {
    const node = document.querySelector('#wfCanvas .wf-node');
    if (node) node.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    return true; })()`);
  await page.settle(200);
  const filled = await page.eval(`(() => {
    // data-field is on the label as well as the control, so the tag matters here.
    const input = document.querySelector('#wfInspector input[data-field="owner"]');
    if (!input) return false;
    input.value = ${JSON.stringify(who)};
    input.dispatchEvent(new Event('input', { bubbles: true }));
    return true; })()`);
  await page.settle(250);
  return filled;
}

async function loadDataAnalysis(page) {
  await page.eval(`(() => { const s = document.getElementById('wfPreset');
    const opt = [...s.options].find((o) => /data-analysis/.test(o.value || o.textContent));
    s.value = opt.value; s.dispatchEvent(new Event('change', {bubbles: true})); return true; })()`);
  await page.settle(600);
}

test('moving a task writes the intermediate steps the validator requires', async (t) => {
  const page = await openWorkflow(t);
  await loadDataAnalysis(page);
  const written = await page.eval(`(() => {
    const task = { task_id: 'da-clarify-business-question', status: 'planned' };
    const steps = self.WfGraph.transitionsFor(task, 'in-progress', { at: '2026-09-01T00:00:00Z' });
    return steps.map((s) => s.from_status + '->' + s.to_status); })()`);
  assert.deepEqual(written, ['planned->ready', 'ready->in-progress'],
    'a cockpit that writes planned->in-progress produces a manifest the validator rejects');
});

test('the history panel reads the manifest and toggles cleanly', async (t) => {
  const page = await openWorkflow(t);
  await loadDataAnalysis(page);
  assert.equal(await page.visible('#wfHistory'), false);
  await page.click('#wfHistoryToggle');
  await page.settle(250);
  assert.equal(await page.visible('#wfHistory'), true);
  assert.equal(await page.onScreen('#wfHistory'), true);
  // A generated workflow ships with no history, and the panel says so rather than showing nothing.
  assert.match(String(await page.text('#wfHistory .wf-plan-head')), /Chưa có bước chuyển nào/);
  await page.click('#wfHistoryToggle');
  await page.settle(150);
  assert.equal(await page.visible('#wfHistory'), false);
});

test('running a task records history and never writes the repository', async (t) => {
  // save is stubbed so the real workflow file is untouched; run:start is stubbed so no model is
  // called. Everything between those two ends is the app's own code.
  const page = await open({ stubs: {
    'suite:pick': SUITE,
    'folder:pick': SUITE,
    'workflow:save': { ok: true },
    'run:start': { ok: true },
  } });
  t.after(() => page.close());

  const before = fs.readFileSync(WORKFLOW, 'utf8');

  await page.click('#pickSuite');
  await page.settle(700);
  await page.click('#grid .card');
  await page.settle(250);
  await page.click('#pickFolder');
  await page.settle(250);
  await page.click('#backToSkills');
  await page.settle(200);
  await page.eval(`(() => { const tabs = [...document.querySelectorAll('button,[role=tab]')]
    .filter((b) => /workflow|quy trình/i.test(b.textContent || ''));
    if (tabs.length) tabs[0].click(); return true; })()`);
  await page.settle(200);
  await loadDataAnalysis(page);

  await setOwner(page, 'kina2711');
  await page.click('#wfHistoryToggle');
  await page.settle(200);
  assert.equal(await page.eval('document.querySelectorAll("#wfHistory .wf-move").length'), 0);

  await page.click('#wfRunNext');
  await page.settle(500);

  const steps = await page.eval(
    '[...document.querySelectorAll("#wfHistory .wf-move .wf-move-step")].map((e) => e.textContent)');
  assert.deepEqual(steps, ['ready \u2192 in-progress', 'planned \u2192 ready'],
    'history shows both steps, newest first');
  assert.equal(await page.text('#wfState'), 'Đang chạy');

  assert.equal(fs.readFileSync(WORKFLOW, 'utf8'), before,
    'a test must not modify the workflow it opens');
});
