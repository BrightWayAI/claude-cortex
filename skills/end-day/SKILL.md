---
name: end-day
description: >
  End-of-day closing routine. Quick mode by default (v4.6+) — runs cortex
  auto-commit, reflective prompts, brief pre-stage, memory-index refresh, and
  close in 30 seconds to 3 minutes. Heavy steps (inbox triage, transcript
  review, mining of non-transcript sources) only run in `/end-day --full`, or
  when auto-offered because the day actually had transcripts (≥2) or inbox
  volume (≥5).

  Auto-fires on "/end-day", "wrapping up", "calling it a day", "done for
  today", "end of day", "closing out today". Quick mode is the default for
  every trigger; the user passes `--full` or accepts the auto-offer prompt to
  get the full chain.

  Reflection (Step 4) appends a `## Reflection` section to today's brief
  markdown — that's the canonical write surface and what tomorrow's `/brief`
  Section 6 reads (daily-brief v0.3.0+).
---

See `commands/end-day.md` for the full workflow.

## When this skill fires

- User runs `/end-day` directly
- User says: "wrapping up", "calling it a day", "done for today", "end of day", "closing out", "before I sign off"
- A scheduled task triggers this (common pattern: weekday 4:30pm)

## Pre-flight

Quick mode (the default) has minimal pre-flight requirements — just `<config-root>/identity.md` for time zone, and `daily-brief` if you want the brief pre-staged.

Full mode (`--full`) works best when:
- At least one note source is configured via `/setup-sources` (otherwise the transcript-review step skips)
- Connectors are wired: HubSpot for commitments dedup, Gmail for activity-miner, Calendar MCP, session-info MCP for conversation-miner

Without any of these, the chain skips the affected step silently and continues. Only the cortex auto-commit step (Step 3) is structurally required.

## What this skill is NOT for

- Mid-day status. Use `/recall` or `/search` instead.
- Long retrospectives. That's `/end-week`.
- Verbose summaries. The closing ritual is light, not exhaustive.
- Replacing manual `/remember`. If the user explicitly invoked `/remember` mid-conversation, that commit stands; `/end-day` just mines what wasn't captured.

## Mining-layer flow (v4.3+)

The big change vs. pre-v4.3: the chain now mines the day's signal from multiple sources, not just the current Cowork chat. Specifically:

1. **`transcript-reviewer`** mines configured note sources (Granola / Gemini / Fireflies / etc.) for commitments AND learnings
2. **`conversation-miner`** mines other Cowork sessions from today (excluding the current one)
3. **`activity-miner`** mines CRM events, sent email, calendar metadata

All three run in parallel. Their proposals are merged, deduped, and presented through one unified review gate so the user reviews ~10-20 items once rather than reviewing per-miner. User accepts, edits, or skips per item. Accepted proposals flow into the existing `/remember` auto-commit path (Step 3) — no parallel write surface.

## Substrate for v4.4 decay

Every knowledge entry the mining layer writes carries `[confirmed:YYYY-MM-DD] [recalled:YYYY-MM-DD]` tags. v4.3 maintains them but doesn't yet decay or demote. v4.4 reads them.

## Failure modes

- No sources configured → transcript-review step skips with a one-line note routing the user to `/setup-sources`
- All miners triage-skip on a quiet day → Step 2b shows "Quiet day — nothing material to surface" and the chain proceeds to Step 3 with current-session content only
- Session-info MCP unavailable → conversation-miner returns empty with a confidence note
- HubSpot / Gmail / Calendar MCPs missing → activity-miner returns empty for the missing source but still runs against the available ones
- User walks away mid-Step-2b → 30s timeout, "skip all" default, dismissals logged
