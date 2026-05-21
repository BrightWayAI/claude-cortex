---
name: listen
description: >
  Nightly autonomous ingest pipeline. Pulls yesterday's calendar / Gmail /
  Slack / transcripts / Drive activity into `<config-root>/archive/YYYY-MM-DD/`
  (immutable substrate), runs the mining agents against the archive, stages all
  proposed memory commits to `staged/commit-drafts/YYYY-MM-DD.md`, and refreshes
  `memory/hot.md`. Designed for unattended scheduled execution — no user gates.

  Auto-fires when the user says: "ingest yesterday", "run nightly ingest",
  "what happened yesterday I haven't captured", "mine yesterday's calendar",
  "process yesterday's transcripts". Most users register it on a schedule
  (11pm or 5am) via core-ops `/register-schedules` and never invoke it by hand.

  Pair with `/morning` for the interactive review-and-merge of the staged draft.
---

# listen

See `commands/listen.md` for the full workflow and `references/archive-layout.md` for the archive directory structure.

## When to fire

- Scheduled: most common path. Cron via core-ops at 11pm or 5am.
- Explicit: `/listen` (yesterday), `/listen --date YYYY-MM-DD`, `/listen --backfill N`, `/listen --remine YYYY-MM-DD`.
- Trigger phrases above — useful when the user catches up after a vacation or wants to ingest a specific past day.

## Pre-flight

- `<config-root>/identity.md` exists.
- `/setup-sources` has been run at least once and configured at least one note adapter.
- For full value, `inbox-triage`-style connectors are wired (Gmail MCP, Calendar MCP, Slack MCP) — but missing connectors just degrade gracefully; the pipeline runs against whatever's available.

## What this skill is NOT for

- Manual mid-day capture. Use `/remember` or `/note`.
- Interactive end-of-day rituals. Use `/end-day` (quick) or `/end-day --full`.
- Memory health audits. Use `/cleanup`.
- Web research. Use `/research-gaps`.
- Merging proposals. Use `/morning`.
