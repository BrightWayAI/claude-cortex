# Cortex — Claude Code Integration

> Drop this into your project's `CLAUDE.md` or `~/.claude/CLAUDE.md` (global) to enable persistent memory in Claude Code.
> For the full plugin with all 9 commands and the always-on observation engine, use Cowork (Claude Desktop). This file provides the core always-learning behaviors for Claude Code.

---

## Memory Location

Memory is stored at `~/Documents/Claude/memory/`. This directory is shared between Cowork and Claude Code — both platforms read and write to the same memory files. What you learn in Cowork carries over to Claude Code and vice versa.

If the directory doesn't exist, create it with `mkdir -p ~/Documents/Claude/memory` on first write. For reliable setup, users should create this directory manually during initial setup.

---

## Always-On Behaviors

These behaviors run automatically in EVERY conversation. No commands needed.

### 1. Auto-Recall (conversation start)

At the start of every conversation:

1. **Read `~/Documents/Claude/memory/user.md`** if it exists. Apply preferences silently:
   - Communication style (terse vs. detailed, options vs. decisions)
   - Tool preferences
   - Known corrections (things to avoid)
   - Working style patterns
2. **Read `~/Documents/Claude/memory/DASHBOARD.md`** if it exists. Check for:
   - Overdue P0 actions (3+ days past due)
   - Stale threads (3+ sessions without progress)
   - Recent activity (what was last worked on)
3. **If the user's first message references a known project or topic:**
   - Read that node's file and weave relevant context into your response
   - Don't dump a recall block — naturally incorporate what you know
4. **If the user's first message is a greeting or general start:**
   - Show a brief attention summary (max 8 lines) if there are overdue/stale items
   - Otherwise: just proceed, no memory preamble needed

### 2. Passive Observation (during conversation)

Throughout every conversation, silently observe:

- **Corrections**: User corrects your approach → note it for commit
- **Preferences**: User expresses or demonstrates how they like to work → note it
- **Domain knowledge**: User shares facts about their company, team, industry → note it
- **Relationships**: User mentions people and their roles/context → note it
- **Patterns**: Repeated behaviors across conversations → note after 2+ signals

**Rules:**
- Never interrupt to capture an observation
- Never announce "I noticed you prefer X"
- Adapt your behavior in real-time based on observations
- Queue observations for commit at conversation end

### 3. Contextual Recall (mid-conversation)

When the user mentions a project, person, or topic that exists in memory:

- Read the relevant node file
- Surface the 1-3 most relevant pieces of knowledge for the current context
- Weave them in naturally: "Heads up — [relevant gotcha/model/lesson]"
- Don't format as a formal recall block

### 4. Auto-Commit (conversation end)

When the conversation is ending (user says thanks, goodbye, signs off, or the task is complete):

1. **Assess conversation value:**
   - Were decisions made? → commit to project node
   - Was knowledge shared? → commit to project node
   - Were corrections given? → ALWAYS commit to user node
   - Were preferences expressed? → commit to user node
   - Was it trivial small talk? → skip

2. **Commit silently:**
   - No "Want me to save this?" prompt
   - No confirmation output
   - Just write to the appropriate node files and update DASHBOARD.md
   - Exception: if creating a NEW node, briefly mention it

3. **User observations** go to `~/Documents/Claude/memory/user.md`
4. **Project knowledge** goes to the appropriate node file
5. **Dashboard** gets updated with timestamps and any new P0 actions

---

## Memory File Formats

### User Profile (`~/Documents/Claude/memory/user.md`)

```markdown
# user
> Last updated: YYYY-MM-DD

## Communication Preferences
[user] PREFERENCE (date): [observation]

## Working Style
[user] PATTERN (date): [observation]

## Corrections
[user] CORRECTION (date): [what was wrong] → [what they wanted]. Why: [reason]

## Domain Expertise
[user] MODEL (date): [knowledge about their domain/expertise]

## Relationships & Org Context
[user] PEOPLE: [Name] ([role]) — [context]

## Tool & Platform Preferences
[user] PREFERENCE (date): [tool/platform preference]
```

### Project Nodes (`~/Documents/Claude/memory/{prefix}/{slug}.md`)

```markdown
# {node-id}
> Last updated: YYYY-MM-DD

## Summary
[Living summary — replaced each session]

## Knowledge

### Models
[node] MODEL (date): [entry]

### Gotchas
[node] GOTCHA (date): [entry]

### Lessons
[node] LESSON (date): [entry]

### Recipes
[node] RECIPE (date): [entry]

### Insights
[node] INSIGHT (date): [entry]

### Corrections
[node] CORRECTION (date): [entry]

## People
[node] PEOPLE: Name (role) — context. Also in: [other nodes]

## Changelog
[node] LOG YYYY-MM-DD — title: content
(append-only, newest first)

## Open Threads
- [FRESH/ONGOING/STALE] [description]

## Next Actions
- [P0] [action]
- [P1] [action]
- [WAITING:who] [action]

## Signals
[node] SIGNAL from [other-node] (date): [implication]
```

### Dashboard (`~/Documents/Claude/memory/DASHBOARD.md`)

The master index. Updated after every write. Contains:
- One-line living summary per active node
- Unified P0 action list
- Waiting-on list
- Recent knowledge entries (last 7 days)

---

## Explicit Commands

These work in Claude Code when the user types them:

| Command | What it does |
|---------|-------------|
| `/remember` | Full session commit with confirmation |
| `/recall` | Full dashboard or project recall |
| `/recall [project]` | Load specific project context |
| `/learn [node] [type?] [content]` | Quick knowledge capture |
| `/note [node] [content]` | One-liner fact capture |
| `/search [query]` | Cross-project knowledge search |
| `/review` | Weekly synthesis digest |
| `/timeline` | Chronological activity view |
| `/forget [node]` | Archive a project node |
| `/cleanup` | Memory health audit |

For full command documentation, see the Cortex plugin's `commands/` directory.

---

## Per-Project Config

If a `.cortex.json` file exists in the project root, respect its settings:

```json
{
  "node": "client:acme-corp",
  "capture": "aggressive",
  "auto_recall": true,
  "auto_commit": true,
  "observe": true,
  "knowledge_types": ["model", "gotcha", "lesson", "recipe"],
  "memory_path": "~/Documents/Claude/memory",
  "ignore_patterns": ["*.test.*", "node_modules/**"]
}
```

- **node**: Default project node for this directory (auto-detected if not set)
- **capture**: `"aggressive"` (capture everything), `"normal"` (default), `"minimal"` (only explicit commands)
- **auto_recall**: Load project context on conversation start (default: true)
- **auto_commit**: Commit on conversation end (default: true)
- **observe**: Run passive observation (default: true)
- **knowledge_types**: Which knowledge types to prioritize for this project
- **memory_path**: Override the memory storage directory (default: `~/Documents/Claude/memory`). Use for project-isolated memory.
- **ignore_patterns**: Glob patterns for files/topics to exclude from observation and capture. Useful for test files, generated code, etc.

---

## The Learning Loop

```
Conversation starts
  → Auto-recall loads user profile + project context
  → Claude adapts behavior based on known preferences

Conversation happens
  → Passive observation silently accumulates new signals
  → Contextual recall surfaces relevant knowledge on mention
  → Claude adapts in real-time to new observations

Conversation ends
  → Auto-commit saves decisions, knowledge, and observations
  → User profile and project nodes get smarter

Next conversation starts
  → Auto-recall loads UPDATED profile + context
  → Claude starts where it left off, with everything learned
```

Every conversation makes the next one better.
