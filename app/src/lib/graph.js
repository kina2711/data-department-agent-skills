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

  return { NODE_W, NODE_H, GAP_X, GAP_Y, PAD, FINISHED, keyOf, layer, layout, readyNow, criticalPath };
});
