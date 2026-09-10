'use strict';

/* Transcript for an in-app run.
 *
 * The CLI's stream-json shape is not a contract this app controls, so every event is handled
 * defensively: known shapes get a proper row, anything else is shown as raw JSON rather than
 * silently dropped. A viewer that hides what it did not understand is worse than a noisy one. */

const runUI = { id: null, running: false, cost: 0, session: '', turns: 0, lastText: '', thinking: 0 };
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

/** One row that counts up, replaced in place, instead of a line per tick. */
function thinkingRow() {
  let el = rq('runLog').querySelector('.run-thinking .run-body');
  if (!el) {
    const wrap = document.createElement('div');
    wrap.className = 'run-row run-thinking';
    const label = document.createElement('span');
    label.className = 'run-label';
    label.textContent = 'suy nghĩ';
    el = document.createElement('div');
    el.className = 'run-body';
    wrap.append(label, el);
    rq('runLog').append(wrap);
  }
  return el;
}

/** Once real output arrives the counter has said everything it can. */
function clearThinking() {
  const row = rq('runLog').querySelector('.run-thinking');
  if (row) row.remove();
  runUI.thinking = 0;
}

function handleEvent(ev) {
  // Every event carries the session id. Holding the first one is what lets a reply resume this
  // conversation instead of starting a fresh one.
  if (!runUI.session && ev && ev.session_id) runUI.session = String(ev.session_id);

  if (!ev || typeof ev !== 'object') return;

  if (ev.type === 'system' && ev.subtype === 'init') {
    row('meta', 'phiên', `${(ev.tools || []).length} tool khả dụng · ${ev.model || ''}`.trim());
    return;
  }
  if (ev.type === 'rate_limit_event') return; // housekeeping, not part of the work

  /* Thinking ticks arrive every few hundred milliseconds and each one used to render its own line
   * of raw JSON, so a transcript was mostly `{"type":"system","subtype":"thinking_tokens",...}`
   * and the actual conversation was buried in it. One line that counts up says the same thing. */
  if (ev.type === 'system' && ev.subtype === 'thinking_tokens') {
    runUI.thinking = Number(ev.estimated_tokens) || runUI.thinking;
    thinkingRow().textContent = `đang suy nghĩ… ~${runUI.thinking} token`;
    return;
  }
  // Any other system housekeeping is noise unless it carries text a person can read.
  if (ev.type === 'system' && !ev.subtype) return;

  if (ev.type === 'assistant' && ev.message) {
    clearThinking();
    for (const block of ev.message.content || []) {
      if (block.type === 'text' && block.text.trim()) {
        runUI.lastText = block.text.trim();
        row('text', '', block.text);
      }
      else if (block.type === 'tool_use') row('tool', block.name || 'tool', describeToolInput(block.input));
      else if (block.type === 'thinking') row('meta', 'suy nghĩ', '…');
    }
    return;
  }
  if (ev.type === 'user' && ev.message) {
    clearThinking();
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
    // The closing event repeats the final assistant message, so every run ended with its own last
    // paragraph printed twice. Show it only when it says something the transcript does not.
    clearThinking();
    const closing = String(ev.result || '').trim();
    if (closing && closing !== runUI.lastText) row('text', '', closing);
    return;
  }

  row('meta', ev.type || 'event', JSON.stringify(ev).slice(0, 200));
}

function setRunning(on) {
  runUI.running = on;
  rq('runLog').classList.toggle('is-live', on);
  rq('runStart').disabled = on;
  rq('runStop').disabled = !on;
  rq('runStatus').textContent = on ? 'đang chạy…' : '';
}

window.runUI = {
  reset() {
    rq('runLog').innerHTML = '';
    runUI.cost = 0;
    runUI.session = '';
    runUI.turns = 0;
    runUI.lastText = '';
    runUI.thinking = 0;
    rq('runStatus').textContent = '';
    rq('replyBox').hidden = true;
    rq('reply').value = '';
  },
  // A reply continues the transcript rather than clearing it, because the thing being replied to
  // is the reason there is a reply.
  startTurn(text) {
    runUI.turns += 1;
    row('you', 'bạn', text);
    setRunning(true);
    rq('replyBox').hidden = true;
  },
  session: () => runUI.session,
  turns: () => runUI.turns,
  lastText: () => runUI.lastText,
  /* Pick up a session recorded before the app closed.
   *
   * Only the id crosses the restart. The transcript is gone and the log says so, because an empty
   * log under a heading that claims a conversation was restored is a lie the person discovers by
   * asking something the agent answers from context they cannot see. */
  adopt(record) {
    // window.runUI, not runUI: the const in this file is the state, and only the exposed object
    // carries the methods. Calling reset() on the state threw, and a thrown adopt looks exactly
    // like a resume that quietly did nothing.
    window.runUI.reset();
    runUI.session = String(record.sessionId);
    runUI.turns = Number(record.turns) || 0;
    runUI.lastText = String(record.lastText || '');
    row('meta', 'phiên cũ', `Nối lại phiên ${record.sessionId.slice(0, 8)}… — ${runUI.turns} lượt trước đó.`);
    row('meta', '', 'Claude vẫn nhớ toàn bộ cuộc trò chuyện cũ; phần hiển thị dưới đây bắt đầu lại từ trống.');
    if (runUI.lastText) row('text', 'câu cuối trước đó', runUI.lastText);
    // Nothing is running yet: leaving Stop live would offer to cancel a run that does not exist.
    setRunning(false);
    rq('runStatus').textContent = 'sẵn sàng nối tiếp';
    rq('replyBox').hidden = false;
    if (window.refreshReplyMode) window.refreshReplyMode();
    rq('reply').focus();
  },
  handleEvent,
  setRunning,
  finish(code, error) {
    setRunning(false);
    const cost = runUI.cost ? ` · ${runUI.cost.toFixed(4)} USD` : '';
    if (error) row('err', 'lỗi', error);
    rq('runStatus').textContent = code === 0 ? `xong${cost}` : `thoát mã ${code}${cost}`;
    // Replying needs a session to resume; without one the box would open a new conversation
    // wearing the same transcript, which is worse than not offering it.
    const canReply = code === 0 && Boolean(runUI.session);
    rq('replyBox').hidden = !canReply;
    // Record it now rather than on quit: a crash is exactly the case this feature exists for.
    if (runUI.session && window.saveRunSession) window.saveRunSession();
    if (canReply) {
      if (window.refreshReplyMode) window.refreshReplyMode();
      rq('reply').focus();
    }
  },
  newId() {
    runUI.id = `run-${Date.now()}`;
    return runUI.id;
  },
  currentId: () => runUI.id,
};
