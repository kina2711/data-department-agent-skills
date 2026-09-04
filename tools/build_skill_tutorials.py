#!/usr/bin/env python3
"""Write a step-by-step walkthrough for each skill, from the tasks that skill actually owns.

A tutorial somebody invents goes stale the first time a task is renamed, and nobody notices because
prose does not fail a build. Every line here is assembled from data that already exists and is
already checked: the entry points a person chose in the Vietnamese guide, the goal and output each
task declares in the catalog, the verb shards that give a skill its natural order, and the risk tier
that says where a run stops for a human.

The shape is four beats, and it is the same four for every skill because the lifecycle is:

  bắt đầu    the entry point somebody nominated, and what it hands you
  làm tiếp   the next shard in plan-design → build-deliver → test-assure → operate-improve order
  cổng chặn  the R3/R4 tasks in this skill, or an honest statement that it has none
  xong khi   what the test-assure shard checks, because "done" is a claim somebody verifies

Where a skill has no task in a shard, that beat says so rather than borrowing one from elsewhere. A
walkthrough that quietly fills a gap teaches a sequence the suite does not have.

It arranges what exists. It cannot tell whether the order is a good way to learn the work.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "huong-dan-tung-buoc.vi.json"

# plan → build → test → operate. A shard name may carry a suffix when a skill split one, so the
# match is on the prefix.
SHARD_ORDER = ["plan-design", "build-deliver", "test-assure", "operate-improve"]
SHARD_LABEL = {
    "plan-design": "lập kế hoạch và thiết kế",
    "build-deliver": "dựng và bàn giao",
    "test-assure": "kiểm chứng",
    "operate-improve": "vận hành và cải tiến",
}
GATE_TIERS = {"R3-controlled", "R4-critical"}


def shard_key(shard: str) -> str:
    for prefix in SHARD_ORDER:
        if shard.startswith(prefix):
            return prefix
    return shard


def collect() -> dict:
    catalog = {t["id"]: t for t in json.loads((ROOT / "task-catalog.json").read_text(encoding="utf-8"))}
    index = json.loads((ROOT / "docs" / "retrieval-index.json").read_text(encoding="utf-8"))
    guides = json.loads((ROOT / "docs" / "huong-dan-skill.vi.json").read_text(encoding="utf-8"))["skills"]

    by_skill: dict[str, list[str]] = {}
    for task in index["tasks"]:
        by_skill.setdefault(task["skill"], []).append(task["id"])

    shard_of: dict[str, str] = {}
    for path in (ROOT / "skills").glob("*/references/catalog-*.md"):
        shard = path.stem.removeprefix("catalog-")
        for task_id in re.findall(r"\(tasks/([a-z0-9-]+)\.md\)", path.read_text(encoding="utf-8")):
            shard_of[task_id] = shard

    out: dict[str, dict] = {}
    for skill, task_ids in sorted(by_skill.items()):
        guide = guides.get(skill, {})
        entries = [t for t in guide.get("bat_dau_tu", []) if t in catalog]

        grouped: dict[str, list[str]] = {k: [] for k in SHARD_ORDER}
        for task_id in sorted(task_ids):
            key = shard_key(shard_of.get(task_id, ""))
            if key in grouped:
                grouped[key].append(task_id)

        def describe(task_id: str) -> dict:
            task = catalog[task_id]
            return {
                "task": task_id,
                "muc_tieu": task.get("goal", ""),
                "ket_qua": task.get("output", ""),
                "rui_ro": task.get("risk_tier", ""),
            }

        steps = []
        if entries:
            steps.append({
                "buoc": "Bắt đầu",
                "vi_sao": "Đây là điểm vào mà hướng dẫn của skill này chỉ định, không phải task đầu tiên theo thứ tự chữ cái.",
                "tasks": [describe(t) for t in entries],
            })

        # The first shard that is not the entry point's own, so the walkthrough moves forward.
        entry_shards = {shard_key(shard_of.get(t, "")) for t in entries}
        for key in SHARD_ORDER:
            if key in entry_shards or not grouped[key]:
                continue
            steps.append({
                "buoc": f"Làm tiếp — {SHARD_LABEL[key]}",
                "vi_sao": f"Skill này có {len(grouped[key])} task ở nhóm {key}; đây là ba task đầu theo thứ tự trong catalog.",
                "tasks": [describe(t) for t in grouped[key][:3]],
            })
            break

        gates = [t for t in task_ids if catalog[t].get("risk_tier") in GATE_TIERS]
        steps.append({
            "buoc": "Cổng chặn",
            "vi_sao": ("Các task này ở mức R3 hoặc R4: chúng dừng lại chờ người duyệt, và app không tự vượt được."
                       if gates else
                       "Skill này không có task nào ở mức R3 hoặc R4. Không có nghĩa là không cần rà soát — chỉ là không có cổng phê duyệt bắt buộc."),
            "tasks": [describe(t) for t in gates[:4]],
        })

        checks = grouped["test-assure"]
        steps.append({
            "buoc": "Xong khi",
            "vi_sao": ("Xong là thứ có người kiểm được, không phải thứ trông có vẻ đủ. Đây là các task kiểm chứng của skill này."
                       if checks else
                       "Skill này không có task nào ở nhóm test-assure. Tiêu chí hoàn thành phải lấy từ contract của từng task, không có bước kiểm chung."),
            "tasks": [describe(t) for t in checks[:3]],
        })

        out[skill] = {
            "tom_tat": guide.get("tom_tat", ""),
            "so_task": len(task_ids),
            "cac_buoc": steps,
        }
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    tutorials = collect()
    doc = {
        "_": ("Sinh tự động bởi tools/build_skill_tutorials.py. Mỗi bước trỏ tới một task có thật, "
              "kèm mục tiêu và kết quả mà chính catalog khai báo. Đừng sửa tay: chạy lại generator."),
        "suite_version": json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"],
        "skills": tutorials,
    }
    rendered = json.dumps(doc, ensure_ascii=False, indent=1) + "\n"

    gateless = [s for s, t in tutorials.items()
                if not any(b["buoc"] == "Cổng chặn" and b["tasks"] for b in t["cac_buoc"])]
    checkless = [s for s, t in tutorials.items()
                 if not any(b["buoc"] == "Xong khi" and b["tasks"] for b in t["cac_buoc"])]
    print(f"skills: {len(tutorials)}  "
          f"steps each: {min(len(t['cac_buoc']) for t in tutorials.values())}–"
          f"{max(len(t['cac_buoc']) for t in tutorials.values())}")
    if gateless:
        print(f"no R3/R4 gate: {', '.join(sorted(gateless))}")
    if checkless:
        print(f"no test-assure task: {', '.join(sorted(checkless))}")

    if OUT.exists() and OUT.read_text(encoding="utf-8") == rendered:
        return
    if args.check:
        print("FAILED: step-by-step guide is out of date; run tools/build_skill_tutorials.py")
        sys.exit(1)
    OUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
