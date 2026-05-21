---
description: Run maintenance on working memory. Consolidates old log entries, detects stale threads, identifies orphaned nodes, and reports on memory health. Run periodically to keep memory sharp and within limits.
---

# /cleanup

You are performing maintenance on Claude's working memory. This keeps the memory graph healthy and within size limits.

---

## Step 1 — Audit current memory

### How to Audit

**Before auditing**: Check if `~/Documents/Claude/memory/` is accessible.
- **Cowork**: Use `mcp__cowork__request_cowork_directory(path="~/Documents/Claude")` to request access. Wait for the user to approve.
- **Claude Code**: The directory is accessible directly via the filesystem.

If the directory cannot be accessed, explain that memory cannot be audited without this folder and stop.

1. Read `~/Documents/Claude/memory/DASHBOARD.md`
2. List all `.md` files in `memory/` and subdirectories (excluding DASHBOARD.md and archive/)
3. For each file, check: last modified date, number of LOG entries, staleness of open threads
4. Compare dashboard entries against actual files (detect orphaned dashboard entries or node files missing from dashboard)
5. Check `memory/archive/` for any archived nodes

Scan all memory entries and compile:

```
## Memory Health Report — [today's date]

### Size
- Total entries: [count]
- By type: [SUMMARY: x] [LOG: x] [PEOPLE: x] [SIGNAL: x] [ARCHIVED: x]
- Estimated usage: [rough assessment: light / moderate / heavy / near limit]

### Nodes
- Active nodes: [count] (updated within 7 days)
- Warm nodes: [count] (8-14 days)
- Cooling nodes: [count] (15-30 days)
- Dormant nodes: [count] (30+ days)
- Archived nodes: [count]
```

---

## Step 2 — Identify maintenance opportunities

Check for each of these issues:

### A. Log consolidation candidates
Nodes with 10+ LOG entries. Oldest entries can be consolidated:
```
Consolidation candidates:
- [node-id]: [count] log entries. Oldest: [date]. Suggest archiving entries before [date].
```

### B. Stale threads
Open threads that have been open for 3+ sessions or 14+ days without mention:
```
Stale threads:
- [node-id]: "[thread description]" — open since [date], last mentioned [date]
- ...
```

### C. Dormant nodes
Nodes with no activity in 30+ days:
```
Dormant nodes (consider archiving):
- [node-id]: Last active [date]. Summary: [1-line]
- ...
```

### D. Orphaned people
People entries that reference nodes that no longer exist or are archived:
```
Orphaned people entries:
- [Name] references [node-id] which is [archived/missing]
```

### E. Expired signals
SIGNAL entries older than 30 days that were never acted on:
```
Expired signals:
- [signal description] — from [date], between [node] and [node]
```

### F. Duplicate or conflicting entries
Any nodes with multiple SUMMARY entries (should only ever have one), or people listed multiple times:
```
Duplicates found:
- [node-id]: [count] SUMMARY entries (should be 1)
- [Name]: appears [count] times in people index
```

### G. Orphan / isolated notes (v4.2+)

Scan all memory nodes for files that are floating off the map. A node is "isolated" when ALL of:

- **No incoming links** — no other node file mentions this node's id (e.g., as `[client/acme]`, `[strategy/q2-growth]`, or a SIGNAL pointing here)
- **No outgoing links** — this node file doesn't reference any other node id
- **Last updated more than 30 days ago** (use the `> Last updated:` line at the top of the file, or `mtime` as fallback)

For each isolated node, suggest one of three dispositions:

- **Archive** — recommended if the node has < 5 entries total and no open threads
- **Merge into <candidate>** — recommended if a sibling node covers the same topic; suggest by Haiku-tier semantic match against active node summaries (1 call, ~$0.01)
- **Keep as standalone** — accept the orphan if it's a genuine one-off (a reference file, a personal log)

Format:

```
Isolated notes (no inbound or outbound links, untouched 30+ days):
- [node-id]: [last updated date], [entry count] entries — suggest: [archive | merge into <candidate> | keep]
```

Also reflect these in DASHBOARD.md's `## Isolated Notes` section so the user sees them on next conversation start.

### H. Person-page maintenance (v4.2+, deepened in v4.4)

Check each file in `memory/person/`. Load thresholds from `<config-root>/memory/.decay-config.md`:

- `person_threshold_cooling` (default 90)
- `person_threshold_dormant` (default 180)
- `person_threshold_archive` (default 365)

For each page:

- **Cooling pages** — `person_threshold_cooling ≤ days_since_last_contact < person_threshold_dormant` AND < 2 recall-counter increments in last 90 days → flag in DASHBOARD's Active People table with `[cooling]` badge. No action proposed.
- **Dormant pages** — `person_threshold_dormant ≤ days_since_last_contact < person_threshold_archive` AND no recalls in 180+ days → propose `archive`.
- **Cold-archive candidates** — `days_since_last_contact ≥ person_threshold_archive` AND no recalls in 180+ days → propose `archive` with a stronger recommendation flag.
- **Stale Recent interactions** — entries older than 90 days that haven't been moved to the page's `## Archive (>90 days)` section → propose `trim` (move them to the page's archive section).
- **Person pages with no Linked entities and < 2 Recent interactions** — likely premature graduation. Surface for review with `keep with note` or `archive` options.

Format:

```
Person-page maintenance:
- person:[slug]: [state] (last contact <N>d ago, <M> recalls in 180d) — suggest: [archive | trim | keep with note]
```

**On accept of `archive`**: move `<config-root>/memory/person/<slug>.md` to `<config-root>/memory/person/archive/<slug>.md`. Remove the row from DASHBOARD's Active People table. The recall counter entry for the slug is preserved (so if the user later interacts with this person again, `/recall person:<slug>` finds the archived page and can offer to unarchive).

`/recall person:<slug>` on an archived page renders the content but flags it: `**[archived person page]** — moved to archive <date>. To bring back: edit <slug>'s file or run \`/recall person:<slug> --unarchive\`.`

### I. Dormant knowledge entries (v4.4+)

Load thresholds from `<config-root>/memory/.decay-config.md`. Scan all active node files (skip `## Demoted knowledge` sections — those entries are already user-demoted).

For each knowledge entry, compute `age = today - [confirmed:...]` (default to original commit date if tag absent). Cross-reference with the entry's type modifier and the node's `decay_profile` front-matter to get the effective threshold (see `references/decay-model.md`).

Surface:

- **Dormant entries** (`threshold_dormant ≤ age < threshold_cold`) — list them grouped by node, sorted by age desc, capped at 15 per cleanup run. Per-entry suggestion: `rehearse | demote | archive`.
- **Cold entries** (`age ≥ threshold_cold`) — list separately with a stronger flag. Suggest `demote` or `archive` by default.

Format:

```
Dormant knowledge:
- [node-id] INSIGHT (2025-09-12, confirmed:2025-09-12): "<first 80 chars>..." [<N>d dormant] — suggest: rehearse | demote | archive
- ...

Cold knowledge:
- [node-id] MODEL (2024-11-03, confirmed:2024-11-03): "<first 80 chars>..." [<N>d cold] — suggest: demote | archive
- ...
```

CORRECTIONs are excluded from this audit (immune to decay).

**On accept of `rehearse`**: tag the entry for the next `/rehearse` batch (this defers the decision rather than acting now). Logged to `<config-root>/memory/staged/queues/rehearse.md` so `/rehearse` picks them up.

**On accept of `demote`**: move entry to the node's `## Demoted knowledge` section with metadata trail.

**On accept of `archive`**: there's no entry-level archive directory; this is equivalent to `demote` plus a note that the user chose archive. (Entry stays readable, just out of active rotation.)

---

## Step 3 — Propose actions (autonomy-aware in v4.7.2+)

**Consult autonomy mode** per `references/autonomy.md`. Default for `/cleanup`: `suggest`.

- **Mode = `auto`**: execute all proposed actions without the gate. Print the actions inline as they happen ("Consolidating [node-id]... Escalating [thread]..."). This is for trusting users running scheduled cleanups.
- **Mode = `suggest`** (default): standard menu prompt as below; user picks `all` / numbered / `none`.
- **Mode = `confirm`**: walk one action at a time; each gets a per-item yes/no/skip prompt instead of the batch menu.

Default prompt (suggest mode):

```
## Recommended Actions

1. **Consolidate** [node-id] logs: Archive [count] entries from [date range] into 1 archive entry
2. **Escalate** stale thread in [node-id]: "[thread]" → move to SUMMARY as a blocker
3. **Archive** dormant node [node-id]: No activity in [count] days
4. **Clean** orphaned people entry for [Name]
5. **Expire** signal between [node] and [node] from [date]
6. **Deduplicate** [specifics]

Execute all? Or select specific actions? (all / 1,3,5 / none)
```

---

## Step 4 — Execute approved actions

For each approved action:
- **Consolidate**: Create archive entry, delete individual old logs
- **Escalate**: Move thread to SUMMARY with [STALE] tag
- **Archive**: Run the archive process from `/forget --archive`
- **Clean**: Remove or update orphaned entries
- **Expire**: Delete old signal entries
- **Deduplicate**: Merge duplicate entries, keeping the most recent

Report what was done after each action.

---

## Step 4.5 — Refresh memory index (v4.5+)

If any approved actions in Step 4 changed memory (demotions, archives, consolidations, edits), invoke the `indexer` skill to regenerate `<config-root>/memory/index.md`.

Deterministic and zero-LLM — runs in seconds. See `skills/indexer/SKILL.md` and `commands/reindex.md`.

If no actions touched memory in Step 4, skip this step.

---

## Step 4.7 — Log to chronicle (v4.7.1+, centralized in v4.7.2+)

Invoke the `log-writer` skill (see `skills/log-writer/SKILL.md`) with:
- **op_name:** `cleanup`
- **summary:** `<A> actions taken. Section H: <person-pages-archived>. Section I: <dormant-entries-deferred> deferred, <demoted> demoted.`

---

## Step 5 — Post-cleanup summary

```
## Cleanup Complete

- Entries before: [count] → After: [count] (freed [count])
- Actions taken: [count]
- Memory health: [assessment]

Next recommended cleanup: [suggest a date based on activity level]
```

---

## Behavior notes

- Always show the audit report before taking any action
- Never auto-execute — always get user approval for destructive changes
- Default to archive over delete for any content removal
- If memory is already clean and healthy, say so and skip the action proposals
- Suggest running `/cleanup` monthly for moderate users, weekly for heavy users
