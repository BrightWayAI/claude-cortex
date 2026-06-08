# surfacing-prefs

> Canonical store for what Nucleus should and should not surface in the daily brief and mining proposals.
> Read by: `daily-brief` (`/brief` filters its priority-task + outreach pulls before render), cortex miners (skip dismissed classes), and `/end-day` (Step 2c updates this file from brief actions + the repeat-ignore rule).
> Created by `/end-day` Step 2c.3 the first time the user marks something "not important" (or via the daily-brief setup).

## Do-not-resurface (explicit suppressions)

Items here must NOT appear as priority tasks or brief action items. Each has a reason and a source so the loop is auditable. Re-surface only if the linked condition flips.

<!-- Format:
- **<title>** (<source node/id>) — <one-line context>. [suppressed:YYYY-MM-DD, reason:user-stated-unimportant | repeat-ignore]
-->

## Surfacing rules (learned heuristics)

- **Admin/finance dunning emails** (subscription payment failures, card-update nags) are noise by default — never promote to a brief priority task unless explicitly flagged. Route at most to a low-priority "admin" mention.
- **Vendor learning-path / certification / onboarding nudges** are noise by default.
- **Repeat-ignore rule:** if a brief priority task is surfaced ≥3 times and never acted on (no done/delegate, only carryover or skip), `/end-day` Step 2c.3 proposes moving it here rather than carrying it forward again. Skip counts live in `<config-root>/memory/.brief-skip-counts.json`.

## Action taxonomy (brief priority tasks)

Each priority task supports these actions, recorded in the brief's localStorage under `brief-YYYY-MM-DD.tasks[id] = { action, detail, ts, name }`. `/end-day` Step 2c mines these and writes back:

| Action | Brief meaning | What `/end-day` does |
|---|---|---|
| `done` | completed | mark source node action COMPLETED; capture as a reflection win candidate |
| `delegate` | handed off (detail = who) | reassign in source node; if CRM connected, create a task for the delegatee; log delegation |
| `skip` | not today (detail = snooze duration) | defer; increment per-task skip counter (feeds the repeat-ignore rule) |
| `not_important` | stop surfacing | append to Do-not-resurface above + demote/close the source node action |
| annotate | free-text note | route per `/process-brief` (draft reply / move date / dismiss) |

## Outreach action taxonomy (brief outreach queue)

Recorded under `brief-YYYY-MM-DD.outreach_actions[id] = { name, action, bucket, signal, value_add, detail, ts }`. `/end-day` Step 2c writes back:

| Action | What `/end-day` does |
|---|---|
| `sent` | log touch + value-add on the person/bizdev node; roll bucket/signal/value-add into outreach analytics |
| `nudge` | log follow-up touch |
| `booked` | advance pipeline stage + create prep task |
| `let_go` / `dead` | mark dead; remove from active queue |
| `skip` | defer reappearance by `detail` |

Category fields (optional quick-tag): **bucket** (`new business` / `relationship building` / `network expansion`), **signal** (lead-engine's 7: Engagement / Job change / Funding / Hiring / Growth-expansion / Tech-stack change / Direct intent — auto-fills from the pipeline entry), **value_add** (article/framework · intro · diagnostic/free sample · case study/result · domain observation).

## Changelog
- (created) — initialized from template.
