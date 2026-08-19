---
name: dd-scan
description: Measure structural drift in a codebase — cycles, dependency depth, coupling, size inequality and duplicated blocks — as first-pass architecture evidence.
argument-hint: "[path] [--gate <score>]"
disable-model-invocation: true
---

Scan for structural drift: $ARGUMENTS

Code generated at machine speed decays structurally before it decays functionally. Tests stay
green while cycles appear, chains deepen, one module absorbs everything and near-identical
blocks multiply.

1. Run the sensor over the target path (default: the working directory):

```
python skills/data-architecture/scripts/scan_architecture_drift.py <path> --max-depth 5 --report-out architecture-report.json
```

2. Report the score out of 10000 and each of the five components (modularity, acyclicity,
   depth, equality, redundancy) with the observation that drives it.
3. **State the method's limits before drawing conclusions.** This is regex-based import
   extraction, not a parse. It misses dynamic imports, aliases, re-exports and conditional
   imports, and it does not understand semantics. A high score is not proof the architecture
   is sound; a flagged cycle is a place to look, not a confirmed defect.
4. Confirm anything you intend to act on against a real parser. Where available, prefer a
   tree-sitter-based tool such as Sentrux (`sentrux check`, `sentrux gate`, or its MCP server,
   MIT-licensed, 52 languages) and record that output as the evidence instead of this scan.
5. Track direction, not absolutes. Re-run with `--baseline architecture-report.json` so a
   regression against the recorded score fails loudly.

For each finding, name the smallest refactor that would resolve it and which atomic task owns
that work. Do not propose a sweeping rewrite off the back of a first-pass signal.

Return: the score, the components, the specific cycles and duplication hotspots with file and
line, the method's limits, and the single highest-value refactor to do first.
