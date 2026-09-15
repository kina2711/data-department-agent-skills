'use strict';

/* Which run was left unfinished, where, and under which skill.
 *
 * A run outlives the process that started it: `claude` keeps the conversation, and `--resume`
 * reopens it. What neither keeps is the pointer — after a reboot the session id is gone from the
 * terminal scrollback and out of the person's head, and a conversation nobody can name is a
 * conversation nobody can continue.
 *
 * So the store is one line per working folder and skill: the id, how far it got, and the last
 * thing it said. Both doors read and write it, because a session started in the app and a session
 * started from the terminal are the same session, and only one of them knowing about it is how a
 * person ends up starting the work twice.
 *
 * What resuming restores is the model's memory of the exchange, not the transcript on screen. The
 * distinction matters enough to keep in the wording everywhere this is offered: the work carries
 * over, the log does not come back.
 */

const fs = require('fs');
const path = require('path');
const config = require('./config');

const LIMIT = 60;

/* Overridable because Chromium locks a userData directory, so two app instances cannot share one
 * — and a test for "the session survived a restart" is exactly two instances that must see the
 * same store. */
function storePath(explicit) {
  if (explicit) return explicit;
  if (process.env.DA_SESSIONS_PATH) return process.env.DA_SESSIONS_PATH;
  return path.join(config.defaultDir(), 'sessions.json');
}

function read(file) {
  try {
    const doc = JSON.parse(fs.readFileSync(storePath(file), 'utf8'));
    return doc && typeof doc === 'object' && doc.sessions ? doc : { version: 1, sessions: {} };
  } catch {
    return { version: 1, sessions: {} };
  }
}

const key = (folder, skillId) => `${folder || ''}::${skillId || ''}`;

function get(folder, skillId, file) {
  return read(file).sessions[key(folder, skillId)] || null;
}

/** Every stored session, newest first — what a person needs after a reboot. */
function list(file) {
  return Object.values(read(file).sessions)
    .sort((a, b) => String(b.updatedAt).localeCompare(String(a.updatedAt)));
}

function save(record, file) {
  if (!record || !record.sessionId || !record.folder) {
    return { ok: false, error: 'thiếu session hoặc thư mục' };
  }
  const doc = read(file);
  const previous = doc.sessions[key(record.folder, record.skillId)];
  doc.sessions[key(record.folder, record.skillId)] = {
    sessionId: record.sessionId,
    folder: record.folder,
    skillId: record.skillId || '',
    skillName: record.skillName || '',
    taskId: record.taskId || (previous && previous.taskId) || '',
    mode: record.mode || 'plan',
    turns: Number(record.turns) || 1,
    lastText: String(record.lastText || '').slice(0, 400),
    updatedAt: new Date().toISOString(),
  };
  // Oldest first, so the cap drops what nobody has touched.
  const entries = Object.entries(doc.sessions)
    .sort((a, b) => String(b[1].updatedAt).localeCompare(String(a[1].updatedAt)))
    .slice(0, LIMIT);
  doc.sessions = Object.fromEntries(entries);
  const target = storePath(file);
  try {
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.writeFileSync(target, JSON.stringify(doc, null, 2) + '\n');
    return { ok: true };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}

function forget(folder, skillId, file) {
  const doc = read(file);
  delete doc.sessions[key(folder, skillId)];
  const target = storePath(file);
  try {
    fs.writeFileSync(target, JSON.stringify(doc, null, 2) + '\n');
    return { ok: true };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}

/* Earlier builds wrote this beside the Electron profile, whose directory is named after the
 * product. Adopt those once so a session started before the split is still offered afterwards —
 * losing it would mean the one feature that exists to survive a restart did not survive an
 * upgrade. Never overwrites a store that already holds sessions. */
function migrate(file) {
  if (process.env.DA_SESSIONS_PATH) return { adopted: '', count: 0 };
  const target = storePath(file);
  if (Object.keys(read(target).sessions).length) return { adopted: '', count: 0 };
  /* Merge every legacy store rather than picking one.
   *
   * Picking the most recently modified adopted a development profile that a test run had just
   * touched, and left the real unfinished work — two days older and in a different directory —
   * behind. There is no need to choose: sessions are keyed by folder and skill, so the union is
   * well defined, and the newer record wins where both stores know the same key. */
  const merged = {};
  const adopted = [];
  for (const file of config.legacyCandidates().map((c) => path.join(path.dirname(c), 'sessions.json'))) {
    if (file === target || !fs.existsSync(file)) continue;
    try {
      const doc = JSON.parse(fs.readFileSync(file, 'utf8'));
      const found = (doc && doc.sessions) || {};
      if (!Object.keys(found).length) continue;
      adopted.push(file);
      for (const [k, v] of Object.entries(found)) {
        const seen = merged[k];
        if (!seen || String(v.updatedAt || '') > String(seen.updatedAt || '')) merged[k] = v;
      }
    } catch {
      /* an unreadable legacy store is not worth failing over */
    }
  }
  const count = Object.keys(merged).length;
  if (!count) return { adopted: '', count: 0 };
  const entries = Object.entries(merged)
    .sort((a, b) => String(b[1].updatedAt).localeCompare(String(a[1].updatedAt)))
    .slice(0, LIMIT);
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, JSON.stringify({ version: 1, sessions: Object.fromEntries(entries) }, null, 2) + '\n');
  return { adopted: adopted.join(', '), count };
}

module.exports = { storePath, read, list, get, save, forget, migrate, key, LIMIT };
