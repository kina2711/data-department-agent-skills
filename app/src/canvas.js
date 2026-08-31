'use strict';

/* Workflow canvas.
 *
 * The manifest schema forbids extra properties and holds no coordinates, so nothing here is
 * persisted as a position. The graph is laid out from `depends_on` on every render, which costs
 * free arrangement and buys a picture that cannot disagree with the file it came from. */

const NODE_W = 232;
const NODE_H = 92;
const GAP_X = 78;
const GAP_Y = 22;
const PAD = 28;

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

/** Longest-path layering: a node sits one column right of its deepest dependency.
 *  Returns null when the graph has a cycle, because no layering exists inside one. */
function layer(tasks) {
  const byKey = new Map(tasks.map((t) => [keyOf(t), t]));
  const depth = new Map();
  const state = new Map();
  let cyclic = false;

  const visit = (key) => {
    if (state.get(key) === 2) return depth.get(key);
    if (state.get(key) === 1) {
      cyclic = true;
      return 0;
    }
    state.set(key, 1);
    const task = byKey.get(key);
    let d = 0;
    for (const dep of (task && task.depends_on) || []) {
      if (byKey.has(dep)) d = Math.max(d, visit(dep) + 1);
    }
    state.set(key, 2);
    depth.set(key, d);
    return d;
  };

  for (const key of byKey.keys()) visit(key);
  return cyclic ? null : depth;
}

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

  const depth = layer(tasks);
  if (!depth) {
    host.innerHTML = '<div class="notice notice-err">Đồ thị có chu trình trong <code>depends_on</code>; không tồn tại thứ tự nào để vẽ. Sửa phụ thuộc rồi mở lại.</div>';
    return;
  }

  const columns = new Map();
  for (const t of tasks) {
    const d = depth.get(keyOf(t)) || 0;
    if (!columns.has(d)) columns.set(d, []);
    columns.get(d).push(t);
  }

  const pos = new Map();
  let maxRows = 0;
  for (const [col, items] of [...columns].sort((a, b) => a[0] - b[0])) {
    maxRows = Math.max(maxRows, items.length);
    items.forEach((t, row) => {
      pos.set(keyOf(t), {
        x: PAD + col * (NODE_W + GAP_X),
        y: PAD + row * (NODE_H + GAP_Y),
      });
    });
  }
  const width = PAD * 2 + (columns.size) * NODE_W + (columns.size - 1) * GAP_X;
  const height = PAD * 2 + maxRows * NODE_H + (maxRows - 1) * GAP_Y;

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
}

window.wfSetMeta = (map) => { wf.meta = map; };

window.wfInit = function wfInit(getSuitePath, getCatalog) {
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
};
