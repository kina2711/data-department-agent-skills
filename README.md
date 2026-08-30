# Data Agent

A local launcher for the [Data Department agent skills](../data-department-agent-skills) suite.
Pick a skill, pick a working folder, and it opens a Claude Code session in that folder primed
with the skill.

It is a **launcher, not a client**. Claude Code does every piece of the work; this app chooses
what to point it at. That means it uses your existing Claude Code login and costs no separate
API billing.

## What it reads

The suite directory, read-only:

| File | Used for |
|---|---|
| `suite-manifest.yaml` | version, skill list, display names, task counts |
| `skills/<skill>/SKILL.md` | the description shown on each card |
| `task-catalog.json` | task ids, goals, outputs, risk tier, model tier |
| `skills/<skill>/references/tasks/` | which tasks belong to which skill |

It never writes to the suite and never edits your project files.

## Running it

```bash
npm install
npm start
```

**If it exits immediately with `Cannot read properties of undefined (reading 'getPath')`**, the
shell has `ELECTRON_RUN_AS_NODE=1` set — VS Code's integrated terminal exports it, and it makes
Electron run the entry file as a plain Node script with no `app` object. Launch from a normal
terminal, or clear it:

```bash
env -u ELECTRON_RUN_AS_NODE npm start
```

## Building an installer

```bash
npm run dist    # AppImage + .deb in dist/
```

`dist/Data Agent-0.1.0.AppImage` runs with no install — mark it executable and
double-click. `dist/app-data-agent_0.1.0_amd64.deb` installs to `/opt` and registers a
desktop entry, so the app appears in the applications menu with its icon:

```bash
sudo dpkg -i dist/app-data-agent_0.1.0_amd64.deb
```

Both are Linux x64. macOS and Windows targets need their own build hosts and are untested.

## First run

Click **Chọn thư mục suite** and point it at the directory containing `suite-manifest.yaml`.
The choice is remembered in the app's user-data directory, alongside recent working folders.

## Design notes

- Content Security Policy is `default-src 'none'` with `style-src 'self'`. No inline styles
  anywhere, which is why card colours come from a fixed palette of classes rather than a
  computed hue.
- The renderer has no Node access. Everything it needs crosses a named `contextBridge` surface
  in `preload.js`.
- `src/suite.js` has no Electron dependency, so the suite-reading logic can be exercised with
  plain `node` without booting a window.

## Limits

- Linux only so far: the launcher looks for `x-terminal-emulator`, `gnome-terminal`, `konsole`,
  `xfce4-terminal` then `xterm`. macOS and Windows need their own branch.
- Launching writes a short script to the OS temp directory and runs that, rather than putting the
  prompt on the terminal's command line. Terminals disagree about how `-e` parses its remainder,
  prompts contain quotes, and a script can hold the window open so a failure to start is readable
  instead of a window that blinks and disappears.
- Model tier comes from the suite's own catalog. It is a recommendation the contract carries,
  not something this app enforces at runtime.
