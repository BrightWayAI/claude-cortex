---
description: Quick one-liner capture to a project node. Lighter than /remember (no extraction process) and lighter than /learn (no knowledge typing). Just append a timestamped note to the changelog. Use for quick facts, status updates, or things worth noting that don't need structure.
---

# /note $ARGUMENTS

The fastest way to commit something to memory. One line, no ceremony.

---

## Usage patterns

```
/note client:acme Kim confirmed the March 15 deadline
/note bizdev Had intro call with Stripe partnership team — they're interested
/note hiring Sent offer letter to Jordan for the ops manager role
/note strategy:pricing Competitor just dropped their entry tier to $29/mo
/note company-ops Renewed Slack and Notion — annual contracts locked through 2027
/note learning:ai-tools Finished testing Cursor vs Claude Code — notes in the shared doc
```

---

## Step 1 — Parse

Extract:
- **Node**: Which project node (required)
- **Content**: The note (everything after the node)

If node is ambiguous or missing, infer from conversation context or ask.

---

## Step 2 — Write

### Storage Location

**Before writing**: Resolve `<config-root>` per `references/core-contract.md` §1 (respects the legacy pointer, the new `~/.cortex/config-root` pointer, and the `~/Documents/Claude` default — do not hardcode the default path).
- **Cowork**: Use `mcp__cowork__request_cowork_directory(path=<config-root>)` to request access. Wait for the user to approve.
- **Claude Code**: The directory is accessible directly via the filesystem.

If the directory cannot be accessed, explain that memory cannot be persisted without this folder and stop.

1. Determine the node's relative file path from the node ID (`references/core-contract.md` §3; legacy `client:acme-corp` colon syntax and `client/acme-corp` slash syntax map to the same file).
2. Build the LOG entry: `[node-id] LOG YYYY-MM-DD — Note: [content]`
3. Write it with the shared locking/atomic-write utility rather than an ad-hoc file edit — this is what actually acquires the lock, creates the node file from the standard template if it doesn't exist, and performs the write atomically:

   ```
   python3 scripts/cortex_cli.py prepend-section \
     --memory-root <config-root>/memory \
     "<node-relative-path>" "## Changelog" "[node-id] LOG YYYY-MM-DD — Note: [content]"
   ```

   This inserts the entry newest-first in `## Changelog` and creates the section/file if absent. It handles locking and atomic writes internally — do not also hand-edit the file for this step.
4. Update `<config-root>/memory/DASHBOARD.md` "Last updated" timestamp.
5. Only update the dashboard summary if the note represents a significant state change.

Do NOT update the living summary unless the note represents a significant state change (e.g. a project completing, a major blocker resolving).

---

## Step 3 — Confirm

One-line confirmation:
```
Noted in [node-id]: [content]
```

That's it. No analysis, no follow-up questions.

---

## Behavior notes

- Absolute minimum friction. This should feel like jotting something on a sticky note.
- No extraction, no knowledge typing, no continuity check.
- If the user streams multiple `/note` calls, handle each independently.
- If the content looks like it should be a knowledge entry (gotcha, lesson, model), suggest: "This sounds like a [gotcha/lesson/model] — want me to `/learn` it instead so it's easier to find later?"
