---
description: Close out the work week. Runs the transcript-reviewer to surface uncaptured commitments, runs cortex's /cleanup to maintain memory health, runs /review for synthesized weekly digest, prompts for weekly reflection, and optionally pre-stages Monday's outreach via weekly-outreach. The Friday afternoon ritual that makes Mondays sharper.
---

# /end-week

End-of-week closing routine. Synthesizes the week, surfaces what slipped through, maintains memory hygiene, and pre-stages Monday. Run Friday afternoon (3–5pm). Takes ~15 minutes.

This is the bigger sibling of `/end-day`. End-day captures today's reflection; end-week looks at patterns across the whole week.

---

## Step 1 — Run transcript-reviewer

If `claude-cortex` is installed and the user uses Granola (or another call-transcript source) for meetings:

Use the Task tool with `subagent_type="transcript-reviewer"` and pass:
- `time-window` — 7 days
- `sources` — `["granola"]` (default; add `"gemini-drive"` if user has Gemini transcripts and the user-context says so)

The agent returns uncaptured commitments — things the user said in meetings that aren't yet tracked in HubSpot tasks or working memory. Surface the table to the user and ask:

> "Want me to create CRM tasks for any of these? Reply with the row numbers (e.g., '1,3,5'), 'all', or 'skip'."

Create tasks for selected items via the user's CRM.

---

## Step 2 — Run cortex /cleanup

Invoke the cortex `/cleanup` workflow to:

- Consolidate old log entries
- Detect stale threads (3+ sessions without progress)
- Identify orphaned nodes
- Report on memory health

Report any findings briefly. Don't auto-archive anything — surface for the user's decision.

---

## Step 3 — Run cortex /review

Invoke `/review` to generate the synthesized weekly digest:

- What moved forward
- What was learned (knowledge entries committed this week)
- What's stuck
- What's coming up

Render the digest to the user.

---

## Step 3.5 — Rehearse aging knowledge (v4.4+)

Invoke `/rehearse` (its full workflow lives in `commands/rehearse.md`). The skill:

1. Builds a candidate pool of knowledge entries past their freshness threshold but not yet cold
2. Selects up to 5 entries (configurable via `<config-root>/memory/.decay-config.md`)
3. Walks the user through each: confirm / update / demote / archive / skip

This is the active retention loop — the explicit consolidation pass that converts dormancy into either re-confirmation or removal. Different from Step 2's `/cleanup` (which audits memory health broadly) — `/rehearse` is per-entry, deliberate, and small-batch.

If the candidate pool is empty ("memory is fresh"), the skill exits cleanly and the user sees a one-line confirmation. Don't pad.

---

## Step 4 — Reflective prompts

Ask, one at a time:

1. **"Biggest win this week?"** — capture as INSIGHT in the most relevant node + DASHBOARD callout
2. **"Biggest miss or blocker?"** — capture as LESSON or GOTCHA, route to the relevant node
3. **"What's one thing you want to change about how you worked this week?"** — capture as a PREFERENCE / PATTERN in `user.md` if it's a working-style change, or as a RECIPE if it's a process change
4. **"What's the most important thing for next week?"** — capture as P0 in the relevant node with a date stamp for Monday

Keep this conversational. The point is reflection, not capture-everything completionism.

---

## Step 5 — Pre-stage Monday outreach (optional)

If `weekly-outreach` is installed, offer:

> "Want me to run `/weekly-outreach` now while you're in the headspace? It'll pull next week's external meetings, build the prioritized outreach queue (delegating to pipeline-analyst + contact-researcher if installed), draft messages, and propose CRM tasks + calendar placeholders. You can review and approve before anything's written."

If yes → invoke `/weekly-outreach`. The user can iterate on the plan before committing.
If no → skip; user can run Monday morning.

---

## Step 5.5 — Research gaps (optional, v4.5+)

Offer:

> "Run `/research-gaps` now to find and fill weak spots in memory (thin entities, stale facts, contradictions, orphans, under-cited claims)? Findings stage to a draft for review — nothing auto-merges. Default scope: full memory."

If yes → invoke `/research-gaps` in chained mode (skips the user prompt at Step 2 of that command; renders the gap list inline and asks "Research the top 5?").
If no → skip; user can run any time with `/research-gaps`.

Skip this step silently if cortex is below v4.5 (no `/research-gaps` available).

---

## Step 5.7 — Log to chronicle (v4.7.1+, centralized in v4.7.2+)

Invoke the `log-writer` skill (see `skills/log-writer/SKILL.md`) with:
- **op_name:** `end-week`
- **summary:** `transcript-reviewer flagged <T> commitments, cleanup <C> actions, rehearse <R> entries, research-gaps <G>. Monday outreach <staged|skipped>.`

---

## Step 6 — Close

Confirm completion:

> "Week closed. [Summary of what was committed and pre-staged.]
> Memory hygiene: [healthy / [N] items flagged for review].
> Have a good weekend."

---

## Behavior rules

- **Pace it.** ~15 minutes total. If the user is in a hurry, ask which steps to skip rather than skipping silently.
- **Don't pile on.** If transcript-reviewer surfaces 20 uncaptured commitments, that's a lot. Surface them but make it easy to triage (numbers, "all," "skip").
- **Honor decisions made earlier.** If the user said "pause Acme outreach" earlier in the week (e.g., via bizdev-outreach's HOLDING PATTERN), don't surface that contact again in pre-stage outreach.
- **Idempotent.** Running `/end-week` twice (e.g., Thursday and Friday) shouldn't double-commit. Memory updates are append-only or update-in-place.

## When this skill is NOT the right fit

- **Daily reflection.** Use `/end-day`.
- **Full project retrospective.** End-week is rhythmic; for a deep project retrospective use `/recall [project]` and ad-hoc dialogue.
- **Quarter-end planning.** End-week looks 1 week back / 1 week forward. For quarterly horizon, that's a separate strategic prompt.

---

## What this enables

The combo of `/end-day` daily and `/end-week` Friday is the **rhythm** that makes the rest of the marketplace compounding:

- **Memory stays fresh** (cleanup runs weekly; commits run daily) → cortex auto-recall is sharper
- **Commitments don't slip** (transcript-reviewer catches what was said but not tracked)
- **Mondays are pre-thought** (weekly-outreach + plan-tomorrow can be staged Friday)
- **Weeks stay self-aware** (review surfaces patterns)

Without these closing rituals, plugins still work but you carry more in your head. With them, the system carries it for you.
