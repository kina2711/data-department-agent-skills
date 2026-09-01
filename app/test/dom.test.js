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
