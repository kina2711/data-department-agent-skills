'use strict';

/* Running two skills at once, without losing the single owner.
 *
 * The suite's discipline is that one deliverable has one accountable owner. "Use both skills" with
 * nothing else said produces two agents each assuming the other handled the gate, which is the
 * failure this feature would introduce if it just concatenated two ids. These cover that the pair
 * always names a primary, that the suite's own confusion boundaries are surfaced rather than
 * quietly crossed, and that a pair never survives into a skill nobody paired. */

const { test } = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');
const os = require('node:os');
const { open, APP } = require('./helpers/page.js');

const SUITE = path.resolve(APP, '..');

async function detail(t, pick = /Data Analysis/i) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'pair-'));
  const page = await open({
    sessionsPath: path.join(dir, 's.json'),
    userData: fs.mkdtempSync(path.join(dir, 'p-')),
    stubs: { 'suite:pick': SUITE, 'folder:pick': SUITE, 'run:start': { ok: true } },
  });
  t.after(async () => { await page.close(); fs.rmSync(dir, { recursive: true, force: true }); });
  await page.click('#pickSuite');
  await page.settle(900);
  const opened = await page.eval(`(() => {
    const c = [...document.querySelectorAll('#grid .card')].find(x => ${pick}.test(x.textContent));
    if (!c) return false; c.click(); return true; })()`);
  assert.equal(opened, true, 'the skill to pair from must be on the grid');
  await page.settle(400);
  return page;
}

async function pairWith(page, id) {
  await page.eval(`(() => { const s = document.getElementById('pairPick');
    s.value = ${JSON.stringify(id)};
    s.dispatchEvent(new Event('change', { bubbles: true })); return s.value; })()`);
  await page.settle(250);
}

test('no pair is set until one is chosen', async (t) => {
  const page = await detail(t);
  assert.equal(await page.eval('document.getElementById("pairBar").hidden'), true);
  assert.equal(await page.onScreen('#pairBar'), false,
    'the bar must be off the screen, not merely marked hidden');
});

test('the picker never offers the skill already open', async (t) => {
  const page = await detail(t);
  const offered = await page.eval(
    `[...document.querySelectorAll('#pairPick option')].map(o => o.value).filter(Boolean)`);
  assert.ok(offered.length > 25, 'every other skill should be offerable');
  assert.equal(offered.includes('data-analysis'), false,
    'pairing a skill with itself is not a pair');
});

test('a pair names which skill owns the deliverable', async (t) => {
  const page = await detail(t);
  await pairWith(page, 'data-engineering');
  assert.equal(await page.eval('document.getElementById("pairBar").hidden'), false);
  const prompt = String(await page.text('#promptText'));
  assert.match(prompt, /data-analysis là skill chính/, 'the open skill stays primary');
  assert.match(prompt, /data-engineering là skill phụ/, 'the added skill is secondary');
  assert.match(prompt, /deliverable, gate và approval/,
    'the prompt must say what the primary owns, or a pair has two owners and no accountability');
});

test('the prompt tells the agent to collapse the pair when only one skill owns the work', async (t) => {
  const page = await detail(t);
  await pairWith(page, 'data-engineering');
  assert.match(String(await page.text('#promptText')), /thuộc hẳn về một trong hai/,
    'a pair that turns out to be one role must be reported, not split down the middle');
});

test('a boundary the suite already settled is surfaced, not crossed silently', async (t) => {
  // analytics-engineering ~ data-engineering is pinned by a confusion-pair case.
  const page = await detail(t, /Analytics Engineering/i);
  await pairWith(page, 'data-engineering');
  const note = String(await page.text('#pairNote'));
  assert.match(note, /ranh giới đã được chốt bằng test/,
    'pairing across a settled boundary must say so');
  assert.equal(await page.eval(
    'document.getElementById("pairNote").classList.contains("is-warn")'), true);
});

test('a pair with no settled boundary is not warned about', async (t) => {
  const page = await detail(t);
  await pairWith(page, 'data-technical-content-and-social');
  assert.equal(await page.eval(
    'document.getElementById("pairNote").classList.contains("is-warn")'), false,
    'warning on every pair teaches people to ignore the warning');
});

test('clearing the pair removes it from the prompt', async (t) => {
  const page = await detail(t);
  await pairWith(page, 'data-engineering');
  await page.click('#pairClear');
  await page.settle(250);
  assert.equal(await page.eval('document.getElementById("pairBar").hidden'), true);
  assert.doesNotMatch(String(await page.text('#promptText')), /skill phụ/);
});

test('the pair does not follow you to the next skill', async (t) => {
  const page = await detail(t);
  await pairWith(page, 'data-engineering');
  await page.click('#backToSkills');
  await page.settle(300);
  await page.eval(`(() => {
    [...document.querySelectorAll('#grid .card')].find(x => /Data Engineering/i.test(x.textContent)).click();
    return true; })()`);
  await page.settle(400);
  assert.equal(await page.eval('document.getElementById("pairBar").hidden'), true,
    'a pair carried across skills pairs something nobody chose');
  assert.doesNotMatch(String(await page.text('#promptText')), /skill phụ/);
});

test('a pair rides along with a preset job rather than replacing it', async (t) => {
  const page = await detail(t);
  await page.eval(`(() => { const j = document.querySelector('#dJobs .job-card');
    if (j) j.click(); return !!j; })()`);
  await page.settle(400);
  await pairWith(page, 'data-engineering');
  const prompt = String(await page.text('#promptText'));
  assert.match(prompt, /skill phụ/, 'the pair clause must survive a job selection');
  assert.ok(prompt.length > 120, 'the job prompt itself must still be there');
});
