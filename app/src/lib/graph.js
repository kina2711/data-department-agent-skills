'use strict';

/* Graph maths for the workflow canvas, kept apart from the drawing.
 *
 * These functions were inside canvas.js, where nothing could reach them: the file runs in the
 * renderer, defines no exports, and touches the DOM in the same breath as it computes a layout.
 * The layering rule and the cycle check are the two places a wrong answer is invisible — a cycle
 * drawn as a tree looks fine — so they belong somewhere a test can call them directly.
 *
 * Loaded by a <script> tag in the app and by require() in the tests, hence the wrapper. */

(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.WfGraph = api;
})(typeof self !== 'undefined' ? self : null, function () {
  const NODE_W = 232;
  const NODE_H = 92;
  const GAP_X = 78;
  const GAP_Y = 22;
  const PAD = 28;

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

  /** Column and row for every node, plus the canvas extent. Null when the graph cannot be laid out. */
  function layout(tasks) {
    const depth = layer(tasks);
    if (!depth) return null;

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
          col,
          row,
        });
      });
    }
    return {
      depth,
      pos,
      columns: columns.size,
      rows: maxRows,
      width: PAD * 2 + columns.size * NODE_W + (columns.size - 1) * GAP_X,
      height: PAD * 2 + maxRows * NODE_H + (maxRows - 1) * GAP_Y,
    };
  }

  /** Which tasks can start now: every dependency already in a finished state.
   *  The cockpit needs this before a run to show what the first wave is, and during one to show
   *  what unblocked. A task whose dependency is missing from the manifest is treated as ready,
   *  because the manifest is the whole world here and a dangling edge is the validator's problem. */
  const FINISHED = new Set(['implemented', 'tested', 'approved', 'released', 'complete']);

  function readyNow(tasks) {
    const status = new Map(tasks.map((t) => [keyOf(t), t.status || 'planned']));
    return tasks
      .filter((t) => !FINISHED.has(status.get(keyOf(t))))
      .filter((t) => ((t.depends_on || []).every((d) => !status.has(d) || FINISHED.has(status.get(d)))))
      .map(keyOf);
  }

  /** Longest chain of dependencies, which is the least number of waves a run can take. */
  function criticalPath(tasks) {
    const depth = layer(tasks);
    if (!depth) return null;
    let deepest = null;
    let best = -1;
    for (const [key, d] of depth) {
      if (d > best) {
        best = d;
        deepest = key;
      }
    }
    const byKey = new Map(tasks.map((t) => [keyOf(t), t]));
    const chain = [];
    const seen = new Set();
    let cur = deepest;
    // The loop trusted layer() to have rejected cycles. A mutation test that made layer() return a
    // depth map for a cyclic graph hung this function instead of failing, which is the wrong way
    // for a renderer to find out. The guard makes the walk terminate on its own.
    while (cur && !seen.has(cur)) {
      seen.add(cur);
      chain.unshift(cur);
      const deps = (byKey.get(cur) || {}).depends_on || [];
      let next = null;
      let nd = -1;
      for (const d of deps) {
        if (depth.has(d) && depth.get(d) > nd) {
          nd = depth.get(d);
          next = d;
        }
      }
      cur = next;
    }
    return chain;
  }

  /* A dry run: the waves a run would go through, computed without calling anything.
   *
   * Each wave is the set of tasks whose dependencies are satisfied by the waves before it, so the
   * wave count is the least number of rounds the work can take and the width of a wave is how much
   * could go in parallel. Tasks already finished in the manifest are not replanned.
   *
   * A gate is a task at R3 or R4. It is reported inside its wave rather than as a separate stage,
   * because approval is a condition on that task and not a step of its own — a run stops there and
   * waits for a person, and the plan should say so where it will actually happen.
   *
   * When a wave comes back empty while work remains, the rest is unreachable: a cycle, or a
   * dependency on a task the manifest does not contain. Those tasks are returned as `stranded`
   * rather than quietly dropped, because a plan that omits them looks complete. */
  const GATE = new Set(['R3-controlled', 'R4-critical']);

  function runPlan(tasks, { limit = 200 } = {}) {
    const done = new Set(
      tasks.filter((t) => FINISHED.has(t.status || 'planned')).map(keyOf));
    const already = done.size;
    const byKey = new Map(tasks.map((t) => [keyOf(t), t]));
    const waves = [];

    while (done.size < tasks.length && waves.length < limit) {
      const ready = tasks
        .filter((t) => !done.has(keyOf(t)))
        .filter((t) => (t.depends_on || []).every((d) => !byKey.has(d) || done.has(d)))
        .map(keyOf);
      if (!ready.length) break;
      waves.push({
        wave: waves.length + 1,
        tasks: ready,
        gates: ready.filter((k) => GATE.has((byKey.get(k) || {}).risk_tier)),
      });
      for (const k of ready) done.add(k);
    }

    const stranded = tasks.filter((t) => !done.has(keyOf(t))).map(keyOf);
    return {
      waves,
      stranded,
      already,
      planned: tasks.length - already - stranded.length,
      gates: waves.reduce((n, w) => n + w.gates.length, 0),
      widest: waves.reduce((n, w) => Math.max(n, w.tasks.length), 0),
    };
  }

  /* What the cockpit should do next, as one decision rather than a loop the UI writes itself.
   *
   * The order matters and is deliberate. A failure outranks everything: a run that walks past a
   * failed task to keep making progress is a run that hides the failure. A gate outranks ready
   * work, because the whole point of a gate is that nothing beyond it proceeds on the agent's own
   * authority; the cockpit surfaces it and stops, and only a person moves it. Stranded work is
   * reported after the reachable work is exhausted, since it is a defect in the manifest rather
   * than a step.
   *
   * The cockpit never marks a gate approved. It can only show that one is waiting. */
  const FAILED = new Set(['failed', 'blocked']);

  function nextAction(tasks) {
    const list = tasks || [];
    if (!list.length) return { kind: 'empty' };

    const failed = list.filter((t) => FAILED.has(t.status || ''));
    if (failed.length) return { kind: 'failed', tasks: failed.map(keyOf) };

    const ready = readyNow(list);
    if (!ready.length) {
      const left = list.filter((t) => !FINISHED.has(t.status || 'planned'));
      if (!left.length) return { kind: 'done' };
      return { kind: 'stranded', tasks: left.map(keyOf) };
    }

    const byKey = new Map(list.map((t) => [keyOf(t), t]));
    const running = list.find((t) => t.status === 'in-progress');
    if (running) return { kind: 'running', task: keyOf(running) };

    const gate = ready.find((k) => GATE.has((byKey.get(k) || {}).risk_tier));
    if (gate) return { kind: 'gate', task: gate, risk: byKey.get(gate).risk_tier, alsoReady: ready.filter((k) => k !== gate) };

    // The validator requires an owner on every task, and generated workflows ship without one:
    // they are templates, and filling the owners is the act of adopting one. Running an unowned
    // task would write a manifest the suite rejects, so the cockpit asks for the owner instead.
    const next = ready[0];
    if (!String((byKey.get(next) || {}).owner || '').trim()) {
      return { kind: 'unowned', task: next, alsoReady: ready.slice(1) };
    }

    return { kind: 'run', task: next, alsoReady: ready.slice(1) };
  }

  /* The legal status moves, copied from validate_workflow.py.
   *
   * Two copies of a rule is a drift waiting to happen, so a test parses the Python table and
   * asserts this one matches it exactly. Copying it is still worth doing: the app must know a move
   * is illegal before it writes the file, not after the validator refuses it, and shelling out to
   * Python on every click is not a reasonable price for that.
   *
   * The move this table forbids that matters most here: planned goes to ready, never straight to
   * in-progress. A cockpit that skips ready writes a manifest the suite rejects. */
  const ALLOWED = {
    planned: ['ready', 'blocked', 'failed'],
    ready: ['in-progress', 'blocked', 'failed'],
    'in-progress': ['implemented', 'blocked', 'failed'],
    implemented: ['in-progress', 'tested', 'blocked', 'failed'],
    tested: ['approved', 'released', 'complete', 'failed'],
    approved: ['released', 'failed'],
    released: ['complete', 'failed'],
    blocked: ['ready', 'failed'],
    failed: ['ready'],
    complete: [],
  };

  // A transition into one of these needs an evidence record, which the app cannot mint. The
  // cockpit stops short of them by design rather than writing a manifest the validator rejects.
  const NEEDS_EVIDENCE = new Set(['tested', 'approved', 'released', 'complete']);

  /** Shortest legal sequence of statuses from one to another, or null when none exists. */
  function statusPath(from, to) {
    if (!(from in ALLOWED) || !(to in ALLOWED)) return null;
    if (from === to) return [];
    const queue = [[from, []]];
    const seen = new Set([from]);
    while (queue.length) {
      const [at, path] = queue.shift();
      for (const next of ALLOWED[at]) {
        if (seen.has(next)) continue;
        const walked = path.concat(next);
        if (next === to) return walked;
        seen.add(next);
        queue.push([next, walked]);
      }
    }
    return null;
  }

  /** The transition records for moving a task, so history is written rather than inferred later.
   *  Returns null when the move is illegal or would need evidence the caller has not supplied. */
  function transitionsFor(task, to, { at, evidence = [] } = {}) {
    const from = task.status || 'planned';
    const path = statusPath(from, to);
    if (!path) return null;
    const stamp = at || new Date().toISOString();
    let cursor = from;
    const out = [];
    for (const step of path) {
      if (NEEDS_EVIDENCE.has(step) && !evidence.length) return null;
      out.push({
        task_id: keyOf(task),
        from_status: cursor,
        to_status: step,
        occurred_at: stamp,
        evidence_refs: NEEDS_EVIDENCE.has(step) ? evidence.slice() : [],
      });
      cursor = step;
    }
    return out;
  }

  /* An evidence envelope drafted from a run the app actually watched.
   *
   * The schema wants thirteen fields and the app honestly knows six of them: which task ran, what
   * command was issued, where, when, by whom, and what the exit status was. It does not know which
   * artifact the run produced, what version that artifact is, its hash, or what the result does not
   * cover. Those are left empty with a note saying so, because an envelope with a guessed hash is
   * worse than one that is visibly unfinished — the first passes a check it should have failed.
   *
   * status follows the exit code into `passed` or `failed`, and never into `observed`: the run
   * either completed or it did not, and softening that is the app editorialising about its own
   * work. */
  function draftEvidence(task, run) {
    const now = run.at || new Date().toISOString();
    return {
      evidence_id: `ev-${keyOf(task)}-${now.replace(/[^0-9]/g, '').slice(0, 14)}`,
      task_id: keyOf(task),
      claim_ids: [`claim-${keyOf(task)}-1`],
      artifact: '',
      artifact_version: '',
      artifact_sha256: '',
      environment: {
        folder: run.folder || '',
        permission_mode: run.permissionMode || '',
        runner: 'app-data-agent',
      },
      method: 'Chạy task qua Claude CLI từ buồng lái của app, không qua terminal.',
      command: run.command || '',
      expected_result: '',
      observed_result: run.exit === 0
        ? `CLI kết thúc với mã 0 sau ${run.durationMs || 0} ms.`
        : `CLI kết thúc với mã ${run.exit} sau ${run.durationMs || 0} ms.`,
      exit_status: typeof run.exit === 'number' ? run.exit : null,
      status: run.exit === 0 ? 'passed' : 'failed',
      captured_at: now,
      captured_by: run.actor || '',
      limitations: [
        'App chỉ ghi lại được việc CLI chạy xong với mã thoát nào. Nó không kiểm tra kết quả có đúng không.',
        'artifact, artifact_version và artifact_sha256 để trống: app không biết run này tạo ra artifact nào.',
        'expected_result để trống: chưa ai phát biểu kỳ vọng trước khi chạy.',
      ],
    };
  }

  /** The fields a drafted envelope leaves for a person, so the gap is reportable and not implied. */
  function evidenceGaps(envelope) {
    const gaps = [];
    for (const field of ['artifact', 'artifact_version', 'artifact_sha256', 'expected_result', 'captured_by']) {
      if (!String(envelope[field] || '').trim()) gaps.push(field);
    }
    return gaps;
  }

  return { NODE_W, NODE_H, GAP_X, GAP_Y, PAD, FINISHED, FAILED, GATE, ALLOWED, NEEDS_EVIDENCE,
    draftEvidence, evidenceGaps,
    keyOf, layer, layout, readyNow, criticalPath, runPlan, nextAction, statusPath, transitionsFor };
});
