---
description: Surface working memory into the current conversation. Runs automatically at conversation start to load the user profile and surface attention items. Also runs explicitly via /recall [project] to load full context for a specific project, or /recall alone for the full dashboard.
---

# /recall [project?]

You are surfacing working memory to set up the current session.

---

## Mode Detection

This command runs in one of three modes:

### Auto mode (conversation start — no user trigger)
- Silently load the user profile node first (apply preferences to behavior)
- Check for attention items (overdue P0s, stale threads, dormant nodes reviving)
- If the user's first message references a specific project → load that context
- If the user's first message is a greeting → show brief attention summary
- If the user's first message is a direct task → load relevant context silently, weave in
- Keep output SHORT — just what needs attention

### Explicit mode (user says /recall)
- Full dashboard or project recall as specified
- Complete output with all details

### Contextual mode (mid-conversation reference)
- User mentions a project, person, or topic with memory
- Don't dump a recall block — weave relevant knowledge into your response naturally
- Only surface what's relevant to the current discussion

---

## Step 0 — Load User Profile (ALWAYS, before anything else)

Read `~/Documents/Claude/memory/user.md` if it exists.

Apply immediately and silently:
- Communication preferences → adjust your response style
- Working style → match their pace and patterns
- Corrections → avoid past mistakes
- Tool preferences → use their preferred tools/platforms
- Relationship context → know who's who

**Do NOT announce this.** Just be the version of Claude they've trained you to be.

---

### Finding Memory

Memory is stored in `~/Documents/Claude/memory/`.

**Before reading**: Check if `~/Documents/Claude/memory/` is accessible.
- **Cowork**: Use `mcp__cowork__request_cowork_directory(path="~/Documents/Claude")` to request access. Wait for the user to approve.
- **Claude Code**: The directory is accessible directly via the filesystem.

If the directory cannot be accessed, explain that memory cannot be loaded without this folder and stop.

- `/recall` with no arguments: Read `memory/DASHBOARD.md` and present the dashboard view
- `/recall [node]`: Determine file path from node ID, read that file, present the full project view
  - If node has a prefix (e.g., `client:acme-corp`): `memory/{prefix}/{slug}.md`
  - If no prefix (e.g., `hiring`): `memory/{node-id}.md`
- `/recall @person`: Read DASHBOARD.md to find which nodes exist, then search node files for PEOPLE entries matching the name
- `/recall [topic]`: Read DASHBOARD.md to identify which nodes might be relevant, then search those node files for matching knowledge entries

If the memory directory doesn't exist or is empty, tell the user and offer to help set it up.

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

## If auto-recall at conversation start (greeting or general opening)

Read `DASHBOARD.md` and scan for attention items. Present a BRIEF summary:

```
Welcome back. Here's what needs attention:

**Overdue**
- [P0 action] in [node] — was due [date]

**Stale**
- [thread] in [node] — no progress in [count] sessions

**Recent**
- Last worked on [node] ([date]): [1-line summary]

What are we working on?
```

Rules for auto-recall output:
- **Maximum 8 lines.** This is a glance, not a report.
- If nothing needs attention: "All clear — what are we working on?"
- Only show overdue P0s (not P1/P2), stale threads (3+ sessions), and the 1-2 most recent sessions
- If the user profile has relationship context relevant to today (e.g., a known meeting cadence), weave it in
- Never show the full dashboard in auto mode — that's what explicit `/recall` is for

---

## If contextual recall (mid-conversation mention)

When the user mentions a project, person, or topic with memory:

1. Read the relevant node file
2. Identify the 1-3 most relevant knowledge entries for the current context
3. Weave them into your response naturally — don't format as a recall block
4. Example: User says "I need to follow up with Acme" → you know from memory their
   procurement needs 3 quotes → say "Heads up — Acme's procurement requires 3 vendor
   quotes even for renewals, so factor in 2 weeks lead time."
5. Only surface what's RELEVANT. Having memory doesn't mean dumping memory.

---

## Behavior notes

- No entries → say so, ask if they want to start building context
- Sparse memory → surface what exists, note it'll improve with each session
- Don't editorialize — surface committed data accurately
- Human-readable dates ("March 4")
- Knowledge entries are high-signal — show them prominently, not buried
- Stale threads or overdue P0s → flag proactively
- User profile → apply silently, never announce
- Auto-recall → be brief, be useful, get out of the way
