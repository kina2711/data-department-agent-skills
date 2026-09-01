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
