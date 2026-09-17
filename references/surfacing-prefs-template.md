# surfacing-prefs

> Canonical store for what Nucleus should and should not surface in the daily brief and mining proposals.
> Read by: `briefing` (`/brief` filters its priority-task + outreach pulls before render), cortex miners (skip dismissed classes), and `/end-day` (Step 2c updates this file from brief actions + the repeat-ignore rule).
> Created by `/end-day` Step 2c.3 the first time the user marks something "not important" (or via the briefing setup).

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

Each priority task supports these actions, recorded in the brief's localStorage under `brief-YYYY-MM-DD.tasks[id] = { action, detail, return_on, priority, reprioritized, ts, name }` (schema_version 0.7.0). `/listen` Step 1.5 mines these nightly (or `/end-day` Step 2c, if the user runs it):

| Action | Brief meaning | What gets written back |
|---|---|---|
| `done` | completed | mark source node action COMPLETED; capture as a reflection win candidate |
| `delegate` | handed off (detail = who) | reassign in source node; if CRM connected, create a task for the delegatee; log delegation |
| `skip` | not today (detail = snooze duration; `return_on` = computed absolute date, weekday-adjusted for 1d/3d) | write/update the snooze-ledger entry (`<config-root>/briefs/.snooze-ledger.json`); increment per-task skip counter (feeds the repeat-ignore rule) |
| `not_important` | stop surfacing | append to Do-not-resurface above + demote/close the source node action; delete any snooze-ledger entry for this id |
| `reprioritized: true` + `priority` | on-the-fly priority change (may co-occur with any action above, or stand alone with no `action`) | edit the priority tag on the source-node action |
| annotate | free-text note (also used for calendar events, keyed `event-<id>`) | route per `/process-brief` (draft reply / move date / dismiss) or, for calendar notes, a touchpoint/person-node proposal |

## Outreach action taxonomy (brief outreach queue)

Recorded under `brief-YYYY-MM-DD.outreach_actions[id] = { name, action, bucket, signal, value_add, detail, return_on, ts }` (schema_version 0.7.0 — `return_on` and the annotation textarea, keyed `outreach-<id>` in the same `annotations` map as tasks, were added when Skip stopped committing immediately and gained the same duration mini-form tasks use). `/listen` Step 1.5 writes back (or `/end-day` Step 2c, if run):

| Action | What gets written back |
|---|---|
| `sent` | log touch + value-add on the person/bizdev node; roll bucket/signal/value-add into outreach analytics; append to growth's `events.jsonl` |
| `nudge` | log follow-up touch; append to `events.jsonl` |
| `booked` | advance pipeline stage + create prep task; append to `events.jsonl` |
| `let_go` / `dead` | mark dead; remove from active queue; delete any snooze-ledger + growth `snoozes.json` entry for this contact |
| `skip` | write/update the snooze-ledger entry AND, when the id resolves to a known `memory/person/<slug>.md`, the matching entry in growth's `<config-root>/relationships/snoozes.json` — `/listen` is the only writer that keeps both in sync (see `/listen` Step 1.5h) |

Category fields (optional quick-tag): **bucket** (`new business` / `relationship building` / `network expansion`), **signal** (lead-engine's 7: Engagement / Job change / Funding / Hiring / Growth-expansion / Tech-stack change / Direct intent — auto-fills from the pipeline entry), **value_add** (article/framework · intro · diagnostic/free sample · case study/result · domain observation).

## Snooze ledger (v0.7.0)

`<config-root>/briefs/.snooze-ledger.json` is the canonical snooze store for the brief — keyed by brief item id (`task-<id>` / `outreach-<id>`), holding `{title, kind, node, return_on, skipped_on, skip_count, last_detail}`. `/brief` Step 0D0 reads it before every render: items with `return_on` in the future are hidden and counted; items whose `return_on` has arrived come back tagged "back from snooze" even if the upstream live source forgot about them — the ledger is itself a source, not just a filter. Owned and written exclusively by `/listen` Step 1.5h (never by `/brief`, which only reads it). For outreach items, `/listen` mirrors the same snooze into growth's `<config-root>/relationships/snoozes.json` so `/relationships` agrees without a second filtering pass.

## Changelog
- (created) — initialized from template.
