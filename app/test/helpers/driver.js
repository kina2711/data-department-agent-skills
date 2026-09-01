'use strict';

/* Electron main process for tests: boots the real window, then serves one command per line.
 *
 * It loads the app's own main.js so every IPC handler under test is the shipped one. Stubs named
 * in DA_TEST_STUBS are registered afterwards and win, because ipcMain.handle replaces a handler
 * rather than stacking on it — that is how a test avoids a real file dialog or a real model call
 * without the app knowing it is under test. */

const { app, BrowserWindow, ipcMain, nativeImage } = require('electron');
const net = require('node:net');
const path = require('node:path');
const fs = require('node:fs');

const PORT = Number(process.env.DA_TEST_PORT);
const STUBS = JSON.parse(process.env.DA_TEST_STUBS || '{}');

app.disableHardwareAcceleration();
app.commandLine.appendSwitch('disable-gpu');

// The app's main.js creates its own window on ready; load it and take the window it made.
require(path.resolve(__dirname, '..', '..', 'src', 'main.js'));

for (const [channel, value] of Object.entries(STUBS)) {
  ipcMain.removeHandler(channel);
  ipcMain.handle(channel, () => value);
}

function windowOf() {
  const [w] = BrowserWindow.getAllWindows();
  return w;
}

app.whenReady().then(async () => {
  // main.js opens the window inside its own whenReady; wait for it to exist.
  const deadline = Date.now() + 15000;
  while (!windowOf() && Date.now() < deadline) await new Promise((r) => setTimeout(r, 50));
  const win = windowOf();
  if (!win) {
    console.error('no window was created by src/main.js');
    app.exit(2);
    return;
  }
  win.setSize(1280, 900);
  if (!win.webContents.isLoading()) { /* already there */ }
  else await new Promise((r) => win.webContents.once('did-finish-load', r));
  await new Promise((r) => setTimeout(r, 400));

  const server = net.createServer((socket) => {
    let buffer = '';
    socket.on('data', async (chunk) => {
      buffer += chunk;
      let cut;
      while ((cut = buffer.indexOf('\n')) >= 0) {
        const line = buffer.slice(0, cut);
        buffer = buffer.slice(cut + 1);
        let reply;
        try {
          reply = { value: await handle(JSON.parse(line), win) };
        } catch (err) {
          reply = { error: String((err && err.message) || err) };
        }
        socket.write(JSON.stringify(reply) + '\n');
      }
    });
  });
  server.listen(PORT, '127.0.0.1');
});

async function handle(cmd, win) {
  if (cmd.op === 'eval') return win.webContents.executeJavaScript(cmd.expression, true);
  if (cmd.op === 'settle') return new Promise((r) => setTimeout(() => r(true), cmd.ms));
  if (cmd.op === 'resize') { win.setSize(cmd.width, cmd.height); return true; }
  if (cmd.op === 'shot') {
    const image = await win.webContents.capturePage();
    fs.mkdirSync(path.dirname(cmd.file), { recursive: true });
    fs.writeFileSync(cmd.file, image.toPNG());
    return cmd.file;
  }
  if (cmd.op === 'compare') return compare(cmd, win);
  if (cmd.op === 'quit') { setTimeout(() => app.exit(0), 40); return true; }
  throw new Error(`unknown op ${cmd.op}`);
}

/* Visual comparison without a PNG library.
 *
 * Electron already decodes PNG, so the baseline is read back through nativeImage and both sides
 * are compared as raw BGRA. A per-channel threshold absorbs font antialiasing, which differs
 * between runs on the same machine and would otherwise fail every comparison; the ratio threshold
 * is what decides, because a handful of edge pixels is not a layout change. */
const CHANNEL_TOLERANCE = 16;
const RATIO_LIMIT = 0.004;

async function compare(cmd, win) {
  const shot = await win.webContents.capturePage();
  const size = shot.getSize();
  if (!fs.existsSync(cmd.baseline)) {
    fs.mkdirSync(path.dirname(cmd.baseline), { recursive: true });
    fs.writeFileSync(cmd.baseline, shot.toPNG());
    return { created: true, width: size.width, height: size.height };
  }
  const base = nativeImage.createFromPath(cmd.baseline);
  const bs = base.getSize();
  if (bs.width !== size.width || bs.height !== size.height) {
    writeActual(cmd, shot);
    return { created: false, sizeMismatch: true, baseline: bs, actual: size, ratio: 1 };
  }
  const a = shot.toBitmap();
  const b = base.toBitmap();
  let differing = 0;
  for (let i = 0; i < a.length; i += 4) {
    if (Math.abs(a[i] - b[i]) > CHANNEL_TOLERANCE
      || Math.abs(a[i + 1] - b[i + 1]) > CHANNEL_TOLERANCE
      || Math.abs(a[i + 2] - b[i + 2]) > CHANNEL_TOLERANCE) differing += 1;
  }
  const pixels = a.length / 4;
  const ratio = differing / pixels;
  if (ratio > RATIO_LIMIT) writeActual(cmd, shot);
  return { created: false, differing, pixels, ratio, limit: RATIO_LIMIT, width: size.width, height: size.height };
}

function writeActual(cmd, shot) {
  const out = cmd.baseline.replace(/\.png$/, '.actual.png');
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.writeFileSync(out, shot.toPNG());
}
