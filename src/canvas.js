'use strict';

/* Workflow canvas.
 *
 * The manifest schema forbids extra properties and holds no coordinates, so nothing here is
 * persisted as a position. The graph is laid out from `depends_on` on every render, which costs
 * free arrangement and buys a picture that cannot disagree with the file it came from. */

const NODE_W = 216;
const NODE_H = 74;
const GAP_X = 78;
const GAP_Y = 22;
const PAD = 28;

const wf = {
  file: '',
  manifest: null,
  selected: null,
  dirty: false,
};

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
  const svg = el('svg', { class: 'wf-svg', width, height, viewBox: `0 0 ${width} ${height}` });

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

    const id = el('text', { class: 'wf-node-title', x: 13, y: 24 });
    id.textContent = clip(t.task_id, 27);
    const sub = el('text', { class: 'wf-node-sub', x: 13, y: 42 });
    sub.textContent = clip(t.instance_id ? `${t.instance_id} · ${t.owner || 'chưa có owner'}` : (t.owner || 'chưa có owner'), 30);
    const st = el('text', { class: 'wf-node-status', x: 13, y: 61 });
    st.textContent = t.status || 'planned';
    g.append(id, sub, st);

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
