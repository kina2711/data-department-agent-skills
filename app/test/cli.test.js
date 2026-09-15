'use strict';

/* The CLI and the library under it.
 *
 * These run in-process rather than by spawning the command, so a failure points at the function
 * that broke instead of at an exit code. The one thing that has to be spawned is the piping
 * behaviour, because the bug it guards against only exists when stdout is a pipe.
 */

const test = require('node:test');
const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const { parseArgs } = require('../cli/data-agent.js');
const ui = require('../cli/ui.js');
const claude = require('../core/claude.js');
const prompt = require('../core/prompt.js');
const config = require('../core/config.js');
const sessionStore = require('../core/session.js');

const CLI = path.join(__dirname, '..', 'cli', 'data-agent.js');
const SUITE = path.join(__dirname, '..', '..');

test('a flag with an attached value and one with a separate value parse the same', () => {
  assert.equal(parseArgs(['--tier=strong']).flags.tier, 'strong');
  assert.equal(parseArgs(['--tier', 'strong']).flags.tier, 'strong');
});

test('a flag with nothing after it is a switch, not a flag swallowing the next flag', () => {
  const { flags } = parseArgs(['--json', '--tier', 'strong']);
  assert.equal(flags.json, true);
  assert.equal(flags.tier, 'strong');
});

test('--set collects key=value pairs and keeps = inside the value', () => {
  const { values } = parseArgs(['--set', 'a=1', '--set', 'b=x=y']);
  assert.deepEqual(values, { a: '1', b: 'x=y' });
});

test('the run argv defaults to plan, so a run cannot write unless asked', () => {
  const argv = claude.buildArgv({ prompt: 'x' });
  assert.ok(argv.includes('--permission-mode'));
  assert.equal(argv[argv.indexOf('--permission-mode') + 1], 'plan');
});

test('no model flag is emitted when none was given', () => {
  // A task declares a tier, never a model name. Passing the tier through produced
  // `--model standard`, which is not a model any provider has.
  assert.ok(!claude.buildArgv({ prompt: 'x' }).includes('--model'));
  assert.ok(claude.buildArgv({ prompt: 'x', model: 'sonnet' }).includes('--model'));
});

test('the prompt is always the last argument, so a flag can never be read as one', () => {
  const argv = claude.buildArgv({ prompt: '--not-a-flag', model: 'sonnet', resume: 'abc' });
  assert.equal(argv[argv.length - 1], '--not-a-flag');
});

test('the stream parser holds the unterminated last line until the stream ends', () => {
  const seen = [];
  const parser = claude.createStreamParser((ev) => seen.push(ev.type));
  parser.push('{"type":"a"}\n{"type":"b"}\n{"type":"c"}');
  assert.deepEqual(seen, ['a', 'b'], 'the tail has no newline yet and must not be emitted early');
  parser.end();
  assert.deepEqual(seen, ['a', 'b', 'c'], 'ending the stream releases the final result event');
});

test('a line that is not JSON is shown rather than dropped', () => {
  const seen = [];
  const parser = claude.createStreamParser((ev) => seen.push(ev));
  parser.push('warning: something\n');
  assert.equal(seen[0].type, 'raw');
  assert.equal(seen[0].text, 'warning: something');
});

test('an optional template part is left out when its condition is unfilled', () => {
  const job = { mau: ['Làm {x}', { neu: 'y', text: 'kèm {y}' }] };
  assert.equal(prompt.composePrompt(job, { x: 'A' }), 'Làm A.');
  assert.equal(prompt.composePrompt(job, { x: 'A', y: 'B' }), 'Làm A. kèm B.');
});

test('width counts display columns, not code points', () => {
  // A combining mark takes no column of its own. Counting it aligned every Vietnamese column
  // one cell too far left.
  assert.equal(ui.width('chi'), 3);
  assert.equal(ui.width('chỉ'), 3);
  assert.equal(ui.width('é'), 1);
});

test('nearest suggests a real neighbour and stays silent when nothing is close', () => {
  assert.match(ui.nearest('skils', ['skills', 'tasks']), /skills/);
  assert.equal(ui.nearest('zzzzzzzzzz', ['skills', 'tasks']), '');
});

test('resolveSuite prefers the explicit path over the saved one', () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'da-cfg-'));
  fs.writeFileSync(path.join(dir, 'config.json'), JSON.stringify({ suitePath: '/nowhere' }));
  assert.equal(config.resolveSuite({ explicit: SUITE, dir }), path.resolve(SUITE));
  fs.rmSync(dir, { recursive: true, force: true });
});

test('resolveSuite returns nothing rather than guessing a directory that holds no suite', () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'da-cfg-'));
  assert.equal(config.resolveSuite({ dir, cwd: os.tmpdir() }), '');
  fs.rmSync(dir, { recursive: true, force: true });
});

test('migrate adopts a legacy config once and never overwrites a live one', () => {
  const home = fs.mkdtempSync(path.join(os.tmpdir(), 'da-home-'));
  const legacy = path.join(home, 'Data Agent');
  fs.mkdirSync(legacy, { recursive: true });
  fs.writeFileSync(path.join(legacy, 'config.json'),
    JSON.stringify({ suitePath: '/from/legacy', recentFolders: ['/a'] }));
  const target = path.join(home, 'data-agent');
  const env = process.env.XDG_CONFIG_HOME;
  const override = process.env.DA_CONFIG_DIR;
  process.env.XDG_CONFIG_HOME = home;
  // DA_CONFIG_DIR disables adoption by design, and the suite runner sets it. Clear it here so
  // this test exercises the migration path rather than the switch that turns it off.
  delete process.env.DA_CONFIG_DIR;
  try {
    assert.equal(config.migrate(target).config.suitePath, '/from/legacy');
    config.write({ suitePath: '/chosen/later', recentFolders: [] }, target);
    assert.equal(config.migrate(target).adopted, '', 'a config that already answers must be left alone');
    assert.equal(config.read(target).suitePath, '/chosen/later');
  } finally {
    if (env === undefined) delete process.env.XDG_CONFIG_HOME;
    else process.env.XDG_CONFIG_HOME = env;
    if (override === undefined) delete process.env.DA_CONFIG_DIR;
    else process.env.DA_CONFIG_DIR = override;
    fs.rmSync(home, { recursive: true, force: true });
  }
});

test('--json survives being piped, which is the only way the truncation bug appears', () => {
  // console.log to a pipe is asynchronous; process.exit() cut the tail off the array, producing
  // a document that parses nowhere. Reading it back is the assertion.
  const out = execFileSync(process.execPath, [CLI, 'tasks', '--suite', SUITE, '--json'],
    { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 });
  const rows = JSON.parse(out);
  assert.ok(rows.length > 800, `expected the whole catalog, got ${rows.length}`);
  assert.ok(rows.every((r) => r.id && r.skill));
});

test('an unknown command fails with a suggestion and a non-zero code', () => {
  let code = 0;
  let stderrText = '';
  try {
    execFileSync(process.execPath, [CLI, 'skils', '--suite', SUITE], { encoding: 'utf8' });
  } catch (err) {
    code = err.status;
    stderrText = `${err.stdout || ''}${err.stderr || ''}`;
  }
  assert.equal(code, 1);
  assert.match(stderrText, /skills/);
});

test('a dry run prints the argv and sends nothing', () => {
  const out = execFileSync(process.execPath,
    [CLI, 'run', 'de-build-batch-ingestion', '--suite', SUITE, '--dir', SUITE, '--dry-run'],
    { encoding: 'utf8' });
  // Assert on the argv line itself: the field table above it prints the words "--model để đặt"
  // as advice, and a substring search over the whole output matched that instead.
  const argvLine = out.split('\n').find((line) => line.startsWith('claude '));
  assert.ok(argvLine, 'the dry run must print the command it would have executed');
  assert.match(argvLine, /--permission-mode plan/);
  assert.ok(!argvLine.includes('--model'), 'the task tier must not be passed as a model name');
});

test('sessions merge from every legacy store, not just the most recently touched', () => {
  // Picking the newest store adopted a development profile a test run had just written, and left
  // the real unfinished work — older, in another directory — behind.
  const home = fs.mkdtempSync(path.join(os.tmpdir(), 'da-home-'));
  const write = (dir, doc) => {
    fs.mkdirSync(path.join(home, dir), { recursive: true });
    fs.writeFileSync(path.join(home, dir, 'sessions.json'), JSON.stringify(doc));
  };
  write('Data Agent', { version: 1, sessions: { '/real::orch': { sessionId: 'real', folder: '/real', skillId: 'orch', updatedAt: '2026-09-13T00:00:00Z' } } });
  write('Electron', { version: 1, sessions: { '/dev::orch': { sessionId: 'dev', folder: '/dev', skillId: 'orch', updatedAt: '2026-09-15T00:00:00Z' } } });
  // Make the development store the newest on disk, which is what misled the first attempt.
  fs.utimesSync(path.join(home, 'Electron', 'sessions.json'), new Date(), new Date());

  const target = path.join(home, 'store.json');
  const env = process.env.XDG_CONFIG_HOME;
  const store = process.env.DA_SESSIONS_PATH;
  process.env.XDG_CONFIG_HOME = home;
  delete process.env.DA_SESSIONS_PATH;
  try {
    const result = sessionStore.migrate(target);
    assert.equal(result.count, 2, 'both stores must survive the merge');
    const ids = sessionStore.list(target).map((s) => s.sessionId).sort();
    assert.deepEqual(ids, ['dev', 'real']);
  } finally {
    if (env === undefined) delete process.env.XDG_CONFIG_HOME;
    else process.env.XDG_CONFIG_HOME = env;
    if (store !== undefined) process.env.DA_SESSIONS_PATH = store;
    fs.rmSync(home, { recursive: true, force: true });
  }
});

test('a saved session keeps the folder and skill it belongs to', () => {
  const file = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'da-sess-')), 'sessions.json');
  sessionStore.save({ sessionId: 'abc', folder: '/w', skillId: 'de', turns: 3, lastText: 'x' }, file);
  const got = sessionStore.get('/w', 'de', file);
  assert.equal(got.sessionId, 'abc');
  assert.equal(got.turns, 3);
  assert.equal(sessionStore.get('/w', 'other', file), null, 'a different skill is a different session');
  fs.rmSync(path.dirname(file), { recursive: true, force: true });
});

test('a session with no id is refused rather than stored as a pointer to nothing', () => {
  const file = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'da-sess-')), 'sessions.json');
  assert.equal(sessionStore.save({ folder: '/w', skillId: 'de' }, file).ok, false);
  fs.rmSync(path.dirname(file), { recursive: true, force: true });
});
