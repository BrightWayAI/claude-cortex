---
description: Surface working memory into the current conversation. Load context for a specific project, person, or topic — or see your full working world dashboard.
---

# /recall $ARGUMENTS

You are surfacing working memory to set up the current session.

Parse `$ARGUMENTS`:
- If empty: show full working world dashboard
- If a project node (e.g. `client:acme`, `strategy:q2-growth`): load that project
- If prefixed with `@` (e.g. `@kim`): cross-project person profile
- Otherwise: treat as a topic/keyword search across all knowledge

---

### Finding Memory

Memory is stored at `~/Documents/Claude/memory/`. If the directory doesn't exist or is empty, tell the user and offer to help set it up.

- Dashboard view: Read `memory/DASHBOARD.md`
- Project view: Determine file path from node ID (`{prefix}/{slug}.md` or `{node-id}.md`), read that file
- Person view: Read DASHBOARD.md to find which nodes exist, then search node files for PEOPLE entries matching the name
- Topic view: Read DASHBOARD.md to identify relevant nodes, then search those node files for matching knowledge entries

---

## If a project was specified (e.g. `/recall client:acme`, `/recall strategy:q2-growth`)

1. Read the node file from the memory directory
2. Pull: SUMMARY, recent LOGs, all knowledge entries (INSIGHT/LESSON/MODEL/GOTCHA/RECIPE/CORRECTION), PEOPLE, SIGNALs

3. Compute staleness:
   - **Active**: within 7 days
   - **Warm**: 8-14 days
   - **Cooling**: 15-30 days
   - **Dormant**: 30+ days

4. Present:

```
## [Project Node] — [today's date] [staleness badge]

**Current State**
[living summary]

**What We Know**
[Knowledge entries grouped by type. Show up to 5 most recent, note "N more" if needed.]

Models:
- [MODEL entry]

Gotchas:
- [GOTCHA entry]

Lessons:
- [LESSON entry]

Recipes:
- [RECIPE entry]

Corrections:
- [CORRECTION entry]

Insights:
- [INSIGHT entry]

**Blockers**
[active blockers, or "None"]

**Open Threads** ([count])
- [FRESH/ONGOING/STALE] [thread]

**Next Actions**
- [P0] [action] ← HIGHLIGHT
- [P1] [action]
- [P2] [action]
- [WAITING:who] [action]

**Unanswered Questions**
[from prior sessions, or "None"]

**Key People**
- [Name] ([role]) — [context]

**Recent Sessions**
- [date] [title]: [1-line summary]
- [date] [title]: [1-line summary]
- [date] [title]: [1-line summary]

**Signals from other projects**
[cross-project flags, or "None"]
```

5. Flag [STALE] threads with a warning.
6. End with: **"What are we working on today?"**

---

## If no project specified (just `/recall`)

Full working world dashboard. Sort by recency.

```
## Working World — [today's date]

### Active (within 7 days)

**[node-id]** [badge]
[summary — 1-2 sentences]
Knowledge: [count] entries
Open threads: [count]
Next up: [top action]

...

### Warm / Cooling / Dormant
[same format, less detail]

---

### Needs Attention
[STALE threads, overdue P0s, unresolved blockers]

### Recent Learning
[3-5 most recently committed INSIGHT/LESSON/GOTCHA entries across ALL nodes]

### Cross-Project Signals
[Recent SIGNALs]

### People Across Projects
[Anyone in 2+ nodes]
```

End with: **"Which project are we picking up today?"**

---

## If a person was specified (`/recall @kim`)

```
## [Name] — Cross-Project Profile

**Projects:** [node-id]: [role]. [node-id]: [role].

**Recent mentions:** [date] in [node]: [context]

**Open items involving them:** [WAITING:them] [description]
```

---

## If a topic/keyword was specified (`/recall pricing`, `/recall onboarding`)

Search all knowledge entries + LOGs for the topic.

```
## What we know about: [topic]

**Mental Models**
[MODEL entries]

**Lessons & Insights**
[LESSON/INSIGHT entries]

**Gotchas**
[GOTCHA entries]

**Recipes**
[RECIPE entries]

**Corrections**
[CORRECTION entries]

**Appears in:** [nodes where this comes up]
```

End with: **"Want to dive deeper or add to what we know?"**

---

## Behavior notes

- No entries → say so, ask if they want to start building context
- Sparse memory → surface what exists, note it'll improve with each `/remember`
- Don't editorialize — surface committed data accurately
- Human-readable dates ("March 4")
- Knowledge entries are high-signal — show them prominently, not buried
- Stale threads or overdue P0s → flag proactively
