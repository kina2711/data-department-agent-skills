'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const { open } = require('./helpers/page.js');

test('the app boots and shows the skills view with no suite connected', async (t) => {
  const page = await open();
  t.after(() => page.close());
  assert.equal(await page.eval('document.title || document.querySelector("h1,.brand")?.textContent || "?"') !== null, true);
  assert.equal(await page.visible('#viewSkills'), true);
  const empty = await page.text('#grid .empty');
  assert.match(String(empty), /Chưa nối suite/);
});
