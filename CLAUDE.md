# Session Memory

You have a persistent memory system stored as markdown files at `~/Documents/Claude/memory/`.

## Storage Layout

```
~/Documents/Claude/memory/
├── DASHBOARD.md          # Master index — living summaries, P0 list, recent knowledge
├── archive/              # Archived nodes
├── client/               # Node files organized by prefix
│   └── acme-corp.md
├── strategy/
│   └── q2-growth.md
└── hiring.md             # Unprefixed nodes live at root
```

Node-to-file mapping: `client:acme-corp` → `memory/client/acme-corp.md`. Nodes without a prefix map directly to `memory/{node}.md`. Create directories as needed.

## Session Start

At the start of every conversation, check if `~/Documents/Claude/memory/DASHBOARD.md` exists. If it does, read it silently and keep the context available. If any P0 actions are overdue or threads are stale, mention them briefly. Do not dump the full dashboard unprompted — just be aware of it.

## Knowledge Taxonomy

Memory captures two categories: **project state** (decisions, threads, blockers, artifacts, next actions) and **knowledge** (reusable insights and patterns).

Knowledge entry types — these are first-class, high-value content:

| Type       | When to use                                         |
|------------|-----------------------------------------------------|
| INSIGHT    | New realization or connection                       |
| LESSON     | Something tried that worked or failed               |
| MODEL      | How something works (process, workflow, system)     |
| GOTCHA     | Trap, hidden requirement, or non-obvious behavior   |
| RECIPE     | Reusable technique, playbook, or process            |
| CORRECTION | Updated or reversed belief                          |

## Auto-Fire Triggers

When you detect these patterns in conversation, run the corresponding command automatically. **Claude Code:** use `.claude/commands/` when present. **Cowork:** the plugin loads the same workflows from `commands/` (those files may call Cowork-only directory tools that do not exist here).

| Pattern | Action |
|---------|--------|
| "save this", wrapping up, "remember that X", "commit this to memory" | Run `/remember` — full session extraction |
| "catch me up", "status of X", "how does X work", "where did we leave off" | Run `/recall` — load project or topic context |
| "TIL", "gotcha:", "the trick is...", "I was wrong about X", "I just realized" | Run `/learn` — capture standalone knowledge |
| "note that", "jot down", "quick note", "FYI for the record" | Run `/note` — one-liner capture |
| "when did we decide", "any gotchas with", "what's blocked", "what are my P0s" | Run `/search` — cross-project search |
| "weekly review", "summarize my week", "what did I accomplish" | Run `/review` — synthesized digest |
| "what have I been working on", "show last week", "timeline of X" | Run `/timeline` — chronological view |
| "we're done with X", "archive X", "close out X" | Run `/forget` — archive or remove node |
| "clean up memory", "what's stale", "memory health check" | Run `/cleanup` — maintenance audit |

## Slash Commands

If `.claude/commands/` is present, these slash commands are available:

| Command | Purpose |
|---------|---------|
| `/remember` | End-of-session commit — extracts state + knowledge |
| `/recall [target]` | Load context for a project, person, topic, or full dashboard |
| `/learn [node] [type?] [content]` | Capture standalone knowledge entry |
| `/note [node] [content]` | Quick one-liner to changelog |
| `/search [query]` | Cross-project search across all memory |
| `/review [--since] [--until]` | Synthesized weekly digest |
| `/timeline [project?] [--since] [--until]` | Chronological activity log |
| `/forget [node] [--archive\|--merge target]` | Archive, merge, or remove a node |
| `/cleanup` | Memory health audit and maintenance |

## Behavior

- Knowledge entries (INSIGHT, LESSON, MODEL, GOTCHA, RECIPE, CORRECTION) are the highest-value content — surface them prominently, preserve them longest.
- Living summaries are replaced each session. Changelogs are append-only.
- Priority tags: `[P0]` do now, `[P1]` this week, `[P2]` eventually, `[WAITING:person]` blocked.
- Staleness: `[FRESH]`, `[ONGOING]`, `[STALE]` (3+ sessions without progress).
- Node activity: Active (7d), Warm (8-14d), Cooling (15-30d), Dormant (30+d).
- Don't fabricate memory. Only surface what's actually committed.
