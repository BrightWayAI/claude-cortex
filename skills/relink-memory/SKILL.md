---
name: relink-memory
description: >
  Retroactive wikilink pass over `<config-root>/memory/`. Scans every node
  file for plain-text mentions of known entities (people / clients / topics /
  workstreams / companies / domains), proposes converting them to
  `[[wikilinks]]`, and graduates heavily-mentioned persons into person pages.

  One-time migration per cortex v4.10+. Idempotent; gated by
  `memory/.migration-wikilink-relink-done` marker. Run once after upgrading;
  future memory writes use wikilinks natively per the canonical rule in
  cortex CLAUDE.md.

  Auto-fires when the user says: "relink my memory", "fix my wikilinks",
  "my graph is disconnected", "why isn't my obsidian graph showing edges",
  "back-fill the wikilinks", "graduate the people in my memory".

  Use `--rerun` to force re-scan after marker exists.

  Cost: 1-3 min for ~30 nodes. Token cost ~$0.10-0.50 per run.
---

# relink-memory

See `commands/relink-memory.md` for the full workflow.

## When to fire

- Explicit: `/relink-memory` or `/relink-memory --rerun`.
- Trigger phrases above.
- Cortex auto-recall at conversation start MAY surface a one-line ping if it detects:
  - `memory/.migration-wikilink-relink-done` doesn't exist
  - AND there are ≥ 10 node files
  - AND wikilink density is < 2× node count
  - → suggest: "Heads up: your memory predates the v4.10 wikilink convention. Run `/relink-memory` once to back-fill plain-text entity mentions and graduate person pages."

## Pre-flight

- `<config-root>/memory/` must exist with at least one node file.
- Cortex v4.10+ installed (this skill assumes v4.10's wikilink discipline).

## What this skill is NOT for

- Editing entity content (entity files themselves aren't modified).
- Modifying staged / archive / briefs / log directories.
- Bulk text replacement of arbitrary strings — only known-entity plain-text mentions get converted.
- Creating client / company / topic / workstream nodes — only person pages (via graduation backfill).
