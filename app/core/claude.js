'use strict';

/* Running `claude` and reading what it streams back.
 *
 * Both doors need this and neither should own it. The argv is the interesting half: which flags
 * a run carries decides whether it can write to the user's files, so building that list in two
 * places is two places for the permission mode to drift.
 *
 * `claude -p --output-format stream-json` emits one JSON object per line. Splitting that stream
 * is the other half, and it is the half with an edge case worth keeping in one copy: the last
 * line arrives without a trailing newline, so a splitter that only acts on newlines silently
 * drops the final result — the one carrying the answer.
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

/** True when this directory is a Claude Code plugin, so `--plugin-dir` is worth passing. */
function isPluginDir(suitePath) {
  return Boolean(suitePath) && fs.existsSync(path.join(suitePath, '.claude-plugin'));
}

/** The argv for a headless run. Exported on its own so a caller can show it before spending. */
function buildArgv({ prompt, suitePath, permissionMode, model, resume }) {
  const argv = ['-p', '--output-format', 'stream-json', '--verbose'];
  if (isPluginDir(suitePath)) argv.push('--plugin-dir', suitePath);
  // Default `plan`: Claude says what it would do and touches nothing. A caller that wants writes
  // has to ask for them by name.
  argv.push('--permission-mode', permissionMode || 'plan');
  // An empty model means the CLI's own default applies, which is the honest outcome for a task
  // whose tier nobody has set.
  if (model) argv.push('--model', String(model));
  // Resuming carries the prior exchange, which is what makes a reply a reply rather than a new
  // conversation about the same subject.
  if (resume) argv.push('--resume', String(resume));
  argv.push(String(prompt));
  return argv;
}

/** The argv for an interactive run, the one a terminal window would show. */
function buildInteractiveArgv({ prompt, suitePath }) {
  const argv = ['claude'];
  if (isPluginDir(suitePath)) argv.push('--plugin-dir', suitePath);
  argv.push(String(prompt));
  return argv;
}

/** Turn a byte stream into whole JSON events, keeping the unterminated tail for the end. */
function createStreamParser(onEvent) {
  let buffer = '';
  const emit = (line) => {
    const trimmed = line.trim();
    if (!trimmed) return;
    try {
      onEvent(JSON.parse(trimmed));
    } catch {
      // Not every line is JSON when the CLI writes a notice; show it rather than drop it.
      onEvent({ type: 'raw', text: trimmed });
    }
  };
  return {
    push(chunk) {
      buffer += chunk;
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';
      for (const line of lines) emit(line);
    },
    // The final line has no newline after it. Without this the result event is lost.
    end() {
      if (buffer.trim()) emit(buffer);
      buffer = '';
    },
  };
}

/**
 * Start a headless run. Returns { ok, child } or { ok: false, error }.
 * Callers supply `onEvent`, `onStderr` and `onDone`; nothing here decides how to display them.
 */
function startRun(options, { onEvent, onStderr, onDone }) {
  const { folder, prompt } = options;
  if (!folder || !fs.existsSync(folder)) return { ok: false, error: 'Thư mục không tồn tại' };
  if (!String(prompt || '').trim()) return { ok: false, error: 'Prompt rỗng' };

  let child;
  try {
    child = spawn('claude', buildArgv(options), { cwd: folder, stdio: ['ignore', 'pipe', 'pipe'] });
  } catch (err) {
    return { ok: false, error: `Không chạy được claude: ${err.message}` };
  }

  const parser = createStreamParser((ev) => onEvent && onEvent(ev));
  child.stdout.on('data', (chunk) => parser.push(chunk.toString('utf8')));
  child.stderr.on('data', (chunk) => onStderr && onStderr(chunk.toString('utf8')));
  child.on('error', (err) => onDone && onDone({ code: -1, error: err.message }));
  child.on('close', (code) => {
    parser.end();
    onDone && onDone({ code });
  });

  return { ok: true, child };
}

/** The prompt a skill or task run opens with, when the caller has not written one. */
function defaultPrompt(skillId, taskId) {
  return taskId
    ? `Use the ${skillId} skill and run the atomic task ${taskId} in this directory.`
    : `Use the ${skillId} skill for work in this directory. Route to the right atomic task by primary deliverable.`;
}

module.exports = {
  isPluginDir, buildArgv, buildInteractiveArgv, createStreamParser, startRun, defaultPrompt,
};
