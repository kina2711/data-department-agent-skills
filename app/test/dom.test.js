'use strict';

/* The app driven the way a person drives it, against the real suite in this repository rather
 * than a fixture. A fixture would test the reader against data written to satisfy the reader. */

const { test } = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const { open, APP } = require('./helpers/page.js');

const SUITE = path.resolve(APP, '..');

async function withSuite(t) {
  const page = await open({ stubs: { 'suite:pick': SUITE } });
  t.after(() => page.close());
  await page.click('#pickSuite');
  await page.settle(700);
  return page;
}

test('picking a suite fills the grid from the real manifest', async (t) => {
  const page = await withSuite(t);
  const cards = await page.eval('document.querySelectorAll("#grid .card").length');
  assert.ok(cards >= 30, `expected the 33 skills of this suite, saw ${cards}`);
  assert.equal(await page.eval('!!document.querySelector("#grid .empty")'), false);
});

test('search narrows the grid and an impossible term empties it with a message', async (t) => {
  const page = await withSuite(t);
  const all = await page.eval('document.querySelectorAll("#grid .card").length');

  await page.eval(`(() => { const s = document.getElementById('search');
    s.value = 'mlops'; s.dispatchEvent(new Event('input', {bubbles: true})); })()`);
  await page.settle(150);
  const some = await page.eval('document.querySelectorAll("#grid .card").length');
  assert.ok(some > 0 && some < all, `expected a narrowed grid, got ${some} of ${all}`);

  await page.eval(`(() => { const s = document.getElementById('search');
    s.value = 'zzzz-khong-co-gi'; s.dispatchEvent(new Event('input', {bubbles: true})); })()`);
  await page.settle(150);
  assert.equal(await page.eval('document.querySelectorAll("#grid .card").length'), 0);
  assert.match(String(await page.text('#grid .empty')), /Không có skill nào khớp/);
});

test('the tier filter is exclusive and returns to all', async (t) => {
  const page = await withSuite(t);
  const all = await page.eval('document.querySelectorAll("#grid .card").length');
  await page.click('#tierFilter button[data-tier="light"]');
  await page.settle(150);
  const light = await page.eval('document.querySelectorAll("#grid .card").length');
  assert.ok(light > 0 && light < all);
  assert.equal(await page.eval(
    'document.querySelector(\'#tierFilter button[data-tier="light"]\').getAttribute("aria-pressed")'), 'true');
  await page.click('#tierFilter button[data-tier=""]');
  await page.settle(150);
  assert.equal(await page.eval('document.querySelectorAll("#grid .card").length'), all);
});

test('a skill opens full window and the back button returns to the grid', async (t) => {
  const page = await withSuite(t);
  await page.click('#grid .card');
  await page.settle(250);
  assert.equal(await page.visible('#viewDetail'), true);
  assert.equal(await page.visible('#viewSkills'), false);
  // The toolbar belongs to the grid; leaving it visible was the bug this pins.
  assert.equal(await page.eval('document.querySelector(".toolbar").hidden'), true);

  await page.click('#backToSkills');
  await page.settle(200);
  assert.equal(await page.visible('#viewSkills'), true);
  assert.equal(await page.visible('#viewDetail'), false);
  assert.equal(await page.eval('document.querySelector(".toolbar").hidden'), false);
});

test('the atlas button says what is wrong instead of doing nothing', async (t) => {
  const page = await open();           // no suite connected
  t.after(() => page.close());
  assert.equal(await page.visible('#status'), false);
  await page.click('#openAtlas');
  await page.settle(150);
  assert.equal(await page.visible('#status'), true);
  assert.match(String(await page.text('#status')), /Chọn thư mục suite/);
});

test('no console errors while loading a suite and opening a skill', async (t) => {
  const page = await open({ stubs: { 'suite:pick': SUITE } });
  t.after(() => page.close());
  await page.eval(`(() => { window.__errs = [];
    window.addEventListener('error', (e) => window.__errs.push(String(e.message)));
    const real = console.error;
    console.error = (...a) => { window.__errs.push(a.map(String).join(' ')); real(...a); }; })()`);
  await page.click('#pickSuite');
  await page.settle(700);
  await page.click('#grid .card');
  await page.settle(250);
  const errs = await page.eval('window.__errs');
  assert.deepEqual(errs, [], `renderer reported: ${JSON.stringify(errs)}`);
});

/* Vietnamese first, and a walkthrough that names real tasks.
 *
 * The English frontmatter description is written to make a router choose correctly; showing it to
 * a person as the primary text was the complaint these cover. */

test('every card carries the Vietnamese summary, not the English description', async (t) => {
  const page = await withSuite(t);
  const total = await page.eval('document.querySelectorAll("#grid .card").length');
  const withGist = await page.eval(
    '[...document.querySelectorAll("#grid .card-gist")].filter(e => e.textContent.trim()).length');
  assert.equal(withGist, total, 'a card without Vietnamese falls back to nothing, not to English');
  const anyEnglish = await page.eval(
    '[...document.querySelectorAll("#grid .card-gist")].some(e => /\\bUse for\\b|\\bUse when\\b/.test(e.textContent))');
  assert.equal(anyEnglish, false, 'router prose must not reach the card');
});

test('the detail view leads in Vietnamese and hides the English original behind a control', async (t) => {
  const page = await withSuite(t);
  await page.click('#grid .card');
  await page.settle(400);
  assert.equal(await page.eval('!!document.querySelector("#dGuide .lead")'), true);
  const englishVisible = await page.eval(`(() => {
    const el = document.querySelector('#dGuide .desc-en');
    return !!el && !el.hidden; })()`);
  assert.equal(englishVisible, false, 'the English description starts hidden');
  assert.match(String(await page.text('.guide-toggle')), /tiếng Anh/);
});

test('the walkthrough sits in the wide column and every row names a real task', async (t) => {
  const page = await withSuite(t);
  await page.click('#grid .card');
  await page.settle(400);

  const steps = await page.eval('document.querySelectorAll("#dWalkthrough .wt-step").length');
  assert.equal(steps, 4, 'four beats: bắt đầu, làm tiếp, cổng chặn, xong khi');

  // In the sidebar the rows collapsed to one word per line; the column has to be wide enough.
  const width = await page.eval(
    'Math.round(document.getElementById("dWalkthrough").getBoundingClientRect().width)');
  assert.ok(width > 700, `the walkthrough needs the wide column, got ${width}px`);

  const ids = await page.eval(
    '[...document.querySelectorAll("#dWalkthrough .wt-task code")].map(e => e.textContent)');
  assert.ok(ids.length >= 4, 'the walkthrough lists tasks');
  const known = await page.eval(`(() => {
    const ids = [...document.querySelectorAll('#dWalkthrough .wt-task code')].map(e => e.textContent);
    return ids.every(id => /^[a-z0-9-]+$/.test(id)); })()`);
  assert.equal(known, true, 'every row is a task id, not prose');
});

test('clicking a walkthrough row selects that task rather than explaining it', async (t) => {
  const page = await withSuite(t);
  await page.click('#grid .card');
  await page.settle(400);
  const first = await page.eval(
    'document.querySelector("#dWalkthrough .wt-task code").textContent');
  await page.click('#dWalkthrough .wt-task');
  await page.settle(300);
  // The task list marks its choice with aria-selected, which is also what the CSS keys on. The id
  // and the goal run together in textContent with no separator, so match the prefix rather than
  // splitting on whitespace that is not there.
  const selected = await page.eval(`(() => {
    const el = document.querySelector('#dTasks [aria-selected="true"]');
    return el ? (el.textContent || '').trim() : null; })()`);
  assert.ok(selected && selected.startsWith(first),
    `expected the selected row to be ${first}, saw ${JSON.stringify(String(selected).slice(0, 60))}`);
  const howMany = await page.eval('document.querySelectorAll(\'#dTasks [aria-selected="true"]\').length');
  assert.equal(howMany, 1, 'exactly one task is selected');
});
