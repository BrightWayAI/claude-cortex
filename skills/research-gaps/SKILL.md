---
name: research-gaps
description: >
  Active maintenance loop for cortex memory. Scans `<config-root>/memory/` for
  thin / stale / contradictory / orphaned / under-cited / past-due / sparse
  content, researches the highest-priority gaps via the open web (≥2 sources per
  claim), and writes findings to `staged/research-drafts/` for user review.

  Auto-fires when the user says: "what's missing from my memory", "research
  gaps in my second brain", "fill in what we don't know", "audit my knowledge
  for holes", "what should we learn more about", "are there contradictions in
  my memory", "what's stale that I should refresh", "what nodes are weak".

  Also fires when invoked explicitly via /research-gaps and as optional Step 6
  of /end-week (cortex v4.5+).

  Honors the private-individual privacy rule: only verifiable professional
  facts surface for person research.

  Never modifies active memory. All findings stage to a draft for user merge.
---

# research-gaps

See `commands/research-gaps.md` for the full workflow and `references/gap-detection-rules.md` for the formal detection rules.

## When to fire

- Explicit: `/research-gaps` or any of the trigger phrases above.
- Chained: optional Step 6 of `/end-week` (`Run /research-gaps to fill knowledge gaps from the week?`).
- Scheduled: weekly Saturday morning if the user registered the schedule via core-ops.

## What to do

1. Resolve `<config-root>` and run the scan per `commands/research-gaps.md`.
2. Present the ranked gap list and capture per-gap actions.
3. Invoke the `gap-researcher` subagent for gaps the user chose to research.
4. Surface the draft path and remind the user to run `/merge-research-draft` next.

## What this skill does NOT do

- Does not modify active memory. The draft is the only side effect outside `staged/skip-logs/research.md`.
- Does not handle merge. That's `/merge-research-draft`.
- Does not run on schedule without explicit user opt-in.
- Does not research private individuals beyond verifiable professional facts.
