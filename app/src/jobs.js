'use strict';

/* Preset jobs: a prompt with parameters.
 *
 * The template is a list of parts. A plain string is always included; an object with `neu` is
 * included only when that parameter was filled. That keeps optional sentences out of the prompt
 * instead of leaving empty placeholders in it. */

const jobState = {
  job: null,
  values: {},
};

const jq = (id) => document.getElementById(id);

// An unfilled slot collapsing to nothing leaves "cho , mức ." — a sentence that reads as broken
// rather than as incomplete. In the preview the slot keeps its label so the gap is legible; in
// the prompt actually sent it resolves, because a run is blocked until every required slot is set.
function fill(text, values, labels) {
  return text.replace(/\{([a-z0-9_]+)\}/g, (_m, key) => {
    const value = String(values[key] || '').trim();
    if (value) return value;
    return labels ? `⟨${labels.get(key) || key}⟩` : '';
  });
}

function composePrompt(job, values, labels) {
  const parts = [];
  for (const part of job.mau || []) {
    if (typeof part === 'string') {
      parts.push(fill(part, values, labels));
      continue;
    }
    const condition = String(part.neu || '').trim();
    if (condition && !String(values[condition] || '').trim()) continue;
    parts.push(fill(part.text || '', values, labels));
  }
  // A user-typed value rarely ends in punctuation, and two fragments joined by a space read as
  // one run-on sentence. Terminate each part rather than asking every template author to remember.
  return parts
    .map((p) => p.trim())
    .filter(Boolean)
    .map((p) => (/[.!?:;]$/.test(p) ? p : `${p}.`))
    .join(' ')
    .replace(/[ \t]+/g, ' ')
    .trim();
}

function missingRequired(job, values) {
  return (job.thong_so || [])
    .filter((p) => p.bat_buoc && !String(values[p.key] || '').trim())
    .map((p) => p.nhan);
}

/** The job list for one skill. */
function renderJobList(skill, onPick) {
  const box = jq('dJobs');
  box.innerHTML = '';
  const jobs = skill.jobs || [];
  if (!jobs.length) {
    box.innerHTML = '<p class="drawer-hint">Skill này chưa có công việc dựng sẵn. Chọn một task ở dưới, hoặc bỏ trống để Claude tự định tuyến.</p>';
    return;
  }
  for (const job of jobs) {
    const card = document.createElement('button');
    card.type = 'button';
    card.className = 'job-card';
    const h = document.createElement('span');
    h.className = 'job-name';
    h.textContent = job.ten;
    const d = document.createElement('span');
    d.className = 'job-desc';
    d.textContent = job.mo_ta;
    card.append(h, d);
    card.addEventListener('click', () => onPick(job));
    box.append(card);
  }
}

/** The parameter form for one job, with a live prompt preview. */
function renderJobForm(job, onChange, onBack) {
  jobState.job = job;
  jobState.values = {};

  const box = jq('paneForm');
  box.innerHTML = '';

  const back = document.createElement('button');
  back.type = 'button';
  back.className = 'guide-toggle';
  back.textContent = '← Chọn công việc khác';
  back.addEventListener('click', onBack);
  box.append(back);

  const title = document.createElement('h3');
  title.className = 'job-form-title';
  title.textContent = job.ten;
  box.append(title);

  const preview = document.createElement('div');
  preview.className = 'job-preview';

  const labels = new Map((job.thong_so || []).map((x) => [x.key, x.nhan]));
  const update = () => {
    const missing = missingRequired(job, jobState.values);
    // Preview keeps the labels so the gaps are readable; what would be sent has none.
    preview.textContent = composePrompt(job, jobState.values, labels) || '—';
    onChange(job, jobState.values, composePrompt(job, jobState.values), missing);
  };

  for (const param of job.thong_so || []) {
    const wrap = document.createElement('label');
    wrap.className = 'job-field';
    const label = document.createElement('span');
    label.textContent = param.nhan + (param.bat_buoc ? '' : ' (không bắt buộc)');
    wrap.append(label);

    let input;
    if (param.kieu === 'chon') {
      input = document.createElement('select');
      input.className = 'search';
      const blank = document.createElement('option');
      blank.value = '';
      blank.textContent = param.bat_buoc ? '— chọn —' : '— bỏ qua —';
      input.append(blank);
      for (const opt of param.chon || []) {
        const o = document.createElement('option');
        o.value = opt;
        o.textContent = opt;
        input.append(o);
      }
    } else if (param.nhieu_dong) {
      input = document.createElement('textarea');
      input.className = 'search';
      input.rows = 2;
    } else {
      input = document.createElement('input');
      input.className = 'search';
      input.type = 'text';
    }
    if (param.goi_y) input.placeholder = `vd: ${param.goi_y}`;
    input.addEventListener('input', () => {
      jobState.values[param.key] = input.value;
      update();
    });
    input.addEventListener('change', () => {
      jobState.values[param.key] = input.value;
      update();
    });
    wrap.append(input);
    box.append(wrap);
  }

  const pl = document.createElement('h4');
  pl.textContent = 'Prompt sẽ gửi';
  box.append(pl, preview);
  update();
}

const jobsUI = { renderJobList, renderJobForm, composePrompt, missingRequired };
// The composing and validation halves are pure; the tests reach them through require, the app
// through the global. Neither half touches the DOM until it is called.
if (typeof window !== 'undefined') window.jobsUI = jobsUI;
if (typeof module === 'object' && module.exports) module.exports = jobsUI;
