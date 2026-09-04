'use strict';
const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const { spawn, spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { readSuite, contractCache } = require('./suite');

// The suite is read, never written. The app is a launcher; Claude Code does the work.
const CONFIG_PATH = path.join(app.getPath('userData'), 'config.json');

function readConfig() {
  try {
    return JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
  } catch {
    return { suitePath: '', recentFolders: [] };
  }
}

function writeConfig(cfg) {
  fs.mkdirSync(path.dirname(CONFIG_PATH), { recursive: true });
  fs.writeFileSync(CONFIG_PATH, JSON.stringify(cfg, null, 2));
}

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

  const prompt = taskId
    ? `Use the ${skillId} skill and run the atomic task ${taskId} in this directory.`
    : `Use the ${skillId} skill for work in this directory. Route to the right atomic task by primary deliverable.`;

  const argv = ['claude'];
  if (suitePath && fs.existsSync(path.join(suitePath, '.claude-plugin'))) {
    argv.push('--plugin-dir', suitePath);
  }
  argv.push(prompt);

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

ipcMain.handle('run:start', (event, { runId, folder, prompt, suitePath, permissionMode, model }) => {
  if (!folder || !fs.existsSync(folder)) return { ok: false, error: 'Thư mục không tồn tại' };
  if (!String(prompt || '').trim()) return { ok: false, error: 'Prompt rỗng' };

  const argv = ['-p', '--output-format', 'stream-json', '--verbose'];
  if (suitePath && fs.existsSync(path.join(suitePath, '.claude-plugin'))) {
    argv.push('--plugin-dir', suitePath);
  }
  argv.push('--permission-mode', permissionMode || 'plan');
  // The task's declared tier decides this; an empty model means the CLI's own default applies,
  // which is the honest outcome for a task whose tier nobody has set.
  if (model) argv.push('--model', String(model));
  argv.push(String(prompt));

  let child;
  try {
    child = spawn('claude', argv, { cwd: folder, stdio: ['ignore', 'pipe', 'pipe'] });
  } catch (err) {
    return { ok: false, error: `Không chạy được claude: ${err.message}` };
  }
  runs.set(runId, child);

  const send = (channel, payload) => {
    if (!event.sender.isDestroyed()) event.sender.send(channel, { runId, ...payload });
  };

  let buffer = '';
  child.stdout.on('data', (chunk) => {
    buffer += chunk.toString('utf8');
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed) continue;
      try {
        send('run:event', { event: JSON.parse(trimmed) });
      } catch {
        // Not every line is JSON when the CLI writes a notice; show it rather than drop it.
        send('run:event', { event: { type: 'raw', text: trimmed } });
      }
    }
  });

  child.stderr.on('data', (chunk) => send('run:stderr', { text: chunk.toString('utf8') }));

  child.on('error', (err) => {
    runs.delete(runId);
    send('run:done', { code: -1, error: err.message });
  });
  child.on('close', (code) => {
    runs.delete(runId);
    if (buffer.trim()) {
      try {
        send('run:event', { event: JSON.parse(buffer.trim()) });
      } catch {
        send('run:event', { event: { type: 'raw', text: buffer.trim() } });
      }
    }
    send('run:done', { code });
  });

  return { ok: true };
});

ipcMain.handle('run:stop', (_e, runId) => {
  const child = runs.get(runId);
  if (!child) return { ok: false };
  child.kill('SIGTERM');
  runs.delete(runId);
  return { ok: true };
});
