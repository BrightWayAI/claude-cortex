# Session Memory Plugin v2.1

**Build persistent intelligence — project state AND knowledge — across your working world.**

Most AI conversations are disposable. This plugin makes them cumulative. Every session can produce two kinds of value: **what changed** (decisions, actions, progress) and **what was learned** (insights, gotchas, mental models, techniques). This plugin captures both and makes them retrievable.

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

## Commands

### Core — Commit & Recall

#### `/remember`
End-of-session commit. Extracts both **project state** and **knowledge**:
- Project state: decisions, open threads, blockers, artifacts, prioritized next actions
- Knowledge: insights, lessons learned, mental models, gotchas, patterns/recipes, corrected beliefs
- Cross-project signals, people index, continuity tracking
- Works for pure learning sessions with zero project state changes

#### `/recall [project | @person | topic]`
Start-of-session context loading:
- **Project**: full state + knowledge base + threads + actions
- **Person**: cross-project profile (which projects, what they own, open items)
- **Topic**: everything known about a subject across all projects (models, gotchas, lessons)
- **No argument**: working world dashboard with recent learning highlighted

### Quick Capture

#### `/learn [node] [type?] [content]`
Capture a single piece of knowledge directly — no full session extraction:
```
/learn infra:aws gotcha Lambda env vars aren't encrypted at rest
/learn crm-dashboard model The sync engine retries 3x with exponential backoff then dead-letters
/learn learning:rust lesson Fighting the borrow checker means your data model is wrong
```
Types: `insight`, `lesson`, `model`, `gotcha`, `recipe`, `correction`. Auto-inferred if omitted.

#### `/note [node] [content]`
Fastest capture — one line, no ceremony:
```
/note client:acme Kim confirmed March 15 deadline
/note infra Deployed v2.3.1 to staging
```

### Analysis

#### `/search [query]`
Cross-project search. Finds knowledge, decisions, people, artifacts, blockers, actions:
- "how does the auth flow work" → finds MODEL entries
- "any gotchas with S3 events" → finds GOTCHA entries
- "what went wrong with the migration" → finds LESSON entries
- "what's my P0 list" → unified action list across all nodes

#### `/review [--since date] [--until date]`
Synthesized weekly review (not just a timeline — an analytical digest):
- **Progress**: what moved forward
- **Learned**: new knowledge committed (the "intellectual growth" section)
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
Memory health audit: stale threads, dormant nodes, orphaned entries, duplicates. Proposes numbered actions for approval.

---

## Memory Types

The plugin stores several types of entries. Knowledge entries persist longer than logs — they're the highest-value content.

### Project State
| Entry | Format | Behavior |
|-------|--------|----------|
| **Summary** | `[node] SUMMARY (date): ...` | Replaced each session (always current) |
| **Changelog** | `[node] LOG date — title: ...` | Append-only (never modified) |

### Knowledge
| Entry | Format | When to use |
|-------|--------|-------------|
| **Insight** | `[node] INSIGHT (date): ...` | New realization or connection |
| **Lesson** | `[node] LESSON (date): tried > happened > takeaway` | Something that worked or failed |
| **Model** | `[node] MODEL (date): ...` | How something works |
| **Gotcha** | `[node] GOTCHA (date): ...` | Trap, footgun, or non-obvious behavior |
| **Recipe** | `[node] RECIPE (date): name — when > how` | Reusable technique or process |
| **Correction** | `[node] CORRECTION (date): old > new` | Updated/reversed belief |

### Cross-cutting
| Entry | Format |
|-------|--------|
| **People** | `[node] PEOPLE: Name (role) — context. Also in: [nodes]` |
| **Signal** | `[node] SIGNAL from [other-node] (date): implication` |
| **Archive** | `[node] ARCHIVED (date): compressed summary` |

---

## Priority System

Next actions: `[P0]` do now, `[P1]` this week, `[P2]` eventually, `[WAITING:person]` blocked.

## Staleness Tracking

Threads: `[FRESH]`, `[ONGOING]`, `[STALE]` (3+ sessions without progress).
Nodes: Active (7 days), Warm (8-14), Cooling (15-30), Dormant (30+).

---

## Node Conventions

Use kebab-case. Common patterns:

| Pattern | Example |
|---------|---------|
| Product | `crm-dashboard`, `mobile-app` |
| Client | `client:acme-corp` |
| Infra | `infra:aws`, `infra:ci-cd` |
| Learning | `learning:rust`, `learning:ml-ops` |
| Domain | `domain:tax-law`, `domain:networking` |
| Research | `research:ai-agents` |
| Personal | `personal`, `personal:finances` |
| Bizdev | `bizdev`, `bizdev:stripe` |
| Ops | `company-ops`, `hiring`, `brand` |

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

## Installation

**In Cowork:**
1. Claude Desktop → Cowork tab → Customize → Upload custom plugin
2. Select `session-memory-plugin.zip`
3. Start with `/recall` or `/remember`

---

## Changelog

### v2.1.0
- **Knowledge-first redesign**: Memory now captures insights, lessons, mental models, gotchas, recipes, and corrected beliefs as first-class entry types
- Added `/learn` — quick knowledge capture without full session extraction
- Added `/note` — one-liner capture for quick facts
- Added `/review` — synthesized weekly digest with "Learned" as a prominent section
- `/recall` now surfaces knowledge entries prominently (not buried under project state)
- `/recall [topic]` — topic-based knowledge recall across all projects
- `/search` redesigned to prioritize knowledge entries for "how/what/why" queries
- `/remember` extraction expanded to cover both project state and knowledge categories
- Learning/study nodes (`learning:topic`) and domain knowledge nodes (`domain:area`) added to taxonomy
- Knowledge entries preserved longer than logs during memory consolidation

### v2.0.0
- Added `/search`, `/forget`, `/timeline`, `/cleanup`
- Priority system, staleness tracking, blocker tracking, people index
- Genericized taxonomy, cross-project signals

### v1.0.0
- Initial release with `/remember` and `/recall`
