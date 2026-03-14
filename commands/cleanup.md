---
description: Run maintenance on working memory. Consolidates old log entries, detects stale threads, identifies orphaned nodes, and reports on memory health. Run periodically to keep memory sharp and within limits.
---

# /cleanup

You are performing maintenance on Claude's working memory. This keeps the memory graph healthy and within size limits.

---

## Step 1 — Audit current memory

### How to Audit

**Before auditing**: Check if `~/Documents/Claude/memory/` is accessible. If not, use the `request_cowork_directory` tool to request access:

```
mcp__cowork__request_cowork_directory(path="~/Documents/Claude")
```

The user will see an approval prompt. Wait for the mount to succeed before proceeding. If the user declines, explain that memory cannot be audited without this folder and stop.

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
- Active nodes: [count] (updated within 14 days)
- Warm nodes: [count] (15-30 days)
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
