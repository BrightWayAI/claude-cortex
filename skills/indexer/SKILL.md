---
name: indexer
description: >
  Regenerate `<config-root>/memory/index.md` — a deterministic, zero-LLM
  catalog of every memory node grouped by type with decay-state flags.

  Auto-fires in THREE scenarios:

  1. CHAIN STEP: invoked as Step 6 of `/end-day` and as the final step of
     `/cleanup`. Runs after user-gated changes are committed so the index
     reflects current state.

  2. DEFERRED: when `/remember` writes a new entry, it appends a line to
     `<config-root>/memory/staged/queues/reindex`. The next `/end-day` or `/cleanup`
     notices the queue and runs the indexer.

  3. EXPLICIT: user runs `/reindex`, or says "regenerate the memory index",
     "rebuild the catalog", "refresh memory/index.md".

  This skill has zero LLM cost in steady state. It is a file-walk +
  string-extract + write. No reasoning, no synthesis — see
  references/memory-index.md for the deterministic spec.
---

# Indexer

See `commands/reindex.md` for the explicit command path and `references/memory-index.md` for the full spec.

## When to fire

- Auto: from `/end-day` Step 6 and `/cleanup` final step.
- Deferred: when `<config-root>/memory/staged/queues/reindex` exists.
- Explicit: user invokes `/reindex` or speaks any trigger phrase above.

## What to do

1. Resolve `<config-root>` via the standard pattern (`~/Documents/.claude-plugin-config-root`).
2. Read `<config-root>/memory/.decay-config.md` for thresholds (use defaults if missing).
3. Walk `<config-root>/memory/` per `references/memory-index.md` rules.
4. For each node file, extract descriptor and latest `[confirmed:...]` date.
5. Classify state per the decay model.
6. Render the grouped catalog with state flags.
7. Write `<config-root>/memory/index.md` (overwrite).
8. If a `staged/queues/reindex` marker exists, delete it.
9. Report briefly: "Indexed N nodes (X fresh, Y stale, Z dormant, W cold). Demoted: D entries across M nodes. Archived: A person pages, K nodes." Do not list every node.

## What this skill does NOT do

- Does not rank, judge, or summarize knowledge content. Pure cataloging.
- Does not edit node files. Read-only across `memory/`.
- Does not call any LLM. Pure deterministic generation.
- Does not handle archive directories' contents (summarizes them by count).
- Does not auto-fix decay-config errors. If `.decay-config.md` is malformed, use defaults and warn the user once.
