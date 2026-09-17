#!/usr/bin/env python3
"""Measure a curriculum roadmap against the things "rigorous" actually means.

"Make it scientific and international-standard" is an adjective, and an adjective cannot be
checked, so a run told to apply one tends to change the wording and report success. The properties
underneath it can be counted, and this counts them:

- **Every module states how you know you are done with it.** An exit criterion is the difference
  between a syllabus and a list of topics. Measured on three real roadmaps holding 74 modules, the
  count was zero, which is the single largest gap between what those documents are and what they
  claim to be.
- **Every lesson objective uses a verb you can observe someone doing.** "Understand X" cannot be
  assessed, so it cannot be failed, so it promises nothing. Bloom's revised taxonomy supplies the
  verbs; the point is not the taxonomy but that the verb names an action a person performs.
- **A claim about industry practice carries a date and a source.** What teams use changes, and a
  curriculum asserting it from memory ages silently into being wrong.
- **A metaphor may illustrate but must not define.** "A warehouse is the heart of the stack"
  leaves the reader with a feeling instead of a definition.

It reports and does not rewrite. What counts as an acceptable exit criterion for a given module is
a judgement by whoever teaches it, and a script that filled them in would be manufacturing the
evidence it exists to look for.

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Bloom's revised taxonomy, lowest to highest. Vietnamese first because these roadmaps are
# Vietnamese; the English is here because the source material and job postings are not.
OBSERVABLE = {
    "remember": ["liệt kê", "gọi tên", "kể tên", "nêu tên", "nhận ra", "nhắc lại", "định nghĩa",
                 "đọc được", "list", "name", "identify", "recall", "define"],
    "understand": ["giải thích", "mô tả", "phân biệt", "diễn giải", "tóm tắt", "phân loại",
                   "phát biểu", "chỉ ra", "đọc hiểu", "nói được", "trình bày",
                   "explain", "describe", "distinguish", "summarise", "summarize", "classify"],
    "apply": ["viết được", "chạy được", "dựng được", "áp dụng", "thực hiện", "cấu hình", "truy vấn",
               "vẽ", "vẽ lại", "xây", "làm được", "tạo", "chuyển", "biến", "sửa", "tối ưu",
               "apply", "implement", "execute", "configure", "write", "query", "build", "draw"],
    "analyse": ["phân tích", "so sánh", "truy nguyên", "chẩn đoán", "tách", "đối chiếu",
                "tìm ra", "định vị", "kiểm chứng", "rà",
                "analyse", "analyze", "compare", "diagnose", "trace", "differentiate"],
    "evaluate": ["đánh giá", "thẩm định", "phản biện", "chọn giữa", "biện minh", "rà soát",
                 "evaluate", "assess", "critique", "justify", "review", "judge"],
    "create": ["thiết kế", "dựng mới", "đề xuất", "xây dựng", "soạn", "tổng hợp",
               "design", "construct", "compose", "propose", "synthesise", "synthesize"],
}
ALL_VERBS = sorted({v for group in OBSERVABLE.values() for v in group}, key=len, reverse=True)

# Verbs that read like objectives and cannot be observed. These are the ones worth naming, because
# they are what a writer reaches for when the objective has not actually been decided yet.
UNOBSERVABLE = ["hiểu", "biết", "nắm được", "nắm vững", "làm quen", "ý thức được", "thấy được",
                "cảm nhận", "understand", "know", "be aware", "be familiar", "appreciate",
                "learn about", "get to know"]

EXIT_MARKERS = ["exit criterion", "exit criteria", "tiêu chí ra", "tiêu chí hoàn thành",
                "đầu ra module", "học xong module", "hoàn thành module khi", "chuẩn ra"]

# A metaphor defining rather than illustrating. Matched with a copula so ordinary comparisons
# ("chạy nhanh như") do not trip it.
METAPHOR_DEFINES = re.compile(
    r"(?i)\b(là|chính là)\s+(chìa khoá|chìa khóa|trái tim|xương sống|kim chỉ nam|linh hồn|"
    r"nền móng vững chắc|bí kíp|tuyệt chiêu|ma thuật|phép màu)\b")

HYPE = re.compile(
    r"(?i)\b(đột phá|thần thánh|đỉnh cao|siêu việt|vô địch|hoàn hảo tuyệt đối|tốt nhất thế giới|"
    r"revolutionary|game.?changing|world.?class|cutting.?edge|state.?of.?the.?art)\b")

# A claim about what the industry does, which needs a date and a source behind it.
INDUSTRY_CLAIM = re.compile(
    r"(?i)(hầu hết (?:các )?(?:công ty|doanh nghiệp|team|đội)|đa số (?:công ty|doanh nghiệp)|"
    r"thị trường (?:hiện )?(?:đang|nay)|ngành (?:hiện )?(?:đang|nay)|xu hướng hiện nay|"
    r"most companies|the industry (?:uses|has moved)|current trend)")

SOURCED = re.compile(r"(https?://|\[\d+\]|\b20[12][0-9]\b|theo\s+[A-Z])")


def lessons(text: str) -> list[dict]:
    """Every lesson block and the labelled fields inside it.

    The format these roadmaps use is a `### Lesson N · title` heading followed by bolded labels:
    Prerequisites, Learn, Outcome, Lab, Pitfalls, Done when. An earlier version of this script
    assumed `##` was a module and `###` a lesson, counted context sections like "Mức lương tham
    chiếu" as modules, and reported zero objectives across three documents that carry one per
    lesson. The lesson format is what to read, so read it.
    """
    blocks: list[dict] = []
    current: dict | None = None
    for line in text.splitlines():
        stripped = line.strip()
        heading = re.match(r"^###\s+(Lesson\s+\d+.*)$", stripped)
        if heading:
            current = {"title": heading.group(1).strip(), "fields": {}}
            blocks.append(current)
            continue
        if current is None:
            continue
        if stripped.startswith("## "):
            current = None
            continue
        field = re.match(r"^\*\*([^.*]{1,28})\.?\*\*\s*(.*)$", stripped)
        if field:
            current["fields"][field.group(1).strip().lower()] = field.group(2).strip()
    return blocks


def field_of(lesson: dict, *names: str) -> str:
    for name in names:
        for key, value in lesson["fields"].items():
            if key.startswith(name):
                return value
    return ""


def classify(objective: str) -> str:
    low = objective.lower()
    for verb in ALL_VERBS:
        if low.startswith(verb) or re.search(rf"\b{re.escape(verb)}\b", low[:60]):
            for level, verbs in OBSERVABLE.items():
                if verb in verbs:
                    return level
    for verb in UNOBSERVABLE:
        if re.search(rf"\b{re.escape(verb)}\b", low[:60]):
            return "unobservable"
    return "unclassified"


def check(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    blocks = lessons(text)

    no_objective, no_exit, no_prereq = [], [], []
    unobservable, unrecognised = [], []
    by_level: dict[str, int] = {}
    for lesson in blocks:
        objective = field_of(lesson, "outcome", "mục tiêu", "objective")
        if not objective:
            no_objective.append(lesson["title"][:70])
        else:
            level = classify(objective)
            by_level[level] = by_level.get(level, 0) + 1
            # `unclassified` means this script did not recognise the verb, which is a gap in its
            # dictionary and not a fault in the curriculum. An early run reported 35% observable
            # on objectives that read "Kể tên sáu vai trò" and "Vẽ lại vòng đời bảy chặng" —
            # both perfectly observable, neither in the list at the time. Counting a dictionary
            # miss as a curriculum defect sends someone to rewrite work that was already right.
            if level == "unobservable":
                unobservable.append(f"{lesson['title'][:40]} → {objective[:70]}")
            elif level == "unclassified":
                unrecognised.append(f"{lesson['title'][:40]} → {objective[:70]}")
        if not field_of(lesson, "done when", "exit", "tiêu chí ra", "hoàn thành khi"):
            no_exit.append(lesson["title"][:70])
        if not field_of(lesson, "prerequisite", "điều kiện"):
            no_prereq.append(lesson["title"][:70])

    metaphors = [m.group(0) for m in METAPHOR_DEFINES.finditer(text)]
    hype = [m.group(0) for m in HYPE.finditer(text)]
    unsourced = [line.strip()[:90] for line in text.splitlines()
                 if INDUSTRY_CLAIM.search(line) and not SOURCED.search(line)]

    observable = sum(n for lvl, n in by_level.items() if lvl in OBSERVABLE)
    return {
        "file": str(path),
        "lessons": len(blocks),
        "lessons_without_objective": no_objective,
        "lessons_without_exit_criterion": no_exit,
        "lessons_without_prerequisite": no_prereq,
        "objectives_observable": observable,
        "objectives_by_level": by_level,
        "objectives_not_observable": unobservable,
        "objectives_verb_unrecognised": unrecognised,
        "metaphor_as_definition": metaphors,
        "hype_without_evidence": hype,
        "industry_claims_without_source": unsourced,
    }


def report(result: dict, verbose: bool) -> int:
    print(f"\n{result['file']}")
    print(f"  {result['lessons']} bài · {result['objectives_observable']} objective quan sát được")
    faults = 0

    def missing(label: str, items: list[str], denom: int) -> None:
        nonlocal faults
        if items:
            faults += 1
            print(f"  ✗ {len(items)}/{denom} bài {label}")
            for item in (items if verbose else items[:5]):
                print(f"      {item}")
            if not verbose and len(items) > 5:
                print(f"      … còn {len(items) - 5}")
        else:
            print(f"  ✓ mọi bài đều có {label.replace('không có ', '')}")

    total = result["lessons"] or 1
    missing("không có objective", result["lessons_without_objective"], total)
    missing("không có exit criterion", result["lessons_without_exit_criterion"], total)
    missing("không nêu prerequisite", result["lessons_without_prerequisite"], total)

    bad = result["objectives_not_observable"]
    unknown = result["objectives_verb_unrecognised"]
    stated = result["objectives_observable"] + len(bad) + len(unknown)
    if stated:
        if bad:
            faults += 1
            print(f"  ✗ {len(bad)}/{stated} objective dùng động từ KHÔNG quan sát được")
            for item in (bad if verbose else bad[:5]):
                print(f"      {item}")
        else:
            print(f"  ✓ không objective nào dùng động từ không quan sát được")
        print(f"  · {result['objectives_observable']}/{stated} nhận diện được động từ "
              f"· phân bố {result['objectives_by_level']}")
        if unknown:
            print(f"  ? {len(unknown)} objective script không nhận ra động từ — người đọc tự "
                  f"xét, đây là thiếu sót của từ điển chứ không phải lỗi giáo trình")
            for item in (unknown if verbose else unknown[:3]):
                print(f"      {item}")

    for label, items in (("ẩn dụ dùng làm định nghĩa", result["metaphor_as_definition"]),
                         ("từ khoa trương không kèm bằng chứng", result["hype_without_evidence"]),
                         ("khẳng định về ngành không dẫn nguồn",
                          result["industry_claims_without_source"])):
        if items:
            faults += 1
            print(f"  ✗ {len(items)} {label}")
            for item in (items if verbose else items[:3]):
                print(f"      {item}")
        else:
            print(f"  ✓ không có {label}")
    return faults


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", type=Path)
    ap.add_argument("--json", type=Path, help="ghi báo cáo ra JSON")
    ap.add_argument("--verbose", action="store_true", help="in đủ, không cắt bớt")
    ap.add_argument("--strict", action="store_true", help="thoát 1 khi còn bất kỳ lỗi nào")
    args = ap.parse_args()

    results, faults = [], 0
    for path in args.paths:
        if not path.is_file():
            print(f"không đọc được: {path}", file=sys.stderr)
            return 2
        result = check(path)
        results.append(result)
        faults += report(result, args.verbose)

    if args.json:
        args.json.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n",
                             encoding="utf-8")
        print(f"\nđã ghi {args.json}")

    print(f"\n{faults} nhóm lỗi trên {len(results)} tệp")
    print("Đây là phép đo, không phải điểm chất lượng. Một roadmap qua hết các mục này vẫn có thể "
          "dạy sai thứ tự; cái nó bảo đảm là mỗi module nói được lúc nào thì xong, và mỗi objective "
          "nêu một việc quan sát được.")
    return 1 if (args.strict and faults) else 0


if __name__ == "__main__":
    raise SystemExit(main())
