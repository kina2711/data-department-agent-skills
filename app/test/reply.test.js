'use strict';

/* Talking back to a run.
 *
 * `claude -p` answers once and exits. When the agent asked eight questions the transcript ended
 * there and the person had nowhere to type, so the whole exchange was one-way. These cover the
 * mechanism that fixes it and, more importantly, the two ways it could look fixed and not be:
 * replying without resuming, and offering a reply box when there is no session to resume. */

const { test } = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const { open, APP } = require('./helpers/page.js');

const SUITE = path.resolve(APP, '..');

async function runPane(t, stubs = {}) {
  const page = await open({ stubs: { 'suite:pick': SUITE, 'folder:pick': SUITE, 'run:start': { ok: true }, ...stubs } });
  t.after(() => page.close());
  await page.click('#pickSuite');
  await page.settle(700);
  await page.click('#grid .card');
  await page.settle(300);
  await page.click('#pickFolder');
  await page.settle(250);
  return page;
}

/** Drive the transcript the way the main process does: events, then a close. */
async function fakeRun(page, { session = 'sess-abc', code = 0 } = {}) {
  await page.eval(`(() => {
    const id = window.runUI.newId();
    window.runUI.reset();
    window.runUI.setRunning(true);
    window.runUI.handleEvent({ type: 'system', session_id: ${JSON.stringify(session)} });
    window.runUI.handleEvent({ type: 'raw', text: 'Bạn muốn học SQL ở mức nào?' });
    window.runUI.finish(${code});
    return true; })()`);
  await page.settle(250);
}

test('the reply box stays hidden until a run has finished with a session', async (t) => {
  const page = await runPane(t);
  assert.equal(await page.eval('document.getElementById("replyBox").hidden'), true);
  await fakeRun(page);
  assert.equal(await page.eval('document.getElementById("replyBox").hidden'), false);
});

test('a run that produced no session offers no reply box', async (t) => {
  const page = await runPane(t);
  await page.eval(`(() => {
    window.runUI.newId(); window.runUI.reset(); window.runUI.setRunning(true);
    window.runUI.handleEvent({ type: 'raw', text: 'không có session_id' });
    window.runUI.finish(0); return true; })()`);
  await page.settle(250);
  assert.equal(await page.eval('document.getElementById("replyBox").hidden'), true,
    'a box that opens a new conversation wearing the old transcript is worse than no box');
});

test('a failed run offers no reply box', async (t) => {
  const page = await runPane(t);
  await fakeRun(page, { code: 1 });
  assert.equal(await page.eval('document.getElementById("replyBox").hidden'), true);
});

test('sending a reply resumes the session rather than starting a new conversation', async (t) => {
  const page = await runPane(t);
  await fakeRun(page, { session: 'sess-xyz' });
  await page.calls('run:start', true);          // forget anything from setting the pane up
  await page.eval(`(() => { document.getElementById('reply').value =
    'câu trả lời của tôi: 1b 2a 3a'; return true; })()`);
  await page.click('#replySend');
  await page.settle(300);

  // Recorded in the main process: the page cannot spy on window.studio, which the context bridge
  // freezes, so a spy installed there records nothing while the real call goes through.
  const sent = await page.calls('run:start');
  assert.equal(sent.length, 1, 'one call per reply');
  assert.equal(sent[0].args.resume, 'sess-xyz', 'the reply must carry the session it is replying to');
  assert.equal(sent[0].args.prompt, 'câu trả lời của tôi: 1b 2a 3a', 'the reply is the prompt, verbatim');
});

test('the reply appears in the transcript and does not clear what came before', async (t) => {
  const page = await runPane(t);
  await fakeRun(page);
  const before = await page.eval('document.querySelectorAll("#runLog .run-row").length');
  await page.eval(`(() => { document.getElementById('reply').value = 'trả lời'; return true; })()`);
  await page.click('#replySend');
  await page.settle(300);
  const after = await page.eval('document.querySelectorAll("#runLog .run-row").length');
  assert.ok(after > before, 'the transcript grows rather than resetting');
  assert.equal(await page.eval('!!document.querySelector("#runLog .run-you")'), true,
    'what the person said is marked as theirs');
});

test('an empty reply sends nothing', async (t) => {
  const page = await runPane(t);
  await fakeRun(page);
  await page.calls('run:start', true);
  await page.eval(`(() => { document.getElementById('reply').value = '   '; return true; })()`);
  await page.click('#replySend');
  await page.settle(250);
  assert.deepEqual(await page.calls('run:start'), []);
});

test('the box clears between runs so a stale answer is never resent', async (t) => {
  const page = await runPane(t);
  await fakeRun(page);
  await page.eval(`(() => { document.getElementById('reply').value = 'chưa gửi'; return true; })()`);
  await fakeRun(page, { session: 'sess-second' });
  assert.equal(await page.eval('document.getElementById("reply").value'), '');
});

/* What the closing event repeats, and what the app was silent about. */

test('the closing result does not repeat the last assistant message', async (t) => {
  const page = await runPane(t);
  await page.eval(`(() => {
    window.runUI.newId(); window.runUI.reset(); window.runUI.setRunning(true);
    window.runUI.handleEvent({ type: 'system', session_id: 'sess-dupe' });
    window.runUI.handleEvent({ type: 'assistant', message: { content: [
      { type: 'text', text: 'Bị chặn ở khâu cuối: phiên này vẫn đang ở plan mode.' }] } });
    window.runUI.handleEvent({ total_cost_usd: 0.01,
      result: 'Bị chặn ở khâu cuối: phiên này vẫn đang ở plan mode.' });
    window.runUI.finish(0); return true; })()`);
  await page.settle(250);
  const texts = await page.eval(
    '[...document.querySelectorAll("#runLog .run-text .run-body")].map(e => e.textContent)');
  assert.equal(texts.length, 1, `the final paragraph was printed ${texts.length} times`);
});

test('a closing result that adds something is still shown', async (t) => {
  const page = await runPane(t);
  await page.eval(`(() => {
    window.runUI.newId(); window.runUI.reset(); window.runUI.setRunning(true);
    window.runUI.handleEvent({ type: 'assistant', message: { content: [
      { type: 'text', text: 'đang làm' }] } });
    window.runUI.handleEvent({ total_cost_usd: 0.01, result: 'kết luận khác hẳn' });
    window.runUI.finish(0); return true; })()`);
  await page.settle(250);
  const texts = await page.eval(
    '[...document.querySelectorAll("#runLog .run-text .run-body")].map(e => e.textContent)');
  assert.deepEqual(texts, ['đang làm', 'kết luận khác hẳn']);
});

test('the reply area names the permission mode the next turn will use', async (t) => {
  const page = await runPane(t);
  await fakeRun(page);
  assert.match(String(await page.text('#replyMode')), /Lượt tới/);
});

test('plan mode is called out, because in it nothing gets written', async (t) => {
  const page = await runPane(t);
  await page.eval(`(() => { const s = document.getElementById('permMode');
    s.value = 'plan'; s.dispatchEvent(new Event('change', { bubbles: true })); return true; })()`);
  await fakeRun(page);
  assert.match(String(await page.text('#replyMode')), /không ghi file nào/);
  assert.equal(await page.eval(
    'document.getElementById("replyMode").classList.contains("is-plan")'), true);
});

test('switching the mode updates what the reply will carry', async (t) => {
  const page = await runPane(t);
  await fakeRun(page, { session: 'sess-mode' });
  await page.eval(`(() => { const s = document.getElementById('permMode');
    s.value = 'acceptEdits'; s.dispatchEvent(new Event('change', { bubbles: true })); return true; })()`);
  await page.settle(150);
  assert.match(String(await page.text('#replyMode')), /Cho sửa file/);

  await page.calls('run:start', true);
  await page.eval(`(() => { document.getElementById('reply').value = 'chạy đi'; return true; })()`);
  await page.click('#replySend');
  await page.settle(300);
  const sent = await page.calls('run:start');
  assert.equal(sent[0].args.permissionMode, 'acceptEdits',
    'the reply must carry the mode shown, or the label is a lie');
  assert.equal(sent[0].args.resume, 'sess-mode');
});
