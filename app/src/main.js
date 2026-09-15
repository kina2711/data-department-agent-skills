'use strict';
const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const { spawn, spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { readSuite, contractCache } = require('../core/suite');
const claudeCore = require('../core/claude');
const configCore = require('../core/config');

// The suite is read, never written. The app is a launcher; Claude Code does the work.
/* The config lives where the CLI also looks, not under Electron's userData.
 *
 * userData is named after the product, so the two doors sat in different directories and a suite
 * picked in the app was invisible to `data-agent`. The first read adopts whatever the old
 * location held — including the recent folders, which are the part a user would have to retype. */
const readConfig = () => configCore.read();
const writeConfig = (cfg) => configCore.write(cfg);
configCore.migrate();

/* Sessions that outlive the window.
 *
 * `--resume` restores the model's side of a conversation, so continuing after a restart needs
 * nothing more than the session id. The transcript on screen is not restored and the app says so:
 * claiming to have brought back a conversation while showing an empty log would be a lie the user
 * only discovers by asking a question the agent answers from context they cannot see.
 *
 * Keyed on folder plus skill, because a session belongs to the work it was doing. Records are
 * capped and the oldest dropped, so a long-running install does not accumulate a session file
 * nobody reads.
 */
/* The store lives beside the config, but its path is overridable.
 *
 * Chromium locks a userData directory, so two app instances cannot share one — and a test for
 * "the session survived a restart" is precisely two instances that must see the same store.
 * Naming the file separately gives the test a shared store without a shared profile lock. */
const SESSIONS_PATH = process.env.DA_SESSIONS_PATH || path.join(app.getPath('userData'), 'sessions.json');
const SESSION_LIMIT = 60;

function readSessions() {
  try {
    const doc = JSON.parse(fs.readFileSync(SESSIONS_PATH, 'utf8'));
    return doc && typeof doc === 'object' && doc.sessions ? doc : { version: 1, sessions: {} };
  } catch {
    return { version: 1, sessions: {} };
  }
}

function sessionKey(folder, skillId) {
  return `${folder || ''}::${skillId || ''}`;
}

ipcMain.handle('session:get', (_e, { folder, skillId }) => {
  const doc = readSessions();
  return doc.sessions[sessionKey(folder, skillId)] || null;
});

ipcMain.handle('session:save', (_e, record) => {
  if (!record || !record.sessionId || !record.folder) return { ok: false, error: 'thiếu session hoặc thư mục' };
  const doc = readSessions();
  doc.sessions[sessionKey(record.folder, record.skillId)] = {
    sessionId: record.sessionId,
    folder: record.folder,
    skillId: record.skillId || '',
    skillName: record.skillName || '',
    mode: record.mode || 'plan',
    turns: Number(record.turns) || 1,
    lastText: String(record.lastText || '').slice(0, 400),
    updatedAt: new Date().toISOString(),
  };
  // Oldest first, so the cap drops what nobody has touched.
  const entries = Object.entries(doc.sessions)
    .sort((a, b) => String(b[1].updatedAt).localeCompare(String(a[1].updatedAt)))
    .slice(0, SESSION_LIMIT);
  doc.sessions = Object.fromEntries(entries);
  try {
    fs.mkdirSync(path.dirname(SESSIONS_PATH), { recursive: true });
    fs.writeFileSync(SESSIONS_PATH, JSON.stringify(doc, null, 2) + '\n');
    return { ok: true };
  } catch (err) {
    return { ok: false, error: err.message };
  }
});

ipcMain.handle('session:forget', (_e, { folder, skillId }) => {
  const doc = readSessions();
  delete doc.sessions[sessionKey(folder, skillId)];
  try {
    fs.writeFileSync(SESSIONS_PATH, JSON.stringify(doc, null, 2) + '\n');
    return { ok: true };
  } catch (err) {
    return { ok: false, error: err.message };
  }
});

function createWindow() {
  const win = new BrowserWindow({
    width: 1180,
    height: 820,
    minWidth: 900,
    backgroundColor: '#f7f7f8',
    titleBarStyle: 'default',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });
  win.loadFile(path.join(__dirname, 'index.html'));
  return win;
}

app.whenReady().then(() => {
  createWindow();
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

ipcMain.handle('config:get', () => readConfig());

ipcMain.handle('suite:pick', async () => {
  const result = await dialog.showOpenDialog({
    title: 'Chọn thư mục suite (chứa suite-manifest.yaml)',
    properties: ['openDirectory'],
  });
  if (result.canceled || !result.filePaths[0]) return null;
  const cfg = readConfig();
  cfg.suitePath = result.filePaths[0];
  writeConfig(cfg);
  return cfg.suitePath;
});

ipcMain.handle('suite:read', (_e, suitePath) => {
  contractCache.clear();
  try {
    return readSuite(suitePath);
  } catch (err) {
    return { error: String(err && err.message ? err.message : err) };
  }
});

ipcMain.handle('folder:pick', async () => {
  const result = await dialog.showOpenDialog({
    title: 'Chọn thư mục làm việc',
    properties: ['openDirectory', 'createDirectory'],
  });
  if (result.canceled || !result.filePaths[0]) return null;
  const folder = result.filePaths[0];
  const cfg = readConfig();
  cfg.recentFolders = [folder, ...(cfg.recentFolders || []).filter((f) => f !== folder)].slice(0, 8);
  writeConfig(cfg);
  return folder;
});

/** Launch Claude Code in a terminal, in the chosen folder, primed with the chosen skill.
 *  The app never runs the model itself and never edits the user's files.
 *
 *  The invocation goes into a generated script rather than onto the terminal's command line:
 *  the prompt contains spaces and quotes, terminals disagree about how -e parses its remainder,
 *  and a script can hold the window open so a failure to start is readable instead of a window
 *  that blinks and disappears. */
function shellQuote(value) {
  return `'${String(value).replace(/'/g, `'\\''`)}'`;
}

ipcMain.handle('session:launch', (_e, { folder, skillId, taskId, suitePath }) => {
  if (!folder || !fs.existsSync(folder)) return { ok: false, error: 'Thư mục không tồn tại' };

  const prompt = claudeCore.defaultPrompt(skillId, taskId);
  const argv = claudeCore.buildInteractiveArgv({ prompt, suitePath });

  const scriptPath = path.join(os.tmpdir(), `dd-studio-${Date.now()}.sh`);
  const script = [
    '#!/usr/bin/env bash',
    `cd ${shellQuote(folder)} || { echo "Không vào được thư mục"; read -rp "Enter để đóng"; exit 1; }`,
    argv.map(shellQuote).join(' '),
    'status=$?',
    'echo',
    'if [ "$status" -ne 0 ]; then echo "claude thoát với mã $status"; fi',
    'read -rp "Enter để đóng cửa sổ này"',
    `rm -f ${shellQuote(scriptPath)}`,
    '',
  ].join('\n');

  try {
    fs.writeFileSync(scriptPath, script, { mode: 0o700 });
  } catch (err) {
    return { ok: false, error: `Không ghi được script phóng: ${err.message}` };
  }

  const terminals = [
    ['x-terminal-emulator', ['-e']],
    ['gnome-terminal', [`--working-directory=${folder}`, '--']],
    ['konsole', ['--workdir', folder, '-e']],
    ['xfce4-terminal', [`--working-directory=${folder}`, '-x']],
    ['xterm', ['-e']],
  ];

  for (const [bin, prefix] of terminals) {
    try {
      const child = spawn(bin, [...prefix, 'bash', scriptPath], {
        cwd: folder, detached: true, stdio: 'ignore',
      });
      child.unref();
      return { ok: true, terminal: bin, script: scriptPath };
    } catch {
      /* try the next terminal */
    }
  }
  return { ok: false, error: 'Không tìm thấy terminal nào để mở. Cài x-terminal-emulator hoặc gnome-terminal.' };
});

ipcMain.handle('shell:openPath', (_e, target) => shell.openPath(target));
ipcMain.handle('os:tmpdir', () => os.tmpdir());

// ---- Workflow canvas -------------------------------------------------------
// The manifest schema sets additionalProperties:false and holds no coordinates, so node
// positions are never persisted. The canvas lays the graph out from depends_on every time,
// which means the picture cannot drift away from the data it draws.

// The suite ships one generated workflow per skill; list them so the canvas opens without a
// file dialog for the common case.
ipcMain.handle('workflow:list', (_e, suitePath) => {
  const dir = path.join(suitePath || '', 'workflows');
  try {
    return fs.readdirSync(dir)
      .filter((f) => f.endsWith('.workflow.json'))
      .sort()
      .map((f) => ({ file: path.join(dir, f), skill: f.replace(/\.workflow\.json$/, '') }));
  } catch {
    return [];
  }
});

ipcMain.handle('workflow:openPath', (_e, file) => {
  try {
    return { file, manifest: JSON.parse(fs.readFileSync(file, 'utf8')) };
  } catch (err) {
    return { file, error: `JSON không đọc được: ${err.message}` };
  }
});

ipcMain.handle('workflow:open', async (_e, suitePath) => {
  const result = await dialog.showOpenDialog({
    title: 'Mở workflow manifest',
    defaultPath: suitePath || undefined,
    filters: [{ name: 'Workflow manifest', extensions: ['json'] }],
    properties: ['openFile'],
  });
  if (result.canceled || !result.filePaths[0]) return null;
  const file = result.filePaths[0];
  try {
    return { file, manifest: JSON.parse(fs.readFileSync(file, 'utf8')) };
  } catch (err) {
    return { file, error: `JSON không đọc được: ${err.message}` };
  }
});

ipcMain.handle('workflow:new', async (_e, suitePath) => {
  const template = path.join(
    suitePath, 'skills', 'data-academy-and-curriculum', 'assets', 'corpus-workflow-manifest.json'
  );
  const result = await dialog.showSaveDialog({
    title: 'Lưu workflow manifest mới',
    defaultPath: path.join(suitePath || os.homedir(), 'workflow-manifest.json'),
    filters: [{ name: 'Workflow manifest', extensions: ['json'] }],
  });
  if (result.canceled || !result.filePath) return null;
  let manifest;
  try {
    manifest = JSON.parse(fs.readFileSync(template, 'utf8'));
  } catch {
    manifest = {
      workflow_id: '', version: '1.0.0', objective: '', status: 'draft',
      workflow_risk_tier: 'R1-reviewed', current_task_id: '',
      tasks: [], transitions: [], claims: [], updated_at: '',
    };
  }
  fs.writeFileSync(result.filePath, JSON.stringify(manifest, null, 2) + '\n');
  return { file: result.filePath, manifest };
});

ipcMain.handle('workflow:save', (_e, { file, manifest }) => {
  try {
    fs.writeFileSync(file, JSON.stringify(manifest, null, 2) + '\n');
    return { ok: true };
  } catch (err) {
    return { ok: false, error: err.message };
  }
});

/** Run the suite's own validator. The app never decides whether a workflow is valid. */
/* Write a drafted evidence envelope next to the workflow it belongs to.
 *
 * The directory is the one the validator reads with --evidence-dir, so a draft becomes resolvable
 * the moment a person finishes it. The app refuses to overwrite: an envelope already on disk may
 * have been completed by hand, and silently replacing it would destroy the only part of the record
 * the app could not produce. */
ipcMain.handle('evidence:write', (_e, { file, envelope }) => {
  try {
    const dir = path.join(path.dirname(file), 'evidence');
    fs.mkdirSync(dir, { recursive: true });
    const out = path.join(dir, `${envelope.evidence_id}.json`);
    if (fs.existsSync(out)) return { ok: false, error: 'Đã có envelope trùng id; không ghi đè.', file: out };
    fs.writeFileSync(out, JSON.stringify(envelope, null, 2) + '\n');
    return { ok: true, file: out };
  } catch (err) {
    return { ok: false, error: err.message };
  }
});

ipcMain.handle('workflow:validate', (_e, { file, suitePath, mode }) => {
  const script = path.join(suitePath, 'skills', 'data-department-orchestrator', 'scripts', 'validate_workflow.py');
  const catalog = path.join(suitePath, 'task-catalog.json');
  if (!fs.existsSync(script)) return { ok: false, output: `Không thấy validate_workflow.py trong ${suitePath}` };
  const run = spawnSync('python3', [script, file, '--catalog', catalog, '--mode', mode || 'plan'], {
    encoding: 'utf8', timeout: 30000,
  });
  if (run.error) return { ok: false, output: String(run.error.message) };
  return { ok: run.status === 0, exit: run.status, output: (run.stdout || '') + (run.stderr || '') };
});

// ---- In-app run ------------------------------------------------------------
// `claude -p --output-format stream-json` emits one JSON object per line. The app parses those
// and renders them itself, so no terminal window is involved. It still runs the CLI, so it uses
// the existing login rather than a separate API key.
//
// Headless means no interactive permission prompt. The mode is the user's choice, surfaced in
// the UI, and it defaults to `plan` — Claude says what it would do and touches nothing.

const runs = new Map();

ipcMain.handle('run:start', (event, options) => {
  const { runId } = options;
  const send = (channel, payload) => {
    if (!event.sender.isDestroyed()) event.sender.send(channel, { runId, ...payload });
  };
  const started = claudeCore.startRun(options, {
    onEvent: (ev) => send('run:event', { event: ev }),
    onStderr: (text) => send('run:stderr', { text }),
    onDone: (result) => {
      runs.delete(runId);
      send('run:done', result);
    },
  });
  if (!started.ok) return { ok: false, error: started.error };
  runs.set(runId, started.child);
  return { ok: true };
});

ipcMain.handle('run:stop', (_e, runId) => {
  const child = runs.get(runId);
  if (!child) return { ok: false };
  child.kill('SIGTERM');
  runs.delete(runId);
  return { ok: true };
});
