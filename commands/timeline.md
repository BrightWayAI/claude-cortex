---
description: Show a chronological timeline of activity across all projects or a single project. Useful for reviewing what happened over a time period, preparing weekly updates, or understanding the arc of a project.
---

# /timeline [project?] [--since date] [--until date]

You are constructing a chronological view of session history from working memory.

---

### Data Source

1. If a project is specified: read that node's file from `~/Documents/Claude/memory/`, extract all LOG entries, sort chronologically
2. If no project: read all node files, extract all LOG entries, sort chronologically across all nodes
3. Use `~/Documents/Claude/memory/DASHBOARD.md` to identify which nodes to scan

---

## Step 1 — Determine scope

- **With project**: Show timeline for that specific node
- **Without project**: Show timeline across all nodes
- **With date range**: Filter to the specified period
- **Default**: Last 14 days if no range specified

---

## Step 2 — Gather entries

Pull all LOG entries (and SIGNAL entries) within scope. Sort chronologically, oldest to newest.

---

## Step 3 — Present the timeline

### Single-project timeline:

```
## Timeline: [node-id] — [date range]

### [Week of Month Day]

**[Day, Month Date]**
[session title]: [1-line summary of decisions + actions]
[artifacts created, if any]

**[Day, Month Date]**
[session title]: [1-line summary]

### [Week of Month Day]
...

---

**Arc summary**: [2-3 sentences describing the trajectory — is this project accelerating, stalled, pivoting?]

**Velocity**: [count] sessions in [count] days. [Assessment: high/steady/low/stalled]

**Unresolved from this period**:
- [open thread or action still pending]
```

### Cross-project timeline:

```
## Timeline: All Projects — [date range]

### [Day, Month Date]

[node-id] — [session title]: [1-line summary]
[node-id] — [session title]: [1-line summary]

### [Day, Month Date]

[node-id] — [session title]: [1-line summary]

...

---

**Period Summary**
- Most active: [node-id] ([count] sessions)
- Least active: [node-id] ([count] sessions or "0 — dormant")
- Cross-project activity: [any signals that fired during this period]

**Attention needed**:
- [node-id]: [reason — e.g. "3 sessions with no decisions, may be spinning"]
- [node-id]: [reason — e.g. "P0 action from March 2 still open"]
```

---

## Step 4 — Offer follow-up

Based on what the timeline shows:
- If a project is stalling: "Want to do a focused session on [node] to break through the blockers?"
- If lots of activity: "Want me to draft a weekly update summary from this?"
- If the user seems to be reviewing: "Want to `/remember` any reflections from this review?"

---

## Behavior notes

- Keep individual entries to one line — this is a scan view, not a detail view
- Use `/recall [node]` for detail on any specific project
- If memory is sparse for the period, say so — don't pad with filler
- The "arc summary" should be based solely on committed memory, not speculation
- Velocity assessment thresholds:
  - High: 4+ sessions/week
  - Steady: 2-3 sessions/week
  - Low: 1 session/week
  - Stalled: 0 sessions in 7+ days
