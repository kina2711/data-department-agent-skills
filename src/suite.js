'use strict';
const fs = require('fs');
const path = require('path');

/** Minimal reader for the manifest's flat `key: "value"` and `- key: value` shape.
 *  A full YAML parser is a dependency this app does not otherwise need. */
function parseSuiteManifest(text) {
  const roles = [];
  let suiteVersion = '';
  let current = null;
  for (const raw of text.split('\n')) {
    const line = raw.trimEnd();
    const version = line.match(/^version:\s*"?([^"]+)"?$/);
    if (version) suiteVersion = version[1];
    const start = line.match(/^\s*-\s*skill:\s*"?([^"]+)"?$/);
    if (start) {
      current = { skill: start[1] };
      roles.push(current);
      continue;
    }
    if (!current) continue;
    const field = line.match(/^\s+(display_name|task_count):\s*"?([^"]+)"?$/);
    if (field) current[field[1]] = field[1] === 'task_count' ? Number(field[2]) : field[2];
  }
  return { suiteVersion, roles };
}

function readSuite(suitePath) {
  const manifestPath = path.join(suitePath, 'suite-manifest.yaml');
  const catalogPath = path.join(suitePath, 'task-catalog.json');
  if (!fs.existsSync(manifestPath)) {
    return { error: `Not a suite directory: no suite-manifest.yaml in ${suitePath}` };
  }
  const { suiteVersion, roles } = parseSuiteManifest(fs.readFileSync(manifestPath, 'utf8'));

  // Vietnamese guides are the human routing layer. They are optional: an older suite still
  // renders, just without them.
  let guides = {};
  try {
    guides = JSON.parse(
      fs.readFileSync(path.join(suitePath, 'docs', 'huong-dan-skill.vi.json'), 'utf8')
    ).skills || {};
  } catch {
    guides = {};
  }

  // Task-level metadata is optional; the grid degrades to names and counts without it.
  let tasks = [];
  if (fs.existsSync(catalogPath)) {
    try {
      tasks = JSON.parse(fs.readFileSync(catalogPath, 'utf8'));
    } catch {
      tasks = [];
    }
  }
  const prefixOf = new Map();
  for (const t of tasks) {
    const prefix = t.id.split('-', 1)[0];
    if (!prefixOf.has(prefix)) prefixOf.set(prefix, []);
    prefixOf.get(prefix).push(t);
  }

  const skills = roles.map((role) => {
    const skillDir = path.join(suitePath, 'skills', role.skill);
    let description = '';
    try {
      const skillMd = fs.readFileSync(path.join(skillDir, 'SKILL.md'), 'utf8');
      const match = skillMd.match(/^description:\s*(.+)$/m);
      if (match) description = match[1].trim();
    } catch {
      /* a skill without SKILL.md still shows its name and count */
    }
    const owned = tasks.filter((t) => taskBelongsTo(t.id, role.skill, suitePath));
    return {
      id: role.skill,
      name: role.display_name || role.skill,
      description,
      guide: guides[role.skill] || null,
      taskCount: role.task_count || owned.length,
      tasks: owned.map((t) => ({
        id: t.id,
        goal: t.goal,
        output: t.output,
        risk: t.risk_tier,
        modelTier: t.model_tier || '',
      })),
    };
  });
  return { suiteVersion, skills, taskTotal: tasks.length };
}

// Task ids carry a role prefix, not the skill directory name, so resolve through the
// contract files that the skill actually ships.
const contractCache = new Map();
function taskBelongsTo(taskId, skill, suitePath) {
  if (!contractCache.has(skill)) {
    const dir = path.join(suitePath, 'skills', skill, 'references', 'tasks');
    let names = [];
    try {
      names = fs.readdirSync(dir).map((f) => f.replace(/\.md$/, ''));
    } catch {
      names = [];
    }
    contractCache.set(skill, new Set(names));
  }
  return contractCache.get(skill).has(taskId);
}

module.exports = { parseSuiteManifest, readSuite, contractCache };
