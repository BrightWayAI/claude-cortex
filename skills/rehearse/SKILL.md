---
name: rehearse
description: Active retention loop — surfaces 3-5 aging knowledge entries past their freshness threshold (but not yet cold) and walks the user through "still true? still useful?" per entry. Confirm / update / demote / archive / skip per entry. The explicit consolidation pass that converts dormancy into either re-confirmation or removal. Auto-fires on "/rehearse", "is this still true", "rehearse my memory", "what should I confirm or forget", "memory rehearsal", "consolidate my memory", or invoked weekly by /end-week. Default batch size 5; cadence weekly.
---

See `commands/rehearse.md` for the full workflow.

## When this skill fires

- User runs `/rehearse` directly
- User says: "is this still true", "rehearse my memory", "what should I confirm or forget", "memory rehearsal", "consolidate my memory", "is what I know still right"
- `/end-week` invokes this as Step 5 of its chain

## What this skill is NOT for

- **Memory health audits** — that's `/cleanup` (broader audit covering stale threads, orphans, dormant person pages, plus the entry-level audit `/rehearse` doesn't do)
- **Bulk archiving** — also `/cleanup`. `/rehearse` is per-entry, deliberate, small-batch.
- **Person-page maintenance** — `/cleanup` section H handles person pages; this skill focuses on knowledge entries inside nodes.
- **New knowledge capture** — that's `/learn` or `/note` or `/remember`. `/rehearse` only acts on entries that already exist.

## Inputs

- `<config-root>/memory/.decay-config.md` — thresholds and per-type modifiers (auto-created with defaults if missing)
- All active node files in `<config-root>/memory/` — to build the candidate pool
- `<config-root>/memory/staged/queues/rehearse.md` (if present) — entries `/cleanup` deferred to rehearsal get priority
- `<config-root>/memory/staged/skip-logs/rehearse.md` — entries the user skipped in recent rehearsals (suppressed for 30 days)

## Outputs

- Updated `[confirmed:<today>]` tags on confirmed entries
- Edited entries with refreshed text (on `update`)
- Entries moved to `## Demoted knowledge` (on `demote` or `archive`)
- Skip-log entries (on `skip`)
- One-line summary to chat: confirmed / updated / demoted / archived / skipped counts

## Cost

Zero model calls in steady state. Date arithmetic + file edits. The user makes the decisions.

## Failure modes

- Empty candidate pool → "Memory is fresh — nothing past the rehearsal threshold today." Exits cleanly. Not an error.
- `.decay-config.md` missing → auto-create with documented defaults; continue.
- Malformed `[confirmed:...]` tags → treat as "default to original commit date" rather than failing
- User abandons mid-batch → partial batch is fine; remaining entries naturally surface in the next rehearsal
