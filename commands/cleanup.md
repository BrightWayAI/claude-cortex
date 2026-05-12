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

### H. Person-page maintenance (v4.2+)

Check each file in `memory/person/`:

- **Dormant pages** — Last meaningful contact > 12 months ago AND no recent recall-counter activity → suggest archive. Don't auto-archive; surface as a recommendation.
- **Stale Recent interactions** — entries older than 90 days that haven't been moved to the page's `## Archive (>90 days)` section → propose moving them to keep the active surface readable.
- **Person pages with no Linked entities and < 2 Recent interactions** — likely premature graduation. Surface for review.

Format:

```
Person-page maintenance:
- person:[slug]: [issue: dormant | stale-interactions | premature] — suggest: [archive | trim | keep with note]
```

---

## Step 3 — Propose actions

For each issue found, propose a specific action:

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
