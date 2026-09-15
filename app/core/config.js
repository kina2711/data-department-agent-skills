'use strict';

/* Where the suite is, and which folders were used recently.
 *
 * The app kept this in Electron's userData directory, which only Electron can name. Once the CLI
 * is a real door, the pair have to agree: pick a suite in one and the other must already know.
 * So the path is computed the same way Electron computes it, and the app passes its own value in
 * rather than each side guessing.
 */

const fs = require('fs');
const os = require('os');
const path = require('path');

const APP_NAME = 'data-agent';

/** Electron's userData path, derived without requiring Electron. */
function defaultDir() {
  if (process.env.DA_CONFIG_DIR) return process.env.DA_CONFIG_DIR;
  if (process.platform === 'darwin') {
    return path.join(os.homedir(), 'Library', 'Application Support', APP_NAME);
  }
  if (process.platform === 'win32') {
    return path.join(process.env.APPDATA || path.join(os.homedir(), 'AppData', 'Roaming'), APP_NAME);
  }
  return path.join(process.env.XDG_CONFIG_HOME || path.join(os.homedir(), '.config'), APP_NAME);
}

const EMPTY = { suitePath: '', recentFolders: [] };

function read(dir) {
  try {
    return { ...EMPTY, ...JSON.parse(fs.readFileSync(path.join(dir || defaultDir(), 'config.json'), 'utf8')) };
  } catch {
    return { ...EMPTY };
  }
}

function write(cfg, dir) {
  const target = path.join(dir || defaultDir(), 'config.json');
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, JSON.stringify(cfg, null, 2));
  return target;
}

/**
 * The suite to work against, in order of how explicit the answer is: an argument beats the
 * environment, which beats the saved choice, which beats the directory you are standing in.
 * Returns '' rather than guessing when none of them holds a suite.
 */
function resolveSuite({ explicit, dir, cwd } = {}) {
  const candidates = [explicit, process.env.DA_SUITE, read(dir).suitePath, cwd || process.cwd()];
  for (const candidate of candidates) {
    if (candidate && fs.existsSync(path.join(candidate, 'suite-manifest.yaml'))) {
      return path.resolve(candidate);
    }
  }
  return '';
}

/* Where earlier versions kept the same file.
 *
 * The app stored this under Electron's userData directory, whose name changed with the product
 * name — so a working install had a suite path and three recent folders in `~/.config/Data Agent`
 * while a fresh CLI looked at `~/.config/data-agent` and saw nothing. Adopting the newest of them
 * once beats asking the user to pick their folders again, and beats a CLI that quietly disagrees
 * with the app about which suite is current. */
const LEGACY_DIRS = ['Data Agent', 'data-department-studio', 'Electron'];

function legacyCandidates() {
  const base = process.platform === 'darwin'
    ? path.join(os.homedir(), 'Library', 'Application Support')
    : (process.env.XDG_CONFIG_HOME || path.join(os.homedir(), '.config'));
  return LEGACY_DIRS.map((name) => path.join(base, name, 'config.json'));
}

/**
 * Adopt the newest legacy config when this one has nothing, and return what was adopted.
 * Never overwrites: a config that already names a suite is the current answer and stays.
 */
function migrate(dir) {
  /* DA_CONFIG_DIR means "this exact directory is the config" — nothing is adopted from elsewhere.
   * Without that, a test pointed at its own empty directory still reached out to the developer's
   * real `~/.config/Data Agent`, adopted the suite saved there, and six tests asserting "no suite
   * connected" saw one. An override that only half overrides is worse than none. */
  if (process.env.DA_CONFIG_DIR) return { adopted: '', config: read(dir) };
  const target = path.join(dir || defaultDir(), 'config.json');
  const current = read(dir);
  if (current.suitePath || (current.recentFolders || []).length) return { adopted: '', config: current };
  const found = legacyCandidates()
    .filter((file) => fs.existsSync(file) && file !== target)
    .map((file) => ({ file, at: fs.statSync(file).mtimeMs }))
    .sort((a, b) => b.at - a.at);
  for (const { file } of found) {
    try {
      const doc = JSON.parse(fs.readFileSync(file, 'utf8'));
      if (!doc || (!doc.suitePath && !(doc.recentFolders || []).length)) continue;
      const merged = { ...EMPTY, ...doc };
      write(merged, dir);
      return { adopted: file, config: merged };
    } catch {
      /* an unreadable legacy file is not worth failing over */
    }
  }
  return { adopted: '', config: current };
}

module.exports = { APP_NAME, defaultDir, read, write, resolveSuite, migrate, legacyCandidates, EMPTY };
