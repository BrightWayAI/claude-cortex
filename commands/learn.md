---
description: Capture standalone knowledge without a full session commit. Use when you've discovered something worth remembering — a gotcha, a mental model, a technique — and want to commit it directly. Faster and more focused than /remember.
---

# /learn [node] [type?] [content]

Quick-commit a single piece of knowledge to a project node.

---

## Usage patterns

```
/learn client:acme gotcha Their procurement team requires 3 vendor quotes even for renewals — build in 2 weeks lead time
/learn bizdev:partnerships model Channel partners want co-marketing commitments before signing — lead with the joint campaign plan, not the rev share
/learn strategy:pricing lesson Tried usage-based pricing with mid-market — too unpredictable for their budgets. Flat tiers with overage charges landed better.
/learn domain:healthcare-compliance recipe For HIPAA BAAs: use our template, get their legal to redline first, then negotiate — saves 2 rounds of back-and-forth
/learn learning:sales-ops insight The bottleneck isn't lead gen — it's the handoff from SDR to AE. Leads go cold in the 48-hour gap.
```

---

## Step 1 — Parse the input

Extract:
- **Node**: Which project node this belongs to (required)
- **Type**: One of: `insight`, `lesson`, `model`, `gotcha`, `recipe`, `correction` (optional — Claude will infer if omitted)
- **Content**: The knowledge to capture

If the user provides just natural language (e.g. `/learn that the API rate limit resets hourly not daily`), Claude should:
1. Infer the most relevant node from conversation context or ask
2. Infer the type from the content
3. Format appropriately

---

## Step 2 — Infer type if not specified

| If the content sounds like... | Assign type |
|-------------------------------|-------------|
| "X works by..." / "Their process is..." / "The way X actually works is..." | MODEL |
| "Watch out for..." / "Don't assume X" / "They require Y even though..." | GOTCHA |
| "Tried X, it [worked/failed] because..." / "What worked was..." | LESSON |
| "I was wrong about X — actually it's Y" / "Turns out..." | CORRECTION |
| "For [situation], do [steps]" / "The playbook for X is..." | RECIPE |
| General realization or connection | INSIGHT |

---

## Step 3 — Write to memory

### Storage Location

**Before writing**: Check if the `~/Documents/Claude/memory/` folder is accessible. If it is not mounted or accessible, ask the user to connect it:

> "I need access to your memory folder to save this. Please mount `~/Documents/Claude` using the folder icon (📎) in the chat input area. This plugin stores memory as files on your computer so it persists between conversations."

Do not proceed until the folder is accessible.

1. Determine the node file path from the node ID:
   - If node has a prefix (e.g., `client:acme-corp`): `~/Documents/Claude/memory/{prefix}/{slug}.md`
   - If no prefix (e.g., `hiring`): `~/Documents/Claude/memory/{node-id}.md`
2. Read the node file if it exists
3. Append the knowledge entry to the appropriate section (Models, Gotchas, Lessons, etc.)
4. If the node file doesn't exist, create it with just a Knowledge section using the standard node file template
5. If the directory doesn't exist, create it
6. Update `~/Documents/Claude/memory/DASHBOARD.md`:
   - Add/update the node's summary in Active Nodes (if this is a new node)
   - Add the entry to Recent Knowledge
   - If the entry is a GOTCHA that applies broadly, also add to Global Gotchas

Write a single knowledge entry:

```
[node-id] [TYPE] (YYYY-MM-DD): [content, compressed but precise]
```

Also check: does this new knowledge invalidate or reinforce any existing entries in this node? If so:
- **Invalidate**: Remove or update the old entry, note the correction
- **Reinforce**: No action needed, but mention it in confirmation

Update the living summary if this knowledge materially changes the current state of the node.

---

## Step 4 — Confirm

Brief confirmation:
```
Committed to [node-id]:
[TYPE]: [content]

[If applicable: "This updates/replaces a previous [TYPE] entry from [date]."]
```

---

## Behavior notes

- This is the fast path. No full extraction, no changelog entry, no continuity check.
- If the user isn't in a conversation with enough context to infer the node, ask.
- Multiple `/learn` calls in one session are fine — each writes independently.
- If the knowledge clearly spans multiple nodes, write to each.
