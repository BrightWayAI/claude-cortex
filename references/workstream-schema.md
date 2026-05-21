# Workstream node schema (v4.9+)

A workstream is an **ongoing initiative pipeline** that spans multiple projects, people, and topics. Examples:
- "BrightWay 2026 product strategy" — multiple advisors, multiple clients, multiple decisions
- "Ops platform evaluation" — multiple vendors, internal stakeholders, evaluation criteria
- "Q3 outbound campaign" — dozens of contacts, message variants, results
- "AI agent framework migration" — multiple repos, multiple specialists, decision points

Workstreams sit ABOVE project nodes (one workstream may include multiple client engagements) and BELOW domain nodes (one domain may have multiple parallel workstreams).

This was the missing primitive identified during the codex-maxxing pattern review (Liu's "pinned workstream / megathread" pattern adapted to cortex's typed-node model).

## Why workstreams aren't projects, topics, or domains

| Type | Captures | Time horizon | Updates |
|---|---|---|---|
| `client/` (project) | A specific engagement | Engagement lifetime | Per session |
| `person/` | A relationship | Indefinite | Per interaction |
| `topic/` | A subject area | Indefinite | Per learning |
| `domain/` (root) | A persistent area of work | Indefinite | Per session |
| **`workstream/`** | **An ongoing initiative pipeline** | **Defined start; eventual end** | **Per session, with explicit current-state** |

A workstream has a beginning (when you decide it's a thing), a current state (what's true today), pinned context (background that doesn't change), recent activity (rolling 20-entry log), open loops (waiting on you / waiting on others / decided), and linked entities (people, clients, topics, domains involved).

## Schema

File location: `<config-root>/memory/workstream/<slug>.md`. Slug is kebab-case, derived from the workstream name.

```markdown
---
type: workstream
status: active | paused | completed | archived
created: YYYY-MM-DD
last_active: YYYY-MM-DD
decay_profile: slow
---

# <Workstream Name>

## Current state
<One paragraph. Where we are right now. What's true today. What's the next concrete move.>

## Pinned context
<Background that doesn't change. The goal. The constraints. The players and their roles. The success criteria.>

## Recent activity
- YYYY-MM-DD — <one line>
- YYYY-MM-DD — <one line>
...
(rolling — keep last 20 entries; older auto-archive into Changelog)

## Open loops
- [P0] <action waiting on me, blocking the workstream>
- [P1] <high-priority action waiting on me>
- [P2] <action waiting on me, not urgent>
- [WAITING:<name>] <action waiting on someone else>
- [DECIDED:YYYY-MM-DD] <resolved loop — kept for traceability for ~30 days, then archive>

## Linked entities
- People: [[person/<slug>]], [[person/<slug>]]
- Clients: [[client/<slug>]]
- Topics: [[topic/<slug>]]
- Domains: [[<root-domain>]]
- Other workstreams (rare; for genuinely connected initiatives): [[workstream/<slug>]]

## Knowledge (workstream-scoped)
### Insights
- [confirmed:YYYY-MM-DD] <entry>
### Models
### Gotchas
### Lessons
### Recipes
### Decisions
- DECISION [confirmed:YYYY-MM-DD] <decision>
  - **What was decided:** ...
  - **When:** YYYY-MM-DD
  - **Why:** ...
  - **Affected:** [[entity]], [[entity]]
  - **Revisit when:** <trigger> (or "n/a")
  - **Status:** active | superseded | revisit-now
### Corrections

## Changelog
[YYYY-MM-DD] <event line>
[YYYY-MM-DD] <event line>
```

## Required vs optional sections

**Required (must exist on creation):**
- Front-matter (type, status, created, last_active)
- `## Current state` (even if one line)
- `## Pinned context` (even if a paragraph)

**Optional (added over time):**
- `## Recent activity` — populated by `/remember` and mining as the workstream is touched
- `## Open loops` — added when commitments emerge
- `## Linked entities` — added as the workstream touches people, clients, etc.
- `## Knowledge` — added when learnings emerge
- `## Changelog` — populated by `/remember` and mining

## Lifecycle

### Creation

User says: "start a workstream: <name>" or "I'm working on a new initiative — <name>" or `/start-workstream <slug>`.

Cortex prompts:
1. **Name** (kebab-case slug confirmation)
2. **Current state** (one paragraph)
3. **Pinned context** (background, goal, constraints, players)
4. **Initial linked entities** (people / clients / topics already involved — optional)

Then writes the new node file at `memory/workstream/<slug>.md` with front-matter `created: today`, `status: active`, `decay_profile: slow`.

### Updates

The workstream node receives writes from:
- `/remember` (when content is workstream-scoped) — routes the knowledge entry to the workstream's `## Knowledge` and updates `## Recent activity`
- `/note` — adds a one-line entry to `## Recent activity` if it references the workstream
- Mining loops (`/listen`, future `/sweep`) — propose updates to workstream nodes the same way they propose updates to project nodes; reviewed at `/morning` / `/end-day`
- `/cleanup` — surfaces workstreams in section H (cooling/dormant) when `last_active` ages past thresholds

### Status transitions

- **active** (default) — workstream is being touched regularly
- **paused** — user explicitly paused; not in active rotation but kept warm
- **completed** — explicit completion; archived loops, final reflection, no further updates
- **archived** — moved to `memory/workstream/archive/<slug>.md` after extended inactivity (with user confirmation via `/cleanup`)

Transitions are user-driven via:
- "pause the X workstream"
- "X is done / wrap up the X workstream"
- (auto-suggest at `/cleanup` for dormant workstreams)

## How workstreams are queried

`/recall workstream:<slug>` — surfaces:
- Current state (1-2 paragraphs)
- Pinned context (read-only)
- Recent activity (top 5)
- Open loops (all)
- Linked entities (with status indicators)
- Recent knowledge (last 5 entries)

Memory-librarian queries that mention an initiative by name → workstream lookup preferred over scattered project / topic node search.

Hot.md "What I worked on (last 7 days)" section pulls from workstreams.last_active first.

## Decay behavior

- Default `decay_profile: slow` (1.5x multiplier on thresholds — workstreams stay fresh longer than topic nodes)
- `last_active` updates on any write to the file
- `/cleanup` section H surfaces workstreams aging into stale/dormant
- Workstreams never auto-archive without user confirmation (in case the initiative is dormant-but-not-dead)
- Completed workstreams retain decay state but stop receiving freshness updates

## Integration points (where workstream awareness matters)

| Location | Effect |
|---|---|
| `/remember` Step 1 (detect target node) | Adds workstream detection — content mentioning an active workstream by name routes there |
| `/remember` Step 2 (extract knowledge) | Workstream-scoped knowledge entries write to the workstream's `## Knowledge` section |
| `/recall` | New target: `/recall workstream:<slug>` |
| `memory-librarian` | New query path: workstream-shape queries route here first |
| `indexer` | New `## Workstreams` section in `memory/index.md` catalog |
| `hot.md` | Active workstreams (last_active within 7d) populate the "What I worked on" section |
| `/cleanup` section H | Surfaces aging workstreams; offers pause/complete/archive |
| Decay model | `decay_profile: slow` honored; recompute uses 1.5x multipliers |
| `/end-day` reflection | Optionally prompts which workstreams advanced today |

## What this is NOT

- **Not a project node.** Project nodes capture a specific engagement (a client, a contract). Workstreams span engagements.
- **Not a topic node.** Topic nodes capture a subject area (knowledge about X). Workstreams capture an *initiative* on X.
- **Not a tag.** Tags don't have current-state, pinned-context, or open-loop sections. Workstreams are first-class nodes.
- **Not a calendar / Gantt chart.** Workstreams capture state, not schedules. Use `/plan-tomorrow` or `/weekly-outreach` for schedule planning.
