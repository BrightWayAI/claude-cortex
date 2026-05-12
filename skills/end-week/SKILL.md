---
name: end-week
description: End-of-week closing routine. Runs transcript-reviewer for uncaptured commitments, /cleanup for memory hygiene, /review for synthesized digest, /rehearse for aging-knowledge triage (v4.4+), prompts for weekly reflection, optionally pre-stages Monday's outreach via weekly-outreach. Auto-fires on "/end-week", "Friday wrap-up", "weekly close", "end of week", "Friday afternoon ritual", "close out the week", or any phrase signaling Friday wind-down. Takes ~15-20 minutes including the rehearsal step.
---

See `commands/end-week.md` for the full workflow.

## When this skill fires

- User runs `/end-week` directly
- User says: "Friday wrap-up", "close out the week", "weekly close", "end of week", "Friday afternoon ritual"
- A scheduled task triggers this (common pattern: Friday 3pm or 4pm)

## Pre-flight

Works best with the full marketplace stack (cortex, brightway-core, weekly-outreach, plan-tomorrow). Each step gracefully skips if its dependency isn't installed:

- `/transcript-reviewer` requires cortex + Granola/transcript source — skipped otherwise
- `/cleanup` requires cortex — skipped otherwise
- `/review` requires cortex — skipped otherwise
- `/rehearse` (v4.4+) requires cortex — skipped otherwise; exits cleanly if no aging entries qualify
- Pre-stage Monday requires weekly-outreach — offered as optional

Even with no dependencies, the reflective prompts in Step 4 still work and write to memory if cortex is present.

## What this skill is NOT for

- Daily reflection. Use `/end-day`.
- Quarter-end strategic planning. Different horizon.
- Full project retrospective. Use `/recall [project]` for that.
