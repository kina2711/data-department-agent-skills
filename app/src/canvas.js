'use strict';

/* Workflow canvas.
 *
 * The manifest schema forbids extra properties and holds no coordinates, so nothing here is
 * persisted as a position. The graph is laid out from `depends_on` on every render, which costs
 * free arrangement and buys a picture that cannot disagree with the file it came from. */

// Layering, layout and the run-order helpers live in lib/graph.js so tests can call them without
// a DOM. Two copies of a layering rule is one copy too many.
const { NODE_W, NODE_H, GAP_X, GAP_Y, PAD, layout, runPlan, nextAction } = self.WfGraph;

const wf = {
  file: '',
  manifest: null,
  selected: null,
  dirty: false,
  meta: new Map(),
  fit: false,
};

const DONE = new Set(['implemented', 'tested', 'approved', 'released', 'complete']);
const OPEN = new Set(['ready', 'in-progress']);

const STATUSES = ['planned', 'ready', 'in-progress', 'blocked', 'failed', 'implemented', 'tested', 'approved', 'released', 'complete'];
const RISKS = ['R0-light', 'R1-reviewed', 'R2-standard', 'R3-controlled', 'R4-critical'];

const q = (id) => document.getElementById(id);
// The validator keys tasks by task_id and rejects duplicates, so instance_id is a label and
// never an identity. depends_on entries resolve against task_id.
const keyOf = (t) => t.task_id;

function render() {
  const host = q('wfCanvas');
  host.innerHTML = '';
  if (!wf.manifest) {
    host.innerHTML = '<div class="empty">Chưa mở workflow nào.</div>';
    return;
  }
  const tasks = wf.manifest.tasks || [];
  if (!tasks.length) {
    host.innerHTML = '<div class="empty">Manifest chưa có task nào. Bấm <b>Thêm task</b>.</div>';
    return;
  }

  const laid = layout(tasks);
  const depth = laid && laid.depth;
  if (!laid) {
    host.innerHTML = '<div class="notice notice-err">Đồ thị có chu trình trong <code>depends_on</code>; không tồn tại thứ tự nào để vẽ. Sửa phụ thuộc rồi mở lại.</div>';
    return;
  }

  const { pos, width, height } = laid;

  const NS = 'http://www.w3.org/2000/svg';
  const el = (tag, attrs) => {
    const n = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs || {})) n.setAttribute(k, String(v));
    return n;
  };
  // Nodes are drawn as SVG, not positioned HTML: the page CSP forbids inline styles, and SVG
  // geometry lives in attributes rather than in a style declaration.
  // A fourteen-stage graph is wider than any panel. Fit scales through the viewBox — an
  // attribute, so it survives the page CSP that forbids inline styles.
  let drawW = width;
  let drawH = height;
  if (wf.fit) {
    const avail = Math.max(320, host.clientWidth - 10);
    const scale = Math.min(1, avail / width);
    drawW = Math.round(width * scale);
    drawH = Math.round(height * scale);
  }
  const svg = el('svg', {
    class: `wf-svg${wf.fit ? ' is-fit' : ''}`,
    width: drawW, height: drawH, viewBox: `0 0 ${width} ${height}`,
  });

  const defs = el('defs');
  const marker = el('marker', {
    id: 'wfArrow', viewBox: '0 0 8 8', refX: 7, refY: 4,
    markerWidth: 7, markerHeight: 7, orient: 'auto-start-reverse',
  });
  marker.append(el('path', { d: 'M0,0 L8,4 L0,8 z', class: 'wf-arrow' }));
  defs.append(marker);
  svg.append(defs);

  for (const t of tasks) {
    const to = pos.get(keyOf(t));
    for (const dep of t.depends_on || []) {
      const from = pos.get(dep);
      if (!from || !to) continue;
      const x1 = from.x + NODE_W;
      const y1 = from.y + NODE_H / 2;
      const x2 = to.x;
      const y2 = to.y + NODE_H / 2;
      const mid = (x1 + x2) / 2;
      svg.append(el('path', {
        d: `M${x1},${y1} C${mid},${y1} ${mid},${y2} ${x2},${y2}`,
        class: 'wf-edge', 'marker-end': 'url(#wfArrow)',
      }));
    }
  }

  const clip = (text, max) => (text.length > max ? `${text.slice(0, max - 1)}…` : text);

  // A control boundary is where risk first rises above everything before it — the point the work
  // needs authority the earlier stages did not. Derived from the same risk data the nodes show,
  // never stored, so it cannot disagree with the manifest.
  const RANK = { 'R0-light': 0, 'R1-reviewed': 1, 'R2-standard': 2, 'R3-controlled': 3, 'R4-critical': 4 };
  const gates = new Set();
  {
    const byCol = new Map();
    for (const t of tasks) {
      const c = depth.get(keyOf(t)) || 0;
      byCol.set(c, Math.max(byCol.get(c) || 0, RANK[t.risk_tier] ?? 0));
    }
    let seen = 0;
    for (const c of [...byCol.keys()].sort((a, b) => a - b)) {
      if (byCol.get(c) > seen && byCol.get(c) >= 2) gates.add(c);
      seen = Math.max(seen, byCol.get(c));
    }
  }
  for (const col of gates) {
    const x = PAD + col * (NODE_W + GAP_X) - GAP_X / 2;
    svg.append(el('line', { class: 'wf-gate', x1: x, y1: 4, x2: x, y2: height - 4 }));
    const label = el('text', { class: 'wf-gate-label', x: x + 5, y: 14 });
    label.textContent = 'cần phê duyệt';
    svg.append(label);
  }

  for (const t of tasks) {
    const p = pos.get(keyOf(t));
    const selected = wf.selected === keyOf(t);
    const g = el('g', {
      class: `wf-node${selected ? ' is-selected' : ''}`,
      transform: `translate(${p.x},${p.y})`,
      tabindex: 0, role: 'button',
      'data-status': t.status || 'planned',
    });
    const tip = el('title');
    tip.textContent = `${t.task_id}${t.instance_id ? ` (${t.instance_id})` : ''}`;
    g.append(tip);
    g.append(el('rect', { class: 'wf-node-box', width: NODE_W, height: NODE_H, rx: 11 }));

    // The manifest schema forbids extra fields, so display metadata is joined from the catalog
    // rather than copied into the file. The picture stays derived; the file stays valid.
    const meta = (wf.meta && wf.meta.get(t.task_id)) || {};

    const id = el('text', { class: 'wf-node-title', x: 13, y: 22 });
    id.textContent = clip(t.task_id, 28);
    const goal = el('text', { class: 'wf-node-goal', x: 13, y: 40 });
    goal.textContent = clip(meta.goal || meta.output || '', 34);
    const sub = el('text', { class: 'wf-node-sub', x: 13, y: 58 });
    sub.textContent = clip(t.instance_id ? `${t.instance_id} · ${t.owner || 'chưa có owner'}` : (t.owner || 'chưa có owner'), 32);
    const st = el('text', { class: 'wf-node-status', x: 13, y: 78 });
    st.textContent = t.status || 'planned';
    g.append(id, goal, sub, st);

    // Risk and model tier are the two things that change how a task must be run.
    if (t.risk_tier) {
      const r = el('text', { class: `wf-node-risk risk-${t.risk_tier.split('-')[0]}`, x: NODE_W - 13, y: 22, 'text-anchor': 'end' });
      r.textContent = t.risk_tier.split('-')[0];
      g.append(r);
    }
    if (meta.modelTier) {
      const m = el('text', { class: `wf-node-tier tier-${meta.modelTier}`, x: NODE_W - 13, y: 78, 'text-anchor': 'end' });
      m.textContent = meta.modelTier;
      g.append(m);
    }

    const activate = () => {
      wf.selected = wf.selected === keyOf(t) ? null : keyOf(t);
      render();
      renderInspector();
    };
    g.addEventListener('click', activate);
    g.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); activate(); }
    });
    svg.append(g);
  }
  host.append(svg);
  renderProgress(tasks, depth);
}

/** Progress is counted from status, and blocked work is never folded into "remaining".
 *  Drawn as SVG: segment widths are geometry, which the page CSP allows, unlike the inline style
 *  a div-based bar would need. */
function renderProgress(tasks, depth) {
  const box = q('wfProgress');
  if (!box) return;
  box.innerHTML = '';
  const total = tasks.length;
  if (!total) return;
  const done = tasks.filter((t) => DONE.has(t.status)).length;
  const active = tasks.filter((t) => OPEN.has(t.status)).length;
  const stuck = tasks.filter((t) => t.status === 'blocked' || t.status === 'failed').length;

  const NS = 'http://www.w3.org/2000/svg';
  const W = 220;
  const svg = document.createElementNS(NS, 'svg');
  svg.setAttribute('class', 'wf-bar-track');
  svg.setAttribute('width', String(W));
  svg.setAttribute('height', '8');
  const track = document.createElementNS(NS, 'rect');
  for (const [k, v] of Object.entries({ class: 'wf-seg-empty', width: W, height: 8, rx: 4 })) {
    track.setAttribute(k, String(v));
  }
  svg.append(track);
  let x = 0;
  for (const [cls, n] of [['done', done], ['active', active], ['stuck', stuck]]) {
    if (!n) continue;
    const w = (n / total) * W;
    const seg = document.createElementNS(NS, 'rect');
    for (const [k, v] of Object.entries({ class: `wf-seg-${cls}`, x, width: w, height: 8, rx: 4 })) {
      seg.setAttribute(k, String(v));
    }
    svg.append(seg);
    x += w;
  }
  box.append(svg);

  const line = document.createElement('span');
  line.className = 'wf-progress-text';
  const parts = [`${done}/${total} xong`];
  if (active) parts.push(`${active} đang chạy`);
  if (stuck) parts.push(`${stuck} tắc`);
  parts.push(`${new Set([...depth.values()]).size} tầng`);
  line.textContent = parts.join(' · ');
  box.append(line);
}

function renderInspector() {
  const box = q('wfInspector');
  box.innerHTML = '';
  const tasks = (wf.manifest && wf.manifest.tasks) || [];
  const task = tasks.find((t) => keyOf(t) === wf.selected);
  if (!task) {
    box.innerHTML = '<p class="drawer-hint">Chọn một node để sửa. Không chọn gì thì các nút dưới tác động lên cả manifest.</p>';
    return;
  }

  const field = (label, node) => {
    const wrap = document.createElement('label');
    wrap.className = 'wf-field';
    const span = document.createElement('span');
    span.textContent = label;
    wrap.append(span, node);
    box.append(wrap);
    return node;
  };

  const idInput = document.createElement('input');
  idInput.className = 'search';
  idInput.value = task.task_id;
  idInput.readOnly = true;
  idInput.title = 'task_id phải khớp catalog; xoá node rồi thêm lại để đổi';
  field('task_id', idInput);

  const inst = document.createElement('input');
  inst.className = 'search';
  inst.value = task.instance_id || '';
  inst.placeholder = 'ví dụ module-1';
  inst.addEventListener('input', () => { task.instance_id = inst.value.trim(); markDirty(); render(); });
  field('instance_id', inst);

  const owner = document.createElement('input');
  owner.className = 'search';
  owner.value = task.owner || '';
  owner.addEventListener('input', () => { task.owner = owner.value; markDirty(); render(); });
  field('owner', owner);

  const status = document.createElement('select');
  status.className = 'search';
  for (const s of STATUSES) {
    const o = document.createElement('option');
    o.value = s; o.textContent = s;
    if ((task.status || 'planned') === s) o.selected = true;
    status.append(o);
  }
  status.addEventListener('change', () => { task.status = status.value; markDirty(); render(); });
  field('status', status);

  const risk = document.createElement('select');
  risk.className = 'search';
  for (const r of RISKS) {
    const o = document.createElement('option');
    o.value = r; o.textContent = r;
    if (task.risk_tier === r) o.selected = true;
    risk.append(o);
  }
  risk.addEventListener('change', () => { task.risk_tier = risk.value; markDirty(); });
  field('risk_tier', risk);

  const depsBox = document.createElement('div');
  depsBox.className = 'wf-deps';
  for (const other of tasks) {
    if (keyOf(other) === keyOf(task)) continue;
    const row = document.createElement('label');
    row.className = 'wf-dep';
    const cb = document.createElement('input');
    cb.type = 'checkbox';
    cb.checked = (task.depends_on || []).includes(keyOf(other));
    cb.addEventListener('change', () => {
      const set = new Set(task.depends_on || []);
      if (cb.checked) set.add(keyOf(other)); else set.delete(keyOf(other));
      task.depends_on = [...set];
      markDirty();
      render();
    });
    const txt = document.createElement('span');
    txt.textContent = keyOf(other);
    row.append(cb, txt);
    depsBox.append(row);
  }
  field('depends_on', depsBox);

  const del = document.createElement('button');
  del.className = 'btn';
  del.textContent = 'Xoá node này';
  del.addEventListener('click', () => {
    const key = keyOf(task);
    wf.manifest.tasks = tasks.filter((t) => keyOf(t) !== key);
    for (const t of wf.manifest.tasks) {
      t.depends_on = (t.depends_on || []).filter((d) => d !== key);
    }
    wf.selected = null;
    markDirty();
    render();
    renderInspector();
  });
  box.append(del);
}


/* The dry run, drawn.
 *
 * It answers three questions before anything is executed: how many rounds this takes, how much
 * runs at once in each round, and where a person has to sign before the next round can start.
 * Nothing here calls the model or the validator — it reads the manifest already open.
 *
 * Stranded tasks get their own row rather than being left out. A plan that silently omits the work
 * it cannot order looks complete, and that is the failure this row exists to prevent. */
function renderPlan() {
  const host = q('wfPlan');
  host.textContent = '';
  if (!wf.manifest) {
    host.hidden = true;
    return;
  }
  const tasks = wf.manifest.tasks || [];
  const plan = runPlan(tasks);
  host.hidden = false;

  const head = document.createElement('div');
  head.className = 'wf-plan-head';
  const bits = [`${plan.waves.length} đợt`, `rộng nhất ${plan.widest} task`, `${plan.planned} task sẽ chạy`];
  if (plan.already) bits.push(`${plan.already} đã xong`);
  if (plan.gates) bits.push(`${plan.gates} cổng duyệt`);
  head.textContent = bits.join(' · ');
  host.append(head);

  if (!plan.waves.length && !plan.stranded.length) {
    const none = document.createElement('p');
    none.className = 'wf-plan-none';
    none.textContent = 'Không còn task nào để chạy.';
    host.append(none);
    return;
  }

  for (const wave of plan.waves) {
    const row = document.createElement('div');
    row.className = 'wf-wave';
    const label = document.createElement('span');
    label.className = 'wf-wave-n';
    label.textContent = `Đợt ${wave.wave}`;
    row.append(label);
    const list = document.createElement('div');
    list.className = 'wf-wave-tasks';
    for (const id of wave.tasks) {
      const chip = document.createElement('span');
      const gate = wave.gates.includes(id);
      chip.className = `wf-chip${gate ? ' is-gate' : ''}`;
      chip.textContent = gate ? `${id} · cần duyệt` : id;
      list.append(chip);
    }
    row.append(list);
    host.append(row);
  }

  if (plan.stranded.length) {
    const row = document.createElement('div');
    row.className = 'wf-wave is-stranded';
    const label = document.createElement('span');
    label.className = 'wf-wave-n';
    label.textContent = 'Không tới được';
    row.append(label);
    const list = document.createElement('div');
    list.className = 'wf-wave-tasks';
    for (const id of plan.stranded) {
      const chip = document.createElement('span');
      chip.className = 'wf-chip is-stranded';
      chip.textContent = id;
      list.append(chip);
    }
    row.append(list);
    host.append(row);
    const why = document.createElement('p');
    why.className = 'wf-plan-none';
    why.textContent = 'Các task này không có thứ tự nào chạy được: hoặc có chu trình trong depends_on, hoặc phụ thuộc vào task không nằm trong manifest.';
    host.append(why);
  }
}


/* The cockpit strip: one line saying what the workflow is waiting on, and the one or two controls
 * that apply to it. It is deliberately not a play button for the whole graph. Every task costs a
 * model call, gates exist so that a person decides, and a control that runs 29 tasks unattended
 * would be the wrong default no matter how convenient. */
const COCKPIT = {
  empty: () => ['Manifest chưa có task nào', ''],
  done: () => ['Hoàn tất', 'Mọi task trong manifest đã ở trạng thái kết thúc.'],
  running: (a) => ['Đang chạy', `${a.task} đang ở trạng thái in-progress.`],
  failed: (a) => ['Có task hỏng', `${a.tasks.join(', ')} — sửa hoặc đặt lại trạng thái trước khi đi tiếp.`],
  stranded: (a) => ['Không tới được', `${a.tasks.join(', ')} — chu trình trong depends_on, hoặc phụ thuộc ngoài manifest.`],
  gate: (a) => ['Cổng duyệt', `${a.task} ở mức ${a.risk}. Cần người duyệt; app không tự vượt cổng.`],
  run: (a) => ['Sẵn sàng', a.alsoReady.length
    ? `${a.task} chạy được ngay, cùng ${a.alsoReady.length} task khác trong đợt này.`
    : `${a.task} chạy được ngay.`],
};

function renderCockpit() {
  const host = q('wfCockpit');
  if (!wf.manifest) {
    host.hidden = true;
    return;
  }
  const action = nextAction(wf.manifest.tasks || []);
  const [state, detail] = (COCKPIT[action.kind] || (() => [action.kind, '']))(action);
  host.hidden = false;
  host.className = `wf-cockpit is-${action.kind}`;
  q('wfState').textContent = state;
  q('wfStateDetail').textContent = detail;

  // Running a task is offered only where it is the agent's to run. There is deliberately no
  // control that clears a gate: approval needs a signed record checked by the suite's own
  // validator, and a button in this app would be a claim it has no standing to make. The gate row
  // shows the command that checks the record instead.
  const runnable = action.kind === 'run';
  q('wfRunNext').hidden = !runnable;
  if (runnable) q('wfRunNext').dataset.task = action.task;

  q('wfMarkFailed').hidden = action.kind !== 'running';
  if (action.kind === 'running') q('wfMarkFailed').dataset.task = action.task;

  const gate = action.kind === 'gate';
  q('wfGateCmd').hidden = !gate;
  if (gate) q('wfGateCmd').textContent = `/dd-approve <hồ sơ duyệt> ${wf.file || ''}`.trim();
  wf.action = action;
}


/** Write a status and persist it, so the picture and the file never disagree. */
async function setStatusAndSave(task, status) {
  task.status = status;
  if (wf.file) await window.studio.saveWorkflow({ file: wf.file, manifest: wf.manifest });
  wf.dirty = false;
  q('wfSave').disabled = true;
  render();
  renderInspector();
  renderCockpit();
  if (!q('wfPlan').hidden) renderPlan();
}

/** The cockpit reports the outcome of a run it started, and ignores runs it did not. */
function cockpitRunFinished(runId, code) {
  if (!wf.awaiting || wf.awaiting.runId !== runId) return;
  const { taskId } = wf.awaiting;
  wf.awaiting = null;
  const task = (wf.manifest.tasks || []).find((x) => x.task_id === taskId);
  if (task) setStatusAndSave(task, code === 0 ? 'implemented' : 'failed');
}
self.cockpitRunFinished = cockpitRunFinished;

function markDirty() {
  wf.dirty = true;
  q('wfSave').disabled = false;
  q('wfFile').textContent = `${wf.file} — chưa lưu`;
}

function loaded(payload) {
  if (!payload) return;
  if (payload.error) {
    q('wfResult').className = 'notice notice-err';
    q('wfResult').textContent = payload.error;
    return;
  }
  wf.file = payload.file;
  wf.manifest = payload.manifest;
  wf.selected = null;
  wf.dirty = false;
  q('wfSave').disabled = true;
  q('wfFile').textContent = payload.file;
  q('wfResult').textContent = '';
  q('wfResult').className = '';
  render();
  renderInspector();
  renderCockpit();
  if (!q('wfPlan').hidden) renderPlan();
}

window.wfSetMeta = (map) => { wf.meta = map; };

window.wfInit = function wfInit(getSuitePath, getCatalog, getRunFolder) {
  q('wfOpen').addEventListener('click', async () => loaded(await window.studio.openWorkflow(getSuitePath())));

  window.wfLoadPresets = async () => {
    const list = await window.studio.listWorkflows(getSuitePath());
    const sel = q('wfPreset');
    sel.innerHTML = '<option value="">Workflow theo skill…</option>';
    for (const item of list) {
      const o = document.createElement('option');
      o.value = item.file;
      o.textContent = item.skill;
      sel.append(o);
    }
  };
  q('wfFit').addEventListener('click', () => {
    wf.fit = !wf.fit;
    q('wfFit').setAttribute('aria-pressed', String(wf.fit));
    q('wfFit').textContent = wf.fit ? 'Cỡ thật' : 'Vừa khung';
    render();
  });
  q('wfPreset').addEventListener('change', async (e) => {
    if (!e.target.value) return;
    loaded(await window.studio.openWorkflowPath(e.target.value));
  });
  q('wfNew').addEventListener('click', async () => loaded(await window.studio.newWorkflow(getSuitePath())));

  q('wfAdd').addEventListener('click', () => {
    if (!wf.manifest) return;
    const id = (q('wfAddId').value || '').trim();
    const known = getCatalog();
    if (!known.has(id)) {
      q('wfResult').className = 'notice notice-err';
      q('wfResult').textContent = `task_id "${id}" không có trong catalog; validator sẽ từ chối nó.`;
      return;
    }
    const meta = known.get(id);
    wf.manifest.tasks = wf.manifest.tasks || [];
    wf.manifest.tasks.push({
      task_id: id,
      owner: '',
      depends_on: [],
      status: 'planned',
      risk_tier: meta.risk || 'R1-reviewed',
      artifact_version: '',
      artifact_sha256: '',
      evidence_refs: [],
      approval_refs: [],
    });
    q('wfAddId').value = '';
    q('wfResult').textContent = '';
    q('wfResult').className = '';
    markDirty();
    render();
  });

  q('wfSave').addEventListener('click', async () => {
    const res = await window.studio.saveWorkflow({ file: wf.file, manifest: wf.manifest });
    if (res.ok) {
      wf.dirty = false;
      q('wfSave').disabled = true;
      q('wfFile').textContent = wf.file;
    } else {
      q('wfResult').className = 'notice notice-err';
      q('wfResult').textContent = res.error;
    }
  });

  /* Run one task from the cockpit.
   *
   * The status is written to the manifest before the run starts and again when it ends, so a run
   * that dies with the app still leaves in-progress behind rather than a task that looks planned.
   * An exit code of zero marks the task implemented, not complete: the run produced something, and
   * whether it is correct is what the test and review stages are for. */
  q('wfRunNext').addEventListener('click', async () => {
    const id = q('wfRunNext').dataset.task;
    const task = (wf.manifest.tasks || []).find((x) => x.task_id === id);
    if (!task) return;

    const folder = getRunFolder();
    if (!folder) {
      q('wfResult').className = 'notice notice-err';
      q('wfResult').textContent = 'Chọn thư mục làm việc ở tab Skills trước khi chạy task.';
      return;
    }

    await setStatusAndSave(task, 'in-progress');
    const runId = window.runUI.newId();
    window.runUI.reset();
    window.runUI.setRunning(true);
    wf.awaiting = { runId, taskId: id };
    const res = await window.studio.startRun({
      runId,
      folder,
      prompt: `Chạy task ${id} theo contract của nó trong suite. Dừng lại và báo cáo nếu contract yêu cầu approval.`,
      suitePath: getSuitePath(),
      permissionMode: q('wfMode').value === 'execute' ? 'acceptEdits' : 'plan',
    });
    if (!res.ok) {
      wf.awaiting = null;
      await setStatusAndSave(task, 'failed');
      q('wfResult').className = 'notice notice-err';
      q('wfResult').textContent = res.error || 'Không chạy được.';
    }
  });

  q('wfMarkFailed').addEventListener('click', async () => {
    const id = q('wfMarkFailed').dataset.task;
    const task = (wf.manifest.tasks || []).find((x) => x.task_id === id);
    if (task) await setStatusAndSave(task, 'failed');
  });

  q('wfDryRun').addEventListener('click', () => {
    const host = q('wfPlan');
    q('wfDryRun').setAttribute('aria-pressed', host.hidden ? 'true' : 'false');
    if (!host.hidden) {
      host.hidden = true;
      host.textContent = '';
      return;
    }
    renderPlan();
    // The canvas fills the window, so a panel appended after it lands a screen below the fold and
    // the button looks broken. Bring the answer to the person who asked for it.
    host.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  });

  q('wfValidate').addEventListener('click', async () => {
    if (!wf.file) return;
    if (wf.dirty) {
      await window.studio.saveWorkflow({ file: wf.file, manifest: wf.manifest });
      wf.dirty = false;
      q('wfSave').disabled = true;
      q('wfFile').textContent = wf.file;
    }
    const res = await window.studio.validateWorkflow({
      file: wf.file, suitePath: getSuitePath(), mode: q('wfMode').value,
    });
    q('wfResult').className = `notice notice-${res.ok ? 'ok' : 'err'}`;
    q('wfResult').textContent = res.output.trim() || (res.ok ? 'PASS' : 'FAILED');
  });

  render();
  renderInspector();
  renderCockpit();
  if (!q('wfPlan').hidden) renderPlan();
};
