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
 *  The app never runs the model itself and never edits the user's files. */
ipcMain.handle('session:launch', (_e, { folder, skillId, taskId, suitePath }) => {
  if (!folder || !fs.existsSync(folder)) return { ok: false, error: 'Thư mục không tồn tại' };

  const prompt = taskId
    ? `Use the ${skillId} skill and run the atomic task ${taskId} in this directory.`
    : `Use the ${skillId} skill for work in this directory. Route to the right atomic task by primary deliverable.`;

  const args = [];
  if (suitePath && fs.existsSync(path.join(suitePath, '.claude-plugin'))) {
    args.push('--plugin-dir', suitePath);
  }
  args.push(prompt);

  const terminals = [
    ['x-terminal-emulator', ['-e']],
    ['gnome-terminal', ['--working-directory=' + folder, '--']],
    ['konsole', ['--workdir', folder, '-e']],
    ['xfce4-terminal', ['--working-directory=' + folder, '-x']],
    ['xterm', ['-e']],
  ];

  for (const [bin, prefix] of terminals) {
    try {
      const child = spawn(bin, [...prefix, 'claude', ...args], {
        cwd: folder,
        detached: true,
        stdio: 'ignore',
      });
      child.unref();
      return { ok: true, terminal: bin };
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
