---
description: Archive or remove a project node from working memory. Use when a project is complete, abandoned, or no longer relevant. Supports full removal, archival (compress to a single summary), or merging two nodes together.
---

# /forget [node-id] [--archive | --merge target-node]

You are modifying the project memory graph. This is a destructive operation — confirm with the user before proceeding.

---

## Step 1 — Validate the node

Search Claude's memory for the specified node. If it doesn't exist, tell the user and list the nodes that do exist.

If it exists, show the user what will be affected:
```
## Forgetting: [node-id]

**Living Summary**: [the current summary]
**Changelog entries**: [count] entries spanning [earliest date] to [latest date]
**People entries**: [count] people indexed under this node
**Signals**: [count] cross-project signals involving this node
```

---

## Step 2 — Determine the operation

### Default: Archive (safe)
Compress all memory for this node into a single archival entry, then remove the individual entries:
```
[node-id] ARCHIVED (YYYY-MM-DD): [1-2 sentence summary of what this project was and how it concluded]. Key decisions: [top 3]. Key people: [names]. [count] sessions logged from [start] to [end].
```

This preserves searchability while freeing memory space.

### With `--merge [target]`: Merge into another node
Move all relevant context from the source node into the target node:
- Append a LOG entry to the target noting the merge
- Transfer any people entries
- Transfer any open threads or next actions
- Delete the source node's entries
- Update the target's living summary to reflect the merged context

### Full removal (only if user explicitly says "delete" or "remove completely")
Remove all memory entries for this node. This is irreversible.

---

## Step 3 — Confirm

**Always ask for explicit confirmation before executing.** Show exactly what will happen:

```
I'll [archive/merge/delete] the [node-id] node. This will:
- [action 1]
- [action 2]
- [action 3]

Proceed? (yes/no)
```

Wait for confirmation before modifying memory.

---

## Step 4 — Execute and report

### File Operations

Memory is stored in `~/Documents/Claude/memory/`.

**Before modifying**: Check if `~/Documents/Claude/memory/` is accessible. If not, use the `request_cowork_directory` tool to request access:

```
mcp__cowork__request_cowork_directory(path="~/Documents/Claude")
```

The user will see an approval prompt. Wait for the mount to succeed before proceeding. If the user declines, explain that memory cannot be modified without this folder and stop.

- **Archive** (default): Move the node file from its current location to `memory/archive/{filename}`. Remove the node's entry from DASHBOARD.md Active Nodes. Add a one-line entry to the Dormant or a new "Archived" section in DASHBOARD.md.
- **Merge**: Read both node files. Append source's changelog, knowledge, and people entries to the target file. Delete the source file. Update DASHBOARD.md.
- **Delete**: Remove the node file entirely. Remove from DASHBOARD.md.

After execution, confirm what was done:
- For archive: "Archived [node-id]. It's searchable but won't appear in dashboards."
- For merge: "Merged [source] into [target]. Updated [target]'s summary."
- For delete: "Removed all [count] entries for [node-id]."

---

## Step 5 — Clean up cross-references

After archiving/deleting, scan for:
- SIGNAL entries in other nodes that reference this node — update them to note the node is archived/deleted
- PEOPLE entries in other nodes that mention this node — update the "Also in:" list
- Any WAITING actions in other nodes that depend on this node — flag them for the user

---

## Behavior notes

- Default to archive, not delete. Data loss should require extra intent.
- If the node has open P0 or P1 actions, warn the user before proceeding
- If the node has cross-project signals to active nodes, flag this
- Never archive/delete `personal` without strong explicit confirmation
