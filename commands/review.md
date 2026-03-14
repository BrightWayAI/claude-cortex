---
description: Generate a synthesized weekly review of activity and learning across all projects. Produces a shareable summary covering what moved forward, what was learned, what's stuck, and what's coming up. Different from /timeline (raw chronology) — this is an analytical digest.
---

# /review [--since date] [--until date]

Generate a weekly (or custom period) review that synthesizes project activity and learning into a shareable digest.

---

### Data Source

**Before reviewing**: Check if `~/Documents/Claude/memory/` is accessible. If not, use the `request_cowork_directory` tool to request access:

```
mcp__cowork__request_cowork_directory(path="~/Documents/Claude")
```

The user will see an approval prompt. Wait for the mount to succeed before proceeding. If the user declines, explain that the review cannot be generated without this folder and stop.

1. Read `~/Documents/Claude/memory/DASHBOARD.md` for the overview
2. Read node files for any nodes updated within the review period
3. Focus on: new knowledge entries, decisions in changelogs, changes in P0/P1 actions, resolved vs. new threads

---

## Step 1 — Determine scope

- Default: last 7 days
- Custom: use `--since` and `--until` if provided
- Pull: all LOG entries, knowledge entries, SIGNAL entries, and current SUMMARYs within the period

---

## Step 2 — Synthesize by category

Don't just list entries chronologically (that's `/timeline`). Synthesize into themes:

```
## Weekly Review — [date range]

### Progress
[Which projects moved forward and what was accomplished. Group related activities across days. Be specific: "Shipped X", "Resolved Y", "Decided Z".]

### Learned
[New knowledge committed during this period. The most interesting/useful INSIGHT, LESSON, MODEL, GOTCHA, RECIPE, CORRECTION entries. This is the "intellectual growth" section.]

### Stuck
[Projects with unresolved blockers, stale threads, or no activity. What's preventing progress and what needs to happen to unblock.]

### Decided
[Key decisions made during this period, with brief reasoning. Useful for accountability and revisiting later.]

### Coming Up
[P0 and P1 actions across all projects. What needs attention this week.]

### Connections
[Cross-project signals that fired. Knowledge from one project that applies to another. Patterns across projects.]

---

**By the Numbers**
- Projects touched: [count]
- Sessions logged: [count]
- Knowledge entries committed: [count]
- Decisions made: [count]
- Open threads: [count] ([count] stale)
- Blockers: [count] active
```

---

## Step 3 — Highlight notable items

Call out 1-3 things worth the user's attention:

```
### Worth Noting
- [Something that might get lost in the noise but is important]
- [A pattern across projects — e.g. "You've been context-switching heavily between 4 projects this week"]
- [A stale thread that's becoming urgent]
- [A correction that changes how a prior decision should be viewed]
```

---

## Step 4 — Offer export

"Want me to format this for Slack/email? Or commit any reflections from this review to memory?"

---

## Behavior notes

- This is synthesis, not listing. Add structure and insight.
- If the period was quiet (few entries), say so: "Light week — only [count] sessions across [count] projects."
- If the period was intense, note the intensity: "Heavy week — [count] sessions, [count] decisions, [count] new knowledge entries."
- Don't fabricate activity. Only surface what was committed.
- The "Learned" section is what makes this different from a standard status report — treat it as a first-class section, not an afterthought.
- If certain projects dominated the period, note the allocation: "80% of activity was on [node] — other projects may need attention."
