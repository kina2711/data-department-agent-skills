'use strict';

const state = {
  suitePath: '',
  suiteVersion: '',
  skills: [],
  filterTier: '',
  query: '',
  openSkill: null,
  catalog: new Map(),
  job: null,
  jobPrompt: '',
  jobMissing: [],
  selectedTask: null,
  folder: '',
};

const $ = (id) => document.getElementById(id);


// Deterministic pastel per skill, so a card keeps the same colour between launches.
// Returns a class index rather than a colour: inline styles are blocked by the page CSP.
function notice(text, kind) {
  $('notice').innerHTML = '';
  if (!text) return;
  const el = document.createElement('div');
  el.className = `notice notice-${kind || 'err'}`;
  el.textContent = text;
  $('notice').append(el);
}

// A query matches a task by its id, its Vietnamese goal, or the keywords the retrieval index
// derived from both — so "cache" finds the semantic cache task without knowing its id.
function taskMatches(task, q) {
  if (!q) return true;
  if (task.id.includes(q)) return true;
  if ((task.goal || '').toLowerCase().includes(q)) return true;
  return (task.keywords || []).some((k) => k.includes(q));
}

function matches(skill) {
  const q = state.query.trim().toLowerCase();
  const tier = state.filterTier;
  const tierOk = !tier || skill.tasks.some((t) => t.modelTier === tier);
  if (!tierOk) return false;
  if (!q) return true;
  if (skill.name.toLowerCase().includes(q) || skill.id.includes(q)) return true;
  return skill.tasks.some((t) => taskMatches(t, q));
}


// Suggest a skill from a plain-language purpose, scored against the retrieval index's keywords.
// Every skill's tasks carry them, so "pipeline chạy lại bị trùng" reaches data-engineering
// through the words in its task goals rather than through its English description.
const SUGGEST_STOP = new Set(
  ('tôi muốn cần làm gì cho về của và với một các là có không thì nào bị ra vào theo khi ' +
   'the for and with from into that this a an of to my i want need make').split(' ')
);

function purposeTerms(text) {
  return [...new Set(
    text.toLowerCase().split(/[^\p{L}\p{N}]+/u).filter((w) => w.length >= 3 && !SUGGEST_STOP.has(w))
  )];
}

function suggestSkills(text, limit = 4) {
  const terms = purposeTerms(text);
  if (!terms.length) return [];
  const scored = [];
  for (const skill of state.skills) {
    let score = 0;
    const why = new Map();
    for (const task of skill.tasks) {
      const hay = [task.id, (task.goal || '').toLowerCase(), ...(task.keywords || [])];
      let taskScore = 0;
      for (const term of terms) {
        if (hay.some((h) => h.includes(term))) {
          taskScore += 1;
          why.set(term, (why.get(term) || 0) + 1);
        }
      }
      // A task matching several terms is stronger evidence than several matching one.
      score += taskScore * taskScore;
    }
    if (score > 0) scored.push({ skill, score, terms: [...why.keys()].slice(0, 4) });
  }
  scored.sort((a, b) => b.score - a.score);
  return scored.slice(0, limit);
}

function renderSuggestions() {
  const box = $('suggestions');
  const text = $('purpose').value.trim();
  $('purposeClear').hidden = !text;
  box.innerHTML = '';
  if (!text) return;
  if (!state.skills.length) {
    box.innerHTML = '<p class="suggest-empty">Chưa nối suite.</p>';
    return;
  }
  const hits = suggestSkills(text);
  if (!hits.length) {
    box.innerHTML = '<p class="suggest-empty">Không khớp skill nào. Thử mô tả bằng từ khác, hoặc chọn thẳng ở lưới bên dưới.</p>';
    return;
  }
  hits.forEach((hit, i) => {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'suggest-hit';
    const rank = document.createElement('span');
    rank.className = 'suggest-rank';
    rank.textContent = `#${i + 1}`;
    const wrap = document.createElement('span');
    const name = document.createElement('span');
    name.className = 'suggest-name';
    name.textContent = hit.skill.name;
    const why = document.createElement('span');
    why.className = 'suggest-why';
    why.textContent = hit.terms.length ? ` khớp: ${hit.terms.join(', ')}` : '';
    wrap.append(name, why);
    b.append(rank, wrap);
    b.addEventListener('click', () => openDrawer(hit.skill));
    box.append(b);
  });
}

/* The grid, grouped by the rollout wave each skill belongs to.
 *
 * Thirty-three skills in one alphabetical wall gives a reader nothing to navigate by, so the
 * grouping comes from skill-map section 40 by way of the atlas — the only structure the suite
 * actually declares — and colour is spent on that rather than on a hash of the skill id. A skill
 * in no wave lands in its own band and says so, which is the same refusal the atlas makes.
 *
 * The card carries what a person scans for: the name, how much work sits under it, and where the
 * risk is. The description was three truncated lines of routing prose, which is written for a
 * router and reads like it; it moved to the detail view, where there is room to read it. */

const RISK_ORDER = ['R0-light', 'R1-reviewed', 'R2-standard', 'R3-controlled', 'R4-critical'];

function riskBar(tasks) {
  const counts = new Map(RISK_ORDER.map((r) => [r, 0]));
  for (const t of tasks) if (counts.has(t.risk)) counts.set(t.risk, counts.get(t.risk) + 1);
  const total = tasks.length || 1;
  const bar = document.createElement('span');
  bar.className = 'risk-bar';
  const label = [];
  for (const risk of RISK_ORDER) {
    const n = counts.get(risk);
    if (!n) continue;
    const seg = document.createElement('span');
    seg.className = `risk-seg risk-${risk.slice(0, 2)}`;
    // Width in a class rather than a style attribute: the page CSP forbids inline styles.
    seg.dataset.share = String(Math.max(1, Math.round((n / total) * 20)));
    bar.append(seg);
    label.push(`${n} ${risk}`);
  }
  bar.title = label.join(', ');
  return bar;
}

function skillCard(skill) {
  const card = document.createElement('button');
  card.className = 'card';
  card.type = 'button';
  card.dataset.skill = skill.id;

  const title = document.createElement('h3');
  title.textContent = skill.name;

  const meta = document.createElement('div');
  meta.className = 'meta';
  const count = document.createElement('span');
  count.className = 'meta-count';
  count.textContent = `${skill.taskCount} task`;
  meta.append(count);
  const strong = skill.tasks.filter((t) => t.modelTier === 'strong').length;
  if (strong) {
    const s = document.createElement('span');
    s.className = 'meta-strong';
    s.textContent = `${strong} strong`;
    meta.append(s);
  }

  card.append(title, meta, riskBar(skill.tasks));
  card.addEventListener('click', () => openDrawer(skill));
  return card;
}

function renderGrid() {
  const grid = $('grid');
  grid.innerHTML = '';
  if (!state.suitePath) {
    grid.innerHTML = '<div class="empty">Chưa nối suite. Bấm <b>Chọn thư mục suite</b> và trỏ tới thư mục chứa <code>suite-manifest.yaml</code>.</div>';
    return;
  }
  const visible = state.skills.filter(matches);
  if (!visible.length) {
    grid.innerHTML = '<div class="empty">Không có skill nào khớp bộ lọc.</div>';
    return;
  }

  const order = (state.waves || []).map((w) => w.wave);
  const byWave = new Map(order.map((w) => [w, []]));
  const loose = [];
  for (const skill of visible) {
    if (byWave.has(skill.wave)) byWave.get(skill.wave).push(skill);
    else loose.push(skill);
  }
  if (loose.length) byWave.set('', loose);

  for (const [wave, skills] of byWave) {
    if (!skills.length) continue;
    const meta = (state.waves || []).find((w) => w.wave === wave);
    const band = document.createElement('section');
    band.className = `band tone-${(meta && meta.tone) || 'unplaced'}`;

    const head = document.createElement('div');
    head.className = 'band-head';
    const name = document.createElement('span');
    name.className = 'band-name';
    name.textContent = wave || 'Chưa xếp wave';
    head.append(name);
    if (meta && meta.title) {
      const sub = document.createElement('span');
      sub.className = 'band-sub';
      sub.textContent = meta.title;
      head.append(sub);
    }
    const tally = document.createElement('span');
    tally.className = 'band-tally';
    tally.textContent = `${skills.length} skill · ${skills.reduce((n, s) => n + s.taskCount, 0)} task`;
    head.append(tally);
    band.append(head);

    const row = document.createElement('div');
    row.className = 'band-cards';
    for (const skill of skills) row.append(skillCard(skill));
    band.append(row);
    grid.append(band);
  }
}

function renderTasks() {
  const box = $('dTasks');
  box.innerHTML = '';
  const skill = state.openSkill;
  if (!skill) return;
  const q = state.query.trim().toLowerCase();
  const list = skill.tasks.filter((t) => {
    if (state.filterTier && t.modelTier !== state.filterTier) return false;
    return taskMatches(t, q);
  });
  if (!list.length) {
    box.innerHTML = '<div class="empty">Không có task nào khớp bộ lọc.</div>';
    return;
  }
  for (const task of list) {
    const row = document.createElement('div');
    row.className = 'task';
    row.setAttribute('role', 'option');
    row.setAttribute('aria-selected', String(state.selectedTask === task.id));

    const main = document.createElement('div');
    main.className = 'task-main';
    const code = document.createElement('code');
    code.textContent = task.id;
    const goal = document.createElement('div');
    goal.className = 'goal';
    // The catalog already carries a Vietnamese goal for 810 of 827 tasks; the English `output`
    // is the fallback, not the default.
    goal.textContent = task.goal || task.output || '';
    if (task.goal && task.output) goal.title = task.output;
    main.append(code, goal);

    const tier = document.createElement('span');
    tier.className = `tier tier-${task.modelTier || 'standard'}`;
    tier.textContent = task.modelTier || '—';

    row.append(main, tier);
    row.addEventListener('click', () => {
      state.selectedTask = state.selectedTask === task.id ? null : task.id;
      renderTasks();
    });
    box.append(row);
  }
}

function renderGuide(skill) {
  const box = $('dGuide');
  box.innerHTML = '';
  const g = skill.guide;

  const section = (label, node) => {
    const h = document.createElement('h4');
    h.textContent = label;
    box.append(h, node);
  };
  const list = (items) => {
    const ul = document.createElement('ul');
    for (const it of items) {
      const li = document.createElement('li');
      li.textContent = it;
      ul.append(li);
    }
    return ul;
  };

  if (!g) {
    const p = document.createElement('p');
    p.className = 'lead';
    p.textContent = skill.description || '';
    box.append(p);
    return;
  }

  const lead = document.createElement('p');
  lead.className = 'lead';
  lead.textContent = g.tom_tat;
  box.append(lead);

  if (g.dung_khi && g.dung_khi.length) section('Dùng khi', list(g.dung_khi));

  if (g.khong_dung_khi) {
    const p = document.createElement('p');
    p.className = 'note';
    p.textContent = g.khong_dung_khi;
    section('Không dùng khi', p);
  }

  if (g.bat_dau_tu && g.bat_dau_tu.length) {
    const row = document.createElement('div');
    row.className = 'starts';
    for (const id of g.bat_dau_tu) {
      const c = document.createElement('code');
      c.textContent = id;
      c.title = 'Chọn task này';
      // Clicking a suggested entry point selects it, so the guide is a shortcut rather than
      // a paragraph to read and then act on separately.
      c.addEventListener('click', () => {
        state.selectedTask = id;
        renderTasks();
      });
      row.append(c);
    }
    section('Bắt đầu từ', row);
  }

  if (g.luu_y) {
    const p = document.createElement('p');
    p.className = 'warn';
    p.textContent = g.luu_y;
    section('Lưu ý', p);
  }

  const toggle = document.createElement('button');
  toggle.className = 'guide-toggle';
  toggle.type = 'button';
  toggle.textContent = 'Xem mô tả gốc (tiếng Anh)';
  const en = document.createElement('p');
  en.className = 'desc-en';
  en.textContent = skill.description || '';
  en.hidden = true;
  toggle.addEventListener('click', () => {
    en.hidden = !en.hidden;
    toggle.textContent = en.hidden ? 'Xem mô tả gốc (tiếng Anh)' : 'Ẩn mô tả gốc';
  });
  box.append(toggle, en);
}

function showPane(which) {
  for (const id of ['paneJobs', 'paneForm', 'paneRun']) $(id).hidden = id !== which;
}

// A preset job and a hand-picked task are two ways to reach the same run; only one is active.
function pickJob(job) {
  state.job = job;
  state.selectedTask = job.task_id;
  window.jobsUI.renderJobForm(
    job,
    (_j, _v, text, missing) => {
      state.jobPrompt = text;
      state.jobMissing = missing;
      updateLaunch();
    },
    () => {
      state.job = null;
      state.jobPrompt = '';
      state.jobMissing = [];
      showPane('paneJobs');
      updateLaunch();
    }
  );
  showPane('paneForm');
  updateLaunch();
}

function openDrawer(skill) {
  state.openSkill = skill;
  state.selectedTask = null;
  state.job = null;
  state.jobPrompt = '';
  state.jobMissing = [];
  showPane('paneJobs');
  showView('viewDetail');
  window.jobsUI.renderJobList(skill, pickJob);
  $('dTitle').textContent = skill.name;
  renderGuide(skill);
  renderTasks();
  updateLaunch();
}

// Keep the tail of a long path: the last two segments identify a folder, the prefix rarely does.
function shortPath(p, keep = 2) {
  const parts = p.split('/').filter(Boolean);
  if (parts.length <= keep) return p;
  return '…/' + parts.slice(-keep).join('/');
}

function effectivePrompt() {
  if (state.job) return state.jobPrompt;
  if (!state.openSkill) return '';
  return state.selectedTask
    ? `Use the ${state.openSkill.id} skill and run the atomic task ${state.selectedTask} in this directory.`
    : `Use the ${state.openSkill.id} skill for work in this directory. Route to the right atomic task by primary deliverable.`;
}

function updateLaunch() {
  const ready = Boolean(state.openSkill && state.folder);
  const blocked = state.job && state.jobMissing.length > 0;
  $('launch').disabled = !ready;
  $('runStart').disabled = !ready || blocked;
  const line = $('folderLine');
  if (blocked) {
    line.textContent = `Còn thiếu: ${state.jobMissing.join(', ')}`;
    line.title = '';
  } else {
    line.textContent = state.folder ? shortPath(state.folder) : 'Chưa chọn thư mục';
    line.title = state.folder || '';
  }
}

async function loadSuite(suitePath) {
  const data = await window.studio.readSuite(suitePath);
  if (data.error) {
    notice(data.error, 'err');
    state.suitePath = '';
    renderGrid();
    return;
  }
  state.suitePath = suitePath;
  state.suiteVersion = data.suiteVersion;
  state.skills = data.skills;
  state.waves = data.waves || [];
  state.catalog = new Map();
  for (const skill of data.skills) {
    for (const t of skill.tasks) state.catalog.set(t.id, t);
  }
  const list = $('taskIds');
  list.innerHTML = '';
  for (const id of [...state.catalog.keys()].sort()) {
    const o = document.createElement('option');
    o.value = id;
    list.append(o);
  }
  $('suiteChip').textContent = `v${data.suiteVersion} · ${data.skills.length} skill · ${data.taskTotal} task`;
  $('subtitle').textContent = suitePath;
  if (window.wfSetMeta) window.wfSetMeta(state.catalog);
  if (window.wfLoadPresets) window.wfLoadPresets();
  notice('');
  renderGrid();
}

// One place to say something went wrong. Before this, a button that could not do its job did
// nothing at all and the user had no way to tell that from a slow disk.
let statusTimer = 0;
function setStatus(message) {
  const el = $('status');
  el.textContent = message;
  el.hidden = !message;
  clearTimeout(statusTimer);
  if (message) statusTimer = setTimeout(() => { el.hidden = true; }, 6000);
}

// The atlas is a generated page inside the suite, so it needs a suite before it can be opened,
// and it can be absent on an older checkout. Say which of the two happened rather than doing
// nothing when the button is pressed.
$('openAtlas').addEventListener('click', async () => {
  if (!state.suitePath) {
    setStatus('Chọn thư mục suite trước khi mở bản đồ.');
    return;
  }
  const page = `${state.suitePath}/docs/skill-atlas.html`;
  const problem = await window.studio.openPath(page);
  if (problem) {
    setStatus('Chưa có docs/skill-atlas.html — chạy tools/build_skill_atlas.py trong suite.');
  }
});

$('pickSuite').addEventListener('click', async () => {
  const picked = await window.studio.pickSuite();
  if (picked) loadSuite(picked);
});

$('pickFolder').addEventListener('click', async () => {
  const folder = await window.studio.pickFolder();
  if (folder) {
    state.folder = folder;
    updateLaunch();
  }
});

$('runStart').addEventListener('click', async () => {
  const prompt = effectivePrompt();
  if (!prompt) return;
  showPane('paneRun');
  window.runUI.reset();
  window.runUI.setRunning(true);
  const runId = window.runUI.newId();
  const res = await window.studio.startRun({
    runId,
    folder: state.folder,
    prompt,
    suitePath: state.suitePath,
    permissionMode: $('permMode').value,
  });
  if (!res.ok) window.runUI.finish(-1, res.error);
});

$('runStop').addEventListener('click', () => window.studio.stopRun(window.runUI.currentId()));
$('runBack').addEventListener('click', () => showPane(state.job ? 'paneForm' : 'paneJobs'));

window.studio.onRunEvent(({ runId, event }) => {
  if (runId === window.runUI.currentId()) window.runUI.handleEvent(event);
});
window.studio.onRunStderr(({ runId, text }) => {
  if (runId === window.runUI.currentId() && text.trim()) window.runUI.handleEvent({ type: 'raw', text });
});
window.studio.onRunDone(({ runId, code, error }) => {
  if (runId === window.runUI.currentId()) window.runUI.finish(code, error);
  // A run the cockpit started writes its outcome back into the manifest.
  if (self.cockpitRunFinished) self.cockpitRunFinished(runId, code);
});

$('launch').addEventListener('click', async () => {
  const result = await window.studio.launch({
    folder: state.folder,
    skillId: state.openSkill.id,
    taskId: state.selectedTask,
    suitePath: state.suitePath,
  });
  if (result.ok) {
    notice(`Đã mở phiên trong ${state.folder} (${result.terminal}).`, 'ok');
    showView('viewSkills');
  } else {
    notice(result.error, 'err');
  }
});

document.addEventListener('keydown', (e) => {
  if (e.key !== 'Escape') return;
  if (!$('viewDetail').hidden) {
    state.openSkill = null;
    state.job = null;
    showView('viewSkills');
  }
});

$('purpose').addEventListener('input', renderSuggestions);
$('purposeClear').addEventListener('click', () => {
  $('purpose').value = '';
  renderSuggestions();
});

$('search').addEventListener('input', (e) => {
  state.query = e.target.value;
  renderGrid();
  if (state.openSkill) renderTasks();
});

$('tierFilter').addEventListener('click', (e) => {
  const btn = e.target.closest('button');
  if (!btn) return;
  state.filterTier = btn.dataset.tier;
  for (const b of $('tierFilter').querySelectorAll('button')) {
    b.setAttribute('aria-pressed', String(b === btn));
  }
  renderGrid();
  if (state.openSkill) renderTasks();
});

// Tabs: the grid launches sessions, the canvas edits the workflow those sessions run inside.
function showView(which) {
  for (const id of ['viewSkills', 'viewDetail', 'viewWorkflow']) {
    $(id).hidden = id !== which;
  }
  // The toolbar filters the grid, so it belongs to the grid view only.
  document.querySelector('.toolbar').hidden = which !== 'viewSkills';
  $('tabSkills').setAttribute('aria-selected', String(which !== 'viewWorkflow'));
  $('tabWorkflow').setAttribute('aria-selected', String(which === 'viewWorkflow'));
  window.scrollTo(0, 0);
}
$('tabSkills').addEventListener('click', () => showView(state.openSkill ? 'viewDetail' : 'viewSkills'));
$('tabWorkflow').addEventListener('click', () => showView('viewWorkflow'));
$('backToSkills').addEventListener('click', () => {
  state.openSkill = null;
  state.job = null;
  showView('viewSkills');
});

window.wfInit(() => state.suitePath, () => state.catalog, () => state.folder);

(async function boot() {
  const cfg = await window.studio.getConfig();
  state.folder = (cfg.recentFolders && cfg.recentFolders[0]) || '';
  updateLaunch();
  if (cfg.suitePath) loadSuite(cfg.suitePath);
  else renderGrid();
})();
