---
name: start-workstream
description: >
  Create a new workstream node — cortex's primitive for ongoing initiative
  pipelines that span multiple projects, people, and topics. Walks a short
  interview (name, current state, pinned context, linked entities) and writes
  `<config-root>/memory/workstream/<slug>.md`.

  Auto-fires when the user says: "start a workstream", "begin tracking X as
  a workstream", "I'm starting a new initiative — X", "I'm working on a new
  initiative", "set up a workstream for X".

  Differentiation:
  - Project nodes (`client/<slug>`) capture a specific engagement.
  - Person pages capture a relationship.
  - Topic nodes capture a subject area.
  - Domain nodes capture a persistent area of work.
  - Workstreams capture an ongoing *initiative pipeline* with current state,
    pinned context, open loops, and linked entities — spans projects/people/topics.

  New in cortex v4.9.0. See `references/workstream-schema.md` for the full schema.
---

# start-workstream

See `commands/start-workstream.md` for the full workflow and `references/workstream-schema.md` for the schema.

## When to fire

- Explicit: `/start-workstream <slug>` (slug provided) or `/start-workstream` (prompts for name).
- Trigger phrases above.
- Implicit hand-off from `/remember`: if `/remember` detects that the content describes a multi-entity ongoing initiative not yet captured as a workstream, it can suggest `/start-workstream` rather than writing to a project or topic node.

## Pre-flight

- `<config-root>/memory/` must exist (cortex setup must have been run).
- No other prerequisite — workstreams can reference yet-to-be-created entities (they'll be added later as the workstream matures).

## What this skill is NOT for

- Creating project / client engagement nodes (use `/remember client:<slug>` instead).
- Creating person pages (these graduate automatically per v4.2 rules).
- Generating a workstream plan / Gantt — workstreams capture state, not schedules.
- Migrating an existing project node into a workstream (manual copy/move).
