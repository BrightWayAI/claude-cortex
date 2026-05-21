---
description: Create a new workstream node — the cortex primitive for ongoing initiative pipelines that span multiple projects, people, and topics. Walks a short interview (name, current state, pinned context, linked entities) and writes `<config-root>/memory/workstream/<slug>.md`. See `references/workstream-schema.md` for the schema. New in cortex v4.9.0.
---

# /start-workstream [name]

You are creating a new workstream node — the cortex primitive for *ongoing initiative pipelines*. Use when the user wants to track an initiative that doesn't fit cleanly into a project node, topic node, or domain node.

Examples of workstream-shaped intents:
- "Start a workstream: 2026 product strategy"
- "I'm beginning work on the ops platform evaluation — track it"
- "Set up a workstream for Q3 outbound campaign"

If the user mentions a "workstream" or "initiative" you don't already have a node for, this is the command.

---

## Step 0 — Resolve config root

Standard pattern. If `<config-root>/memory/` doesn't exist, run `/setup-identity` first.

---

## Step 1 — Determine the slug

If the user provided a name in the argument (`/start-workstream q3-outbound`), use the kebab-case slug directly.

Otherwise, ask:

> "What's the workstream called? I'll use the name as the file slug (kebab-case). E.g., 'Q3 outbound campaign' → `q3-outbound-campaign`."

Validate:
- Slug is kebab-case, lowercase, no spaces
- File `<config-root>/memory/workstream/<slug>.md` doesn't already exist (if it does, say so and offer `/recall workstream:<slug>` or rename)

---

## Step 2 — Capture current state

Ask:

> "One paragraph — where this workstream is *right now*. What's true today. What's the immediate next move."

Capture verbatim. Don't paraphrase. The user's voice goes in unedited; cortex isn't supposed to rewrite their own framing of their work.

---

## Step 3 — Capture pinned context

Ask:

> "Pinned context — the background that doesn't change. What's the goal? Who's involved (briefly)? What constraints are you working under? What does success look like?"

Capture verbatim (or in lightly-structured paragraphs if the user gives narrative).

---

## Step 4 — Capture initial linked entities

Ask (optional — user can skip):

> "Any existing people, clients, topics, or domains this workstream touches? List them — I'll link the workstream to those nodes. (Skip to leave empty for now.)"

For each entity the user mentions:
- If it's a known node (exists at `memory/<type>/<slug>.md`), use the wikilink directly
- If it's not known, ask: "I don't have a node for X yet. Create one as part of this workstream setup, or just note the name?"
  - Create now → use `/remember` to create the node, then link
  - Note only → write the name in the Linked entities section without a wikilink

---

## Step 5 — Write the workstream node

Create `<config-root>/memory/workstream/<slug>.md` with the schema from `references/workstream-schema.md`:

```markdown
---
type: workstream
status: active
created: <today>
last_active: <today>
decay_profile: slow
---

# <Workstream Name>

## Current state
<from Step 2>

## Pinned context
<from Step 3>

## Recent activity
- <today> — Workstream created.

## Open loops
(none yet)

## Linked entities
<from Step 4 — formatted by type>

## Knowledge (workstream-scoped)
### Insights
### Models
### Gotchas
### Lessons
### Recipes
### Decisions
### Corrections

## Changelog
[<today>] Workstream created via /start-workstream.
```

Make sure to:
- Create the `memory/workstream/` directory if it doesn't exist (idempotent)
- Use the slug from Step 1 as the filename
- Set front-matter `decay_profile: slow` (the default for workstreams)

---

## Step 6 — Update related nodes

For each linked entity from Step 4 that already exists:

- Append to the entity's `## Linked entities` or `## Workstreams` section (create if missing):
  ```markdown
  - [[workstream/<slug>]] — <one-line context from current state>
  ```

This gives the workstream backlinks from related nodes (so `/recall person:sarah-chen` will surface the workstream too).

---

## Step 7 — Queue index refresh

Append a line to `<config-root>/memory/staged/queues/reindex`:

```
<today HH:MM> touched: workstream/<slug>
```

So the next `/end-day` or `/reindex` regenerates `memory/index.md` with the new workstream listed.

---

## Step 8 — Log to chronicle

Invoke the `log-writer` skill:
- **op_name:** `start-workstream`
- **summary:** `created workstream/<slug> — <Workstream Name>. <N> linked entities.`

---

## Step 9 — Confirm and offer next steps

Surface the new workstream:

```
Workstream created: <Name>
Location: <config-root>/memory/workstream/<slug>.md
Linked entities: <list>

Next moves:
  • Add open loops: "log a P0 for this workstream — X"
  • Capture knowledge: "remember that <insight> on workstream:<slug>"
  • Recall the workstream: "catch me up on workstream:<slug>"
```

---

## Idempotent re-runs

If the user runs `/start-workstream <slug>` and the file already exists, do NOT overwrite. Surface:

> "Workstream `<slug>` already exists. Want to /recall it, edit current state, rename, or pick a different slug?"

---

## Autonomy

Default autonomy mode: `suggest`. Each step has a prompt; the user can skip optional ones. With `auto` mode, the command runs through all steps with placeholder text in optional fields and prompts the user to fill in later.

---

## What this command does NOT do

- Does not create project / person / company / topic nodes (use `/remember` for those)
- Does not promote a project node into a workstream (manual; copy / move content if needed)
- Does not generate a workstream "plan" or work breakdown — workstreams capture *state*, not schedules
- Does not invoke `/plan-tomorrow` or scheduling commands automatically
