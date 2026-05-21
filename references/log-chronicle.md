# Memory log chronicle: `<config-root>/memory/log.md` (v4.7.1+)

A single append-only chronological log of every audit-worthy Nucleus operation. Grep-friendly date prefixes. Inspired by Karpathy's LLM-wiki `log.md` pattern.

## Why

- **One file to answer "what did I do on date X?"** — `grep '## \[2026-05-12' log.md`.
- **Audit trail for /listen runs, /morning merges, /research-gaps runs, /cleanup actions.** Useful when something went wrong, when telemetry is missing, or when reconstructing a decision chain.
- **Onboarding context for any agent.** A fresh Claude session or a non-cortex agent can read the last ~50 entries to learn what's been happening without traversing every node's changelog.
- **Lightweight observability.** Not a substitute for `/log-agent-run` (core-ops telemetry, structured), but complementary — `log.md` is human-readable.

## Format

```markdown
# Memory log

_Append-only chronicle of audit-worthy Nucleus operations. Cortex writes; humans read._

## [2026-05-16 23:00] listen | archived 2026-05-15 (8 events, 12 inbox, 3 mentions, 2 transcripts, 0 errors). 14 proposals staged.

## [2026-05-16 09:12] morning | merged 11 / 14 proposals from 2026-05-15 draft. 2 rejected, 1 deferred. hot.md + memory/index.md refreshed.

## [2026-05-16 17:45] end-day | quick mode. 3 reflection answers captured to briefs/2026-05-16.md ## Reflection. 0 cheap-tier commits proposed. tomorrow brief pre-staged.

## [2026-05-16 17:46] reindex | 47 nodes catalogued (28 fresh, 12 stale, 5 dormant, 2 cold). 8 demoted entries across 6 nodes.

## [2026-05-16 18:01] research-gaps | scanned 47 nodes, found 6 gaps. Researched 3 (1 high confidence, 2 medium). Draft at staged/research-drafts/2026-05-16-research-gaps.md.

## [2026-05-16 18:30] cleanup | section H archived 1 person page (jane-doe → archive/). Section I deferred 4 dormant entries to .rehearse-queue.

## [2026-05-15 11:00] rehearse | walked 4 entries. 2 re-confirmed, 1 demoted, 1 skipped (in skip-log for 30d).

## [2026-05-15 09:00] merge-research-draft | walked 6 findings from 2026-05-14-research-gaps.md. 4 accepted, 2 rejected. Draft archived.
```

Each entry: one H2 line with `[YYYY-MM-DD HH:MM]` prefix, then operation name, then `|`, then a one-line summary. Optional 1-2 line body indented underneath for context (rare; mostly the H2 line is enough).

## Which operations log

| Operation | Logs? | Why |
|---|---|---|
| `/listen` | ✅ | Major event; visible result of overnight work |
| `/morning` | ✅ | Major merge event |
| `/end-day` | ✅ | Daily ritual close; useful timeline anchor |
| `/end-week` | ✅ | Weekly ritual close |
| `/reindex` | ✅ | Cheap but worth tracking — shows when catalog snapshots happened |
| `/research-gaps` | ✅ | Web research activity is audit-worthy |
| `/merge-research-draft` | ✅ | Memory writes from research; track them |
| `/cleanup` | ✅ | Maintenance actions taken |
| `/rehearse` | ✅ | Re-confirmation activity; ties to decay model |
| `/forget` | ✅ | Archive / demote / merge — non-trivial mutations |
| `/setup-*` commands | First completion only | First setup is worth marking; re-runs aren't |
| `/recall` (auto) | ❌ | Fires every session; would flood the log. Skip silently. |
| `/recall` (explicit) | Optional — opt-in via user-context | Mostly noise; only useful if user opts in |
| `/remember` (full mode) | ✅ | Explicit user commit |
| `/remember` (silent mode) | Counter-style entry every 5 commits | Don't log every silent commit; aggregate |
| `/note` | ❌ | Too noisy; the node's own changelog captures it |
| `/learn` | ❌ | Same as `/note` |
| `/search` | ❌ | Read-only; no state change |
| `/timeline` | ❌ | Read-only |
| `/review` | Optional — opt-in | Read-mostly |

## Append-only contract

- Commands **only append** to `log.md`. Never modify or delete prior entries.
- Each command appends **exactly one entry per invocation** (except `/remember` silent mode which aggregates).
- The append happens at the **end** of the command (after all side effects succeed). If a command errors midway, no log entry is written for the partial run.
- File grows ~1-3 KB per active day at steady state. After 1 year: ~500 KB-1 MB. Acceptable.

## Retention

- **Default: never prune.** The log is small enough to keep indefinitely.
- **Optional retention** via `<config-root>/plugins/cortex.user-context.md`:
  ```yaml
  log_chronicle:
    enabled: true
    max_entries: null       # null = no cap; integer = trim to most recent N
    archive_yearly: false   # if true, move prior-year entries to log-archive/YYYY.md on Jan 1
  ```

## How commands implement logging

At the end of each operation (after side effects, before returning to the user), append:

```python
# Pseudocode
log_path = "<config-root>/memory/log.md"
ensure_exists(log_path, "# Memory log\n\n_Append-only chronicle..._\n")
entry = f"## [{today_local_iso_minute}] {op_name} | {one_line_summary}\n"
append(log_path, entry)
```

In skill prose, this is a "## Step N — Log" section at the end of each logged command, with the exact format string as a fenced code block.

## What this file is NOT

- **Not a substitute for `triage-log.md`** (cortex commit-triage decisions; meta-state).
- **Not a substitute for per-node changelogs** (each node's `## Changelog` captures node-specific history).
- **Not a substitute for `/log-agent-run`** (structured agent telemetry via core-ops).
- **Not an event bus.** Other plugins don't subscribe to it; they don't watch for new entries.
- **Not memory content.** The log is observability; memory is knowledge.

## Reading the log

- `grep '## \[2026-05-12' log.md` — what happened on a specific date.
- `grep 'listen |' log.md | tail -10` — last 10 nightly ingest runs.
- `grep 'research-gaps |' log.md` — every gap-fill run ever.
- `tail -100 log.md` — last ~100 operations across all types.

Obsidian users see the file as a chronological timeline; the Dataview plugin can render it as a table if `log.md` is added as a Dataview source.

## When not to add logging to a command

If you're building a new cortex command, ask:
- Is this a state-changing operation? → log
- Is this read-only / observation? → don't log (unless explicitly opt-in)
- Does this fire many times per session? → don't log every instance; aggregate
- Is this a setup / one-time configuration? → log first completion only
