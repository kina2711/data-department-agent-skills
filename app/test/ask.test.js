'use strict';

/* Writing your own request.
 *
 * Before this the app had three prompt sources and none of them was the person: a preset job, a
 * selected task, or a generic fallback. It also sent whichever one it picked without ever showing
 * it, so these cover both halves — that typing wins, and that what will be sent is visible. */

const { test } = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const { open, APP } = require('./helpers/page.js');

const SUITE = path.resolve(APP, '..');

async function openSkill(t) {
  const page = await open({ stubs: { 'suite:pick': SUITE, 'folder:pick': SUITE } });
  t.after(() => page.close());
  await page.click('#pickSuite');
  await page.settle(700);
  await page.click('#grid .card');
  await page.settle(300);
  return page;
}

async function type(page, text) {
  await page.eval(`(() => { const el = document.getElementById('dAsk');
    el.value = ${JSON.stringify(text)};
    el.dispatchEvent(new Event('input', { bubbles: true })); return true; })()`);
  await page.settle(150);
}

const peek = (page) => page.eval('document.getElementById("promptText").textContent');

test('the box exists and starts empty on a freshly opened skill', async (t) => {
  const page = await openSkill(t);
  assert.equal(await page.eval('document.getElementById("dAsk").value'), '');
  assert.equal(await page.visible('#dAsk'), true);
});

test('what will be sent is visible before anything is sent', async (t) => {
  const page = await openSkill(t);
  const shown = String(await peek(page));
  assert.ok(shown.length > 0 && shown !== '(chưa có gì để gửi)',
    'the default prompt is shown rather than hidden');
});

test('typing replaces the preset and the text is carried verbatim', async (t) => {
  const page = await openSkill(t);
  const asked = 'đọc file doanh thu quý 3 và nói rõ chỗ nào dữ liệu không đủ để kết luận';
  await type(page, asked);
  const shown = String(await peek(page));
  assert.ok(shown.includes(asked), 'the sentence reaches the prompt unaltered');
  assert.match(shown, /Yêu cầu cụ thể:/);
});

test('a selected task travels with the sentence as routing, not instead of it', async (t) => {
  const page = await openSkill(t);
  await page.click('#dTasks [aria-selected]');
  await page.settle(250);
  const taskId = await page.eval(`(() => {
    const el = document.querySelector('#dTasks [aria-selected="true"]');
    return el ? el.textContent.trim().split('\\n')[0] : null; })()`);
  await type(page, 'giải thích cho người không kỹ thuật');
  const shown = String(await peek(page));
  assert.ok(shown.includes('giải thích cho người không kỹ thuật'), 'the sentence survives');
  if (taskId) {
    assert.ok(shown.includes(String(taskId).slice(0, 20)),
      'the selected task is still named in the prompt');
  }
});

test('clearing the box falls back rather than sending an empty request', async (t) => {
  const page = await openSkill(t);
  await type(page, 'tạm thời');
  await type(page, '   ');
  const shown = String(await peek(page));
  assert.ok(!shown.includes('Yêu cầu cụ thể'), 'whitespace is not a request');
  assert.ok(shown.length > 0, 'the fallback prompt returns');
});

test('opening another skill does not carry the previous request over', async (t) => {
  const page = await openSkill(t);
  await type(page, 'yêu cầu của skill trước');
  await page.click('#backToSkills');
  await page.settle(250);
  await page.eval('document.querySelectorAll("#grid .card")[1].click()');
  await page.settle(300);
  assert.equal(await page.eval('document.getElementById("dAsk").value'), '',
    'a request written for one skill must not silently run against another');
  assert.ok(!String(await peek(page)).includes('yêu cầu của skill trước'));
});

test('the run button stays disabled without a folder even with a request typed', async (t) => {
  const page = await open({ stubs: { 'suite:pick': SUITE } });
  t.after(() => page.close());
  await page.click('#pickSuite');
  await page.settle(700);
  await page.click('#grid .card');
  await page.settle(300);
  await type(page, 'làm giúp tôi việc này');
  assert.equal(await page.eval('document.getElementById("runStart").disabled'), true,
    'a request without a working directory has nowhere to run');
});
