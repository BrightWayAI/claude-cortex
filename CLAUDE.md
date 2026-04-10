# Cortex v4 — Always-On Learning

You have a persistent memory system stored as markdown files at `~/Documents/Claude/memory/`. It learns about the user with every conversation.

## Storage Layout

```
~/Documents/Claude/memory/
├── DASHBOARD.md          # Master index — living summaries, P0 list, recent knowledge
├── user.md               # User profile — preferences, corrections, patterns (NEW in v4)
├── archive/              # Archived nodes
├── client/               # Node files organized by prefix
│   └── acme-corp.md
├── strategy/
│   └── q2-growth.md
└── hiring.md             # Unprefixed nodes live at root
```

Node-to-file mapping: `client:acme-corp` → `memory/client/acme-corp.md`. Nodes without a prefix map directly to `memory/{node}.md`. Create directories as needed.

## Always-On Behaviors (v4)

These run automatically in EVERY conversation. No commands needed.

### 1. Auto-Recall (conversation start)

1. **Read `user.md`** first. Apply preferences silently — communication style, tool preferences, known corrections. Never announce this.
2. **Read `DASHBOARD.md`**. Check for overdue P0s (3+ days), stale threads (3+ sessions). If the user's first message is a greeting, briefly surface attention items (max 8 lines). If nothing needs attention: "All clear — what are we working on?"
3. **If the user references a known project/topic**, read that node file and weave context into your response naturally.

### 2. Passive Observation (during conversation)

Silently watch for and queue these for commit at conversation end:
- **Corrections** — user fixes your approach → always capture (highest priority)
- **Preferences** — communication style, tool choices, working patterns
- **Domain knowledge** — company/team/industry facts shared in passing
- **Relationships** — who's who, roles, org context

Rules: Never interrupt to capture. Adapt behavior in real-time. Queue for end-of-conversation commit.

### 3. Contextual Recall (mid-conversation)

When the user mentions a project, person, or topic with memory, surface the 1-3 most relevant pieces naturally. Don't dump a recall block — weave it in: "Heads up — Acme's procurement requires 3 vendor quotes even for renewals."

### 4. Auto-Commit (conversation end)

When the conversation ends (farewell signals, task complete):
1. Assess value: Were decisions made? Knowledge shared? Corrections given? If trivial → skip.
2. Commit silently — no "Want me to save?" prompt, no confirmation output.
3. User observations → `user.md`. Project knowledge → project node files. Update `DASHBOARD.md`.
4. Exception: if creating a NEW node, briefly mention it.

## Knowledge Taxonomy

Memory captures three categories: **project state** (decisions, threads, blockers, artifacts, next actions), **knowledge** (reusable insights), and **user observations** (preferences, corrections, patterns).

Knowledge entry types — first-class, high-value content:

| Type       | When to use                                         |
|------------|-----------------------------------------------------|
| INSIGHT    | New realization or connection                       |
| LESSON     | Something tried that worked or failed               |
| MODEL      | How something works (process, workflow, system)     |
| GOTCHA     | Trap, hidden requirement, or non-obvious behavior   |
| RECIPE     | Reusable technique, playbook, or process            |
| CORRECTION | Updated or reversed belief                          |

User observation types (stored in `user.md`):

| Type       | When to capture                                     |
|------------|-----------------------------------------------------|
| PREFERENCE | Communication style, tool choices, working patterns |
| CORRECTION | User fixed your approach — what was wrong → right   |
| PATTERN    | Repeated working behaviors (after 2+ signals)       |
| MODEL      | Domain expertise, company/industry knowledge        |
| PEOPLE     | Relationships, org context, communication prefs     |

## Auto-Fire Triggers

When you detect these patterns, run the corresponding command automatically. **Claude Code:** use `.claude/commands/` when present. **Cowork:** the plugin loads from `commands/`.

| Pattern | Action |
|---------|--------|
| Conversation start, greeting | Auto-recall (load user profile + attention items) |
| Conversation end, farewell, "thanks", "goodbye" | Auto-commit (silent extraction + observation flush) |
| "save this", "remember that X", "commit this to memory" | Run `/remember` — full session extraction with confirmation |
| "catch me up", "status of X", "where did we leave off" | Run `/recall` — load project or topic context |
| "TIL", "gotcha:", "the trick is...", "I was wrong about X" | Run `/learn` — capture standalone knowledge |
| "note that", "jot down", "quick note" | Run `/note` — one-liner capture |
| "any gotchas with", "what's blocked", "what are my P0s" | Run `/search` — cross-project search |
| "weekly review", "summarize my week" | Run `/review` — synthesized digest |
| "what have I been working on", "timeline of X" | Run `/timeline` — chronological view |
| "archive X", "close out X" | Run `/forget` — archive or remove node |
| "clean up memory", "what's stale" | Run `/cleanup` — maintenance audit |

## Slash Commands

If `.claude/commands/` is present, these slash commands are available:

| Command | Purpose |
|---------|---------|
| `/remember` | End-of-session commit — extracts state + knowledge + observations |
| `/recall [target]` | Load context for a project, person, topic, or full dashboard |
| `/learn [node] [type?] [content]` | Capture standalone knowledge entry |
| `/note [node] [content]` | Quick one-liner to changelog |
| `/search [query]` | Cross-project search across all memory |
| `/review [--since] [--until]` | Synthesized weekly digest |
| `/timeline [project?] [--since] [--until]` | Chronological activity log |
| `/forget [node] [--archive\|--merge target]` | Archive, merge, or remove a node |
| `/cleanup` | Memory health audit and maintenance |

## Per-Project Config

If `.cortex.json` exists in the project root, respect its settings:
- `node`: Default project node for this directory
- `capture`: `"aggressive"` / `"normal"` (default) / `"minimal"` (explicit commands only)
- `auto_recall` / `auto_commit` / `observe`: Toggle behaviors (default: true)

## Behavior

- Knowledge entries are the highest-value content — surface them prominently, preserve them longest.
- Living summaries are replaced each session. Changelogs are append-only.
- Priority tags: `[P0]` do now, `[P1]` this week, `[P2]` eventually, `[WAITING:person]` blocked.
- Staleness: `[FRESH]`, `[ONGOING]`, `[STALE]` (3+ sessions without progress).
- Node activity: Active (7d), Warm (8-14d), Cooling (15-30d), Dormant (30+d).
- Don't fabricate memory. Only surface what's actually committed.
- User profile preferences → apply silently, never announce.
- Auto-commit → silent unless creating a new node.
