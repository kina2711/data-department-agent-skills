'use strict';

/* Pan and zoom on the workflow canvas.
 *
 * All of it rides on the SVG viewBox, because the page CSP forbids inline styles and a viewBox is
 * an attribute. That choice also keeps hit-testing honest — a CSS transform on a wrapper moves the
 * picture and leaves the click targets where they were.
 *
 * The cases worth having are the ones where it looks like it works and does not: a zoom that
 * drifts the graph off screen, a drag that swallows the click which selects a node, and a view
 * that follows you into the next workflow. */

const { test } = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const { open, APP } = require('./helpers/page.js');

const SUITE = path.resolve(APP, '..');

async function openWorkflow(t) {
  const page = await open({ stubs: {
    'suite:pick': SUITE, 'run:start': { ok: true }, 'workflow:save': { ok: true },
  } });
  t.after(() => page.close());
  await page.click('#pickSuite');
  await page.settle(700);
  await page.eval(`(() => { const tabs = [...document.querySelectorAll('button,[role=tab]')]
    .filter((b) => /workflow|quy trình/i.test(b.textContent || ''));
    if (tabs.length) tabs[0].click(); })()`);
  await page.settle(200);
  await page.eval(`(() => { const s = document.getElementById('wfPreset');
    const opt = [...s.options].find((o) => /data-analysis/.test(o.value || o.textContent));
    if (!opt) throw new Error('no data-analysis preset');
    s.value = opt.value; s.dispatchEvent(new Event('change', { bubbles: true })); return true; })()`);
  await page.settle(700);
  return page;
}

const viewBox = (page) => page.eval(
  `(document.querySelector('#wfCanvas svg') || {}).getAttribute
     ? document.querySelector('#wfCanvas svg').getAttribute('viewBox') : null`);

const nums = (s) => String(s).trim().split(/\s+/).map(Number);

test('a freshly opened workflow starts unzoomed and unpanned', async (t) => {
  const page = await openWorkflow(t);
  const [x, y] = nums(await viewBox(page));
  assert.equal(x, 0, 'pan starts at the origin');
  assert.equal(y, 0);
  assert.equal(String(await page.text('#wfZoomLevel')).trim(), '100%');
});

test('zooming in narrows the view, and the readout agrees with it', async (t) => {
  const page = await openWorkflow(t);
  const [, , w0] = nums(await viewBox(page));
  await page.click('#wfZoomIn');
  await page.settle(250);
  const [, , w1] = nums(await viewBox(page));
  assert.ok(w1 < w0, `zooming in must show less of the graph, not more (${w0} -> ${w1})`);
  assert.equal(String(await page.text('#wfZoomLevel')).trim(), '125%');
});

test('zooming with the buttons keeps the centre of the view put', async (t) => {
  const page = await openWorkflow(t);
  const before = nums(await viewBox(page));
  const centre = (v) => [v[0] + v[2] / 2, v[1] + v[3] / 2];
  const [cx0, cy0] = centre(before);
  await page.click('#wfZoomIn');
  await page.settle(200);
  const [cx1, cy1] = centre(nums(await viewBox(page)));
  assert.ok(Math.abs(cx1 - cx0) < 1, `centre drifted horizontally: ${cx0} -> ${cx1}`);
  assert.ok(Math.abs(cy1 - cy0) < 1, `centre drifted vertically: ${cy0} -> ${cy1}`);
});

test('zoom stops at a floor and a ceiling rather than running away', async (t) => {
  const page = await openWorkflow(t);
  for (let i = 0; i < 20; i += 1) await page.eval(`(document.getElementById('wfZoomIn').click(), 1)`);
  await page.settle(300);
  const high = Number(String(await page.text('#wfZoomLevel')).replace('%', ''));
  assert.ok(high <= 300, `zoom ran past the ceiling: ${high}%`);
  for (let i = 0; i < 40; i += 1) await page.eval(`(document.getElementById('wfZoomOut').click(), 1)`);
  await page.settle(300);
  const low = Number(String(await page.text('#wfZoomLevel')).replace('%', ''));
  assert.ok(low >= 35, `zoom ran past the floor: ${low}%`);
});

test('reset puts the view back where it started', async (t) => {
  const page = await openWorkflow(t);
  const start = await viewBox(page);
  await page.click('#wfZoomIn');
  await page.click('#wfZoomIn');
  await page.settle(250);
  assert.notEqual(await viewBox(page), start);
  await page.click('#wfZoomReset');
  await page.settle(250);
  assert.equal(await viewBox(page), start, 'reset must restore the original view exactly');
  assert.equal(String(await page.text('#wfZoomLevel')).trim(), '100%');
});

test('a drag on empty canvas pans, and never leaves the graph unreachable', async (t) => {
  const page = await openWorkflow(t);
  const [x0] = nums(await viewBox(page));
  // Drag far enough that an unclamped pan would put the graph off screen entirely.
  await page.eval(`(() => {
    const svg = document.querySelector('#wfCanvas svg');
    const opts = (x, y) => ({ bubbles: true, clientX: x, clientY: y, button: 0, pointerId: 1 });
    svg.dispatchEvent(new PointerEvent('pointerdown', opts(400, 200)));
    svg.dispatchEvent(new PointerEvent('pointermove', opts(-4000, 200)));
    svg.dispatchEvent(new PointerEvent('pointerup', opts(-4000, 200)));
    return true; })()`);
  await page.settle(250);
  const v = nums(await viewBox(page));
  assert.notEqual(v[0], x0, 'the drag must actually pan');
  assert.ok(v[0] <= 4000, `pan escaped its clamp: ${v[0]}`);
  assert.ok(v[0] + v[2] > 0, 'the graph must still overlap the view after a long drag');
});

test('a pointer press on a node still selects it rather than starting a drag', async (t) => {
  const page = await openWorkflow(t);
  await page.eval(`(() => {
    const n = document.querySelector('#wfCanvas .wf-node');
    if (!n) throw new Error('no node on the canvas');
    n.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, clientX: 50, clientY: 50, button: 0, pointerId: 2 }));
    return true; })()`);
  await page.settle(150);
  assert.equal(await page.eval(
    `document.querySelector('#wfCanvas svg').classList.contains('is-dragging')`), false,
    'pressing a node must not begin a canvas drag, or the click that selects it is swallowed');
});

test('the view does not follow you into the next workflow', async (t) => {
  const page = await openWorkflow(t);
  await page.click('#wfZoomIn');
  await page.click('#wfZoomIn');
  await page.settle(250);
  await page.eval(`(() => { const s = document.getElementById('wfPreset');
    const opt = [...s.options].find((o) => o.value && !/data-analysis/.test(o.value));
    if (!opt) throw new Error('need a second preset');
    s.value = opt.value; s.dispatchEvent(new Event('change', { bubbles: true })); return true; })()`);
  await page.settle(700);
  const [x, y] = nums(await viewBox(page));
  assert.equal(x, 0, 'a new graph opens at the origin');
  assert.equal(y, 0);
  assert.equal(String(await page.text('#wfZoomLevel')).trim(), '100%');
});
