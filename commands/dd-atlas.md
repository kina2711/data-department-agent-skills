---
name: dd-atlas
description: Draw the whole suite as one tree from the repository root down to a single task, and report what the map shows that the taxonomy does not.
argument-hint: "[skill name to focus, or a wave]"
disable-model-invocation: true
---

Map the suite. Optional focus: $ARGUMENTS

You are drawing a map, not designing one. Every level of the tree comes from a file somebody wrote, and where a source says nothing, the map says nothing.

1. Regenerate, so nothing you report is read off a stale picture:

```
python3 tools/build_skill_atlas.py --report
```

This writes `docs/skill-atlas.json`, rewrites the tree in `docs/skill-map.md` section 2 between its generated markers, and renders `docs/skill-atlas.html`.

2. Read the four levels back to the reader in the order they nest, and say where each came from:
   - **root** the repository
   - **wave** rollout bands authored in skill-map section 40
   - **skill** the `SKILL.md` files on disk
   - **shard** the `catalog-*.md` verb shards inside each skill
   - **task** `task-catalog.json`

3. Report the gaps as findings, never as tidy-ups:
   - **Unplaced skills** — named in no wave. Do not file them somewhere plausible. Say how many tasks sit outside every wave and what share of the suite that is.
   - **Waves carrying disproportionate weight** — a band with few skills and many tasks, or the reverse.
   - **Shard imbalance inside a skill** — one shard holding most of the tasks means the verb grouping stopped discriminating.
   - **Risk concentration** — which bands hold the R3 and R4 tasks.

4. If `$ARGUMENTS` names a skill, walk that subtree only: its shards, its task counts, its highest risk tier, and which other skills its workflow depends on.

Return: the tree, the counts per band, the unplaced list with its task share, and any finding from step 3. Never edit `skill-map.md` section 40 to make a skill fit a wave — which wave a skill belongs to is a decision for a person, and an unplaced skill on the map is the correct way to ask for that decision.
