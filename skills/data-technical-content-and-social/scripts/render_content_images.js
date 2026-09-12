'use strict';

/* Turn an image spec into actual PNG files.
 *
 * The suite could already describe a picture — a diagram brief, a carousel script — and describing
 * a picture is not having one. A post needs a file to attach, and a brief cannot be attached.
 *
 * Rendering runs under the app's Electron, which is Chromium, so there is no new dependency and no
 * headless-browser install. Three kinds, because they are the three a technical post actually
 * carries: code with syntax colour, a cheatsheet table, and a diagram supplied as SVG.
 *
 * What it deliberately cannot do is invent a screenshot of a real screen. A screenshot is evidence
 * that something ran, and generating one would be manufacturing that evidence. Take those
 * yourself and drop them in beside the rendered files.
 *
 * Usage:
 *   app/node_modules/electron/dist/electron --no-sandbox \
 *     skills/data-technical-content-and-social/scripts/render_content_images.js spec.json
 */

const { app, BrowserWindow, nativeImage } = require('electron');
const fs = require('node:fs');
const path = require('node:path');

const SPEC = process.argv.find((a) => a.endsWith('.json'));

// Colours chosen to survive both a light and a dark feed, and to stay legible after the
// aggressive recompression every social platform applies.
const CSS = `
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #0d1117; color: #e6edf3; font: 15px/1.6 ui-sans-serif, "Segoe UI", system-ui, sans-serif;
         padding: 38px 42px; -webkit-font-smoothing: antialiased; }
  .title { font-size: 25px; font-weight: 680; letter-spacing: -.015em; margin-bottom: 6px; color: #fff; }
  .sub { font-size: 14px; color: #8b949e; margin-bottom: 24px; }
  pre { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 22px 24px;
        /* JetBrains Mono first, and the reason is measurable rather than aesthetic: "chỉ lấy"
           rendered with the marks detached, because the fallback font has no U+1EC9. A charset
           query over installed fonts says JetBrains Mono carries it and DejaVu Sans Mono does not.
           A pipeline that writes Vietnamese cannot ship images that break Vietnamese. */
        font: 15px/1.72 "JetBrainsMono Nerd Font Mono", "JetBrains Mono", "Noto Sans Mono",
              ui-monospace, Menlo, monospace;
        white-space: pre; color: #e6edf3; }
  .kw { color: #ff7b72; } .str { color: #a5d6ff; }
  .num { color: #79c0ff; } .cmt { color: #8b949e; font-style: italic; }
  table { border-collapse: collapse; width: 100%; }
  th, td { text-align: left; padding: 11px 15px; border-bottom: 1px solid #21262d; vertical-align: top; }
  th { font-size: 12px; text-transform: uppercase; letter-spacing: .05em; color: #8b949e; font-weight: 620; }
  td { font-size: 14.5px; }
  td code, th code { font-family: "JetBrainsMono Nerd Font Mono", "JetBrains Mono", ui-monospace, Menlo, monospace; color: #a5d6ff; font-size: 13.5px; }
  tr:last-child td { border-bottom: 0; }
  .note { margin-top: 20px; font-size: 13px; color: #8b949e; border-left: 2px solid #30363d; padding-left: 12px; }
  .foot { margin-top: 26px; font-size: 12.5px; color: #6e7681; }
  svg { max-width: 100%; height: auto; display: block; }
`;

const esc = (s) => String(s).replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));

/* Enough highlighting to read a query at a glance, and no more.
 *
 * Comments and strings are matched first and parked, because a keyword inside a string is not a
 * keyword, and colouring it there is the classic way a naive highlighter announces itself. The
 * parking marker is ordinary text rather than a control character, so the file stays greppable. */
const KEYWORDS = {
  sql: /\b(SELECT|FROM|WHERE|GROUP BY|ORDER BY|HAVING|JOIN|LEFT|RIGHT|INNER|FULL|OUTER|ON|AS|WITH|UNION|ALL|INTERSECT|EXCEPT|CASE|WHEN|THEN|ELSE|END|OVER|PARTITION BY|DISTINCT|LIMIT|INSERT|UPDATE|DELETE|CREATE|TABLE|VIEW|AND|OR|NOT|NULL|IS|IN|EXISTS|BETWEEN|LIKE|ASC|DESC|RANGE|ROWS|PRECEDING|FOLLOWING|FILTER)\b/gi,
  python: /\b(def|class|return|if|elif|else|for|while|import|from|as|with|try|except|finally|raise|lambda|None|True|False|and|or|not|in|is|yield|async|await)\b/g,
  bash: /\b(if|then|fi|for|do|done|while|case|esac|function|export|local|return|echo)\b/g,
};

function highlight(code, lang) {
  const parked = [];
  const park = (text) => `@@PARK${parked.push(text) - 1}@@`;

  let out = esc(code)
    .replace(/(--[^\n]*|#[^\n]*|\/\/[^\n]*)/g, (m) => park(`<span class="cmt">${m}</span>`))
    .replace(/('(?:[^'\\]|\\.)*'|"(?:[^"\\]|\\.)*")/g, (m) => park(`<span class="str">${m}</span>`));

  const kw = KEYWORDS[String(lang || '').toLowerCase()];
  if (kw) out = out.replace(kw, (m) => `<span class="kw">${m}</span>`);
  out = out.replace(/\b(\d+(?:\.\d+)?)\b/g, '<span class="num">$1</span>');
  return out.replace(/@@PARK(\d+)@@/g, (_m, i) => parked[Number(i)]);
}

function body(image) {
  const head = `<div class="title">${esc(image.title || '')}</div>`
    + (image.subtitle ? `<div class="sub">${esc(image.subtitle)}</div>` : '');
  const foot = image.footer ? `<div class="foot">${esc(image.footer)}</div>` : '';
  const note = image.note ? `<div class="note">${esc(image.note)}</div>` : '';

  if (image.kind === 'code') {
    return `${head}<pre>${highlight(image.code || '', image.lang)}</pre>${note}${foot}`;
  }
  if (image.kind === 'cheatsheet') {
    const cols = image.columns || [];
    const header = cols.length ? `<tr>${cols.map((c) => `<th>${esc(c)}</th>`).join('')}</tr>` : '';
    const rows = (image.rows || []).map((r) => `<tr>${r.map(
      (cell) => `<td>${esc(cell).replace(/`([^`]+)`/g, (_m, c) => `<code>${c}</code>`)}</td>`).join('')}</tr>`);
    return `${head}<table>${header}${rows.join('')}</table>${note}${foot}`;
  }
  if (image.kind === 'svg') {
    // Inserted as authored, so the diagram belongs to whoever drew it rather than to this script.
    return `${head}${image.svg || ''}${note}${foot}`;
  }
  throw new Error(`unknown image kind: ${image.kind}`);
}

async function render(win, image, outDir, width) {
  const html = `<!doctype html><meta charset="utf-8"><style>${CSS}</style>`
    + `<div id="root">${body(image)}</div>`;
  await win.loadURL('data:text/html;charset=utf-8,' + encodeURIComponent(html));
  // Size to the content: nothing cropped at the bottom, no dead space padded underneath.
  const height = await win.webContents.executeJavaScript(
    'Math.ceil(document.getElementById("root").getBoundingClientRect().bottom) + 38');
  win.setContentSize(width, Math.max(220, Math.min(4000, height)));
  await new Promise((done) => setTimeout(done, 140));
  const shot = await win.webContents.capturePage();
  const file = path.join(outDir, `${image.id}.png`);
  fs.writeFileSync(file, shot.toPNG());
  return { file, height };
}

app.disableHardwareAcceleration();
app.commandLine.appendSwitch('disable-gpu');

app.whenReady().then(async () => {
  if (!SPEC || !fs.existsSync(SPEC)) {
    console.error('usage: electron render_content_images.js <spec.json>');
    app.exit(2);
    return;
  }
  const spec = JSON.parse(fs.readFileSync(SPEC, 'utf8'));
  const outDir = path.resolve(spec.out || 'images');
  const width = Number(spec.width) || 1200;
  fs.mkdirSync(outDir, { recursive: true });

  const win = new BrowserWindow({
    width, height: 800, show: false,
    webPreferences: { offscreen: true, nodeIntegration: false, contextIsolation: true },
  });

  const written = [];
  const failed = [];
  for (const image of spec.images || []) {
    try {
      const { file, height } = await render(win, image, outDir, width);
      written.push({ id: image.id, file, width, height });
      console.log(`wrote ${path.relative(process.cwd(), file)}  ${width}x${height}`);
    } catch (err) {
      failed.push({ id: image.id, error: err.message });
      console.error(`FAILED ${image.id}: ${err.message}`);
    }
  }
  fs.writeFileSync(path.join(outDir, 'render-report.json'),
    JSON.stringify({ written, failed, rendered_at: new Date().toISOString() }, null, 2) + '\n');
  console.log(`\n${written.length} anh, ${failed.length} loi -> ${outDir}`);
  app.exit(failed.length ? 1 : 0);
});
