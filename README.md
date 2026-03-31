# Session Memory Plugin v3.0.1

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/BrightWayAI/session-memory-plugin/actions/workflows/validate.yml/badge.svg)](https://github.com/BrightWayAI/session-memory-plugin/actions/workflows/validate.yml)

**Build persistent intelligence — project state AND knowledge — across your working world.**

Most AI conversations are disposable. This plugin makes them cumulative. Every session can produce two kinds of value: **what changed** (decisions, actions, progress) and **what was learned** (insights, gotchas, mental models, techniques). This plugin captures both and makes them retrievable.

Works for any kind of work — client engagements, business development, strategy, operations, hiring, research, learning, and technical projects.

> **Platform note:** This plugin supports **Cowork** (Claude Desktop) and **Claude Code**. Both platforms have full access to all 9 commands and the persistent memory system. See [Setup](#setup) for details.

---

## Quick Start

| You want to... | Command |
|----------------|---------|
| Save a session's context and knowledge | `/remember` |
| Load context before starting work | `/recall [project]` |
| Look up how something works | `/recall [topic]` or `/search [topic]` |
| Quickly capture a gotcha or technique | `/learn [node] [content]` |
| Jot down a quick fact | `/note [node] [content]` |
| Get a weekly digest | `/review` |
| See what happened chronologically | `/timeline [project?]` |
| Archive a finished project | `/forget [node]` |
| Run memory maintenance | `/cleanup` |

---

## What gets captured

Every `/remember` extracts two categories:

### Project State — what changed
- **Decisions made** — what was resolved and why
- **Open threads** — things started but not finished
- **Blockers** — what's preventing progress and who owns it
- **Artifacts** — docs created, proposals sent, decks built
- **Next actions** — prioritized (P0/P1/P2/WAITING)

### Knowledge — what was learned
- **Insights** — "Realized our churn is an onboarding problem, not a product problem"
- **Lessons** — "Tried same-day proposals — close rate dropped. 48-hour tailored decks close 3x better"
- **Mental Models** — "Their approval flow: dept head → finance → VP → procurement"
- **Gotchas** — "Their fiscal year starts April, not January — adjust all budget timing"
- **Recipes** — "For exec buy-in: lead with their metric, show the gap, propose one action"
- **Corrections** — "They're not price-sensitive — they need ROI framing for internal approval"

Knowledge entries are the highest-value content. They persist longer than session logs and surface automatically when you need them.

---

## Commands

### Core — Commit & Recall

#### `/remember`
End-of-session commit. Extracts project state and knowledge, tracks people, spots cross-project signals. Works equally well for a strategy session, a client call debrief, or a pure learning session.

#### `/recall [project | @person | topic]`
Start-of-session context loading:
- **Project**: full state + knowledge base + threads + actions
- **Person**: cross-project profile (which projects, what they own, open items)
- **Topic**: everything known about a subject across all projects
- **No argument**: working world dashboard with all active projects at a glance

### Quick Capture

#### `/learn [node] [type?] [content]`
Capture a single piece of knowledge — no full session extraction needed:
```
/learn client:acme gotcha Their procurement requires 3 vendor quotes even for renewals
/learn bizdev:partnerships model Channel partners want co-marketing before signing
/learn strategy:pricing lesson Usage-based pricing confused mid-market buyers — flat tiers landed better
/learn domain:healthcare recipe For HIPAA BAAs: send our template first, let their legal redline, then negotiate
```
Types: `insight`, `lesson`, `model`, `gotcha`, `recipe`, `correction`. Auto-inferred if omitted.

#### `/note [node] [content]`
Fastest capture — one line, no ceremony:
```
/note client:acme Kim confirmed March 15 deadline
/note hiring Sent offer letter to Jordan for ops manager
/note strategy:pricing Competitor just dropped entry tier to $29/mo
```

### Analysis

#### `/search [query]`
Cross-project search. Finds knowledge, decisions, people, artifacts, blockers, actions:
- "how does their approval process work" → finds MODEL entries
- "any gotchas with Acme's procurement" → finds GOTCHA entries
- "what worked for retention" → finds LESSON entries
- "what's my P0 list" → unified action list across all nodes

#### `/review [--since date] [--until date]`
Synthesized weekly review (not just a timeline — an analytical digest):
- **Progress**: what moved forward
- **Learned**: new knowledge committed
- **Stuck**: blockers and stale threads
- **Decided**: key decisions for accountability
- **Coming Up**: P0/P1 actions across all projects
- **Connections**: cross-project patterns and signals

#### `/timeline [project?] [--since date] [--until date]`
Chronological activity log with velocity assessment and arc analysis.

### Maintenance

#### `/forget [node] [--archive | --merge target]`
Archive (default), merge, or delete project nodes. Cleans up cross-references.

#### `/cleanup`
Memory health audit: stale threads, dormant nodes, orphaned entries, duplicates.

---

## Memory Types

Knowledge entries persist longer than logs — they're the highest-value content.

### Project State
| Entry | Format | Behavior |
|-------|--------|----------|
| **Summary** | `[node] SUMMARY (date): ...` | Replaced each session (always current) |
| **Changelog** | `[node] LOG date — title: ...` | Append-only (never modified) |

### Knowledge
| Entry | Format | When to use |
|-------|--------|-------------|
| **Insight** | `[node] INSIGHT (date): ...` | New realization or connection |
| **Lesson** | `[node] LESSON (date): tried → happened → takeaway` | Something that worked or failed |
| **Model** | `[node] MODEL (date): ...` | How something works (process, workflow, system) |
| **Gotcha** | `[node] GOTCHA (date): ...` | Trap, hidden requirement, or non-obvious behavior |
| **Recipe** | `[node] RECIPE (date): name — when → how` | Reusable technique, playbook, or process |
| **Correction** | `[node] CORRECTION (date): old → new` | Updated or reversed belief |

### Cross-cutting
| Entry | Format |
|-------|--------|
| **People** | `[node] PEOPLE: Name (role) — context. Also in: [nodes]` |
| **Signal** | `[node] SIGNAL from [other-node] (date): implication` |
| **Archive** | `[node] ARCHIVED (date): compressed summary` |

---

## Priority System

Next actions: `[P0]` do now, `[P1]` this week, `[P2]` eventually, `[WAITING:person]` blocked on someone.

## Staleness Tracking

Threads: `[FRESH]`, `[ONGOING]`, `[STALE]` (3+ sessions without progress).
Nodes: Active (7 days), Warm (8-14), Cooling (15-30), Dormant (30+).

---

## Node Conventions

Use kebab-case. Organize however fits your work:

| Pattern | Example |
|---------|---------|
| Client work | `client:acme-corp`, `client:northstar` |
| Business development | `bizdev`, `bizdev:stripe-partnership` |
| Internal ops | `company-ops`, `hiring`, `finance`, `brand` |
| Strategy/planning | `strategy:q2-growth`, `strategy:pricing` |
| Products/services | `onboarding-program`, `crm-dashboard` |
| Learning | `learning:sales-ops`, `learning:ai-tools` |
| Domain knowledge | `domain:tax-law`, `domain:healthcare-compliance` |
| Research | `research:competitor-landscape` |
| Infrastructure | `infra:crm`, `infra:data-pipeline` |
| Personal | `personal`, `personal:finances` |

---

## Git-Aware Memory

When working in a git repository, `/remember` can optionally capture development context:

- **Current branch** — which branch was being worked on
- **Recent commits** — last 3-5 commit messages from the session
- **Uncommitted changes** — high-level summary of staged/modified files
- **Related branches** — feature branches, PRs, or upstream references mentioned

This context is included in the changelog entry, making it easy to pick up exactly where you left off:
```
[crm-dashboard] LOG 2025-03-20 — API refactor: ... | Git: branch feature/api-v2, 3 commits (refactored auth middleware, added rate limiting, updated tests)
```

Git context is automatically skipped for non-code sessions (strategy, client work, etc.).

**Cowork vs Claude Code:** Cowork loads this behavior from `commands/remember.md`. **Claude Code** should use `.claude/commands/remember.md`, which mirrors the same Step 1b git context. Both capture matching `Git: branch …` detail in changelog lines when the session is code-focused.

---

## Auto-firing Skills

All commands also exist as skills that trigger from natural language:

| Trigger pattern | Skill |
|----------------|-------|
| "save this", wrapping up, "remember that X" | `remember` |
| "catch me up", "status of X", "how does X work" | `recall` |
| "TIL", "gotcha:", "the trick is...", "I was wrong about" | `learn` |
| "note that", "jot down", "quick note" | `note` |
| "when did we decide", "any gotchas with", "what's blocked" | `search` |
| "weekly review", "summarize my week", "what did I accomplish" | `review` |
| "we're done with X", "archive X" | `forget` |
| "what have I been working on", "show last week" | `timeline` |
| "clean up memory", "what's stale" | `cleanup` |

---

## How Memory is Stored

Memory lives on your computer at `~/Documents/Claude/memory/`. The plugin creates and manages this folder automatically.

| Platform | Memory path |
|----------|-------------|
| macOS / Linux | `~/Documents/Claude/memory/` |
| Windows | `%USERPROFILE%\Documents\Claude\memory\` (typically `C:\Users\YourName\Documents\Claude\memory\`) |

```
~/Documents/Claude/memory/
├── DASHBOARD.md          ← Master index — one living summary per node, P0 list, recent knowledge
├── archive/              ← Archived nodes get moved here
├── client/
│   ├── acme-corp.md      ← One file per node
│   └── northstar.md
├── bizdev/
│   └── partnerships.md
├── strategy/
│   └── q2-growth.md
├── hiring.md             ← Nodes without a prefix go in the root
└── brand.md
```

Subdirectories are created dynamically from node prefixes. Any prefix is valid — use whatever fits your work.

Both Cowork and Claude Code use the same storage path, so memory is shared seamlessly across platforms. The files are plain markdown — you can read, edit, sync, or back them up with any tool.

---

## Setup

This plugin supports **Cowork** (Claude Desktop) and **Claude Code**. Each platform has its own integration mechanism, but they share the same memory format and storage location (`~/Documents/Claude/memory/`).

### Cowork (Claude Desktop) — Full Support
1. Download the plugin zip
2. Claude Desktop → Cowork tab → Customize → Upload custom plugin
3. Select `session-memory-plugin.zip`
4. Start with `/recall` or `/remember`

**How folder access works**: This plugin needs to read and write files on your computer to persist memory between conversations. The first time you use any memory command (`/remember`, `/recall`, `/learn`, etc.), Claude will automatically request access to `~/Documents/Claude` via the Cowork directory mounting system. You'll see an approval prompt — just approve it and you're set for the rest of the conversation.

This happens once per conversation. You don't need to manually find or attach the folder — the plugin handles it automatically.

**Why this is necessary**: Without file access, everything Claude learns dies when the conversation ends. By storing memory as markdown files on your computer, your knowledge, decisions, and context carry forward into every future session. The files are plain text — you can read, edit, or back them up yourself anytime.

### Claude Code — Supported

Claude Code has native filesystem access — no mounting or approval prompts needed.

**Global setup (recommended):** Memory is shared across projects, so installing once in your user config usually matches how you work.

1. Copy `CLAUDE.md` to `~/.claude/CLAUDE.md`
2. Copy the contents of `.claude/commands/` to `~/.claude/commands/`
3. Memory commands are now available in every project

**Per-project setup:**
1. Copy the `CLAUDE.md` file and `.claude/` directory into your project root
2. Start with `/recall` or just ask — natural language triggers work automatically

**What you get:**
- `CLAUDE.md` loads automatically at session start, giving Claude awareness of your memory system and enabling natural language triggers ("save this", "any gotchas with X", "catch me up")
- All 9 slash commands (`/remember`, `/recall`, `/learn`, `/note`, `/search`, `/review`, `/timeline`, `/forget`, `/cleanup`) work as custom commands
- No approval prompts — Claude Code reads and writes memory files directly

**How it differs from Cowork:**
- No directory mounting step — filesystem access is native
- `CLAUDE.md` auto-loads every session (in Cowork, the plugin system handles this)
- Commands live in `.claude/commands/` instead of the plugin's `commands/` directory

**Cowork `commands/` vs Claude Code:** Files under the plugin's `commands/` folder are written for Cowork. They invoke Cowork's directory-mounting tool (for example `mcp__cowork__request_cowork_directory`), which **does not exist in Claude Code**. **Claude Code users should follow `CLAUDE.md` and use the workflows in `.claude/commands/`** (same behavior, filesystem-native instructions). Do not point Claude Code at the raw `commands/*.md` from the plugin zip unless you replace those Cowork-only tool calls yourself.

### Chat — Not Supported
Chat doesn't have file access or a plugin system. Memory can't persist automatically. You could manually paste node file contents into a project's system prompt, but that's a workaround, not a real integration.

---

## For contributors

Contributions are welcome. Start with **[CONTRIBUTING.md](CONTRIBUTING.md)** (workflow, command/skill parity, versioning) and **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** (how the pieces fit together). Please read the **[Code of Conduct](CODE_OF_CONDUCT.md)**. Security-sensitive reports belong in **[SECURITY.md](SECURITY.md)**. Full release history: **[CHANGELOG.md](CHANGELOG.md)**.

---

## Changelog

See **[CHANGELOG.md](CHANGELOG.md)** for the complete version history. Summary below:

### v3.0.1
- Open source hygiene: `LICENSE`, contributing guides, templates, security policy, architecture doc, and CI validation for `plugin.json` and markdown frontmatter.

### v3.0.0
- **File-based storage**: Memory now persists to `~/Documents/Claude/memory/` as markdown files
- Two-tier structure: `DASHBOARD.md` for fast orientation + individual node files for detail
- Node-to-file mapping: `client:acme-corp` → `memory/client/acme-corp.md`
- Directories created dynamically from node prefixes — any prefix is valid
- Every write operation updates both the node file and the dashboard
- Archive support: `/forget --archive` moves files to `memory/archive/`
- `/cleanup` now audits actual files on disk, detects orphaned entries and missing files
- All 9 commands updated with explicit storage instructions

### v2.2.0
- **Business-operator friendly**: All examples, taxonomy, and language updated for general business use — not just technical projects
- Node conventions now lead with client work, bizdev, strategy, and ops
- Added strategy/planning node type (`strategy:q2-growth`, `strategy:pricing`)
- All knowledge examples rewritten for business contexts (proposals, procurement, pricing, onboarding, retention)

### v2.1.0
- **Knowledge-first redesign**: Memory now captures insights, lessons, mental models, gotchas, recipes, and corrected beliefs as first-class entry types
- Added `/learn` — quick knowledge capture without full session extraction
- Added `/note` — one-liner capture for quick facts
- Added `/review` — synthesized weekly digest with "Learned" as a prominent section
- `/recall` now surfaces knowledge entries prominently (not buried under project state)
- `/recall [topic]` — topic-based knowledge recall across all projects
- `/search` redesigned to prioritize knowledge entries for "how/what/why" queries
- `/remember` extraction expanded to cover both project state and knowledge categories
- Knowledge entries preserved longer than logs during memory consolidation

### v2.0.0
- Added `/search`, `/forget`, `/timeline`, `/cleanup`
- Priority system, staleness tracking, blocker tracking, people index
- Genericized taxonomy, cross-project signals

### v1.0.0
- Initial release with `/remember` and `/recall`
