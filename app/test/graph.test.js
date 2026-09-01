'use strict';

/* The layering rule and the cycle check, which are the two places a wrong answer draws a picture
 * that looks correct. A cycle rendered as a tree is indistinguishable from a tree. */

const { test } = require('node:test');
const assert = require('node:assert/strict');
const g = require('../src/lib/graph.js');

const t = (id, ...deps) => ({ task_id: id, depends_on: deps, status: 'planned' });

test('a chain lays out one column per link', () => {
  const depth = g.layer([t('a'), t('b', 'a'), t('c', 'b')]);
  assert.deepEqual([...depth], [['a', 0], ['b', 1], ['c', 2]]);
});

test('a diamond puts both middles in the same column and the join after them', () => {
  const depth = g.layer([t('a'), t('b', 'a'), t('c', 'a'), t('d', 'b', 'c')]);
  assert.equal(depth.get('b'), depth.get('c'));
  assert.equal(depth.get('d'), depth.get('b') + 1);
});

test('a node sits behind its deepest dependency, not its first', () => {
  // b is shallow, c is deep; d must clear c.
  const depth = g.layer([t('a'), t('b', 'a'), t('c', 'b'), t('d', 'a', 'c')]);
  assert.equal(depth.get('d'), 3);
});

test('a cycle has no layering and returns null rather than a plausible tree', () => {
  assert.equal(g.layer([t('x', 'y'), t('y', 'x')]), null);
  assert.equal(g.layer([t('x', 'z'), t('y', 'x'), t('z', 'y')]), null);
  assert.equal(g.layout([t('x', 'y'), t('y', 'x')]), null);
});

test('a dependency on a task the manifest does not contain is ignored, not fatal', () => {
  const depth = g.layer([t('a', 'somewhere-else')]);
  assert.equal(depth.get('a'), 0);
});

test('layout size grows with columns and rows and never goes negative on one node', () => {
  const one = g.layout([t('a')]);
  assert.equal(one.columns, 1);
  assert.equal(one.rows, 1);
  assert.ok(one.width > 0 && one.height > 0);
  const wide = g.layout([t('a'), t('b', 'a'), t('c', 'b')]);
  assert.ok(wide.width > one.width);
  const tall = g.layout([t('a'), t('b'), t('c')]);
  assert.ok(tall.height > one.height);
});

test('nodes in one column share an x and differ in y', () => {
  const laid = g.layout([t('a'), t('b'), t('c')]);
  const xs = new Set([...laid.pos.values()].map((p) => p.x));
  const ys = new Set([...laid.pos.values()].map((p) => p.y));
  assert.equal(xs.size, 1);
  assert.equal(ys.size, 3);
});

test('readyNow returns the roots first and unblocks as dependencies finish', () => {
  const tasks = [t('a'), t('b', 'a'), t('c', 'a'), t('d', 'b', 'c')];
  assert.deepEqual(g.readyNow(tasks), ['a']);
  tasks[0].status = 'complete';
  assert.deepEqual(g.readyNow(tasks), ['b', 'c']);
  tasks[1].status = 'approved';
  assert.deepEqual(g.readyNow(tasks), ['c']);
  tasks[2].status = 'released';
  assert.deepEqual(g.readyNow(tasks), ['d']);
});

test('a finished task is not offered again', () => {
  const tasks = [t('a')];
  tasks[0].status = 'complete';
  assert.deepEqual(g.readyNow(tasks), []);
});

test('a blocked or failed task is still ready to attempt', () => {
  // Failure is a state to retry from, not a state to hide the node in.
  const tasks = [t('a')];
  tasks[0].status = 'failed';
  assert.deepEqual(g.readyNow(tasks), ['a']);
});

test('the critical path is the longest chain, not merely a path', () => {
  const tasks = [t('a'), t('b', 'a'), t('c', 'b'), t('d', 'a'), t('e', 'c', 'd')];
  assert.deepEqual(g.criticalPath(tasks), ['a', 'b', 'c', 'e']);
});

test('a cyclic graph has no critical path', () => {
  assert.equal(g.criticalPath([t('x', 'y'), t('y', 'x')]), null);
});

/* The dry run. Its whole point is to be trustworthy before anything is executed, so the cases
 * below are the ones where a plan could look complete and not be. */

test('a chain plans one task per wave, a fan plans them together', () => {
  assert.equal(g.runPlan([t('a'), t('b', 'a'), t('c', 'b')]).waves.length, 3);
  const fan = g.runPlan([t('a'), t('b'), t('c')]);
  assert.equal(fan.waves.length, 1);
  assert.equal(fan.widest, 3);
});

test('a diamond takes three waves and the join is alone in the last', () => {
  const plan = g.runPlan([t('a'), t('b', 'a'), t('c', 'a'), t('d', 'b', 'c')]);
  assert.equal(plan.waves.length, 3);
  assert.deepEqual(plan.waves[1].tasks, ['b', 'c']);
  assert.deepEqual(plan.waves[2].tasks, ['d']);
});

test('finished tasks are not replanned and are counted separately', () => {
  const tasks = [t('a'), t('b', 'a')];
  tasks[0].status = 'complete';
  const plan = g.runPlan(tasks);
  assert.equal(plan.already, 1);
  assert.equal(plan.planned, 1);
  assert.deepEqual(plan.waves.map((w) => w.tasks), [['b']]);
});

test('a cycle strands its members instead of being left out of the plan', () => {
  const plan = g.runPlan([t('a'), t('x', 'y'), t('y', 'x')]);
  assert.deepEqual(plan.waves.map((w) => w.tasks), [['a']]);
  assert.deepEqual(plan.stranded.sort(), ['x', 'y']);
  assert.equal(plan.planned, 1);
});

test('a dependency outside the manifest does not strand the task', () => {
  const plan = g.runPlan([t('a', 'lives-elsewhere')]);
  assert.deepEqual(plan.stranded, []);
  assert.deepEqual(plan.waves[0].tasks, ['a']);
});

test('gates are reported in the wave they occur in, not as a stage of their own', () => {
  const tasks = [t('a'), t('b', 'a'), t('c', 'a')];
  tasks[1].risk_tier = 'R3-controlled';
  tasks[2].risk_tier = 'R1-reviewed';
  const plan = g.runPlan(tasks);
  assert.equal(plan.gates, 1);
  assert.deepEqual(plan.waves[1].gates, ['b']);
  assert.deepEqual(plan.waves[1].tasks, ['b', 'c']);
});

test('R4 counts as a gate and R2 does not', () => {
  const mk = (tier) => { const x = t('only'); x.risk_tier = tier; return g.runPlan([x]).gates; };
  assert.equal(mk('R4-critical'), 1);
  assert.equal(mk('R3-controlled'), 1);
  assert.equal(mk('R2-standard'), 0);
  assert.equal(mk(undefined), 0);
});

test('an empty manifest plans nothing rather than looping', () => {
  const plan = g.runPlan([]);
  assert.deepEqual(plan.waves, []);
  assert.deepEqual(plan.stranded, []);
});

/* nextAction is the cockpit's whole control flow. Each case below is an order-of-precedence
 * question: when two things are true at once, which one wins. */

test('an empty manifest has nothing to do', () => {
  assert.deepEqual(g.nextAction([]), { kind: 'empty' });
  assert.deepEqual(g.nextAction(undefined), { kind: 'empty' });
});

test('the first ready task is offered to run', () => {
  const action = g.nextAction([t('a'), t('b', 'a')]);
  assert.equal(action.kind, 'run');
  assert.equal(action.task, 'a');
  assert.deepEqual(action.alsoReady, []);
});

test('a gate is surfaced and stops the run rather than being executed', () => {
  const tasks = [t('a')];
  tasks[0].risk_tier = 'R3-controlled';
  const action = g.nextAction(tasks);
  assert.equal(action.kind, 'gate');
  assert.equal(action.task, 'a');
  assert.equal(action.risk, 'R3-controlled');
});

test('a gate outranks ordinary ready work in the same wave', () => {
  const tasks = [t('plain'), t('locked')];
  tasks[1].risk_tier = 'R4-critical';
  const action = g.nextAction(tasks);
  assert.equal(action.kind, 'gate');
  assert.equal(action.task, 'locked');
  assert.deepEqual(action.alsoReady, ['plain']);
});

test('a failure outranks everything, including a gate', () => {
  const tasks = [t('broken'), t('locked')];
  tasks[0].status = 'failed';
  tasks[1].risk_tier = 'R4-critical';
  const action = g.nextAction(tasks);
  assert.equal(action.kind, 'failed');
  assert.deepEqual(action.tasks, ['broken']);
});

test('blocked counts as a failure to surface, not as work to skip past', () => {
  const tasks = [t('a')];
  tasks[0].status = 'blocked';
  assert.equal(g.nextAction(tasks).kind, 'failed');
});

test('a task already running is reported rather than a second one started', () => {
  const tasks = [t('a'), t('b')];
  tasks[0].status = 'in-progress';
  const action = g.nextAction(tasks);
  assert.equal(action.kind, 'running');
  assert.equal(action.task, 'a');
});

test('all finished means done', () => {
  const tasks = [t('a'), t('b', 'a')];
  tasks[0].status = 'complete';
  tasks[1].status = 'released';
  assert.deepEqual(g.nextAction(tasks), { kind: 'done' });
});

test('unreachable work is reported as stranded once nothing is ready', () => {
  const action = g.nextAction([t('x', 'y'), t('y', 'x')]);
  assert.equal(action.kind, 'stranded');
  assert.deepEqual(action.tasks.sort(), ['x', 'y']);
});
