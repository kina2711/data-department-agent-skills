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
  let jobs = [];
  let searchIndex = new Map();
  try {
    guides = JSON.parse(
      fs.readFileSync(path.join(suitePath, 'docs', 'huong-dan-skill.vi.json'), 'utf8')
    ).skills || {};
  } catch {
    guides = {};
  }
  try {
    jobs = JSON.parse(
      fs.readFileSync(path.join(suitePath, 'docs', 'cong-viec.vi.json'), 'utf8')
    ).cong_viec || [];
  } catch {
    jobs = [];
  }
  // The generated retrieval index carries keywords per task, so search matches a task by what it
  // is about rather than only by the characters in its id.
  try {
    const idx = JSON.parse(
      fs.readFileSync(path.join(suitePath, 'docs', 'retrieval-index.json'), 'utf8')
    );
    for (const t of idx.tasks || []) searchIndex.set(t.id, t.keywords || []);
  } catch {
    searchIndex = new Map();
  }

  /* The skill atlas groups every skill into the rollout wave that skill-map section 40 declares,
   * and that grouping is the only real structure the suite has for 33 skills. Reading it lets the
   * grid show that structure instead of an alphabetical wall, and colour can then carry meaning
   * rather than a hash of the skill id. Absent atlas, the grid falls back to one ungrouped list. */
  let waveOf = new Map();
  let waveOrder = [];
  try {
    const atlas = JSON.parse(
      fs.readFileSync(path.join(suitePath, 'docs', 'skill-atlas.json'), 'utf8')
    );
    for (const wave of atlas.waves || []) {
      waveOrder.push({ wave: wave.wave, title: wave.title, tone: wave.tone });
      for (const s of wave.skills || []) waveOf.set(s.skill, wave.wave);
    }
  } catch {
    waveOf = new Map();
    waveOrder = [];
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
      jobs: jobs.filter((j) => j.skill === role.skill),
      taskCount: role.task_count || owned.length,
      wave: waveOf.get(role.skill) || '',
      tasks: owned.map((t) => ({
        id: t.id,
        keywords: searchIndex.get(t.id) || [],
        goal: t.goal,
        output: t.output,
        risk: t.risk_tier,
        modelTier: t.model_tier || '',
      })),
    };
  });
  return { suiteVersion, skills, taskTotal: tasks.length, waves: waveOrder };
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
