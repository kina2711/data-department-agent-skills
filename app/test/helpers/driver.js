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

/* A baseline is only worth having if the same build always produces it.
 *
 * The first grid baseline captured a card carrying a focus ring, because a click earlier in the
 * session had left focus on it; the next run captured the same card flat and the comparison
 * reported a real change that was really a stray highlight. Focus and hover are cleared before
 * every capture so a screenshot records the layout rather than the pointer's history. */
const CAPTURE_CSS = `
  /* Decorative blur rasterises differently depending on what the GPU was doing beforehand: the
     same build produced a stable picture when visual.test.js ran alone and a 0.6% difference on
     one card when the whole suite ran first, on a different card each time. A baseline cannot
     hold a value the renderer will not reproduce, so the decoration is flattened for the capture.
     Layout, spacing, colour and text -- everything a regression would actually show up in --
     are untouched. */
  .blob { filter: none !important; }
  *, *::before, *::after { transition: none !important; animation: none !important; }
`;

async function settleForCapture(win) {
  await win.webContents.insertCSS(CAPTURE_CSS);
  await win.webContents.executeJavaScript(`(() => {
    if (document.activeElement && document.activeElement !== document.body) {
      document.activeElement.blur();
    }
    // Chromium keeps the last hovered element hot until the pointer moves; a move to the corner
    // outside any card resets it.
    document.dispatchEvent(new MouseEvent('mousemove', {
      bubbles: true, clientX: 0, clientY: 0 }));
    return true; })()`, true);
  await new Promise((r) => setTimeout(r, 120));
}

async function handle(cmd, win) {
  if (cmd.op === 'eval') {
    // executeJavaScript hands back the expression's value over IPC, and anything that is not
    // structured-cloneable — a function, a DOM node — fails with "An object could not be cloned",
    // which points at the transport rather than at the test. Serialising inside the page turns
    // that into a value the test can read, or an explicit marker when there is nothing to read.
    const wrapped = `(() => { const v = (${cmd.expression});
      try { return JSON.stringify(v === undefined ? null : v); }
      catch { return JSON.stringify(String(v)); } })()`;
    const raw = await win.webContents.executeJavaScript(wrapped, true);
    return JSON.parse(raw);
  }
  if (cmd.op === 'settle') return new Promise((r) => setTimeout(() => r(true), cmd.ms));
  if (cmd.op === 'resize') { win.setSize(cmd.width, cmd.height); return true; }
  if (cmd.op === 'shot') {
    await settleForCapture(win);
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
  await settleForCapture(win);
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
