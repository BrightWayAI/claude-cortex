---
name: morning
description: >
  The JARVIS morning routine. Reads the most-recent overnight `/listen` draft
  at `<config-root>/memory/staged/commit-drafts/`, walks the user through each
  proposed memory commit (accept / reject / edit / defer), applies accepted
  proposals to active memory nodes with v4.4 drift-detection, refreshes
  `memory/hot.md` and `memory/index.md`, and optionally chains into `/brief`.

  Auto-fires when the user says: "good morning", "start my day", "what happened
  overnight", "morning routine", "merge overnight ingest", "review last night's
  proposals". Most natural trigger is just opening a session and saying "good
  morning" — the router suggests `/morning` and the chain begins.

  Read-write to active memory but only for user-accepted proposals. Never
  silently merges, even for high-confidence proposals.
---

# morning

See `commands/morning.md` for the full workflow.

## When to fire

- Explicit: `/morning`, `/morning --date YYYY-MM-DD`, `/morning --discard`.
- Trigger phrases above. Default morning greeting routes here.
- Optional chain: cortex auto-recall at conversation start *could* detect a pending draft and prompt "Want to run /morning first?" — opt-in via user-context.

## Pre-flight

- A `/listen` draft must exist at `<config-root>/memory/staged/commit-drafts/`. If not, the command exits gracefully and offers to run `/listen` now.
- `<config-root>/identity.md` for time zone.

## What this skill is NOT for

- Generating new proposals (that's `/listen`).
- Web research (that's `/research-gaps`).
- End-of-day reflection (that's `/end-day`).
- Bulk memory cleanup (that's `/cleanup`).
