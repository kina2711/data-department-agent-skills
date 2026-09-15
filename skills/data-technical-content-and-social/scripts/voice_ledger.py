#!/usr/bin/env python3
"""What was approved, what was turned down, and the reason it was turned down.

A voice guide states what good writing looks like here. It is written in the abstract, so it
describes the target and not the misses, and an agent reading it still has to guess which of a
hundred defensible sentences the person would actually have rejected.

A rejection carries that information exactly. "Too salesy" attached to the sentence that was too
salesy says more than a paragraph of guidance, because the sentence is the evidence and the reason
is the rule. Keeping both, side by side, is what makes the next draft closer instead of merely
different. It is also the half nobody keeps: approved work survives in the published artifact,
while the rejected draft is usually closed and lost with the feedback still in it.

What this refuses to do is infer. It never scores a draft, never decides a rejection reason for
somebody, and never promotes a recurring reason into a rule on its own — it reports that a reason
has recurred and leaves the writing of the rule to a person. A ledger that concluded things would
be a second voice guide nobody agreed to.

Standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

VERDICTS = ("approved", "rejected", "revised")
MAX_EXCERPT = 600


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load(path: Path) -> dict:
    if not path.exists():
        return {"version": 1, "entries": []}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        raise SystemExit(f"{path} is not readable JSON: {err}")
    doc.setdefault("entries", [])
    return doc


def save(path: Path, doc: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def excerpt(text: str) -> str:
    """The passage itself, trimmed but never paraphrased.

    Trimmed because a ledger of whole drafts is a copy of the drafts; verbatim because the whole
    value is that a person can read the sentence that was wrong.
    """
    flat = " ".join(str(text).split())
    if len(flat) <= MAX_EXCERPT:
        return flat
    return flat[: MAX_EXCERPT - 1].rsplit(" ", 1)[0] + "…"


def add(args: argparse.Namespace) -> int:
    if args.verdict not in VERDICTS:
        print(f"ERROR: verdict must be one of {', '.join(VERDICTS)}", file=sys.stderr)
        return 2
    body = args.text
    if args.file:
        body = Path(args.file).read_text(encoding="utf-8")
    if not str(body or "").strip():
        print("ERROR: nothing to record; pass --text or --file", file=sys.stderr)
        return 2
    # A rejection with no reason is the one shape this refuses. It is also the easy one to write,
    # which is why it has to be refused here rather than discouraged in a comment.
    if args.verdict == "rejected" and not str(args.reason or "").strip():
        print("ERROR: a rejection needs --reason; without it the entry records that something was "
              "wrong and not what", file=sys.stderr)
        return 2

    doc = load(args.ledger)
    entry = {
        "id": hashlib.sha256(f"{now()}{body}".encode("utf-8")).hexdigest()[:12],
        "at": now(),
        "verdict": args.verdict,
        "channel": args.channel or "",
        "reason": str(args.reason or "").strip(),
        "reason_tags": sorted({t.strip().lower() for t in (args.tag or []) if t.strip()}),
        "excerpt": excerpt(body),
        "excerpt_chars": len(" ".join(str(body).split())),
        "source": str(args.file or ""),
        "by": args.by or "",
    }
    doc["entries"].append(entry)
    save(args.ledger, doc)
    print(f"{entry['verdict']}  {entry['id']}  {entry['channel'] or '—'}")
    if entry["reason"]:
        print(f"  lý do: {entry['reason']}")
    return 0


def show(args: argparse.Namespace) -> int:
    doc = load(args.ledger)
    rows = doc["entries"]
    if args.verdict:
        rows = [e for e in rows if e["verdict"] == args.verdict]
    if args.channel:
        rows = [e for e in rows if e["channel"] == args.channel]
    if args.tag:
        wanted = {t.lower() for t in args.tag}
        rows = [e for e in rows if wanted & set(e.get("reason_tags") or [])]
    rows = rows[-args.limit:] if args.limit else rows
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0
    if not rows:
        print("Chưa có mục nào khớp.")
        return 0
    for e in rows:
        print(f"\n{e['verdict']:9} {e['id']}  {e['at']}  {e['channel'] or '—'}")
        if e["reason"]:
            print(f"  lý do : {e['reason']}")
        if e["reason_tags"]:
            print(f"  nhãn  : {', '.join(e['reason_tags'])}")
        print(f"  trích : {e['excerpt']}")
    return 0


def brief(args: argparse.Namespace) -> int:
    """The part a draft actually reads: what got through, and what got sent back and why.

    Written as Markdown so it can be pasted into a prompt or committed beside the voice guide.
    Rejections come first, because a writer who reads the approved work first tends to imitate it
    and a writer who reads the rejections first tends to avoid the traps.
    """
    doc = load(args.ledger)
    rows = [e for e in doc["entries"] if not args.channel or e["channel"] == args.channel]
    rejected = [e for e in rows if e["verdict"] == "rejected"][-args.limit:]
    approved = [e for e in rows if e["verdict"] == "approved"][-args.limit:]

    counts: dict[str, int] = {}
    for e in rows:
        if e["verdict"] != "rejected":
            continue
        for tag in e.get("reason_tags") or []:
            counts[tag] = counts.get(tag, 0) + 1

    out: list[str] = [f"# Voice ledger{f' · {args.channel}' if args.channel else ''}", ""]
    out += [f"{len(rows)} mục · {len(rejected)} bị từ chối gần đây · {len(approved)} được duyệt gần đây", ""]

    if counts:
        out += ["## Lý do từ chối lặp lại", ""]
        for tag, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
            out.append(f"- `{tag}` — {n} lần")
        # Counting is a measurement; turning a count into a rule is a judgement, and it is not
        # this script's to make.
        out += ["", "Con số là số lần, không phải một quy tắc. Muốn thành quy tắc thì một người "
                    "viết nó vào voice guide.", ""]

    if rejected:
        out += ["## Bị từ chối — tránh những chỗ này", ""]
        for e in rejected:
            out += [f"**{e['reason'] or 'không ghi lý do'}**"
                    + (f" · `{'`, `'.join(e['reason_tags'])}`" if e["reason_tags"] else ""), "",
                    f"> {e['excerpt']}", ""]
    if approved:
        out += ["## Đã duyệt — giọng đúng là như thế này", ""]
        for e in approved:
            out += [f"> {e['excerpt']}", ""]
    if not rejected and not approved:
        out += ["Ledger rỗng. Một ledger rỗng không nói giọng văn nào đúng; nó nói chưa ai ghi.", ""]

    text = "\n".join(out).rstrip() + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"wrote {args.output}  ({len(rejected)} rejected, {len(approved)} approved)")
    else:
        sys.stdout.write(text)
    return 0


def check(args: argparse.Namespace) -> int:
    """Faults that make a ledger look useful while teaching nothing."""
    doc = load(args.ledger)
    problems: list[str] = []
    for e in doc["entries"]:
        if e["verdict"] == "rejected" and not str(e.get("reason") or "").strip():
            problems.append(f"{e['id']}: rejected with no reason recorded")
        if e["verdict"] not in VERDICTS:
            problems.append(f"{e['id']}: unknown verdict {e['verdict']!r}")
        if not str(e.get("excerpt") or "").strip():
            problems.append(f"{e['id']}: no excerpt, so the reason has nothing to attach to")
        if re.search(r"(?i)\b(api[_-]?key|secret|password|token)\s*[:=]", e.get("excerpt", "")):
            problems.append(f"{e['id']}: excerpt looks like it carries a credential")
    rejected = sum(1 for e in doc["entries"] if e["verdict"] == "rejected")
    print(f"entries: {len(doc['entries'])}  rejected: {rejected}  problems: {len(problems)}")
    if rejected == 0 and doc["entries"]:
        # Not an error. But a ledger of nothing but approvals cannot do the job it exists for.
        print("NOTE: mọi mục đều là approved. Ledger này chưa dạy được điều cần tránh — "
              "phần có giá trị nhất là bản bị từ chối kèm lý do.")
    for p in problems:
        print(f"ERROR: {p}", file=sys.stderr)
    return 1 if problems else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ledger", type=Path, default=Path("voice-ledger.json"))
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="record one approval, rejection or revision")
    a.add_argument("verdict", choices=VERDICTS)
    a.add_argument("--text", help="the passage itself")
    a.add_argument("--file", help="read the passage from a file")
    a.add_argument("--reason", help="why; required for a rejection")
    a.add_argument("--tag", action="append", help="short reason tag, repeatable")
    a.add_argument("--channel", help="facebook, linkedin, threads, article …")
    a.add_argument("--by", help="who decided")
    a.set_defaults(func=add)

    s = sub.add_parser("show", help="list entries")
    s.add_argument("--verdict", choices=VERDICTS)
    s.add_argument("--channel")
    s.add_argument("--tag", action="append")
    s.add_argument("--limit", type=int, default=0)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=show)

    b = sub.add_parser("brief", help="the Markdown a draft should read before writing")
    b.add_argument("--channel")
    b.add_argument("--limit", type=int, default=6)
    b.add_argument("--output")
    b.set_defaults(func=brief)

    c = sub.add_parser("check", help="find entries that teach nothing")
    c.set_defaults(func=check)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
