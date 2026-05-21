# Hot cache: `<config-root>/memory/hot.md` (v4.7+)

A rolling 7-day buffer of recent substrate, auto-maintained by `/listen`, `/morning`, and `/end-day`. Read first by `/recall` auto-fire at conversation start so every session opens warm.

Inspired by Karpathy's LLM-wiki `hot.md` pattern: keep the most-load-bearing recent context in one always-loaded file so the AI doesn't cold-start every time.

## What it contains

A single markdown file, regenerated wholesale on each maintenance run. Sections:

```markdown
# Hot cache

_Last refreshed: YYYY-MM-DD HH:MM by <trigger: listen | morning | end-day | manual>._
_Rolling window: last 7 days (configurable)._

## What I worked on (last 7 days)
- YYYY-MM-DD — <one-line summary from that day's /end-day reflection or /listen digest>
- ...

## Active people (touched in last 7 days)
- [[person/<slug>]] — last touched YYYY-MM-DD via <meeting | inbox | slack | reflection>: <one-line context>
- ...

## Active threads (open, modified in last 7 days)
- [[client/<slug>]] · "<thread name>" — opened YYYY-MM-DD, last touched YYYY-MM-DD
- ...

## Recent commitments
### To others (made by me in last 7 days)
- [[client/<slug>]] — "<commitment>" by <due-date> (<status: open | resolved>)

### From others (made to me in last 7 days)
- [[person/<slug>]] — "<commitment>" expected by <date> (<status>)

## Recent reflections
- YYYY-MM-DD — <last 7 days of /end-day Reflection answers, condensed>

## Recent decisions
- YYYY-MM-DD — <DECISION entries from the last 7 days, surfaced from `### Decisions` sections across active nodes (v4.9+). Include the entry text, the `Revisit when` trigger (if any), and the linked entities.>
```

Capped at ~3000 words total. If the 7-day window produces more, the cache trims to the most-recent / most-referenced and notes the truncation.

## Maintenance triggers

| Trigger | Frequency | Scope of refresh |
|---|---|---|
| `/listen` nightly | Once per day, unattended | Full regeneration after archive + mining complete |
| `/morning` after merge | Once per day, interactive | Full regeneration; new commits are now reflected |
| `/end-day` Step 5.6 | Once per day, interactive | Full regeneration after `/end-day`'s commits land |
| Explicit `/refresh-hot` | On demand | Full regeneration; cheap (~2s) |

All maintenance is **deterministic and zero-LLM**. The cache is a re-render of existing markdown — no synthesis, no judgement. The librarian or research agents may *cite* hot.md but they don't write to it.

## How `/recall` uses it

`/recall`'s auto-fire at conversation start now does:

1. Read `<config-root>/memory/hot.md` first (one file, cached in working memory).
2. Read `<config-root>/memory/user.md` (existing behavior).
3. Read `<config-root>/memory/DASHBOARD.md` (existing behavior).
4. Apply contextual matching against the user's first message — if they mention a person, project, or topic, *additionally* load that node's file.

`hot.md` is the warm-start substrate. DASHBOARD.md is the curated master index. Both load on every session start; they don't duplicate (hot.md is recency-driven, DASHBOARD.md is status-driven).

Explicit `/recall <node>` continues to load the requested node's full content.

## Generation logic

Pure file-walk and date-filtering. No model calls.

1. Read `<config-root>/memory/index.md` for the node list.
2. For each node, parse the file's `## Changelog` section. Extract entries from the last 7 days.
3. For person nodes, also parse `## Recent interactions` — entries from last 7 days.
4. For project / client nodes, also parse `## Open threads` — currently-open threads modified in last 7 days.
5. For workstream nodes (v4.9+), parse `## Recent activity` and `## Open loops` — surface active workstreams in the "What I worked on" section.
6. For all node types, scan `### Decisions` sections. Extract DECISION entries with `[confirmed:...]` in the last 7 days, plus any with `Status: revisit-now` regardless of age. Surface in the "Recent decisions" section. (v4.9+)
7. Walk `<config-root>/briefs/` for the last 7 days. Extract each brief's `## Reflection` section (if present).
8. Walk `<config-root>/memory/staged/commit-drafts/archive/` for resolved drafts in the last 7 days. Note significant decisions / commitments captured.
9. Render the sections above; sort each by date descending.
10. Cap at 3000 words; truncate intelligently (drop oldest, keep most-referenced; never drop a DECISION with Status: revisit-now).
11. Write `<config-root>/memory/hot.md` (overwrite).

## What hot.md is NOT

- **Not a summary.** It cites verbatim from existing nodes; doesn't synthesize.
- **Not curated.** Curated state lives in DASHBOARD.md (which the user / `/cleanup` shape over time).
- **Not derived knowledge.** No INSIGHT / MODEL / GOTCHA extraction here — that's `/remember`'s job.
- **Not a substitute for `memory-librarian`.** When the user asks a broad cross-node question, the librarian still runs.
- **Not write-locked.** Users can edit it but it'll be overwritten on next maintenance run. Hand-edits should go to the source nodes instead.

## Configuration

`<config-root>/plugins/cortex.user-context.md`:

```yaml
hot_cache:
  enabled: true              # set false to disable hot.md entirely
  window_days: 7             # rolling window length
  word_cap: 3000             # max words; cache truncates if longer
  refresh_on:                # which triggers refresh hot.md
    - listen
    - morning
    - end-day
```

If `enabled: false`, `/recall` skips loading hot.md at conversation start (graceful fallback to v4.6 behavior).
