'use strict';

/* Boot the real app in Electron and talk to its renderer.
 *
 * Two things this deliberately does not do. It does not stub the DOM with a library: the bugs this
 * app has produced were a content-security policy blocking a style, a replace() whose anchor had
 * moved, and an element id that no longer existed — none of which a simulated DOM would have
 * noticed. And it does not stub the preload bridge wholesale; it replaces only the handlers a test
 * names, so anything unstubbed still reaches the real main process and fails loudly if it breaks.
 *
 * Offscreen rendering keeps it headless. Screenshots come from the same window as the assertions,
 * so a visual baseline and a DOM assertion can never disagree about which build they saw. */

const { spawn } = require('node:child_process');
const path = require('node:path');
const net = require('node:net');

const APP = path.resolve(__dirname, '..', '..');
const ELECTRON = path.join(APP, 'node_modules', 'electron', 'dist', 'electron');

async function freePort() {
  return new Promise((resolve, reject) => {
    const srv = net.createServer();
    srv.on('error', reject);
    srv.listen(0, '127.0.0.1', () => {
      const { port } = srv.address();
      srv.close(() => resolve(port));
    });
  });
}

/** Start the app under a driver that accepts one JSON command per line and answers on the socket. */
async function open({ stubs = {}, width = 1280, height = 900 } = {}) {
  const port = await freePort();
  const env = { ...process.env, DA_TEST_PORT: String(port), DA_TEST_STUBS: JSON.stringify(stubs) };
  delete env.ELECTRON_RUN_AS_NODE;
  const child = spawn(ELECTRON, [path.join(__dirname, 'driver.js'), '--no-sandbox'], {
    cwd: APP, env, stdio: ['ignore', 'pipe', 'pipe'],
  });

  const noise = [];
  child.stdout.on('data', (d) => noise.push(String(d)));
  child.stderr.on('data', (d) => noise.push(String(d)));

  const socket = await connect(port, child, noise);
  let pending = null;
  let buffer = '';
  socket.on('data', (chunk) => {
    buffer += chunk;
    let cut;
    while ((cut = buffer.indexOf('\n')) >= 0) {
      const line = buffer.slice(0, cut);
      buffer = buffer.slice(cut + 1);
      if (pending) {
        const settle = pending;
        pending = null;
        const msg = JSON.parse(line);
        if (msg.error) settle.reject(new Error(msg.error));
        else settle.resolve(msg.value);
      }
    }
  });

  const send = (command) => new Promise((resolve, reject) => {
    if (pending) return reject(new Error('one command at a time'));
    pending = { resolve, reject };
    socket.write(JSON.stringify(command) + '\n');
  });

  return {
    /** Evaluate an expression in the renderer and return its value. */
    eval: (expression) => send({ op: 'eval', expression }),
    click: (selector) => send({ op: 'eval', expression:
      `(() => { const el = document.querySelector(${JSON.stringify(selector)});
        if (!el) throw new Error('no element ' + ${JSON.stringify(selector)});
        el.click(); return true; })()` }),
    text: (selector) => send({ op: 'eval', expression:
      `(document.querySelector(${JSON.stringify(selector)}) || {}).textContent || null` }),
    visible: (selector) => send({ op: 'eval', expression:
      `(() => { const el = document.querySelector(${JSON.stringify(selector)});
        return !!el && !el.hidden && el.offsetParent !== null; })()` }),
    // Rendered is not the same as seen. This one asks whether the element is actually inside the
    // viewport, which is what a person means by "did the button do anything" -- an earlier version
    // of this helper answered yes for a panel that had rendered a full screen below the fold.
    onScreen: (selector) => send({ op: 'eval', expression:
      `(() => { const el = document.querySelector(${JSON.stringify(selector)});
        if (!el || el.hidden || el.offsetParent === null) return false;
        const r = el.getBoundingClientRect();
        return r.height > 0 && r.top < innerHeight && r.bottom > 0; })()` }),
    shot: (file) => send({ op: 'shot', file }),
    compare: (baseline) => send({ op: 'compare', baseline }),
    resize: (w, h) => send({ op: 'resize', width: w, height: h }),
    settle: (ms = 120) => send({ op: 'settle', ms }),
    noise: () => noise.join(''),
    close: async () => {
      try { await send({ op: 'quit' }); } catch { /* the app going away is the point */ }
      socket.destroy();
      child.kill('SIGTERM');
    },
    width, height,
  };
}

function connect(port, child, noise) {
  const deadline = Date.now() + 30000;
  return new Promise((resolve, reject) => {
    const attempt = () => {
      if (child.exitCode !== null) {
        return reject(new Error(`app exited ${child.exitCode}\n${noise.join('')}`));
      }
      if (Date.now() > deadline) return reject(new Error(`app never listened\n${noise.join('')}`));
      const s = net.connect(port, '127.0.0.1');
      s.once('connect', () => resolve(s));
      s.once('error', () => setTimeout(attempt, 150));
    };
    attempt();
  });
}

module.exports = { open, APP };
