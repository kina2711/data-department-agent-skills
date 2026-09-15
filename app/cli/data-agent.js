#!/usr/bin/env node
'use strict';

/* data-agent — the Data Department suite from a terminal.
 *
 * The Electron app and this command are two clients of one library. Neither owns the suite, the
 * config or the argv that runs Claude; core/ owns all three, so picking a suite in the app is
 * visible here and a permission mode cannot mean one thing in each door.
 *
 * Every listing command takes --json, because a terminal tool that can only be read by a person
 * is half a terminal tool.
 */

const fs = require('fs');
const path = require('path');
const { readSuite, contractCache } = require('../core/suite');
const { composePrompt, missingRequired } = require('../core/prompt');
const claude = require('../core/claude');
const config = require('../core/config');
const ui = require('./ui');

const VERSION = require('../package.json').version;

/* ---------- arguments ---------------------------------------------------------------------- */

function parseArgs(argv) {
  const flags = {};
  const positional = [];
  const sets = [];
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--set') { sets.push(argv[++i]); continue; }
    if (arg.startsWith('--')) {
      const [name, inline] = arg.slice(2).split('=');
      if (inline !== undefined) { flags[name] = inline; continue; }
      const next = argv[i + 1];
      if (next === undefined || next.startsWith('--')) { flags[name] = true; continue; }
      flags[name] = next;
      i += 1;
      continue;
    }
    positional.push(arg);
  }
  const values = {};
  for (const pair of sets) {
    const at = String(pair).indexOf('=');
    if (at > 0) values[pair.slice(0, at)] = pair.slice(at + 1);
  }
  return { flags, positional, values };
}

/* ---------- loading ------------------------------------------------------------------------ */

function loadSuite(flags) {
  const suitePath = config.resolveSuite({ explicit: flags.suite });
  if (!suitePath) {
    ui.fail('Không tìm thấy suite.',
      'Đứng trong thư mục suite, hoặc chạy `data-agent use <đường-dẫn>`, hoặc truyền --suite.');
  }
  let suite;
  try {
    suite = readSuite(suitePath);
  } catch (err) {
    ui.fail(`Không đọc được suite tại ${suitePath}`, err.message);
  }
  return { suitePath, suite };
}

const allTasks = (suite) => suite.skills.flatMap((s) => s.tasks.map((t) => ({ ...t, skill: s.id })));
const allJobs = (suite) => suite.skills.flatMap((s) => (s.jobs || []).map((j) => ({ ...j, skill: s.id })));

function matches(haystack, query) {
  if (!query || query === true) return true;
  const needle = String(query).toLowerCase();
  return String(haystack).toLowerCase().includes(needle);
}

/* ---------- commands ----------------------------------------------------------------------- */

const commands = {};

commands.skills = ({ flags }) => {
  const { suite } = loadSuite(flags);
  let rows = suite.skills;
  if (flags.search) {
    rows = rows.filter((s) => matches(`${s.id} ${s.name} ${s.description}`, flags.search));
  }
  if (flags.tier) {
    rows = rows.filter((s) => s.tasks.some((t) => t.modelTier === flags.tier));
  }
  if (flags.json) return ui.json(rows.map(({ tasks, ...rest }) => ({ ...rest, taskCount: tasks.length })));
  ui.title(`${rows.length} skill · suite ${suite.suiteVersion} · ${suite.taskTotal} task`);
  ui.table(
    ['SKILL', 'TASK', 'WAVE', 'TÊN'],
    rows.map((s) => [s.id, String(s.tasks.length), String(s.wave ?? '—'), s.name]),
  );
  ui.hint('data-agent tasks <skill>   ·   data-agent find "<việc bạn muốn làm>"');
};

commands.tasks = ({ flags, positional }) => {
  const { suite } = loadSuite(flags);
  const [skillId] = positional;
  let rows = allTasks(suite);
  if (skillId) {
    const skill = suite.skills.find((s) => s.id === skillId);
    if (!skill) ui.fail(`Không có skill ${skillId}`, ui.nearest(skillId, suite.skills.map((s) => s.id)));
    rows = skill.tasks.map((t) => ({ ...t, skill: skill.id }));
  }
  if (flags.search) rows = rows.filter((t) => matches(`${t.id} ${t.goal} ${(t.keywords || []).join(' ')}`, flags.search));
  if (flags.tier) rows = rows.filter((t) => t.modelTier === flags.tier);
  if (flags.risk) rows = rows.filter((t) => String(t.risk).startsWith(String(flags.risk)));
  if (flags.json) return ui.json(rows);
  ui.title(`${rows.length} task${skillId ? ` · ${skillId}` : ''}`);
  ui.table(
    ['TASK', 'RISK', 'TIER', 'MỤC TIÊU'],
    rows.map((t) => [t.id, t.risk || '—', t.modelTier || '—', t.goal || '']),
  );
  ui.hint('data-agent show <task-id>');
};

commands.show = ({ flags, positional }) => {
  const { suitePath, suite } = loadSuite(flags);
  const [taskId] = positional;
  if (!taskId) ui.fail('Thiếu task id.', 'data-agent show <task-id>');
  const task = allTasks(suite).find((t) => t.id === taskId);
  if (!task) ui.fail(`Không có task ${taskId}`, ui.nearest(taskId, allTasks(suite).map((t) => t.id)));
  const file = path.join(suitePath, 'skills', task.skill, 'references', 'tasks', `${taskId}.md`);
  const body = fs.existsSync(file) ? fs.readFileSync(file, 'utf8') : '';
  if (flags.json) return ui.json({ ...task, file, contract: body });
  ui.title(task.id);
  ui.fields({ skill: task.skill, risk: task.risk, tier: task.modelTier,
    'mục tiêu': task.goal, 'đầu ra': task.output, contract: file });
  if (!body) return ui.hint('Không đọc được file contract ở đường dẫn trên.');
  if (flags.full) { ui.rule(); process.stdout.write(body); return undefined; }
  ui.rule();
  process.stdout.write(body.split('\n').slice(0, 40).join('\n'));
  ui.hint('\n--full để xem toàn bộ contract');
  return undefined;
};

commands.find = ({ flags, positional }) => {
  const { suite } = loadSuite(flags);
  const query = positional.join(' ').trim();
  if (!query) ui.fail('Thiếu câu mô tả việc.', 'data-agent find "pipeline chạy lại bị trùng dữ liệu"');
  const words = query.toLowerCase().split(/\W+/).filter((w) => w.length > 2);
  const scored = allTasks(suite).map((t) => {
    const hay = `${t.id} ${t.goal} ${t.output} ${(t.keywords || []).join(' ')}`.toLowerCase();
    // Keyword hits count double: a task's keywords were chosen to be matched, its goal was not.
    const score = words.reduce((sum, w) => sum
      + (hay.includes(w) ? 1 : 0)
      + ((t.keywords || []).some((k) => String(k).toLowerCase().includes(w)) ? 1 : 0), 0);
    return { ...t, score };
  }).filter((t) => t.score > 0).sort((a, b) => b.score - a.score).slice(0, Number(flags.limit) || 8);
  if (flags.json) return ui.json(scored);
  if (!scored.length) {
    ui.title('Không khớp task nào');
    return ui.hint('Thử từ khoá cụ thể hơn, hoặc `data-agent skills` để xem toàn bộ.');
  }
  ui.title(`${scored.length} task khớp nhất`);
  ui.table(['TASK', 'SKILL', 'RISK', 'MỤC TIÊU'],
    scored.map((t) => [t.id, t.skill, t.risk || '—', t.goal || '']));
  ui.hint('Đây là gợi ý theo từ khoá, không phải định tuyến. Đọc contract trước khi chạy.');
  return undefined;
};

commands.jobs = ({ flags, positional }) => {
  const { suite } = loadSuite(flags);
  let rows = allJobs(suite);
  const [skillId] = positional;
  if (skillId) rows = rows.filter((j) => j.skill === skillId);
  if (flags.json) return ui.json(rows);
  ui.title(`${rows.length} việc dựng sẵn`);
  ui.table(['JOB', 'SKILL', 'TÊN'], rows.map((j) => [j.id, j.skill, j.ten || '']));
  ui.hint('data-agent job <job-id> --set <tham-số>=<giá-trị>');
  return undefined;
};

commands.job = async ({ flags, positional, values }) => {
  const { suitePath, suite } = loadSuite(flags);
  const [jobId] = positional;
  if (!jobId) ui.fail('Thiếu job id.', 'data-agent jobs  để xem danh sách');
  const job = allJobs(suite).find((j) => j.id === jobId);
  if (!job) ui.fail(`Không có job ${jobId}`, ui.nearest(jobId, allJobs(suite).map((j) => j.id)));

  if (flags.params || (!Object.keys(values).length && !flags.run)) {
    ui.title(job.ten || job.id);
    if (job.mo_ta) ui.para(job.mo_ta);
    ui.table(['THAM SỐ', 'BẮT BUỘC', 'NHÃN'],
      (job.thong_so || []).map((p) => [p.key, p.bat_buoc ? 'có' : '', p.nhan || '']));
    ui.hint(`data-agent job ${job.id} ${(job.thong_so || []).filter((p) => p.bat_buoc)
      .map((p) => `--set ${p.key}=…`).join(' ')}`);
    return undefined;
  }

  const labels = new Map((job.thong_so || []).map((p) => [p.key, p.nhan || p.key]));
  const missing = missingRequired(job, values);
  const prompt = composePrompt(job, values, missing.length ? labels : null);
  if (flags.json) return ui.json({ job: job.id, skill: job.skill, values, missing, prompt });
  ui.title(job.ten || job.id);
  ui.para(prompt);
  if (missing.length) {
    ui.warn(`Còn thiếu: ${missing.join(', ')}`);
    return undefined;
  }
  if (!flags.run) return ui.hint('Thêm --run --dir <thư-mục> để chạy prompt này.');
  return runPrompt({ flags, prompt, suitePath, skillId: job.skill, taskId: job.task_id });
};

commands.run = async ({ flags, positional }) => {
  const { suitePath, suite } = loadSuite(flags);
  const [target] = positional;
  if (!target) ui.fail('Thiếu task id hoặc skill id.', 'data-agent run <task-id> --dir .');
  const task = allTasks(suite).find((t) => t.id === target);
  const skill = suite.skills.find((s) => s.id === target);
  if (!task && !skill) {
    ui.fail(`Không có task hay skill nào tên ${target}`,
      ui.nearest(target, [...allTasks(suite).map((t) => t.id), ...suite.skills.map((s) => s.id)]));
  }
  const skillId = task ? task.skill : skill.id;
  const prompt = flags.prompt && flags.prompt !== true
    ? String(flags.prompt)
    : claude.defaultPrompt(skillId, task ? task.id : '');
  return runPrompt({
    flags, prompt, suitePath, skillId, taskId: task ? task.id : '',
    // The task declares a model *tier*, never a model name — the suite keeps it that way on
    // purpose, because tiers outlive model ids. Passing the tier through as --model sends
    // `--model standard`, which is not a model. So the tier is reported and the flag is the
    // user's to set.
    tier: task ? task.modelTier : '', risk: task ? task.risk : '',
  });
};

async function runPrompt({ flags, prompt, suitePath, skillId, taskId, tier, risk }) {
  const folder = path.resolve(String(flags.dir || process.cwd()));
  if (!fs.existsSync(folder)) ui.fail(`Thư mục không tồn tại: ${folder}`);
  const permissionMode = String(flags.perm || 'plan');
  const model = flags.model && flags.model !== true ? String(flags.model) : '';
  const options = { folder, prompt, suitePath, permissionMode, model, resume: flags.resume };

  if (flags['dry-run']) {
    ui.title('Sẽ chạy (không gửi gì)');
    ui.fields({ 'thư mục': folder, skill: skillId, task: taskId || '—', risk: risk || '—',
      'model tier': tier || '—', quyền: permissionMode,
      model: model || 'mặc định của CLI (--model để đặt)' });
    ui.rule();
    console.log(`claude ${claude.buildArgv(options).map(ui.quote).join(' ')}`);
    return 0;
  }

  // A run that may write announces it. `plan` is the default precisely so this line is rare.
  if (permissionMode !== 'plan') {
    ui.warn(`Chế độ ${permissionMode}: lần chạy này được phép sửa file trong ${folder}`);
  }
  ui.title(`${taskId || skillId}  ·  ${permissionMode}`);
  ui.fields({ 'thư mục': folder, risk: risk || '—', 'model tier': tier || '—' });
  if (tier === 'strong' && !model) {
    ui.warn('Task này khai tier strong. Không có --model thì CLI dùng model mặc định, '
      + 'có thể nhẹ hơn mức task yêu cầu.');
  }
  ui.rule();

  const stream = ui.eventStream({ json: Boolean(flags.json) });
  return new Promise((resolve) => {
    const started = claude.startRun(options, {
      onEvent: (ev) => stream.event(ev),
      onStderr: (text) => stream.stderr(text),
      onDone: ({ code, error }) => { stream.done({ code, error }); resolve(code === 0 ? 0 : 1); },
    });
    if (!started.ok) { ui.fail(started.error); resolve(1); }
    const stop = () => { try { started.child.kill('SIGTERM'); } catch { /* already gone */ } };
    process.on('SIGINT', stop);
  });
}

commands.use = ({ positional }) => {
  const [target] = positional;
  if (!target) ui.fail('Thiếu đường dẫn.', 'data-agent use /đường/dẫn/tới/suite');
  const resolved = path.resolve(target);
  if (!fs.existsSync(path.join(resolved, 'suite-manifest.yaml'))) {
    ui.fail(`${resolved} không phải thư mục suite`, 'Thiếu suite-manifest.yaml ở đó.');
  }
  const cfg = config.read();
  cfg.suitePath = resolved;
  const written = config.write(cfg);
  ui.ok(`Đã nhớ suite: ${resolved}`);
  ui.hint(`Ghi vào ${written}. App Data Agent đọc cùng tệp này.`);
  return undefined;
};

commands.workflows = ({ flags }) => {
  const { suitePath } = loadSuite(flags);
  const dir = path.join(suitePath, 'workflows');
  const files = fs.existsSync(dir) ? fs.readdirSync(dir).filter((f) => f.endsWith('.workflow.json')) : [];
  const rows = files.map((f) => {
    try {
      const doc = JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8'));
      return { id: doc.workflow_id || f.replace('.workflow.json', ''),
        tasks: (doc.tasks || []).length, status: doc.status || '—', file: path.join(dir, f) };
    } catch {
      return { id: f, tasks: 0, status: 'không đọc được', file: path.join(dir, f) };
    }
  });
  if (flags.json) return ui.json(rows);
  ui.title(`${rows.length} workflow`);
  ui.table(['WORKFLOW', 'TASK', 'TRẠNG THÁI'], rows.map((r) => [r.id, String(r.tasks), r.status]));
  return undefined;
};

commands.doctor = ({ flags }) => {
  const { spawnSync } = require('child_process');
  const suitePath = config.resolveSuite({ explicit: flags.suite });
  const which = spawnSync('claude', ['--version'], { encoding: 'utf8' });
  const checks = [
    ['claude trên PATH', which.status === 0, (which.stdout || which.stderr || '').trim().split('\n')[0]],
    ['suite tìm được', Boolean(suitePath), suitePath || 'chưa chọn — chạy `data-agent use <đường-dẫn>`'],
    ['suite là plugin', suitePath ? claude.isPluginDir(suitePath) : false,
      suitePath ? path.join(suitePath, '.claude-plugin') : ''],
    ['config ghi được', (() => {
      try { config.write(config.read()); return true; } catch { return false; }
    })(), config.defaultDir()],
  ];
  if (suitePath) {
    let ok = false;
    let detail = '';
    try {
      const suite = readSuite(suitePath);
      ok = suite.skills.length > 0;
      detail = `${suite.skills.length} skill · ${suite.taskTotal} task · suite ${suite.suiteVersion}`;
    } catch (err) { detail = err.message; }
    checks.push(['suite đọc được', ok, detail]);
  }
  if (flags.json) return ui.json(checks.map(([name, pass, detail]) => ({ name, pass, detail })));
  ui.title('Kiểm tra môi trường');
  for (const [name, pass, detail] of checks) ui.check(name, pass, detail);
  return checks.every(([, pass]) => pass) ? 0 : 1;
};

commands.version = () => { console.log(VERSION); };

commands.help = () => {
  ui.banner(VERSION);
  ui.section('Xem', [
    ['skills [--tier T] [--search Q]', 'liệt kê skill'],
    ['tasks [skill] [--search Q] [--risk R]', 'liệt kê task'],
    ['show <task-id> [--full]', 'xem một task contract'],
    ['find "<việc muốn làm>"', 'gợi ý task theo từ khoá'],
    ['workflows', 'liệt kê workflow'],
  ]);
  ui.section('Chạy', [
    ['run <task-id|skill> --dir .', 'chạy headless, log ra thẳng terminal'],
    ['  --model <tên-model>', 'task khai tier, không khai tên model — tên là của bạn'],
    ['  --perm plan|acceptEdits|bypassPermissions', 'mặc định plan: không sửa file nào'],
    ['  --dry-run', 'in argv sẽ chạy rồi dừng'],
    ['  --resume <session-id>', 'làm tiếp một phiên cũ'],
    ['jobs [skill]', 'liệt kê việc dựng sẵn'],
    ['job <job-id> --set k=v --run --dir .', 'điền tham số rồi chạy'],
  ]);
  ui.section('Thiết lập', [
    ['use <đường-dẫn>', 'nhớ thư mục suite (app dùng chung)'],
    ['doctor', 'kiểm tra claude, suite, config'],
  ]);
  ui.para('Mọi lệnh xem đều nhận --json. Suite lấy theo thứ tự: --suite, $DA_SUITE, '
    + 'lựa chọn đã nhớ, rồi thư mục hiện tại.');
};

/* ---------- entry -------------------------------------------------------------------------- */

async function main(argv) {
  const { flags, positional, values } = parseArgs(argv);
  const name = positional.shift() || (flags.version ? 'version' : 'help');
  const command = commands[name];
  if (!command) {
    ui.fail(`Không có lệnh ${name}`, ui.nearest(name, Object.keys(commands)) || 'data-agent help');
  }
  const code = await command({ flags, positional, values });
  return typeof code === 'number' ? code : 0;
}

if (require.main === module) {
  // Setting the code rather than calling process.exit: console.log to a pipe is asynchronous, so
  // exiting immediately truncates whatever has not flushed. Piping `--json` into another program
  // lost the tail of the array, which is a corrupt document rather than a short one.
  main(process.argv.slice(2))
    .then((code) => { process.exitCode = code; })
    .catch((err) => { ui.fail(err.message, err.stack); });
}

module.exports = { parseArgs, main, commands };
