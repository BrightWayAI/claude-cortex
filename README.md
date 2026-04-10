# Cortex v4.0 — Always-On Learning

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/BrightWayAI/session-memory-plugin/actions/workflows/validate.yml/badge.svg)](https://github.com/BrightWayAI/session-memory-plugin/actions/workflows/validate.yml)

**Claude gets smarter about you with every conversation.**

Most AI conversations are disposable. Cortex makes them cumulative. It runs silently in the background — observing your preferences, capturing knowledge, learning from corrections — so every conversation builds on the last.

No commands required. Just use Claude normally. It learns.

Works on **Cowork** (Claude Desktop) and **Claude Code**.

---

## What's New in v4

### The Always-On Brain

v3 required you to say `/remember`. v4 doesn't wait.

| Behavior | What it does | Platform |
|----------|-------------|----------|
| **Auto-recall** | Loads your profile and project context at conversation start | Both |
| **Passive observation** | Silently learns preferences, corrections, and domain knowledge | Both |
| **Contextual recall** | Surfaces relevant knowledge when you mention a project/topic mid-conversation | Both |
| **Auto-commit** | Saves knowledge and observations when the conversation ends | Both |
| **User profile** | Persistent model of who you are and how you like to work | Both |
| **Per-project config** | Control capture aggressiveness per project via `.cortex.json` | Both |
| **Claude Code support** | Drop-in CLAUDE.md instructions + optional hooks | Claude Code |

### The Learning Loop

```
Conversation starts
  → Auto-recall loads your profile + project context
  → Claude adapts to your known preferences

Conversation happens
  → Passive observation accumulates new signals
  → Contextual recall surfaces relevant knowledge on mention
  → Claude adapts in real-time

Conversation ends
  → Auto-commit saves decisions, knowledge, and observations
  → Your profile and project nodes get smarter

Next conversation starts
  → Claude knows more. Repeats less. Helps better.
```

---

## Quick Start

### Cowork (Claude Desktop) — Full Support

1. Download the plugin zip
2. Claude Desktop → Cowork tab → Customize → Upload custom plugin
3. Select `cortex.zip`
4. Start talking. Memory activates automatically.

### Claude Code — Full Support (new in v4)

**Minimal setup (no hooks):**
1. Copy the contents of `claude-code/INSTRUCTIONS.md` into your `~/.claude/CLAUDE.md` (global) or project-level `CLAUDE.md`
2. `mkdir -p ~/Documents/Claude/memory`
3. Start a new Claude Code session. Done.

**With hooks (recommended):**
1. Do the minimal setup above
2. Add the hooks from `claude-code/hooks.json` to your `~/.claude/settings.json`
3. Hooks make auto-recall more reliable by feeding data at session init

---

## How It Works

### Always-On Behaviors (no commands needed)

#### Auto-Recall
At conversation start, Claude reads your user profile and checks for attention items. If you have overdue P0s or stale threads, it tells you. If you mention a known project, it loads context automatically. All silently — no "loading memory..." preamble.

#### Passive Observation
During every conversation, Claude watches for:
- **Corrections** ("don't do that", "I prefer this") — highest priority, always saved
- **Preferences** (communication style, tool choices, working patterns)
- **Domain knowledge** (how your company works, industry terms, constraints)
- **Relationship context** (who's who, who owns what)

It never interrupts to capture these. It adapts in real-time and saves at conversation end.

#### Contextual Recall
When you mention a project, person, or topic with memory, Claude surfaces relevant knowledge naturally — "Heads up, Acme's procurement requires 3 vendor quotes" — without dumping a formal recall block.

#### Auto-Commit
When the conversation ends, Claude silently commits what was learned. No confirmation prompt. If the conversation was trivial, it skips. Corrections and preferences are always saved.

### The User Profile

New in v4: a `user` node that accumulates knowledge about **you**:

- Communication preferences (terse vs. detailed, options vs. decisions)
- Working style (batching, cadence, delegation patterns)
- Corrections (things Claude should never do again)
- Domain expertise (what you know, what needs explaining)
- Relationships (who you work with, their roles)
- Tool preferences (which platforms you use)

This is what makes Claude feel like it "knows" you. It carries across all projects and both platforms.

---

## Explicit Commands

All commands from v3 still work. Use them when you want manual control.

| Command | What it does |
|---------|-------------|
| `/remember` | Full session commit with confirmation |
| `/recall [project?]` | Dashboard (no arg) or specific project context |
| `/learn [node] [type?] [content]` | Quick knowledge capture |
| `/note [node] [content]` | One-liner fact |
| `/search [query]` | Cross-project search |
| `/review` | Weekly synthesis digest |
| `/timeline [project?]` | Chronological activity |
| `/forget [node]` | Archive a project |
| `/cleanup` | Memory health audit |

### Always-On Skill

| Skill | Behavior |
|-------|----------|
| `observe` | Runs silently in every conversation. No trigger needed. Captures preferences, corrections, and domain knowledge. |

### Auto-firing Skills

Commands also fire from natural language:

| Trigger | Skill |
|---------|-------|
| "save this", wrapping up, farewell | `remember` (auto-commit) |
| Conversation start, greeting, "catch me up" | `recall` (auto-recall) |
| "TIL", "gotcha:", "the trick is...", "I was wrong about" | `learn` |
| "note that", "jot down", "quick note" | `note` |
| "any gotchas with", "what's blocked", "how does X work" | `search` |
| "weekly review", "summarize my week" | `review` |
| "we're done with X", "archive X" | `forget` |
| "what have I been working on" | `timeline` |
| "clean up memory", "what's stale" | `cleanup` |

---

## What Gets Captured

### Project State (what changed)
- Decisions made and reasoning
- Open threads with staleness tracking
- Blockers and who/what is blocking
- Artifacts created (docs, decks, proposals)
- Next actions (P0/P1/P2/WAITING)

### Knowledge (what was learned)
| Type | Example |
|------|---------|
| **Insight** | "Churn is an onboarding problem, not a product problem" |
| **Lesson** | "Same-day proposals fail. 48-hour tailored decks close 3x better" |
| **Model** | "Their approval: dept head → finance → VP → procurement" |
| **Gotcha** | "Fiscal year starts April, not January — adjust all budget timing" |
| **Recipe** | "For exec buy-in: lead with their metric, show the gap, propose one action" |
| **Correction** | "Not price-sensitive — they need ROI framing for internal approval" |

### User Observations (who you are)
| Type | Example |
|------|---------|
| **Preference** | "Prefers terse responses — told Claude to stop summarizing" |
| **Correction** | "Don't add emojis to professional communications" |
| **Pattern** | "Starts mornings with email triage, then deep work blocks" |
| **Domain** | "Deep expertise in AI go-to-market — skip 101 explanations" |
| **Relationship** | "Reports to [Name] (CEO), weekly 1:1s on Mondays" |

---

## Per-Project Config

Control behavior per project via `.cortex.json` in the project root:

```json
{
  "node": "client:acme-corp",
  "capture": "aggressive",
  "auto_recall": true,
  "auto_commit": true,
  "observe": true
}
```

| Capture Level | Behavior |
|--------------|----------|
| `"aggressive"` | Capture everything. Use for high-value client work. |
| `"normal"` | Standard capture. Default. |
| `"minimal"` | Only explicit commands. No auto behaviors. |

See `cortex.config.md` for the full spec.

---

## Memory Storage

Memory lives on your computer at `~/Documents/Claude/memory/`. Shared between Cowork and Claude Code.

```
~/Documents/Claude/memory/
├── DASHBOARD.md          ← Master index
├── user.md               ← Your profile (NEW in v4)
├── archive/              ← Archived nodes
├── client/
│   ├── acme-corp.md
│   └── northstar.md
├── bizdev/
│   └── partnerships.md
├── strategy/
│   └── q2-growth.md
├── hiring.md
└── brand.md
```

All files are plain markdown. Human-readable. Editable. Backupable.

---

## Node Conventions

Use kebab-case. Organize however fits your work:

| Pattern | Example |
|---------|---------|
| Client work | `client:acme-corp` |
| Business dev | `bizdev:stripe-partnership` |
| Internal ops | `company-ops`, `hiring`, `finance` |
| Strategy | `strategy:q2-growth` |
| Products | `onboarding-program`, `crm-dashboard` |
| Learning | `learning:sales-ops` |
| Domain | `domain:healthcare-compliance` |
| Infrastructure | `infra:data-pipeline` |
| Personal | `personal` |
| **User profile** | `user` (auto-managed) |

---

## Platform Comparison

| Feature | Cowork | Claude Code |
|---------|--------|-------------|
| Plugin system | Native | Via CLAUDE.md |
| Auto-recall | Skill auto-fire | CLAUDE.md instructions + hooks |
| Auto-commit | Skill auto-fire | CLAUDE.md instructions |
| Passive observation | Always on | Always on |
| Contextual recall | Always on | Always on |
| User profile | Shared | Shared |
| Per-project config | Supported | Supported |
| Explicit commands | All 10 | All 10 |
| Memory files | Shared location | Shared location |

Both platforms read/write the same memory files. Learn something in Cowork → Claude Code knows it. And vice versa.

---

## Changelog

### v4.0.0 — Always-On Learning
- **Passive observation engine**: Claude silently learns about you during every conversation
- **User profile node**: Persistent model of preferences, corrections, patterns, domain expertise
- **Auto-recall**: Context loads at conversation start without commands
- **Auto-commit**: Knowledge saves at conversation end without commands
- **Contextual recall**: Relevant knowledge surfaces mid-conversation on mention
- **Claude Code support**: Full integration via CLAUDE.md instructions and optional hooks
- **Per-project config**: `.cortex.json` for per-directory behavior control
- **Silent mode**: Auto-triggered commits produce no output (unless creating new nodes)
- **The learning loop**: Every conversation makes the next one better

### v3.0.0
- File-based storage at `~/Documents/Claude/memory/`
- Two-tier structure: DASHBOARD.md + individual node files
- Dynamic directory creation from node prefixes
- Archive support

### v2.2.0
- Business-operator friendly language and examples
- Strategy/planning node types

### v2.1.0
- Knowledge-first redesign with six knowledge types
- Added `/learn` and `/note` for quick capture
- `/review` weekly digest

### v2.0.0
- Added `/search`, `/forget`, `/timeline`, `/cleanup`
- Priority system, staleness tracking, cross-project signals

### v1.0.0
- Initial release with `/remember` and `/recall`
