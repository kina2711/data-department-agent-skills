'use strict';

/* Transcript for an in-app run.
 *
 * The CLI's stream-json shape is not a contract this app controls, so every event is handled
 * defensively: known shapes get a proper row, anything else is shown as raw JSON rather than
 * silently dropped. A viewer that hides what it did not understand is worse than a noisy one. */

const runUI = { id: null, running: false, cost: 0 };
const rq = (id) => document.getElementById(id);

function row(kind, label, body) {
  const el = document.createElement('div');
  el.className = `run-row run-${kind}`;
  if (label) {
    const l = document.createElement('span');
    l.className = 'run-label';
    l.textContent = label;
    el.append(l);
  }
  const b = document.createElement('div');
  b.className = 'run-body';
  b.textContent = body;
  el.append(b);
  rq('runLog').append(el);
  rq('runLog').scrollTop = rq('runLog').scrollHeight;
  return el;
}

function describeToolInput(input) {
  if (!input || typeof input !== 'object') return '';
  for (const key of ['file_path', 'path', 'command', 'pattern', 'url', 'query', 'prompt']) {
    if (input[key]) return String(input[key]).slice(0, 160);
  }
  return Object.keys(input).join(', ').slice(0, 160);
}

function handleEvent(ev) {
  if (!ev || typeof ev !== 'object') return;

  if (ev.type === 'system' && ev.subtype === 'init') {
    row('meta', 'phiên', `${(ev.tools || []).length} tool khả dụng · ${ev.model || ''}`.trim());
    return;
  }
  if (ev.type === 'rate_limit_event') return; // housekeeping, not part of the work

  if (ev.type === 'assistant' && ev.message) {
    for (const block of ev.message.content || []) {
      if (block.type === 'text' && block.text.trim()) row('text', '', block.text);
      else if (block.type === 'tool_use') row('tool', block.name || 'tool', describeToolInput(block.input));
      else if (block.type === 'thinking') row('meta', 'suy nghĩ', '…');
    }
    return;
  }
  if (ev.type === 'user' && ev.message) {
    for (const block of ev.message.content || []) {
      if (block.type === 'tool_result') {
        const text = typeof block.content === 'string'
          ? block.content
          : (block.content || []).map((c) => c.text || '').join('\n');
        row('result', 'kết quả', String(text).slice(0, 600));
      }
    }
    return;
  }
  if (ev.type === 'raw') {
    row('meta', '', ev.text);
    return;
  }

  // The terminal event carries cost and stop reason; its `type` is not relied upon.
  if (ev.total_cost_usd !== undefined || ev.stop_reason !== undefined) {
    if (typeof ev.total_cost_usd === 'number') runUI.cost = ev.total_cost_usd;
    if (ev.result) row('text', '', String(ev.result));
    return;
  }

  row('meta', ev.type || 'event', JSON.stringify(ev).slice(0, 200));
}

function setRunning(on) {
  runUI.running = on;
  rq('runStart').disabled = on;
  rq('runStop').disabled = !on;
  rq('runStatus').textContent = on ? 'đang chạy…' : '';
}

window.runUI = {
  reset() {
    rq('runLog').innerHTML = '';
    runUI.cost = 0;
    rq('runStatus').textContent = '';
  },
  handleEvent,
  setRunning,
  finish(code, error) {
    setRunning(false);
    const cost = runUI.cost ? ` · ${runUI.cost.toFixed(4)} USD` : '';
    if (error) row('err', 'lỗi', error);
    rq('runStatus').textContent = code === 0 ? `xong${cost}` : `thoát mã ${code}${cost}`;
  },
  newId() {
    runUI.id = `run-${Date.now()}`;
    return runUI.id;
  },
  currentId: () => runUI.id,
};
