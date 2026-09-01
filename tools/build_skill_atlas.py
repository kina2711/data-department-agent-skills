#!/usr/bin/env python3
"""Draw the whole suite as one tree, from the repository root down to a single task.

The only tree that existed was hand-drawn, in section 2 of docs/skill-map.md, and it had drifted:
28 skills listed against 33 on disk. Nobody noticed, because the generator reads a Python dict and
the picture is decorative. A hand-drawn map of a system that changes weekly is a map of last
quarter.

Four levels, and every one comes from something a person wrote rather than from a rule invented
here:

  root    the repository
  wave    the rollout waves authored in skill-map section 40
  skill   the SKILL.md files on disk
  shard   the catalog-*.md verb shards inside each skill
  task    task-catalog.json

Skills that belong to no wave are reported as unplaced rather than filed somewhere plausible. Five
of them are unplaced right now, all added after section 40 was last written, and putting them into
a wave here would be inventing an ordering that nobody decided.

It also rewrites the section 2 tree between generated markers, so the one picture in the canonical
document stops being a thing that can drift.

It reads structure. A tree tells you what exists and how it nests; it says nothing about whether
the arrangement is a good one.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
MAP = ROOT / "docs" / "skill-map.md"
OUT = ROOT / "docs" / "skill-atlas.json"
PAGE = ROOT / "docs" / "skill-atlas.html"

HTML_HEAD = """<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Bản đồ bộ skill</title>
<style>
:root {
  color-scheme: dark;
  --ink: #e8ecf4; --dim: #7b869c; --faint: #39415400;
  --bg: #080b12; --panel: #0e131d; --line: #1e2636;
  --control: #b0567f; --request-to-analytics: #3fb6a8; --platform: #4a8fd4;
  --ai-ml: #8b6fd4; --specialised: #c98a3e; --unplaced: #7b869c;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink);
  font: 14px/1.55 ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; }
body::before { content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 0;
  background-image: linear-gradient(var(--line) 1px, transparent 1px),
                    linear-gradient(90deg, var(--line) 1px, transparent 1px);
  background-size: 44px 44px; opacity: .30; }
.wrap { position: relative; z-index: 1; max-width: 1180px; margin: 0 auto; padding: 28px 20px 72px; }
header { text-align: center; margin-bottom: 6px; }
h1 { font-size: 15px; letter-spacing: .22em; text-transform: uppercase; color: var(--dim);
  font-weight: 600; margin: 0 0 4px; }
.root { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 20px;
  color: var(--ink); margin: 0 0 6px; }
.tally { color: var(--dim); font-size: 13px; margin: 0 0 22px; }
.tally b { color: var(--ink); font-weight: 600; }
.band { border: 1px dashed var(--line); border-radius: 12px; padding: 14px 16px 18px;
  margin-bottom: 16px; position: relative; }
.band-label { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12.5px;
  color: var(--dim); margin-bottom: 12px; }
.band-label b { color: var(--ink); font-weight: 600; }
.band-count { float: right; color: var(--dim); font-size: 12px; }
.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(226px, 1fr)); gap: 11px; }
.card { background: var(--panel); border: 1px solid var(--line); border-left: 3px solid var(--tone);
  border-radius: 9px; padding: 11px 13px; cursor: pointer; text-align: left; color: inherit;
  font: inherit; transition: border-color .16s, box-shadow .16s, opacity .16s, transform .16s; }
.card:hover { border-color: var(--tone); transform: translateY(-1px); }
.card:focus-visible { outline: 2px solid var(--tone); outline-offset: 2px; }
.card .nm { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 13px;
  color: var(--ink); word-break: break-word; }
.card .meta { color: var(--dim); font-size: 11.5px; margin-top: 5px; }
.pip { display: inline-block; width: 6px; height: 6px; border-radius: 50%; margin-right: 5px;
  vertical-align: 1px; background: var(--tone); }
body.focusing .card { opacity: .26; }
body.focusing .card.lit { opacity: 1; border-color: var(--tone);
  box-shadow: 0 0 0 1px var(--tone), 0 0 22px -6px var(--tone); }
.panel { position: fixed; inset: auto 0 0 0; z-index: 3; background: var(--panel);
  border-top: 1px solid var(--line); max-height: 62vh; overflow: auto;
  box-shadow: 0 -18px 44px -22px #000; }
.panel-in { max-width: 1180px; margin: 0 auto; padding: 16px 20px 26px; }
.panel h2 { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 16px;
  margin: 0 0 4px; }
.panel .desc { color: var(--dim); font-size: 13px; margin: 0 0 14px; max-width: 78ch; }
.close { float: right; background: none; border: 1px solid var(--line); color: var(--dim);
  border-radius: 6px; padding: 4px 11px; cursor: pointer; font: inherit; font-size: 12px; }
.close:hover { color: var(--ink); border-color: var(--dim); }
.shard { margin-bottom: 13px; }
.shard h3 { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12.5px;
  color: var(--dim); font-weight: 600; margin: 0 0 6px; }
.tasks { display: flex; flex-wrap: wrap; gap: 5px; }
.task { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 11.5px;
  border: 1px solid var(--line); border-radius: 5px; padding: 3px 8px; color: var(--dim); }
.task[data-risk^="R3"] { border-color: #7a4a2e; color: #d79a63; }
.task[data-risk^="R4"] { border-color: #7d3242; color: #e3798f; }
.note { border: 1px solid var(--line); border-left: 3px solid var(--unplaced); border-radius: 9px;
  padding: 12px 14px; color: var(--dim); font-size: 13px; margin: 22px 0 0; }
.note b { color: var(--ink); font-weight: 600; }
.foot { color: var(--dim); font-size: 12px; margin-top: 26px; text-align: center; }
@media (max-width: 620px) { .cards { grid-template-columns: 1fr; } }
</style>
<div class="wrap">
<header>
  <h1>Bản đồ bộ skill</h1>
  <p class="root">__ROOT__</p>
  <p class="tally"><b>__SKILLS__</b> skill · <b>__TASKS__</b> task · <b>__WAVES__</b> băng triển khai</p>
</header>
__BANDS__
__NOTE__
<p class="foot">Sinh từ <code>tools/build_skill_atlas.py</code>. Wave lấy từ skill-map mục 40,
skill từ SKILL.md trên đĩa, shard từ catalog-*.md, task từ task-catalog.json.
Bấm một thẻ để soi; bấm lại hoặc Esc để thôi.</p>
</div>
<div class="panel" id="panel" hidden><div class="panel-in">
  <button class="close" id="close">đóng</button>
  <h2 id="pname"></h2><p class="desc" id="pdesc"></p><div id="pbody"></div>
</div></div>
<script id="atlas" type="application/json">__DATA__</script>
<script>
const atlas = JSON.parse(document.getElementById('atlas').textContent);
const byName = {};
for (const w of atlas.waves) for (const s of w.skills) byName[s.skill] = {skill: s, tone: w.tone};
const panel = document.getElementById('panel');
let lit = null;

function show(name) {
  const found = byName[name];
  if (!found) return;
  document.body.classList.add('focusing');
  for (const el of document.querySelectorAll('.card')) el.classList.toggle('lit', el.dataset.skill === name);
  document.getElementById('pname').textContent = name;
  document.getElementById('pdesc').textContent = found.skill.description;
  const body = document.getElementById('pbody');
  body.textContent = '';
  for (const shard of found.skill.shards) {
    const box = document.createElement('div');
    box.className = 'shard';
    const h = document.createElement('h3');
    h.textContent = shard.shard + ' · ' + shard.task_count;
    const row = document.createElement('div');
    row.className = 'tasks';
    for (const t of shard.tasks) {
      const chip = document.createElement('span');
      chip.className = 'task';
      chip.dataset.risk = t.risk_tier;
      chip.textContent = t.id;
      chip.title = t.output + ' — ' + t.risk_tier + ', ' + t.execution_path;
      row.append(chip);
    }
    box.append(h, row);
    body.append(box);
  }
  panel.hidden = false;
  lit = name;
}
function clear() {
  document.body.classList.remove('focusing');
  for (const el of document.querySelectorAll('.card')) el.classList.remove('lit');
  panel.hidden = true;
  lit = null;
}
for (const el of document.querySelectorAll('.card')) {
  el.addEventListener('click', () => (lit === el.dataset.skill ? clear() : show(el.dataset.skill)));
}
document.getElementById('close').addEventListener('click', clear);
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') clear(); });
</script>
"""


BEGIN = "<!-- generated by tools/build_skill_atlas.py -- do not edit by hand -->"
END = "<!-- end generated tree -->"

# The visual grammar this atlas is drawn with: one colour per wave, dim by default, one node lit at
# a time. Bands read top to bottom in rollout order, which is also roughly dependency order.
WAVE_TONE = {
    "Wave 0": "control",
    "Wave 1": "request-to-analytics",
    "Wave 2": "platform",
    "Wave 3": "ai-ml",
    "Wave 4": "specialised",
    "Unplaced": "unplaced",
}


def parse_waves() -> tuple[dict[str, str], dict[str, str]]:
    """Wave membership and each wave's authored subtitle, read from skill-map section 40."""
    text = MAP.read_text(encoding="utf-8")
    section = text.split("## 40. Thứ tự triển khai khuyến nghị", 1)
    if len(section) < 2:
        raise SystemExit("skill-map has no section 40; the wave bands come from there")
    body = section[1].split("\n## ", 1)[0]
    membership: dict[str, str] = {}
    titles: dict[str, str] = {}
    current = ""
    for line in body.splitlines():
        heading = re.match(r"^###\s+(Wave \d+)\s*—\s*(.+)$", line.strip())
        if heading:
            current = heading.group(1)
            titles[current] = heading.group(2).strip()
            continue
        item = re.match(r"^\d+\.\s+`([a-z0-9-]+)`", line.strip())
        if item and current:
            membership[item.group(1)] = current
    return membership, titles


def parse_drawn_tree() -> set[str]:
    text = MAP.read_text(encoding="utf-8")
    block = text.split("## 2. Kiến trúc phân tầng", 1)[1].split("```")[1]
    return set(re.findall(r"[├└]──\s+(\S+)", block)) | {"data-department-orchestrator"}


def collect() -> dict:
    membership, titles = parse_waves()
    catalog = json.loads((ROOT / "task-catalog.json").read_text(encoding="utf-8"))
    by_skill_task: dict[str, dict] = {t["id"]: t for t in catalog}

    index = json.loads((ROOT / "docs" / "retrieval-index.json").read_text(encoding="utf-8"))
    task_skill = {t["id"]: t["skill"] for t in index["tasks"]}

    shard_of: dict[str, str] = {}
    for path in SKILLS.glob("*/references/catalog-*.md"):
        shard = path.stem.removeprefix("catalog-")
        for task_id in re.findall(r"\(tasks/([a-z0-9-]+)\.md\)", path.read_text(encoding="utf-8")):
            shard_of[task_id] = shard

    waves: dict[str, list] = defaultdict(list)
    unplaced: list[str] = []
    for skill_md in sorted(SKILLS.glob("*/SKILL.md")):
        name = skill_md.parent.name
        text = skill_md.read_text(encoding="utf-8")
        desc = re.search(r"^description:\s*(.+)$", text, re.M)
        wave = membership.get(name)
        if wave is None:
            unplaced.append(name)
            wave = "Unplaced"

        tasks = [tid for tid, s in task_skill.items() if s == name]
        shards: dict[str, list[dict]] = defaultdict(list)
        for tid in sorted(tasks):
            entry = by_skill_task[tid]
            shards[shard_of.get(tid, "unsharded")].append({
                "id": tid,
                "output": entry.get("output", ""),
                "risk_tier": entry.get("risk_tier", ""),
                "execution_path": entry.get("execution_path", ""),
                "criticality": entry.get("criticality", ""),
            })
        risk = Counter(t["risk_tier"] for group in shards.values() for t in group)
        waves[wave].append({
            "skill": name,
            "description": (desc.group(1).strip() if desc else ""),
            "task_count": len(tasks),
            "risk_mix": dict(sorted(risk.items())),
            "highest_risk": max(risk, default=""),
            "shards": [{"shard": s, "task_count": len(v), "tasks": v}
                       for s, v in sorted(shards.items())],
        })

    order = ["Wave 0", "Wave 1", "Wave 2", "Wave 3", "Wave 4", "Unplaced"]
    drawn = parse_drawn_tree()
    on_disk = {p.parent.name for p in SKILLS.glob("*/SKILL.md")}

    return {
        "_": ("Generated. Every level comes from an authored source: waves from skill-map section 40, "
              "skills from SKILL.md on disk, shards from catalog-*.md, tasks from task-catalog.json. "
              "A skill in no wave is reported as unplaced, never filed somewhere plausible."),
        "root": "data-department-agent-skills",
        "skill_count": len(on_disk),
        "task_count": sum(s["task_count"] for w in waves.values() for s in w),
        "waves": [
            {"wave": w, "title": titles.get(w, "chưa được xếp vào wave nào trong skill-map"),
             "tone": WAVE_TONE[w], "skill_count": len(waves[w]), "skills": waves[w]}
            for w in order if waves.get(w)
        ],
        "unplaced": sorted(unplaced),
        "drawn_tree_missing": sorted(on_disk - drawn),
    }


def render_tree(atlas: dict) -> str:
    lines = [BEGIN, "", "```text", atlas["root"]]
    waves = atlas["waves"]
    for w_i, wave in enumerate(waves):
        w_last = w_i == len(waves) - 1
        lines.append(f"{'└──' if w_last else '├──'} {wave['wave']} — {wave['title']}")
        pad = "    " if w_last else "│   "
        for s_i, skill in enumerate(wave["skills"]):
            s_last = s_i == len(wave["skills"]) - 1
            lines.append(f"{pad}{'└──' if s_last else '├──'} {skill['skill']}  "
                         f"({skill['task_count']} tasks, cao nhất {skill['highest_risk']})")
    lines += ["```", "", END]
    return "\n".join(lines)


def write_tree(atlas: dict) -> bool:
    text = MAP.read_text(encoding="utf-8")
    tree = render_tree(atlas)
    if BEGIN in text and END in text:
        head, rest = text.split(BEGIN, 1)
        _, tail = rest.split(END, 1)
        updated = head + tree + tail
    else:
        # First run: replace exactly the first fenced block after the section heading and nothing
        # else. Splitting the whole section on fences ate a sentence and the opening fence of the
        # block after it, so this walks the lines instead.
        lines = text.splitlines(keepends=True)
        start = next(i for i, l in enumerate(lines) if l.startswith("## 2. Kiến trúc phân tầng"))
        open_fence = next(i for i in range(start, len(lines)) if lines[i].startswith("```"))
        close_fence = next(i for i in range(open_fence + 1, len(lines)) if lines[i].startswith("```"))
        updated = "".join(lines[:open_fence]) + tree + "\n" + "".join(lines[close_fence + 1:])
    if updated == text:
        return False
    MAP.write_text(updated, encoding="utf-8")
    return True


def render_html(atlas: dict) -> str:
    """The picture, drawn with the grammar the source videos used: bands top to bottom in rollout
    order, one card per skill, and a focus mode that dims everything except what you are reading."""
    import html as _html

    bands = []
    for wave in atlas["waves"]:
        cards = []
        for skill in wave["skills"]:
            risk = skill["highest_risk"] or "—"
            cards.append(
                f'<button class="card" data-skill="{_html.escape(skill["skill"])}">'
                f'<div class="nm"><span class="pip"></span>{_html.escape(skill["skill"])}</div>'
                f'<div class="meta">{skill["task_count"]} task · {len(skill["shards"])} nhóm · '
                f'cao nhất {risk}</div></button>'
            )
        bands.append(
            f'<section class="band" style="--tone: var(--{wave["tone"]})">'
            f'<div class="band-label"><span class="band-count">{wave["skill_count"]} skill · '
            f'{sum(s["task_count"] for s in wave["skills"])} task</span>'
            f'<b>{_html.escape(wave["wave"])}</b> — {_html.escape(wave["title"])}</div>'
            f'<div class="cards">{"".join(cards)}</div></section>'
        )

    note = ""
    if atlas["unplaced"]:
        unplaced_tasks = sum(
            s["task_count"] for w in atlas["waves"] if w["wave"] == "Unplaced" for s in w["skills"])
        note = (
            '<p class="note"><b>Băng cuối không phải một wave.</b> '
            f'{len(atlas["unplaced"])} skill — {unplaced_tasks} task, '
            f'{unplaced_tasks * 100 // max(1, atlas["task_count"])}% toàn bộ suite — không được nêu tên '
            'trong mục 40 của skill-map. Chúng được thêm sau khi mục ấy được viết, và công cụ này xếp '
            'chúng vào một băng riêng thay vì đoán một wave nghe hợp lý.</p>')

    slim = {"waves": [{"wave": w["wave"], "tone": w["tone"], "skills": [
        {"skill": s["skill"], "description": s["description"], "shards": s["shards"]}
        for s in w["skills"]]} for w in atlas["waves"]]}

    return (HTML_HEAD
            .replace("__ROOT__", atlas["root"])
            .replace("__SKILLS__", str(atlas["skill_count"]))
            .replace("__TASKS__", str(atlas["task_count"]))
            .replace("__WAVES__", str(len(atlas["waves"])))
            .replace("__BANDS__", "\n".join(bands))
            .replace("__NOTE__", note)
            .replace("__DATA__", json.dumps(slim, ensure_ascii=False).replace("</", "<\\/")))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--report", action="store_true")
    args = parser.parse_args()

    atlas = collect()
    rendered = json.dumps(atlas, ensure_ascii=False, indent=1) + "\n"

    print(f"root: {atlas['root']}  waves: {len(atlas['waves'])}  "
          f"skills: {atlas['skill_count']}  tasks: {atlas['task_count']}")
    if atlas["unplaced"]:
        print(f"unplaced — in no wave in skill-map section 40: {', '.join(atlas['unplaced'])}")

    if args.report:
        for wave in atlas["waves"]:
            print(f"\n{wave['wave']} — {wave['title']}  ({wave['skill_count']} skills)")
            for skill in wave["skills"]:
                shards = ", ".join(f"{s['shard']}:{s['task_count']}" for s in skill["shards"])
                print(f"  {skill['skill']:42} {skill['task_count']:4} tasks  {shards}")

    page = render_html(atlas)
    stale_json = not OUT.exists() or OUT.read_text(encoding="utf-8") != rendered
    stale_page = not PAGE.exists() or PAGE.read_text(encoding="utf-8") != page
    stale_tree = render_tree(atlas) not in MAP.read_text(encoding="utf-8")
    if args.check:
        if stale_json or stale_tree or stale_page:
            print("FAILED: skill atlas is out of date; run tools/build_skill_atlas.py")
            sys.exit(1)
        return
    if stale_json:
        OUT.write_text(rendered, encoding="utf-8")
        print(f"wrote {OUT.relative_to(ROOT)}")
    if stale_page:
        PAGE.write_text(page, encoding="utf-8")
        print(f"wrote {PAGE.relative_to(ROOT)}")
    if write_tree(atlas):
        print("rewrote the tree in docs/skill-map.md section 2")


if __name__ == "__main__":
    main()
