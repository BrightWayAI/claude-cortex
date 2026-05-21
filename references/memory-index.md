# Memory index (v4.5+)

How cortex maintains `<config-root>/memory/index.md` — an always-current, human-readable catalog of every memory node.

The index is **deterministic and zero-LLM**. It's a file-walk + string-extract that runs as part of `/end-day`, `/cleanup`, and on demand via `/reindex`. It never invents content; it summarizes what's already in the files.

## Why

- **Obsidian gets a home page.** The user opens `<config-root>/` in Obsidian, the index renders the whole graph as a navigable catalog. No plugin code needed in Obsidian itself.
- **Non-cortex agents can read memory cold.** Any future plugin (or one-off agent) reads `memory/index.md` first and finds its way around with one file read instead of loading `memory-librarian`.
- **At-a-glance health.** Stale/dormant counts surface at the top — the user sees the audit before asking for one.

## Output structure

```markdown
# Memory index

_Last updated: YYYY-MM-DD HH:MM. Auto-maintained by cortex; do not hand-edit._
_Total nodes: N (X client, Y person, Z company, ...)._

## User profile
- [[user]] — <first-line descriptor>. _<state>. Confirmed <date>._

## Clients
- [[client/<slug>]] — <descriptor>. _<state>._
...

## People
- [[person/<slug>]] — <descriptor>. _<state>._
...

## Companies
- [[company/<slug>]] — <descriptor>. _<state>._
...

## Topics
- [[topic/<slug>]] — <descriptor>. _<state>._
...

## Domain notes
- [[<name>]] — <descriptor>. _<state>._
...

## Bizdev (active prospects)
- [[bizdev/<slug>]] — <descriptor>. _<state>._
...

## System
- [[DASHBOARD]] — Auto-recall entry point.
- [[.decay-config]] — Decay thresholds. Hand-editable.
...

## Demoted knowledge (preserved for context)
<N> demoted entries across <M> nodes — see individual node `## Demoted knowledge` sections.

## Archived
<N> archived person pages in `memory/person/archive/` — last archived <date>.
<K> archived nodes in `memory/archive/` — last archived <date>.
```

Each line: wikilink, descriptor, decay state, last confirmation date. Demoted/archived material is summarized at the bottom — not listed inline (would balloon the file).

## Generation logic

### Inputs
- `<config-root>/memory/**/*.md` — all node files.
- `<config-root>/memory/.decay-config.md` — thresholds for state classification.

### Outputs
- `<config-root>/memory/index.md` — regenerated wholesale on each run.

### Steps

1. **Walk** `<config-root>/memory/` recursively. Skip:
   - `index.md` itself (the output)
   - `archive/` subdirectories (summarized in footer instead)
   - `staged/` entirely (drafts and queues handled separately; never indexed as nodes)
   - All dot-prefixed dirs (legacy from pre-v4.8.1; migration moves them under `staged/`)
   - `hot.md` and `log.md` (operational, not knowledge)
   - All `.md` files in the root that match a "system" allowlist (DASHBOARD, .decay-config) — these go in the "System" section
   - Files with no extension or non-`.md` extensions

2. **Classify each file by directory:**
   - `memory/user.md` → User profile
   - `memory/client/*.md` → Clients
   - `memory/person/*.md` → People (excluding `person/archive/`)
   - `memory/company/*.md` → Companies
   - `memory/topic/*.md` → Topics
   - `memory/bizdev/*.md` → Bizdev
   - `memory/<other-dir>/*.md` → group under the dir name as section heading
   - `memory/*.md` (root-level, not in system allowlist) → Domain notes

3. **Extract per-file metadata:**
   - **Descriptor:** first H1 line content stripped of `#`, then first non-empty line of body if the H1 is just the slug. Cap at 80 chars.
   - **Last confirmation:** scan body for `[confirmed:YYYY-MM-DD]` tags; take the max date. If none, use file mtime as fallback.
   - **State:** apply decay-config thresholds to determine Fresh / Stale / Dormant / Cold. If a `decay_profile: fast | normal | slow` is present in the file's front-matter or first lines, apply the multiplier.

4. **Count active vs. demoted:**
   - Active entries: any `[confirmed:...]` tag not within a `## Demoted knowledge` section.
   - Demoted: tags inside `## Demoted knowledge`.

5. **Render** the markdown index. Within each group, sort by state (Fresh first, then Stale, Dormant, Cold) and alphabetically within state.

6. **Write** `<config-root>/memory/index.md`. Always overwrites; never appends.

### Decay classification

```
days_since_confirmed = today - max(confirmed_date_in_file)
type_modifier = max type-modifier across entry types in file (default 1.0)
profile_multiplier = front-matter decay_profile (fast=0.5, normal=1.0, slow=2.0)

effective_fresh = threshold_fresh * type_modifier * profile_multiplier
effective_dormant = threshold_dormant * type_modifier * profile_multiplier
effective_cold = threshold_cold * type_modifier * profile_multiplier

if days_since_confirmed <= effective_fresh: Fresh
elif days_since_confirmed <= effective_dormant: Stale
elif days_since_confirmed <= effective_cold: Dormant
else: Cold
```

For person pages, use the parallel state model from `references/decay-model.md` (Active / Cooling / Dormant / Archived).

For files with no `[confirmed:...]` tags at all (e.g., raw scratch notes), classify by file mtime against the same thresholds.

### When to run

- **`/end-day`** Step 6 (after Phase 4 auto-commit and Phase 5 reflective prompts). Keeps index fresh daily.
- **`/cleanup`** final step (after section H and I). Reflects any demotions/archives the user just confirmed.
- **`/remember`** (silent path): write a marker file `<config-root>/memory/staged/queues/reindex` with `touched: <node-id>` line per write. Do NOT regenerate synchronously — that would chunk every `/remember` call. The next `/end-day` notices the marker and runs the indexer.
- **`/reindex`** (explicit command): always regenerates immediately. Fast (no model calls).

### Out of scope

- The indexer does not compute "what's most important." It catalogs everything. Ranking and surfacing are the librarian's job, not the indexer's.
- The indexer does not edit node files. Read-only across the tree.
- The indexer does not handle multi-vault scenarios. One `<config-root>` per run.
