'use strict';

/* A session that survives the app closing.
 *
 * `claude -p --resume <id>` carries the model's side of a conversation across a restart; the
 * transcript on screen does not come back. So the thing worth testing is not only that the id is
 * stored and reused, but that the app is honest about which half returned — an empty log under a
 * heading claiming the conversation was restored is a lie the person finds out about by asking a
 * question the agent answers from context they cannot see.
 *
 * Every case runs against a throwaway userData directory, so the real profile is never touched. */

const { test } = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');
const os = require('node:os');
const { open, APP } = require('./helpers/page.js');

const SUITE = path.resolve(APP, '..');

/* One throwaway store per test, and a fresh profile per app instance.
 *
 * Chromium locks a userData directory, so the two instances that make up a restart cannot share
 * one; the session store is named separately precisely so they can share that and nothing else. */
function store(t) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'da-session-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  return path.join(dir, 'sessions.json');
}

function sessionsFile(file) {
  return fs.existsSync(file) ? JSON.parse(fs.readFileSync(file, 'utf8')) : null;
}

async function detail(t, sessionsPath, stubs = {}) {
  const page = await open({
    sessionsPath,
    // Inside the store's own directory, so the test's cleanup takes the profiles with it.
    userData: fs.mkdtempSync(path.join(path.dirname(sessionsPath), 'profile-')),
    stubs: { 'suite:pick': SUITE, 'folder:pick': SUITE, 'run:start': { ok: true }, ...stubs },
  });
  t.after(() => page.close());
  await page.click('#pickSuite');
  await page.settle(700);
  await page.click('#grid .card');
  await page.settle(300);
  await page.click('#pickFolder');
  await page.settle(300);
  return page;
}

async function fakeRun(page, { session = 'sess-keep', code = 0 } = {}) {
  await page.eval(`(() => {
    window.runUI.newId();
    window.runUI.reset();
    window.runUI.setRunning(true);
    window.runUI.handleEvent({ type: 'system', session_id: ${JSON.stringify(session)} });
    window.runUI.handleEvent({ type: 'assistant', message: { content: [
      { type: 'text', text: 'Đã đọc xong repo, bạn muốn bắt đầu từ đâu?' }] } });
    window.runUI.finish(${code});
    return true; })()`);
  await page.settle(350);
}

test('a finished run leaves the session on disk', async (t) => {
  const dir = store(t);
  const page = await detail(t, dir);
  await fakeRun(page, { session: 'sess-on-disk' });

  const doc = sessionsFile(dir);
  assert.ok(doc, 'sessions.json must exist after a run that produced a session');
  const rec = Object.values(doc.sessions)[0];
  assert.equal(rec.sessionId, 'sess-on-disk');
  assert.equal(rec.folder, SUITE, 'the folder is what makes the id meaningful');
  assert.ok(rec.updatedAt, 'without a timestamp the offer cannot say how old it is');
});

test('a run that produced no session stores nothing to resume', async (t) => {
  const dir = store(t);
  const page = await detail(t, dir);
  await page.eval(`(() => {
    window.runUI.newId(); window.runUI.reset(); window.runUI.setRunning(true);
    window.runUI.handleEvent({ type: 'raw', text: 'không có session_id' });
    window.runUI.finish(0); return true; })()`);
  await page.settle(300);
  assert.equal(sessionsFile(dir), null, 'an id-less run must not leave a resume offer behind');
});

test('reopening the app offers the unfinished session', async (t) => {
  const dir = store(t);
  const first = await detail(t, dir);
  await fakeRun(first, { session: 'sess-across-restart' });
  await first.close();

  // A second app, same profile: exactly what a restart is.
  const page = await detail(t, dir);
  assert.equal(await page.eval('document.getElementById("resumeBar").hidden'), false,
    'the offer must appear on its own, without the person remembering the session id');
  assert.match(String(await page.text('#resumeSub')), /ngữ cảnh/);
});

test('resuming reuses the stored id instead of starting a new conversation', async (t) => {
  const dir = store(t);
  const first = await detail(t, dir);
  await fakeRun(first, { session: 'sess-reused' });
  await first.close();

  const page = await detail(t, dir);
  await page.click('#resumeGo');
  await page.settle(300);
  await page.calls('run:start', true);
  await page.eval(`(() => { document.getElementById('reply').value = 'tiếp đi'; return true; })()`);
  await page.click('#replySend');
  await page.settle(350);

  const sent = await page.calls('run:start');
  assert.equal(sent.length, 1);
  assert.equal(sent[0].args.resume, 'sess-reused',
    'resuming a stored session must carry its id, or the restart silently began a new conversation');
});

test('the resumed transcript says the log did not come back', async (t) => {
  const dir = store(t);
  const first = await detail(t, dir);
  await fakeRun(first, { session: 'sess-honest' });
  await first.close();

  const page = await detail(t, dir);
  await page.click('#resumeGo');
  await page.settle(300);
  const log = String(await page.text('#runLog'));
  assert.match(log, /bắt đầu lại từ trống/,
    'an empty log under a restored session must say which half of it returned');
  assert.equal(await page.eval('document.getElementById("replyBox").hidden'), false,
    'the point of resuming is being able to type the next question');
  assert.equal(await page.eval('document.getElementById("runStop").disabled'), true,
    'nothing is running yet, so Stop must not offer to cancel a run that does not exist');
});

test('dismissing the offer forgets the session for good', async (t) => {
  const dir = store(t);
  const first = await detail(t, dir);
  await fakeRun(first, { session: 'sess-dropped' });
  await first.close();

  const page = await detail(t, dir);
  await page.click('#resumeDrop');
  await page.settle(300);
  assert.equal(await page.eval('document.getElementById("resumeBar").hidden'), true);
  const doc = sessionsFile(dir);
  assert.deepEqual(Object.values(doc.sessions || {}), [],
    'a dismissed offer that comes back next launch is not a dismissal');
});

test('a fresh profile offers nothing, and the offer is really off the screen', async (t) => {
  const dir = store(t);
  const page = await detail(t, dir);
  assert.equal(await page.eval('document.getElementById("resumeBar").hidden'), true);
  // The attribute is not the truth. A class that sets `display` outranks the UA rule for [hidden],
  // so the bar rendered in full while `.hidden` kept answering true -- an assertion on the
  // attribute alone passed while the screen showed an offer that did not exist.
  assert.equal(await page.onScreen('#resumeBar'), false,
    'the bar must be off the screen, not merely marked hidden');
});
