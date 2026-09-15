'use strict';

/* Drawing a terminal interface that reads well on a real terminal.
 *
 * Two rules decide most of this. Colour is written to a TTY and stripped everywhere else, so a
 * piped or redirected run produces text a script can parse instead of escape codes it cannot.
 * And width is measured rather than assumed: Vietnamese carries combining marks, so a column
 * aligned by `String.length` drifts by one cell per diacritic and the table stops lining up
 * exactly where the content is most Vietnamese.
 */

const ESC = '[';
const TTY = process.stdout.isTTY && !process.env.NO_COLOR;
const WIDTH = Math.max(60, Math.min(process.stdout.columns || 100, 120));

const paint = (code) => (text) => (TTY ? `${ESC}${code}m${text}${ESC}0m` : String(text));
const c = {
  dim: paint('2'), bold: paint('1'), red: paint('31'), green: paint('32'),
  yellow: paint('33'), blue: paint('34'), magenta: paint('35'), cyan: paint('36'),
};

/* A combining mark occupies no column of its own; CJK and emoji occupy two. Counting code points
 * gets both wrong, in opposite directions. */
function width(text) {
  let total = 0;
  for (const ch of String(text)) {
    const code = ch.codePointAt(0);
    if (code >= 0x0300 && code <= 0x036f) continue;          // combining diacritics
    if (code >= 0x1ab0 && code <= 0x1aff) continue;
    if (code >= 0x20d0 && code <= 0x20ff) continue;
    if (code >= 0xfe20 && code <= 0xfe2f) continue;
    const wide = (code >= 0x1100 && code <= 0x115f)
      || (code >= 0x2e80 && code <= 0xa4cf)
      || (code >= 0xac00 && code <= 0xd7a3)
      || (code >= 0xf900 && code <= 0xfaff)
      || (code >= 0xff00 && code <= 0xff60)
      || (code >= 0x1f300 && code <= 0x1f9ff);
    total += wide ? 2 : 1;
  }
  return total;
}

const pad = (text, size) => String(text) + ' '.repeat(Math.max(0, size - width(text)));

function clip(text, size) {
  const raw = String(text ?? '');
  if (width(raw) <= size) return raw;
  let out = '';
  for (const ch of raw) {
    if (width(out + ch) > size - 1) break;
    out += ch;
  }
  return `${out}…`;
}

const out = (line = '') => console.log(line);

function banner(version) {
  const inner = WIDTH - 4;
  const left = `Data Agent  ·  v${version}`;
  out();
  out(c.cyan(`  ┌${'─'.repeat(inner)}┐`));
  out(`${c.cyan('  │ ')}${c.bold('Data Agent')}${c.dim(`  ·  v${version}`)}${pad('', inner - width(left) - 1)}${c.cyan('│')}`);
  out(c.cyan(`  └${'─'.repeat(inner)}┘`));
}

function title(text) {
  out();
  out(`  ${c.bold(text)}`);
  out(`  ${c.dim('─'.repeat(Math.min(width(text), WIDTH - 4)))}`);
}

const rule = () => out(c.dim(`  ${'─'.repeat(WIDTH - 4)}`));
const hint = (text) => { out(); out(c.dim(`  ${text}`)); };
const ok = (text) => out(`  ${c.green('✓')} ${text}`);
const warn = (text) => out(`  ${c.yellow('!')} ${text}`);

function wrap(text, size) {
  const lines = [];
  for (const paragraph of String(text).split('\n')) {
    let line = '';
    for (const word of paragraph.split(/\s+/)) {
      if (!word) continue;
      if (line && width(`${line} ${word}`) > size) { lines.push(line); line = word; continue; }
      line = line ? `${line} ${word}` : word;
    }
    lines.push(line);
  }
  return lines;
}

const para = (text) => { out(); for (const line of wrap(String(text), WIDTH - 4)) out(`  ${line}`); };

function table(headers, rows) {
  if (!rows.length) { hint('(không có dòng nào)'); return; }
  const columns = headers.map((h, i) => Math.max(width(h), ...rows.map((r) => width(r[i] ?? ''))));
  // The last column absorbs whatever is left, and is the one allowed to be cut.
  const fixed = columns.slice(0, -1).reduce((sum, n) => sum + n + 2, 0);
  columns[columns.length - 1] = Math.max(10, WIDTH - 4 - fixed);
  out();
  out(`  ${c.dim(headers.map((h, i) => pad(h, columns[i])).join('  ').trimEnd())}`);
  for (const row of rows) {
    const cells = row.map((cell, i) => (i === row.length - 1
      ? clip(cell, columns[i]) : pad(clip(cell, columns[i]), columns[i])));
    out(`  ${c.cyan(cells[0])}  ${cells.slice(1).join('  ').trimEnd()}`);
  }
}

function fields(map) {
  const keys = Object.keys(map);
  const size = Math.max(...keys.map(width));
  out();
  for (const key of keys) out(`  ${c.dim(pad(key, size))}  ${map[key] ?? '—'}`);
}

function section(heading, rows) {
  out();
  out(`  ${c.bold(heading)}`);
  const size = Math.max(...rows.map(([left]) => width(left)));
  for (const [left, right] of rows) out(`    ${c.cyan(pad(left, size))}  ${c.dim(right)}`);
}

function check(name, pass, detail) {
  out(`  ${pass ? c.green('✓') : c.red('✗')} ${pad(name, 20)} ${c.dim(clip(detail || '', WIDTH - 28))}`);
}

/** Levenshtein, only to answer "did you mean". Suggesting nothing beats suggesting nonsense. */
function nearest(input, options) {
  const distance = (a, b) => {
    const prev = Array.from({ length: b.length + 1 }, (_, i) => i);
    for (let i = 1; i <= a.length; i += 1) {
      let carry = prev[0];
      prev[0] = i;
      for (let j = 1; j <= b.length; j += 1) {
        const temp = prev[j];
        prev[j] = Math.min(prev[j] + 1, prev[j - 1] + 1, carry + (a[i - 1] === b[j - 1] ? 0 : 1));
        carry = temp;
      }
    }
    return prev[b.length];
  };
  const ranked = options
    .map((option) => ({ option, d: distance(String(input), option) }))
    .sort((a, b) => a.d - b.d)
    .filter((r) => r.d <= Math.max(3, Math.floor(String(input).length / 2)));
  return ranked.length ? `Ý bạn là: ${ranked.slice(0, 3).map((r) => r.option).join(', ')}?` : '';
}

function fail(message, detail) {
  out();
  out(`  ${c.red('✗')} ${c.bold(message)}`);
  if (detail) out(`    ${c.dim(detail)}`);
  out();
  process.exit(1);
}

const json = (value) => { console.log(JSON.stringify(value, null, 2)); };

/**
 * Render a run as it streams.
 *
 * A headless run emits structured events, and the useful shape for a terminal is one line per
 * thing that happened plus the assistant's own text in full. Tool calls are named rather than
 * dumped: the input of a write is the file being written, and printing the whole payload buries
 * the one fact the reader is watching for.
 */
function eventStream({ json: asJson } = {}) {
  let sessionId = '';
  let tools = 0;
  const started = Date.now();

  const label = (block) => {
    const input = block.input || {};
    const target = input.file_path || input.path || input.pattern || input.command || input.url || '';
    return target ? `${block.name} ${c.dim(clip(target, WIDTH - 20))}` : block.name;
  };

  return {
    event(ev) {
      if (asJson) { console.log(JSON.stringify(ev)); return; }
      if (ev.session_id && !sessionId) {
        sessionId = ev.session_id;
        out(`  ${c.dim('session')}  ${sessionId}`);
      }
      if (ev.type === 'raw') { out(c.dim(`  ${ev.text}`)); return; }
      const content = ev.message && ev.message.content;
      if (!Array.isArray(content)) return;
      for (const block of content) {
        if (block.type === 'text' && String(block.text).trim()) {
          out();
          for (const line of wrap(block.text, WIDTH - 4)) out(`  ${line}`);
        } else if (block.type === 'tool_use') {
          tools += 1;
          out(`  ${c.magenta('▸')} ${label(block)}`);
        } else if (block.type === 'thinking') {
          out(`  ${c.dim('· đang suy nghĩ')}`);
        }
      }
    },
    stderr(text) {
      const trimmed = String(text).trim();
      if (trimmed) out(c.yellow(`  ${trimmed}`));
    },
    done({ code, error }) {
      if (asJson) {
        console.log(JSON.stringify({ type: 'done', code, error, session_id: sessionId }));
        return;
      }
      const seconds = ((Date.now() - started) / 1000).toFixed(1);
      out();
      rule();
      if (error) { out(`  ${c.red('✗')} ${error}`); return; }
      const mark = code === 0 ? c.green('✓') : c.red('✗');
      out(`  ${mark} kết thúc mã ${code}  ${c.dim(`· ${tools} tool · ${seconds}s`)}`);
      if (sessionId) out(c.dim(`  làm tiếp:  data-agent run … --resume ${sessionId}`));
    },
  };
}

const quote = (arg) => (/^[\w@%+=:,./-]+$/.test(arg) ? arg : `'${String(arg).replace(/'/g, "'\\''")}'`);

module.exports = {
  banner, title, rule, para, hint, ok, warn, table, fields, section, check,
  nearest, fail, json, eventStream, quote, width, wrap, clip, c, WIDTH,
};
